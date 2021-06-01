# Copyright: (c) 2019, George Rawlinson <george@rawlinson.net.nz>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.modules.packaging.os import pacman_key
import pytest
import json


@pytest.fixture
def patch_pacman_key_calls(mocker):
    get_bin_path = mocker.patch.object(
        AnsibleModule,
        'get_bin_path',
        return_value="/mocked/path",
    )


#
# test invalid user input
#
TEST_FAILING_PARAMS = [
    # state: present, id: absent
    [
        {
            'state': 'present',
        },
        {
            'id': 'state_present_id_missing',
            'msg': 'missing required arguments: id',
        },
    ],
    # state: present, required parameters: missing
    [
        {
            'state': 'present',
            'id': '0xDOESNTMATTER',
        },
        {
            'id': 'state_present_required_param_missing',
            'msg': 'state is present but any of the following are missing: data, file, url, keyserver',
        },
    ],
    # state: present, id: invalid (not full-length)
    [
        {
            # default state: present
            'id': '0xDOESNTMATTER',
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_present_id_invalid',
            'msg': 'identifier is not full-length: DOESNTMATTER',
        },
    ],
    # state: present, fingerprint: invalid (not hexadecimal)
    [
        {
            'state': 'present',
            'id': '01234567890ABCDE01234567890ABCDE12345678',
            'fingerprint': '01234567890ABCDE01234567890ABCDE1234567M',
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_present_fpr_invalid',
            'msg': 'identifier is not hexadecimal: 01234567890ABCDE01234567890ABCDE1234567M',
        },
    ],
    # state: absent, id: absent
    [
        {
            'state': 'absent',
        },
        {
            'id': 'state_absent_id_missing',
            'msg': 'missing required arguments: id',
        },
    ],
]


@pytest.mark.parametrize(
    'patch_ansible_module, expected',
    TEST_FAILING_PARAMS,
    ids=[item[1]['id'] for item in TEST_FAILING_PARAMS],
    indirect=['patch_ansible_module']
)
@pytest.mark.usefixtures('patch_ansible_module')
def test_failing_params(mocker, capfd, patch_pacman_key_calls, expected):
    # invoke module
    with pytest.raises(SystemExit):
        pacman_key.main()

    # capture std{out,err}
    out, err = capfd.readouterr()
    results = json.loads(out)
    print(results)

    # assertion time!
    assert 'failed' in results
    if 'msg' in results:
        assert results['msg'] == expected['msg']


#
# test normal operation
#
TEST_CASES = [
    # check mode: state & key present
    [
        {
            'state': 'present',
            'id': '14F26682D0916CDD81E37B6D61B7B526D98F0353',
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_and_key_present',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '14F26682D0916CDD81E37B6D61B7B526D98F0353',
                    ],
                    {'check_rc': False},
                    (
                        0,
                        '''
tru::1:1616373715:0:3:1:5
pub:-:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23::0:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:-::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>::::::::::0:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
''',
                        '',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # check mode: state present, key absent
    [
        {
            'state': 'present',
            'id': '01234567890ABCDE01234567890ABCDE12345678',
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_present_key_absent',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '01234567890ABCDE01234567890ABCDE12345678',
                    ],
                    {'check_rc': False},
                    (
                        2,
                        '',
                        '''
                        gpg: error reading key: No public key
                        tru::1:1616373715:0:3:1:5
                        ''',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # check mode: state & key absent
    [
        {
            'state': 'absent',
            'id': '01234567890ABCDE01234567890ABCDE12345678',
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_and_key_absent',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '01234567890ABCDE01234567890ABCDE12345678',
                    ],
                    {'check_rc': False},
                    (
                        2,
                        '',
                        '''
                        gpg: error reading key: No public key
                        tru::1:1616373715:0:3:1:5
                        ''',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # check mode: state absent, key present
    [
        {
            'state': 'absent',
            'id': '14F26682D0916CDD81E37B6D61B7B526D98F0353',
            '_ansible_check_mode': True,
        },
        {
            'id': 'check_mode_state_absent_key_present',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '14F26682D0916CDD81E37B6D61B7B526D98F0353',
                    ],
                    {'check_rc': False},
                    (
                        0,
                        '''
tru::1:1616373715:0:3:1:5
pub:-:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23::0:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:-::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>::::::::::0:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
                        ''',
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # state & key present
    [
        {
            'state': 'present',
            'id': '14F26682D0916CDD81E37B6D61B7B526D98F0353',
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_and_key_present',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '14F26682D0916CDD81E37B6D61B7B526D98F0353',
                    ],
                    {'check_rc': False},
                    (
                        0,
                        '''
tru::1:1616373715:0:3:1:5
pub:-:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23::0:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:-::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>::::::::::0:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
''',
                        '',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # state absent, key present
    [
        {
            'state': 'absent',
            'id': '14F26682D0916CDD81E37B6D61B7B526D98F0353',
        },
        {
            'id': 'state_absent_key_present',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '14F26682D0916CDD81E37B6D61B7B526D98F0353',
                    ],
                    {'check_rc': False},
                    (
                        0,
                        '''
tru::1:1616373715:0:3:1:5
pub:-:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23::0:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:-::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>::::::::::0:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
''',
                        '',
                    ),
                ),
                (
                    [
                        '/mocked/path',
                        '--gpgdir',
                        '/etc/pacman.d/gnupg',
                        '--delete',
                        '14F26682D0916CDD81E37B6D61B7B526D98F0353',
                    ],
                    {'check_rc': True},
                    (
                        0,
                        '''
                        ==> Updating trust database...
                        gpg: next trustdb check due at 2021-08-02
                        ''',
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # state & key absent
    [
        {
            'state': 'absent',
            'id': '01234567890ABCDE01234567890ABCDE12345678',
        },
        {
            'id': 'state_and_key_absent',
            'run_command.calls': [
                (
                    [
                        '/mocked/path',
                        '--with-colons',
                        '--batch',
                        '--no-tty',
                        '--no-default-keyring',
                        '--keyring=/etc/pacman.d/gnupg/pubring.gpg',
                        '--list-keys',
                        '01234567890ABCDE01234567890ABCDE12345678',
                    ],
                    {'check_rc': False},
                    (
                        2,
                        '',
                        '''
                        gpg: error reading key: No public key
                        tru::1:1616373715:0:3:1:5
                        ''',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
]


@pytest.mark.parametrize(
    'patch_ansible_module, testcase',
    TEST_CASES,
    ids=[item[1]['id'] for item in TEST_CASES],
    indirect=['patch_ansible_module']
)
@pytest.mark.usefixtures('patch_ansible_module')
def test_normal_operation(mocker, capfd, patch_pacman_key_calls, testcase):
    # patch run_command invocations with mock data
    call_results = [item[2] for item in testcase['run_command.calls']]
    mock_run_command = mocker.patch.object(
        AnsibleModule,
        'run_command',
        side_effect=call_results,
    )

    # invoke module
    with pytest.raises(SystemExit):
        pacman_key.main()

    # capture std{out,err}
    out, err = capfd.readouterr()
    results = json.loads(out)

    # assertion time!
    assert 'changed' in results
    assert results['changed'] == testcase['changed']
    if 'msg' in results:
        assert results['msg'] == testcase['msg']

    assert AnsibleModule.run_command.call_count == len(testcase['run_command.calls'])
    if AnsibleModule.run_command.call_count:
        call_args_list = [(item[0][0], item[1]) for item in AnsibleModule.run_command.call_args_list]
        expected_call_args_list = [(item[0], item[1]) for item in testcase['run_command.calls']]
        assert call_args_list == expected_call_args_list
