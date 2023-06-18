# -*- coding: utf-8 -*-

# Copyright (c) 2020, Pavlo Bashynskyi (@levonet) <levonet@gmail.com>
# Copyright (c) 2023, Xcelirate (@vicmunoz) <victor1 at teamxcl dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
import json
from redis import __version__

from ansible_collections.community.general.plugins.modules import redis_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


HAS_REDIS_USERNAME_OPTION = True
if tuple(map(int, __version__.split('.'))) < (3, 4, 0):
    HAS_REDIS_USERNAME_OPTION = False


def test_redis_info_with_wrong_argument(capfd):
    set_module_args({'section': 'test_fake'})
    with pytest.raises(SystemExit):
        redis_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['failed']


def test_redis_info_with_fail_client(capfd):
    set_module_args({})
    with pytest.raises(SystemExit):
        redis_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert json.loads(out)['failed']


def test_redis_info_with_params(capfd, mocker):
    set_module_args({'login_host': 'localhost',
                     'login_port': 6379,
                     'login_user': 'user_test',
                     'login_password': 'pass_test',
                     'section': 'cluster'})
    mocker.patch('redis.Redis.info', return_value={'cluster_enabled': 0})
    with pytest.raises(SystemExit):
        redis_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert not json.loads(out)['changed']
    assert json.loads(out)['info'] == {'cluster_enabled': 0}


def test_redis_info_without_params(capfd, mocker):
    set_module_args({})
    mocker.patch('redis.Redis.info', return_value={'test_without_params': 123})
    with pytest.raises(SystemExit):
        redis_info.main()
    out, err = capfd.readouterr()
    print(out)
    assert not err
    assert not json.loads(out)['changed']
    assert json.loads(out)['info'] == {'test_without_params': 123}
