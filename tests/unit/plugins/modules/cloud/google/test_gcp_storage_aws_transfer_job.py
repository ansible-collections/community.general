# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest

from ansible_collections.community.general.plugins.modules.cloud.google.gcp_storage_aws_transfer_job import _validate_params


class TestParmeters(unittest.TestCase):
    """Unit tests for gcp_storage_aws_transfer_job module."""

    failure_message = "Incorrect format. Date and Times must be formatted as YYYY/MM/DD and HH:SS"

    def test_validate_params_pass(self):
        params_dict = {
            'scheduled_start_date_utc': '2020/01/01',
            'scheduled_end_date_utc': '2099/01/01',
            'scheduled_start_time_utc': '22:35'
        }

        actual = _validate_params(params_dict)
        self.assertEqual((True, ''), actual)

    def test_validate_params_fail_date(self):
        params_dict = {
            'scheduled_start_date_utc': '2020/011/01',
            'scheduled_end_date_utc': '2099/01/01',
            'scheduled_start_time_utc': '22:35'
        }

        try:
            _validate_params(params_dict)
        except Exception as e:
            self.assertEqual(self.failure_message, str(e))

    def test_validate_params_fail_time(self):
        params_dict = {
            'scheduled_start_date_utc': '2020/01/01',
            'scheduled_end_date_utc': '2099/01/01',
            'scheduled_start_time_utc': '22:135'
        }

        try:
            _validate_params(params_dict)
        except Exception as e:
            self.assertEqual(self.failure_message, str(e))
