#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rax_scaling_group
short_description: Manipulate Rackspace Cloud Autoscale Groups
description:
    - Manipulate Rackspace Cloud Autoscale Groups
options:
  config_drive:
    description:
      - Attach read-only configuration drive to server as label config-2
    type: bool
    default: 'no'
  cooldown:
    type: int
    description:
      - The period of time, in seconds, that must pass before any scaling can
        occur after the previous scaling. Must be an integer between 0 and
        86400 (24 hrs).
    default: 300
  disk_config:
    type: str
    description:
      - Disk partitioning strategy
      - If not specified, it will fallback to C(auto).
    choices:
      - auto
      - manual
  files:
    type: dict
    description:
      - 'Files to insert into the instance. Hash of C(remotepath: localpath)'
  flavor:
    type: str
    description:
      - flavor to use for the instance
    required: true
  image:
    type: str
    description:
      - image to use for the instance. Can be an C(id), C(human_id) or C(name)
    required: true
  key_name:
    type: str
    description:
      - key pair to use on the instance
  loadbalancers:
    type: list
    elements: dict
    description:
      - List of load balancer C(id) and C(port) hashes
  max_entities:
    type: int
    description:
      - The maximum number of entities that are allowed in the scaling group.
        Must be an integer between 0 and 1000.
    required: true
  meta:
    type: dict
    description:
      - A hash of metadata to associate with the instance
  min_entities:
    type: int
    description:
      - The minimum number of entities that are allowed in the scaling group.
        Must be an integer between 0 and 1000.
    required: true
  name:
    type: str
    description:
      - Name to give the scaling group
    required: true
  networks:
    type: list
    elements: str
    description:
      - The network to attach to the instances. If specified, you must include
        ALL networks including the public and private interfaces. Can be C(id)
        or C(label).
    default:
      - public
      - private
  server_name:
    type: str
    description:
      - The base name for servers created by Autoscale
    required: true
  state:
    type: str
    description:
      - Indicate desired state of the resource
    choices:
      - present
      - absent
    default: present
  user_data:
    type: str
    description:
      - Data to be uploaded to the servers config drive. This option implies
        I(config_drive). Can be a file path or a string
  wait:
    description:
      - wait for the scaling group to finish provisioning the minimum amount of
        servers
    type: bool
    default: 'no'
  wait_timeout:
    type: int
    description:
      - how long before wait gives up, in seconds
    default: 300
author: "Matt Martz (@sivel)"
extends_documentation_fragment:
- community.general.rackspace
- community.general.rackspace.openstack

'''

EXAMPLES = '''
---
- hosts: localhost
  gather_facts: false
  connection: local
  tasks:
    - community.general.rax_scaling_group:
        credentials: ~/.raxpub
        region: ORD
        cooldown: 300
        flavor: performance1-1
        image: bb02b1a3-bc77-4d17-ab5b-421d89850fca
        min_entities: 5
        max_entities: 10
        name: ASG Test
        server_name: asgtest
        loadbalancers:
            - id: 228385
              port: 80
      register: asg
'''

import base64
import json
import os
import time

try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rax import (rax_argument_spec, rax_find_image, rax_find_network,
                                                                            rax_required_together, rax_to_dict, setup_rax_module)
from ansible.module_utils.six import string_types


def rax_asg(module, cooldown=300, disk_config=None, files=None, flavor=None,
            image=None, key_name=None, loadbalancers=None, meta=None,
            min_entities=0, max_entities=0, name=None, networks=None,
            server_name=None, state='present', user_data=None,
            config_drive=False, wait=True, wait_timeout=300):
    files = {} if files is None else files
    loadbalancers = [] if loadbalancers is None else loadbalancers
    meta = {} if meta is None else meta
    networks = [] if networks is None else networks

    changed = False

    au = pyrax.autoscale
    if not au:
        module.fail_json(msg='Failed to instantiate clients. This '
                             'typically indicates an invalid region or an '
                             'incorrectly capitalized region name.')

    if user_data:
        config_drive = True

    if user_data and os.path.isfile(user_data):
        try:
            f = open(user_data)
            user_data = f.read()
            f.close()
        except Exception as e:
            module.fail_json(msg='Failed to load %s' % user_data)

    if state == 'present':
        # Normalize and ensure all metadata values are strings
        if meta:
            for k, v in meta.items():
                if isinstance(v, list):
                    meta[k] = ','.join(['%s' % i for i in v])
                elif isinstance(v, dict):
                    meta[k] = json.dumps(v)
                elif not isinstance(v, string_types):
                    meta[k] = '%s' % v

        if image:
            image = rax_find_image(module, pyrax, image)

        nics = []
        if networks:
            for network in networks:
                nics.extend(rax_find_network(module, pyrax, network))

            for nic in nics:
                # pyrax is currently returning net-id, but we need uuid
                # this check makes this forward compatible for a time when
                # pyrax uses uuid instead
                if nic.get('net-id'):
                    nic.update(uuid=nic['net-id'])
                    del nic['net-id']

        # Handle the file contents
        personality = []
        if files:
            for rpath in files.keys():
                lpath = os.path.expanduser(files[rpath])
                try:
                    f = open(lpath, 'r')
                    personality.append({
                        'path': rpath,
                        'contents': f.read()
                    })
                    f.close()
                except Exception as e:
                    module.fail_json(msg='Failed to load %s' % lpath)

        lbs = []
        if loadbalancers:
            for lb in loadbalancers:
                try:
                    lb_id = int(lb.get('id'))
                except (ValueError, TypeError):
                    module.fail_json(msg='Load balancer ID is not an integer: '
                                         '%s' % lb.get('id'))
                try:
                    port = int(lb.get('port'))
                except (ValueError, TypeError):
                    module.fail_json(msg='Load balancer port is not an '
                                         'integer: %s' % lb.get('port'))
                if not lb_id or not port:
                    continue
                lbs.append((lb_id, port))

        try:
            sg = au.find(name=name)
        except pyrax.exceptions.NoUniqueMatch as e:
            module.fail_json(msg='%s' % e.message)
        except pyrax.exceptions.NotFound:
            try:
                sg = au.create(name, cooldown=cooldown,
                               min_entities=min_entities,
                               max_entities=max_entities,
                               launch_config_type='launch_server',
                               server_name=server_name, image=image,
                               flavor=flavor, disk_config=disk_config,
                               metadata=meta, personality=personality,
                               networks=nics, load_balancers=lbs,
                               key_name=key_name, config_drive=config_drive,
                               user_data=user_data)
                changed = True
            except Exception as e:
                module.fail_json(msg='%s' % e.message)

        if not changed:
            # Scaling Group Updates
            group_args = {}
            if cooldown != sg.cooldown:
                group_args['cooldown'] = cooldown

            if min_entities != sg.min_entities:
                group_args['min_entities'] = min_entities

            if max_entities != sg.max_entities:
                group_args['max_entities'] = max_entities

            if group_args:
                changed = True
                sg.update(**group_args)

            # Launch Configuration Updates
            lc = sg.get_launch_config()
            lc_args = {}
            if server_name != lc.get('name'):
                lc_args['server_name'] = server_name

            if image != lc.get('image'):
                lc_args['image'] = image

            if flavor != lc.get('flavor'):
                lc_args['flavor'] = flavor

            disk_config = disk_config or 'AUTO'
            if ((disk_config or lc.get('disk_config')) and
                    disk_config != lc.get('disk_config', 'AUTO')):
                lc_args['disk_config'] = disk_config

            if (meta or lc.get('meta')) and meta != lc.get('metadata'):
                lc_args['metadata'] = meta

            test_personality = []
            for p in personality:
                test_personality.append({
                    'path': p['path'],
                    'contents': base64.b64encode(p['contents'])
                })
            if ((test_personality or lc.get('personality')) and
                    test_personality != lc.get('personality')):
                lc_args['personality'] = personality

            if nics != lc.get('networks'):
                lc_args['networks'] = nics

            if lbs != lc.get('load_balancers'):
                # Work around for https://github.com/rackspace/pyrax/pull/393
                lc_args['load_balancers'] = sg.manager._resolve_lbs(lbs)

            if key_name != lc.get('key_name'):
                lc_args['key_name'] = key_name

            if config_drive != lc.get('config_drive', False):
                lc_args['config_drive'] = config_drive

            if (user_data and
                    base64.b64encode(user_data) != lc.get('user_data')):
                lc_args['user_data'] = user_data

            if lc_args:
                # Work around for https://github.com/rackspace/pyrax/pull/389
                if 'flavor' not in lc_args:
                    lc_args['flavor'] = lc.get('flavor')
                changed = True
                sg.update_launch_config(**lc_args)

            sg.get()

        if wait:
            end_time = time.time() + wait_timeout
            infinite = wait_timeout == 0
            while infinite or time.time() < end_time:
                state = sg.get_state()
                if state["pending_capacity"] == 0:
                    break

                time.sleep(5)

        module.exit_json(changed=changed, autoscale_group=rax_to_dict(sg))

    else:
        try:
            sg = au.find(name=name)
            sg.delete()
            changed = True
        except pyrax.exceptions.NotFound as e:
            sg = {}
        except Exception as e:
            module.fail_json(msg='%s' % e.message)

        module.exit_json(changed=changed, autoscale_group=rax_to_dict(sg))


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            config_drive=dict(default=False, type='bool'),
            cooldown=dict(type='int', default=300),
            disk_config=dict(choices=['auto', 'manual']),
            files=dict(type='dict', default={}),
            flavor=dict(required=True),
            image=dict(required=True),
            key_name=dict(),
            loadbalancers=dict(type='list', elements='dict'),
            meta=dict(type='dict', default={}),
            min_entities=dict(type='int', required=True),
            max_entities=dict(type='int', required=True),
            name=dict(required=True),
            networks=dict(type='list', elements='str', default=['public', 'private']),
            server_name=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
            user_data=dict(no_log=True),
            wait=dict(default=False, type='bool'),
            wait_timeout=dict(default=300, type='int'),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together(),
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    config_drive = module.params.get('config_drive')
    cooldown = module.params.get('cooldown')
    disk_config = module.params.get('disk_config')
    if disk_config:
        disk_config = disk_config.upper()
    files = module.params.get('files')
    flavor = module.params.get('flavor')
    image = module.params.get('image')
    key_name = module.params.get('key_name')
    loadbalancers = module.params.get('loadbalancers')
    meta = module.params.get('meta')
    min_entities = module.params.get('min_entities')
    max_entities = module.params.get('max_entities')
    name = module.params.get('name')
    networks = module.params.get('networks')
    server_name = module.params.get('server_name')
    state = module.params.get('state')
    user_data = module.params.get('user_data')

    if not 0 <= min_entities <= 1000 or not 0 <= max_entities <= 1000:
        module.fail_json(msg='min_entities and max_entities must be an '
                             'integer between 0 and 1000')

    if not 0 <= cooldown <= 86400:
        module.fail_json(msg='cooldown must be an integer between 0 and 86400')

    setup_rax_module(module, pyrax)

    rax_asg(module, cooldown=cooldown, disk_config=disk_config,
            files=files, flavor=flavor, image=image, meta=meta,
            key_name=key_name, loadbalancers=loadbalancers,
            min_entities=min_entities, max_entities=max_entities,
            name=name, networks=networks, server_name=server_name,
            state=state, config_drive=config_drive, user_data=user_data)


if __name__ == '__main__':
    main()
