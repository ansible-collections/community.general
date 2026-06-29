# Copyright (c) 2025, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Felix Fontein (@felixfontein)
name: tasks_only
type: stdout
version_added: 11.1.0
short_description: Only show tasks
description:
  - Removes play start and stats marker from P(ansible.builtin.default#callback)'s output.
  - Can be used to generate output for documentation examples.
    For this, the O(number_of_columns) option should be set to an explicit value.
extends_documentation_fragment:
  - ansible.builtin.default_callback
  - ansible.builtin.result_format_callback
options:
  number_of_columns:
    description:
      - Sets the number of columns for Ansible's display.
    type: int
    env:
      - name: ANSIBLE_COLLECTIONS_TASKS_ONLY_NUMBER_OF_COLUMNS
  result_format:
    # Part of the ansible.builtin.result_format_callback doc fragment
    version_added: 11.2.0
  pretty_results:
    # Part of the ansible.builtin.result_format_callback doc fragment
    version_added: 11.2.0
"""

EXAMPLES = r"""
---
# Enable callback in ansible.cfg:
ansible_config: |-
  [defaults]
  stdout_callback = community.general.tasks_only

---
# Enable callback with environment variables:
environment_variable: |-
  ANSIBLE_STDOUT_CALLBACK=community.general.tasks_only
"""

from ansible.plugins.callback.default import CallbackModule as Default


class CallbackModule(Default):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "community.general.tasks_only"

    def v2_playbook_on_play_start(self, play):
        pass

    def v2_playbook_on_stats(self, stats):
        pass

    def set_options(self, *args, **kwargs):
        result = super().set_options(*args, **kwargs)
        self.number_of_columns = self.get_option("number_of_columns")
        if self.number_of_columns is not None:
            self._display.columns = self.number_of_columns
        return result
