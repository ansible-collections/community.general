# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.community.general.plugins.modules import lvm_pv


def _make_disk(sysfs, devices_path, disk, partitions=(), rescan_attr=None):
    """Create a fake sysfs layout for a disk and its partitions.

    Mimics the kernel layout where /sys/class/block/<name> and /sys/block/<disk> are symlinks
    into /sys/devices/..., and partitions are subdirectories of their parent disk.
    """
    disk_dir = sysfs / "devices" / devices_path / "block" / disk
    disk_dir.mkdir(parents=True)
    device_dir = sysfs / "devices" / devices_path / "device"
    device_dir.mkdir(parents=True, exist_ok=True)
    (disk_dir / "device").symlink_to(device_dir)
    if rescan_attr:
        (device_dir / rescan_attr).write_text("")

    for d in ("class/block", "block"):
        (sysfs / d).mkdir(parents=True, exist_ok=True)
    (sysfs / "class" / "block" / disk).symlink_to(disk_dir)
    (sysfs / "block" / disk).symlink_to(disk_dir)

    for part in partitions:
        part_dir = disk_dir / part
        part_dir.mkdir()
        (part_dir / "partition").write_text("1")
        (sysfs / "class" / "block" / part).symlink_to(part_dir)

    return device_dir / rescan_attr if rescan_attr else None


@pytest.fixture
def sysfs(tmp_path, monkeypatch):
    root = tmp_path / "sys"
    root.mkdir()
    monkeypatch.setattr(lvm_pv, "_SYSFS", str(root))
    return root


@pytest.fixture
def dev(tmp_path):
    root = tmp_path / "dev"
    root.mkdir()
    return root


def _device(dev, name):
    path = dev / name
    path.write_text("")
    return str(path)


@pytest.mark.parametrize(
    "devices_path, disk, partition, rescan_attr",
    [
        ("pci0000:00/scsi", "sdb", None, "rescan"),
        ("pci0000:00/scsi", "sdb", "sdb2", "rescan"),
        ("pci0000:00/nvme0", "nvme0n1", None, "rescan_controller"),
        ("pci0000:00/nvme0", "nvme0n1", "nvme0n1p1", "rescan_controller"),
    ],
)
def test_rescan_supported(sysfs, dev, devices_path, disk, partition, rescan_attr):
    rescan = _make_disk(sysfs, devices_path, disk, [partition] if partition else [], rescan_attr)
    module = MagicMock()

    assert lvm_pv.rescan_device(module, _device(dev, partition or disk)) is True
    assert rescan.read_text() == "1"
    module.warn.assert_not_called()


@pytest.mark.parametrize("name", ["vdb", "vdb1"])
def test_rescan_virtio_skipped_without_warning(sysfs, dev, name):
    _make_disk(sysfs, "pci0000:00/virtio2", "vdb", ["vdb1"])
    module = MagicMock()

    assert lvm_pv.rescan_device(module, _device(dev, name)) is False
    module.warn.assert_not_called()


def test_rescan_unknown_device_skipped_without_warning(sysfs, dev):
    module = MagicMock()

    assert lvm_pv.rescan_device(module, _device(dev, "loop0")) is False
    module.warn.assert_not_called()


def test_rescan_resolves_symlink(sysfs, dev):
    rescan = _make_disk(sysfs, "pci0000:00/scsi", "sdb", ["sdb1"], "rescan")
    by_id = dev / "disk" / "by-id"
    by_id.mkdir(parents=True)
    link = by_id / "scsi-0QEMU_QEMU_HARDDISK_drive-scsi1-part1"
    link.symlink_to(_device(dev, "sdb1"))
    module = MagicMock()

    assert lvm_pv.rescan_device(module, str(link)) is True
    assert rescan.read_text() == "1"


def test_rescan_mmcblk_partition_parent(sysfs, dev):
    """The parent disk is derived from sysfs, not by stripping digits from the name."""
    rescan = _make_disk(sysfs, "platform/mmc0", "mmcblk0", ["mmcblk0p1"], "rescan")
    module = MagicMock()

    assert lvm_pv.rescan_device(module, _device(dev, "mmcblk0p1")) is True
    assert rescan.read_text() == "1"


def test_rescan_write_failure_warns(sysfs, dev, monkeypatch):
    _make_disk(sysfs, "pci0000:00/scsi", "sdb", [], "rescan")
    device = _device(dev, "sdb")
    module = MagicMock()

    def failing_open(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr("builtins.open", failing_open)
    assert lvm_pv.rescan_device(module, device) is False
    module.warn.assert_called_once()
    assert "Failed to rescan device" in module.warn.call_args[0][0]
