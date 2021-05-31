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
from ansible.module_utils._text import to_bytes, to_native
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


def get_filter(exclusion_patterns, format):
    def zip_filter(path):
        return matches_exclusion_patterns(path, exclusion_patterns)

    def tar_filter(tarinfo):
        return None if matches_exclusion_patterns(tarinfo.name, exclusion_patterns) else tarinfo

    return zip_filter if format == 'zip' or not PY27 else tar_filter


def get_archive_contains(format):
    def archive_contains(archive, name):
        try:
            if format == 'zip':
                archive.getinfo(name)
            else:
                archive.getmember(name)
        except KeyError:
            return False

        return True

    return archive_contains


def get_add_to_archive(format, filter):
    def add_to_zip_archive(archive_file, path, archive_name):
        try:
            if not filter(path):
                archive_file.write(path, archive_name)
        except Exception as e:
            return e

        return None

    def add_to_tar_archive(archive_file, path, archive_name):
        try:
            if PY27:
                archive_file.add(path, archive_name, recursive=False, filter=filter)
            else:
                archive_file.add(path, archive_name, recursive=False, exclude=filter)
        except Exception as e:
            return e

        return None

    return add_to_zip_archive if format == 'zip' else add_to_tar_archive


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

    params = module.params
    check_mode = module.check_mode
    paths = params['path']
    dest = params['dest']
    b_dest = None if not dest else to_b(dest)
    exclude_paths = params['exclude_path']
    remove = params['remove']

    fmt = params['format']
    b_fmt = to_b(fmt)
    force_archive = params['force_archive']
    changed = False
    state = 'absent'

    exclusion_patterns = params['exclusion_patterns'] or []

    # Simple or archive file compression (inapplicable with 'zip' since it's always an archive)
    b_successes = []

    # Fail early
    if not HAS_LZMA and fmt == 'xz':
        module.fail_json(msg=missing_required_lib("lzma or backports.lzma", reason="when using xz format"),
                         exception=LZMA_IMP_ERR)
        module.fail_json(msg="lzma or backports.lzma is required when using xz format.")

    b_expanded_paths, globby = expand_paths(paths)
    if not b_expanded_paths:
        return module.fail_json(
            path=', '.join(paths),
            expanded_paths=to_native(b', '.join(b_expanded_paths), errors='surrogate_or_strict'),
            msg='Error, no source paths were found'
        )

    # Only attempt to expand the exclude paths if it exists
    b_expanded_exclude_paths = expand_paths(exclude_paths)[0] if exclude_paths else []

    filter = get_filter(exclusion_patterns, fmt)
    archive_contains = get_archive_contains(fmt)
    add_to_archive = get_add_to_archive(fmt, filter)

    # Only try to determine if we are working with an archive or not if we haven't set archive to true
    if not force_archive:
        # If we actually matched multiple files or TRIED to, then
        # treat this as a multi-file archive
        archive = globby or os.path.isdir(b_expanded_paths[0]) or len(b_expanded_paths) > 1
    else:
        archive = True

    # Default created file name (for single-file archives) to
    # <file>.<format>
    if not b_dest and not archive:
        b_dest = b'%s.%s' % (b_expanded_paths[0], b_fmt)

    # Force archives to specify 'dest'
    if archive and not b_dest:
        module.fail_json(dest=dest, path=', '.join(paths), msg='Error, must specify "dest" when archiving multiple files or trees')

    b_sep = to_b(os.sep)

    b_archive_paths = []
    b_missing = []
    b_arcroot = b''

    for b_path in b_expanded_paths:
        # Use the longest common directory name among all the files
        # as the archive root path
        if b_arcroot == b'':
            b_arcroot = os.path.dirname(b_path) + b_sep
        else:
            for i in range(len(b_arcroot)):
                if b_path[i] != b_arcroot[i]:
                    break

            if i < len(b_arcroot):
                b_arcroot = os.path.dirname(b_arcroot[0:i + 1])

            b_arcroot += b_sep

        # Don't allow archives to be created anywhere within paths to be removed
        if remove and os.path.isdir(b_path):
            b_path_dir = b_path
            if not b_path.endswith(b'/'):
                b_path_dir += b'/'

            if b_dest.startswith(b_path_dir):
                module.fail_json(
                    path=', '.join(paths),
                    msg='Error, created archive can not be contained in source paths when remove=True'
                )

        if os.path.lexists(b_path) and b_path not in b_expanded_exclude_paths:
            b_archive_paths.append(b_path)
        else:
            b_missing.append(b_path)

    # No source files were found but the named archive exists: are we 'compress' or 'archive' now?
    if len(b_missing) == len(b_expanded_paths) and b_dest and os.path.exists(b_dest):
        # Just check the filename to know if it's an archive or simple compressed file
        if re.search(br'\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip)$', os.path.basename(b_dest), re.IGNORECASE):
            state = 'archive'
        else:
            state = 'compress'

    # Multiple files, or globbiness
    elif archive:
        if not b_archive_paths:
            # No source files were found, but the archive is there.
            if os.path.lexists(b_dest):
                state = 'archive'
        elif b_missing:
            # SOME source files were found, but not all of them
            state = 'incomplete'

        archive = None
        size = 0
        errors = []

        if os.path.lexists(b_dest):
            size = os.path.getsize(b_dest)

        if state != 'archive':
            if check_mode:
                changed = True

            else:
                try:
                    # Slightly more difficult (and less efficient!) compression using zipfile module
                    if fmt == 'zip':
                        arcfile = zipfile.ZipFile(
                            to_na(b_dest),
                            'w',
                            zipfile.ZIP_DEFLATED,
                            True
                        )

                    # Easier compression using tarfile module
                    elif fmt == 'gz' or fmt == 'bz2':
                        arcfile = tarfile.open(to_na(b_dest), 'w|' + fmt)

                    # python3 tarfile module allows xz format but for python2 we have to create the tarfile
                    # in memory and then compress it with lzma.
                    elif fmt == 'xz':
                        arcfileIO = io.BytesIO()
                        arcfile = tarfile.open(fileobj=arcfileIO, mode='w')

                    # Or plain tar archiving
                    elif fmt == 'tar':
                        arcfile = tarfile.open(to_na(b_dest), 'w')

                    b_match_root = re.compile(br'^%s' % re.escape(b_arcroot))
                    for b_path in b_archive_paths:
                        if os.path.isdir(b_path):
                            # Recurse into directories
                            for b_dirpath, b_dirnames, b_filenames in os.walk(b_path, topdown=True):
                                if not b_dirpath.endswith(b_sep):
                                    b_dirpath += b_sep

                                for b_dirname in b_dirnames:
                                    b_fullpath = b_dirpath + b_dirname
                                    n_fullpath = to_na(b_fullpath)
                                    n_arcname = to_native(b_match_root.sub(b'', b_fullpath), errors='surrogate_or_strict')

                                    err = add_to_archive(arcfile, n_fullpath, n_arcname)
                                    if err:
                                        errors.append('%s: %s' % (n_fullpath, to_native(err)))

                                for b_filename in b_filenames:
                                    b_fullpath = b_dirpath + b_filename
                                    n_fullpath = to_na(b_fullpath)
                                    n_arcname = to_n(b_match_root.sub(b'', b_fullpath))

                                    err = add_to_archive(arcfile, n_fullpath, n_arcname)
                                    if err:
                                        errors.append('Adding %s: %s' % (to_native(b_path), to_native(err)))

                                    if archive_contains(arcfile, n_arcname):
                                        b_successes.append(b_fullpath)
                        else:
                            path = to_na(b_path)
                            arcname = to_n(b_match_root.sub(b'', b_path))

                            err = add_to_archive(arcfile, path, arcname)
                            if err:
                                errors.append('Adding %s: %s' % (to_native(b_path), to_native(err)))

                            if archive_contains(arcfile, arcname):
                                b_successes.append(b_path)

                except Exception as e:
                    expanded_fmt = 'zip' if fmt == 'zip' else ('tar.' + fmt)
                    module.fail_json(
                        msg='Error when writing %s archive at %s: %s' % (expanded_fmt, dest, to_native(e)),
                        exception=format_exc()
                    )

                if arcfile:
                    arcfile.close()
                    state = 'archive'

                if fmt == 'xz':
                    with lzma.open(b_dest, 'wb') as f:
                        f.write(arcfileIO.getvalue())
                    arcfileIO.close()

                if errors:
                    module.fail_json(msg='Errors when writing archive at %s: %s' % (dest, '; '.join(errors)))

        if state in ['archive', 'incomplete'] and remove:
            for b_path in b_successes:
                try:
                    if os.path.isdir(b_path):
                        shutil.rmtree(b_path)
                    elif not check_mode:
                        os.remove(b_path)
                except OSError:
                    errors.append(to_native(b_path))

            for b_path in b_expanded_paths:
                try:
                    if os.path.isdir(b_path):
                        shutil.rmtree(b_path)
                except OSError:
                    errors.append(to_native(b_path))

            if errors:
                module.fail_json(dest=dest, msg='Error deleting some source files: ', files=errors)

        # Rudimentary check: If size changed then file changed. Not perfect, but easy.
        if not check_mode and os.path.getsize(b_dest) != size:
            changed = True

        if b_successes and state != 'incomplete':
            state = 'archive'

    # Simple, single-file compression
    else:
        b_path = b_expanded_paths[0]

        # No source or compressed file
        if not (os.path.exists(b_path) or os.path.lexists(b_dest)):
            state = 'absent'

        # if it already exists and the source file isn't there, consider this done
        elif not os.path.lexists(b_path) and os.path.lexists(b_dest):
            state = 'compress'

        else:
            if module.check_mode:
                if not os.path.exists(b_dest):
                    changed = True
            else:
                size = 0
                f_in = f_out = arcfile = None

                if os.path.lexists(b_dest):
                    size = os.path.getsize(b_dest)

                try:
                    if fmt == 'zip':
                        arcfile = zipfile.ZipFile(
                            to_na(b_dest),
                            'w',
                            zipfile.ZIP_DEFLATED,
                            True
                        )
                        arcfile.write(
                            to_na(b_path),
                            to_n(b_path[len(b_arcroot):])
                        )
                        arcfile.close()
                        state = 'archive'  # because all zip files are archives
                    elif fmt == 'tar':
                        arcfile = tarfile.open(to_na(b_dest), 'w')
                        arcfile.add(to_na(b_path))
                        arcfile.close()
                    else:
                        f_in = open(b_path, 'rb')

                        n_dest = to_na(b_dest)
                        if fmt == 'gz':
                            f_out = gzip.open(n_dest, 'wb')
                        elif fmt == 'bz2':
                            f_out = bz2.BZ2File(n_dest, 'wb')
                        elif fmt == 'xz':
                            f_out = lzma.LZMAFile(n_dest, 'wb')
                        else:
                            raise OSError("Invalid format")

                        shutil.copyfileobj(f_in, f_out)

                    b_successes.append(b_path)

                except OSError as e:
                    module.fail_json(
                        path=to_native(b_path),
                        dest=dest,
                        msg='Unable to write to compressed file: %s' % to_native(e), exception=format_exc()
                    )

                if arcfile:
                    arcfile.close()
                if f_in:
                    f_in.close()
                if f_out:
                    f_out.close()

                # Rudimentary check: If size changed then file changed. Not perfect, but easy.
                if os.path.getsize(b_dest) != size:
                    changed = True

            state = 'compress'

        if remove and not check_mode:
            try:
                os.remove(b_path)

            except OSError as e:
                module.fail_json(
                    path=to_native(b_path),
                    msg='Unable to remove source file: %s' % to_native(e), exception=format_exc()
                )

    try:
        file_args = module.load_file_common_arguments(params, path=b_dest)
    except TypeError:
        # The path argument is only supported in Ansible-base 2.10+. Fall back to
        # pre-2.10 behavior for older Ansible versions.
        params['path'] = b_dest
        file_args = module.load_file_common_arguments(params)

    if not check_mode:
        changed = module.set_fs_attributes_if_different(file_args, changed)

    module.exit_json(
        archived=[to_n(p) for p in b_successes],
        dest=dest,
        changed=changed,
        state=state,
        arcroot=to_n(b_arcroot),
        missing=[to_n(p) for p in b_missing],
        expanded_paths=[to_n(p) for p in b_expanded_paths],
        expanded_exclude_paths=[to_n(p) for p in b_expanded_exclude_paths],
    )


if __name__ == '__main__':
    main()
