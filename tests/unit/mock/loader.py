# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.errors import AnsibleParserError
from ansible.parsing.dataloader import DataLoader
from ansible.module_utils._text import to_bytes, to_text


class DictDataLoader(DataLoader):

    def __init__(self, file_mapping=None):
        file_mapping = {} if file_mapping is None else file_mapping
        assert type(file_mapping) == dict

        super(DictDataLoader, self).__init__()

        self._file_mapping = file_mapping
        self._build_known_directories()
        self._vault_secrets = None

    def load_from_file(self, path, cache=True, unsafe=False):
        path = to_text(path)
        if path in self._file_mapping:
            return self.load(self._file_mapping[path], path)
        return None

    # TODO: the real _get_file_contents returns a bytestring, so we actually convert the
    #       unicode/text it's created with to utf-8
    def _get_file_contents(self, path):
        path = to_text(path)
        if path in self._file_mapping:
            return (to_bytes(self._file_mapping[path]), False)
        else:
            raise AnsibleParserError("file not found: %s" % path)

    def path_exists(self, path):
        path = to_text(path)
        return path in self._file_mapping or path in self._known_directories

    def is_file(self, path):
        path = to_text(path)
        return path in self._file_mapping

    def is_directory(self, path):
        path = to_text(path)
        return path in self._known_directories

    def list_directory(self, path):
        ret = []
        path = to_text(path)
        for x in (list(self._file_mapping.keys()) + self._known_directories):
            if x.startswith(path):
                if os.path.dirname(x) == path:
                    ret.append(os.path.basename(x))
        return ret

    def is_executable(self, path):
        # FIXME: figure out a way to make paths return true for this
        return False

    def _add_known_directory(self, directory):
        if directory not in self._known_directories:
            self._known_directories.append(directory)

    def _build_known_directories(self):
        self._known_directories = []
        for path in self._file_mapping:
            dirname = os.path.dirname(path)
            while dirname not in ('/', ''):
                self._add_known_directory(dirname)
                dirname = os.path.dirname(dirname)

    def push(self, path, content):
        rebuild_dirs = False
        if path not in self._file_mapping:
            rebuild_dirs = True

        self._file_mapping[path] = content

        if rebuild_dirs:
            self._build_known_directories()

    def pop(self, path):
        if path in self._file_mapping:
            del self._file_mapping[path]
            self._build_known_directories()

    def clear(self):
        self._file_mapping = dict()
        self._known_directories = []

    def get_basedir(self):
        return os.getcwd()

    def set_vault_secrets(self, vault_secrets):
        self._vault_secrets = vault_secrets
