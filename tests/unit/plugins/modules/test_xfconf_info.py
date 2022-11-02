# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.plugins.modules import xfconf_info

import pytest

TESTED_MODULE = xfconf_info.__name__


@pytest.fixture
def patch_xfconf_info(mocker):
    """
    Function used for mocking some parts of redhat_subscription module
    """
    mocker.patch('ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.get_bin_path',
                 return_value='/testbin/xfconf-query')


TEST_CASES = [
    [
        {'channel': 'xfwm4', 'property': '/general/inactive_opacity'},
        {
            'id': 'test_simple_property_get',
            'run_command.calls': [
                (
                    # Calling of following command will be asserted
                    ['/testbin/xfconf-query', '--channel', 'xfwm4', '--property', '/general/inactive_opacity'],
                    # Was return code checked?
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    # Mock of returned code, stdout and stderr
                    (0, '100\n', '',),
                ),
            ],
            'is_array': False,
            'value': '100',
        }
    ],
    [
        {'channel': 'xfwm4', 'property': '/general/i_dont_exist'},
        {
            'id': 'test_simple_property_get_nonexistent',
            'run_command.calls': [
                (
                    # Calling of following command will be asserted
                    ['/testbin/xfconf-query', '--channel', 'xfwm4', '--property', '/general/i_dont_exist'],
                    # Was return code checked?
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    # Mock of returned code, stdout and stderr
                    (1, '', 'Property "/general/i_dont_exist" does not exist on channel "xfwm4".\n',),
                ),
            ],
            'is_array': False,
        }
    ],
    [
        {'property': '/general/i_dont_exist'},
        {
            'id': 'test_property_no_channel',
            'run_command.calls': [],
        }
    ],
    [
        {'channel': 'xfwm4', 'property': '/general/workspace_names'},
        {
            'id': 'test_property_get_array',
            'run_command.calls': [
                (
                    # Calling of following command will be asserted
                    ['/testbin/xfconf-query', '--channel', 'xfwm4', '--property', '/general/workspace_names'],
                    # Was return code checked?
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    # Mock of returned code, stdout and stderr
                    (0, 'Value is an array with 3 items:\n\nMain\nWork\nTmp\n', '',),
                ),
            ],
            'is_array': True,
            'value_array': ['Main', 'Work', 'Tmp'],
        },
    ],
    [
        {},
        {
            'id': 'get_channels',
            'run_command.calls': [
                (
                    # Calling of following command will be asserted
                    ['/testbin/xfconf-query', '--list'],
                    # Was return code checked?
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    # Mock of returned code, stdout and stderr
                    (0, 'Channels:\n  a\n  b\n  c\n', '',),
                ),
            ],
            'is_array': False,
            'channels': ['a', 'b', 'c'],
        },
    ],
    [
        {'channel': 'xfwm4'},
        {
            'id': 'get_properties',
            'run_command.calls': [
                (
                    # Calling of following command will be asserted
                    ['/testbin/xfconf-query', '--list', '--channel', 'xfwm4'],
                    # Was return code checked?
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    # Mock of returned code, stdout and stderr
                    (0, '/general/wrap_cycle\n/general/wrap_layout\n/general/wrap_resistance\n/general/wrap_windows\n'
                        '/general/wrap_workspaces\n/general/zoom_desktop\n', '',),
                ),
            ],
            'is_array': False,
            'properties': [
                '/general/wrap_cycle',
                '/general/wrap_layout',
                '/general/wrap_resistance',
                '/general/wrap_windows',
                '/general/wrap_workspaces',
                '/general/zoom_desktop',
            ],
        },
    ],
]
TEST_CASES_IDS = [item[1]['id'] for item in TEST_CASES]


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         TEST_CASES,
                         ids=TEST_CASES_IDS,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_xfconf_info(mocker, capfd, patch_xfconf_info, testcase):
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
        xfconf_info.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("testcase =\n%s" % testcase)
    print("results =\n%s" % results)

    for conditional_test_result in ('value_array', 'value', 'is_array', 'properties', 'channels'):
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
