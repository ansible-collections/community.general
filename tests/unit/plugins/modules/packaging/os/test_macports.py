# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.community.general.plugins.modules.packaging.os import macports

import pytest

TESTED_MODULE = macports.__name__

QUERY_PORT_TEST_CASES = [
    pytest.param('', False, False, id='Not installed'),
    pytest.param('  git @2.29.2_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28', True, False, id='Installed but not active'),
    pytest.param('  git @2.29.2_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28 (active)', True, True, id='Installed and active'),
    pytest.param('''  git @2.29.2_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28
  git @2.28.1_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28
''', True, False, id='2 versions installed, neither active'),
    pytest.param('''  git @2.29.2_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28 (active)
  git @2.28.1_0+credential_osxkeychain+diff_highlight+doc+pcre+perl5_28
''', True, True, id='2 versions installed, one active'),
]


@pytest.mark.parametrize("run_cmd_return_val, present_expected, active_expected", QUERY_PORT_TEST_CASES)
def test_macports_query_port(mocker, run_cmd_return_val, present_expected, active_expected):
    module = mocker.Mock()
    run_command = mocker.Mock()
    run_command.return_value = (0, run_cmd_return_val, '')
    module.run_command = run_command

    assert macports.query_port(module, 'port', 'git', state="present") == present_expected
    assert macports.query_port(module, 'port', 'git', state="active") == active_expected
