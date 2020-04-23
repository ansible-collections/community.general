#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# Copyright (c) 2020 Tomi Raittinen
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: nios_vlan
version_added: "2.10"
author:
  - Tomi Raittinen (@traittinen)
  - Peter Sprygada (@privateip)
short_description: Configure Infoblox NIOS vlan object
description:
  - Adds and/or removes instances of vlan objects from
    Infoblox NIOS servers.  This module manages NIOS C(vlan) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment:
- community.general.nios

options:
  id:
    description:
      - Specifies the vlan ID to add or remove from the system.
    required: true
    type: int
  name:
    description:
      - Specifies the name of the vlan to add or remove from the system.
    required: true
  vlan_view:
    description:
      - Specifies the name of the vlan view to associate with this
        configured instance.
    default: default
  extattrs:
    description:
      - Allows for the configuration of Extensible Attributes on the
        instance of the object.  This argument accepts a set of key / value
        pairs for configuration.
  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: Configure VLAN
  nios_vlan:
    id: 10
    name: vlan10
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
      wapi_version: 2.10
  connection: local

- name: Remove VLAN
  nios_vlan:
    id: 10
    name: vlan10
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
      wapi_version: 2.10
  connection: local
'''

RETURN = '''
ref:
  description: Infoblox object reference
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import flatten_extattrs


def main():
    ''' Main entry point for module execution
    '''
    ib_spec = dict(
        id=dict(required=True, type='int', ib_req=True),
        name=dict(required=True, ib_req=True),
        vlan_view=dict(default='default'),
        extattrs=dict(type='dict'),
        comment=dict()
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(ib_spec)
    argument_spec.update(WapiModule.provider_spec)
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    state = module.params['state']
    if state not in ('present', 'absent'):
        module.fail_json(msg='state must be one of `present`, `absent`, got `%s`' % state)

    result = {'changed': False}
    obj_filter = dict([(k, module.params[k]) for k, v in iteritems(ib_spec) if v.get('ib_req')])
    vlan_view = module.params['vlan_view']

    # Create proposed object based on ib_spec
    proposed_object = {}
    for key, value in iteritems(ib_spec):
        if module.params[key] is not None:
            if 'transform' in value:
                proposed_object[key] = value['transform'](module)
            else:
                proposed_object[key] = module.params[key]
    proposed_object.pop('vlan_view')
    proposed_object.update(id=int(proposed_object.get('id')))

    # Instantiate wapi object
    wapi = WapiModule(module)

    # Try to get existing VLAN object
    id_filter = dict([('id', obj_filter['id'])])
    return_fields = ib_spec.keys()
    return_fields.remove('vlan_view')
    ib_obj_ref = wapi.get_object('vlan', id_filter.copy(), return_fields=return_fields)

    if ib_obj_ref:
        # If multiple VLANs are returned by ID, check VLAN matching the specified VLAN view
        if len(ib_obj_ref) > 1:
            for each in ib_obj_ref:
                # If VLAN matching the view is found
                if vlan_view in each.get('_ref'):
                    current_object = each
                    break
                else:
                    current_object = obj_filter
                    ref = None
        else:
            current_object = ib_obj_ref[0]

        if 'extattrs' in current_object:
            current_object['extattrs'] = flatten_extattrs(current_object['extattrs'])
        if current_object.get('_ref'):
            ref = current_object.pop('_ref')
    else:
        current_object = obj_filter
        ref = None

    # Check if object needs to be modified
    modified = not wapi.compare_objects(current_object, proposed_object)

    vlan_ref = ref

    if state == 'present':
        # Create object
        if ref is None:
            # Get parent (vlan view) ref
            parent = wapi.get_object('vlanview', dict([('name', vlan_view)]))[0].get('_ref')
            proposed_object.update({'parent': parent})
            if not module.check_mode:
                vlan_ref = wapi.create_object('vlan', proposed_object)
            result['changed'] = True
        # Modify object
        elif modified and ref:
            if not module.check_mode:
                proposed_object = wapi.on_update(proposed_object, ib_spec)
                wapi.update_object(ref, proposed_object)
            result['changed'] = True
    elif state == 'absent':
        if ref is not None:
            # Delete object
            if not module.check_mode:
                wapi.delete_object(ref)
            result['changed'] = True

    module.exit_json(ref=vlan_ref, **result)


if __name__ == '__main__':
    main()
