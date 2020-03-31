# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Andrey Tuzhilin <andrei.tuzhilin@gmail.com>
# Copyright: (c) 2020, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.saslprep import saslprep


VALID = [
    (u'', u''),
    (u'\u00A0', u' '),
    (u'a', u'a'),
    (u'й', u'й'),
    (u'\u30DE\u30C8\u30EA\u30C3\u30AF\u30B9', u'\u30DE\u30C8\u30EA\u30C3\u30AF\u30B9'),
    (u'The\u00ADM\u00AAtr\u2168', u'TheMatrIX'),
    (u'I\u00ADX', u'IX'),
    (u'user', u'user'),
    (u'USER', u'USER'),
    (u'\u00AA', u'a'),
    (u'\u2168', u'IX'),
    (u'\u05BE\u00A0\u05BE', u'\u05BE\u0020\u05BE'),
]

INVALID = [
    (None, TypeError),
    (b'', TypeError),
    (u'\u0221', ValueError),
    (u'\u0007', ValueError),
    (u'\u0627\u0031', ValueError),
    (u'\uE0001', ValueError),
    (u'\uE0020', ValueError),
    (u'\uFFF9', ValueError),
    (u'\uFDD0', ValueError),
    (u'\u0000', ValueError),
    (u'\u06DD', ValueError),
    (u'\uFFFFD', ValueError),
    (u'\uD800', ValueError),
    (u'\u200E', ValueError),
    (u'\u05BE\u00AA\u05BE', ValueError),
]


@pytest.mark.parametrize('source,target', VALID)
def test_saslprep_conversions(source, target):
    assert saslprep(source) == target


@pytest.mark.parametrize('source,exception', INVALID)
def test_saslprep_exceptions(source, exception):
    with pytest.raises(exception) as ex:
        saslprep(source)
