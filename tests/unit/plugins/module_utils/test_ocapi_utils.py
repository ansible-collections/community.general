# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import re
import shutil
import tempfile
import unittest

from ansible_collections.community.general.plugins.module_utils.ocapi_utils import OcapiUtils


class TestOcapiUtils(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.utils = OcapiUtils(
            creds={"user": "a_user", "pswd": "a_password"},
            base_uri="fakeUri",
            proxy_slot_number=None,
            timeout=30,
            module=None,
        )

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_prepare_multipart_firmware_upload(self):
        # Generate a binary file and save it
        filename = "fake_firmware.bin"
        filepath = os.path.join(self.tempdir, filename)
        file_contents = b"\x00\x01\x02\x03\x04"
        with open(filepath, "wb+") as f:
            f.write(file_contents)

        # Call prepare_mutipart_firmware_upload
        content_type, b_form_data = self.utils.prepare_multipart_firmware_upload(filepath)

        # Check the returned content-type
        content_type_pattern = r"multipart/form-data; boundary=(.*)"
        m = re.match(content_type_pattern, content_type)
        self.assertIsNotNone(m)

        # Check the returned binary data
        boundary = m.group(1)
        expected_content_text = f"--{boundary}\r\n"
        expected_content_text += f'Content-Disposition: form-data; name="FirmwareFile"; filename="{filename}"\r\n'
        expected_content_text += "Content-Type: application/octet-stream\r\n\r\n"
        expected_content_bytes = bytearray(expected_content_text, "utf-8")
        expected_content_bytes += file_contents
        expected_content_bytes += bytearray(f"\r\n--{boundary}--", "utf-8")
        self.assertEqual(expected_content_bytes, b_form_data)
