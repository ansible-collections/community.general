#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Afterburn <https://github.com/afterburn>
# Copyright: (c) 2013, Aaron Bull Schaefer <aaron@elasticdog.com>
# Copyright: (c) 2015, Indrajit Raychaudhuri <irc+code@indrajit.com>
# Copyright: (c) 2022, Jean Raby <jean@raby.sh>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: pacman
short_description: Manage packages with I(pacman)
description:
    - Manage packages with the I(pacman) package manager, which is used by Arch Linux and its variants.
author:
    - Indrajit Raychaudhuri (@indrajitr)
    - Aaron Bull Schaefer (@elasticdog) <aaron@elasticdog.com>
    - Maxime de Roucy (@tchernomax)
    - Jean Raby (@jraby)
options:
    name:
        description:
            - Name or list of names of the package(s) or file(s) to install, upgrade, or remove.
              Can't be used in combination with C(upgrade).
        aliases: [ package, pkg ]
        type: list
        elements: str

    state:
        description:
          - Whether to install (C(present) or C(installed), C(latest)), or remove (C(absent) or C(removed)) a package.
          - C(present) and C(installed) will simply ensure that a desired package is installed.
          - C(latest) will update the specified package if it is not of the latest available version.
          - C(absent) and C(removed) will remove the specified package.
        default: present
        choices: [ absent, installed, latest, present, removed ]
        type: str

    force:
        description:
            - When removing package, force remove package, without any checks.
              Same as `extra_args="--nodeps --nodeps"`.
              When update_cache, force redownload repo databases.
              Same as `update_cache_extra_args="--refresh --refresh"`.
        default: no
        type: bool

    executable:
        description:
            - Name of binary to use. This can either be C(pacman) or a pacman compatible AUR helper.
            - Beware that AUR helpers might behave unexpectedly and are therefore not recommended.
        default: pacman
        type: str
        version_added: 3.1.0

    extra_args:
        description:
            - Additional option to pass to pacman when enforcing C(state).
        default:
        type: str

    update_cache:
        description:
            - Whether or not to refresh the master package lists.
            - This can be run as part of a package installation or as a separate step.
            - Alias C(update-cache) has been deprecated and will be removed in community.general 5.0.0.
            - If not specified, it defaults to C(false).
        type: bool
        aliases: [ update-cache ]

    update_cache_extra_args:
        description:
            - Additional option to pass to pacman when enforcing C(update_cache).
        default:
        type: str

    upgrade:
        description:
            - Whether or not to upgrade the whole system.
              Can't be used in combination with C(name).
            - If not specified, it defaults to C(false).
        type: bool

    upgrade_extra_args:
        description:
            - Additional option to pass to pacman when enforcing C(upgrade).
        default:
        type: str

notes:
  - When used with a C(loop:) each package will be processed individually,
    it is much more efficient to pass the list directly to the I(name) option.
  - To use an AUR helper (I(executable) option), a few extra setup steps might be required beforehand.
    For example, a dedicated build user with permissions to install packages could be necessary.
"""

RETURN = """
packages:
    description: a list of packages that have been changed
    returned: when upgrade is set to yes
    type: list
    sample: [ package, other-package ]

stdout:
    description: Output from pacman.
    returned: success, when needed
    type: str
    sample: ":: Synchronizing package databases...  core is up to date :: Starting full system upgrade..."
    version_added: 4.1.0

stderr:
    description: Error output from pacman.
    returned: success, when needed
    type: str
    sample: "warning: libtool: local (2.4.6+44+gb9b44533-14) is newer than core (2.4.6+42+gb88cebd5-15)\nwarning ..."
    version_added: 4.1.0
"""

EXAMPLES = """
- name: Install package foo from repo
  community.general.pacman:
    name: foo
    state: present

- name: Install package bar from file
  community.general.pacman:
    name: ~/bar-1.0-1-any.pkg.tar.xz
    state: present

- name: Install package foo from repo and bar from file
  community.general.pacman:
    name:
      - foo
      - ~/bar-1.0-1-any.pkg.tar.xz
    state: present

- name: Install package from AUR using a Pacman compatible AUR helper
  community.general.pacman:
    name: foo
    state: present
    executable: yay
    extra_args: --builddir /var/cache/yay

- name: Upgrade package foo
  community.general.pacman:
    name: foo
    state: latest
    update_cache: yes

- name: Remove packages foo and bar
  community.general.pacman:
    name:
      - foo
      - bar
    state: absent

- name: Recursively remove package baz
  community.general.pacman:
    name: baz
    state: absent
    extra_args: --recursive

- name: Run the equivalent of "pacman -Sy" as a separate step
  community.general.pacman:
    update_cache: yes

- name: Run the equivalent of "pacman -Su" as a separate step
  community.general.pacman:
    upgrade: yes

- name: Run the equivalent of "pacman -Syu" as a separate step
  community.general.pacman:
    update_cache: yes
    upgrade: yes

- name: Run the equivalent of "pacman -Rdd", force remove package baz
  community.general.pacman:
    name: baz
    state: absent
    force: yes
"""

import shlex
from ansible.module_utils.basic import AnsibleModule
from collections import defaultdict, namedtuple


Package = namedtuple("Package", ["name", "source"])
VersionTuple = namedtuple("VersionTuple", ["current", "latest"])


class Pacman(object):
    def __init__(self, module):
        self.m = module

        self.m.run_command_environ_update = dict(LC_ALL="C")
        p = self.m.params

        self._msgs = []
        self._stdouts = []
        self._stderrs = []
        self.changed = False
        self.exit_params = {}

        self.pacman_path = self.m.get_bin_path(p["executable"], True)

        # Normalize for old configs
        if p["state"] == "installed":
            self.target_state = "present"
        elif p["state"] == "removed":
            self.target_state = "absent"
        else:
            self.target_state = p["state"]

    def add_exit_infos(self, msg=None, stdout=None, stderr=None):
        if msg:
            self._msgs.append(msg)
        if stdout:
            self._stdouts.append(stdout)
        if stderr:
            self._stderrs.append(stderr)

    def _set_mandatory_exit_params(self):
        msg = "\n".join(self._msgs)
        stdouts = "\n".join(self._stdouts)
        stderrs = "\n".join(self._stderrs)
        if stdouts:
            self.exit_params["stdout"] = stdouts
        if stderrs:
            self.exit_params["stderr"] = stderrs
        self.exit_params["msg"] = msg  # mandatory, but might be empty

    def fail(self, msg=None, stdout=None, stderr=None, **kwargs):
        self.add_exit_infos(msg, stdout, stderr)
        self._set_mandatory_exit_params()
        if kwargs:
            self.exit_params.update(**kwargs)
        self.m.fail_json(**self.exit_params)

    def success(self):
        self._set_mandatory_exit_params()
        self.m.exit_json(changed=self.changed, **self.exit_params)

    def run(self):
        if self.m.params["update_cache"]:
            self.update_package_db()

            if not (self.m.params["name"] or self.m.params["upgrade"]):
                self.success()

        self.inventory = self._build_inventory()
        if self.m.params["upgrade"]:
            self.upgrade()
            self.success()

        if self.m.params["name"]:
            pkgs = self.package_list()

            if self.target_state == "absent":
                self.remove_packages(pkgs)
                self.success()
            else:
                self.install_packages(pkgs)
                self.success()

        # This shouldn't happen...
        self.fail("This is a bug")

    def install_packages(self, pkgs):
        pkgs_to_install = []
        for p in pkgs:
            if (
                p.name not in self.inventory["installed_pkgs"]
                or self.target_state == "latest"
                and p.name in self.inventory["upgradable_pkgs"]
            ):
                pkgs_to_install.append(p)

        if len(pkgs_to_install) == 0:
            self.add_exit_infos("package(s) already installed")
            return

        self.changed = True
        cmd_base = [
            self.pacman_path,
            "--sync",
            "--noconfirm",
            "--noprogressbar",
            "--needed",
        ]
        if self.m.params["extra_args"]:
            cmd_base.extend(self.m.params["extra_args"])

        # Dry run first to gather what will be done
        cmd = cmd_base + ["--print-format", "%n %v"] + [p.source for p in pkgs_to_install]
        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("Failed to list package(s) to install", stdout=stdout, stderr=stderr)

        name_ver = [l.strip() for l in stdout.splitlines()]
        before = []
        after = []
        installed_pkgs = []
        self.exit_params["packages"] = []
        for p in name_ver:
            name, version = p.split()
            if name in self.inventory["installed_pkgs"]:
                before.append("%s-%s" % (name, self.inventory["installed_pkgs"][name]))
            after.append("%s-%s" % (name, version))
            installed_pkgs.append(name)

        self.exit_params["diff"] = {
            "before": "\n".join(before) + "\n" if before else "",
            "after": "\n".join(after) + "\n" if after else "",
        }

        if self.m.check_mode:
            self.add_exit_infos("Would have installed %d packages" % len(installed_pkgs))
            self.exit_params["packages"] = installed_pkgs
            return

        # actually do it
        cmd = cmd_base + [p.source for p in pkgs_to_install]

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("Failed to install package(s)", stdout=stdout, stderr=stderr)

        self.exit_params["packages"] = installed_pkgs
        self.add_exit_infos(
            "Installed %d package(s)" % len(installed_pkgs), stdout=stdout, stderr=stderr
        )

    def remove_packages(self, pkgs):
        force_args = ["--nodeps", "--nodeps"] if self.m.params["force"] else []

        # filter out pkgs that are already absent
        pkg_names_to_remove = [p.name for p in pkgs if p.name in self.inventory["installed_pkgs"]]

        if len(pkg_names_to_remove) == 0:
            self.add_exit_infos("package(s) already absent")
            return

        # There's something to do, set this in advance
        self.changed = True

        cmd_base = [self.pacman_path, "--remove", "--noconfirm", "--noprogressbar"]
        if self.m.params["extra_args"]:
            cmd_base.extend(self.m.params["extra_args"])
        if force_args:
            cmd_base.extend(force_args)

        # This is a bit of a TOCTOU but it is better than parsing the output of
        # pacman -R, which is different depending on the user config (VerbosePkgLists)
        # Start by gathering what would be removed
        cmd = cmd_base + ["--print-format", "%n-%v"] + pkg_names_to_remove

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("failed to list package(s) to remove", stdout=stdout, stderr=stderr)

        removed_pkgs = stdout.split()
        self.exit_params["packages"] = removed_pkgs
        self.exit_params["diff"] = {
            "before": "\n".join(removed_pkgs) + "\n",  # trailing \n to avoid diff complaints
            "after": "",
        }

        if self.m.check_mode:
            self.exit_params["packages"] = removed_pkgs
            self.add_exit_infos("Would have removed %d packages" % len(removed_pkgs))
            return

        # actually do it
        cmd = cmd_base + pkg_names_to_remove

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("failed to remove package(s)", stdout=stdout, stderr=stderr)
        self.exit_params["packages"] = removed_pkgs
        self.add_exit_infos("Removed %d package(s)" % len(removed_pkgs), stdout=stdout, stderr=stderr)

    def upgrade(self):
        """Runs pacman --sync --sysupgrade if there are upgradable packages"""

        if len(self.inventory["upgradable_pkgs"]) == 0:
            self.add_exit_infos("Nothing to upgrade")
            return

        self.changed = True  # there are upgrades, so there will be changes

        # Build diff based on inventory first.
        diff = {"before": "", "after": ""}
        for pkg, versions in self.inventory["upgradable_pkgs"].items():
            diff["before"] += "%s-%s\n" % (pkg, versions.current)
            diff["after"] += "%s-%s\n" % (pkg, versions.latest)
        self.exit_params["diff"] = diff
        self.exit_params["packages"] = self.inventory["upgradable_pkgs"].keys()

        if self.m.check_mode:
            self.add_exit_infos(
                "%d packages would have been upgraded" % (len(self.inventory["upgradable_pkgs"]))
            )
        else:
            cmd = [
                self.pacman_path,
                "--sync",
                "--sys-upgrade",
                "--quiet",
                "--noconfirm",
            ]
            if self.m.params["upgrade_extra_args"]:
                cmd += self.m.params["upgrade_extra_args"]
            rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
            if rc == 0:
                self.add_exit_infos("System upgraded", stdout=stdout, stderr=stderr)
            else:
                self.fail("Could not upgrade", stdout=stdout, stderr=stderr)

    def update_package_db(self):
        """runs pacman --sync --refresh"""
        if self.m.check_mode:
            self.add_exit_infos("Would have updated the package db")
            self.changed = True
            return

        cmd = [
            self.pacman_path,
            "--sync",
            "--refresh",
        ]
        if self.m.params["update_cache_extra_args"]:
            cmd += self.m.params["update_cache_extra_args"]
        if self.m.params["force"]:
            cmd += ["--refresh"]

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)

        self.changed = True

        if rc == 0:
            self.add_exit_infos("Updated package db", stdout=stdout, stderr=stderr)
        else:
            self.fail("could not update package db", stdout=stdout, stderr=stderr)

    def package_list(self):
        """Takes the input package list and resolves packages groups to their package list using the inventory,
        extracts package names from packages given as files or URLs using calls to pacman

        Returns the expanded/resolved list as a list of Package
        """
        pkg_list = []
        for pkg in self.m.params["name"]:
            if not pkg:
                continue

            if pkg in self.inventory["available_groups"]:
                # Expand group members
                for group_member in self.inventory["available_groups"][pkg]:
                    pkg_list.append(Package(name=group_member, source=group_member))
            elif pkg in self.inventory["available_pkgs"]:
                # just a regular pkg
                pkg_list.append(Package(name=pkg, source=pkg))
            else:
                # Last resort, call out to pacman to extract the info,
                # pkg is possibly in the <repo>/<pkgname> format, or a filename or a URL

                # Start with <repo>/<pkgname> case
                cmd = [self.pacman_path, "--sync", "--print-format", "%n", pkg]
                rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
                if rc != 0:
                    # fallback to filename / URL
                    cmd = [self.pacman_path, "--upgrade", "--print-format", "%n", pkg]
                    rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
                    if rc != 0:
                        if self.target_state == "absent":
                            continue  # Don't bark for unavailable packages when trying to remove them
                        else:
                            self.fail(
                                msg="Failed to list package %s" % (pkg),
                                cmd=cmd,
                                stdout=stdout,
                                stderr=stderr,
                                rc=rc,
                            )
                pkg_name = stdout.strip()
                pkg_list.append(Package(name=pkg_name, source=pkg))

        return pkg_list

    def _build_inventory(self):
        """Build a cache datastructure used for all pkg lookups
        Returns a dict:
        {
            "installed_pkgs": {pkgname: version},
            "installed_groups": {groupname: set(pkgnames)},
            "available_pkgs": {pkgname: version},
            "available_groups": {groupname: set(pkgnames)},
            "upgradable_pkgs": {pkgname: (current_version,latest_version)},
        }

        Fails the module if a package requested for install cannot be found
        """

        installed_pkgs = {}
        dummy, stdout, dummy = self.m.run_command([self.pacman_path, "--query"], check_rc=True)
        # Format of a line: "pacman 6.0.1-2"
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            pkg, ver = l.split()
            installed_pkgs[pkg] = ver

        installed_groups = defaultdict(set)
        dummy, stdout, dummy = self.m.run_command(
            [self.pacman_path, "--query", "--group"], check_rc=True
        )
        # Format of lines:
        #     base-devel file
        #     base-devel findutils
        #     ...
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            group, pkgname = l.split()
            installed_groups[group].add(pkgname)

        available_pkgs = {}
        dummy, stdout, dummy = self.m.run_command([self.pacman_path, "--sync", "--list"], check_rc=True)
        # Format of a line: "core pacman 6.0.1-2"
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            repo, pkg, ver = l.split()[:3]
            available_pkgs[pkg] = ver

        available_groups = defaultdict(set)
        dummy, stdout, dummy = self.m.run_command(
            [self.pacman_path, "--sync", "--group", "--group"], check_rc=True
        )
        # Format of lines:
        #     vim-plugins vim-airline
        #     vim-plugins vim-airline-themes
        #     vim-plugins vim-ale
        #     ...
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            group, pkg = l.split()
            available_groups[group].add(pkg)

        upgradable_pkgs = {}
        rc, stdout, stderr = self.m.run_command(
            [self.pacman_path, "--query", "--upgrades"], check_rc=False
        )

        # non-zero exit with nothing in stdout -> nothing to upgrade, all good
        # stderr can have warnings, so not checked here
        if rc == 1 and stdout == "":
            pass  # nothing to upgrade
        elif rc == 0:
            # Format of lines:
            #     strace 5.14-1 -> 5.15-1
            #     systemd 249.7-1 -> 249.7-2 [ignored]
            for l in stdout.splitlines():
                l = l.strip()
                if not l:
                    continue
                if "[ignored]" in l:
                    continue
                s = l.split()
                if len(s) != 4:
                    self.fail(msg="Invalid line: %s" % l)

                pkg = s[0]
                current = s[1]
                latest = s[3]
                upgradable_pkgs[pkg] = VersionTuple(current=current, latest=latest)
        else:
            # stuff in stdout but rc!=0, abort
            self.fail(
                "Couldn't get list of packages available for upgrade",
                stdout=stdout,
                stderr=stderr,
                rc=rc,
            )

        return dict(
            installed_pkgs=installed_pkgs,
            installed_groups=installed_groups,
            available_pkgs=available_pkgs,
            available_groups=available_groups,
            upgradable_pkgs=upgradable_pkgs,
        )


def setup_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="list", elements="str", aliases=["pkg", "package"]),
            state=dict(
                type="str",
                default="present",
                choices=["present", "installed", "latest", "absent", "removed"],
            ),
            force=dict(type="bool", default=False),
            executable=dict(type="str", default="pacman"),
            extra_args=dict(type="str", default=""),
            upgrade=dict(type="bool"),
            upgrade_extra_args=dict(type="str", default=""),
            update_cache=dict(
                type="bool",
                aliases=["update-cache"],
                deprecated_aliases=[
                    dict(
                        name="update-cache",
                        version="5.0.0",
                        collection_name="community.general",
                    )
                ],
            ),
            update_cache_extra_args=dict(type="str", default=""),
        ),
        required_one_of=[["name", "update_cache", "upgrade"]],
        mutually_exclusive=[["name", "upgrade"]],
        supports_check_mode=True,
    )

    # Split extra_args as the shell would for easier handling later
    for str_args in ["extra_args", "upgrade_extra_args", "update_cache_extra_args"]:
        module.params[str_args] = shlex.split(module.params[str_args])

    return module


def main():

    Pacman(setup_module()).run()


if __name__ == "__main__":
    main()
