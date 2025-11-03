#!/usr/bin/python

# Copyright (c) 2015, Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: puppet
short_description: Runs puppet
description:
  - Runs C(puppet) agent or apply in a reliable manner.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  timeout:
    description:
      - How long to wait for C(puppet) to finish.
    type: str
    default: 30m
  puppetmaster:
    description:
      - The hostname of the puppetmaster to contact.
    type: str
  modulepath:
    description:
      - Path to an alternate location for puppet modules.
    type: str
  manifest:
    description:
      - Path to the manifest file to run puppet apply on.
    type: str
  noop:
    description:
      - Override puppet.conf noop mode.
      - When V(true), run Puppet agent with C(--noop) switch set.
      - When V(false), run Puppet agent with C(--no-noop) switch set.
      - When unset (default), use default or puppet.conf value if defined.
    type: bool
  facts:
    description:
      - A dict of values to pass in as persistent external facter facts.
    type: dict
  facter_basename:
    description:
      - Basename of the facter output file.
    type: str
    default: ansible
  environment:
    description:
      - Puppet environment to be used.
    type: str
  confdir:
    description:
      - Path to the directory containing the puppet.conf file.
    type: str
    version_added: 5.1.0
  logdest:
    description:
      - Where the puppet logs should go, if puppet apply is being used.
      - V(all) goes to both C(console) and C(syslog).
      - V(stdout) is deprecated and replaced by C(console).
    type: str
    choices: [all, stdout, syslog]
    default: stdout
  certname:
    description:
      - The name to use when handling certificates.
    type: str
  tags:
    description:
      - A list of puppet tags to be used.
    type: list
    elements: str
  skip_tags:
    description:
      - A list of puppet tags to be excluded.
    type: list
    elements: str
    version_added: 6.6.0
  execute:
    description:
      - Execute a specific piece of Puppet code.
      - It has no effect with a puppetmaster.
    type: str
  use_srv_records:
    description:
      - Toggles use_srv_records flag.
    type: bool
  summarize:
    description:
      - Whether to print a transaction summary.
    type: bool
    default: false
  waitforlock:
    description:
      - The maximum amount of time C(puppet) should wait for an already running C(puppet) agent to finish before starting.
      - If a number without unit is provided, it is assumed to be a number of seconds. Allowed units are V(m) for minutes
        and V(h) for hours.
    type: str
    version_added: 9.0.0
  verbose:
    description:
      - Print extra information.
    type: bool
    default: false
  debug:
    description:
      - Enable full debugging.
    type: bool
    default: false
  show_diff:
    description:
      - Whether to print file changes details.
    type: bool
    default: false
  environment_lang:
    description:
      - The lang environment to use when running the puppet agent.
      - The default value, V(C), is supported on every system, but can lead to encoding errors if UTF-8 is used in the output.
      - Use V(C.UTF-8) or V(en_US.UTF-8) or similar UTF-8 supporting locales in case of problems. You need to make sure the
        selected locale is supported on the system the puppet agent runs on.
      - Starting with community.general 9.1.0, you can use the value V(auto) and the module tries to determine the best parseable
        locale to use.
    type: str
    default: C
    version_added: 8.6.0
requirements:
  - puppet
author:
  - Monty Taylor (@emonty)
"""

EXAMPLES = r"""
- name: Run puppet agent and fail if anything goes wrong
  community.general.puppet:

- name: Run puppet and timeout in 5 minutes
  community.general.puppet:
    timeout: 5m

- name: Run puppet using a different environment
  community.general.puppet:
    environment: testing

- name: Run puppet using a specific certname
  community.general.puppet:
    certname: agent01.example.com

- name: Run puppet using a specific piece of Puppet code. Has no effect with a puppetmaster
  community.general.puppet:
    execute: include ::mymodule

- name: Run puppet using a specific tags
  community.general.puppet:
    tags:
      - update
      - nginx
    skip_tags:
      - service

- name: Wait 30 seconds for any current puppet runs to finish
  community.general.puppet:
    waitforlock: 30

- name: Wait 5 minutes for any current puppet runs to finish
  community.general.puppet:
    waitforlock: 5m

- name: Run puppet agent in noop mode
  community.general.puppet:
    noop: true

- name: Run a manifest with debug, log to both syslog and console, specify module path
  community.general.puppet:
    modulepath: /etc/puppet/modules:/opt/stack/puppet-modules:/usr/share/openstack-puppet/modules
    logdest: all
    manifest: /var/lib/example/puppet_step_config.pp
"""

import json
import os
import stat

import ansible_collections.community.general.plugins.module_utils.puppet as puppet_utils

from ansible.module_utils.basic import AnsibleModule


def _write_structured_data(basedir, basename, data):
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    file_path = os.path.join(basedir, f"{basename}.json")
    # This is more complex than you might normally expect because we want to
    # open the file with only u+rw set. Also, we use the stat constants
    # because ansible still supports python 2.4 and the octal syntax changed
    out_file = os.fdopen(os.open(file_path, os.O_CREAT | os.O_WRONLY, stat.S_IRUSR | stat.S_IWUSR), "w")
    out_file.write(json.dumps(data).encode("utf8"))
    out_file.close()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            timeout=dict(type="str", default="30m"),
            puppetmaster=dict(type="str"),
            modulepath=dict(type="str"),
            manifest=dict(type="str"),
            confdir=dict(type="str"),
            noop=dict(type="bool"),
            logdest=dict(type="str", default="stdout", choices=["all", "stdout", "syslog"]),
            # The following is not related to Ansible's diff; see https://github.com/ansible-collections/community.general/pull/3980#issuecomment-1005666154
            show_diff=dict(type="bool", default=False),
            facts=dict(type="dict"),
            facter_basename=dict(type="str", default="ansible"),
            environment=dict(type="str"),
            certname=dict(type="str"),
            tags=dict(type="list", elements="str"),
            skip_tags=dict(type="list", elements="str"),
            execute=dict(type="str"),
            summarize=dict(type="bool", default=False),
            waitforlock=dict(type="str"),
            debug=dict(type="bool", default=False),
            verbose=dict(type="bool", default=False),
            use_srv_records=dict(type="bool"),
            environment_lang=dict(type="str", default="C"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ("puppetmaster", "manifest"),
            ("puppetmaster", "manifest", "execute"),
            ("puppetmaster", "modulepath"),
        ],
    )
    p = module.params

    if p["manifest"]:
        if not os.path.exists(p["manifest"]):
            module.fail_json(msg=f"Manifest file {dict(manifest=p['manifest'])['manifest']} not found.")

    # Check if puppet is disabled here
    if not p["manifest"]:
        puppet_utils.ensure_agent_enabled(module)

    if module.params["facts"] and not module.check_mode:
        _write_structured_data(puppet_utils.get_facter_dir(), module.params["facter_basename"], module.params["facts"])

    runner = puppet_utils.puppet_runner(module)

    if not p["manifest"] and not p["execute"]:
        args_order = "_agent_fixed puppetmaster show_diff confdir environment tags skip_tags certname noop use_srv_records waitforlock"
        with runner(args_order) as ctx:
            rc, stdout, stderr = ctx.run()
    else:
        args_order = "_apply_fixed logdest modulepath environment certname tags skip_tags noop _execute summarize debug verbose waitforlock"
        with runner(args_order) as ctx:
            rc, stdout, stderr = ctx.run(_execute=[p["execute"], p["manifest"]])

    if rc == 0:
        # success
        module.exit_json(rc=rc, changed=False, stdout=stdout, stderr=stderr)
    elif rc == 1:
        # rc==1 could be because it is disabled
        # rc==1 could also mean there was a compilation failure
        disabled = "administratively disabled" in stdout
        if disabled:
            msg = "puppet is disabled"
        else:
            msg = "puppet did not run"
        module.exit_json(rc=rc, disabled=disabled, msg=msg, error=True, stdout=stdout, stderr=stderr)
    elif rc == 2:
        # success with changes
        module.exit_json(rc=0, changed=True, stdout=stdout, stderr=stderr)
    elif rc == 124:
        # timeout
        module.exit_json(rc=rc, msg=f"{ctx.cmd} timed out", stdout=stdout, stderr=stderr)
    else:
        # failure
        module.fail_json(rc=rc, msg=f"{ctx.cmd} failed with return code: {rc}", stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    main()
