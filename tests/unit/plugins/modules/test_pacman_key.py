# Copyright (c) 2019, George Rawlinson <george@rawlinson.net.nz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.modules import pacman_key
import pytest
import json

# path used for mocking get_bin_path()
MOCK_BIN_PATH = '/mocked/path'

# Key ID used for tests
TESTING_KEYID = '14F26682D0916CDD81E37B6D61B7B526D98F0353'
TESTING_KEYFILE_PATH = '/tmp/pubkey.asc'

# gpg --{show,list}-key output (key present, but expired)
GPG_SHOWKEY_OUTPUT_EXPIRED = """
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
""".strip()

# gpg --{show,list}-key output (key present and trusted)
GPG_SHOWKEY_OUTPUT_TRUSTED = """
tru::1:1616373715:0:3:1:5
pub:f:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23::0:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:f::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>::::::::::0:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
""".strip()

GPG_LIST_SECRET_KEY_OUTPUT = """
sec:u:2048:1:58FCCBCC131FCCAB:1406639814:::u:::scSC:::+:::23::0:
fpr:::::::::AC0F357BE07F1493C34DCAB258FCCBCC131FCCAB:
grp:::::::::C1227FFDD039AD942F777EA0639E1F1EAA96AB12:
uid:u::::1406639814::79311EDEA01302E0DBBB2F33AE799F8BB677652F::Pacman Keyring Master Key <pacman@localhost>::::::::::0:
""".lstrip()

GPG_CHECK_SIGNATURES_OUTPUT = """
tru::1:1742507906:1750096255:3:1:5
pub:f:4096:1:61B7B526D98F0353:1437155332:::-:::scSC::::::23:1742507897:1 https\x3a//185.125.188.26\x3a443:
fpr:::::::::14F26682D0916CDD81E37B6D61B7B526D98F0353:
uid:f::::1437155332::E57D1F9BFF3B404F9F30333629369B08DF5E2161::Mozilla Software Releases <release@mozilla.com>:::::::::1742507897:1:
sig:!::1:61B7B526D98F0353:1437155332::::Mozilla Software Releases <release@mozilla.com>:13x:::::2:
sig:!::1:58FCCBCC131FCCAB:1742507905::::Pacman Keyring Master Key <pacman@localhost>:10l::AC0F357BE07F1493C34DCAB258FCCBCC131FCCAB:::8:
sub:f:4096:1:E36D3B13F3D93274:1683308659:1746380659:::::s::::::23:
fpr:::::::::ADD7079479700DCADFDD5337E36D3B13F3D93274:
sig:!::1:61B7B526D98F0353:1683308659::::Mozilla Software Releases <release@mozilla.com>:18x::14F26682D0916CDD81E37B6D61B7B526D98F0353:::10:
sub:e:4096:1:1C69C4E55E9905DB:1437155572:1500227572:::::s::::::23:
fpr:::::::::F2EF4E6E6AE75B95F11F1EB51C69C4E55E9905DB:
sig:!::1:61B7B526D98F0353:1437155572::::Mozilla Software Releases <release@mozilla.com>:18x:::::2:
sub:e:4096:1:BBBEBDBB24C6F355:1498143157:1561215157:::::s::::::23:
fpr:::::::::DCEAC5D96135B91C4EA672ABBBBEBDBB24C6F355:
sig:!::1:61B7B526D98F0353:1498143157::::Mozilla Software Releases <release@mozilla.com>:18x::14F26682D0916CDD81E37B6D61B7B526D98F0353:::8:
sub:e:4096:1:F1A6668FBB7D572E:1559247338:1622319338:::::s::::::23:
fpr:::::::::097B313077AE62A02F84DA4DF1A6668FBB7D572E:
sig:!::1:61B7B526D98F0353:1559247338::::Mozilla Software Releases <release@mozilla.com>:18x::14F26682D0916CDD81E37B6D61B7B526D98F0353:::10:
sub:e:4096:1:EBE41E90F6F12F6D:1621282261:1684354261:::::s::::::23:
fpr:::::::::4360FE2109C49763186F8E21EBE41E90F6F12F6D:
sig:!::1:61B7B526D98F0353:1621282261::::Mozilla Software Releases <release@mozilla.com>:18x::14F26682D0916CDD81E37B6D61B7B526D98F0353:::10:
""".strip()

# gpg --{show,list}-key output (key absent)
GPG_NOKEY_OUTPUT = """
gpg: error reading key: No public key
tru::1:1616373715:0:3:1:5
""".strip()

# pacman-key output (successful invocation)
PACMAN_KEY_SUCCESS = """
==> Updating trust database...
gpg: next trustdb check due at 2021-08-02
""".strip()

# expected command for gpg --list-keys KEYID
RUN_CMD_LISTKEYS = [
    MOCK_BIN_PATH,
    '--homedir=/etc/pacman.d/gnupg',
    '--no-permission-warning',
    '--with-colons',
    '--quiet',
    '--batch',
    '--no-tty',
    '--no-default-keyring',
    '--list-keys',
    TESTING_KEYID,
]

# expected command for gpg --show-keys KEYFILE
RUN_CMD_SHOW_KEYFILE = [
    MOCK_BIN_PATH,
    '--no-permission-warning',
    '--with-colons',
    '--quiet',
    '--batch',
    '--no-tty',
    '--with-fingerprint',
    '--show-keys',
    TESTING_KEYFILE_PATH,
]

# expected command for pacman-key --lsign-key KEYID
RUN_CMD_LSIGN_KEY = [
    MOCK_BIN_PATH,
    '--gpgdir',
    '/etc/pacman.d/gnupg',
    '--lsign-key',
    TESTING_KEYID,
]

RUN_CMD_LIST_SECRET_KEY = [
    MOCK_BIN_PATH,
    '--homedir=/etc/pacman.d/gnupg',
    '--no-permission-warning',
    '--with-colons',
    '--quiet',
    '--batch',
    '--no-tty',
    '--list-secret-key',
]

# expected command for gpg --check-signatures
RUN_CMD_CHECK_SIGNATURES = [
    MOCK_BIN_PATH,
    '--homedir=/etc/pacman.d/gnupg',
    '--no-permission-warning',
    '--with-colons',
    '--quiet',
    '--batch',
    '--no-tty',
    '--check-signatures',
    TESTING_KEYID,
]

TESTCASES = [
    #
    # invalid user input
    #
    # state: present, id: absent
    [
        {
            'state': 'present',
        },
        {
            'id': 'param_missing_id',
            'msg': 'missing required arguments: id',
            'failed': True,
        },
    ],
    # state: present, required parameters: missing
    [
        {
            'state': 'present',
            'id': '0xDOESNTMATTER',
        },
        {
            'id': 'param_missing_method',
            'msg': 'state is present but any of the following are missing: data, file, url, keyserver',
            'failed': True,
        },
    ],
    # state: present, id: invalid (not full-length)
    [
        {
            'id': '0xDOESNTMATTER',
            'data': 'FAKEDATA',
        },
        {
            'id': 'param_id_not_full',
            'msg': 'key ID is not full-length: DOESNTMATTER',
            'failed': True,
        },
    ],
    # state: present, id: invalid (not hexadecimal)
    [
        {
            'state': 'present',
            'id': '01234567890ABCDE01234567890ABCDE1234567M',
            'data': 'FAKEDATA',
        },
        {
            'id': 'param_id_not_hex',
            'msg': 'key ID is not hexadecimal: 01234567890ABCDE01234567890ABCDE1234567M',
            'failed': True,
        },
    ],
    # state: absent, id: absent
    [
        {
            'state': 'absent',
        },
        {
            'id': 'param_absent_state_missing_id',
            'msg': 'missing required arguments: id',
            'failed': True,
        },
    ],
    #
    # check mode
    #
    # state & key present
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_and_key_present',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # state present, key absent
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_present_key_absent',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
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
            'id': TESTING_KEYID,
            '_ansible_check_mode': True,
        },
        {
            'id': 'checkmode_state_and_key_absent',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
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
            'id': TESTING_KEYID,
            '_ansible_check_mode': True,
        },
        {
            'id': 'check_mode_state_absent_key_present',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    #
    # normal operation
    #
    # state & key present
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_and_key_present',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # state present, ensure_trusted & key expired
    [
        {
            'state': 'present',
            'ensure_trusted': True,
            'id': TESTING_KEYID,
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'state_present_trusted_key_expired',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {
                        'check_rc': False,
                    },
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # state present & key trusted
    [
        {
            'state': 'present',
            'ensure_trusted': True,
            'id': TESTING_KEYID,
            'data': 'FAKEDATA',
            '_ansible_check_mode': True,
        },
        {
            'id': 'state_present_and_key_trusted',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {
                        'check_rc': False,
                    },
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_TRUSTED,
                        '',
                    ),
                ),
                (
                    RUN_CMD_CHECK_SIGNATURES,
                    {},
                    (
                        0,
                        GPG_CHECK_SIGNATURES_OUTPUT,
                        '',
                    ),
                ),
                (
                    RUN_CMD_LIST_SECRET_KEY,
                    {},
                    (
                        0,
                        GPG_LIST_SECRET_KEY_OUTPUT,
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
            'id': TESTING_KEYID,
        },
        {
            'id': 'state_absent_key_present',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
                (
                    [
                        MOCK_BIN_PATH,
                        '--gpgdir',
                        '/etc/pacman.d/gnupg',
                        '--delete',
                        TESTING_KEYID,
                    ],
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
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
            'id': TESTING_KEYID,
        },
        {
            'id': 'state_and_key_absent',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
                    ),
                ),
            ],
            'changed': False,
        },
    ],
    # state: present, key: absent, method: file
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'file': TESTING_KEYFILE_PATH,
        },
        {
            'id': 'state_present_key_absent_method_file',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
                    ),
                ),
                (
                    RUN_CMD_SHOW_KEYFILE,
                    {'check_rc': True},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
                (
                    [
                        MOCK_BIN_PATH,
                        '--gpgdir',
                        '/etc/pacman.d/gnupg',
                        '--add',
                        '/tmp/pubkey.asc',
                    ],
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
                        '',
                    ),
                ),
                (
                    RUN_CMD_LSIGN_KEY,
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # state: present, key: absent, method: file
    # failure: keyid & keyfile don't match
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'file': TESTING_KEYFILE_PATH,
        },
        {
            'id': 'state_present_key_absent_verify_failed',
            'msg': 'key ID does not match. expected 14F26682D0916CDD81E37B6D61B7B526D98F0353, got 14F26682D0916CDD81E37B6D61B7B526D98F0354',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
                    ),
                ),
                (
                    RUN_CMD_SHOW_KEYFILE,
                    {'check_rc': True},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED.replace('61B7B526D98F0353', '61B7B526D98F0354'),
                        '',
                    ),
                ),
            ],
            'failed': True,
        },
    ],
    # state: present, key: absent, method: keyserver
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'keyserver': 'pgp.mit.edu',
        },
        {
            'id': 'state_present_key_absent_method_keyserver',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
                    ),
                ),
                (
                    [
                        MOCK_BIN_PATH,
                        '--gpgdir',
                        '/etc/pacman.d/gnupg',
                        '--keyserver',
                        'pgp.mit.edu',
                        '--recv-keys',
                        TESTING_KEYID,
                    ],
                    {'check_rc': True},
                    (
                        0,
                        '''
gpg: key 0x61B7B526D98F0353: 32 signatures not checked due to missing keys
gpg: key 0x61B7B526D98F0353: public key "Mozilla Software Releases <release@mozilla.com>" imported
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
gpg: Total number processed: 1
gpg:               imported: 1
''',
                        '',
                    ),
                ),
                (
                    RUN_CMD_LSIGN_KEY,
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
                        '',
                    ),
                ),
            ],
            'changed': True,
        },
    ],
    # state: present, key: absent, method: data
    [
        {
            'state': 'present',
            'id': TESTING_KEYID,
            'data': 'PGP_DATA',
        },
        {
            'id': 'state_present_key_absent_method_data',
            'run_command.calls': [
                (
                    RUN_CMD_LISTKEYS,
                    {'check_rc': False},
                    (
                        2,
                        '',
                        GPG_NOKEY_OUTPUT,
                    ),
                ),
                (
                    RUN_CMD_SHOW_KEYFILE,
                    {'check_rc': True},
                    (
                        0,
                        GPG_SHOWKEY_OUTPUT_EXPIRED,
                        '',
                    ),
                ),
                (
                    [
                        MOCK_BIN_PATH,
                        '--gpgdir',
                        '/etc/pacman.d/gnupg',
                        '--add',
                        '/tmp/pubkey.asc',
                    ],
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
                        '',
                    ),
                ),
                (
                    RUN_CMD_LSIGN_KEY,
                    {'check_rc': True},
                    (
                        0,
                        PACMAN_KEY_SUCCESS,
                        '',
                    ),
                ),
            ],
            'save_key_output': TESTING_KEYFILE_PATH,
            'changed': True,
        },
    ],
]


@pytest.fixture
def patch_get_bin_path(mocker):
    get_bin_path = mocker.patch.object(
        AnsibleModule,
        'get_bin_path',
        return_value=MOCK_BIN_PATH,
    )


@pytest.mark.parametrize(
    'patch_ansible_module, expected',
    TESTCASES,
    ids=[item[1]['id'] for item in TESTCASES],
    indirect=['patch_ansible_module']
)
@pytest.mark.usefixtures('patch_ansible_module')
def test_operation(mocker, capfd, patch_get_bin_path, expected):
    # patch run_command invocations with mock data
    if 'run_command.calls' in expected:
        mock_run_command = mocker.patch.object(
            AnsibleModule,
            'run_command',
            side_effect=[item[2] for item in expected['run_command.calls']],
        )

    # patch save_key invocations with mock data
    if 'save_key_output' in expected:
        mock_save_key = mocker.patch.object(
            pacman_key.PacmanKey,
            'save_key',
            return_value=expected['save_key_output'],
        )

    # invoke module
    with pytest.raises(SystemExit):
        pacman_key.main()

    # capture std{out,err}
    out, err = capfd.readouterr()
    results = json.loads(out)

    # assertion time!
    if 'msg' in expected:
        assert results['msg'] == expected['msg']
    if 'changed' in expected:
        assert results['changed'] == expected['changed']
    if 'failed' in expected:
        assert results['failed'] == expected['failed']

    if 'run_command.calls' in expected:
        assert AnsibleModule.run_command.call_count == len(expected['run_command.calls'])
        call_args_list = [(item[0][0], item[1]) for item in AnsibleModule.run_command.call_args_list]
        expected_call_args_list = [(item[0], item[1]) for item in expected['run_command.calls']]
        assert call_args_list == expected_call_args_list
