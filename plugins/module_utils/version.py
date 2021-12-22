#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Provide Version object to compare version numbers."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six import raise_from

try:
    from ansible.module_utils.compat.version import LooseVersion as Version
except ImportError:
    try:
        from distutils.version import LooseVersion as Version
    except ImportError as exc:
        raise_from(ImportError('To use this plugin or module with ansible-core < 2.11, you need to use Python < 2.12 with distutils.version present'), exc)
