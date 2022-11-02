# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.modules.proxmox_kvm import parse_dev, parse_mac


def test_parse_mac():
    assert parse_mac('virtio=00:11:22:AA:BB:CC,bridge=vmbr0,firewall=1') == '00:11:22:AA:BB:CC'


def test_parse_dev():
    assert parse_dev('local-lvm:vm-1000-disk-0,format=qcow2') == 'local-lvm:vm-1000-disk-0'
    assert parse_dev('local-lvm:vm-101-disk-1,size=8G') == 'local-lvm:vm-101-disk-1'
    assert parse_dev('local-zfs:vm-1001-disk-0') == 'local-zfs:vm-1001-disk-0'
