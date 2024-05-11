# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re
from ansible.module_utils.six import string_types


def _create_regex_group_complement(s):
    lines = (line.strip() for line in s.split("\n") if line.strip())
    chars = filter(None, (line.split("#")[0].strip() for line in lines))
    group = r"[^" + r"".join(chars) + r"]"
    return re.compile(group)


class HomebrewValidate(object):
    # class regexes ------------------------------------------------ {{{
    VALID_PATH_CHARS = r"""
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        :                   # colons
        {sep}               # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    """.format(
        sep=os.path.sep
    )

    VALID_BREW_PATH_CHARS = r"""
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        {sep}               # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    """.format(
        sep=os.path.sep
    )

    VALID_PACKAGE_CHARS = r"""
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        .                   # dots
        /                   # slash (for taps)
        \+                  # plusses
        \-                  # dashes
        :                   # colons (for URLs)
        @                   # at-sign
    """

    INVALID_PATH_REGEX = _create_regex_group_complement(VALID_PATH_CHARS)
    INVALID_BREW_PATH_REGEX = _create_regex_group_complement(VALID_BREW_PATH_CHARS)
    INVALID_PACKAGE_REGEX = _create_regex_group_complement(VALID_PACKAGE_CHARS)
    # /class regexes ----------------------------------------------- }}}

    # class validations -------------------------------------------- {{{
    @classmethod
    def valid_path(cls, path):
        """
        `path` must be one of:
         - list of paths
         - a string containing only:
             - alphanumeric characters
             - dashes
             - dots
             - spaces
             - colons
             - os.path.sep
        """

        if isinstance(path, string_types):
            return not cls.INVALID_PATH_REGEX.search(path)

        try:
            iter(path)
        except TypeError:
            return False
        else:
            paths = path
            return all(cls.valid_brew_path(path_) for path_ in paths)

    @classmethod
    def valid_brew_path(cls, brew_path):
        """
        `brew_path` must be one of:
         - None
         - a string containing only:
             - alphanumeric characters
             - dashes
             - dots
             - spaces
             - os.path.sep
        """

        if brew_path is None:
            return True

        return isinstance(
            brew_path, string_types
        ) and not cls.INVALID_BREW_PATH_REGEX.search(brew_path)

    @classmethod
    def valid_package(cls, package):
        """A valid package is either None or alphanumeric."""

        if package is None:
            return True

        return isinstance(
            package, string_types
        ) and not cls.INVALID_PACKAGE_REGEX.search(package)
