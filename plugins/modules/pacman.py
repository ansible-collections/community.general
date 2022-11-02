#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Afterburn <https://github.com/afterburn>
# Copyright (c) 2013, Aaron Bull Schaefer <aaron@elasticdog.com>
# Copyright (c) 2015, Indrajit Raychaudhuri <irc+code@indrajit.com>
# Copyright (c) 2022, Jean Raby <jean@raby.sh>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
            - When removing packages, forcefully remove them, without any checks.
              Same as I(extra_args="--nodeps --nodeps").
              When combined with I(update_cache), force a refresh of all package databases.
              Same as I(update_cache_extra_args="--refresh --refresh").
        default: false
        type: bool

    remove_nosave:
        description:
            - When removing packages, do not save modified configuration files as C(.pacsave) files.
              (passes C(--nosave) to pacman)
        version_added: 4.6.0
        default: false
        type: bool

    executable:
        description:
            - Path of the binary to use. This can either be C(pacman) or a pacman compatible AUR helper.
            - Pacman compatibility is unfortunately ill defined, in particular, this modules makes
              extensive use of the C(--print-format) directive which is known not to be implemented by
              some AUR helpers (notably, C(yay)).
            - Beware that AUR helpers might behave unexpectedly and are therefore not recommended.
        default: pacman
        type: str
        version_added: 3.1.0

    extra_args:
        description:
            - Additional option to pass to pacman when enforcing C(state).
        default: ''
        type: str

    update_cache:
        description:
            - Whether or not to refresh the master package lists.
            - This can be run as part of a package installation or as a separate step.
            - If not specified, it defaults to C(false).
            - Please note that this option only had an influence on the module's C(changed) state
              if I(name) and I(upgrade) are not specified before community.general 5.0.0.
              See the examples for how to keep the old behavior.
        type: bool

    update_cache_extra_args:
        description:
            - Additional option to pass to pacman when enforcing C(update_cache).
        default: ''
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
        default: ''
        type: str

    reason:
        description:
            - The install reason to set for the packages.
        choices: [ dependency, explicit ]
        type: str
        version_added: 5.4.0

    reason_for:
        description:
            - Set the install reason for C(all) packages or only for C(new) packages.
            - In case of I(state=latest) already installed packages which will be updated to a newer version are not counted as C(new).
        default: new
        choices: [ all, new ]
        type: str
        version_added: 5.4.0

notes:
  - When used with a C(loop:) each package will be processed individually,
    it is much more efficient to pass the list directly to the I(name) option.
  - To use an AUR helper (I(executable) option), a few extra setup steps might be required beforehand.
    For example, a dedicated build user with permissions to install packages could be necessary.
"""

RETURN = """
packages:
    description:
        - A list of packages that have been changed.
        - Before community.general 4.5.0 this was only returned when I(upgrade=true).
          In community.general 4.5.0, it was sometimes omitted when the package list is empty,
          but since community.general 4.6.0 it is always returned when I(name) is specified or
          I(upgrade=true).
    returned: success and I(name) is specified or I(upgrade=true)
    type: list
    elements: str
    sample: [ package, other-package ]

cache_updated:
    description:
        - The changed status of C(pacman -Sy).
        - Useful when I(name) or I(upgrade=true) are specified next to I(update_cache=true).
    returned: success, when I(update_cache=true)
    type: bool
    sample: false
    version_added: 4.6.0

stdout:
    description:
        - Output from pacman.
    returned: success, when needed
    type: str
    sample: ":: Synchronizing package databases...  core is up to date :: Starting full system upgrade..."
    version_added: 4.1.0

stderr:
    description:
        - Error output from pacman.
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
  # The 'changed' state of this call will indicate whether the cache was
  # updated *or* whether foo was installed/upgraded.
  community.general.pacman:
    name: foo
    state: latest
    update_cache: true

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
    update_cache: true

- name: Run the equivalent of "pacman -Su" as a separate step
  community.general.pacman:
    upgrade: true

- name: Run the equivalent of "pacman -Syu" as a separate step
  # Since community.general 5.0.0 the 'changed' state of this call
  # will be 'true' in case the cache was updated, or when a package
  # was updated.
  #
  # The previous behavior was to only indicate whether something was
  # upgraded. To keep the old behavior, add the following to the task:
  #
  #   register: result
  #   changed_when: result.packages | length > 0
  community.general.pacman:
    update_cache: true
    upgrade: true

- name: Run the equivalent of "pacman -Rdd", force remove package baz
  community.general.pacman:
    name: baz
    state: absent
    force: true

- name: Install foo as dependency and leave reason untouched if already installed
  community.general.pacman:
    name: foo
    state: present
    reason: dependency
    reason_for: new

- name: Run the equivalent of "pacman -S --asexplicit", mark foo as explicit and install it if not present
  community.general.pacman:
    name: foo
    state: present
    reason: explicit
    reason_for: all
"""

import shlex
from ansible.module_utils.basic import AnsibleModule
from collections import defaultdict, namedtuple


class Package(object):
    def __init__(self, name, source, source_is_URL=False):
        self.name = name
        self.source = source
        self.source_is_URL = source_is_URL

    def __eq__(self, o):
        return self.name == o.name and self.source == o.source and self.source_is_URL == o.source_is_URL

    def __lt__(self, o):
        return self.name < o.name

    def __repr__(self):
        return 'Package("%s", "%s", %s)' % (self.name, self.source, self.source_is_URL)


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

        self._cached_database = None

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
        pkgs_to_install_from_url = []
        pkgs_to_set_reason = []
        for p in pkgs:
            if self.m.params["reason"] and (
                p.name not in self.inventory["pkg_reasons"]
                or self.m.params["reason_for"] == "all"
                and self.inventory["pkg_reasons"][p.name] != self.m.params["reason"]
            ):
                pkgs_to_set_reason.append(p.name)
            if p.source_is_URL:
                # URL packages bypass the latest / upgradable_pkgs test
                # They go through the dry-run to let pacman decide if they will be installed
                pkgs_to_install_from_url.append(p)
                continue
            if (
                p.name not in self.inventory["installed_pkgs"]
                or self.target_state == "latest"
                and p.name in self.inventory["upgradable_pkgs"]
            ):
                pkgs_to_install.append(p)

        if len(pkgs_to_install) == 0 and len(pkgs_to_install_from_url) == 0 and len(pkgs_to_set_reason) == 0:
            self.exit_params["packages"] = []
            self.add_exit_infos("package(s) already installed")
            return

        cmd_base = [
            self.pacman_path,
            "--noconfirm",
            "--noprogressbar",
            "--needed",
        ]
        if self.m.params["extra_args"]:
            cmd_base.extend(self.m.params["extra_args"])

        def _build_install_diff(pacman_verb, pkglist):
            # Dry run to build the installation diff

            cmd = cmd_base + [pacman_verb, "--print-format", "%n %v"] + [p.source for p in pkglist]
            rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
            if rc != 0:
                self.fail("Failed to list package(s) to install", cmd=cmd, stdout=stdout, stderr=stderr)

            name_ver = [l.strip() for l in stdout.splitlines()]
            before = []
            after = []
            to_be_installed = []
            for p in name_ver:
                # With Pacman v6.0.1 - libalpm v13.0.1, --upgrade outputs "loading packages..." on stdout. strip that.
                # When installing from URLs, pacman can also output a 'nothing to do' message. strip that too.
                if "loading packages" in p or "there is nothing to do" in p:
                    continue
                name, version = p.split()
                if name in self.inventory["installed_pkgs"]:
                    before.append("%s-%s-%s" % (name, self.inventory["installed_pkgs"][name], self.inventory["pkg_reasons"][name]))
                if name in pkgs_to_set_reason:
                    after.append("%s-%s-%s" % (name, version, self.m.params["reason"]))
                elif name in self.inventory["pkg_reasons"]:
                    after.append("%s-%s-%s" % (name, version, self.inventory["pkg_reasons"][name]))
                else:
                    after.append("%s-%s" % (name, version))
                to_be_installed.append(name)

            return (to_be_installed, before, after)

        before = []
        after = []
        installed_pkgs = []

        if pkgs_to_install:
            p, b, a = _build_install_diff("--sync", pkgs_to_install)
            installed_pkgs.extend(p)
            before.extend(b)
            after.extend(a)
        if pkgs_to_install_from_url:
            p, b, a = _build_install_diff("--upgrade", pkgs_to_install_from_url)
            installed_pkgs.extend(p)
            before.extend(b)
            after.extend(a)

        if len(installed_pkgs) == 0 and len(pkgs_to_set_reason) == 0:
            # This can happen with URL packages if pacman decides there's nothing to do
            self.exit_params["packages"] = []
            self.add_exit_infos("package(s) already installed")
            return

        self.changed = True

        self.exit_params["diff"] = {
            "before": "\n".join(sorted(before)) + "\n" if before else "",
            "after": "\n".join(sorted(after)) + "\n" if after else "",
        }

        changed_reason_pkgs = [p for p in pkgs_to_set_reason if p not in installed_pkgs]

        if self.m.check_mode:
            self.add_exit_infos("Would have installed %d packages" % (len(installed_pkgs) + len(changed_reason_pkgs)))
            self.exit_params["packages"] = sorted(installed_pkgs + changed_reason_pkgs)
            return

        # actually do it
        def _install_packages_for_real(pacman_verb, pkglist):
            cmd = cmd_base + [pacman_verb] + [p.source for p in pkglist]
            rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
            if rc != 0:
                self.fail("Failed to install package(s)", cmd=cmd, stdout=stdout, stderr=stderr)
            self.add_exit_infos(stdout=stdout, stderr=stderr)
            self._invalidate_database()

        if pkgs_to_install:
            _install_packages_for_real("--sync", pkgs_to_install)
        if pkgs_to_install_from_url:
            _install_packages_for_real("--upgrade", pkgs_to_install_from_url)

        # set reason
        if pkgs_to_set_reason:
            cmd = [self.pacman_path, "--noconfirm", "--database"]
            if self.m.params["reason"] == "dependency":
                cmd.append("--asdeps")
            else:
                cmd.append("--asexplicit")
            cmd.extend(pkgs_to_set_reason)

            rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
            if rc != 0:
                self.fail("Failed to install package(s)", cmd=cmd, stdout=stdout, stderr=stderr)
            self.add_exit_infos(stdout=stdout, stderr=stderr)

        self.exit_params["packages"] = sorted(installed_pkgs + changed_reason_pkgs)
        self.add_exit_infos("Installed %d package(s)" % (len(installed_pkgs) + len(changed_reason_pkgs)))

    def remove_packages(self, pkgs):
        # filter out pkgs that are already absent
        pkg_names_to_remove = [p.name for p in pkgs if p.name in self.inventory["installed_pkgs"]]

        if len(pkg_names_to_remove) == 0:
            self.exit_params["packages"] = []
            self.add_exit_infos("package(s) already absent")
            return

        # There's something to do, set this in advance
        self.changed = True

        cmd_base = [self.pacman_path, "--remove", "--noconfirm", "--noprogressbar"]
        cmd_base += self.m.params["extra_args"]
        cmd_base += ["--nodeps", "--nodeps"] if self.m.params["force"] else []
        # nosave_args conflicts with --print-format. Added later.
        # https://github.com/ansible-collections/community.general/issues/4315

        # This is a bit of a TOCTOU but it is better than parsing the output of
        # pacman -R, which is different depending on the user config (VerbosePkgLists)
        # Start by gathering what would be removed
        cmd = cmd_base + ["--print-format", "%n-%v"] + pkg_names_to_remove

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("failed to list package(s) to remove", cmd=cmd, stdout=stdout, stderr=stderr)

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

        nosave_args = ["--nosave"] if self.m.params["remove_nosave"] else []
        cmd = cmd_base + nosave_args + pkg_names_to_remove

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        if rc != 0:
            self.fail("failed to remove package(s)", cmd=cmd, stdout=stdout, stderr=stderr)
        self._invalidate_database()
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
                "--sysupgrade",
                "--quiet",
                "--noconfirm",
            ]
            if self.m.params["upgrade_extra_args"]:
                cmd += self.m.params["upgrade_extra_args"]
            rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
            self._invalidate_database()
            if rc == 0:
                self.add_exit_infos("System upgraded", stdout=stdout, stderr=stderr)
            else:
                self.fail("Could not upgrade", cmd=cmd, stdout=stdout, stderr=stderr)

    def _list_database(self):
        """runs pacman --sync --list with some caching"""
        if self._cached_database is None:
            dummy, packages, dummy = self.m.run_command([self.pacman_path, '--sync', '--list'], check_rc=True)
            self._cached_database = packages.splitlines()
        return self._cached_database

    def _invalidate_database(self):
        """invalidates the pacman --sync --list cache"""
        self._cached_database = None

    def update_package_db(self):
        """runs pacman --sync --refresh"""
        if self.m.check_mode:
            self.add_exit_infos("Would have updated the package db")
            self.changed = True
            self.exit_params["cache_updated"] = True
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
        else:
            # Dump package database to get contents before update
            pre_state = sorted(self._list_database())

        rc, stdout, stderr = self.m.run_command(cmd, check_rc=False)
        self._invalidate_database()

        if self.m.params["force"]:
            # Always changed when force=true
            self.exit_params["cache_updated"] = True
        else:
            # Dump package database to get contents after update
            post_state = sorted(self._list_database())
            # If contents changed, set changed=true
            self.exit_params["cache_updated"] = pre_state != post_state
        if self.exit_params["cache_updated"]:
            self.changed = True

        if rc == 0:
            self.add_exit_infos("Updated package db", stdout=stdout, stderr=stderr)
        else:
            self.fail("could not update package db", cmd=cmd, stdout=stdout, stderr=stderr)

    def package_list(self):
        """Takes the input package list and resolves packages groups to their package list using the inventory,
        extracts package names from packages given as files or URLs using calls to pacman

        Returns the expanded/resolved list as a list of Package
        """
        pkg_list = []
        for pkg in self.m.params["name"]:
            if not pkg:
                continue

            is_URL = False
            if pkg in self.inventory["available_groups"]:
                # Expand group members
                for group_member in self.inventory["available_groups"][pkg]:
                    pkg_list.append(Package(name=group_member, source=group_member))
            elif pkg in self.inventory["available_pkgs"] or pkg in self.inventory["installed_pkgs"]:
                # Just a regular pkg, either available in the repositories,
                # or locally installed, which we need to know for absent state
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
                    # With Pacman v6.0.1 - libalpm v13.0.1, --upgrade outputs " filename_without_extension downloading..." if the URL is unseen.
                    # In all cases, pacman outputs "loading packages..." on stdout. strip both
                    stdout = stdout.splitlines()[-1]
                    is_URL = True
                pkg_name = stdout.strip()
                pkg_list.append(Package(name=pkg_name, source=pkg, source_is_URL=is_URL))

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
            "pkg_reasons": {pkgname: reason},
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
            [self.pacman_path, "--query", "--groups"], check_rc=True
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
        database = self._list_database()
        # Format of a line: "core pacman 6.0.1-2"
        for l in database:
            l = l.strip()
            if not l:
                continue
            repo, pkg, ver = l.split()[:3]
            available_pkgs[pkg] = ver

        available_groups = defaultdict(set)
        dummy, stdout, dummy = self.m.run_command(
            [self.pacman_path, "--sync", "--groups", "--groups"], check_rc=True
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

        pkg_reasons = {}
        dummy, stdout, dummy = self.m.run_command([self.pacman_path, "--query", "--explicit"], check_rc=True)
        # Format of a line: "pacman 6.0.1-2"
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            pkg = l.split()[0]
            pkg_reasons[pkg] = "explicit"
        dummy, stdout, dummy = self.m.run_command([self.pacman_path, "--query", "--deps"], check_rc=True)
        # Format of a line: "pacman 6.0.1-2"
        for l in stdout.splitlines():
            l = l.strip()
            if not l:
                continue
            pkg = l.split()[0]
            pkg_reasons[pkg] = "dependency"

        return dict(
            installed_pkgs=installed_pkgs,
            installed_groups=installed_groups,
            available_pkgs=available_pkgs,
            available_groups=available_groups,
            upgradable_pkgs=upgradable_pkgs,
            pkg_reasons=pkg_reasons,
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
            remove_nosave=dict(type="bool", default=False),
            executable=dict(type="str", default="pacman"),
            extra_args=dict(type="str", default=""),
            upgrade=dict(type="bool"),
            upgrade_extra_args=dict(type="str", default=""),
            update_cache=dict(type="bool"),
            update_cache_extra_args=dict(type="str", default=""),
            reason=dict(type="str", choices=["explicit", "dependency"]),
            reason_for=dict(type="str", default="new", choices=["new", "all"]),
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
