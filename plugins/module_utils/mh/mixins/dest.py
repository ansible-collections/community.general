# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
# use local_* to write more reliable mock for os in units test
from os import stat as local_os_stat
from os import access as local_os_access
from os.path import isfile as local_os_path_is_file
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException
from ansible_collections.community.general.plugins.module_utils.mh.deco import cause_changes, check_mode_skip

# Python 2 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


class DestFileChecks(object):
    """
    Standard checks for working with destionations files on managed nodes.
    """

    class NotExists(ModuleHelperException):
        """Explicit error for non existent destination file."""
        pass

    class NotCreatable(ModuleHelperException):
        """
        Explicit error for destinations files that have not writeable parent.
        """
        pass

    class NotReadable(ModuleHelperException):
        """Explicit error when the destination is not readable."""
        pass

    class NotWriteable(ModuleHelperException):
        """Explicit error for not writable destination file."""
        pass

    class NotRegularFile(ModuleHelperException):
        """Explicit error for destination file that are not regular file."""
        pass

    class CanNotCreateBackup(ModuleHelperException):
        """
        Explicit error when a destination file backup can not be created.
        (This is when the destination file parent's is not writeable.)
        """
        pass

    def __init__(self, dest):
        # type: (str) -> None
        """
        Does the following checks on the file that given by `dest` full path :

        - is exists
        - has writable parent
        - is readable
        - is writable
        - is regular file
        """
        self._dest = dest

        self._def_exists()  # Must be done in first (required by other)
        self._def_writeable_parent()
        self._def_readable()
        self._def_writeable()
        self._def_regular()

    @property
    def exists(self):
        # type: () -> bool
        """`True` if the destination file exists."""
        return self._exists

    @property
    def writeable_parent(self):
        # type: () -> bool
        """`True` if the destination file parent's is writeable. """
        return self._writeable_parent

    @property
    def readable(self):
        # type: () -> bool
        """`True` if the destination file exists and is readable."""
        return self._readable

    @property
    def writeable(self):
        # type: () -> bool
        """
        `True` if the destination file exists and is writeable.
        Also `True` if it does not exists but its parent is writable.
        """
        return self._writeable

    @property
    def regular(self):
        # type: () -> bool
        """
        `True` if the destination file is a regular file.
        """
        return self._regular

    def infos(self):
        # type: () -> dict
        """
        Get some facts about the state of the destination file in the following
        `dict` items :

        - `can_create` : True if it not exists and if its parent has writeable,
                         else False.
        - `can_read`   : True if it exists, is readable and is regular file,
                         else False.
        - `can_write`  : True if it exists, is writeable and is regular file or
                         if it not exists but its parent directory is writeable.
        - `can_backup` : True if it exists, is regular file and its parent
                         directory is writeable, else False.
        - `is_regular` : True if it a regular file, else False.
        """
        return {
            'can_create': (self._writeable_parent and not self._exists),
            'can_read': (self._readable and self._regular),
            'can_write': (self._writeable and (self._regular or not self._exists)),
            'can_backup': (self._writeable_parent and self._exists and self._readable and self._regular),
            'is_regular': self._regular,
        }

    def check(self, create=False, backup=False):
        # type: (bool, bool) -> None
        """
        Ensuring some facts about the destination file full path and raise an
        explicit error if something was wrong.

        If the destination file does not exists :
        - If `create` is `False`, raise `NotExists`.
        - Else, if `create` is `True` but its parent is not writable, raise
          `NotCreatable`.
        Else :
        - If destination file is not regular, raise `NotRegularFile`.
        - If destination file is not readable , raise `NotReadable`.
        - If destination file is not writable, raise `NotWriteable`.

        If `backup` is `True` and if the parent is not writeable, raise
        `CanNotCreateBackup`.
        """
        infos = self.infos()
        if self.exists:
            if not infos['is_regular']:
                raise self.NotRegularFile(msg="{0} is not a regular file !".format(self._dest))
            if not infos['can_read']:
                raise self.NotReadable(msg="Can not read dest file {0} !".format(self._dest))
            if not infos['can_write']:
                raise self.NotWriteable(msg="Can not write dest file {0} !".format(self._dest))
            if backup and not infos['can_backup']:
                raise self.CanNotCreateBackup(msg="Can not create backup for {0} !".format(self._dest))
        else:
            if create:
                if not infos['can_create']:
                    raise self.NotCreatable(msg="Can not create dest file {0} !".format(self._dest))
            else:
                raise self.NotExists(msg="{0} does not exists !".format(self._dest))

    def _def_exists(self):
        try:
            local_os_stat(self._dest)
        except FileNotFoundError:
            self._exists = False
        else:
            self._exists = True

    def _def_writeable_parent(self):
        self._writeable_parent = local_os_access(os.path.dirname(self._dest), os.W_OK)

    def _def_readable(self):
        if self._exists:
            self._readable = local_os_access(self._dest, os.R_OK)
        else:
            self._readable = False

    def _def_writeable(self):
        if self._exists:
            self._writeable = local_os_access(self._dest, os.W_OK)
        else:
            self._writeable = self._writeable_parent

    def _def_regular(self):
        if self._exists:
            self._regular = local_os_path_is_file(self._dest)
        else:
            self._regular = False


class DestFileMixin(object):
    """
    Extends `ModuleHelper` by adding some features that help to quickly write
    and maintain modules that work with a destination file. It implements most
    common tasks that can be done in a standard way (do some checks on the
    destination file, handle creation allowing, set fs attributes and do
    backup).

    In common case, the only things that you need to do in you module is
    implementing the method `__process_data__`.

    The logic that this helper implements can be summarised by these step :
    1. `__read_dest__`
    2. `__process_data__`
    3. `__update_dest__`
    """

    # /!\ WARN : Can add new default value but avoid to modifying them after
    #            because that could break some modules that use them.
    _DESTFILE_MIXIN_DEFAULT_MODULE_PARAMS = {
        'argument_spec': {
            'path': {'type': 'path', 'required': True, 'aliases': ['dest']},
            'allow_creation': {'type': 'bool', 'default': False},
            'backup': {'type': 'bool', 'default': False},
        },
        'supports_check_mode': True,
        'add_file_common_args': True,
    }

    def __init__(self, module=None):
        # type: (dict | AnsibleModule | None) -> None
        self.raw_content = None  # type: bytes
        self._dest_check = None  # type: DestFileChecks
        self._dest_infos = None  # type: dict
        self._dest_attrs = None   # type: dict
        super(DestFileMixin, self).__init__(module)

    def __init_module__(self):
        # type: () -> None
        """
        Checks and get some informations about the destination file.
        """
        super(DestFileMixin, self).__init_module__()
        self.vars.set('created', False)
        self._dest_check = DestFileChecks(self.vars['path'])
        self._dest_check.check(self.vars['allow_creation'], self.vars['backup'])
        self._dest_infos = self._dest_check.infos()
        self._dest_attrs = self.module.load_file_common_arguments(self.module.params)

    def __run__(self):
        # type: () -> None
        self.__read_dest__()
        self.__process_data__()

    def __read_dest__(self):
        # type: () -> None
        """
        Open the destination file and put its binary raw contents in
        `self.raw_content`.
        """
        try:
            with open(self.vars['path'], 'rb') as file:
                self.raw_content = file.read()
        except FileNotFoundError:
            pass

    def __process_data__(self):
        # type: () -> None
        """
        Implement this in your module to define how to process data the
        destination file.

        When you run this method, you get binary raw data from your destination
        file into `self.raw_content` method.

        After you process it, do not write the result directly in the
        destination file (it is automatically done later with the
        content of `self.raw_content`) instead, put your result in binary form
        `self.raw_content`.

        It is expected that this method manage the module change flag if data
        was updated. A good way do de this is by adding an item in `self.vars`
        which can handle diffs and changes on data.
        """
        raise NotImplementedError()

    def __quit_module__(self):
        # type: () -> None
        self.__update_dest__()

    def __update_dest__(self):
        # type: () -> None
        if self.has_changed():
            self._write_temp_file()
            self._backup_dest()
            self._replace_dest_with_temp()
            self.vars.set('created', self._dest_infos['can_create'])
        self._update_dest_fs_attributes()

    @check_mode_skip
    def _write_temp_file(self):
        # type: () -> None
        """
        Write the binary data from `self.raw_content` into an Ansible temp
        file.
        """
        fd, self._tmpfile = tempfile.mkstemp(dir=self.module.tmpdir)
        os.write(fd, self.raw_content)
        self.module.add_cleanup_file(self._tmpfile)
        os.close(fd)

    @check_mode_skip
    def _backup_dest(self):
        # type: () -> None
        if self._dest_infos['can_backup'] and self.vars.get('backup'):
            self.vars.set('backup_file',
                          self.module.backup_local(self.vars['path']))

    @cause_changes(on_success=True)
    @check_mode_skip
    def _replace_dest_with_temp(self):
        # type: () -> None
        try:
            self.module.atomic_move(self._tmpfile, self.vars['path'])
        except Exception as ex:
            if self.vars.get('backup_file'):
                self.module.add_cleanup_file(self.vars.backup_file)
            raise ex

    def _update_dest_fs_attributes(self):
        # type: () -> None
        attr_changes = {'before': {}, 'after': {}}
        self.module.set_fs_attributes_if_different(self._dest_attrs,
                                                   self.changed,
                                                   diff=attr_changes)
        for key, val in attr_changes['after'].items():
            if key == 'dest' or key == 'path':
                continue
            if val is not None:
                self.vars.meta(key).set(diff=True, change=True, output=True)
                self.vars.set(key, val)
        self.changed = self.has_changed()

    @classmethod
    def with_default_params(cls, params):
        # type (dict) -> dict
        """
        Provides a merge of yours module arguments with these implemented by
        this helper (also exists a corresponding doc fragment
        `dest_file_module`).

        Use it like this in your module description :
        ```
        class YourModule(DestFileModuleHelper):
            module = DestFileModuleHelper.with_default_params({
                'argument_spec': {
                    'value': {'type': 'str', 'required': True},
                },
            })
        ```
        """
        return dict_merge(cls._DESTFILE_MIXIN_DEFAULT_MODULE_PARAMS, params)
