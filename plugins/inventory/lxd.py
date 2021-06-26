# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Frank Dornheim <dornheim@posteo.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: lxd
    short_description: Returns Ansible inventory from lxd host
    description:
        - Get inventory from the lxd.
        - Uses a YAML configuration file that ends with 'lxd.(yml|yaml)'.
    version_added: "3.0.0"
    author: "Frank Dornheim (@conloos)"
    requirements:
        - ipaddress
    options:
        plugin:
            description: Token that ensures this is a source file for the 'lxd' plugin.
            required: true
            choices: [ 'community.general.lxd' ]
        url:
            description:
            - The unix domain socket path or the https URL for the lxd server.
            - Sockets in filesystem have to start with C(unix:).
            - Mostly C(unix:/var/lib/lxd/unix.socket) or C(unix:/var/snap/lxd/common/lxd/unix.socket).
            default: unix:/var/snap/lxd/common/lxd/unix.socket
            type: str
        client_key:
            description:
            - The client certificate key file path.
            aliases: [ key_file ]
            default: $HOME/.config/lxc/client.key
            type: path
        client_cert:
            description:
            - The client certificate file path.
            aliases: [ cert_file ]
            default: $HOME/.config/lxc/client.crt
            type: path
        trust_password:
            description:
            - The client trusted password.
            - You need to set this password on the lxd server before
                running this module using the following command
                C(lxc config set core.trust_password <some random password>)
                See U(https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/).
            - If I(trust_password) is set, this module send a request for authentication before sending any requests.
            type: str
        state:
            description: Filter the container according to the current status.
            type: str
            default: none
            choices: [ 'STOPPED', 'STARTING', 'RUNNING', 'none' ]
        prefered_container_network_interface:
            description:
            - If a container has multiple network interfaces, select which one is the prefered as pattern.
            - Combined with the first number that can be found e.g. 'eth' + 0.
            type: str
            default: eth
        prefered_container_network_family:
            description:
            - If a container has multiple network interfaces, which one is the prefered by family.
            - Specify C(inet) for IPv4 and C(inet6) for IPv6.
            type: str
            default: inet
            choices: [ 'inet', 'inet6' ]
        groupby:
            description:
            - Create groups by the following keywords C(location), C(pattern), C(network_range), C(os), C(release), C(profile), C(vlanid).
            - See example for syntax.
            type: dict
'''

EXAMPLES = '''
# simple lxd.yml
plugin: community.general.lxd
url: unix:/var/snap/lxd/common/lxd/unix.socket

# simple lxd.yml including filter
plugin: community.general.lxd
url: unix:/var/snap/lxd/common/lxd/unix.socket
state: RUNNING

# grouping lxd.yml
groupby:
  testpattern:
    type: pattern
    attribute: test
  vlan666:
    type: vlanid
    attribute: 666
  locationBerlin:
    type: location
    attribute: Berlin
  osUbuntu:
    type: os
    attribute: ubuntu
  releaseFocal:
    type: release
    attribute: focal
  releaseBionic:
    type: release
    attribute: bionic
  profileDefault:
    type: profile
    attribute: default
  profileX11:
    type: profile
    attribute: x11
  netRangeIPv4:
    type: network_range
    attribute: 10.98.143.0/24
  netRangeIPv6:
    type: network_range
    attribute: fd42:bd00:7b11:2167:216:3eff::/24
'''

import binascii
import json
import re
import time
import os
import socket
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible.module_utils.six import raise_from
from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.module_utils.lxd import LXDClient, LXDClientException

try:
    import ipaddress
except ImportError as exc:
    IPADDRESS_IMPORT_ERROR = exc
else:
    IPADDRESS_IMPORT_ERROR = None


class InventoryModule(BaseInventoryPlugin):
    DEBUG = 4
    NAME = 'community.general.lxd'
    SNAP_SOCKET_URL = 'unix:/var/snap/lxd/common/lxd/unix.socket'
    SOCKET_URL = 'unix:/var/lib/lxd/unix.socket'

    @staticmethod
    def load_json_data(path):
        """Load json data

        Load json data from file

        Args:
            list(path): Path elements
            str(file_name): Filename of data
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(json_data): json data"""
        try:
            with open(path, 'r') as json_file:
                return json.load(json_file)
        except (IOError, json.decoder.JSONDecodeError) as err:
            raise AnsibleParserError('Could not load the test data from {0}: {1}'.format(to_native(path), to_native(err)))

    def save_json_data(self, path, file_name=None):
        """save data as json

        Save data as json file

        Args:
            list(path): Path elements
            str(file_name): Filename of data
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""

        if file_name:
            path.append(file_name)
        else:
            prefix = 'lxd_data-'
            time_stamp = time.strftime('%Y%m%d-%H%M%S')
            suffix = '.atd'
            path.append(prefix + time_stamp + suffix)

        try:
            cwd = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.abspath(os.path.join(cwd, *path)), 'w') as json_file:
                json.dump(self.data, json_file)
        except IOError as err:
            raise AnsibleParserError('Could not save data: {0}'.format(to_native(err)))

    def verify_file(self, path):
        """Check the config

        Return true/false if the config-file is valid for this plugin

        Args:
            str(path): path to the config
        Kwargs:
            None
        Raises:
            None
        Returns:
            bool(valid): is valid"""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('lxd.yaml', 'lxd.yml')):
                valid = True
            else:
                self.display.vvv('Inventory source not ending in "lxd.yaml" or "lxd.yml"')
        return valid

    @staticmethod
    def validate_url(url):
        """validate url

        check whether the url is correctly formatted

        Args:
            url
        Kwargs:
            None
        Raises:
            AnsibleError
        Returns:
            bool"""
        if not isinstance(url, str):
            return False
        if not url.startswith(('unix:', 'https:')):
            raise AnsibleError('URL is malformed: {0}'.format(to_native(url)))
        return True

    def _connect_to_socket(self):
        """connect to lxd socket

        Connect to lxd socket by provided url or defaults

        Args:
            None
        Kwargs:
            None
        Raises:
            AnsibleError
        Returns:
            None"""
        error_storage = {}
        url_list = [self.get_option('url'), self.SNAP_SOCKET_URL, self.SOCKET_URL]
        urls = (url for url in url_list if self.validate_url(url))
        for url in urls:
            try:
                socket_connection = LXDClient(url, self.client_key, self.client_cert, self.debug)
                return socket_connection
            except LXDClientException as err:
                error_storage[url] = err
        raise AnsibleError('No connection to the socket: {0}'.format(to_native(error_storage)))

    def _get_networks(self):
        """Get Networknames

        Returns all network config names

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            list(names): names of all network_configs"""
        # e.g. {'type': 'sync',
        #       'status': 'Success',
        #       'status_code': 200,
        #       'operation': '',
        #       'error_code': 0,
        #       'error': '',
        #       'metadata': ['/1.0/networks/lxdbr0']}
        network_configs = self.socket.do('GET', '/1.0/networks')
        return [m.split('/')[3] for m in network_configs['metadata']]

    def _get_containers(self):
        """Get Containernames

        Returns all containernames

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            list(names): names of all containers"""
        # e.g. {'type': 'sync',
        #       'status': 'Success',
        #       'status_code': 200,
        #       'operation': '',
        #       'error_code': 0,
        #       'error': '',
        #       'metadata': ['/1.0/containers/udemy-ansible-ubuntu-2004']}
        containers = self.socket.do('GET', '/1.0/containers')
        return [m.split('/')[3] for m in containers['metadata']]

    def _get_config(self, branch, name):
        """Get inventory of container

        Get config of container

        Args:
            str(branch): Name oft the API-Branch
            str(name): Name of Container
        Kwargs:
            None
        Source:
            https://github.com/lxc/lxd/blob/master/doc/rest-api.md
        Raises:
            None
        Returns:
            dict(config): Config of the container"""
        config = {}
        if isinstance(branch, (tuple, list)):
            config[name] = {branch[1]: self.socket.do('GET', '/1.0/{0}/{1}/{2}'.format(to_native(branch[0]), to_native(name), to_native(branch[1])))}
        else:
            config[name] = {branch: self.socket.do('GET', '/1.0/{0}/{1}'.format(to_native(branch), to_native(name)))}
        return config

    def get_container_data(self, names):
        """Create Inventory of the container

        Iterate through the different branches of the containers and collect Informations.

        Args:
            list(names): List of container names
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # tuple(('instances','metadata/templates')) to get section in branch
        # e.g. /1.0/instances/<name>/metadata/templates
        branches = ['containers', ('instances', 'state')]
        container_config = {}
        for branch in branches:
            for name in names:
                container_config['containers'] = self._get_config(branch, name)
                self.data = dict_merge(container_config, self.data)

    def get_network_data(self, names):
        """Create Inventory of the container

        Iterate through the different branches of the containers and collect Informations.

        Args:
            list(names): List of container names
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # tuple(('instances','metadata/templates')) to get section in branch
        # e.g. /1.0/instances/<name>/metadata/templates
        branches = [('networks', 'state')]
        network_config = {}
        for branch in branches:
            for name in names:
                try:
                    network_config['networks'] = self._get_config(branch, name)
                except LXDClientException:
                    network_config['networks'] = {name: None}
                self.data = dict_merge(network_config, self.data)

    def extract_network_information_from_container_config(self, container_name):
        """Returns the network interface configuration

        Returns the network ipv4 and ipv6 config of the container without local-link

        Args:
            str(container_name): Name oft he container
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(network_configuration): network config"""
        container_network_interfaces = self._get_data_entry('containers/{0}/state/metadata/network'.format(container_name))
        network_configuration = None
        if container_network_interfaces:
            network_configuration = {}
            gen_interface_names = [interface_name for interface_name in container_network_interfaces if interface_name != 'lo']
            for interface_name in gen_interface_names:
                gen_address = [address for address in container_network_interfaces[interface_name]['addresses'] if address.get('scope') != 'link']
                network_configuration[interface_name] = []
                for address in gen_address:
                    address_set = {}
                    address_set['family'] = address.get('family')
                    address_set['address'] = address.get('address')
                    address_set['netmask'] = address.get('netmask')
                    address_set['combined'] = address.get('address') + '/' + address.get('netmask')
                    network_configuration[interface_name].append(address_set)
        return network_configuration

    def get_prefered_container_network_interface(self, container_name):
        """Helper to get the prefered interface of thr container

        Helper to get the prefered interface provide by neme pattern from 'prefered_container_network_interface'.

        Args:
            str(containe_name): name of container
        Kwargs:
            None
        Raises:
            None
        Returns:
            str(prefered_interface): None or interface name"""
        container_network_interfaces = self._get_data_entry('inventory/{0}/network_interfaces'.format(container_name))
        prefered_interface = None  # init
        if container_network_interfaces:  # container have network interfaces
            # generator if interfaces which start with the desired pattern
            net_generator = [interface for interface in container_network_interfaces if interface.startswith(self.prefered_container_network_interface)]
            selected_interfaces = []  # init
            for interface in net_generator:
                selected_interfaces.append(interface)
            if len(selected_interfaces) > 0:
                prefered_interface = sorted(selected_interfaces)[0]
        return prefered_interface

    def get_container_vlans(self, container_name):
        """Get VLAN(s) from container

        Helper to get the VLAN_ID from the container

        Args:
            str(containe_name): name of container
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # get network device configuration and store {network: vlan_id}
        network_vlans = {}
        for network in self._get_data_entry('networks'):
            if self._get_data_entry('state/metadata/vlan/vid', data=self.data['networks'].get(network)):
                network_vlans[network] = self._get_data_entry('state/metadata/vlan/vid', data=self.data['networks'].get(network))

        # get networkdevices of container and return
        # e.g.
        # "eth0":{ "name":"eth0",
        #          "network":"lxdbr0",
        #          "type":"nic"},
        vlan_ids = {}
        devices = self._get_data_entry('containers/{0}/containers/metadata/expanded_devices'.format(to_native(container_name)))
        for device in devices:
            if 'network' in devices[device]:
                if devices[device]['network'] in network_vlans:
                    vlan_ids[devices[device].get('network')] = network_vlans[devices[device].get('network')]
        return vlan_ids if vlan_ids else None

    def _get_data_entry(self, path, data=None, delimiter='/'):
        """Helper to get data

        Helper to get data from self.data by a path like 'path/to/target'
        Attention: Escaping of the delimiter is not (yet) provided.

        Args:
            str(path): path to nested dict
        Kwargs:
            dict(data): datastore
            str(delimiter): delimiter in Path.
        Raises:
            None
        Returns:
            *(value)"""
        try:
            if not data:
                data = self.data
            if delimiter in path:
                path = path.split(delimiter)

            if isinstance(path, list) and len(path) > 1:
                data = data[path.pop(0)]
                path = delimiter.join(path)
                return self._get_data_entry(path, data, delimiter)  # recursion
            return data[path]
        except KeyError:
            return None

    def _set_data_entry(self, container_name, key, value, path=None):
        """Helper to save data

        Helper to save the data in self.data
        Detect if data is allready in branch and use dict_merge() to prevent that branch is overwritten.

        Args:
            str(container_name): name of container
            str(key): same as dict
            *(value): same as dict
        Kwargs:
            str(path): path to branch-part
        Raises:
            AnsibleParserError
        Returns:
            None"""
        if not path:
            path = self.data['inventory']
        if container_name not in path:
            path[container_name] = {}

        try:
            if isinstance(value, dict) and key in path[container_name]:
                path[container_name] = dict_merge(value, path[container_name][key])
            else:
                path[container_name][key] = value
        except KeyError as err:
            raise AnsibleParserError("Unable to store Informations: {0}".format(to_native(err)))

    def extract_information_from_container_configs(self):
        """Process configuration information

        Preparation of the data

        Args:
            dict(configs): Container configurations
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # create branch "inventory"
        if 'inventory' not in self.data:
            self.data['inventory'] = {}

        for container_name in self.data['containers']:
            self._set_data_entry(container_name, 'os', self._get_data_entry(
                'containers/{0}/containers/metadata/config/image.os'.format(container_name)))
            self._set_data_entry(container_name, 'release', self._get_data_entry(
                'containers/{0}/containers/metadata/config/image.release'.format(container_name)))
            self._set_data_entry(container_name, 'version', self._get_data_entry(
                'containers/{0}/containers/metadata/config/image.version'.format(container_name)))
            self._set_data_entry(container_name, 'profile', self._get_data_entry(
                'containers/{0}/containers/metadata/profiles'.format(container_name)))
            self._set_data_entry(container_name, 'location', self._get_data_entry(
                'containers/{0}/containers/metadata/location'.format(container_name)))
            self._set_data_entry(container_name, 'state', self._get_data_entry(
                'containers/{0}/containers/metadata/config/volatile.last_state.power'.format(container_name)))
            self._set_data_entry(container_name, 'network_interfaces', self.extract_network_information_from_container_config(container_name))
            self._set_data_entry(container_name, 'preferred_interface', self.get_prefered_container_network_interface(container_name))
            self._set_data_entry(container_name, 'vlan_ids', self.get_container_vlans(container_name))

    def build_inventory_network(self, container_name):
        """Add the network interfaces of the container to the inventory

        Logic:
            - if the container have no interface -> 'ansible_connection: local'
            - get preferred_interface & prefered_container_network_family -> 'ansible_connection: ssh' & 'ansible_host: <IP>'
            - first Interface from: network_interfaces prefered_container_network_family -> 'ansible_connection: ssh' & 'ansible_host: <IP>'

        Args:
            str(container_name): name of container
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""

        def interface_selection(container_name):
            """Select container Interface for inventory

            Logic:
                - get preferred_interface & prefered_container_network_family -> str(IP)
                - first Interface from: network_interfaces prefered_container_network_family -> str(IP)

            Args:
                str(container_name): name of container
            Kwargs:
                None
            Raises:
                None
            Returns:
                dict(interface_name: ip)"""
            prefered_interface = self._get_data_entry('inventory/{0}/preferred_interface'.format(container_name))  # name or None
            prefered_container_network_family = self.prefered_container_network_family

            ip_address = ''
            if prefered_interface:
                interface = self._get_data_entry('inventory/{0}/network_interfaces/{1}'.format(container_name, prefered_interface))
                for config in interface:
                    if config['family'] == prefered_container_network_family:
                        ip_address = config['address']
                        break
            else:
                interface = self._get_data_entry('inventory/{0}/network_interfaces'.format(container_name))
                for config in interface:
                    if config['family'] == prefered_container_network_family:
                        ip_address = config['address']
                        break
            return ip_address

        if self._get_data_entry('inventory/{0}/network_interfaces'.format(container_name)):  # container have network interfaces
            if self._get_data_entry('inventory/{0}/preferred_interface'.format(container_name)):  # container have a preferred interface
                self.inventory.set_variable(container_name, 'ansible_connection', 'ssh')
                self.inventory.set_variable(container_name, 'ansible_host', interface_selection(container_name))
        else:
            self.inventory.set_variable(container_name, 'ansible_connection', 'local')

    def build_inventory_hosts(self):
        """Build host-part dynamic inventory

        Build the host-part of the dynamic inventory.
        Add Hosts and host_vars to the inventory.

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        for container_name in self.data['inventory']:
            # Only consider containers that match the "state" filter, if self.state is not None
            if self.filter:
                if self.filter.lower() != self._get_data_entry('inventory/{0}/state'.format(container_name)).lower():
                    continue
            # add container
            self.inventory.add_host(container_name)
            # add network informations
            self.build_inventory_network(container_name)
            # add os
            self.inventory.set_variable(container_name, 'ansible_lxd_os', self._get_data_entry('inventory/{0}/os'.format(container_name)).lower())
            # add release
            self.inventory.set_variable(container_name, 'ansible_lxd_release', self._get_data_entry('inventory/{0}/release'.format(container_name)).lower())
            # add profile
            self.inventory.set_variable(container_name, 'ansible_lxd_profile', self._get_data_entry('inventory/{0}/profile'.format(container_name)))
            # add state
            self.inventory.set_variable(container_name, 'ansible_lxd_state', self._get_data_entry('inventory/{0}/state'.format(container_name)).lower())
            # add location information
            if self._get_data_entry('inventory/{0}/location'.format(container_name)) != "none":  # wrong type by lxd 'none' != 'None'
                self.inventory.set_variable(container_name, 'ansible_lxd_location', self._get_data_entry('inventory/{0}/location'.format(container_name)))
            # add VLAN_ID information
            if self._get_data_entry('inventory/{0}/vlan_ids'.format(container_name)):
                self.inventory.set_variable(container_name, 'ansible_lxd_vlan_ids', self._get_data_entry('inventory/{0}/vlan_ids'.format(container_name)))

    def build_inventory_groups_location(self, group_name):
        """create group by attribute: location

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        for container_name in self.inventory.hosts:
            if 'ansible_lxd_location' in self.inventory.get_host(container_name).get_vars():
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups_pattern(self, group_name):
        """create group by name pattern

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        regex_pattern = self.groupby[group_name].get('attribute')

        for container_name in self.inventory.hosts:
            result = re.search(regex_pattern, container_name)
            if result:
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups_network_range(self, group_name):
        """check if IP is in network-class

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        try:
            network = ipaddress.ip_network(to_text(self.groupby[group_name].get('attribute')))
        except ValueError as err:
            raise AnsibleParserError(
                'Error while parsing network range {0}: {1}'.format(self.groupby[group_name].get('attribute'), to_native(err)))

        for container_name in self.inventory.hosts:
            if self.data['inventory'][container_name].get('network_interfaces') is not None:
                for interface in self.data['inventory'][container_name].get('network_interfaces'):
                    for interface_family in self.data['inventory'][container_name].get('network_interfaces')[interface]:
                        try:
                            address = ipaddress.ip_address(to_text(interface_family['address']))
                            if address.version == network.version and address in network:
                                self.inventory.add_child(group_name, container_name)
                        except ValueError:
                            # Ignore invalid IP addresses returned by lxd
                            pass

    def build_inventory_groups_os(self, group_name):
        """create group by attribute: os

        Args:
            str(group_name): Group name
        Kwargs:
            Noneself.data['inventory'][container_name][interface]
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        gen_containers = [
            container_name for container_name in self.inventory.hosts
            if 'ansible_lxd_os' in self.inventory.get_host(container_name).get_vars()]
        for container_name in gen_containers:
            if self.groupby[group_name].get('attribute').lower() == self.inventory.get_host(container_name).get_vars().get('ansible_lxd_os'):
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups_release(self, group_name):
        """create group by attribute: release

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        gen_containers = [
            container_name for container_name in self.inventory.hosts
            if 'ansible_lxd_release' in self.inventory.get_host(container_name).get_vars()]
        for container_name in gen_containers:
            if self.groupby[group_name].get('attribute').lower() == self.inventory.get_host(container_name).get_vars().get('ansible_lxd_release'):
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups_profile(self, group_name):
        """create group by attribute: profile

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        gen_containers = [
            container_name for container_name in self.inventory.hosts.keys()
            if 'ansible_lxd_profile' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groupby[group_name].get('attribute').lower() in self.inventory.get_host(container_name).get_vars().get('ansible_lxd_profile'):
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups_vlanid(self, group_name):
        """create group by attribute: vlanid

        Args:
            str(group_name): Group name
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        # maybe we just want to expand one group
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)

        gen_containers = [
            container_name for container_name in self.inventory.hosts.keys()
            if 'ansible_lxd_vlan_ids' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groupby[group_name].get('attribute') in self.inventory.get_host(container_name).get_vars().get('ansible_lxd_vlan_ids').values():
                self.inventory.add_child(group_name, container_name)

    def build_inventory_groups(self):
        """Build group-part dynamic inventory

        Build the group-part of the dynamic inventory.
        Add groups to the inventory.

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""

        def group_type(group_name):
            """create groups defined by lxd.yml or defaultvalues

            create groups defined by lxd.yml or defaultvalues
            supportetd:
                * 'location'
                * 'pattern'
                * 'network_range'
                * 'os'
                * 'release'
                * 'profile'
                * 'vlanid'

            Args:
                str(group_name): Group name
            Kwargs:
                None
            Raises:
                None
            Returns:
                None"""

            # Due to the compatibility with python 2 no use of map
            if self.groupby[group_name].get('type') == 'location':
                self.build_inventory_groups_location(group_name)
            elif self.groupby[group_name].get('type') == 'pattern':
                self.build_inventory_groups_pattern(group_name)
            elif self.groupby[group_name].get('type') == 'network_range':
                self.build_inventory_groups_network_range(group_name)
            elif self.groupby[group_name].get('type') == 'os':
                self.build_inventory_groups_os(group_name)
            elif self.groupby[group_name].get('type') == 'release':
                self.build_inventory_groups_release(group_name)
            elif self.groupby[group_name].get('type') == 'profile':
                self.build_inventory_groups_profile(group_name)
            elif self.groupby[group_name].get('type') == 'vlanid':
                self.build_inventory_groups_vlanid(group_name)
            else:
                raise AnsibleParserError('Unknown group type: {0}'.format(to_native(group_name)))

        if self.groupby:
            for group_name in self.groupby:
                if not group_name.isalnum():
                    raise AnsibleParserError('Invalid character(s) in groupname: {0}'.format(to_native(group_name)))
                group_type(group_name)

    def build_inventory(self):
        """Build dynamic inventory

        Build the dynamic inventory.

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""

        self.build_inventory_hosts()
        self.build_inventory_groups()

    def _populate(self):
        """Return the hosts and groups

        Returns the processed container configurations from the lxd import

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""

        if len(self.data) == 0:  # If no data is injected by unittests open socket
            self.socket = self._connect_to_socket()
            self.get_container_data(self._get_containers())
            self.get_network_data(self._get_networks())

        self.extract_information_from_container_configs()

        # self.display.vvv(self.save_json_data([os.path.abspath(__file__)]))

        self.build_inventory()

    def parse(self, inventory, loader, path, cache):
        """Return dynamic inventory from source

        Returns the processed inventory from the lxd import

        Args:
            str(inventory): inventory object with existing data and
                            the methods to add hosts/groups/variables
                            to inventory
            str(loader):    Ansible's DataLoader
            str(path):      path to the config
            bool(cache):    use or avoid caches
        Kwargs:
            None
        Raises:
            AnsibleParserError
        Returns:
            None"""
        if IPADDRESS_IMPORT_ERROR:
            raise_from(
                AnsibleError('another_library must be installed to use this plugin'),
                IPADDRESS_IMPORT_ERROR)

        super(InventoryModule, self).parse(inventory, loader, path, cache=False)
        # Read the inventory YAML file
        self._read_config_data(path)
        try:
            self.client_key = self.get_option('client_key')
            self.client_cert = self.get_option('client_cert')
            self.debug = self.DEBUG
            self.data = {}  # store for inventory-data
            self.groupby = self.get_option('groupby')
            self.plugin = self.get_option('plugin')
            self.prefered_container_network_family = self.get_option('prefered_container_network_family')
            self.prefered_container_network_interface = self.get_option('prefered_container_network_interface')
            if self.get_option('state').lower() == 'none':  # none in config is str()
                self.filter = None
            else:
                self.filter = self.get_option('state').lower()
            self.trust_password = self.get_option('trust_password')
            self.url = self.get_option('url')
        except Exception as err:
            raise AnsibleParserError(
                'All correct options required: {0}'.format(to_native(err)))
        # Call our internal helper to populate the dynamic inventory
        self._populate()
