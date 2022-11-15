# -*- coding: utf-8 -*-
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.plugins.modules import gconftool2

import pytest

TESTED_MODULE = gconftool2.__name__


@pytest.fixture
def patch_gconftool2(mocker):
    """
    Function used for mocking some parts of redhat_subscription module
    """
    mocker.patch('ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.get_bin_path',
                 return_value='/testbin/gconftool-2')


TEST_CASES = [
    [
        {'state': 'get', 'key': '/desktop/gnome/background/picture_filename'},
        {
            'id': 'test_simple_element_get',
            'run_command.calls': [
                (
                    ['/testbin/gconftool-2', '--get', '/desktop/gnome/background/picture_filename'],
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    (0, '100\n', '',),
                ),
            ],
            'new_value': '100',
        }
    ],
    [
        {'state': 'get', 'key': '/desktop/gnome/background/picture_filename'},
        {
            'id': 'test_simple_element_get_not_found',
            'run_command.calls': [
                (
                    ['/testbin/gconftool-2', '--get', '/desktop/gnome/background/picture_filename'],
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    (0, '', "No value set for `/desktop/gnome/background/picture_filename'\n",),
                ),
            ],
            'new_value': None,
        }
    ],
    [
        {'state': 'present', 'key': '/desktop/gnome/background/picture_filename', 'value': '200', 'value_type': 'int'},
        {
            'id': 'test_simple_element_set',
            'run_command.calls': [
                (
                    ['/testbin/gconftool-2', '--get', '/desktop/gnome/background/picture_filename'],
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    (0, '100\n', '',),
                ),
                (
                    ['/testbin/gconftool-2', '--type', 'int', '--set', '/desktop/gnome/background/picture_filename', '200'],
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    (0, '200\n', '',),
                ),
            ],
            'new_value': '200',
        }
    ],
]
TEST_CASES_IDS = [item[1]['id'] for item in TEST_CASES]


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         TEST_CASES,
                         ids=TEST_CASES_IDS,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_gconftool2(mocker, capfd, patch_gconftool2, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    # Mock function used for running commands first
    call_results = [item[2] for item in testcase['run_command.calls']]
    mock_run_command = mocker.patch(
        'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.run_command',
        side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        gconftool2.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("testcase =\n%s" % testcase)
    print("results =\n%s" % results)

    for conditional_test_result in ('value',):
        if conditional_test_result in testcase:
            assert conditional_test_result in results, "'{0}' not found in {1}".format(conditional_test_result, results)
            assert results[conditional_test_result] == testcase[conditional_test_result], \
                "'{0}': '{1}' != '{2}'".format(conditional_test_result, results[conditional_test_result], testcase[conditional_test_result])

    assert mock_run_command.call_count == len(testcase['run_command.calls'])
    if mock_run_command.call_count:
        call_args_list = [(item[0][0], item[1]) for item in mock_run_command.call_args_list]
        expected_call_args_list = [(item[0], item[1]) for item in testcase['run_command.calls']]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)
        assert call_args_list == expected_call_args_list
