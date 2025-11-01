# Copyright (c) 2024, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: default_without_diff
type: stdout
short_description: The default ansible callback without diff output
version_added: 8.4.0
description:
  - This is basically the default ansible callback plugin (P(ansible.builtin.default#callback)) without showing diff output.
    This can be useful when using another callback which sends more detailed information to another service, like the L(ARA,
    https://ara.recordsansible.org/) callback, and you want diff output sent to that plugin but not shown on the console output.
author: Felix Fontein (@felixfontein)
extends_documentation_fragment:
  - ansible.builtin.default_callback
  - ansible.builtin.result_format_callback
"""

EXAMPLES = r"""
# Enable callback in ansible.cfg:
ansible_config: |
  [defaults]
  stdout_callback = community.general.default_without_diff

# Enable callback with environment variables:
environment_variable: |-
  ANSIBLE_STDOUT_CALLBACK=community.general.default_without_diff
"""

from ansible.plugins.callback.default import CallbackModule as Default


class CallbackModule(Default):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "community.general.default_without_diff"

    def v2_on_file_diff(self, result):
        pass
