# -*- coding: utf-8 -*-
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from collections import namedtuple
from ansible_collections.community.general.plugins.modules import opkg

import pytest

TESTED_MODULE = opkg.__name__


ModuleTestCase = namedtuple("ModuleTestCase", ["id", "input", "output", "run_command_calls"])
RunCmdCall = namedtuple("RunCmdCall", ["command", "environ", "rc", "out", "err"])


@pytest.fixture
def patch_opkg(mocker):
    mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', return_value='/testbin/opkg')


TEST_CASES = [
    ModuleTestCase(
        id="install_zlibdev",
        input={"name": "zlib-dev", "state": "present"},
        output={
            "msg": "installed 1 package(s)"
        },
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "install", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out=(
                    "Installing zlib-dev (1.2.11-6) to root..."
                    "Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk"
                    "Installing zlib (1.2.11-6) to root..."
                    "Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib_1.2.11-6_mips_24kc.ipk"
                    "Configuring zlib."
                    "Configuring zlib-dev."
                ),
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="zlib-dev - 1.2.11-6\n",
                err="",
            ),
        ],
    ),
    ModuleTestCase(
        id="install_zlibdev_present",
        input={"name": "zlib-dev", "state": "present"},
        output={
            "msg": "package(s) already present"
        },
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="zlib-dev - 1.2.11-6\n",
                err="",
            ),
        ],
    ),
    ModuleTestCase(
        id="install_zlibdev_force_reinstall",
        input={"name": "zlib-dev", "state": "present", "force": "reinstall"},
        output={
            "msg": "installed 1 package(s)"
        },
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="zlib-dev - 1.2.11-6\n",
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "install", "--force-reinstall", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out=(
                    "Installing zlib-dev (1.2.11-6) to root...\n"
                    "Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk\n"
                    "Configuring zlib-dev.\n"
                ),
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="zlib-dev - 1.2.11-6\n",
                err="",
            ),
        ],
    ),
    ModuleTestCase(
        id="install_zlibdev_with_version",
        input={"name": "zlib-dev=1.2.11-6", "state": "present"},
        output={
            "msg": "installed 1 package(s)"
        },
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "install", "zlib-dev=1.2.11-6"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out=(
                    "Installing zlib-dev (1.2.11-6) to root..."
                    "Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk"
                    "Installing zlib (1.2.11-6) to root..."
                    "Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib_1.2.11-6_mips_24kc.ipk"
                    "Configuring zlib."
                    "Configuring zlib-dev."
                ),
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "zlib-dev"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="zlib-dev - 1.2.11-6 \n",   # This output has the extra space at the end, to satisfy the behaviour of Yocto/OpenEmbedded's opkg
                err="",
            ),
        ],
    ),
    ModuleTestCase(
        id="install_vim_updatecache",
        input={"name": "vim-fuller", "state": "present", "update_cache": True},
        output={
            "msg": "installed 1 package(s)"
        },
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/opkg", "update"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "vim-fuller"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "install", "vim-fuller"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out=(
                    "Multiple packages (libgcc1 and libgcc1) providing same name marked HOLD or PREFER. Using latest.\n"
                    "Installing vim-fuller (9.0-1) to root...\n"
                    "Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/packages/vim-fuller_9.0-1_x86_64.ipk\n"
                    "Installing terminfo (6.4-2) to root...\n"
                    "Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/base/terminfo_6.4-2_x86_64.ipk\n"
                    "Installing libncurses6 (6.4-2) to root...\n"
                    "Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/base/libncurses6_6.4-2_x86_64.ipk\n"
                    "Configuring terminfo.\n"
                    "Configuring libncurses6.\n"
                    "Configuring vim-fuller.\n"
                ),
                err="",
            ),
            RunCmdCall(
                command=["/testbin/opkg", "list-installed", "vim-fuller"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="vim-fuller - 9.0-1 \n",   # This output has the extra space at the end, to satisfy the behaviour of Yocto/OpenEmbedded's opkg
                err="",
            ),
        ],
    ),
]
TEST_CASES_IDS = [item.id for item in TEST_CASES]


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         [[x.input, x] for x in TEST_CASES],
                         ids=TEST_CASES_IDS,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_opkg(mocker, capfd, patch_opkg, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    run_cmd_calls = testcase.run_command_calls

    # Mock function used for running commands first
    call_results = [(x.rc, x.out, x.err) for x in run_cmd_calls]
    mock_run_command = mocker.patch('ansible.module_utils.basic.AnsibleModule.run_command', side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        opkg.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("testcase =\n%s" % str(testcase))
    print("results =\n%s" % results)

    for test_result in testcase.output:
        assert results[test_result] == testcase.output[test_result], \
            "'{0}': '{1}' != '{2}'".format(test_result, results[test_result], testcase.output[test_result])

    call_args_list = [(item[0][0], item[1]) for item in mock_run_command.call_args_list]
    expected_call_args_list = [(item.command, item.environ) for item in run_cmd_calls]
    print("call args list =\n%s" % call_args_list)
    print("expected args list =\n%s" % expected_call_args_list)

    assert mock_run_command.call_count == len(run_cmd_calls)
    if mock_run_command.call_count:
        assert call_args_list == expected_call_args_list
