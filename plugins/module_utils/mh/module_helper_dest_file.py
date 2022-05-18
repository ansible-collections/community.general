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
from functools import wraps
from typing import Callable, Union

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


class DestNotRegularFile(ModuleHelperException):
    pass


class CantCreateBackup(ModuleHelperException):
    pass


def check_if_dest_exists(dest: str) -> bool:
    try:
        os.stat(dest)
    except FileNotFoundError:
        return False
    except PermissionError:
        pass
    return True


def check_if_parent_is_writable(dest: str) -> bool:
    if os.access(os.path.dirname(dest), os.W_OK):
        return True
    return False


def check_if_dest_is_readable(dest: str) -> bool:
    if os.access(dest, os.R_OK):
        return True
    return False


def check_if_dest_is_regular_file(dest: str) -> bool:
    if os.path.isfile(dest):
        return True
    return False


def dest_file_sanity_check(dest: str,
                           create: bool = False,
                           backup: bool = False) -> bool:
    """
    Ensure that the destination exist and is readable or if not exists and
    'create' is True, ensure that the parent of the destination is writable. If
    'backup' is True, also ensure that the backup file can be created.

    Return `True` if the file will be created else `False`.
    """
    exists = check_if_dest_exists(dest)
    writable_parent = check_if_parent_is_writable(dest)
    if not create and not exists:
        raise DestNotExists(msg=f"{dest} does not not exist !")
    elif create and not exists and not writable_parent:
        raise ParentNotWriteable(msg=f"Can't create {dest}, " +
                                 "parent directory is not writable !")
    elif exists and not check_if_dest_is_readable(dest):
        raise DestNotReadable(msg=f"Destination {dest} is not readable !")
    elif exists and not check_if_dest_is_regular_file(dest):
        raise DestNotRegularFile(
            msg=f"Destination {dest} is not a regular file !")
    elif exists and backup and not writable_parent:
        raise CantCreateBackup(msg=f"Can't create backup file for {dest} " +
                               "because parrent dir is not writable !")
    return (not exists and create)


class DestFileModuleHelper(ModuleHelper):

    def __init__(self,
                 module: Union[dict, AnsibleModule, None] = None,
                 var_dest_file: str = 'path',
                 var_result_data: str = 'result') -> None:
        self._tmpfile = None
        self._created = False
        self.var_dest_file = var_dest_file
        self.var_result_data = var_result_data
        super().__init__(module)

    def __init_module__(self) -> None:
        self._created = dest_file_sanity_check(
            self.vars[self.var_dest_file],
            self.vars['create'],
            self.vars['backup'])
        self.__load_result_data__()

    @abstractmethod
    def __load_result_data__(self):
        """
        Implement it in the module class to describe how read data in the
        destination file and how save the result in `self.vars`.
        """
        pass

    def __quit_module__(self) -> None:
        if self.has_changed():
            self.__update_dest_file__()
        self.vars.set('created', self._created)

    @cause_changes(on_success=True)
    @check_mode_skip
    def __update_dest_file__(self) -> None:
        self.__write_temp__()
        self.__make_backup__()
        self.__move_temp__()

    @abstractmethod
    def __write_temp__(self, *args, **kwargs) -> None:
        """
        Implement it in the module to describe how the destination must be
        written in the tempfile.

        This function must set `self.__tmpfile` with the created tempfile.

        If cat you use the wrapper `DestFileModuleHelper.write_tempfile`
        decorator you car automaticall create the temp file(with the file
        descriptor set in `kwargs['fd']) and set self.__tempfile.

        Example:
            class MyModule(DestFileModuleHelper)
                ...

                @DestFileModuleHelper.write_tempfile decorator
                def __write_temp(self, *args, **kwargs):
                    temp_file_descriptor = kwargs['fd']
                    ...
        """
        pass

    def __make_backup__(self) -> None:
        if self.vars.get('backup') and not self._created:
            self.vars.set(
                'backup_file',
                self.module.backup_local(self.vars.get(self.var_dest_file)))

    def __move_temp__(self) -> None:
        try:
            self.module.atomic_move(self._tmpfile, self.vars['path'])
        except Exception as ex:
            if self.vars.get('backup_file'):
                self.module.add_cleanup_file(self.vars.backup_file)
            raise ex

    @staticmethod
    def write_tempfile(func: Callable) -> Callable:
        """
        Decorator to create tempfile to write destination content and set
        `self.__tempfile`.

        Return Callable with file descriptor in `kwargs['fd']`.
        """
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            kwargs['fd'], self._tmpfile = tempfile.mkstemp(
                dir=self.module.tmpdir)
            self.module.add_cleanup_file(self._tmpfile)
            res = func(self, *args, **kwargs)
            os.close(kwargs['fd'])
            return res
        return wrapped
