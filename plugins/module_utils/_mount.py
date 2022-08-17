# -*- coding: utf-8 -*-
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is based on
# Lib/posixpath.py of cpython
#
# Copyright (c) 2001-2022 Python Software Foundation.  All rights reserved.
# It is licensed under the PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# (See LICENSES/PSF-2.0.txt in this collection)
# SPDX-License-Identifier: PSF-2.0

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os


def ismount(path):
    """Test whether a path is a mount point
    This is a copy of the upstream version of ismount(). Originally this was copied here as a workaround
    until Python issue 2466 was fixed. Now it is here so this will work on older versions of Python
    that may not have the upstream fix.
    https://github.com/ansible/ansible-modules-core/issues/2186
    http://bugs.python.org/issue2466
    """
    try:
        s1 = os.lstat(path)
    except (OSError, ValueError):
        # It doesn't exist -- so not a mount point. :-)
        return False
    else:
        # A symlink can never be a mount point
        if os.path.stat.S_ISLNK(s1.st_mode):
            return False

    if isinstance(path, bytes):
        parent = os.path.join(path, b'..')
    else:
        parent = os.path.join(path, '..')
    parent = os.path.realpath(parent)
    try:
        s2 = os.lstat(parent)
    except (OSError, ValueError):
        return False

    dev1 = s1.st_dev
    dev2 = s2.st_dev
    if dev1 != dev2:
        return True     # path/.. on a different device as path
    ino1 = s1.st_ino
    ino2 = s2.st_ino
    if ino1 == ino2:
        return True     # path/.. is the same i-node as path
    return False
