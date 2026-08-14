# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.module_utils.homebrew import (
    HomebrewValidate,
)
from ansible_collections.community.general.plugins.modules.homebrew_cask import (
    HomebrewCask,
)


def test_valid_cask_names():
    brew_cask_names = ["visual-studio-code", "firefox"]
    for name in brew_cask_names:
        assert HomebrewCask.valid_cask(name)


def test_homebrew_version(mocker):
    # NB: HomebrewCask._get_brew_version() caches its result on the instance, so
    # brew_version is reset before each case below -- otherwise every iteration after
    # the first would just return the first case's cached value without actually
    # exercising the regex (as the previous version of this test did: it only ever
    # verified the first case below).
    brew_versions = {
        "Homebrew 4.1.0": "4.1.0",
        # A placeholder version (e.g. a shallow git clone) is deliberately treated as
        # "newer than anything we'd otherwise compare against" -- see _get_brew_version.
        "Homebrew >=4.1.0 (shallow or no git repository)": "99.0.0",
        "Homebrew 4.1.0-dirty": "4.1.0",
        # Some Homebrew builds report more than three dot-separated version segments.
        "Homebrew 4.6.13.1-custom-18-gabcdef0": "4.6.13.1",
    }
    module = mocker.Mock()

    mocker.patch.object(HomebrewCask, "valid_module", return_value=True)
    mocker.patch.object(HomebrewValidate, "valid_path", return_value=True)
    mocker.patch.object(HomebrewValidate, "valid_brew_path", return_value=True)

    homebrewcask = HomebrewCask(module=module)
    for version, expected in brew_versions.items():
        homebrewcask.brew_version = None
        module.run_command.return_value = (0, version, "")
        assert homebrewcask._get_brew_version() == expected
