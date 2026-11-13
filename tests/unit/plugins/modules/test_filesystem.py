# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock

import pytest

from ansible_collections.community.general.plugins.modules import filesystem


class ModuleExit(Exception):
    pass


@pytest.mark.parametrize("fs_class", [filesystem.Ext2, filesystem.Ext3, filesystem.Ext4])
@pytest.mark.parametrize("block_size", [1024, 2048, 4096])
@pytest.mark.parametrize("extra_blocks", [0, 1])
@pytest.mark.parametrize("check_mode", [False, True])
def test_ext_growth_ignores_only_incomplete_blocks(fs_class, block_size, extra_blocks, check_mode):
    module = Mock()
    module.check_mode = check_mode
    module.exit_json.side_effect = ModuleExit
    module.get_bin_path.side_effect = lambda name, **kwargs: name
    module.run_command.return_value = (0, f"Block count: 100\nBlock size: {block_size}\n", "")
    device = Mock()
    device.size.return_value = (100 + extra_blocks) * block_size + block_size - 1
    fs = fs_class(module)

    if not extra_blocks or check_mode:
        with pytest.raises(ModuleExit):
            fs.grow(device)
        assert module.exit_json.call_args.kwargs["changed"] is bool(extra_blocks)
        assert module.run_command.call_count == 1
    else:
        fs.grow(device)
        assert module.run_command.call_count == 2
        assert module.run_command.call_args.args[0] == ["resize2fs", str(device)]
