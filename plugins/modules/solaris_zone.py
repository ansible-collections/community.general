#!/usr/bin/python

# Copyright (c) 2015, Paul Markham <pmarkham@netrefinery.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: solaris_zone
short_description: Manage Solaris zones
description:
  - Create, start, stop and delete Solaris zones.
  - This module does not currently allow changing of options for a zone that is already been created.
author:
  - Paul Markham (@pmarkham)
requirements:
  - Solaris 10 or 11
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - V(present), configure and install the zone.
      - V(installed), synonym for V(present).
      - V(running), if the zone already exists, boot it, otherwise, configure and install the zone first, then boot it.
      - V(started), synonym for V(running).
      - V(stopped), shutdown a zone.
      - V(absent), destroy the zone.
      - V(configured), configure the ready so that it is to be attached.
      - V(attached), attach a zone, but do not boot it.
      - V(detached), shutdown and detach a zone.
    type: str
    choices: [absent, attached, configured, detached, installed, present, running, started, stopped]
    default: present
  name:
    description:
      - Zone name.
      - A zone name must be unique name.
      - A zone name must begin with an alphanumeric character.
      - The name can contain alphanumeric characters, underscores V(_), hyphens V(-), and periods V(.).
      - The name cannot be longer than 64 characters.
    type: str
    required: true
  path:
    description:
      - The path where the zone is created. This is required when the zone is created, but not used otherwise.
    type: str
  sparse:
    description:
      - Whether to create a sparse (V(true)) or whole root (V(false)) zone.
    type: bool
    default: false
  root_password:
    description:
      - The password hash for the root account. If not specified, the zone's root account does not have a password.
    type: str
  config:
    description:
      - The C(zonecfg) configuration commands for this zone. See zonecfg(1M) for the valid options and syntax. Typically this
        is a list of options separated by semi-colons or new lines, for example V(set auto-boot=true;add net;set physical=bge0;set
        address=10.1.1.1;end).
    type: str
    default: ''
  create_options:
    description:
      - Extra options to the zonecfg(1M) create command.
    type: str
    default: ''
  install_options:
    description:
      - Extra options to the zoneadm(1M) install command. To automate Solaris 11 zone creation, use this to specify the profile
        XML file, for example O(install_options=-c sc_profile.xml).
    type: str
    default: ''
  attach_options:
    description:
      - Extra options to the zoneadm attach command. For example, this can be used to specify whether a minimum or full update
        of packages is required and if any packages need to be deleted. For valid values, see zoneadm(1M).
    type: str
    default: ''
  timeout:
    description:
      - Timeout, in seconds, for zone to boot.
    type: int
    default: 600
"""

EXAMPLES = r"""
- name: Create and install a zone, but don't boot it
  community.general.solaris_zone:
    name: zone1
    state: present
    path: /zones/zone1
    sparse: true
    root_password: Be9oX7OSwWoU.
    config: 'set autoboot=true; add net; set physical=bge0; set address=10.1.1.1; end'

- name: Create and install a zone and boot it
  community.general.solaris_zone:
    name: zone1
    state: running
    path: /zones/zone1
    root_password: Be9oX7OSwWoU.
    config: 'set autoboot=true; add net; set physical=bge0; set address=10.1.1.1; end'

- name: Boot an already installed zone
  community.general.solaris_zone:
    name: zone1
    state: running

- name: Stop a zone
  community.general.solaris_zone:
    name: zone1
    state: stopped

- name: Destroy a zone
  community.general.solaris_zone:
    name: zone1
    state: absent

- name: Detach a zone
  community.general.solaris_zone:
    name: zone1
    state: detached

- name: Configure a zone, ready to be attached
  community.general.solaris_zone:
    name: zone1
    state: configured
    path: /zones/zone1
    root_password: Be9oX7OSwWoU.
    config: 'set autoboot=true; add net; set physical=bge0; set address=10.1.1.1; end'

- name: Attach zone1
  community.general.solaris_zone:
    name: zone1
    state: attached
    attach_options: -u
"""

import os
import platform
import re
import tempfile
import time

from ansible.module_utils.basic import AnsibleModule


class Zone:
    def __init__(self, module):
        self.changed = False
        self.msg = []

        self.module = module
        self.path = self.module.params["path"]
        self.name = self.module.params["name"]
        self.sparse = self.module.params["sparse"]
        self.root_password = self.module.params["root_password"]
        self.timeout = self.module.params["timeout"]
        self.config = self.module.params["config"]
        self.create_options = self.module.params["create_options"]
        self.install_options = self.module.params["install_options"]
        self.attach_options = self.module.params["attach_options"]

        self.zoneadm_cmd = self.module.get_bin_path("zoneadm", True)
        self.zonecfg_cmd = self.module.get_bin_path("zonecfg", True)
        self.ssh_keygen_cmd = self.module.get_bin_path("ssh-keygen", True)

        if self.module.check_mode:
            self.msg.append("Running in check mode")

        if platform.system() != "SunOS":
            self.module.fail_json(msg="This module requires Solaris")

        (self.os_major, self.os_minor) = platform.release().split(".")
        if int(self.os_minor) < 10:
            self.module.fail_json(msg="This module requires Solaris 10 or later")

        match = re.match("^[a-zA-Z0-9][-_.a-zA-Z0-9]{0,62}$", self.name)
        if not match:
            self.module.fail_json(
                msg="Provided zone name is not a valid zone name. "
                "Please refer documentation for correct zone name specifications."
            )

    def configure(self):
        if not self.path:
            self.module.fail_json(msg="Missing required argument: path")

        if not self.module.check_mode:
            t = tempfile.NamedTemporaryFile(delete=False, mode="wt")

            if self.sparse:
                t.write(f"create {self.create_options}\n")
                self.msg.append("creating sparse-root zone")
            else:
                t.write(f"create -b {self.create_options}\n")
                self.msg.append("creating whole-root zone")

            t.write(f"set zonepath={self.path}\n")
            t.write(f"{self.config}\n")
            t.close()

            cmd = [self.zonecfg_cmd, "-z", self.name, "-f", t.name]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to create zone. {out + err}")
            os.unlink(t.name)

        self.changed = True
        self.msg.append("zone configured")

    def install(self):
        if not self.module.check_mode:
            cmd = [self.zoneadm_cmd, "-z", self.name, "install", self.install_options]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to install zone. {out + err}")
            if int(self.os_minor) == 10:
                self.configure_sysid()
            self.configure_password()
            self.configure_ssh_keys()
        self.changed = True
        self.msg.append("zone installed")

    def uninstall(self):
        if self.is_installed():
            if not self.module.check_mode:
                cmd = [self.zoneadm_cmd, "-z", self.name, "uninstall", "-F"]
                (rc, out, err) = self.module.run_command(cmd)
                if rc != 0:
                    self.module.fail_json(msg=f"Failed to uninstall zone. {out + err}")
            self.changed = True
            self.msg.append("zone uninstalled")

    def configure_sysid(self):
        if os.path.isfile(f"{self.path}/root/etc/.UNCONFIGURED"):
            os.unlink(f"{self.path}/root/etc/.UNCONFIGURED")

        open(f"{self.path}/root/noautoshutdown", "w").close()

        with open(f"{self.path}/root/etc/nodename", "w") as node:
            node.write(self.name)

        with open(f"{self.path}/root/etc/.sysIDtool.state", "w") as id:
            id.write("1       # System previously configured?\n")
            id.write("1       # Bootparams succeeded?\n")
            id.write("1       # System is on a network?\n")
            id.write("1       # Extended network information gathered?\n")
            id.write("0       # Autobinder succeeded?\n")
            id.write("1       # Network has subnets?\n")
            id.write("1       # root password prompted for?\n")
            id.write("1       # locale and term prompted for?\n")
            id.write("1       # security policy in place\n")
            id.write("1       # NFSv4 domain configured\n")
            id.write("0       # Auto Registration Configured\n")
            id.write("vt100")

    def configure_ssh_keys(self):
        rsa_key_file = f"{self.path}/root/etc/ssh/ssh_host_rsa_key"
        dsa_key_file = f"{self.path}/root/etc/ssh/ssh_host_dsa_key"

        if not os.path.isfile(rsa_key_file):
            cmd = [self.ssh_keygen_cmd, "-f", rsa_key_file, "-t", "rsa", "-N", ""]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to create rsa key. {out + err}")

        if not os.path.isfile(dsa_key_file):
            cmd = [self.ssh_keygen_cmd, "-f", dsa_key_file, "-t", "dsa", "-N", ""]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to create dsa key. {out + err}")

    def configure_password(self):
        shadow = f"{self.path}/root/etc/shadow"
        if self.root_password:
            with open(shadow, "r") as f:
                lines = f.readlines()

            for i in range(0, len(lines)):
                fields = lines[i].split(":")
                if fields[0] == "root":
                    fields[1] = self.root_password
                    lines[i] = ":".join(fields)

            with open(shadow, "w") as f:
                for line in lines:
                    f.write(line)

    def boot(self):
        if not self.module.check_mode:
            cmd = [self.zoneadm_cmd, "-z", self.name, "boot"]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to boot zone. {out + err}")

            """
            The boot command can return before the zone has fully booted. This is especially
            true on the first boot when the zone initializes the SMF services. Unless the zone
            has fully booted, subsequent tasks in the playbook may fail as services aren't running yet.
            Wait until the zone's console login is running; once that's running, consider the zone booted.
            """

            elapsed = 0
            while True:
                if elapsed > self.timeout:
                    self.module.fail_json(msg="timed out waiting for zone to boot")
                rc = os.system(f'ps -z {self.name} -o args|grep "ttymon.*-d /dev/console" > /dev/null 2>/dev/null')
                if rc == 0:
                    break
                time.sleep(10)
                elapsed += 10
        self.changed = True
        self.msg.append("zone booted")

    def destroy(self):
        if self.is_running():
            self.stop()
        if self.is_installed():
            self.uninstall()
        if not self.module.check_mode:
            cmd = [self.zonecfg_cmd, "-z", self.name, "delete", "-F"]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to delete zone. {out + err}")
        self.changed = True
        self.msg.append("zone deleted")

    def stop(self):
        if not self.module.check_mode:
            cmd = [self.zoneadm_cmd, "-z", self.name, "halt"]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to stop zone. {out + err}")
        self.changed = True
        self.msg.append("zone stopped")

    def detach(self):
        if not self.module.check_mode:
            cmd = [self.zoneadm_cmd, "-z", self.name, "detach"]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to detach zone. {out + err}")
        self.changed = True
        self.msg.append("zone detached")

    def attach(self):
        if not self.module.check_mode:
            cmd = [self.zoneadm_cmd, "-z", self.name, "attach", self.attach_options]
            (rc, out, err) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=f"Failed to attach zone. {out + err}")
        self.changed = True
        self.msg.append("zone attached")

    def exists(self):
        cmd = [self.zoneadm_cmd, "-z", self.name, "list"]
        (rc, out, err) = self.module.run_command(cmd)
        if rc == 0:
            return True
        else:
            return False

    def is_running(self):
        return self.status() == "running"

    def is_installed(self):
        return self.status() == "installed"

    def is_configured(self):
        return self.status() == "configured"

    def status(self):
        cmd = [self.zoneadm_cmd, "-z", self.name, "list", "-p"]
        (rc, out, err) = self.module.run_command(cmd)
        if rc == 0:
            return out.split(":")[2]
        else:
            return "undefined"

    def state_present(self):
        if self.exists():
            self.msg.append("zone already exists")
        else:
            self.configure()
            self.install()

    def state_running(self):
        self.state_present()
        if self.is_running():
            self.msg.append("zone already running")
        else:
            self.boot()

    def state_stopped(self):
        if self.exists():
            self.stop()
        else:
            self.module.fail_json(msg="zone does not exist")

    def state_absent(self):
        if self.exists():
            if self.is_running():
                self.stop()
            self.destroy()
        else:
            self.msg.append("zone does not exist")

    def state_configured(self):
        if self.exists():
            self.msg.append("zone already exists")
        else:
            self.configure()

    def state_detached(self):
        if not self.exists():
            self.module.fail_json(msg="zone does not exist")
        if self.is_configured():
            self.msg.append("zone already detached")
        else:
            self.stop()
            self.detach()

    def state_attached(self):
        if not self.exists():
            self.msg.append("zone does not exist")
        if self.is_configured():
            self.attach()
        else:
            self.msg.append("zone already attached")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str",
                default="present",
                choices=[
                    "absent",
                    "attached",
                    "configured",
                    "detached",
                    "installed",
                    "present",
                    "running",
                    "started",
                    "stopped",
                ],
            ),
            path=dict(type="str"),
            sparse=dict(type="bool", default=False),
            root_password=dict(type="str", no_log=True),
            timeout=dict(type="int", default=600),
            config=dict(type="str", default=""),
            create_options=dict(type="str", default=""),
            install_options=dict(type="str", default=""),
            attach_options=dict(type="str", default=""),
        ),
        supports_check_mode=True,
    )

    zone = Zone(module)

    state = module.params["state"]

    if state == "running" or state == "started":
        zone.state_running()
    elif state == "present" or state == "installed":
        zone.state_present()
    elif state == "stopped":
        zone.state_stopped()
    elif state == "absent":
        zone.state_absent()
    elif state == "configured":
        zone.state_configured()
    elif state == "detached":
        zone.state_detached()
    elif state == "attached":
        zone.state_attached()
    else:
        module.fail_json(msg=f"Invalid state: {state}")

    module.exit_json(changed=zone.changed, msg=", ".join(zone.msg))


if __name__ == "__main__":
    main()
