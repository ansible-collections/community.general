
# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest


from ansible_collections.community.general.plugins.modules import scaleway_private_network
from ansible_collections.community.general.plugins.module_utils.scaleway import Scaleway, Response
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch


def response_with_zero_network():
    info = {"status": 200,
            "body": '{ "private_networks": [], "total_count": 0}'
            }
    return Response(None, info)


def response_with_new_network():
    info = {"status": 200,
            "body": ('{ "private_networks": [{'
                     '"id": "c123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"name": "new_network_name",'
                     '"tags": ["tag1"]'
                     '}], "total_count": 1}'
                     )
            }
    return Response(None, info)


def response_create_new():
    info = {"status": 200,
            "body": ('{"id": "c123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"name": "anoter_network",'
                     '"organization_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"project_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"zone": "fr-par-2",'
                     '"tags": ["tag1"],'
                     '"created_at": "2019-04-18T15:27:24.177854Z",'
                     '"updated_at": "2019-04-18T15:27:24.177854Z"}'
                     )
            }
    return Response(None, info)


def response_create_new_newtag():
    info = {"status": 200,
            "body": ('{"id": "c123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"name": "anoter_network",'
                     '"organization_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"project_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",'
                     '"zone": "fr-par-2",'
                     '"tags": ["newtag"],'
                     '"created_at": "2019-04-18T15:27:24.177854Z",'
                     '"updated_at": "2020-01-18T15:27:24.177854Z"}'
                     )
            }
    return Response(None, info)


def response_delete():
    info = {"status": 204}
    return Response(None, info)


def test_scaleway_private_network_without_arguments(capfd):
    with set_module_args({}):
        with pytest.raises(SystemExit) as results:
            scaleway_private_network.main()
    out, err = capfd.readouterr()

    assert not err
    assert json.loads(out)['failed']


def test_scaleway_create_pn(capfd):
    with set_module_args({
        "state": "present",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par2",
        "name": "new_network_name",
        "tags": ["tag1"]
    }):

        os.environ['SCW_API_TOKEN'] = 'notrealtoken'
        with patch.object(Scaleway, 'get') as mock_scw_get:
            mock_scw_get.return_value = response_with_zero_network()
            with patch.object(Scaleway, 'post') as mock_scw_post:
                mock_scw_post.return_value = response_create_new()
                with pytest.raises(SystemExit) as results:
                    scaleway_private_network.main()
        mock_scw_post.assert_any_call(path='private-networks/', data={'name': 'new_network_name',
                                                                      'project_id': 'a123b4cd-ef5g-678h-90i1-jk2345678l90',
                                                                      'tags': ['tag1']})
    mock_scw_get.assert_any_call('private-networks', params={'name': 'new_network_name', 'order_by': 'name_asc', 'page': 1, 'page_size': 10})

    out, err = capfd.readouterr()
    del os.environ['SCW_API_TOKEN']


def test_scaleway_existing_pn(capfd):
    with set_module_args({
        "state": "present",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par2",
        "name": "new_network_name",
        "tags": ["tag1"]
    }):

        os.environ['SCW_API_TOKEN'] = 'notrealtoken'
        with patch.object(Scaleway, 'get') as mock_scw_get:
            mock_scw_get.return_value = response_with_new_network()
            with pytest.raises(SystemExit) as results:
                scaleway_private_network.main()
    mock_scw_get.assert_any_call('private-networks', params={'name': 'new_network_name', 'order_by': 'name_asc', 'page': 1, 'page_size': 10})

    out, err = capfd.readouterr()
    del os.environ['SCW_API_TOKEN']

    assert not err
    assert not json.loads(out)['changed']


def test_scaleway_add_tag_pn(capfd):
    with set_module_args({
        "state": "present",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par2",
        "name": "new_network_name",
        "tags": ["newtag"]
    }):

        os.environ['SCW_API_TOKEN'] = 'notrealtoken'
        with patch.object(Scaleway, 'get') as mock_scw_get:
            mock_scw_get.return_value = response_with_new_network()
            with patch.object(Scaleway, 'patch') as mock_scw_patch:
                mock_scw_patch.return_value = response_create_new_newtag()
                with pytest.raises(SystemExit) as results:
                    scaleway_private_network.main()
            mock_scw_patch.assert_any_call(path='private-networks/c123b4cd-ef5g-678h-90i1-jk2345678l90', data={'name': 'new_network_name', 'tags': ['newtag']})
    mock_scw_get.assert_any_call('private-networks', params={'name': 'new_network_name', 'order_by': 'name_asc', 'page': 1, 'page_size': 10})

    out, err = capfd.readouterr()
    del os.environ['SCW_API_TOKEN']

    assert not err
    assert json.loads(out)['changed']


def test_scaleway_remove_pn(capfd):
    with set_module_args({
        "state": "absent",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par2",
        "name": "new_network_name",
        "tags": ["newtag"]
    }):

        os.environ['SCW_API_TOKEN'] = 'notrealtoken'
        with patch.object(Scaleway, 'get') as mock_scw_get:
            mock_scw_get.return_value = response_with_new_network()
            with patch.object(Scaleway, 'delete') as mock_scw_delete:
                mock_scw_delete.return_value = response_delete()
                with pytest.raises(SystemExit) as results:
                    scaleway_private_network.main()
        mock_scw_delete.assert_any_call('private-networks/c123b4cd-ef5g-678h-90i1-jk2345678l90')
    mock_scw_get.assert_any_call('private-networks', params={'name': 'new_network_name', 'order_by': 'name_asc', 'page': 1, 'page_size': 10})

    out, err = capfd.readouterr()
    del os.environ['SCW_API_TOKEN']

    assert not err
    assert json.loads(out)['changed']


def test_scaleway_absent_pn_not_exists(capfd):
    with set_module_args({
        "state": "absent",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par2",
        "name": "new_network_name",
        "tags": ["newtag"]
    }):

        os.environ['SCW_API_TOKEN'] = 'notrealtoken'
        with patch.object(Scaleway, 'get') as mock_scw_get:
            mock_scw_get.return_value = response_with_zero_network()
            with pytest.raises(SystemExit) as results:
                scaleway_private_network.main()
    mock_scw_get.assert_any_call('private-networks', params={'name': 'new_network_name', 'order_by': 'name_asc', 'page': 1, 'page_size': 10})

    out, err = capfd.readouterr()
    del os.environ['SCW_API_TOKEN']

    assert not err
    assert not json.loads(out)['changed']
