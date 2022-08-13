# Author: Alexei Znamensky (russoz@gmail.com)
# Largely adapted from test_redhat_subscription by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.plugins.modules.packaging.language import cpanm

import pytest

TESTED_MODULE = cpanm.__name__


@pytest.fixture
def patch_cpanm(mocker):
    """
    Function used for mocking some parts of redhat_subscription module
    """
    mocker.patch('ansible_collections.community.general.plugins.module_utils.module_helper.AnsibleModule.get_bin_path',
                 return_value='/testbin/cpanm')


TEST_CASES = [
    [
        {'name': 'Dancer'},
        {
            'id': 'install_dancer_compatibility',
            'run_command.calls': [
                (
                    ['perl', '-le', 'use Dancer;'],
                    {'environ_update': {}, 'check_rc': False},
                    (2, '', 'error, not installed',),  # output rc, out, err
                ),
                (
                    ['/testbin/cpanm', 'Dancer'],
                    {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                    (0, '', '',),  # output rc, out, err
                ),
            ],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer'},
        {
            'id': 'install_dancer_already_installed_compatibility',
            'run_command.calls': [
                (
                    ['perl', '-le', 'use Dancer;'],
                    {'environ_update': {}, 'check_rc': False},
                    (0, '', '',),  # output rc, out, err
                ),
            ],
            'changed': False,
        }
    ],
    [
        {'name': 'Dancer', 'mode': 'new'},
        {
            'id': 'install_dancer',
            'run_command.calls': [(
                ['/testbin/cpanm', 'Dancer'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'MIYAGAWA/Plack-0.99_05.tar.gz'},
        {
            'id': 'install_distribution_file_compatibility',
            'run_command.calls': [(
                ['/testbin/cpanm', 'MIYAGAWA/Plack-0.99_05.tar.gz'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'MIYAGAWA/Plack-0.99_05.tar.gz', 'mode': 'new'},
        {
            'id': 'install_distribution_file',
            'run_command.calls': [(
                ['/testbin/cpanm', 'MIYAGAWA/Plack-0.99_05.tar.gz'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'locallib': '/srv/webapps/my_app/extlib', 'mode': 'new'},
        {
            'id': 'install_into_locallib',
            'run_command.calls': [(
                ['/testbin/cpanm', '--local-lib', '/srv/webapps/my_app/extlib', 'Dancer'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'from_path': '/srv/webapps/my_app/src/', 'mode': 'new'},
        {
            'id': 'install_from_local_directory',
            'run_command.calls': [(
                ['/testbin/cpanm', '/srv/webapps/my_app/src/'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'locallib': '/srv/webapps/my_app/extlib', 'notest': True, 'mode': 'new'},
        {
            'id': 'install_into_locallib_no_unit_testing',
            'run_command.calls': [(
                ['/testbin/cpanm', '--notest', '--local-lib', '/srv/webapps/my_app/extlib', 'Dancer'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'mirror': 'http://cpan.cpantesters.org/', 'mode': 'new'},
        {
            'id': 'install_from_mirror',
            'run_command.calls': [(
                ['/testbin/cpanm', '--mirror', 'http://cpan.cpantesters.org/', 'Dancer'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'system_lib': True, 'mode': 'new'},
        {
            'id': 'install_into_system_lib',
            'run_command.calls': [],
            'changed': False,
            'failed': True,
        }
    ],
    [
        {'name': 'Dancer', 'version': '1.0', 'mode': 'new'},
        {
            'id': 'install_minversion_implicit',
            'run_command.calls': [(
                ['/testbin/cpanm', 'Dancer~1.0'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'version': '~1.5', 'mode': 'new'},
        {
            'id': 'install_minversion_explicit',
            'run_command.calls': [(
                ['/testbin/cpanm', 'Dancer~1.5'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
        }
    ],
    [
        {'name': 'Dancer', 'version': '@1.7', 'mode': 'new'},
        {
            'id': 'install_specific_version',
            'run_command.calls': [(
                ['/testbin/cpanm', 'Dancer@1.7'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
            'failed': False,
        }
    ],
    [
        {'name': 'MIYAGAWA/Plack-0.99_05.tar.gz', 'version': '@1.7', 'mode': 'new'},
        {
            'id': 'install_specific_version_from_file_error',
            'run_command.calls': [],
            'changed': False,
            'failed': True,
            'msg': "parameter 'version' must not be used when installing from a file",
        }
    ],
    [
        {'from_path': '~/', 'version': '@1.7', 'mode': 'new'},
        {
            'id': 'install_specific_version_from_directory_error',
            'run_command.calls': [],
            'changed': False,
            'failed': True,
            'msg': "parameter 'version' must not be used when installing from a directory",
        }
    ],
    [
        {'name': 'git://github.com/plack/Plack.git', 'version': '@1.7', 'mode': 'new'},
        {
            'id': 'install_specific_version_from_git_url_explicit',
            'run_command.calls': [(
                ['/testbin/cpanm', 'git://github.com/plack/Plack.git@1.7'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
            'failed': False,
        }
    ],
    [
        {'name': 'git://github.com/plack/Plack.git', 'version': '2.5', 'mode': 'new'},
        {
            'id': 'install_specific_version_from_git_url_implicit',
            'run_command.calls': [(
                ['/testbin/cpanm', 'git://github.com/plack/Plack.git@2.5'],
                {'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': True},
                (0, '', '',),  # output rc, out, err
            )],
            'changed': True,
            'failed': False,
        }
    ],
    [
        {'name': 'git://github.com/plack/Plack.git', 'version': '~2.5', 'mode': 'new'},
        {
            'id': 'install_version_operator_from_git_url_error',
            'run_command.calls': [],
            'changed': False,
            'failed': True,
            'msg': "operator '~' not allowed in version parameter when installing from git repository",
        }
    ],
]
TEST_CASES_IDS = [item[1]['id'] for item in TEST_CASES]


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         TEST_CASES,
                         ids=TEST_CASES_IDS,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_cpanm(mocker, capfd, patch_cpanm, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    # Mock function used for running commands first
    call_results = [item[2] for item in testcase['run_command.calls']]
    mock_run_command = mocker.patch(
        'ansible_collections.community.general.plugins.module_utils.module_helper.AnsibleModule.run_command',
        side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        cpanm.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("results =\n%s" % results)

    assert mock_run_command.call_count == len(testcase['run_command.calls'])
    if mock_run_command.call_count:
        call_args_list = [(item[0][0], item[1]) for item in mock_run_command.call_args_list]
        expected_call_args_list = [(item[0], item[1]) for item in testcase['run_command.calls']]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)
        assert call_args_list == expected_call_args_list

    assert results.get('changed', False) == testcase['changed']
    if 'failed' in testcase:
        assert results.get('failed', False) == testcase['failed']
    if 'msg' in testcase:
        assert results.get('msg', '') == testcase['msg']
