# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest
import json

from ansible_collections.community.general.plugins.modules.database.misc import (
    redis_data_info)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def test_redis_data_info_without_arguments(capfd):
    set_module_args({})
    with pytest.raises(SystemExit):
        redis_data_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


def test_redis_data_info_existing_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value='bar')
    with pytest.raises(SystemExit):
        redis_data_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['exists'] == True
    assert json.loads(out)['value'] == 'bar'


def test_redis_data_info_absent_key(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_user': 'root',
                     'login_password': 'secret',
                     'key': 'foo',
                     '_ansible_check_mode': False})
    mocker.patch('redis.Redis.get', return_value=None)
    with pytest.raises(SystemExit):
        redis_data_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['exists'] == False
    assert 'value' not in json.loads(out)
