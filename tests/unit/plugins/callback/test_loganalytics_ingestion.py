# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import time
import unittest
import unittest.mock
import urllib

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

    @unittest.mock.patch(
        "ansible_collections.community.general.plugins.callback.loganalytics_ingestion.open_url", autospec=True
    )
    def setUp(self, open_url_mock):
        # Generate a fake access token.
        open_url_mock.return_value.read.return_value = json.dumps(
            {"expires_in": time.time() + 3600, "access_token": "fake_access_token"}
        ).encode("utf-8")

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

    @unittest.mock.patch(
        "ansible_collections.community.general.plugins.callback.loganalytics_ingestion.open_url", autospec=True
    )
    @unittest.mock.patch("json.dumps")
    @unittest.mock.patch("ansible.executor.task_result.TaskResult")
    def test_sending_data(self, task_result_mock, json_dumps_mock, open_url_mock):
        """
        Tests sending data by verifying that the expected POST requests are submitted to the expected hosts.
        """
        # Neither the Mock objects nor its attributes are serializable but we don't care about getting accurate JSON in this case so just return fake JSON data.
        json_dumps_mock.return_value = '{"name": "fake_json"}'

        self.loganalytics.send_to_loganalytics("fake_playbook", task_result_mock(), "OK")
        self.loganalytics.send_to_loganalytics("fake_playbook", task_result_mock(), "FAILED")
        self.loganalytics.send_to_loganalytics("fake_playbook", task_result_mock(), "OK")

        # Validate the three POST requests for sending data (one for each task).
        assert open_url_mock.call_count == 3
        # Three POST requests to the DCE.
        for i in range(0, 2):
            url = urllib.parse.urlparse(open_url_mock.call_args_list[i][0][0])
            assert url.scheme + "://" + url.netloc == self.dce_url
