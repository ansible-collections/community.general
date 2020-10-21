# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from unittest.mock import MagicMock

from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_snap
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args

def get_resources(type):
    return [{
      "diskwrite": 0,
      "vmid": 100,
      "node": "localhost",
      "id": "lxc/100",
      "maxdisk": 10000,
      "template": 0,
      "disk": 10000,
      "uptime": 10000,
      "maxmem": 10000,
      "maxcpu": 1,
      "netin": 10000,
      "type": "lxc",
      "netout": 10000,
      "mem": 10000,
      "diskread": 10000,
      "cpu": 0.01,
      "name": "test-lxc",
      "status": "running" }]

def get_snaps():
    return [{
      "running": 0,
      "name": "test",
      "digest": "deadbeef",
      "description": "Test!"
    }]

def task_start(snapname, description, vmstate):
    return str("UPID:localhost:00007C26:05D37B74:5F90A0B7:vzsnapshot:100:root@pam:")

def task_status():
    return {"starttime": 100000,
    "node": "localhost",
    "upid": "UPID:localhost:00007C26:05D37B74:5F90A0B7:vzsnapshot:100:root@pam:",
    "pstart": 100001,
    "exitstatus": "OK",
    "status": "stopped",
    "type": "vzsnapshot",
    "id": "100",
    "user": "root@pam",
    "pid": 1001}


def fake_api(api_host, api_user, api_password, validate_certs):
    #vmid = "100"
    #taskid = "UPID:localhost:00007C26:05D37B74:5F90A0B7:vzsnapshot:100:root@pam:"
    r = MagicMock()
    r.cluster.resources.get = MagicMock(side_effect=get_resources)
    r.nodes.localhost.lxc.vmid.snapshot.get = MagicMock(side_effect=get_snaps)
    r.nodes.localhost.lxc.vmid.snapshot.post = MagicMock(side_effect=task_start)
    r.nodes.localhost.tasks.taskid.status.get = MagicMock(side_effect=task_status)
    return r

def test_proxmox_snap_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']

def test_create_snapshot(mocker):
    set_module_args({"hostname": "test-lxc",
        "api_user": "root@pam",
        "api_password": "secret",
        "api_host": "127.0.0.1",
        "state": "present",
        "snapname": "test",
        "timeout": "1",
        "force": True,
        })
    proxmox_snap.HAS_PROXMOXER = True
    proxmox_snap.setup_api = mocker.MagicMock(side_effect=fake_api)
    proxmox_snap.main()
