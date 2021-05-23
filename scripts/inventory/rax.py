#!/usr/bin/env python

# (c) 2013, Jesse Keating <jesse.keating@rackspace.com,
#           Paul Durivage <paul.durivage@rackspace.com>,
#           Matt Martz <matt@sivel.net>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

"""
Rackspace Cloud Inventory

Authors:
    Jesse Keating <jesse.keating@rackspace.com,
    Paul Durivage <paul.durivage@rackspace.com>,
    Matt Martz <matt@sivel.net>


Description:
    Generates inventory that Ansible can understand by making API request to
    Rackspace Public Cloud API

    When run against a specific host, this script returns variables similar to:
        rax_os-ext-sts_task_state
        rax_addresses
        rax_links
        rax_image
        rax_os-ext-sts_vm_state
        rax_flavor
        rax_id
        rax_rax-bandwidth_bandwidth
        rax_user_id
        rax_os-dcf_diskconfig
        rax_accessipv4
        rax_accessipv6
        rax_progress
        rax_os-ext-sts_power_state
        rax_metadata
        rax_status
        rax_updated
        rax_hostid
        rax_name
        rax_created
        rax_tenant_id
        rax_loaded

Configuration:
    rax.py can be configured using a rax.ini file or via environment
    variables. The rax.ini file should live in the same directory along side
    this script.

    The section header for configuration values related to this
    inventory plugin is [rax]

    [rax]
    creds_file = ~/.rackspace_cloud_credentials
    regions = IAD,ORD,DFW
    env = prod
    meta_prefix = meta
    access_network = public
    access_ip_version = 4

    Each of these configurations also has a corresponding environment variable.
    An environment variable will override a configuration file value.

    creds_file:
        Environment Variable: RAX_CREDS_FILE

        An optional configuration that points to a pyrax-compatible credentials
        file.

        If not supplied, rax.py will look for a credentials file
        at ~/.rackspace_cloud_credentials.  It uses the Rackspace Python SDK,
        and therefore requires a file formatted per the SDK's specifications.

        https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md

    regions:
        Environment Variable: RAX_REGION

        An optional environment variable to narrow inventory search
        scope. If used, needs a value like ORD, DFW, SYD (a Rackspace
        datacenter) and optionally accepts a comma-separated list.

    environment:
        Environment Variable: RAX_ENV

        A configuration that will use an environment as configured in
        ~/.pyrax.cfg, see
        https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md

    meta_prefix:
        Environment Variable: RAX_META_PREFIX
        Default: meta

        A configuration that changes the prefix used for meta key/value groups.
        For compatibility with ec2.py set to "tag"

    access_network:
        Environment Variable: RAX_ACCESS_NETWORK
        Default: public

        A configuration that will tell the inventory script to use a specific
        server network to determine the ansible_ssh_host value. If no address
        is found, ansible_ssh_host will not be set. Accepts a comma-separated
        list of network names, the first found wins.

    access_ip_version:
        Environment Variable: RAX_ACCESS_IP_VERSION
        Default: 4

        A configuration related to "access_network" that will attempt to
        determine the ansible_ssh_host value for either IPv4 or IPv6. If no
        address is found, ansible_ssh_host will not be set.
        Acceptable values are: 4 or 6. Values other than 4 or 6
        will be ignored, and 4 will be used. Accepts a comma-separated list,
        the first found wins.

Examples:
    List server instances
    $ RAX_CREDS_FILE=~/.raxpub rax.py --list

    List servers in ORD datacenter only
    $ RAX_CREDS_FILE=~/.raxpub RAX_REGION=ORD rax.py --list

    List servers in ORD and DFW datacenters
    $ RAX_CREDS_FILE=~/.raxpub RAX_REGION=ORD,DFW rax.py --list

    Get server details for server named "server.example.com"
    $ RAX_CREDS_FILE=~/.raxpub rax.py --host server.example.com

    Use the instance private IP to connect (instead of public IP)
    $ RAX_CREDS_FILE=~/.raxpub RAX_ACCESS_NETWORK=private rax.py --list
"""

import os
import re
import sys
import argparse
import warnings
import collections

from ansible.module_utils.six import iteritems
from ansible.module_utils.six.moves import configparser as ConfigParser

import json

try:
    import pyrax
    from pyrax.utils import slugify
except ImportError:
    sys.exit('pyrax is required for this module')

from time import time

from ansible.constants import get_config
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.six import text_type

NON_CALLABLES = (text_type, str, bool, dict, int, list, type(None))


def load_config_file():
    p = ConfigParser.ConfigParser()
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'rax.ini')
    try:
        p.read(config_file)
    except ConfigParser.Error:
        return None
    else:
        return p


def rax_slugify(value):
    return 'rax_%s' % (re.sub(r'[^\w-]', '_', value).lower().lstrip('_'))


def to_dict(obj):
    instance = {}
    for key in dir(obj):
        value = getattr(obj, key)
        if isinstance(value, NON_CALLABLES) and not key.startswith('_'):
            key = rax_slugify(key)
            instance[key] = value

    return instance


def host(regions, hostname):
    hostvars = {}

    for region in regions:
        # Connect to the region
        cs = pyrax.connect_to_cloudservers(region=region)
        for server in cs.servers.list():
            if server.name == hostname:
                for key, value in to_dict(server).items():
                    hostvars[key] = value

                # And finally, add an IP address
                hostvars['ansible_ssh_host'] = server.accessIPv4
    print(json.dumps(hostvars, sort_keys=True, indent=4))


def _list_into_cache(regions):
    groups = collections.defaultdict(list)
    hostvars = collections.defaultdict(dict)
    images = {}
    cbs_attachments = collections.defaultdict(dict)

    prefix = get_config(p, 'rax', 'meta_prefix', 'RAX_META_PREFIX', 'meta')

    try:
        # Ansible 2.3+
        networks = get_config(p, 'rax', 'access_network',
                              'RAX_ACCESS_NETWORK', 'public', value_type='list')
    except TypeError:
        # Ansible 2.2.x and below
        # pylint: disable=unexpected-keyword-arg
        networks = get_config(p, 'rax', 'access_network',
                              'RAX_ACCESS_NETWORK', 'public', islist=True)
    try:
        try:
            # Ansible 2.3+
            ip_versions = map(int, get_config(p, 'rax', 'access_ip_version',
                                              'RAX_ACCESS_IP_VERSION', 4, value_type='list'))
        except TypeError:
            # Ansible 2.2.x and below
            # pylint: disable=unexpected-keyword-arg
            ip_versions = map(int, get_config(p, 'rax', 'access_ip_version',
                                              'RAX_ACCESS_IP_VERSION', 4, islist=True))
    except Exception:
        ip_versions = [4]
    else:
        ip_versions = [v for v in ip_versions if v in [4, 6]]
        if not ip_versions:
            ip_versions = [4]

    # Go through all the regions looking for servers
    for region in regions:
        # Connect to the region
        cs = pyrax.connect_to_cloudservers(region=region)
        if cs is None:
            warnings.warn(
                'Connecting to Rackspace region "%s" has caused Pyrax to '
                'return None. Is this a valid region?' % region,
                RuntimeWarning)
            continue
        for server in cs.servers.list():
            # Create a group on region
            groups[region].append(server.name)

            # Check if group metadata key in servers' metadata
            group = server.metadata.get('group')
            if group:
                groups[group].append(server.name)

            for extra_group in server.metadata.get('groups', '').split(','):
                if extra_group:
                    groups[extra_group].append(server.name)

            # Add host metadata
            for key, value in to_dict(server).items():
                hostvars[server.name][key] = value

            hostvars[server.name]['rax_region'] = region

            for key, value in iteritems(server.metadata):
                groups['%s_%s_%s' % (prefix, key, value)].append(server.name)

            groups['instance-%s' % server.id].append(server.name)
            groups['flavor-%s' % server.flavor['id']].append(server.name)

            # Handle boot from volume
            if not server.image:
                if not cbs_attachments[region]:
                    cbs = pyrax.connect_to_cloud_blockstorage(region)
                    for vol in cbs.list():
                        if boolean(vol.bootable, strict=False):
                            for attachment in vol.attachments:
                                metadata = vol.volume_image_metadata
                                server_id = attachment['server_id']
                                cbs_attachments[region][server_id] = {
                                    'id': metadata['image_id'],
                                    'name': slugify(metadata['image_name'])
                                }
                image = cbs_attachments[region].get(server.id)
                if image:
                    server.image = {'id': image['id']}
                    hostvars[server.name]['rax_image'] = server.image
                    hostvars[server.name]['rax_boot_source'] = 'volume'
                    images[image['id']] = image['name']
            else:
                hostvars[server.name]['rax_boot_source'] = 'local'

            try:
                imagegroup = 'image-%s' % images[server.image['id']]
                groups[imagegroup].append(server.name)
                groups['image-%s' % server.image['id']].append(server.name)
            except KeyError:
                try:
                    image = cs.images.get(server.image['id'])
                except cs.exceptions.NotFound:
                    groups['image-%s' % server.image['id']].append(server.name)
                else:
                    images[image.id] = image.human_id
                    groups['image-%s' % image.human_id].append(server.name)
                    groups['image-%s' % server.image['id']].append(server.name)

            # And finally, add an IP address
            ansible_ssh_host = None
            # use accessIPv[46] instead of looping address for 'public'
            for network_name in networks:
                if ansible_ssh_host:
                    break
                if network_name == 'public':
                    for version_name in ip_versions:
                        if ansible_ssh_host:
                            break
                        if version_name == 6 and server.accessIPv6:
                            ansible_ssh_host = server.accessIPv6
                        elif server.accessIPv4:
                            ansible_ssh_host = server.accessIPv4
                if not ansible_ssh_host:
                    addresses = server.addresses.get(network_name, [])
                    for address in addresses:
                        for version_name in ip_versions:
                            if ansible_ssh_host:
                                break
                            if address.get('version') == version_name:
                                ansible_ssh_host = address.get('addr')
                                break
            if ansible_ssh_host:
                hostvars[server.name]['ansible_ssh_host'] = ansible_ssh_host

    if hostvars:
        groups['_meta'] = {'hostvars': hostvars}

    with open(get_cache_file_path(regions), 'w') as cache_file:
        json.dump(groups, cache_file)


def get_cache_file_path(regions):
    regions_str = '.'.join([reg.strip().lower() for reg in regions])
    ansible_tmp_path = os.path.join(os.path.expanduser("~"), '.ansible', 'tmp')
    if not os.path.exists(ansible_tmp_path):
        os.makedirs(ansible_tmp_path)
    return os.path.join(ansible_tmp_path,
                        'ansible-rax-%s-%s.cache' % (
                            pyrax.identity.username, regions_str))


def _list(regions, refresh_cache=True):
    cache_max_age = int(get_config(p, 'rax', 'cache_max_age',
                                   'RAX_CACHE_MAX_AGE', 600))

    if (not os.path.exists(get_cache_file_path(regions)) or
            refresh_cache or
            (time() - os.stat(get_cache_file_path(regions))[-1]) > cache_max_age):
        # Cache file doesn't exist or older than 10m or refresh cache requested
        _list_into_cache(regions)

    with open(get_cache_file_path(regions), 'r') as cache_file:
        groups = json.load(cache_file)
        print(json.dumps(groups, sort_keys=True, indent=4))


def parse_args():
    parser = argparse.ArgumentParser(description='Ansible Rackspace Cloud '
                                                 'inventory module')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                       help='List active servers')
    group.add_argument('--host', help='List details about the specific host')
    parser.add_argument('--refresh-cache', action='store_true', default=False,
                        help=('Force refresh of cache, making API requests to'
                              'RackSpace (default: False - use cache files)'))
    return parser.parse_args()


def setup():
    default_creds_file = os.path.expanduser('~/.rackspace_cloud_credentials')

    env = get_config(p, 'rax', 'environment', 'RAX_ENV', None)
    if env:
        pyrax.set_environment(env)

    keyring_username = pyrax.get_setting('keyring_username')

    # Attempt to grab credentials from environment first
    creds_file = get_config(p, 'rax', 'creds_file',
                            'RAX_CREDS_FILE', None)
    if creds_file is not None:
        creds_file = os.path.expanduser(creds_file)
    else:
        # But if that fails, use the default location of
        # ~/.rackspace_cloud_credentials
        if os.path.isfile(default_creds_file):
            creds_file = default_creds_file
        elif not keyring_username:
            sys.exit('No value in environment variable %s and/or no '
                     'credentials file at %s'
                     % ('RAX_CREDS_FILE', default_creds_file))

    identity_type = pyrax.get_setting('identity_type')
    pyrax.set_setting('identity_type', identity_type or 'rackspace')

    region = pyrax.get_setting('region')

    try:
        if keyring_username:
            pyrax.keyring_auth(keyring_username, region=region)
        else:
            pyrax.set_credential_file(creds_file, region=region)
    except Exception as e:
        sys.exit("%s: %s" % (e, e.message))

    regions = []
    if region:
        regions.append(region)
    else:
        try:
            # Ansible 2.3+
            region_list = get_config(p, 'rax', 'regions', 'RAX_REGION', 'all',
                                     value_type='list')
        except TypeError:
            # Ansible 2.2.x and below
            # pylint: disable=unexpected-keyword-arg
            region_list = get_config(p, 'rax', 'regions', 'RAX_REGION', 'all',
                                     islist=True)

        for region in region_list:
            region = region.strip().upper()
            if region == 'ALL':
                regions = pyrax.regions
                break
            elif region not in pyrax.regions:
                sys.exit('Unsupported region %s' % region)
            elif region not in regions:
                regions.append(region)

    return regions


def main():
    args = parse_args()
    regions = setup()
    if args.list:
        _list(regions, refresh_cache=args.refresh_cache)
    elif args.host:
        host(regions, args.host)
    sys.exit(0)


p = load_config_file()
if __name__ == '__main__':
    main()
