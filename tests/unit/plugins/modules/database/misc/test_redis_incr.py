# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest
import json
from redis import __version__

from redis.exceptions import RedisError, ResponseError
from ansible_collections.community.general.plugins.modules.database.misc import redis_incr
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


HAS_REDIS_USERNAME_OPTION = True
if tuple(map(int, __version__.split('.'))) < (3, 4, 0):
    HAS_REDIS_USERNAME_OPTION = False


def test_redis_incr_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        redis_incr.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
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


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_increment_int(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment_int': 10})
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


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_increment_float(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment_float': '5.5'})
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


@pytest.mark.skipif(not HAS_REDIS_USERNAME_OPTION, reason="Redis version < 3.4.0")
def test_redis_increment_float_wrong_value(capfd):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment_float': 'not_a_number'})
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(
        out)['msg'] == 'Increment: not_a_number is not a floating point number'
    assert json.loads(out)['changed'] is False
    assert json.loads(out)['failed'] is True


@pytest.mark.skipif(HAS_REDIS_USERNAME_OPTION, reason="Redis version > 3.4.0")
def test_redis_incr_fail_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     '_ansible_check_mode': False})
    with pytest.raises(SystemExit):
        redis_incr.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['failed']
    assert json.loads(
        out)['msg'] == 'The option `username` in only supported with redis >= 3.4.0.'


def test_redis_incr_no_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
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


def test_redis_increment_float_no_username(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_password': 'secret',
                     'key': 'foo',
                     'increment_float': '5.5'})
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
