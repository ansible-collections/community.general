# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.web_infrastructure.apache2_module import create_apache_identifier

REPLACEMENTS = [
    ('php7.1', 'php7_module'),
    ('php5.6', 'php5_module'),
    ('shib2', 'mod_shib'),
    ('evasive', 'evasive20_module'),
    ('thismoduledoesnotexist', 'thismoduledoesnotexist_module'),  # the default
]


@pytest.mark.parametrize("replacement", REPLACEMENTS, ids=lambda x: x[0])
def test_apache_identifier(replacement):
    "test the correct replacement of an a2enmod name with an apache2ctl name"
    assert create_apache_identifier(replacement[0]) == replacement[1]
