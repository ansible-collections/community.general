#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Lincoln Wallace (locnnil) <lincoln.wallace@canonical.com>
# Copyright (c) 2021, Alexei Znamensky (russoz) <russoz@gmail.com>
# Copyright (c) 2021, Marcus Rickert <marcus.rickert@web.de>
# Copyright (c) 2018, Stanislas Lange (angristan) <angristan@pm.me>
# Copyright (c) 2018, Victor Carceler <vcarceler@iespuigcastellar.xeill.net>

# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: snap
short_description: Manages snaps
description:
  - Manages snaps packages.
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
      - Name of the snaps to be installed.
      - Any named snap accepted by the C(snap) command is valid.
      - O(dangerous=true) may be necessary when installing C(.snap) files. See O(dangerous) for more details.
    required: true
    type: list
    elements: str
  state:
    description:
      - Desired state of the package.
      - When O(state=present) the module will use C(snap install) if the snap is not installed, and C(snap refresh) if it
        is installed but from a different channel.
    default: present
    choices: [absent, present, enabled, disabled]
    type: str
  classic:
    description:
      - Install a snap that has classic confinement.
      - This option corresponds to the C(--classic) argument of the C(snap install) command.
      - This level of confinement is permissive, granting full system access, similar to that of traditionally packaged applications
        that do not use sandboxing mechanisms. This option can only be specified when the task involves a single snap.
      - See U(https://snapcraft.io/docs/snap-confinement) for more details about classic confinement and confinement levels.
    type: bool
    required: false
    default: false
  channel:
    description:
      - Define which release of a snap is installed and tracked for updates. This option can only be specified if there is
        a single snap in the task.
      - If not passed, the C(snap) command will default to V(stable).
      - If the value passed does not contain the C(track), it will default to C(latest). For example, if V(edge) is passed,
        the module will assume the channel to be V(latest/edge).
      - See U(https://snapcraft.io/docs/channels) for more details about snap channels.
    type: str
    required: false
  options:
    description:
      - Set options with pattern C(key=value) or C(snap:key=value). If a snap name is given, the option will be applied to
        that snap only. If the snap name is omitted, the options will be applied to all snaps listed in O(name). Options will
        only be applied to active snaps.
      - Options will only be applied when C(state) is set to V(present). This is done after the necessary installation or
        refresh (upgrade/downgrade) of all the snaps listed in O(name).
      - See U(https://snapcraft.io/docs/configuration-in-snaps) for more details about snap configuration options.
    required: false
    type: list
    elements: str
    version_added: 4.4.0
  dangerous:
    description:
      - Install the snap in dangerous mode, without validating its assertions and signatures.
      - This is useful when installing local snaps that are either unsigned or have signatures that have not been acknowledged.
      - See U(https://snapcraft.io/docs/install-modes) for more details about installation modes.
    type: bool
    required: false
    default: false
    version_added: 7.2.0
notes:
  - Privileged operations, such as installing and configuring snaps, require root priviledges. This is only the case if the
    user has not logged in to the Snap Store.
author:
  - Victor Carceler (@vcarceler) <vcarceler@iespuigcastellar.xeill.net>
  - Stanislas Lange (@angristan) <angristan@pm.me>

seealso:
  - module: community.general.snap_alias
"""

EXAMPLES = r"""
# Install "foo" and "bar" snap
- name: Install foo
  community.general.snap:
    name:
      - foo
      - bar

# Install "foo" snap with options par1=A and par2=B
- name: Install "foo" with options
  community.general.snap:
    name:
      - foo
    options:
      - par1=A
      - par2=B

# Install "foo" and "bar" snaps with common option com=A and specific options fooPar=X and barPar=Y
- name: Install "foo" and "bar" with options
  community.general.snap:
    name:
      - foo
      - bar
    options:
      - com=A
      - foo:fooPar=X
      - bar:barPar=Y

# Remove "foo" snap
- name: Remove foo
  community.general.snap:
    name: foo
    state: absent

# Install a snap with classic confinement
- name: Install "foo" with option --classic
  community.general.snap:
    name: foo
    classic: true

# Install a snap with from a specific channel
- name: Install "foo" with option --channel=latest/edge
  community.general.snap:
    name: foo
    channel: latest/edge
"""

RETURN = r"""
classic:
  description: Whether or not the snaps were installed with the classic confinement.
  type: bool
  returned: When snaps are installed
channel:
  description: The channel the snaps were installed from.
  type: str
  returned: When snaps are installed
cmd:
  description: The command that was executed on the host.
  type: str
  returned: When changed is true
snaps_installed:
  description: The list of actually installed snaps.
  type: list
  returned: When any snaps have been installed
snaps_removed:
  description: The list of actually removed snaps.
  type: list
  returned: When any snaps have been removed
options_changed:
  description: The list of options set/changed in format C(snap:key=value).
  type: list
  returned: When any options have been changed/set
  version_added: 4.4.0
version:
  description: Versions of snap components as reported by C(snap version).
  type: dict
  returned: always
  version_added: 10.3.0
"""

import re
import json
import numbers

from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.snap import snap_runner, get_version


class Snap(StateModuleHelper):
    NOT_INSTALLED = 0
    CHANNEL_MISMATCH = 1
    INSTALLED = 2

    __disable_re = re.compile(r'(?:\S+\s+){5}(?P<notes>\S+)')
    __set_param_re = re.compile(r'(?P<snap_prefix>\S+:)?(?P<key>\S+)\s*=\s*(?P<value>.+)')
    __list_re = re.compile(r'^(?P<name>\S+)\s+\S+\s+\S+\s+(?P<channel>\S+)')
    module = dict(
        argument_spec={
            'name': dict(type='list', elements='str', required=True),
            'state': dict(type='str', default='present', choices=['absent', 'present', 'enabled', 'disabled']),
            'classic': dict(type='bool', default=False),
            'channel': dict(type='str'),
            'options': dict(type='list', elements='str'),
            'dangerous': dict(type='bool', default=False),
        },
        supports_check_mode=True,
    )
    use_old_vardict = False

    @staticmethod
    def _first_non_zero(a):
        for elem in a:
            if elem != 0:
                return elem

        return 0

    def __init_module__(self):
        self.runner = snap_runner(self.module)
        self.vars.version = get_version(self.runner)
        # if state=present there might be file names passed in 'name', in
        # which case they must be converted to their actual snap names, which
        # is done using the names_from_snaps() method calling 'snap info'.
        self.vars.set("snapinfo_run_info", [], output=(self.verbosity >= 4))
        self.vars.set("status_run_info", [], output=(self.verbosity >= 4))
        self.vars.set("status_out", None, output=(self.verbosity >= 4))
        self.vars.set("run_info", [], output=(self.verbosity >= 4))

        if self.vars.state == "present":
            self.vars.set("snap_names", self.names_from_snaps(self.vars.name))
            status_var = "snap_names"
        else:
            status_var = "name"
        self.vars.set("status_var", status_var, output=False)
        self.vars.set("snap_status", self.snap_status(self.vars[self.vars.status_var], self.vars.channel), output=False, change=True)
        self.vars.set("snap_status_map", dict(zip(self.vars.name, self.vars.snap_status)), output=False, change=True)

    def __quit_module__(self):
        self.vars.snap_status = self.snap_status(self.vars[self.vars.status_var], self.vars.channel)
        if self.vars.channel is None:
            self.vars.channel = "stable"

    def _run_multiple_commands(self, commands, actionable_names, bundle=True, refresh=False):
        results_cmd = []
        results_rc = []
        results_out = []
        results_err = []
        results_run_info = []

        state = "refresh" if refresh else self.vars.state

        with self.runner(commands + ["name"]) as ctx:
            if bundle:
                rc, out, err = ctx.run(state=state, name=actionable_names)
                results_cmd.append(commands + actionable_names)
                results_rc.append(rc)
                results_out.append(out.strip())
                results_err.append(err.strip())
                results_run_info.append(ctx.run_info)
            else:
                for name in actionable_names:
                    rc, out, err = ctx.run(state=state, name=name)
                    results_cmd.append(commands + [name])
                    results_rc.append(rc)
                    results_out.append(out.strip())
                    results_err.append(err.strip())
                    results_run_info.append(ctx.run_info)

        return (
            '; '.join([to_native(x) for x in results_cmd]),
            self._first_non_zero(results_rc),
            '\n'.join(results_out),
            '\n'.join(results_err),
            results_run_info,
        )

    def convert_json_subtree_to_map(self, json_subtree, prefix=None):
        option_map = {}

        if not isinstance(json_subtree, dict):
            self.do_raise("Non-dict non-leaf element encountered while parsing option map. "
                          "The output format of 'snap set' may have changed. Aborting!")

        for key, value in json_subtree.items():
            full_key = key if prefix is None else prefix + "." + key

            if isinstance(value, (str, float, bool, numbers.Integral)):
                option_map[full_key] = str(value)
            else:
                option_map.update(self.convert_json_subtree_to_map(json_subtree=value, prefix=full_key))

        return option_map

    def convert_json_to_map(self, json_string):
        json_object = json.loads(json_string)
        return self.convert_json_subtree_to_map(json_object)

    def retrieve_option_map(self, snap_name):
        with self.runner("get name") as ctx:
            rc, out, err = ctx.run(name=snap_name)

        if rc != 0:
            return {}

        result = out.splitlines()

        if "has no configuration" in result[0]:
            return {}

        try:
            option_map = self.convert_json_to_map(out)
            return option_map
        except Exception as e:
            self.do_raise(
                msg="Parsing option map returned by 'snap get {0}' triggers exception '{1}', output:\n'{2}'".format(snap_name, str(e), out))

    def names_from_snaps(self, snaps):
        def process_one(rc, out, err):
            res = [line for line in out.split("\n") if line.startswith("name:")]
            name = res[0].split()[1]
            return [name]

        def process_many(rc, out, err):
            # This needs to be "\n---" instead of just "---" because otherwise
            # if a snap uses "---" in its description then that will incorrectly
            # be interpreted as a separator between snaps in the output.
            outputs = out.split("\n---")
            res = []
            for sout in outputs:
                res.extend(process_one(rc, sout, ""))
            return res

        def process(rc, out, err):
            if len(snaps) == 1:
                check_error = err
                process_ = process_one
            else:
                check_error = out
                process_ = process_many

            if "warning: no snap found" in check_error:
                self.do_raise("Snaps not found: {0}.".format([x.split()[-1]
                                                              for x in out.split('\n')
                                                              if x.startswith("warning: no snap found")]))
            return process_(rc, out, err)

        names = []
        if snaps:
            with self.runner("info name", output_process=process) as ctx:
                try:
                    names = ctx.run(name=snaps)
                finally:
                    self.vars.snapinfo_run_info.append(ctx.run_info)
        return names

    def snap_status(self, snap_name, channel):
        def _status_check(name, channel, installed):
            match = [c for n, c in installed if n == name]
            if not match:
                return Snap.NOT_INSTALLED
            if channel and match[0] not in (channel, "latest/{0}".format(channel)):
                return Snap.CHANNEL_MISMATCH
            else:
                return Snap.INSTALLED

        with self.runner("_list") as ctx:
            rc, out, err = ctx.run(check_rc=True)
        list_out = out.split('\n')[1:]
        list_out = [self.__list_re.match(x) for x in list_out]
        list_out = [(m.group('name'), m.group('channel')) for m in list_out if m]
        self.vars.status_out = list_out
        self.vars.status_run_info = ctx.run_info

        return [_status_check(n, channel, list_out) for n in snap_name]

    def is_snap_enabled(self, snap_name):
        with self.runner("_list name") as ctx:
            rc, out, err = ctx.run(name=snap_name)
        if rc != 0:
            return None
        result = out.splitlines()[1]
        match = self.__disable_re.match(result)
        if not match:
            self.do_raise(msg="Unable to parse 'snap list {0}' output:\n{1}".format(snap_name, out))
        notes = match.group('notes')
        return "disabled" not in notes.split(',')

    def _present(self, actionable_snaps, refresh=False):
        self.changed = True
        self.vars.snaps_installed = actionable_snaps

        if self.check_mode:
            return

        params = ['state', 'classic', 'channel', 'dangerous']  # get base cmd parts
        has_one_pkg_params = bool(self.vars.classic) or self.vars.channel != 'stable'
        has_multiple_snaps = len(actionable_snaps) > 1

        if has_one_pkg_params and has_multiple_snaps:
            self.vars.cmd, rc, out, err, run_info = self._run_multiple_commands(params, actionable_snaps, bundle=False, refresh=refresh)
        else:
            self.vars.cmd, rc, out, err, run_info = self._run_multiple_commands(params, actionable_snaps, refresh=refresh)
        self.vars.run_info = run_info

        if rc == 0:
            return

        classic_snap_pattern = re.compile(r'^error: This revision of snap "(?P<package_name>\w+)"'
                                          r' was published using classic confinement')
        match = classic_snap_pattern.match(err)
        if match:
            err_pkg = match.group('package_name')
            msg = "Couldn't install {name} because it requires classic confinement".format(name=err_pkg)
        else:
            msg = "Ooops! Snap installation failed while executing '{cmd}', please examine logs and " \
                  "error output for more details.".format(cmd=self.vars.cmd)
        self.do_raise(msg=msg)

    def state_present(self):

        self.vars.set_meta('classic', output=True)
        self.vars.set_meta('channel', output=True)

        actionable_refresh = [snap for snap in self.vars.name if self.vars.snap_status_map[snap] == Snap.CHANNEL_MISMATCH]
        if actionable_refresh:
            self._present(actionable_refresh, refresh=True)
        actionable_install = [snap for snap in self.vars.name if self.vars.snap_status_map[snap] == Snap.NOT_INSTALLED]
        if actionable_install:
            self._present(actionable_install)

        self.set_options()

    def set_options(self):
        if self.vars.options is None:
            return

        actionable_snaps = [s for s in self.vars.name if self.vars.snap_status_map[s] != Snap.NOT_INSTALLED]
        overall_options_changed = []

        for snap_name in actionable_snaps:
            option_map = self.retrieve_option_map(snap_name=snap_name)

            options_changed = []

            for option_string in self.vars.options:
                match = self.__set_param_re.match(option_string)

                if not match:
                    msg = "Cannot parse set option '{option_string}'".format(option_string=option_string)
                    self.do_raise(msg)

                snap_prefix = match.group("snap_prefix")
                selected_snap_name = snap_prefix[:-1] if snap_prefix else None

                if selected_snap_name is not None and selected_snap_name not in self.vars.name:
                    msg = "Snap option '{option_string}' refers to snap which is not in the list of snap names".format(option_string=option_string)
                    self.do_raise(msg)

                if selected_snap_name is None or (snap_name is not None and snap_name == selected_snap_name):
                    key = match.group("key")
                    value = match.group("value").strip()

                    if key not in option_map or key in option_map and option_map[key] != value:
                        option_without_prefix = key + "=" + value
                        option_with_prefix = option_string if selected_snap_name is not None else snap_name + ":" + option_string
                        options_changed.append(option_without_prefix)
                        overall_options_changed.append(option_with_prefix)

            if options_changed:
                self.changed = True

                if not self.check_mode:
                    with self.runner("_set name options") as ctx:
                        rc, out, err = ctx.run(name=snap_name, options=options_changed)
                    if rc != 0:
                        if 'has no "configure" hook' in err:
                            msg = "Snap '{snap}' does not have any configurable options".format(snap=snap_name)
                            self.do_raise(msg)

                        msg = "Cannot set options '{options}' for snap '{snap}': error={error}".format(
                            options=" ".join(options_changed), snap=snap_name, error=err)
                        self.do_raise(msg)

        if overall_options_changed:
            self.vars.options_changed = overall_options_changed

    def _generic_state_action(self, actionable_func, actionable_var, params):
        actionable_snaps = [s for s in self.vars.name if actionable_func(s)]
        if not actionable_snaps:
            return
        self.changed = True
        self.vars[actionable_var] = actionable_snaps
        if self.check_mode:
            return
        self.vars.cmd, rc, out, err, run_info = self._run_multiple_commands(params, actionable_snaps)
        self.vars.run_info = run_info
        if rc == 0:
            return
        msg = "Ooops! Snap operation failed while executing '{cmd}', please examine logs and " \
              "error output for more details.".format(cmd=self.vars.cmd)
        self.do_raise(msg=msg)

    def state_absent(self):
        self._generic_state_action(lambda s: self.vars.snap_status_map[s] != Snap.NOT_INSTALLED, "snaps_removed", ['classic', 'channel', 'state'])

    def state_enabled(self):
        self._generic_state_action(lambda s: not self.is_snap_enabled(s), "snaps_enabled", ['classic', 'channel', 'state'])

    def state_disabled(self):
        self._generic_state_action(self.is_snap_enabled, "snaps_disabled", ['classic', 'channel', 'state'])


def main():
    Snap.execute()


if __name__ == '__main__':
    main()
