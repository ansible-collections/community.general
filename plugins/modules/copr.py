#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Silvie Chlupova <schlupov@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: copr
short_description: Manage one of the Copr repositories
version_added: 2.0.0
description: This module can enable, disable or remove the specified repository.
author: Silvie Chlupova (@schlupov) <schlupov@redhat.com>
requirements:
  - dnf
  - dnf-plugins-core
notes:
  - Supports C(check_mode).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  host:
    description: The Copr host to work with.
    default: copr.fedorainfracloud.org
    type: str
  protocol:
    description: This indicate which protocol to use with the host.
    default: https
    type: str
  name:
    description: Copr directory name, for example C(@copr/copr-dev).
    required: true
    type: str
  state:
    description:
      - Whether to set this project as V(enabled), V(disabled), or V(absent).
    default: enabled
    type: str
    choices: [absent, enabled, disabled]
  chroot:
    description:
      - The name of the chroot that you want to enable/disable/remove in the project, for example V(epel-7-x86_64). Default
        chroot is determined by the operating system, version of the operating system, and architecture on which the module
        is run.
    type: str
  includepkgs:
    description: List of packages to include.
    required: false
    type: list
    elements: str
    version_added: 9.4.0
  excludepkgs:
    description: List of packages to exclude.
    required: false
    type: list
    elements: str
    version_added: 9.4.0
"""

EXAMPLES = r"""
- name: Enable project Test of the user schlupov
  community.general.copr:
    host: copr.fedorainfracloud.org
    state: enabled
    name: schlupov/Test
    chroot: fedora-31-x86_64

- name: Remove project integration_tests of the group copr
  community.general.copr:
    state: absent
    name: '@copr/integration_tests'

- name: Install Caddy
  community.general.copr:
    name: '@caddy/caddy'
    chroot: fedora-rawhide-{{ ansible_facts.architecture }}
    includepkgs:
      - caddy
"""

RETURN = r"""
repo_filename:
  description: The name of the repo file in which the copr project information is stored.
  returned: success
  type: str
  sample: _copr:copr.fedorainfracloud.org:group_copr:integration_tests.repo

repo:
  description: Path to the project on the host.
  returned: success
  type: str
  sample: copr.fedorainfracloud.org/group_copr/integration_tests
"""

import stat
import os
import traceback

try:
    import dnf
    import dnf.cli
    import dnf.repodict
    from dnf.conf import Conf
    HAS_DNF_PACKAGES = True
    DNF_IMP_ERR = None
except ImportError:
    DNF_IMP_ERR = traceback.format_exc()
    HAS_DNF_PACKAGES = False

from ansible.module_utils.common import respawn
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils import distro
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url


def _respawn_dnf():
    if respawn.has_respawned():
        return
    system_interpreters = (
        "/usr/libexec/platform-python",
        "/usr/bin/python3",
        "/usr/bin/python2",
        "/usr/bin/python",
    )
    interpreter = respawn.probe_interpreters_for_module(system_interpreters, "dnf")
    if interpreter:
        respawn.respawn_module(interpreter)


class CoprModule(object):
    """The class represents a copr module.

    The class contains methods that take care of the repository state of a project,
    whether the project is enabled, disabled or missing.
    """

    ansible_module = None

    def __init__(self, host, name, state, protocol, chroot=None, check_mode=False):
        self.host = host
        self.name = name
        self.state = state
        self.chroot = chroot
        self.protocol = protocol
        self.check_mode = check_mode
        if not chroot:
            self.chroot = self.chroot_conf()
        else:
            self.chroot = chroot
            self.get_base()

    @property
    def short_chroot(self):
        """str: Chroot (distribution-version-architecture) shorten to distribution-version."""
        return self.chroot.rsplit('-', 1)[0]

    @property
    def arch(self):
        """str: Target architecture."""
        chroot_parts = self.chroot.split("-")
        return chroot_parts[-1]

    @property
    def user(self):
        """str: Copr user (this can also be the name of the group)."""
        return self._sanitize_username(self.name.split("/")[0])

    @property
    def project(self):
        """str: The name of the copr project."""
        return self.name.split("/")[1]

    @classmethod
    def need_root(cls):
        """Check if the module was run as root."""
        if os.geteuid() != 0:
            cls.raise_exception("This command has to be run under the root user.")

    @classmethod
    def get_base(cls):
        """Initialize the configuration from dnf.

        Returns:
            An instance of the BaseCli class.
        """
        cls.base = dnf.cli.cli.BaseCli(Conf())
        return cls.base

    @classmethod
    def raise_exception(cls, msg):
        """Raise either an ansible exception or a python exception.

        Args:
            msg: The message to be displayed when an exception is thrown.
        """
        if cls.ansible_module:
            raise cls.ansible_module.fail_json(msg=msg, changed=False)
        raise Exception(msg)

    def _get(self, chroot):
        """Send a get request to the server to obtain the necessary data.

        Args:
            chroot: Chroot in the form of distribution-version.

        Returns:
            Info about a repository and status code of the get request.
        """
        repo_info = None
        url = "{0}://{1}/coprs/{2}/repo/{3}/dnf.repo?arch={4}".format(
            self.protocol, self.host, self.name, chroot, self.arch
        )
        try:
            r = open_url(url)
            status_code = r.getcode()
            repo_info = r.read().decode("utf-8")
        except HTTPError as e:
            status_code = e.getcode()
        return repo_info, status_code

    def _download_repo_info(self):
        """Download information about the repository.

        Returns:
            Information about the repository.
        """
        distribution, version = self.short_chroot.split('-', 1)
        chroot = self.short_chroot
        while True:
            repo_info, status_code = self._get(chroot)
            if repo_info:
                return repo_info
            if distribution == "rhel":
                chroot = "centos-stream-8"
                distribution = "centos"
            elif distribution == "centos":
                if version == "stream-8":
                    version = "8"
                elif version == "stream-9":
                    version = "9"
                chroot = "epel-{0}".format(version)
                distribution = "epel"
            else:
                if str(status_code) != "404":
                    self.raise_exception(
                        "This repository does not have any builds yet so you cannot enable it now."
                    )
                else:
                    self.raise_exception(
                        "Chroot {0} does not exist in {1}".format(self.chroot, self.name)
                    )

    def _enable_repo(self, repo_filename_path, repo_content=None):
        """Write information to a repo file.

        Args:
            repo_filename_path: Path to repository.
            repo_content: Repository information from the host.

        Returns:
            True, if the information in the repo file matches that stored on the host,
            False otherwise.
        """
        if not repo_content:
            repo_content = self._download_repo_info()
        if self.ansible_module.params["includepkgs"]:
            includepkgs_value = ','.join(self.ansible_module.params['includepkgs'])
            repo_content = repo_content.rstrip('\n') + '\nincludepkgs={0}\n'.format(includepkgs_value)
        if self.ansible_module.params["excludepkgs"]:
            excludepkgs_value = ','.join(self.ansible_module.params['excludepkgs'])
            repo_content = repo_content.rstrip('\n') + '\nexcludepkgs={0}\n'.format(excludepkgs_value)
        if self._compare_repo_content(repo_filename_path, repo_content):
            return False
        if not self.check_mode:
            with open(repo_filename_path, "w+") as file:
                file.write(repo_content)
            os.chmod(
                repo_filename_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
            )
        return True

    def _get_repo_with_old_id(self):
        """Try to get a repository with the old name."""
        repo_id = "{0}-{1}".format(self.user, self.project)
        if repo_id in self.base.repos and "_copr" in self.base.repos[repo_id].repofile:
            file_name = self.base.repos[repo_id].repofile.split("/")[-1]
            try:
                copr_hostname = file_name.rsplit(":", 2)[0].split(":", 1)[1]
                if copr_hostname != self.host:
                    return None
                return file_name
            except IndexError:
                return file_name
        return None

    def _read_all_repos(self, repo_id=None):
        """The method is used to initialize the base variable by
        repositories using the RepoReader class from dnf.

        Args:
            repo_id: Repo id of the repository we want to work with.
        """
        reader = dnf.conf.read.RepoReader(self.base.conf, None)
        for repo in reader:
            try:
                if repo_id:
                    if repo.id == repo_id:
                        self.base.repos.add(repo)
                        break
                else:
                    self.base.repos.add(repo)
            except dnf.exceptions.ConfigError as e:
                self.raise_exception(str(e))

    def _get_copr_repo(self):
        """Return one specific repository from all repositories on the system.

        Returns:
            The repository that a user wants to enable, disable, or remove.
        """
        repo_id = "copr:{0}:{1}:{2}".format(self.host, self.user, self.project)
        if repo_id not in self.base.repos:
            if self._get_repo_with_old_id() is None:
                return None
        return self.base.repos[repo_id]

    def _disable_repo(self, repo_filename_path):
        """Disable the repository.

        Args:
            repo_filename_path: Path to repository.

        Returns:
            False, if the repository is already disabled on the system,
            True otherwise.
        """
        self._read_all_repos()
        repo = self._get_copr_repo()
        if repo is None:
            if self.check_mode:
                return True
            self._enable_repo(repo_filename_path)
            self._read_all_repos("copr:{0}:{1}:{2}".format(self.host, self.user, self.project))
            repo = self._get_copr_repo()
        for repo_id in repo.cfg.sections():
            repo_content_api = self._download_repo_info()
            with open(repo_filename_path, "r") as file:
                repo_content_file = file.read()
            if repo_content_file != repo_content_api:
                if not self.resolve_differences(
                    repo_content_file, repo_content_api, repo_filename_path
                ):
                    return False
            if not self.check_mode:
                self.base.conf.write_raw_configfile(
                    repo.repofile, repo_id, self.base.conf.substitutions, {"enabled": "0"},
                )
        return True

    def resolve_differences(self, repo_content_file, repo_content_api, repo_filename_path):
        """Detect differences between the contents of the repository stored on the
        system and the information about the repository on the server.

        Args:
            repo_content_file: The contents of the repository stored on the system.
            repo_content_api: The information about the repository from the server.
            repo_filename_path: Path to repository.

        Returns:
            False, if the contents of the repo file and the information on the server match,
            True otherwise.
        """
        repo_file_lines = repo_content_file.split("\n")
        repo_api_lines = repo_content_api.split("\n")
        repo_api_lines.remove("enabled=1")
        if "enabled=0" in repo_file_lines:
            repo_file_lines.remove("enabled=0")
            if " ".join(repo_api_lines) == " ".join(repo_file_lines):
                return False
            if not self.check_mode:
                os.remove(repo_filename_path)
                self._enable_repo(repo_filename_path, repo_content_api)
        else:
            repo_file_lines.remove("enabled=1")
            if " ".join(repo_api_lines) != " ".join(repo_file_lines):
                if not self.check_mode:
                    os.remove(repo_filename_path)
                    self._enable_repo(repo_filename_path, repo_content_api)
        return True

    def _remove_repo(self):
        """Remove the required repository.

        Returns:
            True, if the repository has been removed, False otherwise.
        """
        self._read_all_repos()
        repo = self._get_copr_repo()
        if not repo:
            return False
        if not self.check_mode:
            try:
                os.remove(repo.repofile)
            except OSError as e:
                self.raise_exception(str(e))
        return True

    def run(self):
        """The method uses methods of the CoprModule class to change the state of the repository.

        Returns:
            Dictionary with information that the ansible module displays to the user at the end of the run.
        """
        self.need_root()
        state = dict()
        repo_filename = "_copr:{0}:{1}:{2}.repo".format(self.host, self.user, self.project)
        state["repo"] = "{0}/{1}/{2}".format(self.host, self.user, self.project)
        state["repo_filename"] = repo_filename
        repo_filename_path = "{0}/_copr:{1}:{2}:{3}.repo".format(
            self.base.conf.get_reposdir, self.host, self.user, self.project
        )
        if self.state == "enabled":
            enabled = self._enable_repo(repo_filename_path)
            state["msg"] = "enabled"
            state["state"] = bool(enabled)
        elif self.state == "disabled":
            disabled = self._disable_repo(repo_filename_path)
            state["msg"] = "disabled"
            state["state"] = bool(disabled)
        elif self.state == "absent":
            removed = self._remove_repo()
            state["msg"] = "absent"
            state["state"] = bool(removed)
        return state

    @staticmethod
    def _compare_repo_content(repo_filename_path, repo_content_api):
        """Compare the contents of the stored repository with the information from the server.

        Args:
            repo_filename_path: Path to repository.
            repo_content_api: The information about the repository from the server.

        Returns:
            True, if the information matches, False otherwise.
        """
        if not os.path.isfile(repo_filename_path):
            return False
        with open(repo_filename_path, "r") as file:
            repo_content_file = file.read()
        return repo_content_file == repo_content_api

    @staticmethod
    def chroot_conf():
        """Obtain information about the distribution, version, and architecture of the target.

        Returns:
            Chroot info in the form of distribution-version-architecture.
        """
        (distribution, version, codename) = distro.linux_distribution(full_distribution_name=False)
        base = CoprModule.get_base()
        return "{0}-{1}-{2}".format(distribution, version, base.conf.arch)

    @staticmethod
    def _sanitize_username(user):
        """Modify the group name.

        Args:
            user: User name.

        Returns:
            Modified user name if it is a group name with @.
        """
        if user[0] == "@":
            return "group_{0}".format(user[1:])
        return user


def run_module():
    """The function takes care of the functioning of the whole ansible copr module."""
    module_args = dict(
        host=dict(type="str", default="copr.fedorainfracloud.org"),
        protocol=dict(type="str", default="https"),
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["enabled", "disabled", "absent"], default="enabled"),
        chroot=dict(type="str"),
        includepkgs=dict(type='list', elements="str", required=False),
        excludepkgs=dict(type='list', elements="str", required=False),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    params = module.params

    if not HAS_DNF_PACKAGES:
        _respawn_dnf()
        module.fail_json(msg=missing_required_lib("dnf"), exception=DNF_IMP_ERR)

    CoprModule.ansible_module = module
    copr_module = CoprModule(
        host=params["host"],
        name=params["name"],
        state=params["state"],
        protocol=params["protocol"],
        chroot=params["chroot"],
        check_mode=module.check_mode,
    )
    state = copr_module.run()

    info = "Please note that this repository is not part of the main distribution"

    if params["state"] == "enabled" and state["state"]:
        module.exit_json(
            changed=state["state"],
            msg=state["msg"],
            repo=state["repo"],
            repo_filename=state["repo_filename"],
            info=info,
        )
    module.exit_json(
        changed=state["state"],
        msg=state["msg"],
        repo=state["repo"],
        repo_filename=state["repo_filename"],
    )


def main():
    """Launches ansible Copr module."""
    run_module()


if __name__ == "__main__":
    main()
