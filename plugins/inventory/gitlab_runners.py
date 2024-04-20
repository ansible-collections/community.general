# -*- coding: utf-8 -*-
# Copyright (c) 2018, Stefan Heitmueller <stefan.heitmueller@gmx.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
    name: gitlab_runners
    author:
      - Stefan Heitmüller (@morph027) <stefan.heitmueller@gmx.com>
    short_description: Ansible dynamic inventory plugin for GitLab runners.
    requirements:
        - python-gitlab > 1.8.0
    extends_documentation_fragment:
        - constructed
    description:
        - Reads inventories from the GitLab API.
        - Uses a YAML configuration file gitlab_runners.[yml|yaml].
    options:
        plugin:
            description: The name of this plugin, it should always be set to 'gitlab_runners' for this plugin to recognize it as it's own.
            type: str
            required: true
            choices:
              - gitlab_runners
              - community.general.gitlab_runners
        server_url:
            description: The URL of the GitLab server, with protocol (i.e. http or https).
            env:
              - name: GITLAB_SERVER_URL
                version_added: 1.0.0
            type: str
            required: true
        api_token:
            description: GitLab token for logging in.
            env:
              - name: GITLAB_API_TOKEN
                version_added: 1.0.0
            type: str
            aliases:
              - private_token
              - access_token
        filter:
            description: filter runners from GitLab API
            env:
              - name: GITLAB_FILTER
                version_added: 1.0.0
            type: str
            choices: ['active', 'paused', 'online', 'specific', 'shared']
        verbose_output:
            description: Toggle to (not) include all available nodes metadata
            type: bool
            default: true
'''

EXAMPLES = '''
# gitlab_runners.yml
plugin: community.general.gitlab_runners
host: https://gitlab.com

# Example using constructed features to create groups and set ansible_host
plugin: community.general.gitlab_runners
host: https://gitlab.com
strict: false
keyed_groups:
  # add e.g. amd64 hosts to an arch_amd64 group
  - prefix: arch
    key: 'architecture'
  # add e.g. linux hosts to an os_linux group
  - prefix: os
    key: 'platform'
  # create a group per runner tag
  # e.g. a runner tagged w/ "production" ends up in group "label_production"
  # hint: labels containing special characters will be converted to safe names
  - key: 'tag_list'
    prefix: tag
'''

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable

from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe

try:
    import gitlab
    HAS_GITLAB = True
except ImportError:
    HAS_GITLAB = False


class InventoryModule(BaseInventoryPlugin, Constructable):
    ''' Host inventory parser for ansible using GitLab API as source. '''

    NAME = 'community.general.gitlab_runners'

    def _populate(self):
        gl = gitlab.Gitlab(self.get_option('server_url'), private_token=self.get_option('api_token'))
        self.inventory.add_group('gitlab_runners')
        try:
            if self.get_option('filter'):
                runners = gl.runners.all(scope=self.get_option('filter'))
            else:
                runners = gl.runners.all()
            for runner in runners:
                host = make_unsafe(str(runner['id']))
                ip_address = runner['ip_address']
                host_attrs = make_unsafe(vars(gl.runners.get(runner['id']))['_attrs'])
                self.inventory.add_host(host, group='gitlab_runners')
                self.inventory.set_variable(host, 'ansible_host', make_unsafe(ip_address))
                if self.get_option('verbose_output', True):
                    self.inventory.set_variable(host, 'gitlab_runner_attributes', host_attrs)

                # Use constructed if applicable
                strict = self.get_option('strict')
                # Composed variables
                self._set_composite_vars(self.get_option('compose'), host_attrs, host, strict=strict)
                # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
                self._add_host_to_composed_groups(self.get_option('groups'), host_attrs, host, strict=strict)
                # Create groups based on variable values and add the corresponding hosts to it
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host_attrs, host, strict=strict)
        except Exception as e:
            raise AnsibleParserError('Unable to fetch hosts from GitLab API, this was the original exception: %s' % to_native(e))

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return (
            super(InventoryModule, self).verify_file(path) and
            path.endswith(("gitlab_runners.yaml", "gitlab_runners.yml")))

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_GITLAB:
            raise AnsibleError('The GitLab runners dynamic inventory plugin requires python-gitlab: https://python-gitlab.readthedocs.io/en/stable/')
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        self._populate()
