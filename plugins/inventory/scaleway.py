# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
    name: scaleway
    author:
      - Remy Leone (@remyleone)
    short_description: Scaleway inventory source
    description:
        - Get inventory hosts from Scaleway.
    requirements:
        - PyYAML
    options:
        plugin:
            description: Token that ensures this is a source file for the 'scaleway' plugin.
            required: true
            choices: ['scaleway', 'community.general.scaleway']
        regions:
            description: Filter results on a specific Scaleway region.
            type: list
            elements: string
            default:
                - ams1
                - par1
                - par2
                - waw1
        tags:
            description: Filter results on a specific tag.
            type: list
            elements: string
        scw_profile:
            description:
            - The config profile to use in config file.
            - By default uses the one specified as C(active_profile) in the config file, or falls back to C(default) if that is not defined.
            type: string
            version_added: 4.4.0
        oauth_token:
            description:
            - Scaleway OAuth token.
            - If not explicitly defined or in environment variables, it will try to lookup in the scaleway-cli configuration file
              (C($SCW_CONFIG_PATH), C($XDG_CONFIG_HOME/scw/config.yaml), or C(~/.config/scw/config.yaml)).
            - More details on L(how to generate token, https://www.scaleway.com/en/docs/generate-api-keys/).
            env:
                # in order of precedence
                - name: SCW_TOKEN
                - name: SCW_API_KEY
                - name: SCW_OAUTH_TOKEN
        hostnames:
            description: List of preference about what to use as an hostname.
            type: list
            elements: string
            default:
                - public_ipv4
            choices:
                - public_ipv4
                - private_ipv4
                - public_ipv6
                - hostname
                - id
        variables:
            description: 'Set individual variables: keys are variable names and
                          values are templates. Any value returned by the
                          L(Scaleway API, https://developer.scaleway.com/#servers-server-get)
                          can be used.'
            type: dict
'''

EXAMPLES = r'''
# scaleway_inventory.yml file in YAML format
# Example command line: ansible-inventory --list -i scaleway_inventory.yml

# use hostname as inventory_hostname
# use the private IP address to connect to the host
plugin: community.general.scaleway
regions:
  - ams1
  - par1
tags:
  - foobar
hostnames:
  - hostname
variables:
  ansible_host: private_ip
  state: state

# use hostname as inventory_hostname and public IP address to connect to the host
plugin: community.general.scaleway
hostnames:
  - hostname
regions:
  - par1
variables:
  ansible_host: public_ip.address

# Using static strings as variables
plugin: community.general.scaleway
hostnames:
  - hostname
variables:
  ansible_host: public_ip.address
  ansible_connection: "'ssh'"
  ansible_user: "'admin'"
'''

import os
import json

try:
    import yaml
except ImportError as exc:
    YAML_IMPORT_ERROR = exc
else:
    YAML_IMPORT_ERROR = None

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible_collections.community.general.plugins.module_utils.scaleway import SCALEWAY_LOCATION, parse_pagination_link
from ansible.module_utils.urls import open_url
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.six import raise_from

import ansible.module_utils.six.moves.urllib.parse as urllib_parse


def _fetch_information(token, url):
    results = []
    paginated_url = url
    while True:
        try:
            response = open_url(paginated_url,
                                headers={'X-Auth-Token': token,
                                         'Content-type': 'application/json'})
        except Exception as e:
            raise AnsibleError("Error while fetching %s: %s" % (url, to_native(e)))
        try:
            raw_json = json.loads(to_text(response.read()))
        except ValueError:
            raise AnsibleError("Incorrect JSON payload")

        try:
            results.extend(raw_json["servers"])
        except KeyError:
            raise AnsibleError("Incorrect format from the Scaleway API response")

        link = response.headers['Link']
        if not link:
            return results
        relations = parse_pagination_link(link)
        if 'next' not in relations:
            return results
        paginated_url = urllib_parse.urljoin(paginated_url, relations['next'])


def _build_server_url(api_endpoint):
    return "/".join([api_endpoint, "servers"])


def extract_public_ipv4(server_info):
    try:
        return server_info["public_ip"]["address"]
    except (KeyError, TypeError):
        return None


def extract_private_ipv4(server_info):
    try:
        return server_info["private_ip"]
    except (KeyError, TypeError):
        return None


def extract_hostname(server_info):
    try:
        return server_info["hostname"]
    except (KeyError, TypeError):
        return None


def extract_server_id(server_info):
    try:
        return server_info["id"]
    except (KeyError, TypeError):
        return None


def extract_public_ipv6(server_info):
    try:
        return server_info["ipv6"]["address"]
    except (KeyError, TypeError):
        return None


def extract_tags(server_info):
    try:
        return server_info["tags"]
    except (KeyError, TypeError):
        return None


def extract_zone(server_info):
    try:
        return server_info["location"]["zone_id"]
    except (KeyError, TypeError):
        return None


extractors = {
    "public_ipv4": extract_public_ipv4,
    "private_ipv4": extract_private_ipv4,
    "public_ipv6": extract_public_ipv6,
    "hostname": extract_hostname,
    "id": extract_server_id
}


class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = 'community.general.scaleway'

    def _fill_host_variables(self, host, server_info):
        targeted_attributes = (
            "arch",
            "commercial_type",
            "id",
            "organization",
            "state",
            "hostname",
        )
        for attribute in targeted_attributes:
            self.inventory.set_variable(host, attribute, server_info[attribute])

        self.inventory.set_variable(host, "tags", server_info["tags"])

        if extract_public_ipv6(server_info=server_info):
            self.inventory.set_variable(host, "public_ipv6", extract_public_ipv6(server_info=server_info))

        if extract_public_ipv4(server_info=server_info):
            self.inventory.set_variable(host, "public_ipv4", extract_public_ipv4(server_info=server_info))

        if extract_private_ipv4(server_info=server_info):
            self.inventory.set_variable(host, "private_ipv4", extract_private_ipv4(server_info=server_info))

    def _get_zones(self, config_zones):
        return set(SCALEWAY_LOCATION.keys()).intersection(config_zones)

    def match_groups(self, server_info, tags):
        server_zone = extract_zone(server_info=server_info)
        server_tags = extract_tags(server_info=server_info)

        # If a server does not have a zone, it means it is archived
        if server_zone is None:
            return set()

        # If no filtering is defined, all tags are valid groups
        if tags is None:
            return set(server_tags).union((server_zone,))

        matching_tags = set(server_tags).intersection(tags)

        if not matching_tags:
            return set()
        return matching_tags.union((server_zone,))

    def _filter_host(self, host_infos, hostname_preferences):

        for pref in hostname_preferences:
            if extractors[pref](host_infos):
                return extractors[pref](host_infos)

        return None

    def do_zone_inventory(self, zone, token, tags, hostname_preferences):
        self.inventory.add_group(zone)
        zone_info = SCALEWAY_LOCATION[zone]

        url = _build_server_url(zone_info["api_endpoint"])
        raw_zone_hosts_infos = _fetch_information(url=url, token=token)

        for host_infos in raw_zone_hosts_infos:

            hostname = self._filter_host(host_infos=host_infos,
                                         hostname_preferences=hostname_preferences)

            # No suitable hostname were found in the attributes and the host won't be in the inventory
            if not hostname:
                continue

            groups = self.match_groups(host_infos, tags)

            for group in groups:
                self.inventory.add_group(group=group)
                self.inventory.add_host(group=group, host=hostname)
                self._fill_host_variables(host=hostname, server_info=host_infos)

                # Composed variables
                self._set_composite_vars(self.get_option('variables'), host_infos, hostname, strict=False)

    def get_oauth_token(self):
        oauth_token = self.get_option('oauth_token')

        if 'SCW_CONFIG_PATH' in os.environ:
            scw_config_path = os.getenv('SCW_CONFIG_PATH')
        elif 'XDG_CONFIG_HOME' in os.environ:
            scw_config_path = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'scw', 'config.yaml')
        else:
            scw_config_path = os.path.join(os.path.expanduser('~'), '.config', 'scw', 'config.yaml')

        if not oauth_token and os.path.exists(scw_config_path):
            with open(scw_config_path) as fh:
                scw_config = yaml.safe_load(fh)
                ansible_profile = self.get_option('scw_profile')

                if ansible_profile:
                    active_profile = ansible_profile
                else:
                    active_profile = scw_config.get('active_profile', 'default')

                if active_profile == 'default':
                    oauth_token = scw_config.get('secret_key')
                else:
                    oauth_token = scw_config['profiles'][active_profile].get('secret_key')

        return oauth_token

    def parse(self, inventory, loader, path, cache=True):
        if YAML_IMPORT_ERROR:
            raise_from(AnsibleError('PyYAML is probably missing'), YAML_IMPORT_ERROR)
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path=path)

        config_zones = self.get_option("regions")
        tags = self.get_option("tags")
        token = self.get_oauth_token()
        if not token:
            raise AnsibleError("'oauth_token' value is null, you must configure it either in inventory, envvars or scaleway-cli config.")
        hostname_preference = self.get_option("hostnames")

        for zone in self._get_zones(config_zones):
            self.do_zone_inventory(zone=zone, token=token, tags=tags, hostname_preferences=hostname_preference)
