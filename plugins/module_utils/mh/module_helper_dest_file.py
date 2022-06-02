# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or
# https://opensource.org/licenses/BSD-2-Clause)
"""
Toolbox that help to do somme basics on a destination file for module that need
it.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import tempfile

from abc import abstractmethod

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.mh.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException
from ansible_collections.community.general.plugins.module_utils.mh.deco import (
    cause_changes,
    check_mode_skip)


class DestNotExists(ModuleHelperException):
    pass


class ParentNotWriteable(ModuleHelperException):
    pass


class DestNotReadable(ModuleHelperException):
    pass


class DestNotWriteable(ModuleHelperException):
    pass


class DestNotRegularFile(ModuleHelperException):
    pass


class CantCreateBackup(ModuleHelperException):
    pass


def check_if_dest_exists(dest):
    # type: (str) -> bool
    try:
        os.stat(dest)
    except FileNotFoundError:
        return False
    except PermissionError:
        pass
    return True


def check_if_parent_is_writeable(dest):
    # type: (str) -> bool
    if os.access(os.path.dirname(dest), os.W_OK):
        return True
    return False


def check_if_dest_is_readable(dest):
    # type: (str) -> bool
    if os.access(dest, os.R_OK):
        return True
    return False


def check_if_dest_is_writeable(dest):
    # type: (str) -> bool
    if os.access(dest, os.W_OK):
        return True
    return False


def check_if_dest_is_regular_file(dest):
    # type: (str) -> bool
    if os.path.isfile(dest):
        return True
    return False


def dest_file_sanity_check(dest, create=False, backup=False):
    # type: (str, bool, bool) -> bool
    """
    Ensure that the destination exist and is readable or if not exists and
    'create' is True, ensure that the parent of the destination is writeable. If
    'backup' is True, also ensure that the backup file can be created.

    Return `True` if the file will be created else `False`.
    """
    exists = check_if_dest_exists(dest)
    writeable_parent = check_if_parent_is_writeable(dest)
    if not create and not exists:
        raise DestNotExists(msg="{0} does not not exist !".format(dest))
    if create and not exists and not writeable_parent:
        raise ParentNotWriteable(msg="Can't create {0}, parent directory is not writeable !".format(dest))
    if exists and not check_if_dest_is_readable(dest):
        raise DestNotReadable(msg="Destination {0} is not readable !".format(dest))
    if exists and not check_if_dest_is_writeable(dest):
        raise DestNotWriteable(msg="Destination {0} is not writeable !".format(dest))
    if exists and not check_if_dest_is_regular_file(dest):
        raise DestNotRegularFile(msg="Destination {0} is not a regular file !".format(dest))
    if exists and backup and not writeable_parent:
        raise CantCreateBackup(msg="Can't create backup file for {0} because parrent dir is not writeable !".format(dest))
    return (not exists and create)


class DestFileModuleHelper(ModuleHelper):

    def __init__(self, module=None, var_dest_file='path', var_result_data='result'):
        # type: (dict | AnsibleModule | None, str, str) -> None
        self._tmpfile = None
        self._created = False
        self.file_args = None
        self.var_dest_file = var_dest_file
        self.var_result_data = var_result_data
        super(DestFileModuleHelper, self).__init__(module)

    def __init_module__(self):
        # type: () -> None
        self._created = dest_file_sanity_check(
            self.vars[self.var_dest_file],
            self.vars['allow_creation'],
            self.vars['backup'])
        self.file_args = self.module.load_file_common_arguments(self.module.params)
        self.__load_result_data__()

    @abstractmethod
    def __load_result_data__(self):
        """
        Implement it in the module class to describe how read data in the
        destination file and how save the result in `self.vars`.
        """
        pass

    def __quit_module__(self):
        # type: () -> None
        if self.has_changed():
            self.__update_dest_file__()
        self.vars.set('created', self._created)
        self._update_file_args()

    def _update_file_args(self):
        attr_changes = {'before': {}, 'after': {}}
        self.changed = self.module.set_fs_attributes_if_different(self.file_args, self.changed, diff=attr_changes)
        for key, val in attr_changes['after'].items():
            if key == 'dest' or key == 'path':
                continue
            if val is not None:
                self.vars.meta(key).set(diff=True, change=True, output=True)
                self.vars.set(key, val)

    @cause_changes(on_success=True)
    @check_mode_skip
    def __update_dest_file__(self):
        # type: () -> None
        self.__write_temp__()
        self.__make_backup__()
        self.__move_temp__()

    @abstractmethod
    def __write_temp__(self, *args, **kwargs):
        # type: () -> None
        """
        Implement it in the module to describe how the destination must be
        written in the tempfile.

        You must set self_tmpfile with the name of created temps file.

        You can use `self._write_in_tmpfile()` to help you to write content in
        temp file like this :

        ```
        self._tmpfile = self._write_in_tempfile('my file content')
        ```
        """
        pass

    def __make_backup__(self):
        # type: () -> None
        if self.vars.get('backup') and not self._created:
            self.vars.set('backup_file', self.module.backup_local(self.vars.get(self.var_dest_file)))

    def __move_temp__(self):
        # type: () -> None
        try:
            self.module.atomic_move(self._tmpfile, self.vars['path'])
        except Exception as ex:
            if self.vars.get('backup_file'):
                self.module.add_cleanup_file(self.vars.backup_file)
            raise ex

    def _write_in_tempfile(self, content):
        # type: (str) -> str
        """
        Helper that can be used to create a temp file and write a content
        into it. It add the created temps file in module cleanup file stack.

        Return the name of the temp file.
        """
        fd, tf = tempfile.mkstemp(dir=self.module.tmpdir)
        self.module.add_cleanup_file(tf)
        os.write(fd, bytes(content, 'utf-8'))
        os.close(fd)
        return tf
