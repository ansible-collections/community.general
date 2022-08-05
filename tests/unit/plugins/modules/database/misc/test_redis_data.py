# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest
import json
from redis import __version__

from ansible_collections.community.general.plugins.modules.database.misc import redis_data
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args

HAS_REDIS_USERNAME_OPTION = True
if tuple(map(int, __version__.split('.'))) < (3, 4, 0):
    HAS_REDIS_USERNAME_OPTION = False


def test_redis_data_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_data.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_data_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.set', return_value=True)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert json.loads(out)['value'] == 'baz'
    assert json.loads(out)['msg'] == 'Set key: foo'
    assert json.loads(out)['changed'] is True


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_data_existing_key_nx(capfd, mocker):
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
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert 'value' not in json.loads(out)
    assert json.loads(
        out)['msg'] == 'Could not set key: foo. Key already present.'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_data_non_existing_key_xx(capfd, mocker):
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
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] is None
    assert 'value' not in json.loads(out)
    assert json.loads(
        out)['msg'] == 'Could not set key: foo. Key not present.'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_data_delete_present_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent'})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.delete', return_value=1)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Deleted key: foo'
    assert json.loads(out)['changed'] is True


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_data_delete_absent_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent'})
    mocker.patch('redis.Redis.delete', return_value=0)
    mocker.patch('redis.Redis.get', return_value=None)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Key: foo not present'
    assert json.loads(out)['changed'] is False


@pytest.mark.skipif(HAS_REDIS_USERNAME_OPTION, reason="Redis version > 3.4.0")
def test_redis_data_fail_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     '_ansible_check_mode': False})
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['failed']
    assert json.loads(
        out)['msg'] == 'The option `username` in only supported with redis >= 3.4.0.'


def test_redis_data_key_no_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.set', return_value=True)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert json.loads(out)['value'] == 'baz'
    assert json.loads(out)['msg'] == 'Set key: foo'
    assert json.loads(out)['changed'] is True


def test_redis_delete_key_no_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    mocker.patch('redis.Redis.delete', return_value=1)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Deleted key: foo'
    assert json.loads(out)['changed'] is True


def test_redis_delete_key_non_existent_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'absent',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value=None)
    mocker.patch('redis.Redis.delete', return_value=0)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Key: foo not present'
    assert json.loads(out)['changed'] is False


def test_redis_set_key_check_mode_nochange(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'present',
                     'value': 'bar',
                     '_ansible_check_mode': True})
    mocker.patch('redis.Redis.get', return_value='bar')
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Key foo already has desired value'
    assert json.loads(out)['value'] == 'bar'
    assert not json.loads(out)['changed']
    assert json.loads(out)['old_value'] == 'bar'


def test_redis_set_key_check_mode_delete_nx(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'present',
                     'value': 'baz',
                     '_ansible_check_mode': True})
    mocker.patch('redis.Redis.get', return_value=None)
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Set key: foo'
    assert json.loads(out)['value'] == 'baz'
    assert json.loads(out)['old_value'] is None


def test_redis_set_key_check_mode_delete(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'present',
                     'value': 'baz',
                     '_ansible_check_mode': True})
    mocker.patch('redis.Redis.get', return_value='bar')
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Set key: foo'
    assert json.loads(out)['value'] == 'baz'
    assert json.loads(out)['old_value'] == 'bar'


def test_redis_set_key_check_mode(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'state': 'present',
                     'value': 'baz',
                     '_ansible_check_mode': True})
    mocker.patch('redis.Redis.get', return_value='bar')
    with pytest.raises(SystemExit):
        redis_data.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['msg'] == 'Set key: foo'
    assert json.loads(out)['value'] == 'baz'
    assert json.loads(out)['old_value'] == 'bar'
