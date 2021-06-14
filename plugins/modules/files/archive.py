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
        The current state of the archived file.
        If 'absent', then no source files were found and the archive does not exist.
        If 'compress', then the file source file is in the compressed state.
        If 'archive', then the source file or paths are currently archived.
        If 'incomplete', then an archive was created, but not all source paths were found.
    type: str
    returned: always
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
from ansible.module_utils.six import PY3


LZMA_IMP_ERR = None
if PY3:
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

PY27 = version_info[0:2] >= (2, 7)


def to_b(s):
    return to_bytes(s, errors='surrogate_or_strict')


def to_n(s):
    return to_native(s, errors='surrogate_or_strict')


def to_na(s):
    return to_native(s, errors='surrogate_or_strict', encoding='ascii')


def expand_paths(paths):
    expanded_path = []
    is_globby = False
    for path in paths:
        b_path = to_b(path)
        if b'*' in b_path or b'?' in b_path:
            e_paths = glob.glob(b_path)
            is_globby = True

        else:
            e_paths = [b_path]
        expanded_path.extend(e_paths)
    return expanded_path, is_globby


def matches_exclusion_patterns(path, exclusion_patterns):
    return any(fnmatch(path, p) for p in exclusion_patterns)


def is_archive(path):
    return re.search(br'\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip)$', os.path.basename(path), re.IGNORECASE)


PATH_SEP = to_b(os.sep)


@six.add_metaclass(abc.ABCMeta)
class Archive(abc.ABCMeta):
    def __init__(self, module):
        self.destination = to_b(module.params['dest']) if module.params['dest'] else None
        self.exclude_paths = module.params['exclude_path']
        self.exclusion_patterns = module.params['exclusion_patterns'] or []
        self.format = module.params['format']
        self.must_archive = module.params['force_archive']
        self.paths = module.params['path']

        self.targets = []
        self.changed = False
        self.errors = []
        self.excluded = []
        self.file = None
        self.missing = []
        self.root = b''
        self.state = 'absent'
        self.successes = []

        self.expanded_paths, has_globs = expand_paths(self.paths)

        if not self.expanded_paths:
            module.fail_json(
                path=', '.join(self.paths),
                expanded_paths=to_native(b', '.join(self.expanded_paths), errors='surrogate_or_strict'),
                msg='Error, no source paths were found'
            )

        # Only attempt to expand the exclude paths if it exists
        self.expanded_exclude_paths = expand_paths(self.exclude_paths)[0] if self.exclude_paths else []

        if not self.must_archive:
            # If we actually matched multiple files or TRIED to, then treat this as a multi-file archive
            self.must_archive = any([has_globs, os.path.isdir(self.expanded_paths[0]), len(self.expanded_paths) > 1])
        # Default created file name (for single-file archives) to <file>.<format>
        if not self.destination and not self.must_archive:
            self.destination = b'%s.%s' % (self.expanded_paths[0], to_b(self.format))
        # Force archives to specify 'dest'
        if self.must_archive and not self.destination:
            module.fail_json(
                dest=to_na(self.destination),
                path=', '.join(self.paths),
                msg='Error, must specify "dest" when archiving multiple files or trees'
            )

    def find_archive_paths(self):
        for path in self.expanded_paths:
            # Use the longest common directory name among all the files
            # as the archive root path
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
                        msg='Error, created archive can not be contained in source paths when remove=True'
                    )

            if path in self.expanded_exclude_paths:
                self.excluded.append(path)
            else:
                if os.path.lexists(path):
                    self.targets.append(path)
                else:
                    self.missing.append(path)

    def add_targets(self):
        self.open()

        try:
            match_root = re.compile(br'^%s' % re.escape(self.root))
            for path in self.targets:
                if os.path.isdir(path):
                    for directory_path, directory_names, file_names in os.walk(path, topdown=True):
                        if not directory_path.endswith(PATH_SEP):
                            directory_path += PATH_SEP

                        for directory_name in directory_names:
                            full_path = directory_path + directory_name
                            archive_name = to_n(match_root.sub(b'', full_path))
                            self.add(to_na(full_path), archive_name)

                        for file_name in file_names:
                            full_path = directory_path + file_name
                            archive_name = to_n(match_root.sub(b'', full_path))

                            # The previous code logged ``b_path`` in case of error,
                            # but it seems more informative to log the full path here
                            self.add(to_na(full_path), archive_name)
                else:
                    path = to_na(path)
                    archive_name = to_n(match_root.sub(b'', path))
                    self.add(path, archive_name)
        except Exception as e:
            archive_format = 'zip' if self.format == 'zip' else ('tar.' + self.format)
            self.module.fail_json(
                msg='Error when writing %s archive at %s: %s' % (archive_format, self.destination, to_na(e)),
                exception=format_exc()
            )

        self.close()

    def add_one(self, path):
        # No source or compressed file
        if not os.path.exists(path):
            if self.destination_exists():
                # if it already exists and the source file isn't there, consider this done
                self.state = 'compress'
            else:
                self.state = 'absent'
        else:
            if self.module.check_mode:
                if not self.destination_exists():
                    self.changed = True
            else:
                size = self.destination_size()
                try:
                    if self.format in ('zip', 'tar'):
                        self.open()
                        self.add(to_na(path), to_n(path[len(self.root):]))
                        self.close()
                        self.state = 'archive'  # because all zip files are archives (all tar files are archives too)
                    else:
                        compressor = self._get_compressor()
                        with open(path, 'rb') as f_in:
                            with compressor(to_na(self.destination), 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    self.successes.append(path)
                except OSError as e:
                    self.module.fail_json(
                        path=to_n(path),
                        dest=to_n(self.destination),
                        msg='Unable to write to compressed file: %s' % to_n(e), exception=format_exc()
                    )

                # Rudimentary check: If size changed then file changed. Not perfect, but easy.
                if self.destination_size() != size:
                    self.changed = True

            self.state = 'compress'

    def _get_compressor(self):
        if self.format == 'gz':
            func = gzip.open
        elif self.format == 'bz2':
            func = bz2.BZ2File
        elif self.format == 'xz':
            func = lzma.LZMAFile
        else:
            raise ValueError("%s has no compression function" % self.format)

        return func

    def remove_targets(self):
        for path in self.successes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except OSError:
                self.errors.append(to_n(path))

        for path in self.expanded_paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
            except OSError:
                self.errors.append(to_n(path))

        if self.errors:
            self.module.fail_json(
                dest=to_n(self.destination), msg='Error deleting some source files: ', files=self.errors
            )

    def has_archive_paths(self):
        return bool(self.targets)

    def has_excluded_or_unfound_paths(self):
        return bool(self.missing)

    def destination_exists(self):
        return self.destination and os.path.exists(self.destination)

    def destination_size(self):
        return os.path.getsize(self.destination) if self.destination_exists() else 0

    @property
    def result(self):
        return {
            'archived': [to_n(p) for p in self.successes],
            'dest': to_n(self.destination),
            'changed': self.changed,
            'state': self.state,
            'arcroot': to_n(self.root),
            'missing': [to_n(p) for p in self.missing],
            'expanded_paths': [to_n(p) for p in self.expanded_paths],
            'expanded_exclude_paths': [to_n(p) for p in self.expanded_exclude_paths],
        }

    @abc.abstractmethod
    def add(self, path, archive_name):
        pass

    @abc.abstractmethod
    def contains(self, name):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class ZipArchive(Archive):
    def __init__(self, module):
        super(ZipArchive, self).__init__(module)

    def filter(self, path):
        return matches_exclusion_patterns(path, self.exclusion_patterns)

    def contains(self, name):
        try:
            self.file.getinfo(name)
        except KeyError:
            return False
        return True

    def add(self, path, archive_name):
        try:
            if not self.filter(path):
                self.file.write(path, archive_name)
        except Exception as e:
            self.errors.append('%s: %s' % (path, to_native(e)))

        if self.contains(archive_name):
            self.successes.append(path)

    def open(self):
        self.file = zipfile.ZipFile(to_na(self.destination), 'w', zipfile.ZIP_DEFLATED, True)

    def close(self):
        self.file.close()


class TarArchive(Archive):
    def __init__(self, module):
        super(TarArchive, self).__init__(module)

        self.fileIO = None

    def filter(self, path_or_tarinfo):
        if PY27:
            return self._py27_filter(path_or_tarinfo)
        else:
            return self._py26_filter(path_or_tarinfo)

    def _py27_filter(self, tarinfo):
        return None if matches_exclusion_patterns(tarinfo.name, self.exclusion_patterns) else tarinfo

    def _py26_filter(self, path):
        return matches_exclusion_patterns(path, self.exclusion_patterns)

    def contains(self, name):
        try:
            self.file.getmember(name)
        except KeyError:
            return False
        return True

    def add(self, path, archive_name):
        try:
            if PY27:
                self.file.add(path, archive_name, recursive=False, filter=self.filter)
            else:
                self.file.add(path, archive_name, recursive=False, exclude=self.filter)
        except Exception as e:
            self.errors.append('%s: %s' % (path, to_native(e)))

        if self.contains(archive_name):
            self.successes.append(path)

    def open(self):
        if self.format in ('gz','bz2'):
            self.file = tarfile.open(to_na(self.destination), 'w|' + self.format)
        # python3 tarfile module allows xz format but for python2 we have to create the tarfile
        # in memory and then compress it with lzma.
        elif self.format == 'xz':
            self.fileIO = io.BytesIO()
            self.file = tarfile.open(fileobj=self.fileIO, mode='w')
        # Or plain tar archiving
        elif self.format == 'tar':
            self.file = tarfile.open(to_na(self.destination), 'w')
        else:
            self.module.fail_json(msg="%s is not a valid archive format" % self.format)

    def close(self):
        self.arcfile.close()
        if self.format == 'xz':
            with lzma.open(to_n(self.destination), 'wb') as f:
                f.write(self.arcfileIO.getvalue())
            self.arcfileIO.close()


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
            exclude_path=dict(type='list', elements='path'),
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

    remove = module.params['remove']

    archive = get_archive(module)

    archive.find_archive_paths()

    if not archive.has_archive_paths():
        # Previous behavior fell through to else instead of moving straight to exit_json
        if archive.destination_exists():
            archive.state = 'archive' if is_archive(archive.destination) else 'compress'
    elif archive.must_archive:
        size = archive.destination_size()

        if module.check_mode:
            archive.changed = True
        else:
            archive.add_targets()

            if archive.errors:
                module.fail_json(
                    msg='Errors when writing archive at %s: %s' % (
                        to_n(archive.destination), '; '.join(archive.errors)
                    )
                )

            archive.state = 'archive'

        # Previous behavior set this before archiving causing it to be overwritten
        if archive.has_excluded_or_unfound_paths():
            archive.state = 'incomplete'

        if all([archive.state in ['archive', 'incomplete'], remove, not module.check_mode]):
            archive.remove_targets()

        # Rudimentary check: If size changed then file changed. Not perfect, but easy.
        if not module.check_mode and archive.destination_size() != size:
            archive.changed = True

        if archive.successes and archive.state != 'incomplete':
            archive.state = 'archive'
    else:
        path = archive.expanded_paths[0]
        archive.add_one(path)

        if remove and not module.check_mode:
            try:
                os.remove(path)

            except OSError as e:
                module.fail_json(
                    path=to_n(path),
                    msg='Unable to remove source file: %s' % to_native(e), exception=format_exc()
                )
    try:
        file_args = module.load_file_common_arguments(module.params, path=archive.destination)
    except TypeError:
        # The path argument is only supported in Ansible-base 2.10+. Fall back to
        # pre-2.10 behavior for older Ansible versions.
        module.params['path'] = archive.destination
        file_args = module.load_file_common_arguments(module.params)

    archive.changed = module.set_fs_attributes_if_different(file_args, archive.changed)

    module.exit_json(**archive.result)


if __name__ == '__main__':
    main()
