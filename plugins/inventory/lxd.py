# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Frank Dornheim <dornheim@posteo.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: lxd
    plugin_type: inventory
    short_description: Returns Ansible inventory from lxd host
    description:
        - Get inventory from the lxd
        - Uses a YAML configuration file that ends with 'lxd.(yml|yaml)'.
    version_added: "2.1.0"
    author: "Frank Dornheim (@conloos)"
    options:
        plugin:
            description: token that ensures this is a source file for the 'lxd' plugin
            required: true
            choices: ['lxd']
        url:
            description:
            - The unix domain socket path or the https URL for the LXD server.
            - mostly: unix:/var/lib/lxd/unix.socket or unix:/var/snap/lxd/common/lxd/unix.socket
            required: false
            type: str
        client_key:
            description:
            - The client certificate key file path.
            required: false
            aliases: [ key_file ]
            default: $HOME/.config/lxc/client.key
            type: path
        client_cert:
            description:
            - The client certificate file path.
            required: false
            aliases: [ cert_file ]
            default: $HOME/.config/lxc/client.crt
            type: path
        trust_password:
            description:
            - The client trusted password.
            - You need to set this password on the LXD server before
                running this module using the following command.
                lxc config set core.trust_password <some random password>
                See (https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/)
            - If trust_password is set, this module send a request for
                authentication before sending any requests.
            required: false
            type: str
        state:
            description: Filter the container according to the current status
            required: false
            type: str
            default: none
            choices: ['STOPPED', 'STARTING', 'RUNNING', 'none']
        prefered_container_network_interface:
            description: if a container has multiple network interfaces, which one is the prefered as pattern
            required: false
            type: str
            default: eth
            notes:
              - combined with the first number that can be found e.g. eth + 0
        prefered_container_network_family:
            description: if a container has multiple network interfaces, which one is the prefered by family
            required: false
            type: str
            default: inet
            choices: ['inet', 'inet6']
            notes:
              - inet == ipv4
              - inet6 == ipv6
        groups:
            description: Group the results
            required: false
            type: json
            default: none
            notes:
              - lxd location: no idea need sample
              - pattern: samba* or regex
              - network_range: 192.168.0.0/24
              - os: ubuntu
              - release: groovy
              - profile: default
              - vlanid: works on defined networks e.g. br0 with vlan_default == 666
        selftest:
            description: Load default data to test plugIn
            required: false
            type: bool
            default: false
        dumpdata:
            description: dump out data to debug
            required: false
            type: bool
            default: false
'''

EXAMPLES = '''
# simple lxd.yml
plugin: lxd
url: unix:/var/snap/lxd/common/lxd/unix.socket

# simple lxd.yml including filter
plugin: lxd
url: unix:/var/snap/lxd/common/lxd/unix.socket
state: RUNNING

# grouping lxd.yml
plugin: lxd
state: RUNNING
groups:
  SMB-Server:
    type: pattern
    attribute: samba
  vlan666:
    type: vlanid
    attribute: 666
'''

import binascii
import json
import re
import time
import os
import socket
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.module_utils._text import to_native
from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.module_utils.lxd import LXDClient, LXDClientException


class InventoryModule(BaseInventoryPlugin):
    DEBUG = 4
    NAME = 'lxd'
    SNAP_SOCKET_URL = 'unix:/var/snap/lxd/common/lxd/unix.socket'
    SOCKET_URL = 'unix:/var/lib/lxd/unix.socket'
    TEST_PATH = ['test']

    @staticmethod
    def load_json_data(path, file_name=None):
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

        if file_name:
            path.append(file_name)
        else:
            path.append('lxd_inventory.atd')

        try:
            cwd = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.abspath(os.path.join(cwd, *path)), 'r') as json_file:
                return json.load(json_file)
        except IOError as err:
            raise AnsibleParserError('Could not load the test data: {0}'.format(to_native(err))) from IOError

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
            raise AnsibleParserError('Could not save data: {0}'.format(to_native(err))) from IOError

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
        network_configs = self.socket.do('GET', '/1.0/networks')
        # e.g. {'type': 'sync',
        #       'status': 'Success',
        #       'status_code': 200,
        #       'operation': '',
        #       'error_code': 0,
        #       'error': '',
        #       'metadata': ['/1.0/networks/lxdbr0']}
        names = []
        for index in network_configs['metadata']:
            # e.g. ['', '1.0', 'networks', 'lxdbr0']
            names.append(index.split('/')[3])
        return names

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
        names = []
        for index in containers['metadata']:
            # e.g. ['', '1.0', 'containers', 'udemy-ansible-ubuntu-2004']
            names.append(index.split('/')[3])
        return names

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
        if isinstance(branch, tuple):
            config[name] = {branch[1]: self.socket.do('GET', '/1.0/{0}/{1}/{2}'.format(to_native(branch[0]), to_native(name), to_native(branch[1])))}
        else:
            config[name] = {branch: self.socket.do('GET', '/1.0/{0}/{1}'.format(to_native(branch), to_native(name)))}
        return config

    def _merge_dicts(self, source, destination):
        """merge dicts

        Merge two dicts without overwrite the branches of the destination dictionary.

        Args:
            diclearct(source): Source Dictionary
            dict(destination): Destination Dictionary
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(destination): merged Dictionary"""
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self._merge_dicts(value, node)
            else:
                destination[key] = value
        return destination

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
                self.data = self._merge_dicts(container_config, self.data)

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
                self.data = self._merge_dicts(network_config, self.data)

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
            # generator if interfases which start with the desired pattern
            net_generaor = [interface for interface in container_network_interfaces if interface.startswith(self.prefered_container_network_interface)]
            selected_interfaces = []  # init
            for interface in net_generaor:
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
            if 'network' in devices[device].keys():
                if devices[device]['network'] in network_vlans.keys():
                    vlan_ids[devices[device].get('network')] = network_vlans[devices[device].get('network')]
        if len(vlan_ids) == 0:
            return None
        return vlan_ids

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
        Detect if data is allready in branch and use _merge_dicts() to prevent that branch is overwritten.

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
            if isinstance(value, dict) and key in path[container_name].keys():
                path[container_name] = self._merge_dicts(value, path[container_name][key])
            else:
                path[container_name][key] = value
        except KeyError as err:
            raise AnsibleParserError("Unable to store Informations: {0}".format(to_native(err))) from KeyError

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

        for container_name in self.data['containers'].keys():
            self._set_data_entry(container_name, 'os', self._get_data_entry('containers/{0}/containers/metadata/config/image.os'.format(container_name)))
            self._set_data_entry(container_name, 'release', self._get_data_entry('containers/{0}/containers/metadata/config/image.release'.format(container_name)))
            self._set_data_entry(container_name, 'version', self._get_data_entry('containers/{0}/containers/metadata/config/image.version'.format(container_name)))
            self._set_data_entry(container_name, 'profile', self._get_data_entry('containers/{0}/containers/metadata/profiles'.format(container_name)))
            self._set_data_entry(container_name, 'location', self._get_data_entry('containers/{0}/containers/metadata/location'.format(container_name)))
            self._set_data_entry(container_name, 'state', self._get_data_entry('containers/{0}/containers/metadata/config/volatile.last_state.power'.format(container_name)))
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
        for container_name in self.data['inventory'].keys():
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

        for container_name in self.data['inventory'].keys():
            if 'ansible_lxd_location' in self.inventory.get_host(container_name).get_vars().keys():
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

        regex_pattern = self.groups[group_name].get('attribute')

        for container_name in self.data['inventory'].keys():
            result = re.search(regex_pattern, container_name)
            if result:
                self.inventory.add_child(group_name, container_name)

    def ip_in_subnetwork(self, ip_address, subnetwork):
        """Test if IP is in IP-Subnet.

        Both IPv4 addresses/subnetworks (e.g. "192.168.178.99" and "192.168.1.0/24") and
             IPv6 addresses/subnetworks (e.g. "fd42:bd00:7b11:2167:216:3eff:fe21:e86b" and "fd42:bd00:7b11:2167:216:3eff::/44") are accepted.
        Source: https://diego.assencio.com/?index=85e407d6c771ba2bc5f02b17714241e2

        Args:
            str(ip_address): IP-Address e.g. 192.168.178.99
            str(subnetwork): IP-Subnet e.g. 192.168.178.0/24
        Kwargs:
            None
        Raises:
            None
        Returns:
            bool:   True if the given IP address belongs to the subnetwork expressed in CIDR notation, otherwise False.
                    Both parameters are strings."""
        (ip_integer, version1) = self.ip_to_integer(ip_address)
        (ip_lower, ip_upper, version2) = self.subnetwork_to_ip_range(subnetwork)

        if version1 != version2:
            raise ValueError("incompatible IP versions")
        return ip_lower <= ip_integer <= ip_upper

    @staticmethod
    def ip_to_integer(ip_address):
        """Converts an IP address

        Converts an IP address expressed as a string to its representation as an integer value and returns a tuple
        (ip_integer, version), with version being the IP version (either 4 or 6).

        Args:
            str(ip_address): IP-Address e.g. 192.168.178.99 or fd42:bd00:7b11:2167:216:3eff:fe21:e86b
        Kwargs:
            None
        Raises:
            None
        Returns:
            tuple(
                int(ip_integer): int ip representation
                int(ip version): 4 for IPv4 or 6 for IPv6
                )"""
        # try parsing the IP address first as IPv4, then as IPv6
        for version in (socket.AF_INET, socket.AF_INET6):
            try:
                ip_hex = socket.inet_pton(version, ip_address)
                ip_integer = int(binascii.hexlify(ip_hex), 16)
                return (ip_integer, 4 if version == socket.AF_INET else 6)
            except Exception:
                pass
        raise ValueError("invalid IP address")

    @staticmethod
    def subnetwork_to_ip_range(subnetwork):
        """Returns the uper and lower ip representations of the IP-Subnet.

        Returns a tuple (ip_lower, ip_upper, version) containing the integer values of the lower and upper IP addresses respectively
        in a subnetwork expressed in CIDR notation (as a string), with version being the subnetwork IP version (either 4 or 6).

        Args:
            str(subnetwork): IP-Subnet e.g. 192.168.178.0/24 or fd42:bd00:7b11:2167:216:3eff::/44
        Kwargs:
            None
        Raises:
            None
        Returns:
            tuple(
                int(ip_lower): int ip representation lower subnet end
                int(ip_upper): int ip representation upper subnet end
                int(ip version): 4 for IPv4 or 6 for IPv6
                )"""
        try:
            fragments = subnetwork.split('/')
            network_prefix = fragments[0]
            netmask_len = int(fragments[1])

            # try parsing the subnetwork first as IPv4, then as IPv6
            for version in (socket.AF_INET, socket.AF_INET6):
                ip_len = 32 if version == socket.AF_INET else 128
                try:
                    suffix_mask = (1 << (ip_len - netmask_len)) - 1
                    netmask = ((1 << ip_len) - 1) - suffix_mask
                    ip_hex = socket.inet_pton(version, network_prefix)
                    ip_lower = int(binascii.hexlify(ip_hex), 16) & netmask
                    ip_upper = ip_lower + suffix_mask
                    return (ip_lower,
                            ip_upper,
                            4 if version == socket.AF_INET else 6)
                except Exception:
                    pass
        except Exception:
            pass
        raise ValueError("invalid subnetwork")

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

        for container_name in self.data['inventory'].keys():
            if self.data['inventory'][container_name].get('network_interfaces') is not None:
                for interface in self.data['inventory'][container_name].get('network_interfaces'):
                    for interface_family in self.data['inventory'][container_name].get('network_interfaces')[interface]:
                        try:
                            if self.ip_in_subnetwork(interface_family['address'], self.groups[group_name].get('attribute')):
                                self.inventory.add_child(group_name, container_name)
                        except ValueError:
                            # catch ipv4/ipv6 matching incompatibility errors
                            continue

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

        gen_containers = [container_name for container_name in self.data['inventory'].keys() if 'ansible_lxd_os' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groups[group_name].get('attribute').lower() == self.inventory.get_host(container_name).get_vars().get('ansible_lxd_os'):
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

        gen_containers = [container_name for container_name in self.data['inventory'].keys() if 'ansible_lxd_release' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groups[group_name].get('attribute').lower() == self.inventory.get_host(container_name).get_vars().get('ansible_lxd_release'):
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

        gen_containers = [container_name for container_name in self.data['inventory'].keys() if 'ansible_lxd_profile' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groups[group_name].get('attribute').lower() in self.inventory.get_host(container_name).get_vars().get('ansible_lxd_profile'):
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

        gen_containers = [container_name for container_name in self.data['inventory'].keys() if 'ansible_lxd_vlan_ids' in self.inventory.get_host(container_name).get_vars().keys()]
        for container_name in gen_containers:
            if self.groups[group_name].get('attribute') in self.inventory.get_host(container_name).get_vars().get('ansible_lxd_vlan_ids').values():
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
            if self.groups[group_name].get('type') == 'location':
                self.build_inventory_groups_location(group_name)
            elif self.groups[group_name].get('type') == 'pattern':
                self.build_inventory_groups_pattern(group_name)
            elif self.groups[group_name].get('type') == 'network_range':
                self.build_inventory_groups_network_range(group_name)
            elif self.groups[group_name].get('type') == 'os':
                self.build_inventory_groups_os(group_name)
            elif self.groups[group_name].get('type') == 'release':
                self.build_inventory_groups_release(group_name)
            elif self.groups[group_name].get('type') == 'profile':
                self.build_inventory_groups_profile(group_name)
            elif self.groups[group_name].get('type') == 'vlanid':
                self.build_inventory_groups_vlanid(group_name)
            else:
                raise AnsibleParserError('Unknown group type: {0}'.format(to_native(group_name)))

        for group_name in self.groups.keys():
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
        if self.selftest:
            self.data = self.load_json_data(self.TEST_PATH)
        else:
            self.socket = self._connect_to_socket()
            self.get_container_data(self._get_containers())
            self.get_network_data(self._get_networks())

        self.extract_information_from_container_configs()

        if self.dump_data:
            self.save_json_data(self.TEST_PATH)
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
            AnsibleParseError
        Returns:
            None"""
        super(InventoryModule, self).parse(inventory, loader, path, cache=False)
        # Read the inventory YAML file
        self._read_config_data(path)
        try:
            self.client_key = self.get_option('client_key')
            self.client_cert = self.get_option('client_cert')
            self.debug = self.DEBUG
            self.data = {}  # store for inventory-data
            self.dump_data = self.get_option('dumpdata')
            self.groups = self.get_option('groups')
            self.plugin = self.get_option('plugin')
            self.prefered_container_network_family = self.get_option('prefered_container_network_family')
            self.prefered_container_network_interface = self.get_option('prefered_container_network_interface')
            self.selftest = self.get_option('selftest')
            self.filter = self.get_option('state')
            self.trust_password = self.get_option('trust_password')
            self.url = self.get_option('url')
        except Exception as err:
            raise AnsibleParserError(
                'All correct options required: {0}'.format(to_native(err))) from Exception
        # Call our internal helper to populate the dynamic inventory
        self._populate()
