#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: logstash_plugin
short_description: Manage Logstash plugins
description:
  - Manages Logstash plugins.
author: Loic Blot (@nerzhul)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - Install plugin with that name.
    required: true
  state:
    type: str
    description:
      - Apply plugin state.
    choices: ["present", "absent"]
    default: present
  plugin_bin:
    type: path
    description:
      - Specify logstash-plugin to use for plugin management.
    default: /usr/share/logstash/bin/logstash-plugin
  proxy_host:
    type: str
    description:
      - Proxy host to use during plugin installation.
  proxy_port:
    type: str
    description:
      - Proxy port to use during plugin installation.
  version:
    type: str
    description:
      - Specify version of the plugin to install. If the plugin exists with a previous version, it is B(not) updated.
"""

EXAMPLES = r"""
- name: Install Logstash beats input plugin
  community.general.logstash_plugin:
    state: present
    name: logstash-input-beats

- name: Install specific version of a plugin
  community.general.logstash_plugin:
    state: present
    name: logstash-input-syslog
    version: '3.2.0'

- name: Uninstall Logstash plugin
  community.general.logstash_plugin:
    state: absent
    name: logstash-filter-multiline

- name: Install Logstash plugin with alternate heap size
  community.general.logstash_plugin:
    state: present
    name: logstash-input-beats
  environment:
    LS_JAVA_OPTS: "-Xms256m -Xmx256m"
"""

from ansible.module_utils.basic import AnsibleModule


PACKAGE_STATE_MAP = dict(
    present="install",
    absent="remove"
)


def is_plugin_present(module, plugin_bin, plugin_name):
    cmd_args = [plugin_bin, "list", plugin_name]
    rc, out, err = module.run_command(cmd_args)
    return rc == 0


def parse_error(string):
    reason = "reason: "
    try:
        return string[string.index(reason) + len(reason):].strip()
    except ValueError:
        return string


def install_plugin(module, plugin_bin, plugin_name, version, proxy_host, proxy_port):
    cmd_args = [plugin_bin, PACKAGE_STATE_MAP["present"], plugin_name]

    if version:
        cmd_args.extend(["--version", version])

    if proxy_host and proxy_port:
        cmd_args.extend(["-DproxyHost=%s" % proxy_host, "-DproxyPort=%s" % proxy_port])

    cmd = " ".join(cmd_args)

    if module.check_mode:
        rc, out, err = 0, "check mode", ""
    else:
        rc, out, err = module.run_command(cmd_args)

    if rc != 0:
        reason = parse_error(out)
        module.fail_json(msg=reason)

    return True, cmd, out, err


def remove_plugin(module, plugin_bin, plugin_name):
    cmd_args = [plugin_bin, PACKAGE_STATE_MAP["absent"], plugin_name]

    cmd = " ".join(cmd_args)

    if module.check_mode:
        rc, out, err = 0, "check mode", ""
    else:
        rc, out, err = module.run_command(cmd_args)

    if rc != 0:
        reason = parse_error(out)
        module.fail_json(msg=reason)

    return True, cmd, out, err


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(default="present", choices=list(PACKAGE_STATE_MAP.keys())),
            plugin_bin=dict(default="/usr/share/logstash/bin/logstash-plugin", type="path"),
            proxy_host=dict(),
            proxy_port=dict(),
            version=dict()
        ),
        supports_check_mode=True
    )

    name = module.params["name"]
    state = module.params["state"]
    plugin_bin = module.params["plugin_bin"]
    proxy_host = module.params["proxy_host"]
    proxy_port = module.params["proxy_port"]
    version = module.params["version"]

    present = is_plugin_present(module, plugin_bin, name)

    # skip if the state is correct
    if (present and state == "present") or (state == "absent" and not present):
        module.exit_json(changed=False, name=name, state=state)

    if state == "present":
        changed, cmd, out, err = install_plugin(module, plugin_bin, name, version, proxy_host, proxy_port)
    elif state == "absent":
        changed, cmd, out, err = remove_plugin(module, plugin_bin, name)

    module.exit_json(changed=changed, cmd=cmd, name=name, state=state, stdout=out, stderr=err)


if __name__ == '__main__':
    main()
