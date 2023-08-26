# -*- coding: utf-8 -*-
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible_collections.community.general.plugins.modules import opkg

import pytest

from .cmd_runner_test_utils import CmdRunnerTestHelper

TESTED_MODULE = opkg.__name__
TEST_CASES = """---
- id: install_zlibdev
  input:
    name: zlib-dev
    state: present
  output:
    msg: installed 1 package(s)
  run_command_calls:
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: ""
      err: ""
    - command: [/testbin/opkg, install, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        Installing zlib-dev (1.2.11-6) to root...
        Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk
        Installing zlib (1.2.11-6) to root...
        Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib_1.2.11-6_mips_24kc.ipk
        Configuring zlib.
        Configuring zlib-dev.
      err: ""
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        zlib-dev - 1.2.11-6
      err: ""
- id: install_zlibdev_present
  input:
    name: zlib-dev
    state: present
  output:
    msg: package(s) already present
  run_command_calls:
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        zlib-dev - 1.2.11-6
      err: ""
- id: install_zlibdev_force_reinstall
  input:
    name: zlib-dev
    state: present
    force: reinstall
  output:
    msg: installed 1 package(s)
  run_command_calls:
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        zlib-dev - 1.2.11-6
      err: ""
    - command: [/testbin/opkg, install, --force-reinstall, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        Installing zlib-dev (1.2.11-6) to root...
        Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk
        Configuring zlib-dev.
      err: ""
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        zlib-dev - 1.2.11-6
      err: ""
- id: install_zlibdev_with_version
  input:
    name: zlib-dev=1.2.11-6
    state: present
  output:
    msg: installed 1 package(s)
  run_command_calls:
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: ""
      err: ""
    - command: [/testbin/opkg, install, zlib-dev=1.2.11-6]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        Installing zlib-dev (1.2.11-6) to root...
        Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk
        Installing zlib (1.2.11-6) to root...
        Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib_1.2.11-6_mips_24kc.ipk
        Configuring zlib.
        Configuring zlib-dev.
      err: ""
    - command: [/testbin/opkg, list-installed, zlib-dev]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: "zlib-dev - 1.2.11-6 \n"   # This output has the extra space at the end, to satisfy the behaviour of Yocto/OpenEmbedded's opkg
      err: ""
- id: install_vim_updatecache
  input:
    name: vim-fuller
    state: present
    update_cache: true
  output:
    msg: installed 1 package(s)
  run_command_calls:
    - command: [/testbin/opkg, update]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: ""
      err: ""
    - command: [/testbin/opkg, list-installed, vim-fuller]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: ""
      err: ""
    - command: [/testbin/opkg, install, vim-fuller]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: |
        Multiple packages (libgcc1 and libgcc1) providing same name marked HOLD or PREFER. Using latest.
        Installing vim-fuller (9.0-1) to root...
        Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/packages/vim-fuller_9.0-1_x86_64.ipk
        Installing terminfo (6.4-2) to root...
        Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/base/terminfo_6.4-2_x86_64.ipk
        Installing libncurses6 (6.4-2) to root...
        Downloading https://downloads.openwrt.org/snapshots/packages/x86_64/base/libncurses6_6.4-2_x86_64.ipk
        Configuring terminfo.
        Configuring libncurses6.
        Configuring vim-fuller.
      err: ""
    - command: [/testbin/opkg, list-installed, vim-fuller]
      environ: {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
      rc: 0
      out: "vim-fuller - 9.0-1 \n"   # This output has the extra space at the end, to satisfy the behaviour of Yocto/OpenEmbedded's opkg
      err: ""
"""


helper = CmdRunnerTestHelper("opkg", TEST_CASES)
patch_opkg = helper.cmd_fixture


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         helper.testcases_params, ids=helper.testcases_ids,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_opkg(mocker, capfd, patch_opkg, testcase):
    """
    Run unit tests for test cases listed in TEST_CASES
    """

    with helper(testcase, mocker) as ctx:
        # Try to run test case
        with pytest.raises(SystemExit):
            opkg.main()

        out, err = capfd.readouterr()
        results = json.loads(out)

        ctx.check_results(results)
