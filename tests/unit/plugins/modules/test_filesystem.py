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
def test_ext_growth_reports_only_actual_size_changes(fs_class, block_size, extra_blocks, check_mode):
    module = Mock()
    module.check_mode = check_mode
    module.exit_json.side_effect = ModuleExit
    module.get_bin_path.side_effect = lambda name, **kwargs: name
    info_calls = 0

    def run_command(args, **kwargs):
        nonlocal info_calls
        if args[0] == "tune2fs":
            info_calls += 1
            block_count = 100 + (extra_blocks if info_calls > 1 else 0)
            return 0, f"Block count: {block_count}\nBlock size: {block_size}\n", ""
        return 0, "resize output", ""

    module.run_command.side_effect = run_command
    device = Mock()
    device.size.return_value = (100 + extra_blocks) * block_size + block_size - 1
    fs = fs_class(module)

    if check_mode or not extra_blocks:
        with pytest.raises(ModuleExit):
            fs.grow(device)
        assert module.exit_json.call_args.kwargs["changed"] is bool(extra_blocks)
        assert module.run_command.call_count == (1 if check_mode else 3)
    else:
        assert fs.grow(device) == "resize output"
        assert module.run_command.call_count == 3
        assert module.run_command.call_args_list[1].args[0] == ["resize2fs", str(device)]
