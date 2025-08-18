# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import difflib

from ansible.module_utils.six import string_types


def callback_results_extractor(outputs_results):
    results = []
    for result in outputs_results:
        differences = []
        expected_output = result['test']['expected_output']
        stdout_lines = result['stdout_lines']
        results.append({
            'name': result['test']['name'],
            'diff': list(
                difflib.unified_diff(
                    expected_output,
                    stdout_lines,
                    fromfile="expected",
                    tofile="found",
                )
            )
        })
    return results


class FilterModule:
    ''' Jinja2 compat filters '''

    def filters(self):
        return {
            'callback_results_extractor': callback_results_extractor,
        }
