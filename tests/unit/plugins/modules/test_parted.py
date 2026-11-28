# (c) 2017 Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import call, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import parted as parted_module
from ansible_collections.community.general.plugins.modules.parted import (
    get_end_location,
    get_partition_sectors,
    parse_parted_version,
    parse_partition_info,
)

# Example of output : parted -s -m /dev/sdb -- unit 'MB' print
parted_output1 = """
BYT;
/dev/sdb:286061MB:scsi:512:512:msdos:ATA TOSHIBA THNSFJ25:;
1:1.05MB:106MB:105MB:fat32::esp;
2:106MB:368MB:262MB:ext2::;
3:368MB:256061MB:255692MB:::;"""

# Example of output : parted -s -m /dev/sdb -- unit s print free
parted_free_output1 = """
BYT;
/dev/sdb:558712890s:scsi:512:512:msdos:ATA TOSHIBA THNSFJ25:;
1:32s:2047s:2016s:free;
1:2048s:206847s:204800s:fat32::esp;
2:206848s:718847s:512000s:ext2::;
3:718848s:500118191s:499399344s:::;
1:500118192s:558712889s:58594698s:free;"""

# GPT disk whose partition can still grow: parted -s -m /dev/sdb -- unit s print free
parted_gpt_free_output_grow = """
BYT;
/dev/sdb:2097152s:file:512:512:gpt::;
1:34s:2047s:2014s:free;
1:2048s:1048575s:1046528s::primary:;
1:1048576s:2097118s:1048543s:free;"""

# Same disk after "resizepart 1 100%": parted -s -m /dev/sdb -- unit s print free
parted_gpt_free_output_full = """
BYT;
/dev/sdb:2097152s:file:512:512:gpt::;
1:34s:2047s:2014s:free;
1:2048s:2097118s:2095071s::primary:;"""

# Same disk: parted -s -m /dev/sdb -- unit KiB print
parted_gpt_output_full = """
BYT;
/dev/sdb:1048576kiB:file:512:512:gpt::;
1:1024kiB:1048559kiB:1047536kiB::primary:;"""

# Logical partition filling its extended partition: parted -s -m /dev/sdb -- unit s print free
parted_logical_free_output = """
BYT;
/dev/sdb:2097152s:file:512:512:msdos::;
1:32s:2047s:2016s:free;
1:2048s:1228799s:1226752s:::lba;
1:2080s:3967s:1888s:free;
5:4096s:1228799s:1224704s:::;
1:1228800s:1433599s:204800s:free;
2:1433600s:2097151s:663552s:::;"""

parted_version_info = {
    """
        parted (GNU parted) 3.3
        Copyright (C) 2019 Free Software Foundation, Inc.
        License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.

        Written by <http://git.debian.org/?p=parted/parted.git;a=blob_plain;f=AUTHORS>.
        """: (3, 3, 0),
    """
        parted (GNU parted) 3.4.5
        Copyright (C) 2019 Free Software Foundation, Inc.
        License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.

        Written by <http://git.debian.org/?p=parted/parted.git;a=blob_plain;f=AUTHORS>.
        """: (3, 4, 5),
    """
        parted (GNU parted) 3.3.14-dfc61
        Copyright (C) 2019 Free Software Foundation, Inc.
        License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.

        Written by <http://git.debian.org/?p=parted/parted.git;a=blob_plain;f=AUTHORS>.
        """: (3, 3, 14),
}

# corresponding dictionary after parsing by parse_partition_info
parted_dict1 = {
    "generic": {
        "dev": "/dev/sdb",
        "size": 286061.0,
        "unit": "mb",
        "table": "msdos",
        "model": "ATA TOSHIBA THNSFJ25",
        "logical_block": 512,
        "physical_block": 512,
    },
    "partitions": [
        {
            "num": 1,
            "begin": 1.05,
            "end": 106.0,
            "size": 105.0,
            "fstype": "fat32",
            "name": "",
            "flags": ["esp"],
            "unit": "mb",
        },
        {
            "num": 2,
            "begin": 106.0,
            "end": 368.0,
            "size": 262.0,
            "fstype": "ext2",
            "name": "",
            "flags": [],
            "unit": "mb",
        },
        {
            "num": 3,
            "begin": 368.0,
            "end": 256061.0,
            "size": 255692.0,
            "fstype": "",
            "name": "",
            "flags": [],
            "unit": "mb",
        },
    ],
}

parted_output2 = """
BYT;
/dev/sdb:286061MB:scsi:512:512:msdos:ATA TOSHIBA THNSFJ25:;"""

# corresponding dictionary after parsing by parse_partition_info
parted_dict2 = {
    "generic": {
        "dev": "/dev/sdb",
        "size": 286061.0,
        "unit": "mb",
        "table": "msdos",
        "model": "ATA TOSHIBA THNSFJ25",
        "logical_block": 512,
        "physical_block": 512,
    },
    "partitions": [],
}

# fake some_flag exists
parted_dict3 = {
    "generic": {
        "dev": "/dev/sdb",
        "size": 286061.0,
        "unit": "mb",
        "table": "msdos",
        "model": "ATA TOSHIBA THNSFJ25",
        "logical_block": 512,
        "physical_block": 512,
    },
    "partitions": [
        {
            "num": 1,
            "begin": 1.05,
            "end": 106.0,
            "size": 105.0,
            "fstype": "fat32",
            "name": "",
            "flags": ["some_flag"],
            "unit": "mb",
        }
    ],
}


# Simulates SUSE-patched parted that exposes MBR type codes as flags.
# Partition 1 has "lvm" set + SUSE adds "type=8e" as a pseudo-flag.
parted_dict_suse_lvm = {
    "generic": {
        "dev": "/dev/sdb",
        "size": 286061.0,
        "unit": "mb",
        "table": "msdos",
        "model": "ATA TOSHIBA THNSFJ25",
        "logical_block": 512,
        "physical_block": 512,
    },
    "partitions": [
        {
            "num": 1,
            "begin": 1.05,
            "end": 106.0,
            "size": 105.0,
            "fstype": "",
            "name": "",
            "flags": ["lvm", "type=8e"],
            "unit": "mb",
        }
    ],
}

# Simulates SUSE-patched parted where partition has no logical flags yet,
# but SUSE reports "type=83" (Linux MBR type code) as a pseudo-flag.
parted_dict_suse_noflag = {
    "generic": {
        "dev": "/dev/sdb",
        "size": 286061.0,
        "unit": "mb",
        "table": "msdos",
        "model": "ATA TOSHIBA THNSFJ25",
        "logical_block": 512,
        "physical_block": 512,
    },
    "partitions": [
        {
            "num": 1,
            "begin": 1.05,
            "end": 106.0,
            "size": 105.0,
            "fstype": "",
            "name": "",
            "flags": ["type=83"],
            "unit": "mb",
        }
    ],
}


class TestParted(ModuleTestCase):
    def setUp(self):
        super().setUp()

        self.module = parted_module
        self.mock_check_parted_label = patch(
            "ansible_collections.community.general.plugins.modules.parted.check_parted_label", return_value=False
        )
        self.check_parted_label = self.mock_check_parted_label.start()

        self.mock_parted = patch("ansible_collections.community.general.plugins.modules.parted.parted")
        self.parted = self.mock_parted.start()

        self.mock_run_command = patch("ansible.module_utils.basic.AnsibleModule.run_command")
        self.run_command = self.mock_run_command.start()

        self.mock_get_bin_path = patch("ansible.module_utils.basic.AnsibleModule.get_bin_path")
        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        super().tearDown()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        self.mock_parted.stop()
        self.mock_check_parted_label.stop()

    def execute_module(self, failed=False, changed=False, script=None):
        if failed:
            result = self.failed()
            self.assertTrue(result["failed"], result)
        else:
            result = self.changed(changed)
            self.assertEqual(result["changed"], changed, result)

        if script:
            self.assertEqual(script, result["script"], result["script"])

        return result

    def failed(self):
        with self.assertRaises(AnsibleFailJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertTrue(result["failed"], result)
        return result

    def changed(self, changed=False):
        with self.assertRaises(AnsibleExitJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertEqual(result["changed"], changed, result)
        return result

    def test_parse_partition_info(self):
        """Test that the parse_partition_info returns the expected dictionary"""
        self.assertEqual(parse_partition_info(parted_output1, "MB", False), parted_dict1)
        self.assertEqual(parse_partition_info(parted_output2, "MB", False), parted_dict2)

    def test_partition_already_exists(self):
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=False)

    def test_create_new_partition(self):
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 4,
                "state": "present",
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["unit", "KiB", "mkpart", "primary", "0%", "100%"])

    def test_create_new_partition_1G(self):
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 4,
                "state": "present",
                "part_end": "1GiB",
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["unit", "KiB", "mkpart", "primary", "0%", "1GiB"])

    def test_create_new_partition_minus_1G(self):
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 4,
                "state": "present",
                "fs_type": "ext2",
                "part_start": "-1GiB",
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["unit", "KiB", "mkpart", "primary", "ext2", "-1GiB", "100%"])

    def test_remove_partition_number_1(self):
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "absent",
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["rm", "1"])

    def test_resize_partition(self):
        self.run_command.return_value = (0, parted_free_output1, "")
        with set_module_args(
            {"device": "/dev/sdb", "number": 3, "state": "present", "part_end": "100%", "resize": True}
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["resizepart", "3", "100%"])

    def test_resize_partition_gpt_already_at_end(self):
        self.run_command.return_value = (0, parted_gpt_free_output_full, "")
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "label": "gpt",
                "unit": "KiB",
                "part_end": "100%",
                "resize": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parse_partition_info(parted_gpt_output_full, "KiB", False),
            ):
                self.execute_module(changed=False)
        self.parted.assert_not_called()

    def test_resize_partition_gpt_check_mode(self):
        self.run_command.return_value = (0, parted_gpt_free_output_grow, "")
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "label": "gpt",
                "unit": "KiB",
                "part_end": "100%",
                "resize": True,
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parse_partition_info(parted_gpt_output_full, "KiB", False),
            ):
                self.execute_module(changed=True, script=["resizepart", "1", "100%"])

    def test_resize_partition_gpt_beyond_free_space(self):
        # An exact location past the usable space is passed on to parted, which reports the error
        self.run_command.return_value = (0, parted_gpt_free_output_full, "")
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "label": "gpt",
                "part_end": "-1s",
                "resize": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parse_partition_info(parted_gpt_output_full, "KiB", False),
            ):
                self.execute_module(changed=True, script=["resizepart", "1", "-1s"])

    def test_change_flag(self):
        # Flags are set in a second run of parted().
        # Between the two runs, the partition dict is updated.
        # use checkmode here allow us to continue even if the dictionary is
        # not updated.
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 3,
                "state": "present",
                "flags": ["lvm", "boot"],
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.parted.reset_mock()
                self.execute_module(changed=True)
                # When using multiple flags:
                # order of execution is non deterministic, because set() operations are used in
                # the current implementation.
                expected_calls_order1 = [
                    call(["unit", "KiB", "set", "3", "lvm", "on", "set", "3", "boot", "on"], "/dev/sdb", "optimal")
                ]
                expected_calls_order2 = [
                    call(["unit", "KiB", "set", "3", "boot", "on", "set", "3", "lvm", "on"], "/dev/sdb", "optimal")
                ]
                self.assertTrue(
                    self.parted.mock_calls == expected_calls_order1 or self.parted.mock_calls == expected_calls_order2
                )

    def test_create_new_primary_lvm_partition(self):
        # use check_mode, see previous test comment
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 4,
                "flags": ["boot"],
                "state": "present",
                "part_start": "257GiB",
                "fs_type": "ext3",
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(
                    changed=True,
                    script=[
                        "unit",
                        "KiB",
                        "mkpart",
                        "primary",
                        "ext3",
                        "257GiB",
                        "100%",
                        "unit",
                        "KiB",
                        "set",
                        "4",
                        "boot",
                        "on",
                    ],
                )

    def test_create_label_gpt(self):
        # Like previous test, current implementation use parted to create the partition and
        # then retrieve and update the dictionary. Use check_mode to force to continue even if
        # dictionary is not updated.
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "flags": ["lvm"],
                "label": "gpt",
                "name": "lvmpartition",
                "state": "present",
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict2,
            ):
                self.execute_module(
                    changed=True,
                    script=[
                        "unit",
                        "KiB",
                        "mklabel",
                        "gpt",
                        "mkpart",
                        "primary",
                        "0%",
                        "100%",
                        "unit",
                        "KiB",
                        "name",
                        "1",
                        '"lvmpartition"',
                        "set",
                        "1",
                        "lvm",
                        "on",
                    ],
                )

    def test_change_label_gpt(self):
        # When partitions already exists and label is changed, mkpart should be called even when partition already exists,
        # because new empty label will be created anyway
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "label": "gpt",
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(
                    changed=True, script=["unit", "KiB", "mklabel", "gpt", "mkpart", "primary", "0%", "100%"]
                )

    def test_check_mode_unchanged(self):
        # Test that get_device_info result is checked in check mode too
        # No change on partition 1
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "flags": ["some_flag"],
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict3,
            ):
                self.execute_module(changed=False)

    def test_check_mode_changed(self):
        # Test that get_device_info result is checked in check mode too
        # Flag change on partition 1
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "flags": ["other_flag"],
                "_ansible_check_mode": True,
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict3,
            ):
                self.execute_module(changed=True)

    def test_suse_msdos_type_code_with_lvm_already_set(self):
        # When SUSE parted reports "type=8e" alongside "lvm" in the flags output,
        # the module must not try to unset the pseudo-flag (issue #6292).
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "flags": ["lvm"],
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict_suse_lvm,
            ):
                self.execute_module(changed=False)

    def test_suse_msdos_type_code_set_lvm_flag(self):
        # When SUSE parted only reports "type=83" (no logical flags) and the user
        # requests lvm, the module must set lvm without trying to unset type=83.
        with set_module_args(
            {
                "device": "/dev/sdb",
                "number": 1,
                "state": "present",
                "flags": ["lvm"],
            }
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict_suse_noflag,
            ):
                self.parted.reset_mock()
                self.execute_module(changed=True)
                self.assertEqual(
                    self.parted.mock_calls,
                    [call(["unit", "KiB", "set", "1", "lvm", "on"], "/dev/sdb", "optimal")],
                )

    def test_version_info(self):
        """Test that the parse_parted_version returns the expected tuple"""
        for key, value in parted_version_info.items():
            self.assertEqual(parse_parted_version(key), value)


# Expected values measured with parted 3.6 on a 1GiB disk (2097152 sectors) unless stated otherwise
@pytest.mark.parametrize(
    "part_end, unit, disk_length, expected",
    [
        ("1000000s", "KiB", 2097152, (1000000, 0)),
        ("512000000B", "KiB", 2097152, (1000000, 0)),
        ("500MiB", "KiB", 2097152, (1023999, 0)),
        ("500MB", "KiB", 2097152, (976562, 976)),
        ("700001KB", "KiB", 2097152, (1367189, 0)),
        ("600", "compact", 2097152, (1171875, 976)),
        ("600", "MB", 2097152, (1171875, 976)),
        ("50%", "KiB", 2097152, (1048575, 10485)),
        ("33%", "KiB", 2097152, (692060, 10485)),
        ("1%", "KiB", 1000000, (10000, 4999)),
        ("-1s", "KiB", 2097152, (2097151, 0)),
        ("-10MiB", "KiB", 2097152, (2076671, 0)),
        ("-100", "MB", 2097152, (1901840, 976)),
        ("100", "cyl", 2097152, None),
        ("10,20,30", "KiB", 2097152, None),
    ],
)
def test_get_end_location(part_end, unit, disk_length, expected):
    assert get_end_location(part_end, unit, disk_length, 512) == expected


@pytest.mark.parametrize(
    "output, number, expected",
    [
        (parted_gpt_free_output_grow, 1, (2097152, 512, 1048575, 2097118)),
        (parted_gpt_free_output_full, 1, (2097152, 512, 2097118, 2097118)),
        (parted_logical_free_output, 5, (2097152, 512, 1228799, 1228799)),
        (parted_logical_free_output, 1, (2097152, 512, 1228799, 1433599)),
    ],
)
def test_get_partition_sectors(mocker, output, number, expected):
    module = mocker.patch.object(parted_module, "module", create=True)
    mocker.patch.object(parted_module, "parted_exec", "/sbin/parted", create=True)
    module.run_command.return_value = (0, output, "")

    assert get_partition_sectors("/dev/sdb", number) == expected
    module.run_command.assert_called_once_with(
        ["/sbin/parted", "-s", "-m", "/dev/sdb", "--", "unit", "s", "print", "free"]
    )
