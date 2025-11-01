# Copyright (c) Ansible project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations


import os
import re


def _create_regex_group_complement(s):
    lines = (line.strip() for line in s.split("\n") if line.strip())
    chars = [_f for _f in (line.split("#")[0].strip() for line in lines) if _f]
    group = rf"[^{''.join(chars)}]"
    return re.compile(group)


class HomebrewValidate:
    # class regexes ------------------------------------------------ {{{
    VALID_PATH_CHARS = rf"""
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        :                   # colons
        {os.path.sep}       # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    """

    VALID_BREW_PATH_CHARS = rf"""
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        {os.path.sep}       # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    """

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

        if isinstance(path, str):
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

        return isinstance(brew_path, str) and not cls.INVALID_BREW_PATH_REGEX.search(brew_path)

    @classmethod
    def valid_package(cls, package):
        """A valid package is either None or alphanumeric."""

        if package is None:
            return True

        return isinstance(package, str) and not cls.INVALID_PACKAGE_REGEX.search(package)


def parse_brew_path(module):
    # type: (...) -> str
    """Attempt to find the Homebrew executable path.

    Requires:
        - module has a `path` parameter
        - path is a valid path string for the target OS. Otherwise, module.fail_json()
          is called with msg="Invalid_path: <path>".
    """
    path = module.params["path"]
    if not HomebrewValidate.valid_path(path):
        module.fail_json(msg=f"Invalid path: {path}")

    if isinstance(path, str):
        paths = path.split(":")
    elif isinstance(path, list):
        paths = path
    else:
        module.fail_json(msg=f"Invalid path: {path}")

    brew_path = module.get_bin_path("brew", required=True, opt_dirs=paths)
    if not HomebrewValidate.valid_brew_path(brew_path):
        module.fail_json(msg=f"Invalid brew path: {brew_path}")

    return brew_path
