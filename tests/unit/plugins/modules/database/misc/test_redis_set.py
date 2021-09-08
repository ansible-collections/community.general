# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest
import json

from ansible_collections.community.general.plugins.modules.database.misc import redis_set
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def test_redis_set_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_set.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


def test_redis_set_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.set', return_value=True)
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert json.loads(
        out)['msg'] == 'Set key: foo to baz'
    assert json.loads(out)['changed'] is True


def test_redis_set_existing_key_nx(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     'non_existing': True,
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.set', return_value=None)
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert json.loads(
        out)['msg'] == 'Could not set key: foo to baz. Key already present.'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


def test_redis_set_non_existing_key_xx(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     'existing': True,
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value=None)
    mocker.patch('redis.Redis.set', return_value=None)
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] is None
    assert json.loads(
        out)['msg'] == 'Could not set key: foo to baz. Key not present.'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


def test_redis_set_delete_present_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent'})
    mocker.patch('redis.Redis.delete', return_value=1)
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Deleted key: foo'
    assert json.loads(out)['changed'] is True


def test_redis_set_delete_absent_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent'})
    mocker.patch('redis.Redis.delete', return_value=0)
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Key: foo not present'
    assert json.loads(out)['changed'] is False
