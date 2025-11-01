# (c) 2017 Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import patch, call

from ansible_collections.community.general.plugins.modules import parted as parted_module
from ansible_collections.community.general.plugins.modules.parted import parse_parted_version
from ansible_collections.community.general.plugins.modules.parted import parse_partition_info
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

# Example of output : parted -s -m /dev/sdb -- unit 'MB' print
parted_output1 = """
BYT;
/dev/sdb:286061MB:scsi:512:512:msdos:ATA TOSHIBA THNSFJ25:;
1:1.05MB:106MB:105MB:fat32::esp;
2:106MB:368MB:262MB:ext2::;
3:368MB:256061MB:255692MB:::;"""

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
        self.assertEqual(parse_partition_info(parted_output1, "MB"), parted_dict1)
        self.assertEqual(parse_partition_info(parted_output2, "MB"), parted_dict2)

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
        with set_module_args(
            {"device": "/dev/sdb", "number": 3, "state": "present", "part_end": "100%", "resize": True}
        ):
            with patch(
                "ansible_collections.community.general.plugins.modules.parted.get_device_info",
                return_value=parted_dict1,
            ):
                self.execute_module(changed=True, script=["resizepart", "3", "100%"])

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

    def test_version_info(self):
        """Test that the parse_parted_version returns the expected tuple"""
        for key, value in parted_version_info.items():
            self.assertEqual(parse_parted_version(key), value)
