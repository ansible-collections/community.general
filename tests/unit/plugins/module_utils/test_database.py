# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.database import (
    is_input_dangerous,
    pg_quote_identifier,
    SQLParseError,
)

# These are all valid strings
# The results are based on interpreting the identifier as a table name
VALID = {
    # User quoted
    '"public.table"': '"public.table"',
    '"public"."table"': '"public"."table"',
    '"schema test"."table test"': '"schema test"."table test"',

    # We quote part
    'public.table': '"public"."table"',
    '"public".table': '"public"."table"',
    'public."table"': '"public"."table"',
    'schema test.table test': '"schema test"."table test"',
    '"schema test".table test': '"schema test"."table test"',
    'schema test."table test"': '"schema test"."table test"',

    # Embedded double quotes
    'table "test"': '"table ""test"""',
    'public."table ""test"""': '"public"."table ""test"""',
    'public.table "test"': '"public"."table ""test"""',
    'schema "test".table': '"schema ""test"""."table"',
    '"schema ""test""".table': '"schema ""test"""."table"',
    '"""wat"""."""test"""': '"""wat"""."""test"""',
    # Sigh, handle these as well:
    '"no end quote': '"""no end quote"',
    'schema."table': '"schema"."""table"',
    '"schema.table': '"""schema"."table"',
    'schema."table.something': '"schema"."""table"."something"',

    # Embedded dots
    '"schema.test"."table.test"': '"schema.test"."table.test"',
    '"schema.".table': '"schema."."table"',
    '"schema."."table"': '"schema."."table"',
    'schema.".table"': '"schema".".table"',
    '"schema".".table"': '"schema".".table"',
    '"schema.".".table"': '"schema.".".table"',
    # These are valid but maybe not what the user intended
    '."table"': '".""table"""',
    'table.': '"table."',
}

INVALID = {
    ('test.too.many.dots', 'table'): 'PostgreSQL does not support table with more than 3 dots',
    ('"test.too".many.dots', 'database'): 'PostgreSQL does not support database with more than 1 dots',
    ('test.too."many.dots"', 'database'): 'PostgreSQL does not support database with more than 1 dots',
    ('"test"."too"."many"."dots"', 'database'): "PostgreSQL does not support database with more than 1 dots",
    ('"test"."too"."many"."dots"', 'schema'): "PostgreSQL does not support schema with more than 2 dots",
    ('"test"."too"."many"."dots"', 'table'): "PostgreSQL does not support table with more than 3 dots",
    ('"test"."too"."many"."dots"."for"."column"', 'column'): "PostgreSQL does not support column with more than 4 dots",
    ('"table "invalid" double quote"', 'table'): 'User escaped identifiers must escape extra quotes',
    ('"schema "invalid"""."table "invalid"', 'table'): 'User escaped identifiers must escape extra quotes',
    ('"schema."table"', 'table'): 'User escaped identifiers must escape extra quotes',
    ('"schema".', 'table'): 'Identifier name unspecified or unquoted trailing dot',
}

HOW_MANY_DOTS = (
    ('role', 'role', '"role"',
     'PostgreSQL does not support role with more than 1 dots'),
    ('db', 'database', '"db"',
     'PostgreSQL does not support database with more than 1 dots'),
    ('db.schema', 'schema', '"db"."schema"',
     'PostgreSQL does not support schema with more than 2 dots'),
    ('db.schema.table', 'table', '"db"."schema"."table"',
     'PostgreSQL does not support table with more than 3 dots'),
    ('db.schema.table.column', 'column', '"db"."schema"."table"."column"',
     'PostgreSQL does not support column with more than 4 dots'),
)

VALID_QUOTES = ((test, VALID[test]) for test in sorted(VALID))
INVALID_QUOTES = ((test[0], test[1], INVALID[test]) for test in sorted(INVALID))

IS_STRINGS_DANGEROUS = (
    (u'', False),
    (u' ', False),
    (u'alternative database', False),
    (u'backup of TRUNCATED table', False),
    (u'bob.dropper', False),
    (u'd\'artagnan', False),
    (u'user_with_select_update_truncate_right', False),
    (u';DROP DATABASE fluffy_pets_photos', True),
    (u';drop DATABASE fluffy_pets_photos', True),
    (u'; TRUNCATE TABLE his_valuable_table', True),
    (u'; truncate TABLE his_valuable_table', True),
    (u'\'--', True),
    (u'"--', True),
    (u'\' union select username, password from admin_credentials', True),
    (u'\' UNION SELECT username, password from admin_credentials', True),
    (u'\' intersect select', True),
    (u'\' INTERSECT select', True),
    (u'\' except select', True),
    (u'\' EXCEPT select', True),
    (u';ALTER TABLE prices', True),
    (u';alter table prices', True),
    (u"; UPDATE products SET price = '0'", True),
    (u";update products SET price = '0'", True),
    (u"; DELETE FROM products", True),
    (u"; delete FROM products", True),
    (u"; SELECT * FROM products", True),
    (u" ; select * from products", True),
)


@pytest.mark.parametrize("identifier, quoted_identifier", VALID_QUOTES)
def test_valid_quotes(identifier, quoted_identifier):
    assert pg_quote_identifier(identifier, 'table') == quoted_identifier


@pytest.mark.parametrize("identifier, id_type, msg", INVALID_QUOTES)
def test_invalid_quotes(identifier, id_type, msg):
    with pytest.raises(SQLParseError) as ex:
        pg_quote_identifier(identifier, id_type)

    ex.match(msg)


@pytest.mark.parametrize("identifier, id_type, quoted_identifier, msg", HOW_MANY_DOTS)
def test_how_many_dots(identifier, id_type, quoted_identifier, msg):
    assert pg_quote_identifier(identifier, id_type) == quoted_identifier

    with pytest.raises(SQLParseError) as ex:
        pg_quote_identifier('%s.more' % identifier, id_type)

    ex.match(msg)


@pytest.mark.parametrize("string, result", IS_STRINGS_DANGEROUS)
def test_is_input_dangerous(string, result):
    assert is_input_dangerous(string) == result
