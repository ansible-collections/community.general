# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


def callback_results_extractor(outputs_results):
    results = []
    for result in outputs_results:
        differences = []
        expected_output = result['test']['expected_output']
        stdout_lines = result['stdout_lines']
        for i in range(max(len(expected_output), len(stdout_lines))):
            line = "line_%s" % (i + 1)
            test_line = stdout_lines[i] if i < len(stdout_lines) else None
            expected_lines = expected_output[i] if i < len(expected_output) else None
            if not isinstance(expected_lines, str) and expected_lines is not None:
                if test_line not in expected_lines:
                    differences.append({
                        'line': {
                            'expected_one_of': expected_lines,
                            'got': test_line,
                        }
                    })
            else:
                if test_line != expected_lines:
                    differences.append({
                        'line': {
                            'expected': expected_lines,
                            'got': test_line,
                        }
                    })
        results.append({
            'name': result['test']['name'],
            'output': {
                'differences': differences,
                'expected': expected_output,
                'got': stdout_lines,
            },
        })
    return results


class FilterModule:
    ''' Jinja2 compat filters '''

    def filters(self):
        return {
            'callback_results_extractor': callback_results_extractor,
        }
