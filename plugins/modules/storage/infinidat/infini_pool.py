#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Gregory Shulov (gregory.shulov@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: infini_pool
short_description: Create, Delete and Modify Pools on Infinibox
description:
    - This module to creates, deletes or modifies pools on Infinibox.
author: Gregory Shulov (@GR360RY)
options:
  name:
    description:
      - Pool Name
    required: true
  state:
    description:
      - Creates/Modifies Pool when present or removes when absent
    required: false
    default: present
    choices: [ "present", "absent" ]
  size:
    description:
      - Pool Physical Capacity in MB, GB or TB units.
        If pool size is not set on pool creation, size will be equal to 1TB.
        See examples.
    required: false
  vsize:
    description:
      - Pool Virtual Capacity in MB, GB or TB units.
        If pool vsize is not set on pool creation, Virtual Capacity will be equal to Physical Capacity.
        See examples.
    required: false
  ssd_cache:
    description:
      - Enable/Disable SSD Cache on Pool
    required: false
    default: yes
    type: bool
notes:
  - Infinibox Admin level access is required for pool modifications
extends_documentation_fragment:
- community.general.infinibox

requirements:
    - capacity
'''

EXAMPLES = '''
- name: Make sure pool foo exists. Set pool physical capacity to 10TB
  infini_pool:
    name: foo
    size: 10TB
    vsize: 10TB
    user: admin
    password: secret
    system: ibox001

- name: Disable SSD Cache on pool
  infini_pool:
    name: foo
    ssd_cache: no
    user: admin
    password: secret
    system: ibox001
'''

RETURN = '''
'''
import traceback

CAPACITY_IMP_ERR = None
try:
    from capacity import KiB, Capacity
    HAS_CAPACITY = True
except ImportError:
    CAPACITY_IMP_ERR = traceback.format_exc()
    HAS_CAPACITY = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.infinibox import HAS_INFINISDK, api_wrapper, get_system, infinibox_argument_spec


@api_wrapper
def get_pool(module, system):
    """Return Pool on None"""
    try:
        return system.pools.get(name=module.params['name'])
    except Exception:
        return None


@api_wrapper
def create_pool(module, system):
    """Create Pool"""
    name = module.params['name']
    size = module.params['size']
    vsize = module.params['vsize']
    ssd_cache = module.params['ssd_cache']

    if not module.check_mode:
        if not size and not vsize:
            pool = system.pools.create(name=name, physical_capacity=Capacity('1TB'), virtual_capacity=Capacity('1TB'))
        elif size and not vsize:
            pool = system.pools.create(name=name, physical_capacity=Capacity(size), virtual_capacity=Capacity(size))
        elif not size and vsize:
            pool = system.pools.create(name=name, physical_capacity=Capacity('1TB'), virtual_capacity=Capacity(vsize))
        else:
            pool = system.pools.create(name=name, physical_capacity=Capacity(size), virtual_capacity=Capacity(vsize))
        # Default value of ssd_cache is True. Disable ssd caching if False
        if not ssd_cache:
            pool.update_ssd_enabled(ssd_cache)

    module.exit_json(changed=True)


@api_wrapper
def update_pool(module, system, pool):
    """Update Pool"""
    changed = False

    size = module.params['size']
    vsize = module.params['vsize']
    ssd_cache = module.params['ssd_cache']

    # Roundup the capacity to mimic Infinibox behaviour
    if size:
        physical_capacity = Capacity(size).roundup(6 * 64 * KiB)
        if pool.get_physical_capacity() != physical_capacity:
            if not module.check_mode:
                pool.update_physical_capacity(physical_capacity)
            changed = True

    if vsize:
        virtual_capacity = Capacity(vsize).roundup(6 * 64 * KiB)
        if pool.get_virtual_capacity() != virtual_capacity:
            if not module.check_mode:
                pool.update_virtual_capacity(virtual_capacity)
            changed = True

    if pool.get_ssd_enabled() != ssd_cache:
        if not module.check_mode:
            pool.update_ssd_enabled(ssd_cache)
        changed = True

    module.exit_json(changed=changed)


@api_wrapper
def delete_pool(module, pool):
    """Delete Pool"""
    if not module.check_mode:
        pool.delete()
    module.exit_json(changed=True)


def main():
    argument_spec = infinibox_argument_spec()
    argument_spec.update(
        dict(
            name=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
            size=dict(),
            vsize=dict(),
            ssd_cache=dict(type='bool', default=True)
        )
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)

    if not HAS_INFINISDK:
        module.fail_json(msg=missing_required_lib('infinisdk'))
    if not HAS_CAPACITY:
        module.fail_json(msg=missing_required_lib('capacity'), exception=CAPACITY_IMP_ERR)

    if module.params['size']:
        try:
            Capacity(module.params['size'])
        except Exception:
            module.fail_json(msg='size (Physical Capacity) should be defined in MB, GB, TB or PB units')

    if module.params['vsize']:
        try:
            Capacity(module.params['vsize'])
        except Exception:
            module.fail_json(msg='vsize (Virtual Capacity) should be defined in MB, GB, TB or PB units')

    state = module.params['state']
    system = get_system(module)
    pool = get_pool(module, system)

    if state == 'present' and not pool:
        create_pool(module, system)
    elif state == 'present' and pool:
        update_pool(module, system, pool)
    elif state == 'absent' and pool:
        delete_pool(module, pool)
    elif state == 'absent' and not pool:
        module.exit_json(changed=False)


if __name__ == '__main__':
    main()
