# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    exit_json,
)

from ansible_collections.community.general.plugins.modules import filesystem


class ModuleExit(Exception):
    pass


@pytest.mark.parametrize("fs_class", [filesystem.Ext2, filesystem.Ext3, filesystem.Ext4])
@pytest.mark.parametrize("block_size", [1024, 2048, 4096])
@pytest.mark.parametrize("extra_blocks", [0, 1])
@pytest.mark.parametrize("check_mode", [False, True])
@pytest.mark.parametrize("compare_disk_blocks", [False, True])
def test_ext_growth_change_detection(fs_class, block_size, extra_blocks, check_mode, compare_disk_blocks):
    module = Mock()
    module.check_mode = check_mode
    module.params = dict(
        state="present",
        fstype=fs_class.__name__.lower(),
        dev="/dev/test",
        opts=None,
        force=False,
        resizefs=True,
        resize_compare_disk_blocks=compare_disk_blocks,
        uuid=None,
        label=None,
    )
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

    if check_mode or (compare_disk_blocks and not extra_blocks):
        with pytest.raises(ModuleExit):
            fs.grow(device)
        assert module.exit_json.call_args.kwargs["changed"] is (bool(extra_blocks) or not compare_disk_blocks)
        assert module.run_command.call_count == (1 if check_mode else 3)
    else:
        assert fs.grow(device) == "resize output"
        assert module.run_command.call_count == (3 if compare_disk_blocks else 2)
        assert module.run_command.call_args_list[1].args[0] == ["resize2fs", str(device)]


@pytest.mark.parametrize(
    "options, changed",
    [({}, True), ({"resize_compare_disk_blocks": False}, True), ({"resize_compare_disk_blocks": True}, False)],
)
def test_main_ext_resize_option(options, changed, tmp_path, monkeypatch, patch_ansible_module_uthelper):
    image = tmp_path / "ext.img"
    with image.open("wb") as stream:
        stream.truncate(409599)

    def run_command(self, args, **kwargs):
        if args[0] == "blkid":
            return 0, "ext4\n", ""
        if args[0] == "tune2fs":
            return 0, "Block count: 99\nBlock size: 4096\n", ""
        pytest.fail(f"Unexpected command in check mode: {args}")

    monkeypatch.setattr(filesystem.AnsibleModule, "get_bin_path", lambda self, name, **kwargs: name)
    monkeypatch.setattr(filesystem.AnsibleModule, "run_command", run_command)
    monkeypatch.setattr(filesystem.AnsibleModule, "exit_json", exit_json)
    with patch_ansible_module_uthelper(
        dict(dev=str(image), fstype="ext4", resizefs=True, _ansible_check_mode=True, **options)
    ):
        with pytest.raises(AnsibleExitJson) as result:
            filesystem.main()
    assert result.value.args[0]["changed"] is changed
