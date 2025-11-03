#!/usr/bin/python

# Copyright (c) 2016, Thierno IB. BARRY @barryib
# Sponsored by Polyconseil http://polyconseil.fr.
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: kibana_plugin
short_description: Manage Kibana plugins
description:
  - This module can be used to manage Kibana plugins.
author: Thierno IB. BARRY (@barryib)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the plugin to install.
    required: true
    type: str
  state:
    description:
      - Desired state of a plugin.
    choices: ["present", "absent"]
    default: present
    type: str
  url:
    description:
      - Set exact URL to download the plugin from.
      - For local file, prefix its absolute path with C(file://).
    type: str
  timeout:
    description:
      - 'Timeout setting: V(30s), V(1m), V(1h) and so on.'
    default: 1m
    type: str
  plugin_bin:
    description:
      - Location of the Kibana binary.
    default: /opt/kibana/bin/kibana
    type: path
  plugin_dir:
    description:
      - Your configured plugin directory specified in Kibana.
    default: /opt/kibana/installedPlugins/
    type: path
  version:
    description:
      - Version of the plugin to be installed.
      - If the plugin is installed with in a previous version, it is B(not) updated unless O(force=true).
    type: str
  force:
    description:
      - Delete and re-install the plugin. It can be useful for plugins update.
    type: bool
    default: false
  allow_root:
    description:
      - Whether to allow C(kibana) and C(kibana-plugin) to be run as root. Passes the C(--allow-root) flag to these commands.
    type: bool
    default: false
    version_added: 2.3.0
"""

EXAMPLES = r"""
- name: Install Elasticsearch head plugin
  community.general.kibana_plugin:
    state: present
    name: elasticsearch/marvel

- name: Install specific version of a plugin
  community.general.kibana_plugin:
    state: present
    name: elasticsearch/marvel
    version: '2.3.3'

- name: Uninstall Elasticsearch head plugin
  community.general.kibana_plugin:
    state: absent
    name: elasticsearch/marvel
"""

RETURN = r"""
cmd:
  description: The launched command during plugin management (install / remove).
  returned: success
  type: str
name:
  description: The plugin name to install or remove.
  returned: success
  type: str
url:
  description: The URL from where the plugin is installed from.
  returned: success
  type: str
timeout:
  description: The timeout for plugin download.
  returned: success
  type: str
state:
  description: The state for the managed plugin.
  returned: success
  type: str
"""

import os
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


PACKAGE_STATE_MAP = dict(present="--install", absent="--remove")


def parse_plugin_repo(string):
    elements = string.split("/")

    # We first consider the simplest form: pluginname
    repo = elements[0]

    # We consider the form: username/pluginname
    if len(elements) > 1:
        repo = elements[1]

    # remove elasticsearch- prefix
    # remove es- prefix
    for string in ("elasticsearch-", "es-"):
        if repo.startswith(string):
            return repo[len(string) :]

    return repo


def is_plugin_present(plugin_dir, working_dir):
    return os.path.isdir(os.path.join(working_dir, plugin_dir))


def parse_error(string):
    reason = "reason: "
    try:
        return string[string.index(reason) + len(reason) :].strip()
    except ValueError:
        return string


def install_plugin(module, plugin_bin, plugin_name, url, timeout, allow_root, kibana_version="4.6"):
    if LooseVersion(kibana_version) > LooseVersion("4.6"):
        kibana_plugin_bin = os.path.join(os.path.dirname(plugin_bin), "kibana-plugin")
        cmd_args = [kibana_plugin_bin, "install"]
        if url:
            cmd_args.append(url)
        else:
            cmd_args.append(plugin_name)
    else:
        cmd_args = [plugin_bin, "plugin", PACKAGE_STATE_MAP["present"], plugin_name]

        if url:
            cmd_args.extend(["--url", url])

    if timeout:
        cmd_args.extend(["--timeout", timeout])

    if allow_root:
        cmd_args.append("--allow-root")

    if module.check_mode:
        return True, " ".join(cmd_args), "check mode", ""

    rc, out, err = module.run_command(cmd_args)
    if rc != 0:
        reason = parse_error(out)
        module.fail_json(msg=reason)

    return True, " ".join(cmd_args), out, err


def remove_plugin(module, plugin_bin, plugin_name, allow_root, kibana_version="4.6"):
    if LooseVersion(kibana_version) > LooseVersion("4.6"):
        kibana_plugin_bin = os.path.join(os.path.dirname(plugin_bin), "kibana-plugin")
        cmd_args = [kibana_plugin_bin, "remove", plugin_name]
    else:
        cmd_args = [plugin_bin, "plugin", PACKAGE_STATE_MAP["absent"], plugin_name]

    if allow_root:
        cmd_args.append("--allow-root")

    if module.check_mode:
        return True, " ".join(cmd_args), "check mode", ""

    rc, out, err = module.run_command(cmd_args)
    if rc != 0:
        reason = parse_error(out)
        module.fail_json(msg=reason)

    return True, " ".join(cmd_args), out, err


def get_kibana_version(module, plugin_bin, allow_root):
    cmd_args = [plugin_bin, "--version"]

    if allow_root:
        cmd_args.append("--allow-root")

    rc, out, err = module.run_command(cmd_args)
    if rc != 0:
        module.fail_json(msg=f"Failed to get Kibana version : {err}")

    return out.strip()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(default="present", choices=list(PACKAGE_STATE_MAP.keys())),
            url=dict(),
            timeout=dict(default="1m"),
            plugin_bin=dict(default="/opt/kibana/bin/kibana", type="path"),
            plugin_dir=dict(default="/opt/kibana/installedPlugins/", type="path"),
            version=dict(),
            force=dict(default=False, type="bool"),
            allow_root=dict(default=False, type="bool"),
        ),
        supports_check_mode=True,
    )

    name = module.params["name"]
    state = module.params["state"]
    url = module.params["url"]
    timeout = module.params["timeout"]
    plugin_bin = module.params["plugin_bin"]
    plugin_dir = module.params["plugin_dir"]
    version = module.params["version"]
    force = module.params["force"]
    allow_root = module.params["allow_root"]

    changed, cmd, out, err = False, "", "", ""

    kibana_version = get_kibana_version(module, plugin_bin, allow_root)

    present = is_plugin_present(parse_plugin_repo(name), plugin_dir)

    # skip if the state is correct
    if (present and state == "present" and not force) or (state == "absent" and not present and not force):
        module.exit_json(changed=False, name=name, state=state)

    if version:
        name = f"{name}/{version}"

    if state == "present":
        if force:
            remove_plugin(module, plugin_bin, name, allow_root, kibana_version)
        changed, cmd, out, err = install_plugin(module, plugin_bin, name, url, timeout, allow_root, kibana_version)

    elif state == "absent":
        changed, cmd, out, err = remove_plugin(module, plugin_bin, name, allow_root, kibana_version)

    module.exit_json(changed=changed, cmd=cmd, name=name, state=state, url=url, timeout=timeout, stdout=out, stderr=err)


if __name__ == "__main__":
    main()
