#!/usr/bin/python

# Copyright (c) 2017, Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: sensu_client
author: "David Moreau Simard (@dmsimard)"
short_description: Manages Sensu client configuration
description:
  - Manages Sensu client configuration.
  - For more information, refer to the L(Sensu documentation, https://sensuapp.org/docs/latest/reference/clients.html).
deprecated:
  removed_in: 13.0.0
  why: Sensu Core and Sensu Enterprise products have been End of Life since 2019/20.
  alternative: Use Sensu Go and its accompanying collection C(sensu.sensu_go).
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
      - Whether the client should be present or not.
    choices: ['present', 'absent']
    default: present
  name:
    type: str
    description:
      - A unique name for the client. The name cannot contain special characters or spaces.
      - If not specified, it defaults to the system hostname as determined by Ruby Socket.gethostname (provided by Sensu).
  address:
    type: str
    description:
      - An address to help identify and reach the client. This is only informational, usually an IP address or hostname.
      - If not specified it defaults to non-loopback IPv4 address as determined by Ruby C(Socket.ip_address_list) (provided
        by Sensu).
  subscriptions:
    type: list
    elements: str
    description:
      - An array of client subscriptions, a list of roles and/or responsibilities assigned to the system (for example V(webserver)).
      - These subscriptions determine which monitoring checks are executed by the client, as check requests are sent to subscriptions.
      - The subscriptions array items must be strings.
  safe_mode:
    description:
      - If safe mode is enabled for the client. Safe mode requires local check definitions in order to accept a check request
        and execute the check.
    type: bool
    default: false
  redact:
    type: list
    elements: str
    description:
      - Client definition attributes to redact (values) when logging and sending client keepalives.
  socket:
    type: dict
    description:
      - The socket definition scope, used to configure the Sensu client socket.
  keepalives:
    description:
      - If Sensu should monitor keepalives for this client.
    type: bool
    default: true
  keepalive:
    type: dict
    description:
      - The keepalive definition scope, used to configure Sensu client keepalives behavior (for example keepalive thresholds
        and so).
  registration:
    type: dict
    description:
      - The registration definition scope, used to configure Sensu registration event handlers.
  deregister:
    description:
      - If a deregistration event should be created upon Sensu client process stop.
      - Default is V(false).
    type: bool
  deregistration:
    type: dict
    description:
      - The deregistration definition scope, used to configure automated Sensu client de-registration.
  ec2:
    type: dict
    description:
      - The ec2 definition scope, used to configure the Sensu Enterprise AWS EC2 integration (Sensu Enterprise users only).
  chef:
    type: dict
    description:
      - The chef definition scope, used to configure the Sensu Enterprise Chef integration (Sensu Enterprise users only).
  puppet:
    type: dict
    description:
      - The puppet definition scope, used to configure the Sensu Enterprise Puppet integration (Sensu Enterprise users only).
  servicenow:
    type: dict
    description:
      - The servicenow definition scope, used to configure the Sensu Enterprise ServiceNow integration (Sensu Enterprise users
        only).
"""

EXAMPLES = r"""
# Minimum possible configuration
- name: Configure Sensu client
  community.general.sensu_client:
    subscriptions:
      - default

# With customization
- name: Configure Sensu client
  community.general.sensu_client:
    name: "{{ ansible_fqdn }}"
    address: "{{ ansible_default_ipv4['address'] }}"
    subscriptions:
      - default
      - webserver
    redact:
      - password
    socket:
      bind: 127.0.0.1
      port: 3030
    keepalive:
      thresholds:
        warning: 180
        critical: 300
      handlers:
        - email
      custom:
        - broadcast: irc
      occurrences: 3
  register: client
  notify:
    - Restart sensu-client

- name: Secure Sensu client configuration file
  ansible.builtin.file:
    path: "{{ client['file'] }}"
    owner: "sensu"
    group: "sensu"
    mode: "0600"

- name: Delete the Sensu client configuration
  community.general.sensu_client:
    state: "absent"
"""

RETURN = r"""
config:
  description: Effective client configuration, when state is present.
  returned: success
  type: dict
  sample:
    {
      "name": "client",
      "subscriptions": [
        "default"
      ]
    }
file:
  description: Path to the client configuration file.
  returned: success
  type: str
  sample: "/etc/sensu/conf.d/client.json"
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),
            name=dict(
                type="str",
            ),
            address=dict(
                type="str",
            ),
            subscriptions=dict(type="list", elements="str"),
            safe_mode=dict(type="bool", default=False),
            redact=dict(type="list", elements="str"),
            socket=dict(type="dict"),
            keepalives=dict(type="bool", default=True),
            keepalive=dict(type="dict"),
            registration=dict(type="dict"),
            deregister=dict(type="bool"),
            deregistration=dict(type="dict"),
            ec2=dict(type="dict"),
            chef=dict(type="dict"),
            puppet=dict(type="dict"),
            servicenow=dict(type="dict"),
        ),
        required_if=[["state", "present", ["subscriptions"]]],
    )

    state = module.params["state"]
    path = "/etc/sensu/conf.d/client.json"

    if state == "absent":
        if os.path.exists(path):
            if module.check_mode:
                msg = f"{path} would have been deleted"
                module.exit_json(msg=msg, changed=True)
            else:
                try:
                    os.remove(path)
                    msg = f"{path} deleted successfully"
                    module.exit_json(msg=msg, changed=True)
                except OSError as e:
                    msg = "Exception when trying to delete {path}: {exception}"
                    module.fail_json(msg=msg.format(path=path, exception=str(e)))
        else:
            # Idempotency: it is okay if the file doesn't exist
            msg = f"{path} already does not exist"
            module.exit_json(msg=msg)

    # Build client configuration from module arguments
    config = {"client": {}}
    args = [
        "name",
        "address",
        "subscriptions",
        "safe_mode",
        "redact",
        "socket",
        "keepalives",
        "keepalive",
        "registration",
        "deregister",
        "deregistration",
        "ec2",
        "chef",
        "puppet",
        "servicenow",
    ]

    for arg in args:
        if arg in module.params and module.params[arg] is not None:
            config["client"][arg] = module.params[arg]

    # Load the current config, if there is one, so we can compare
    current_config = None
    try:
        current_config = json.load(open(path, "r"))
    except (IOError, ValueError):
        # File either doesn't exist or it is invalid JSON
        pass

    if current_config is not None and current_config == config:
        # Config is the same, let's not change anything
        module.exit_json(msg="Client configuration is already up to date", config=config["client"], file=path)

    # Validate that directory exists before trying to write to it
    if not module.check_mode and not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            module.fail_json(msg=f"Unable to create {os.path.dirname(path)}: {e}")

    if module.check_mode:
        module.exit_json(
            msg="Client configuration would have been updated", changed=True, config=config["client"], file=path
        )

    try:
        with open(path, "w") as client:
            client.write(json.dumps(config, indent=4))
            module.exit_json(msg="Client configuration updated", changed=True, config=config["client"], file=path)
    except (OSError, IOError) as e:
        module.fail_json(msg=f"Unable to write file {path}: {e}")


if __name__ == "__main__":
    main()
