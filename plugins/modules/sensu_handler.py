#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: sensu_handler
author: "David Moreau Simard (@dmsimard)"
short_description: Manages Sensu handler configuration
description:
  - Manages Sensu handler configuration
  - 'For more information, refer to the Sensu documentation: U(https://sensuapp.org/docs/latest/reference/handlers.html)'
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    type: str
    description:
      - Whether the handler should be present or not
    choices: [ 'present', 'absent' ]
    default: present
  name:
    type: str
    description:
      - A unique name for the handler. The name cannot contain special characters or spaces.
    required: true
  type:
    type: str
    description:
      - The handler type
    choices: [ 'pipe', 'tcp', 'udp', 'transport', 'set' ]
  filter:
    type: str
    description:
      - The Sensu event filter (name) to use when filtering events for the handler.
  filters:
    type: list
    elements: str
    description:
      - An array of Sensu event filters (names) to use when filtering events for the handler.
      - Each array item must be a string.
  severities:
    type: list
    elements: str
    description:
      - An array of check result severities the handler will handle.
      - 'NOTE: event resolution bypasses this filtering.'
      - "Example: [ 'warning', 'critical', 'unknown' ]."
  mutator:
    type: str
    description:
      - The Sensu event mutator (name) to use to mutate event data for the handler.
  timeout:
    type: int
    description:
      - The handler execution duration timeout in seconds (hard stop).
      - Only used by pipe and tcp handler types.
    default: 10
  handle_silenced:
    description:
      - If events matching one or more silence entries should be handled.
    type: bool
    default: false
  handle_flapping:
    description:
      - If events in the flapping state should be handled.
    type: bool
    default: false
  command:
    type: str
    description:
      - The handler command to be executed.
      - The event data is passed to the process via STDIN.
      - 'NOTE: the command attribute is only required for Pipe handlers (i.e. handlers configured with "type": "pipe").'
  socket:
    type: dict
    description:
      - The socket definition scope, used to configure the TCP/UDP handler socket.
      - 'NOTE: the socket attribute is only required for TCP/UDP handlers (i.e. handlers configured with "type": "tcp" or "type": "udp").'
  pipe:
    type: dict
    description:
      - The pipe definition scope, used to configure the Sensu transport pipe.
      - 'NOTE: the pipe attribute is only required for Transport handlers (i.e. handlers configured with "type": "transport").'
  handlers:
    type: list
    elements: str
    description:
      - An array of Sensu event handlers (names) to use for events using the handler set.
      - 'NOTE: the handlers attribute is only required for handler sets (i.e. handlers configured with "type": "set").'
notes:
  - Check mode is supported
'''

EXAMPLES = '''
# Configure a handler that sends event data as STDIN (pipe)
- name: Configure IRC Sensu handler
  community.general.sensu_handler:
    name: "irc_handler"
    type: "pipe"
    command: "/usr/local/bin/notify-irc.sh"
    severities:
      - "ok"
      - "critical"
      - "warning"
      - "unknown"
    timeout: 15
  notify:
    - Restart sensu-client
    - Restart sensu-server

# Delete a handler
- name: Delete IRC Sensu handler
  community.general.sensu_handler:
    name: "irc_handler"
    state: "absent"

# Example of a TCP handler
- name: Configure TCP Sensu handler
  community.general.sensu_handler:
    name: "tcp_handler"
    type: "tcp"
    timeout: 30
    socket:
      host: "10.0.1.99"
      port: 4444
  register: handler
  notify:
    - Restart sensu-client
    - Restart sensu-server

- name: Secure Sensu handler configuration file
  ansible.builtin.file:
    path: "{{ handler['file'] }}"
    owner: "sensu"
    group: "sensu"
    mode: "0600"
'''

RETURN = '''
config:
  description: Effective handler configuration, when state is present
  returned: success
  type: dict
  sample: {'name': 'irc', 'type': 'pipe', 'command': '/usr/local/bin/notify-irc.sh'}
file:
  description: Path to the handler configuration file
  returned: success
  type: str
  sample: "/etc/sensu/conf.d/handlers/irc.json"
name:
  description: Name of the handler
  returned: success
  type: str
  sample: "irc"
'''

import json
import os

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(type='str', required=True),
            type=dict(type='str', choices=['pipe', 'tcp', 'udp', 'transport', 'set']),
            filter=dict(type='str'),
            filters=dict(type='list', elements='str'),
            severities=dict(type='list', elements='str'),
            mutator=dict(type='str'),
            timeout=dict(type='int', default=10),
            handle_silenced=dict(type='bool', default=False),
            handle_flapping=dict(type='bool', default=False),
            command=dict(type='str'),
            socket=dict(type='dict'),
            pipe=dict(type='dict'),
            handlers=dict(type='list', elements='str'),
        ),
        required_if=[
            ['state', 'present', ['type']],
            ['type', 'pipe', ['command']],
            ['type', 'tcp', ['socket']],
            ['type', 'udp', ['socket']],
            ['type', 'transport', ['pipe']],
            ['type', 'set', ['handlers']]
        ]
    )

    state = module.params['state']
    name = module.params['name']
    path = '/etc/sensu/conf.d/handlers/{0}.json'.format(name)

    if state == 'absent':
        if os.path.exists(path):
            if module.check_mode:
                msg = '{path} would have been deleted'.format(path=path)
                module.exit_json(msg=msg, changed=True)
            else:
                try:
                    os.remove(path)
                    msg = '{path} deleted successfully'.format(path=path)
                    module.exit_json(msg=msg, changed=True)
                except OSError as e:
                    msg = 'Exception when trying to delete {path}: {exception}'
                    module.fail_json(
                        msg=msg.format(path=path, exception=str(e)))
        else:
            # Idempotency: it's okay if the file doesn't exist
            msg = '{path} already does not exist'.format(path=path)
            module.exit_json(msg=msg)

    # Build handler configuration from module arguments
    config = {'handlers': {name: {}}}
    args = ['type', 'filter', 'filters', 'severities', 'mutator', 'timeout',
            'handle_silenced', 'handle_flapping', 'command', 'socket',
            'pipe', 'handlers']

    for arg in args:
        if arg in module.params and module.params[arg] is not None:
            config['handlers'][name][arg] = module.params[arg]

    # Load the current config, if there is one, so we can compare
    current_config = None
    try:
        current_config = json.load(open(path, 'r'))
    except (IOError, ValueError):
        # File either doesn't exist or it's invalid JSON
        pass

    if current_config is not None and current_config == config:
        # Config is the same, let's not change anything
        module.exit_json(msg='Handler configuration is already up to date',
                         config=config['handlers'][name],
                         file=path,
                         name=name)

    # Validate that directory exists before trying to write to it
    if not module.check_mode and not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            module.fail_json(msg='Unable to create {0}: {1}'.format(os.path.dirname(path),
                                                                    str(e)))

    if module.check_mode:
        module.exit_json(msg='Handler configuration would have been updated',
                         changed=True,
                         config=config['handlers'][name],
                         file=path,
                         name=name)

    try:
        with open(path, 'w') as handler:
            handler.write(json.dumps(config, indent=4))
            module.exit_json(msg='Handler configuration updated',
                             changed=True,
                             config=config['handlers'][name],
                             file=path,
                             name=name)
    except (OSError, IOError) as e:
        module.fail_json(msg='Unable to write file {0}: {1}'.format(path,
                                                                    str(e)))


if __name__ == '__main__':
    main()
