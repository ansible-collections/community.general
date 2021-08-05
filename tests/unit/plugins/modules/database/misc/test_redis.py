# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
__metaclass__ = type


import pytest
import json
import redis

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock
from ansible_collections.community.general.plugins.module_utils import redis
from ansible_collections.community.general.plugins.modules.database.misc import redis_set, redis_incr, redis_data_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def test_redis_set_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_set.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


def test_redis_set_check_mode(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'value': 'baz',
                     '_ansible_check_mode': True})
    mocker.patch(
        'redis.Redis.get',
        return_value='bar'
    )
    with pytest.raises(SystemExit):
        redis_set.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['old_value'] == 'bar'
    assert json.loads(
        out)['msg'] == 'Key: foo had value: bar now has value baz'
    assert not json.loads(out)['changed'] is True


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


def test_redis_incr_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_incr.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


def test_redis_incr(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo', })
    mocker.patch('redis.Redis.incr', return_value=57)
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['value'] == '57'
    assert json.loads(
        out)['msg'] == 'Incremented key: foo to 57'
    assert json.loads(out)['changed'] is True


def test_redis_incrby(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment': 10})
    mocker.patch('redis.Redis.incrby', return_value=57)
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['value'] == '57'
    assert json.loads(
        out)['msg'] == 'Incremented key: foo by 10 to 57'
    assert json.loads(out)['changed'] is True


def test_redis_incrbyfloat(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment': '5.5'})
    mocker.patch('redis.Redis.incrbyfloat', return_value=57.45)
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['value'] == '57.45'
    assert json.loads(
        out)['msg'] == 'Incremented key: foo by 5.5 to 57.45'
    assert json.loads(out)['changed'] is True


def test_redis_incrby_wrong_value(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment': 'not_a_number'})
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(
        out)['msg'] == 'Increment: not_a_number is not a number'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


def test_redis_data_info_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_data_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']
