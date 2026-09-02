# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest import mock

from ansible_collections.community.general.plugins.modules import haproxy
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

STAT_HEADER = (
    "# pxname,svname,qcur,qmax,scur,smax,slim,stot,bin,bout,dreq,dresp,ereq,econ,"
    "eresp,wretr,wredis,status,weight,act,bck,chkfail,chkdown,lastchg,downtime,"
    "qlimit,pid,iid,sid,throttle,lbtot,tracked,type,rate,rate_lim,rate_max,"
)


class FakeSocket:
    def __init__(self, status, scur=0):
        self.status = status
        self.scur = scur
        self.commands = []

    def __call__(self, cmd, timeout=200, capture_output=True):
        self.commands.append(cmd)

        if cmd == "show info":
            return "Name: HAProxy\nVersion: 2.8.0\n"

        if cmd == "show stat":
            rows = [
                STAT_HEADER,
                f"bk_test,srv,0,0,{self.scur},0,,0,0,0,,0,,0,0,0,0,{self.status},1,1,0,0,0,0,0,,1,3,1,,0,,2,0,,0,,,",
                f"bk_test,BACKEND,0,0,{self.scur},0,200,0,0,0,0,0,,0,0,0,0,UP,1,1,0,,0,0,0,,1,3,0,,0,,1,0,,0,,,",
            ]
            return "\n".join(rows) + "\n"

        if "state drain" in cmd and not self.status.startswith("DOWN"):
            self.status = "DRAIN"
        if "disable server" in cmd:
            self.status = "MAINT"
        return ""


class TestHAProxyDrain(ModuleTestCase):
    def run_disable(self, status, scur=0):
        fake = FakeSocket(status, scur)
        args = {
            "state": "disabled",
            "backend": "bk_test",
            "host": "srv",
            "socket": "/var/run/haproxy.sock",
            "drain": True,
            "wait": True,
            "wait_retries": 3,
            "wait_interval": 1,
            "fail_on_not_found": True,
        }
        with set_module_args(args), mock.patch.object(haproxy.HAProxy, "execute", fake):
            try:
                haproxy.main()
            except (AnsibleExitJson, AnsibleFailJson) as exc:
                return fake, exc
            raise AssertionError("the module neither succeeded nor failed")

    def test_down_server_goes_to_maintenance_without_waiting_for_drain(self):
        fake, exc = self.run_disable("DOWN")

        self.assertIsInstance(exc, AnsibleExitJson)
        self.assertEqual(fake.status, "MAINT")

    def test_composite_down_status_is_recognized_as_down(self):
        fake, exc = self.run_disable("DOWN 2/3")

        self.assertIsInstance(exc, AnsibleExitJson)
        self.assertEqual(fake.status, "MAINT")

    def test_running_server_is_still_drained(self):
        fake, exc = self.run_disable("UP")

        self.assertIsInstance(exc, AnsibleExitJson)
        self.assertEqual(fake.status, "MAINT")
        self.assertTrue(any("state drain" in cmd for cmd in fake.commands))

    def test_sessions_in_flight_still_exhaust_the_retries(self):
        fake, exc = self.run_disable("UP", scur=4)

        self.assertIsInstance(exc, AnsibleFailJson)
        self.assertIn("not status 'DRAIN'", exc.args[0]["msg"])
