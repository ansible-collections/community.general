# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

import pytest

proxmox = pytest.importorskip('proxmoxer')

from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_snap
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def test_proxmox_snap_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']
    assert 'project_path' in json.loads(out)['msg']
