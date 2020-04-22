#
# Copyright 2018 Red Hat | Ansible
# Copyright 2020 Tomi Raittinen <tomi.raittinen@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
---
lookup: nios_next_vlanid
version_added: "2.10"
short_description: Return the next available VLAN ID for a VLAN range
description:
  - Uses the Infoblox WAPI API to return the next available VLAN ID for
    a given VLAN range
requirements:
  - infoblox_client
extends_documentation_fragment: nios
options:
    _terms:
      description: The VLAN range container to get the next available VLAN ID
      required: False
    view:
      description: The VLAN view to get the next available VLAN ID
      required: False
      default: default
    num:
      description: The number of next free VLAN IDs to return from VLAN range container
      required: False
      default: 1
    exclude:
      description: VLAN IDs to exclude not getting returned
      required: False
      default: ''
"""

EXAMPLES = """
- name: return next available network for network-container 192.168.10.0/24
  set_fact:
    vlanid: "{{ lookup('nios_next_vlanid', 'range1', provider={'host': 'nios01', 'username': 'admin', 'password': 'password', 'wapi_version': '2.10'})[0] }}"

- name: return the next 2 available network addresses for network-container 192.168.10.0/24
  set_fact:
    vlanids: "{{ lookup('nios_next_vlanid', 'range1', num=2,
                        provider={'host': 'nios01', 'username': 'admin', 'password': 'password', 'wapi_version': '2.10'}) }}"

"""

RETURN = """
_list:
  description:
    - The list of next VLAN IDs available
  returned: always
  type: list
"""

from ansible.plugins.lookup import LookupBase
from ansible.module_utils.net_tools.nios.api import WapiLookup
from ansible.module_utils._text import to_text
from ansible.errors import AnsibleError


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
      vlanview_name = kwargs.get('view', 'default')
      num = kwargs.get('num', 1)
      exclude_vlan = kwargs.get('exclude', [])
      provider = kwargs.pop('provider', {})

      if terms:
        vlanrange_name = terms[0]
      else:
        vlanrange_name = None

      # VLAN functionality requires API version >=2.10
      # provider.update({'wapi_version' : '2.10' })

      wapi = WapiLookup(provider)
      
      vlanview_obj = wapi.get_object('vlanview', {'name': vlanview_name})
      vlanview_ref = vlanview_obj[0].get('_ref')      
      vlanrange_ref = None

      if vlanrange_name:
        vlanrange_obj = wapi.get_object('vlanrange', {'name': vlanrange_name})
        if vlanrange_obj is None:
          raise AnsibleError('Unable to find vlanrange object %s' % vlanrange_name)
        if len(vlanrange_obj) > 1:
          for obj in vlanrange_obj:
            if obj['vlan_view']['_ref'] == vlanview_ref:
              vlanrange_ref = obj.get('_ref')
        else:
          vlanrange_ref = vlanrange_obj[0].get('_ref')            

      if vlanrange_ref:
        ref = vlanrange_ref
      else: 
        ref = vlanview_ref

      try:
          avail_vlans = wapi.call_func('next_available_vlan_id', ref, {'num': num, 'exclude': exclude_vlan})
          return [avail_vlans['vlan_ids']]
      except Exception as exc:
          raise AnsibleError(to_text(exc))