# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
import json
from unittest.mock import patch

import pytest

from ansible_collections.community.general.plugins.modules import scaleway_compute_private_network
from ansible_collections.community.general.plugins.module_utils.scaleway import Scaleway, Response
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args


def response_without_nics():
    info = {"status": 200, "body": '{ "private_nics": []}'}
    return Response(None, info)


def response_with_nics():
    info = {
        "status": 200,
        "body": (
            '{ "private_nics": [{'
            '"id": "c123b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"private_network_id": "b589b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"server_id": "c004b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"mac_address": "02:00:00:00:12:23",'
            '"state": "available",'
            '"creation_date": "2022-03-30T06:25:28.155973+00:00",'
            '"modification_date": "2022-03-30T06:25:28.155973+00:00",'
            '"zone": "fr-par-1"'
            "}]}"
        ),
    }
    return Response(None, info)


def response_when_add_nics():
    info = {
        "status": 200,
        "body": (
            '{ "private_nics": {'
            '"id": "c123b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"private_network_id": "b589b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"server_id": "c004b4cd-ef5g-678h-90i1-jk2345678l90",'
            '"mac_address": "02:00:00:00:12:23",'
            '"state": "available",'
            '"creation_date": "2022-03-30T06:25:28.155973+00:00",'
            '"modification_date": "2022-03-30T06:25:28.155973+00:00",'
            '"zone": "fr-par-1"'
            "}}"
        ),
    }
    return Response(None, info)


def response_remove_nics():
    info = {"status": 200}
    return Response(None, info)


def test_scaleway_private_network_without_arguments(capfd):
    with set_module_args({}):
        with pytest.raises(SystemExit):
            scaleway_compute_private_network.main()
    out, err = capfd.readouterr()

    assert not err
    assert json.loads(out)["failed"]


def test_scaleway_add_nic(capfd):
    os.environ["SCW_API_TOKEN"] = "notrealtoken"
    pnid = "b589b4cd-ef5g-678h-90i1-jk2345678l90"
    cid = "c004b4cd-ef5g-678h-90i1-jk2345678l90"
    url = f"servers/{cid}/private_nics"

    with set_module_args(
        {
            "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
            "state": "present",
            "region": "par1",
            "compute_id": cid,
            "private_network_id": pnid,
        }
    ):
        with patch.object(Scaleway, "get") as mock_scw_get:
            mock_scw_get.return_value = response_without_nics()
            with patch.object(Scaleway, "post") as mock_scw_post:
                mock_scw_post.return_value = response_when_add_nics()
                with pytest.raises(SystemExit):
                    scaleway_compute_private_network.main()
            mock_scw_post.assert_any_call(path=url, data={"private_network_id": pnid})
        mock_scw_get.assert_any_call(url)

    out, err = capfd.readouterr()
    del os.environ["SCW_API_TOKEN"]
    assert not err
    assert json.loads(out)["changed"]


def test_scaleway_add_existing_nic(capfd):
    os.environ["SCW_API_TOKEN"] = "notrealtoken"
    pnid = "b589b4cd-ef5g-678h-90i1-jk2345678l90"
    cid = "c004b4cd-ef5g-678h-90i1-jk2345678l90"
    url = f"servers/{cid}/private_nics"

    with set_module_args(
        {
            "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
            "state": "present",
            "region": "par1",
            "compute_id": cid,
            "private_network_id": pnid,
        }
    ):
        with patch.object(Scaleway, "get") as mock_scw_get:
            mock_scw_get.return_value = response_with_nics()
            with pytest.raises(SystemExit):
                scaleway_compute_private_network.main()
        mock_scw_get.assert_any_call(url)

    out, err = capfd.readouterr()
    del os.environ["SCW_API_TOKEN"]
    assert not err
    assert not json.loads(out)["changed"]


def test_scaleway_remove_existing_nic(capfd):
    os.environ["SCW_API_TOKEN"] = "notrealtoken"
    pnid = "b589b4cd-ef5g-678h-90i1-jk2345678l90"
    cid = "c004b4cd-ef5g-678h-90i1-jk2345678l90"
    nicid = "c123b4cd-ef5g-678h-90i1-jk2345678l90"
    url = f"servers/{cid}/private_nics"
    urlremove = f"servers/{cid}/private_nics/{nicid}"

    with set_module_args(
        {
            "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
            "state": "absent",
            "region": "par1",
            "compute_id": cid,
            "private_network_id": pnid,
        }
    ):
        with patch.object(Scaleway, "get") as mock_scw_get:
            mock_scw_get.return_value = response_with_nics()
            with patch.object(Scaleway, "delete") as mock_scw_delete:
                mock_scw_delete.return_value = response_remove_nics()
                with pytest.raises(SystemExit):
                    scaleway_compute_private_network.main()
            mock_scw_delete.assert_any_call(urlremove)
        mock_scw_get.assert_any_call(url)

    out, err = capfd.readouterr()

    del os.environ["SCW_API_TOKEN"]
    assert not err
    assert json.loads(out)["changed"]


def test_scaleway_remove_absent_nic(capfd):
    os.environ["SCW_API_TOKEN"] = "notrealtoken"
    pnid = "b589b4cd-ef5g-678h-90i1-jk2345678l90"
    cid = "c004b4cd-ef5g-678h-90i1-jk2345678l90"
    url = f"servers/{cid}/private_nics"

    with set_module_args(
        {
            "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
            "state": "absent",
            "region": "par1",
            "compute_id": cid,
            "private_network_id": pnid,
        }
    ):
        with patch.object(Scaleway, "get") as mock_scw_get:
            mock_scw_get.return_value = response_without_nics()
            with pytest.raises(SystemExit):
                scaleway_compute_private_network.main()
        mock_scw_get.assert_any_call(url)

    out, err = capfd.readouterr()
    del os.environ["SCW_API_TOKEN"]
    assert not err
    assert not json.loads(out)["changed"]
