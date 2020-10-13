from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import platform

import pytest
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.modules.system import (
    solaris_zone
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    set_module_args,
)


ZONEADM = "/usr/sbin/zoneadm"


def mocker_zone_set(mocker, zone_exists=False, rc=0, out="", err=""):
    """
    Configure common mocker object for Solaris Zone tests
    """
    get_bin_path = mocker.patch.object(AnsibleModule, "get_bin_path")
    get_bin_path.return_value = ZONEADM
    run_command = mocker.patch.object(AnsibleModule, "run_command")
    run_command.return_value = (rc, out, err)
    zone_exists_func = mocker.patch.object(solaris_zone.Zone, "exists")
    zone_exists_func.return_value = zone_exists
    platform_release = mocker.patch.object(platform, "release")
    platform_release.return_value = '5.11'
    platform_system = mocker.patch.object(platform, "system")
    platform_system.return_value = 'SunOS'


@pytest.fixture
def mocked_zone_create(mocker):
    mocker_zone_set(mocker)


@pytest.fixture
def mocked_zone_delete(mocker):
    mocker_zone_set(mocker, zone_exists=True)


def test_zone_create(mocked_zone_create, capfd):
    """
    zone creation
    """
    zone_name = "z1"
    set_module_args(
        {
            "name": zone_name,
            "state": "installed",
            "path": "/zones/" + zone_name,
            "_ansible_check_mode": False,
        }
    )
    with pytest.raises(SystemExit):
        solaris_zone.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print(results)
    assert not results.get("failed")
    assert results["changed"]
