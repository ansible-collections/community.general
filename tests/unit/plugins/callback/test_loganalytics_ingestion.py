# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import time
import unittest
import unittest.mock
import urllib

from ansible.executor.task_result import TaskResult

from ansible_collections.community.general.plugins.callback.loganalytics_ingestion import (
    AzureLogAnalyticsIngestionSource,
)


class TestAzureLogAnalyticsIngestion(unittest.TestCase):
    dce_url = "https://fake.dce_url.ansible.com"
    dcr_id = "fake-dcr-id"
    client_id = "fake-client_id"
    client_secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    stream_name = "fake-stream-name"
    fake_access_token = None

    def setUp(self):
        self.fake_access_token = json.dumps(
            {"expires_in": time.time() + 3600, "access_token": "fake_access_token"}
        ).encode("utf-8")

    @unittest.mock.patch(
        "ansible_collections.community.general.plugins.callback.loganalytics_ingestion.open_url", autospec=True
    )
    @unittest.mock.patch("ansible.executor.task_result.TaskResult")
    def test_sending_data(self, task_result_mock, open_url_mock):
        """
        Tests sending data by verifying that the expected POST requests are submitted to the expected hosts.
        """
        # The data returned from 'open_url' is only ever read during authentication.
        open_url_mock.return_value.read.return_value = self.fake_access_token

        # TODO: How to set plugin default arguments?
        #       I tried instantiating the 'CallbackModule' but all it ever did was complain that 'client_id' wasn't defined.
        self.loganalytics = AzureLogAnalyticsIngestionSource(
            self.dce_url,
            self.dcr_id,
            3,
            True,
            self.client_id,
            self.client_secret,
            self.tenant_id,
            self.stream_name,
            False,
            False,
            2,
            "community.general.loganalytics_ingestion",
        )

        assert open_url_mock.call_count == 1
        url = urllib.parse.urlparse(open_url_mock.call_args_list[0][0][0])
        assert url.netloc == "login.microsoftonline.com"

        results = ["foo", "bar", "biz"]
        for i, result in enumerate(results, start=1):
            host_mock = unittest.mock.Mock("host_mock")
            host_mock.name = "fake-name"
            task_mock = unittest.mock.Mock("task_mock")
            task_mock._role = "fake-role"
            task_mock.get_name = lambda r=result: r

            task_result = TaskResult(
                host=host_mock, task=task_mock, return_data={}, task_fields={"action": "fake-action", "args": {}}
            )
            self.loganalytics.send_to_loganalytics("fake-playbook", task_result, "OK")

            assert open_url_mock.call_count == 1 + i

            url = urllib.parse.urlparse(open_url_mock.call_args_list[i][0][0])
            assert url.scheme + "://" + url.netloc == self.dce_url

            assert json.loads(open_url_mock.call_args_list[i].kwargs.get("data"))[0].get("TaskName") == result
