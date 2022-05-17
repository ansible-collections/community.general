# -*- coding: utf-8 -*-
# (c) 2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from __future__ import (absolute_import, division, print_function)
# pylint: disable-next=invalid-name
__metaclass__ = type

import pytest
from typing import Union
from ansible_collections.community.general.plugins.module_utils.mh.deco\
    import basic_annotation_type_checking


@basic_annotation_type_checking
def fixture_func(arg1: list,
                 arg2: Union[int, bool] = 16, *args, **kwarg) -> None:
    pass


def test_with_good_positional_args() -> None:
    fixture_func([], 8, 'foo', 'bar', foo='bar', bar='foo')
    fixture_func([], True, 'foo', 'bar', foo='bar', bar='foo')


def test_with_good_named_args() -> None:
    fixture_func(arg2=8, arg1=[], foo='bar', bar='foo')
    fixture_func(arg2=True, arg1=[], foo='bar', bar='foo')


def test_with_good_mixed_args() -> None:
    fixture_func([], arg2=8, foo='bar', bar='foo')
    fixture_func([], arg2=True, foo='bar', bar='foo')


def test_with_good_default_value() -> None:
    fixture_func([], foo='bar', bar='foo')


def test_with_bad_positional_args():
    with pytest.raises(TypeError):
        fixture_func({}, 8, 'foo', 'bar', foo='bar', bar='foo')
        fixture_func([], 'a', 'foo', 'bar', foo='bar', bar='foo')


def test_with_bad_named_args():
    with pytest.raises(TypeError):
        fixture_func(arg2='a', arg1=[], foo='bar', bar='foo')
        fixture_func(arg2=True, arg1='a', foo='bar', bar='foo')


def test_with_bad_mixed_args():
    with pytest.raises(TypeError):
        fixture_func('a', arg2=8, foo='bar', bar='foo')
        fixture_func([], arg2='a', foo='bar', bar='foo')


def test_with_bad_default_value():
    with pytest.raises(TypeError):
        fixture_func('a', foo='bar', bar='foo')
