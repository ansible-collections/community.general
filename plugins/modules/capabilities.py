#!/usr/bin/python

# Copyright (c) 2014, Nate Coraor <nate@bx.psu.edu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: capabilities
short_description: Manage Linux capabilities
description:
  - This module manipulates files privileges using the Linux capabilities(7) system.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    description:
      - Specifies the path to the file to be managed.
    type: str
    required: true
    aliases: [key]
  capability:
    description:
      - Desired capability to set (with operator and flags, if O(state=present)) or remove (if O(state=absent)).
      - The value is passed to C(setcap) as is, so it accepts the same syntax, including setting several capabilities
        at once (for example V(cap_chown,cap_fowner+ep)).
    type: str
    required: true
    aliases: [cap]
  state:
    description:
      - Whether the entry should be present or absent in the file's capabilities.
    type: str
    choices: [absent, present]
    default: present
notes:
  - Whether a change is required is determined with C(setcap --verify), so a task is reported as changed only when
    the capabilities on O(path) actually differ from the request, regardless of how the local C(libcap) version
    normalizes operators and flags (some versions turn C(cap_foo+ep) into C(cap_foo=ep)).
  - When O(state=present), capabilities already set on O(path) that are not listed in O(capability) are left untouched.
author:
  - Nate Coraor (@natefoo)
"""

EXAMPLES = r"""
- name: Set cap_sys_chroot+ep on /foo
  community.general.capabilities:
    path: /foo
    capability: cap_sys_chroot+ep
    state: present

- name: Remove cap_net_bind_service from /bar
  community.general.capabilities:
    path: /bar
    capability: cap_net_bind_service
    state: absent
"""

from ansible.module_utils.basic import AnsibleModule

OPS = ("=", "-", "+")


class CapabilitiesModule:
    platform = "Linux"
    distribution = None

    def __init__(self, module):
        self.module = module
        self.path = module.params["path"].strip()
        self.capability = module.params["capability"].strip().lower()
        self.state = module.params["state"]
        self.getcap_cmd = module.get_bin_path("getcap", required=True)
        self.setcap_cmd = module.get_bin_path("setcap", required=True)

        if self.state == "present" and not any(op in self.capability for op in OPS):
            self.module.fail_json(msg=f"Couldn't find operator (one of: {OPS})")

        self.run()

    def run(self):
        current = self.getcap(self.path)
        current_names = [cap[0] for cap in current]
        requested_names = self._requested_cap_names()

        # Preserve capabilities already on the file that the user did not mention.
        kept = [self._cap_str(cap) for cap in current if cap[0] not in requested_names]

        if self.state == "present":
            clauses = " ".join(kept + [self.capability])
        else:
            if not any(name in current_names for name in requested_names):
                self.module.exit_json(changed=False, state=self.state)
            clauses = " ".join(kept)

        if clauses:
            already_set = self._verify(clauses)
        else:
            # Desired state is "no capabilities": it already matches only if the file has none.
            already_set = not current

        if already_set:
            self.module.exit_json(changed=False, state=self.state)

        if self.module.check_mode:
            # setcap --verify can report a difference that setcap would not actually apply
            # (for example an effective-only flag without the matching permitted flag), but
            # check mode cannot run setcap to find out for sure without mutating the file, so
            # a reported difference is taken at face value here.
            self.module.exit_json(changed=True, state=self.state, msg="capabilities changed")

        stdout = self.setcap(self.path, clauses)
        # Now that setcap has actually run, confirm the change by re-reading the
        # capabilities instead of trusting the --verify result from above.
        changed = sorted(current) != sorted(self.getcap(self.path))
        self.module.exit_json(changed=changed, state=self.state, msg="capabilities changed", stdout=stdout)

    def getcap(self, path):
        rval = []
        cmd = [self.getcap_cmd, "-v", path]
        rc, stdout, stderr = self.module.run_command(cmd)
        # If file xattrs are set but no caps are set the output will be:
        #   '/foo ='
        # If file xattrs are unset the output will be:
        #   '/foo'
        # If the file does not exist, the stderr will be (with rc == 0...):
        #   '/foo (No such file or directory)'
        if rc != 0 or stderr != "":
            self.module.fail_json(msg=f"Unable to get capabilities of {path}", stdout=stdout.strip(), stderr=stderr)
        if stdout.strip() != path:
            if " =" in stdout:
                # process output of an older version of libcap
                caps = stdout.split(" =")[1].strip().split()
            elif stdout.strip().endswith(")"):  # '/foo (Error Message)'
                self.module.fail_json(msg=f"Unable to get capabilities of {path}", stdout=stdout.strip(), stderr=stderr)
            else:
                # otherwise, we have a newer version here
                # see original commit message of cap/v0.2.40-18-g177cd41 in libcap.git
                caps = stdout.split()[1].strip().split()
            for cap in caps:
                cap = cap.lower()
                # getcap condenses capabilities with the same op/flags into a
                # comma-separated list, so we have to parse that
                if "," in cap:
                    cap_group = cap.split(",")
                    cap_group[-1], op, flags = self._parse_cap(cap_group[-1])
                    for subcap in cap_group:
                        rval.append((subcap, op, flags))
                else:
                    rval.append(self._parse_cap(cap))
        return rval

    def setcap(self, path, clauses):
        cmd = [self.setcap_cmd, clauses, path]
        rc, stdout, stderr = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg=f"Unable to set capabilities of {path}", stdout=stdout, stderr=stderr)
        return stdout

    def _verify(self, clauses):
        """Return True when setcap does not need to run because the file already matches clauses."""
        cmd = [self.setcap_cmd, "-v", clauses, self.path]
        rc, dummy, dummy2 = self.module.run_command(cmd)
        return rc == 0

    def _requested_cap_names(self):
        """Return the capability names referenced by the capability parameter, ignoring operators and flags."""
        names = []
        for clause in self.capability.split():
            cut = len(clause)
            for op in OPS:
                pos = clause.find(op)
                if pos != -1:
                    cut = min(cut, pos)
            names.extend(name for name in clause[:cut].split(",") if name)
        return names

    @staticmethod
    def _cap_str(cap):
        name, op, flags = cap
        return f"{name}{op}{flags}"

    def _parse_cap(self, cap, op_required=True):
        opind = -1
        try:
            i = 0
            while opind == -1:
                opind = cap.find(OPS[i])
                i += 1
        except Exception:
            if op_required:
                self.module.fail_json(msg=f"Couldn't find operator (one of: {OPS})")
            else:
                return (cap, None, None)
        op = cap[opind]
        cap, flags = cap.split(op)
        return (cap, op, flags)


# ==============================================================
# main


def main():
    # defining module
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="str", required=True, aliases=["key"]),
            capability=dict(type="str", required=True, aliases=["cap"]),
            state=dict(type="str", default="present", choices=["absent", "present"]),
        ),
        supports_check_mode=True,
    )
    module.run_command_environ_update = {"LANGUAGE": "C", "LC_ALL": "C"}

    CapabilitiesModule(module)


if __name__ == "__main__":
    main()
