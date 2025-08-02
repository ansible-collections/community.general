# -*- coding: utf-8 -*-
# Copyright (c) 2015, Filipe Niero Felisbino <filipenf@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: json_query
short_description: Select a single element or a data subset from a complex data structure
description:
  - This filter lets you query a complex JSON structure and iterate over it using a loop structure.
positional: expr
options:
  _input:
    description:
      - The JSON data to query.
    type: any
    required: true
  expr:
    description:
      - The query expression.
      - See U(http://jmespath.org/examples.html) for examples.
    type: string
    required: true
requirements:
  - jmespath
"""

EXAMPLES = r"""
- name: Define data to work on in the examples below
  ansible.builtin.set_fact:
    domain_definition:
      domain:
        cluster:
          - name: cluster1
          - name: cluster2
        server:
          - name: server11
            cluster: cluster1
            port: '8080'
          - name: server12
            cluster: cluster1
            port: '8090'
          - name: server21
            cluster: cluster2
            port: '9080'
          - name: server22
            cluster: cluster2
            port: '9090'
        library:
          - name: lib1
            target: cluster1
          - name: lib2
            target: cluster2

- name: Display all cluster names
  ansible.builtin.debug:
    var: item
  loop: "{{ domain_definition | community.general.json_query('domain.cluster[*].name') }}"

- name: Display all server names
  ansible.builtin.debug:
    var: item
  loop: "{{ domain_definition | community.general.json_query('domain.server[*].name') }}"

- name: Display all ports from cluster1
  ansible.builtin.debug:
    var: item
  loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
  vars:
    server_name_cluster1_query: "domain.server[?cluster=='cluster1'].port"

- name: Display all ports from cluster1 as a string
  ansible.builtin.debug:
    msg: "{{ domain_definition | community.general.json_query('domain.server[?cluster==`cluster1`].port') | join(', ') }}"

- name: Display all ports from cluster1
  ansible.builtin.debug:
    var: item
  loop: "{{ domain_definition | community.general.json_query('domain.server[?cluster==''cluster1''].port') }}"

- name: Display all server ports and names from cluster1
  ansible.builtin.debug:
    var: item
  loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
  vars:
    server_name_cluster1_query: "domain.server[?cluster=='cluster2'].{name: name, port: port}"

- name: Display all ports from cluster1
  ansible.builtin.debug:
    msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
  vars:
    server_name_query: "domain.server[?starts_with(name,'server1')].port"

- name: Display all ports from cluster1
  ansible.builtin.debug:
    msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
  vars:
    server_name_query: "domain.server[?contains(name,'server1')].port"
"""

RETURN = r"""
_value:
  description: The result of the query.
  type: any
"""

from ansible.errors import AnsibleError, AnsibleFilterError

try:
    import jmespath
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def json_query(data, expr):
    '''Query data using jmespath query language ( http://jmespath.org ). Example:
    - ansible.builtin.debug: msg="{{ instance | json_query(tagged_instances[*].block_device_mapping.*.volume_id') }}"
    '''
    if not HAS_LIB:
        raise AnsibleError('You need to install "jmespath" prior to running '
                           'json_query filter')

    # Hack to handle Ansible Unsafe text, AnsibleMapping and AnsibleSequence
    # See issues https://github.com/ansible-collections/community.general/issues/320
    # and https://github.com/ansible/ansible/issues/85600.
    jmespath.functions.REVERSE_TYPES_MAP['string'] = jmespath.functions.REVERSE_TYPES_MAP['string'] + (
        'AnsibleUnicode', 'AnsibleUnsafeText', '_AnsibleTaggedStr',
    )
    jmespath.functions.REVERSE_TYPES_MAP['array'] = jmespath.functions.REVERSE_TYPES_MAP['array'] + (
        'AnsibleSequence', '_AnsibleLazyTemplateList',
    )
    jmespath.functions.REVERSE_TYPES_MAP['object'] = jmespath.functions.REVERSE_TYPES_MAP['object'] + (
        'AnsibleMapping', '_AnsibleLazyTemplateDict',
    )
    try:
        return jmespath.search(expr, data)
    except jmespath.exceptions.JMESPathError as e:
        raise AnsibleFilterError('JMESPathError in json_query filter plugin:\n%s' % e)
    except Exception as e:
        # For older jmespath, we can get ValueError and TypeError without much info.
        raise AnsibleFilterError('Error in jmespath.search in json_query filter plugin:\n%s' % e)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'json_query': json_query
        }
