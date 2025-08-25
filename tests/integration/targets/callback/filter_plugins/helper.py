# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import difflib


def callback_results_extractor(outputs_results):
    return [
        {
            'name': result['test']['name'],
            'output': {
                'diff': list(
                    difflib.unified_diff(
                        result['test']['expected_output'],
                        result['stdout_lines'],
                        fromfile="expected",
                        tofile="got",
                    )
                ),
                'expected': result['test']['expected_output'],
                'got': result['stdout_lines'],
            },
        }
        for result in outputs_results
    ]


class FilterModule:
    ''' Jinja2 compat filters '''

    def filters(self):
        return {
            'callback_results_extractor': callback_results_extractor,
        }
