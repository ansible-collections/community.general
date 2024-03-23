#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Radek Sprta <mail@radeksprta.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cargo
short_description: Manage Rust packages with cargo
version_added: 4.3.0
description:
  - Manage Rust packages with cargo.
author: "Radek Sprta (@radek-sprta)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  executable:
    description:
      - Path to the C(cargo) installed in the system.
      - If not specified, the module will look C(cargo) in E(PATH).
    type: path
    version_added: 7.5.0
  name:
    description:
      - The name of a Rust package to install.
    type: list
    elements: str
    required: true
  path:
    description:
      ->
      The base path where to install the Rust packages. Cargo automatically appends
      V(/bin). In other words, V(/usr/local) will become V(/usr/local/bin).
    type: path
  version:
    description:
      ->
      The version to install. If O(name) contains multiple values, the module will
      try to install all of them in this version.
    type: str
    required: false
  locked:
    description:
      - Install with locked dependencies.
      - This is only used when installing packages.
    required: false
    type: bool
    default: false
    version_added: 7.5.0
  force:
    description:
      - Forcefully install package(s).
      - Ignores many checks, and updates/installs forcefully.
    type: bool
    default: false
    required: false
    version_added: 8.4.0
  state:
    description:
      - The state of the Rust package.
    required: false
    type: str
    default: present
    choices: [ "present", "absent", "latest" ]
  features:
    description:
      - List of features to enable for the package.
      - If O(name) contains multiple values, the module will try to install all
        of them with these same features.
    type: list
    elements: str
    required: false
    default: []
    version_added: 8.4.0
  all_features:
    description:
      - Enable all features for a package.
      - If O(name) has multiple values, for each package all of their features
        would be enabled.
    type: bool
    default: false
    required: false
    version_added: 8.4.0
  directory:
    description:
      - Path to install the package(s) from.
    type: path
    required: false
    version_added: 8.4.0
  registry:
    description:
      - Registry to install the package(s) from.
    type: str
    required: false
    version_added: 8.4.0
  git:
    description:
      - Git URL to install the package(s) from.
      - Can optionally either be used with O(branch), O(tag) or O(rev).
    type: str
    required: false
    version_added: 8.4.0
  branch:
    description:
      - Git branch to install the package(s) from.
      - C(git) option must be specified.
    type: str
    required: false
    version_added: 8.4.0
  tag:
    description:
      - Git tag to install the package(s) from.
      - C(git) option must be specified.
    type: str
    required: false
    version_added: 8.4.0
  rev:
    description:
      - Git commit to install the package(s) from.
      - C(git) option must be specified.
    type: str
    required: false
    version_added: 8.4.0
  debug:
    description:
      - Specify whether to install package(s) in debug mode.
    type: bool
    default: false
    required: false
    version_added: 8.4.0
requirements:
    - cargo and git installed
    - optionally, toml or tomli library present, if Python version is less than 3.11 and TOML support is needed
"""

EXAMPLES = r"""
- name: Install "ludusavi" Rust package
  community.general.cargo:
    name: ludusavi

- name: Install "ludusavi" Rust package with locked dependencies
  community.general.cargo:
    name: ludusavi
    locked: true

- name: Install "ludusavi" Rust package in version 0.10.0
  community.general.cargo:
    name: ludusavi
    version: '0.10.0'

- name: Install "ludusavi" Rust package to global location
  community.general.cargo:
    name: ludusavi
    path: /usr/local

- name: Remove "ludusavi" Rust package
  community.general.cargo:
    name: ludusavi
    state: absent

- name: Update "ludusavi" Rust package its latest version
  community.general.cargo:
    name: ludusavi
    state: latest
"""

import os
import re
import json
from collections import deque

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlsplit, parse_qs
from ansible.module_utils.urls import fetch_url

# From : https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory/toml.py
HAS_TOMLI = False
try:
    import tomllib as toml

    HAS_TOMLI = True
except ImportError:
    try:
        import tomli as toml

        HAS_TOMLI = True
    except ImportError:
        pass

HAS_TOML = False
if not HAS_TOMLI:
    try:
        import toml

        HAS_TOML = True
    except ImportError:
        pass

NAME_REGEX = re.compile(r"([^\s]+) ([^\s]+) \(([^\s]+)\)")


class Cargo(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.executable = [kwargs["executable"] or module.get_bin_path("cargo", True)]
        self.name = kwargs["name"]
        self.path = kwargs["path"]
        self.state = kwargs["state"]
        self.version = kwargs["version"]
        self.locked = kwargs["locked"]
        self.features = kwargs["features"]
        self.all_features = kwargs["all_features"]
        self.force = kwargs["force"]
        self.directory = kwargs["directory"]
        self.registry = kwargs["registry"]
        self.git = kwargs["git"]
        self.branch = kwargs["branch"]
        self.tag = kwargs["tag"]
        self.rev = kwargs["rev"]
        self.debug = kwargs["debug"]

        self.metadata = dict()
        self.cargo_dir = ""
        self.registry_url = None
        self.metadata_cached = False

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if path is not None and not os.path.isdir(path):
            self.module.fail_json(msg="Path %s is not a directory" % path)
        self._path = path

    def _exec(
        self, args, run_in_check_mode=False, check_rc=True, add_package_name=True
    ):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = self.executable + args
            dummy, out, err = self.module.run_command(cmd, check_rc=check_rc)
            return out, err
        return "", ""

    def cache_metadata(self):
        if self.metadata_cached:
            return

        self.cargo_dir = (
            self.path
            or os.getenv("CARGO_HOME")
            or os.path.join(os.path.expanduser("~"), ".cargo")
        )
        if self.cargo_dir is None:
            self.module.fail_json(
                msg="Cannot detect cargo home directory, set CARGO_HOME environment variable explicitly"
            )

        crates_json = os.path.join(self.cargo_dir, ".crates2.json")
        if not os.path.isfile(crates_json):
            # On first install, might not be present, so return gracefully
            return

        with open(crates_json, "r") as f:
            all_installed_info = json.load(f)["installs"]

        for key, value in all_installed_info.items():
            dummy, name, version, url, dummy = NAME_REGEX.split(key)
            parsed_url = urlsplit(url)
            scheme = parsed_url.scheme.split("+")

            if scheme[0] == "git":
                self.metadata[name] = {
                    "git": "%s://%s%s"
                    % (scheme[-1], parsed_url.netloc, parsed_url.path),
                    "rev": parsed_url.fragment,
                    "branch": None,
                    "tag": None,
                    "feat": value["features"],
                    "allf": value["all_features"],
                    "prof": value["profile"],
                    "scm": scheme[0],
                }
                if parsed_url.query != "":
                    for k, v in parse_qs(parsed_url.query).items():
                        self.metadata[name][k] = v[0]
            elif scheme[0] == "path":
                self.metadata[name] = {
                    "path": parsed_url.path,
                    "feat": value["features"],
                    "allf": value["all_features"],
                    "prof": value["profile"],
                    "scm": scheme[0],
                }
            else:
                registry_url = "%s://%s%s" % (
                    scheme[-1],
                    parsed_url.netloc,
                    parsed_url.path,
                )
                is_sparse = False
                if "sparse" in scheme:
                    registry_url = "sparse+%s" % (registry_url)
                    is_sparse = True
                self.metadata[name] = {
                    "ver": version,
                    "reg": registry_url,
                    "feat": value["features"],
                    "allf": value["all_features"],
                    "prof": value["profile"],
                    "scm": "registry" if is_sparse else "sparse",
                }
        self.metadata_cached = True

    def is_present(self, name):
        if not self.metadata_cached:
            self.cache_metadata()

        version = self.version
        if "@" in name:
            name, version = name.split("@")

        if name not in self.metadata:
            return False

        if self.state == "absent":
            return True

        metadata = self.metadata[name]

        if (
            self.all_features != metadata["allf"]
            or ("dev" if self.debug else "release") != metadata["prof"]
            or self.features != metadata["feat"]
        ):
            return False

        if self.directory is not None:
            return metadata["scm"] == "path" and self.directory == metadata["path"]

        if self.git is not None:
            self.git = self.git.split("+")[-1]
            return (
                metadata["scm"] == "git"
                and self.git == metadata["git"]
                and (self.rev is None or self.rev == metadata["rev"])
                and self.branch == metadata["branch"]
                and self.tag == metadata["tag"]
            )

        if version is not None and version != metadata["ver"]:
            return False

        DEFAULT_SPARSE = "sparse+https://index.crates.io"
        DEFAULT_GIT = "https://github.com/rust-lang/crates.io-index"

        if metadata["reg"] in [DEFAULT_SPARSE, DEFAULT_GIT]:
            metadata["reg"] = "default"

        if self.registry_url is not None:
            if self.registry_url == metadata["reg"] or (
                metadata["reg"] == "default"
                and self.registry_url in [DEFAULT_SPARSE, DEFAULT_GIT]
            ):
                return True
            return False

        if HAS_TOMLI or HAS_TOML:
            config = os.path.join(self.cargo_dir, "config.toml")
            if not os.path.isfile(config):
                toml_conf = {}
            else:
                read_mode = "rb" if HAS_TOMLI else "r"
                with open(config, read_mode) as f:
                    toml_conf = toml.load(f)

            self.registry = self.registry or toml_conf.get("registry", {}).get(
                "default", "crates-io"
            )

            is_default_sparse = (
                toml_conf.get("registries", {})
                .get("crates-io", {})
                .get("protocol", "sparse")
            ) == "sparse"

            reg_to_index = {
                k: v["index"]
                for k, v in toml_conf.get("registries", {}).items()
                if isinstance(v, dict) and v.get("index") is not None
            }

            reg_to_index["crates-io"] = "default"

            # NOTE: It is not clear what happens when under [source.<name>]
            # along with replace-with other options like directory, git,
            # registry, or local-registry is present simultaneously. I decided
            # that the source name should be resolved with "replace-with" first.
            replace = self.registry
            source = toml_conf.get("source", {})
            while source.get(replace, {}).get("replace-with") is not None:
                replace = source[replace]["replace-with"]

            self.registry = replace

            # NOTE: If the registry is not in [registries] in config.toml, then
            # the only other place it can be is in [source.<name>.registry]. Of
            # course, it can be in directory, local-registry, or git too. But,
            # I don't know how the registry url changes then, as I have never
            # used any local registry myself. In the meantime, if you want to
            # use any of these options, you have to set them in ansible script
            # manually.
            self.registry_url = reg_to_index.get(self.registry) or source.get(
                self.registry, {}
            ).get("registry")

            if self.registry_url == metadata["reg"]:
                if self.registry_url == "default":
                    self.registry_url = (
                        DEFAULT_SPARSE if is_default_sparse else DEFAULT_GIT
                    )
                return True

        return False

    def is_outdated(self, name):
        # NOTE: If features differed, or all_features had been different this time,
        # those differences would have been caught in is_present_exact. So, this
        # time, we have to check for only a subset.

        version = self.version
        if "@" in name:
            name, version = name.split("@")

        metadata = self.metadata[name]

        # HACK: Since we cannot ensure whether cargo install was ran with the
        # --locked option previously, I decided that we have to update the package
        # every time, regardless whether there is an update or not. This is
        # subject to change if we can decide it from .crates2.json someday.
        if self.locked:
            return True

        if metadata["scm"] == "path":
            return False

        # We have already checked whether the git urls match, or whether the
        # branches match, or tags, or revs, as mentioned in the script with one
        # installed. If self.rev matches, we have nothing to do. Otherwise, we
        # have to check whether they changed or not. We use the git ls-remote
        # command for that, and filter by branch if present, or by tags that is
        # present, as branch might get updated, and so can tag, but rev can
        # never change.
        if metadata["scm"] == "git":
            if self.rev is not None:
                return False

            filter_ls = "HEAD"
            if self.branch is not None:
                filter_ls = "refs/heads/%s" % self.branch
            if self.tag is not None:
                filter_ls = "refs/tags/v%s" % self.tag

            git_bin = self.module.get_bin_path("git", True)
            dummy, out, err = self.module.run_command(
                [git_bin, "ls-remote", self.git, filter_ls]
            )

            if err:
                self.module.fail_json(
                    "Failed to run git ls-remote %s %s" % (self.git, filter_ls)
                )

            new_rev = out[:40]
            return new_rev != metadata["rev"]

        # If the version installed is already equal to one mentioned, we don't
        # need to update
        if version is not None:
            return False

        # For this one, we just have to check whether the version in remote
        # index and local install are same. However, cargo search <name>
        # --registry <registry.name> --limit 1, doesn't update the local
        # registry, so, version in remote might still be different. There is
        # already an open issue in cargo (https://github.com/rust-lang/cargo/issues/11034)
        # about this. Until then, we can just fetch the the file from index for
        # the package if this is a sparse index. However, if it is a git index,
        # we have to manually fetch the index in local storage. That causes an
        # unintended system state, something that in my opinion shouldn't be
        # done. Moreover, since sparse index are faster and now the default, I
        # haven't taken care of the git index.
        latest_version = metadata["ver"]
        if metadata["scm"] == "sparse" and self.registry_url is not None:
            url = self.registry_url
            url = url[7:] if url.startswith("sparse+") else url
            url = url.rstrip("/")

            name_elems = []
            if len(name) < 3:
                name_elems = ["%s" % len(name), name]
            elif len(name) == 3:
                name_elems = ["%s" % len(name), name[0], name]
            else:
                name_elems = [name[0:2], name[2:4], name]

            url = "%s/%s" % (url, "/".join(name_elems))

            resp, info = fetch_url(self.module, url)
            if info["status"] == 200:
                latest_version = json.loads(deque(resp, 1)[0])["vers"]
            return metadata["ver"] != latest_version

        cmd = ["search", name, "--registry", self.registry, "--limit", "1"]
        data, err = self._exec(cmd, True, False, False)

        match = re.search(r'"(.+)"', data)
        if match:
            latest_version = match.group(1)

        return metadata["ver"] != latest_version

    def install(self, packages=None):
        cmd = ["install"]
        cmd.extend(packages or self.name)
        if self.locked:
            cmd.append("--locked")
        if self.path:
            cmd.append("--root")
            cmd.append(self.path)
        if self.version:
            cmd.append("--version")
            cmd.append(self.version)
        if self.directory is not None:
            cmd.append("--path")
            cmd.append(self.directory)
        if self.registry is not None:
            cmd.append("--registry")
            cmd.append(self.registry)
        if self.git is not None:
            cmd.append("--git")
            cmd.append(self.git)
        if self.branch is not None:
            cmd.append("--branch")
            cmd.append(self.branch)
        if self.tag is not None:
            cmd.append("--tag")
            cmd.append(self.tag)
        if self.rev is not None:
            cmd.append("--rev")
            cmd.append(self.rev)
        if len(self.features) > 0:
            cmd.append("--features")
            cmd.append('"%s"' % (",".join(self.features)))
        if self.all_features:
            cmd.append("--all-features")
        if self.force:
            cmd.append("--force")
        if self.debug:
            cmd.append("--debug")
        return self._exec(cmd)

    def uninstall(self, packages=None):
        cmd = ["uninstall"]
        cmd.extend(packages or self.name)
        return self._exec(cmd)


def main():
    arg_spec = dict(
        executable=dict(default=None, type="path"),
        name=dict(required=True, type="list", elements="str"),
        path=dict(default=None, type="path"),
        state=dict(default="present", choices=["present", "absent", "latest"]),
        version=dict(default=None, type="str"),
        locked=dict(default=False, type="bool"),
        features=dict(default=[], type="list", elements="str"),
        all_features=dict(default=False, type="bool"),
        force=dict(default=False, type="bool"),
        directory=dict(default=None, type="path"),
        git=dict(default=None, type="str"),
        branch=dict(default=None, type="str"),
        tag=dict(default=None, type="str"),
        rev=dict(default=None, type="str"),
        registry=dict(default=None, type="str"),
        debug=dict(default=False, type="bool"),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("git", "registry", "directory"),
            ("version", "directory"),
            ("version", "git"),
            ("version", "branch"),
            ("version", "tag"),
            ("version", "rev"),
            ("features", "all_features"),
            ("branch", "tag", "rev"),
        ],
        required_by={
            "branch": "git",
            "tag": "git",
            "rev": "git",
        },
    )

    name = module.params["name"]
    state = module.params["state"]
    force = module.params["force"]
    directory = module.params["directory"]

    if not name:
        module.fail_json(msg="Package name must be specified")

    if directory is not None and not os.path.isdir(directory):
        module.fail_json(
            msg="Directory from where to install doesn't exist or format not understood"
        )

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(
        LANG="C", LC_ALL="C", LC_MESSAGES="C", LC_CTYPE="C"
    )

    cargo = Cargo(module, **module.params)
    changed, out, err = False, None, None
    if state == "present":
        to_install = [n for n in name if (force or not cargo.is_present(n))]
        if to_install:
            changed = True
            out, err = cargo.install(to_install)
    elif state == "latest":
        to_update = [
            n
            for n in name
            if (force or not cargo.is_present(n) or cargo.is_outdated(n))
        ]
        if to_update:
            changed = True
            out, err = cargo.install(to_update)
    else:  # absent
        to_uninstall = [n for n in name if cargo.is_present(n)]
        if to_uninstall:
            changed = True
            out, err = cargo.uninstall(to_uninstall)

    module.exit_json(changed=changed, stdout=out, stderr=err)


if __name__ == "__main__":
    main()
