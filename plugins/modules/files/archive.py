#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Ben Doherty <bendohmv@gmail.com>
# Sponsored by Oomph, Inc. http://www.oomphinc.com
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: archive
short_description: Creates a compressed archive of one or more files or trees
extends_documentation_fragment: files
description:
    - Creates or extends an archive.
    - The source and archive are on the remote host, and the archive I(is not) copied to the local host.
    - Source files can be deleted after archival by specifying I(remove=True).
options:
  path:
    description:
      - Remote absolute path, glob, or list of paths or globs for the file or files to compress or archive.
    type: list
    elements: path
    required: true
  format:
    description:
      - The type of compression to use.
      - Support for xz was added in Ansible 2.5.
    type: str
    choices: [ bz2, gz, tar, xz, zip ]
    default: gz
  dest:
    description:
      - The file name of the destination archive. The parent directory must exists on the remote host.
      - This is required when C(path) refers to multiple files by either specifying a glob, a directory or multiple paths in a list.
      - If the destination archive already exists, it will be truncated and overwritten.
    type: path
  exclude_path:
    description:
      - Remote absolute path, glob, or list of paths or globs for the file or files to exclude from I(path) list and glob expansion.
      - Use I(exclusion_patterns) to instead exclude files or subdirectories below any of the paths from the I(path) list.
    type: list
    elements: path
    default: []
  exclusion_patterns:
    description:
      - Glob style patterns to exclude files or directories from the resulting archive.
      - This differs from I(exclude_path) which applies only to the source paths from I(path).
    type: list
    elements: path
    version_added: 3.2.0
  force_archive:
    description:
      - Allows you to force the module to treat this as an archive even if only a single file is specified.
      - By default when a single file is specified it is compressed only (not archived).
      - Enable this if you want to use M(ansible.builtin.unarchive) on an archive of a single file created with this module.
    type: bool
    default: false
  remove:
    description:
      - Remove any added source files and trees after adding to archive.
    type: bool
    default: no
notes:
    - Requires tarfile, zipfile, gzip and bzip2 packages on target host.
    - Requires lzma or backports.lzma if using xz format.
    - Can produce I(gzip), I(bzip2), I(lzma) and I(zip) compressed files or archives.
seealso:
- module: ansible.builtin.unarchive
author:
- Ben Doherty (@bendoh)
'''

EXAMPLES = r'''
- name: Compress directory /path/to/foo/ into /path/to/foo.tgz
  community.general.archive:
    path: /path/to/foo
    dest: /path/to/foo.tgz

- name: Compress regular file /path/to/foo into /path/to/foo.gz and remove it
  community.general.archive:
    path: /path/to/foo
    remove: yes

- name: Create a zip archive of /path/to/foo
  community.general.archive:
    path: /path/to/foo
    format: zip

- name: Create a bz2 archive of multiple files, rooted at /path
  community.general.archive:
    path:
    - /path/to/foo
    - /path/wong/foo
    dest: /path/file.tar.bz2
    format: bz2

- name: Create a bz2 archive of a globbed path, while excluding specific dirnames
  community.general.archive:
    path:
    - /path/to/foo/*
    dest: /path/file.tar.bz2
    exclude_path:
    - /path/to/foo/bar
    - /path/to/foo/baz
    format: bz2

- name: Create a bz2 archive of a globbed path, while excluding a glob of dirnames
  community.general.archive:
    path:
    - /path/to/foo/*
    dest: /path/file.tar.bz2
    exclude_path:
    - /path/to/foo/ba*
    format: bz2

- name: Use gzip to compress a single archive (i.e don't archive it first with tar)
  community.general.archive:
    path: /path/to/foo/single.file
    dest: /path/file.gz
    format: gz

- name: Create a tar.gz archive of a single file.
  community.general.archive:
    path: /path/to/foo/single.file
    dest: /path/file.tar.gz
    format: gz
    force_archive: true
'''

RETURN = r'''
state:
    description:
        The state of the input C(path).
    type: str
    returned: always
dest_state:
    description:
      - The state of the I(dest) file.
      - C(absent) when the file does not exist.
      - C(archive) when the file is an archive.
      - C(compress) when the file is compressed, but not an archive.
      - C(incomplete) when the file is an archive, but some files under I(path) were not found.
    type: str
    returned: success
    version_added: 3.4.0
missing:
    description: Any files that were missing from the source.
    type: list
    returned: success
archived:
    description: Any files that were compressed or added to the archive.
    type: list
    returned: success
arcroot:
    description: The archive root.
    type: str
    returned: always
expanded_paths:
    description: The list of matching paths from paths argument.
    type: list
    returned: always
expanded_exclude_paths:
    description: The list of matching exclude paths from the exclude_path argument.
    type: list
    returned: always
'''

import abc
import bz2
import glob
import gzip
import io
import os
import re
import shutil
import tarfile
import zipfile
from fnmatch import fnmatch
from sys import version_info
from traceback import format_exc

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes, to_native
from ansible.module_utils import six


LZMA_IMP_ERR = None
if six.PY3:
    try:
        import lzma
        HAS_LZMA = True
    except ImportError:
        LZMA_IMP_ERR = format_exc()
        HAS_LZMA = False
else:
    try:
        from backports import lzma
        HAS_LZMA = True
    except ImportError:
        LZMA_IMP_ERR = format_exc()
        HAS_LZMA = False

PATH_SEP = to_bytes(os.sep)
PY27 = version_info[0:2] >= (2, 7)

STATE_ABSENT = 'absent'
STATE_ARCHIVED = 'archive'
STATE_COMPRESSED = 'compress'
STATE_INCOMPLETE = 'incomplete'


def _to_bytes(s):
    return to_bytes(s, errors='surrogate_or_strict')


def _to_native(s):
    return to_native(s, errors='surrogate_or_strict')


def _to_native_ascii(s):
    return to_native(s, errors='surrogate_or_strict', encoding='ascii')


def expand_paths(paths):
    expanded_path = []
    is_globby = False
    for path in paths:
        b_path = _to_bytes(path)
        if b'*' in b_path or b'?' in b_path:
            e_paths = glob.glob(b_path)
            is_globby = True
        else:
            e_paths = [b_path]
        expanded_path.extend(e_paths)
    return expanded_path, is_globby


def is_archive(path):
    return re.search(br'\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip)$', os.path.basename(path), re.IGNORECASE)


def legacy_filter(path, exclusion_patterns):
    return matches_exclusion_patterns(path, exclusion_patterns)


def matches_exclusion_patterns(path, exclusion_patterns):
    return any(fnmatch(path, p) for p in exclusion_patterns)


@six.add_metaclass(abc.ABCMeta)
class Archive(object):
    def __init__(self, module):
        self.module = module

        self.destination = _to_bytes(module.params['dest']) if module.params['dest'] else None
        self.exclusion_patterns = module.params['exclusion_patterns'] or []
        self.format = module.params['format']
        self.must_archive = module.params['force_archive']
        self.remove = module.params['remove']

        self.changed = False
        self.destination_state = STATE_ABSENT
        self.errors = []
        self.file = None
        self.root = b''
        self.successes = []
        self.targets = []
        self.not_found = []

        paths = module.params['path']
        self.expanded_paths, has_globs = expand_paths(paths)
        self.expanded_exclude_paths = expand_paths(module.params['exclude_path'])[0]

        self.paths = list(set(self.expanded_paths) - set(self.expanded_exclude_paths))

        if not self.paths:
            module.fail_json(
                path=', '.join(paths),
                expanded_paths=_to_native(b', '.join(self.expanded_paths)),
                expanded_exclude_paths=_to_native(b', '.join(self.expanded_exclude_paths)),
                msg='Error, no source paths were found'
            )

        if not self.must_archive:
            self.must_archive = any([has_globs, os.path.isdir(self.paths[0]), len(self.paths) > 1])

        if not self.destination and not self.must_archive:
            self.destination = b'%s.%s' % (self.paths[0], _to_bytes(self.format))

        if self.must_archive and not self.destination:
            module.fail_json(
                dest=_to_native(self.destination),
                path=', '.join(paths),
                msg='Error, must specify "dest" when archiving multiple files or trees'
            )

        self.original_size = self.destination_size()

    def add(self, path, archive_name):
        try:
            self._add(_to_native_ascii(path), _to_native(archive_name))
            if self.contains(_to_native(archive_name)):
                self.successes.append(path)
        except Exception as e:
            self.errors.append('%s: %s' % (_to_native_ascii(path), _to_native(e)))

    def add_single_target(self, path):
        if self.format in ('zip', 'tar'):
            archive_name = re.sub(br'^%s' % re.escape(self.root), b'', path)
            self.open()
            self.add(path, archive_name)
            self.close()
            self.destination_state = STATE_ARCHIVED
        else:
            try:
                f_out = self._open_compressed_file(_to_native_ascii(self.destination), 'wb')
                with open(path, 'rb') as f_in:
                    shutil.copyfileobj(f_in, f_out)
                f_out.close()
                self.successes.append(path)
                self.destination_state = STATE_COMPRESSED
            except (IOError, OSError) as e:
                self.module.fail_json(
                    path=_to_native(path),
                    dest=_to_native(self.destination),
                    msg='Unable to write to compressed file: %s' % _to_native(e), exception=format_exc()
                )

    def add_targets(self):
        self.open()
        try:
            match_root = re.compile(br'^%s' % re.escape(self.root))
            for target in self.targets:
                if os.path.isdir(target):
                    for directory_path, directory_names, file_names in os.walk(target, topdown=True):
                        if not directory_path.endswith(PATH_SEP):
                            directory_path += PATH_SEP

                        for directory_name in directory_names:
                            full_path = directory_path + directory_name
                            archive_name = match_root.sub(b'', full_path)
                            self.add(full_path, archive_name)

                        for file_name in file_names:
                            full_path = directory_path + file_name
                            archive_name = match_root.sub(b'', full_path)
                            self.add(full_path, archive_name)
                else:
                    archive_name = match_root.sub(b'', target)
                    self.add(target, archive_name)
        except Exception as e:
            if self.format in ('zip', 'tar'):
                archive_format = self.format
            else:
                archive_format = 'tar.' + self.format
            self.module.fail_json(
                msg='Error when writing %s archive at %s: %s' % (
                    archive_format, _to_native(self.destination), _to_native(e)
                ),
                exception=format_exc()
            )
        self.close()

        if self.errors:
            self.module.fail_json(
                msg='Errors when writing archive at %s: %s' % (_to_native(self.destination), '; '.join(self.errors))
            )

    def compare_with_original(self):
        self.changed |= self.original_size != self.destination_size()

    def destination_exists(self):
        return self.destination and os.path.exists(self.destination)

    def destination_readable(self):
        return self.destination and os.access(self.destination, os.R_OK)

    def destination_size(self):
        return os.path.getsize(self.destination) if self.destination_exists() else 0

    def find_targets(self):
        for path in self.paths:
            # Use the longest common directory name among all the files as the archive root path
            if self.root == b'':
                self.root = os.path.dirname(path) + PATH_SEP
            else:
                for i in range(len(self.root)):
                    if path[i] != self.root[i]:
                        break

                if i < len(self.root):
                    self.root = os.path.dirname(self.root[0:i + 1])

                self.root += PATH_SEP
            # Don't allow archives to be created anywhere within paths to be removed
            if self.remove and os.path.isdir(path):
                prefix = path if path.endswith(PATH_SEP) else path + PATH_SEP
                if self.destination.startswith(prefix):
                    self.module.fail_json(
                        path=', '.join(self.paths),
                        msg='Error, created archive can not be contained in source paths when remove=true'
                    )
            if not os.path.lexists(path):
                self.not_found.append(path)
            else:
                self.targets.append(path)

    def has_targets(self):
        return bool(self.targets)

    def has_unfound_targets(self):
        return bool(self.not_found)

    def remove_single_target(self, path):
        try:
            os.remove(path)
        except OSError as e:
            self.module.fail_json(
                path=_to_native(path),
                msg='Unable to remove source file: %s' % _to_native(e), exception=format_exc()
            )

    def remove_targets(self):
        for path in self.successes:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except OSError:
                    self.errors.append(_to_native(path))
        for path in self.paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
            except OSError:
                self.errors.append(_to_native(path))

        if self.errors:
            self.module.fail_json(
                dest=_to_native(self.destination), msg='Error deleting some source files: ', files=self.errors
            )

    def update_permissions(self):
        try:
            file_args = self.module.load_file_common_arguments(self.module.params, path=self.destination)
        except TypeError:
            # The path argument is only supported in Ansible-base 2.10+. Fall back to
            # pre-2.10 behavior for older Ansible versions.
            self.module.params['path'] = self.destination
            file_args = self.module.load_file_common_arguments(self.module.params)

        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    @property
    def result(self):
        return {
            'archived': [_to_native(p) for p in self.successes],
            'dest': _to_native(self.destination),
            'dest_state': self.destination_state,
            'changed': self.changed,
            'arcroot': _to_native(self.root),
            'missing': [_to_native(p) for p in self.not_found],
            'expanded_paths': [_to_native(p) for p in self.expanded_paths],
            'expanded_exclude_paths': [_to_native(p) for p in self.expanded_exclude_paths],
        }

    def _open_compressed_file(self, path, mode):
        f = None
        if self.format == 'gz':
            f = gzip.open(path, mode)
        elif self.format == 'bz2':
            f = bz2.BZ2File(path, mode)
        elif self.format == 'xz':
            f = lzma.LZMAFile(path, mode)
        else:
            self.module.fail_json(msg="%s is not a valid format" % self.format)

        return f

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def contains(self, name):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def _add(self, path, archive_name):
        pass


class ZipArchive(Archive):
    def __init__(self, module):
        super(ZipArchive, self).__init__(module)

    def close(self):
        self.file.close()

    def contains(self, name):
        try:
            self.file.getinfo(name)
        except KeyError:
            return False
        return True

    def open(self):
        self.file = zipfile.ZipFile(_to_native_ascii(self.destination), 'w', zipfile.ZIP_DEFLATED, True)

    def _add(self, path, archive_name):
        if not legacy_filter(path, self.exclusion_patterns):
            self.file.write(path, archive_name)


class TarArchive(Archive):
    def __init__(self, module):
        super(TarArchive, self).__init__(module)
        self.fileIO = None

    def close(self):
        self.file.close()
        if self.format == 'xz':
            with lzma.open(_to_native(self.destination), 'wb') as f:
                f.write(self.fileIO.getvalue())
            self.fileIO.close()

    def contains(self, name):
        try:
            self.file.getmember(name)
        except KeyError:
            return False
        return True

    def open(self):
        if self.format in ('gz', 'bz2'):
            self.file = tarfile.open(_to_native_ascii(self.destination), 'w|' + self.format)
        # python3 tarfile module allows xz format but for python2 we have to create the tarfile
        # in memory and then compress it with lzma.
        elif self.format == 'xz':
            self.fileIO = io.BytesIO()
            self.file = tarfile.open(fileobj=self.fileIO, mode='w')
        elif self.format == 'tar':
            self.file = tarfile.open(_to_native_ascii(self.destination), 'w')
        else:
            self.module.fail_json(msg="%s is not a valid archive format" % self.format)

    def _add(self, path, archive_name):
        def py27_filter(tarinfo):
            return None if matches_exclusion_patterns(tarinfo.name, self.exclusion_patterns) else tarinfo

        def py26_filter(path):
            return legacy_filter(path, self.exclusion_patterns)

        if PY27:
            self.file.add(path, archive_name, recursive=False, filter=py27_filter)
        else:
            self.file.add(path, archive_name, recursive=False, exclude=py26_filter)


def get_archive(module):
    if module.params['format'] == 'zip':
        return ZipArchive(module)
    else:
        return TarArchive(module)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='list', elements='path', required=True),
            format=dict(type='str', default='gz', choices=['bz2', 'gz', 'tar', 'xz', 'zip']),
            dest=dict(type='path'),
            exclude_path=dict(type='list', elements='path', default=[]),
            exclusion_patterns=dict(type='list', elements='path'),
            force_archive=dict(type='bool', default=False),
            remove=dict(type='bool', default=False),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )

    if not HAS_LZMA and module.params['format'] == 'xz':
        module.fail_json(
            msg=missing_required_lib("lzma or backports.lzma", reason="when using xz format"), exception=LZMA_IMP_ERR
        )

    check_mode = module.check_mode

    archive = get_archive(module)
    archive.find_targets()

    if not archive.has_targets():
        if archive.destination_exists():
            archive.destination_state = STATE_ARCHIVED if is_archive(archive.destination) else STATE_COMPRESSED
    elif archive.has_targets() and archive.must_archive:
        if check_mode:
            archive.changed = True
        else:
            archive.add_targets()
            archive.destination_state = STATE_INCOMPLETE if archive.has_unfound_targets() else STATE_ARCHIVED
            archive.compare_with_original()
            if archive.remove:
                archive.remove_targets()
    else:
        if check_mode:
            if not archive.destination_exists():
                archive.changed = True
        else:
            path = archive.paths[0]
            archive.add_single_target(path)
            archive.compare_with_original()
            if archive.remove:
                archive.remove_single_target(path)

    if archive.destination_exists():
        archive.update_permissions()

    module.exit_json(**archive.result)


if __name__ == '__main__':
    main()
