# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.community.general.plugins.modules.homebrew_cask import (
    HomebrewCask,
)
from ansible_collections.community.general.plugins.module_utils.homebrew import (
    HomebrewValidate,
)


def test_valid_cask_names():
    brew_cask_names = ["visual-studio-code", "firefox"]
    for name in brew_cask_names:
        assert HomebrewCask.valid_cask(name)


def test_homebrew_version(mocker):
    brew_versions = [
        "Homebrew 4.1.0",
        "Homebrew >=4.1.0 (shallow or no git repository)",
        "Homebrew 4.1.0-dirty",
    ]
    module = mocker.Mock()

    mocker.patch.object(HomebrewCask, "valid_module", return_value=True)
    mocker.patch.object(HomebrewValidate, "valid_path", return_value=True)
    mocker.patch.object(HomebrewValidate, "valid_brew_path", return_value=True)

    homebrewcask = HomebrewCask(module=module)
    for version in brew_versions:
        module.run_command.return_value = (0, version, "")
        assert homebrewcask._get_brew_version() == "4.1.0"
