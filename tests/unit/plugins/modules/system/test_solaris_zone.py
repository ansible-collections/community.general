# Copyright (c) 2020 Justin Bronn <jbronn@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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


def mocker_zone_set(mocker, rc=0, out="", err="", zone_exists=False, zone_status=None):
    """
    Configure common mocker object for Solaris Zone tests
    """
    exists = mocker.patch.object(solaris_zone.Zone, "exists")
    exists.return_value = zone_exists
    get_bin_path = mocker.patch.object(AnsibleModule, "get_bin_path")
    get_bin_path.return_value = ZONEADM
    run_command = mocker.patch.object(AnsibleModule, "run_command")
    run_command.return_value = (rc, out, err)
    platform_release = mocker.patch.object(platform, "release")
    platform_release.return_value = "5.11"
    platform_system = mocker.patch.object(platform, "system")
    platform_system.return_value = "SunOS"
    if zone_status is not None:
        status = mocker.patch.object(solaris_zone.Zone, "status")
        status.return_value = zone_status


@pytest.fixture
def mocked_zone_create(mocker):
    mocker_zone_set(mocker)


@pytest.fixture
def mocked_zone_delete(mocker):
    mocker_zone_set(mocker, zone_exists=True, zone_status="running")


def test_zone_create(mocked_zone_create, capfd):
    """
    test zone creation
    """
    set_module_args(
        {
            "name": "z1",
            "state": "installed",
            "path": "/zones/z1",
            "_ansible_check_mode": False,
        }
    )
    with pytest.raises(SystemExit):
        solaris_zone.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get("failed")
    assert results["changed"]


def test_zone_delete(mocked_zone_delete, capfd):
    """
    test zone deletion
    """
    set_module_args(
        {
            "name": "z1",
            "state": "absent",
            "path": "/zones/z1",
            "_ansible_check_mode": False,
        }
    )
    with pytest.raises(SystemExit):
        solaris_zone.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get("failed")
    assert results["changed"]


def test_zone_create_invalid_names(mocked_zone_create, capfd):
    """
    test zone creation with invalid names
    """
    # 1. Invalid character ('!').
    # 2. Zone name > 64 characters.
    # 3. Zone name beginning with non-alphanumeric character.
    for invalid_name in ('foo!bar', 'z' * 65, '_zone'):
        set_module_args(
            {
                "name": invalid_name,
                "state": "installed",
                "path": "/zones/" + invalid_name,
                "_ansible_check_mode": False,
            }
        )
        with pytest.raises(SystemExit):
            solaris_zone.main()

        out, err = capfd.readouterr()
        results = json.loads(out)
        assert results.get("failed")
