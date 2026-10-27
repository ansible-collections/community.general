# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import mail as mail_module


@pytest.fixture
def smtp_classes(mocker):
    smtp_class = mocker.patch.object(mail_module.smtplib, "SMTP")
    smtp_ssl_class = mocker.patch.object(mail_module.smtplib, "SMTP_SSL")
    for cls in (smtp_class, smtp_ssl_class):
        cls.return_value.has_extn.return_value = False
        cls.return_value.sendmail.return_value = {}
    return smtp_class, smtp_ssl_class


@pytest.mark.parametrize(
    "secure, used_index",
    [
        ("never", 0),
        ("always", 1),
    ],
)
def test_single_connection(capfd, smtp_classes, secure, used_index):
    used_class = smtp_classes[used_index]
    unused_class = smtp_classes[1 - used_index]
    args = {
        "host": "mail.example.com",
        "port": 2525,
        "subject": "Test",
        "secure": secure,
    }

    with pytest.raises(SystemExit), set_module_args(args):
        mail_module.main()

    result = json.loads(capfd.readouterr()[0])
    assert result["msg"] == "Mail sent successfully"
    used_class.assert_called_once_with(host="mail.example.com", port=2525, local_hostname=None, timeout=20)
    used_class.return_value.connect.assert_not_called()
    used_class.return_value.sendmail.assert_called_once()
    unused_class.assert_not_called()
