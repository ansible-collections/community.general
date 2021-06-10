# Copyright (c) 2020 Shay Rybak <shay.rybak@stackpath.com>
# Copyright (c) 2020 Ansible Project
# GNGeneral Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError
from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.stackpath_compute import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_get_stack_slugs(inventory):
    stacks = [
        {
            'status': 'ACTIVE',
            'name': 'test1',
            'id': 'XXXX',
            'updatedAt': '2020-07-08T01:00:00.000000Z',
            'slug': 'test1',
            'createdAt': '2020-07-08T00:00:00.000000Z',
            'accountId': 'XXXX',
        }, {
            'status': 'ACTIVE',
            'name': 'test2',
            'id': 'XXXX',
            'updatedAt': '2019-10-22T18:00:00.000000Z',
            'slug': 'test2',
            'createdAt': '2019-10-22T18:00:00.000000Z',
            'accountId': 'XXXX',
        }, {
            'status': 'DISABLED',
            'name': 'test3',
            'id': 'XXXX',
            'updatedAt': '2020-01-16T20:00:00.000000Z',
            'slug': 'test3',
            'createdAt': '2019-10-15T13:00:00.000000Z',
            'accountId': 'XXXX',
        }, {
            'status': 'ACTIVE',
            'name': 'test4',
            'id': 'XXXX',
            'updatedAt': '2019-11-20T22:00:00.000000Z',
            'slug': 'test4',
            'createdAt': '2019-11-20T22:00:00.000000Z',
            'accountId': 'XXXX',
        }
    ]
    inventory._get_stack_slugs(stacks)
    assert len(inventory.stack_slugs) == 4
    assert inventory.stack_slugs == [
        "test1",
        "test2",
        "test3",
        "test4"
    ]


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.stackpath_compute.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.stackpath_compute.yml') is False


def test_validate_config(inventory):
    config = {
        "client_secret": "short_client_secret",
        "use_internal_ip": False,
        "stack_slugs": ["test1"],
        "client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "plugin": "community.general.stackpath_compute",
    }
    with pytest.raises(AnsibleError) as error_message:
        inventory._validate_config(config)
        assert "client_secret must be 64 characters long" in error_message

    config = {
        "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "use_internal_ip": True,
        "stack_slugs": ["test1"],
        "client_id": "short_client_id",
        "plugin": "community.general.stackpath_compute",
    }
    with pytest.raises(AnsibleError) as error_message:
        inventory._validate_config(config)
        assert "client_id must be 32 characters long" in error_message

    config = {
        "use_internal_ip": True,
        "stack_slugs": ["test1"],
        "client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "plugin": "community.general.stackpath_compute",
    }
    with pytest.raises(AnsibleError) as error_message:
        inventory._validate_config(config)
        assert "config missing client_secret, a required paramter" in error_message

    config = {
        "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "use_internal_ip": False,
        "plugin": "community.general.stackpath_compute",
    }
    with pytest.raises(AnsibleError) as error_message:
        inventory._validate_config(config)
        assert "config missing client_id, a required paramter" in error_message


def test_populate(inventory):
    instances = [
        {
            "name": "instance1",
            "countryCode": "SE",
            "workloadSlug": "wokrload1",
            "continent": "Europe",
            "workloadId": "id1",
            "cityCode": "ARN",
            "externalIpAddress": "20.0.0.1",
            "target": "target1",
            "stackSlug": "stack1",
            "ipAddress": "10.0.0.1",
        },
        {
            "name": "instance2",
            "countryCode": "US",
            "workloadSlug": "wokrload2",
            "continent": "America",
            "workloadId": "id2",
            "cityCode": "JFK",
            "externalIpAddress": "20.0.0.2",
            "target": "target2",
            "stackSlug": "stack1",
            "ipAddress": "10.0.0.2",
        },
        {
            "name": "instance3",
            "countryCode": "SE",
            "workloadSlug": "workload3",
            "continent": "Europe",
            "workloadId": "id3",
            "cityCode": "ARN",
            "externalIpAddress": "20.0.0.3",
            "target": "target1",
            "stackSlug": "stack2",
            "ipAddress": "10.0.0.3",
        },
        {
            "name": "instance4",
            "countryCode": "US",
            "workloadSlug": "workload3",
            "continent": "America",
            "workloadId": "id4",
            "cityCode": "JFK",
            "externalIpAddress": "20.0.0.4",
            "target": "target2",
            "stackSlug": "stack2",
            "ipAddress": "10.0.0.4",
        },
    ]
    inventory.hostname_key = "externalIpAddress"
    inventory._populate(instances)
    # get different hosts
    host1 = inventory.inventory.get_host('20.0.0.1')
    host2 = inventory.inventory.get_host('20.0.0.2')
    host3 = inventory.inventory.get_host('20.0.0.3')
    host4 = inventory.inventory.get_host('20.0.0.4')

    # get different groups
    assert 'citycode_arn' in inventory.inventory.groups
    group_citycode_arn = inventory.inventory.groups['citycode_arn']
    assert 'countrycode_se' in inventory.inventory.groups
    group_countrycode_se = inventory.inventory.groups['countrycode_se']
    assert 'continent_america' in inventory.inventory.groups
    group_continent_america = inventory.inventory.groups['continent_america']
    assert 'name_instance1' in inventory.inventory.groups
    group_name_instance1 = inventory.inventory.groups['name_instance1']
    assert 'stackslug_stack1' in inventory.inventory.groups
    group_stackslug_stack1 = inventory.inventory.groups['stackslug_stack1']
    assert 'target_target1' in inventory.inventory.groups
    group_target_target1 = inventory.inventory.groups['target_target1']
    assert 'workloadslug_workload3' in inventory.inventory.groups
    group_workloadslug_workload3 = inventory.inventory.groups['workloadslug_workload3']
    assert 'workloadid_id1' in inventory.inventory.groups
    group_workloadid_id1 = inventory.inventory.groups['workloadid_id1']

    assert group_citycode_arn.hosts == [host1, host3]
    assert group_countrycode_se.hosts == [host1, host3]
    assert group_continent_america.hosts == [host2, host4]
    assert group_name_instance1.hosts == [host1]
    assert group_stackslug_stack1.hosts == [host1, host2]
    assert group_target_target1.hosts == [host1, host3]
    assert group_workloadslug_workload3.hosts == [host3, host4]
    assert group_workloadid_id1.hosts == [host1]
