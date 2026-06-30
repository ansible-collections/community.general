#!/usr/bin/python

# Copyright (c) 2016, Ben Doherty <bendohmv@gmail.com>
# Sponsored by Oomph, Inc. http://www.oomphinc.com
# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: archive
short_description: Creates a compressed archive of one or more files or trees
extends_documentation_fragment:
  - ansible.builtin.files
  - community.general._attributes
description:
  - Creates or extends an archive.
  - The source and archive are on the target host, and the archive I(is not) copied to the controller host.
  - Source files can be deleted after archival by specifying O(remove=True).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
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
    type: str
    choices: [bz2, gz, tar, xz, zip]
    default: gz
  dest:
    description:
      - The file name of the destination archive. The parent directory must exists on the remote host.
      - This is required when O(path) refers to multiple files by either specifying a glob, a directory or multiple paths
        in a list.
      - If the destination archive already exists, it is truncated and overwritten.
    type: path
  exclude_path:
    description:
      - Remote absolute path, glob, or list of paths or globs for the file or files to exclude from O(path) list and glob
        expansion.
      - Use O(exclusion_patterns) to instead exclude files or subdirectories below any of the paths from the O(path) list.
    type: list
    elements: path
    default: []
  exclusion_patterns:
    description:
      - Glob style patterns to exclude files or directories from the resulting archive.
      - This differs from O(exclude_path) which applies only to the source paths from O(path).
    type: list
    elements: path
    version_added: 3.2.0
  entry_owner:
    description:
      - When set, overrides the owner name (C(uname)) recorded on every entry inside the archive.
      - Useful for byte-reproducible tarballs. Has no effect on the on-disk source files.
      - Tar formats only (V(gz), V(bz2), V(xz), V(tar)).
    type: str
    version_added: 13.1.0
  entry_group:
    description:
      - When set, overrides the group name (C(gname)) recorded on every entry inside the archive.
      - Tar formats only.
    type: str
    version_added: 13.1.0
  entry_uid:
    description:
      - When set, overrides the numeric UID recorded on every entry inside the archive.
      - Tar formats only.
    type: int
    version_added: 13.1.0
  entry_gid:
    description:
      - When set, overrides the numeric GID recorded on every entry inside the archive.
      - Tar formats only.
    type: int
    version_added: 13.1.0
  entry_mtime:
    description:
      - When set, overrides the modification time (epoch seconds) recorded on every entry inside the archive.
      - Tar formats only.
    type: int
    version_added: 13.1.0
  entry_file_mode:
    description:
      - When set, overrides the mode recorded on every regular non-executable file entry inside the archive.
      - Accepts an octal string (for example V("0644")) or an integer.
      - Tar formats only.
    type: str
    version_added: 13.1.0
  entry_dir_mode:
    description:
      - When set, overrides the mode recorded on every directory entry inside the archive.
      - Accepts an octal string (for example V("0755")) or an integer.
      - Tar formats only.
    type: str
    version_added: 13.1.0
  entry_executable_mode:
    description:
      - When set, overrides the mode recorded on every file entry whose source file has any executable bit set.
      - Accepts an octal string (for example V("0755")) or an integer.
      - Tar formats only.
    type: str
    version_added: 13.1.0
  sort_entries:
    description:
      - When V(true), entries are added to the archive in lexical order by archive name rather than in filesystem walk order.
      - Required for byte-reproducible archives across different hosts and filesystems.
      - Tar formats only.
    type: bool
    default: false
    version_added: 13.1.0
  tar_format:
    description:
      - Override the tar header format. Defaults to the C(tarfile) module default (PAX).
      - PAX headers embed live timestamps that defeat byte-reproducibility; use V(gnu) or V(ustar) for reproducible output.
      - Tar formats only.
    type: str
    choices: [ustar, gnu, pax]
    version_added: 13.1.0
  gzip_mtime:
    description:
      - Override the modification time written into the gzip header (epoch seconds).
      - The standard gzip layer embeds the current time by default; set this (commonly to V(0)) for byte-reproducible C(.tar.gz) output.
      - Only meaningful when O(format=gz).
    type: int
    version_added: 13.1.0
  gzip_filename:
    description:
      - Override the original filename embedded in the gzip header. Pass an empty string (V("")) to strip the field entirely.
      - Only meaningful when O(format=gz).
    type: str
    version_added: 13.1.0
  gzip_level:
    description:
      - Compression level passed to gzip when O(format=gz). Range 1-9.
      - Only meaningful when O(format=gz) and one of the other C(gzip_*) options or any of the entry-normalization options is set, since these trigger the in-memory tar buffer path.
    type: int
    version_added: 13.1.0
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
    default: false
notes:
  - Can produce C(gzip), C(bzip2), C(lzma), and C(zip) compressed files or archives.
  - This module uses C(tarfile), C(zipfile), C(gzip), C(bz2), and C(lzma) packages on the target host to create archives. These are
    part of the Python standard library.
seealso:
  - module: ansible.builtin.unarchive
author:
  - Ben Doherty (@bendoh)
"""

EXAMPLES = r"""
- name: Compress directory /path/to/foo/ into /path/to/foo.tgz
  community.general.archive:
    path: /path/to/foo
    dest: /path/to/foo.tgz

- name: Compress regular file /path/to/foo into /path/to/foo.gz and remove it
  community.general.archive:
    path: /path/to/foo
    remove: true

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
"""

RETURN = r"""
state:
  description: The state of the input O(path).
  type: str
  returned: always
dest_state:
  description:
    - The state of the O(dest) file.
    - V(absent) when the file does not exist.
    - V(archive) when the file is an archive.
    - V(compress) when the file is compressed, but not an archive.
    - V(incomplete) when the file is an archive, but some files under O(path) were not found.
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
"""

import abc
import bz2
import glob
import gzip
import io
import lzma
import os
import re
import shutil
import tarfile
import zipfile
from fnmatch import fnmatch
from traceback import format_exc
from zipfile import BadZipFile
from zlib import crc32

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_native

STATE_ABSENT = "absent"
STATE_ARCHIVED = "archive"
STATE_COMPRESSED = "compress"
STATE_INCOMPLETE = "incomplete"


def common_path(paths):
    empty = b"" if paths and isinstance(paths[0], bytes) else ""

    return os.path.join(
        os.path.dirname(os.path.commonprefix([os.path.join(os.path.dirname(p), empty) for p in paths])), empty
    )


def expand_paths(paths):
    expanded_path = []
    is_globby = False
    for path in paths:
        b_path = _to_bytes(path)
        if b"*" in b_path or b"?" in b_path:
            e_paths = glob.glob(b_path)
            is_globby = True
        else:
            e_paths = [b_path]
        expanded_path.extend(e_paths)
    return expanded_path, is_globby


def matches_exclusion_patterns(path, exclusion_patterns):
    return any(fnmatch(path, p) for p in exclusion_patterns)


def is_archive(path):
    return re.search(rb"\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip)$", os.path.basename(path), re.IGNORECASE)


def strip_prefix(prefix, string):
    return string[len(prefix) :] if string.startswith(prefix) else string


def _to_bytes(s):
    return to_bytes(s, errors="surrogate_or_strict")


def _to_native(s):
    return to_native(s, errors="surrogate_or_strict")


def _to_native_ascii(s):
    return to_native(s, errors="surrogate_or_strict", encoding="ascii")


def _parse_octal_mode(value):
    """Accept an octal string ("0644", "644", "0o644") or int and return int.

    Returns None if value is None so callers can treat "unset" as a no-op.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if not s:
        return None
    return int(s, 8)


class Archive(metaclass=abc.ABCMeta):
    def __init__(self, module):
        self.module = module

        self.destination = _to_bytes(module.params["dest"]) if module.params["dest"] else None
        self.exclusion_patterns = module.params["exclusion_patterns"] or []
        self.format = module.params["format"]
        self.must_archive = module.params["force_archive"]
        self.remove = module.params["remove"]

        # Per-entry normalization + ordering + format overrides. Every
        # one of these defaults to None ("do not change behavior").
        self.entry_owner = module.params.get("entry_owner")
        self.entry_group = module.params.get("entry_group")
        self.entry_uid = module.params.get("entry_uid")
        self.entry_gid = module.params.get("entry_gid")
        self.entry_mtime = module.params.get("entry_mtime")
        self.entry_file_mode = _parse_octal_mode(module.params.get("entry_file_mode"))
        self.entry_dir_mode = _parse_octal_mode(module.params.get("entry_dir_mode"))
        self.entry_executable_mode = _parse_octal_mode(module.params.get("entry_executable_mode"))
        self.sort_entries = bool(module.params.get("sort_entries"))
        self.tar_format = module.params.get("tar_format")
        self.gzip_mtime = module.params.get("gzip_mtime")
        self.gzip_filename = module.params.get("gzip_filename")
        self.gzip_level = module.params.get("gzip_level")

        self.changed = False
        self.destination_state = STATE_ABSENT
        self.errors = []
        self.file = None
        self.successes = []
        self.targets = []
        self.not_found = []

        paths = module.params["path"]
        self.expanded_paths, has_globs = expand_paths(paths)
        self.expanded_exclude_paths = expand_paths(module.params["exclude_path"])[0]

        self.paths = sorted(set(self.expanded_paths) - set(self.expanded_exclude_paths))

        if not self.paths:
            module.fail_json(
                path=", ".join(paths),
                expanded_paths=_to_native(b", ".join(self.expanded_paths)),
                expanded_exclude_paths=_to_native(b", ".join(self.expanded_exclude_paths)),
                msg="Error, no source paths were found",
            )

        self.root = common_path(self.paths)

        if not self.must_archive:
            self.must_archive = any([has_globs, os.path.isdir(self.paths[0]), len(self.paths) > 1])

        if not self.destination and not self.must_archive:
            self.destination = b"%s.%s" % (self.paths[0], _to_bytes(self.format))

        if self.must_archive and not self.destination:
            module.fail_json(
                dest=_to_native(self.destination),
                path=", ".join(paths),
                msg='Error, must specify "dest" when archiving multiple files or trees',
            )

        if self.remove:
            self._check_removal_safety()

        self.original_checksums = self.destination_checksums()
        self.original_size = self.destination_size()

    def add(self, path, archive_name):
        try:
            self._add(_to_native_ascii(path), _to_native(archive_name))
            if self.contains(_to_native(archive_name)):
                self.successes.append(path)
        except Exception as e:
            self.errors.append(f"{_to_native_ascii(path)}: {e}")

    def add_single_target(self, path):
        if self.format in ("zip", "tar"):
            self.open()
            self.add(path, strip_prefix(self.root, path))
            self.close()
            self.destination_state = STATE_ARCHIVED
        else:
            try:
                f_out = self._open_compressed_file(_to_native_ascii(self.destination), "wb")
                with open(path, "rb") as f_in:
                    shutil.copyfileobj(f_in, f_out)
                f_out.close()
                self.successes.append(path)
                self.destination_state = STATE_COMPRESSED
            except OSError as e:
                self.module.fail_json(
                    path=_to_native(path),
                    dest=_to_native(self.destination),
                    msg=f"Unable to write to compressed file: {e}",
                    exception=format_exc(),
                )

    def add_targets(self):
        self.open()
        try:
            # When sort_entries is set, iterate targets and walked entries in
            # lex order so the archive layout is independent of filesystem
            # walk order. Mutating directory_names in-place during a
            # topdown=True walk is the documented way to control os.walk's
            # descent order.
            iter_targets = sorted(self.targets) if self.sort_entries else self.targets
            for target in iter_targets:
                if os.path.isdir(target):
                    for directory_path, directory_names, file_names in os.walk(target, topdown=True):
                        if self.sort_entries:
                            directory_names.sort()
                            file_names.sort()
                        for directory_name in directory_names:
                            full_path = os.path.join(directory_path, directory_name)
                            self.add(full_path, strip_prefix(self.root, full_path))

                        for file_name in file_names:
                            full_path = os.path.join(directory_path, file_name)
                            self.add(full_path, strip_prefix(self.root, full_path))
                else:
                    self.add(target, strip_prefix(self.root, target))
        except Exception as e:
            if self.format in ("zip", "tar"):
                archive_format = self.format
            else:
                archive_format = f"tar.{self.format}"
            self.module.fail_json(
                msg=f"Error when writing {archive_format} archive at {_to_native(self.destination)}: {e}",
                exception=format_exc(),
            )
        self.close()

        if self.errors:
            self.module.fail_json(
                msg=f"Errors when writing archive at {_to_native(self.destination)}: {'; '.join(self.errors)}"
            )

    def is_different_from_original(self):
        if self.original_checksums is None:
            return self.original_size != self.destination_size()
        else:
            return self.original_checksums != self.destination_checksums()

    def destination_checksums(self):
        if self.destination_exists() and self.destination_readable():
            return self._get_checksums(self.destination)
        return None

    def destination_exists(self):
        return self.destination and os.path.exists(self.destination)

    def destination_readable(self):
        return self.destination and os.access(self.destination, os.R_OK)

    def destination_size(self):
        return os.path.getsize(self.destination) if self.destination_exists() else 0

    def find_targets(self):
        for path in self.paths:
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
                path=_to_native(path), msg=f"Unable to remove source file: {e}", exception=format_exc()
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
                dest=_to_native(self.destination), msg="Error deleting some source files: ", files=self.errors
            )

    def update_permissions(self):
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.destination)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    @property
    def result(self):
        return {
            "archived": [_to_native(p) for p in self.successes],
            "dest": _to_native(self.destination),
            "dest_state": self.destination_state,
            "changed": self.changed,
            "arcroot": _to_native(self.root),
            "missing": [_to_native(p) for p in self.not_found],
            "expanded_paths": [_to_native(p) for p in self.expanded_paths],
            "expanded_exclude_paths": [_to_native(p) for p in self.expanded_exclude_paths],
        }

    def _check_removal_safety(self):
        for path in self.paths:
            if os.path.isdir(path) and self.destination.startswith(os.path.join(path, b"")):
                self.module.fail_json(
                    path=b", ".join(self.paths),
                    msg="Error, created archive can not be contained in source paths when remove=true",
                )

    def _open_compressed_file(self, path, mode):
        f = None
        if self.format == "gz":
            f = gzip.open(path, mode)
        elif self.format == "bz2":
            f = bz2.BZ2File(path, mode)
        elif self.format == "xz":
            f = lzma.LZMAFile(path, mode)
        else:
            self.module.fail_json(msg=f"{self.format} is not a valid format")

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

    @abc.abstractmethod
    def _get_checksums(self, path):
        pass


class ZipArchive(Archive):
    def __init__(self, module):
        super().__init__(module)

    def close(self):
        self.file.close()

    def contains(self, name):
        try:
            self.file.getinfo(name)
        except KeyError:
            return False
        return True

    def open(self):
        self.file = zipfile.ZipFile(_to_native_ascii(self.destination), "w", zipfile.ZIP_DEFLATED, True)

    def _add(self, path, archive_name):
        if not matches_exclusion_patterns(path, self.exclusion_patterns):
            self.file.write(path, archive_name)

    def _get_checksums(self, path):
        try:
            archive = zipfile.ZipFile(_to_native_ascii(path), "r")
            checksums = {(info.filename, info.CRC) for info in archive.infolist()}
            archive.close()
        except BadZipFile:
            checksums = set()
        return checksums


_TAR_FORMAT_MAP = {
    "ustar": tarfile.USTAR_FORMAT,
    "gnu": tarfile.GNU_FORMAT,
    "pax": tarfile.PAX_FORMAT,
}


class TarArchive(Archive):
    def __init__(self, module):
        super().__init__(module)
        self.fileIO = None
        # _buffered_gz is True when any gzip_* / entry-normalization param is
        # set with format=gz; in that case we buffer the tar in memory and
        # write the gzip layer in close() with a controlled header. Existing
        # callers (no new params set) keep the streaming `w|gz` path and see
        # zero behavioral / performance change.
        self._buffered_gz = (
            self.format == "gz"
            and any(
                v is not None
                for v in (
                    self.gzip_mtime,
                    self.gzip_filename,
                    self.gzip_level,
                    self.entry_owner,
                    self.entry_group,
                    self.entry_uid,
                    self.entry_gid,
                    self.entry_mtime,
                    self.entry_file_mode,
                    self.entry_dir_mode,
                    self.entry_executable_mode,
                )
            )
        )
        if self._buffered_gz or self.sort_entries:
            # sort_entries on its own also forces buffered mode for gz,
            # otherwise streaming `w|gz` would interleave header writes
            # before we know the final entry list.
            if self.format == "gz":
                self._buffered_gz = True

    def _tar_open_kwargs(self):
        """Build kwargs for tarfile.open() that include format= when requested."""
        kwargs = {}
        if self.tar_format is not None:
            kwargs["format"] = _TAR_FORMAT_MAP[self.tar_format]
        return kwargs

    def close(self):
        self.file.close()
        if self.format == "xz":
            with lzma.open(_to_native(self.destination), "wb") as f:
                f.write(self.fileIO.getvalue())
            self.fileIO.close()
        elif self._buffered_gz:
            # Write the gzip layer ourselves with a controlled header, then
            # atomically replace the destination. Atomic rename guarantees
            # readers never see a partial file mid-build.
            dest_native = _to_native(self.destination)
            tmp_dest = dest_native + ".tmp"
            level = self.gzip_level if self.gzip_level is not None else 9
            mtime = self.gzip_mtime if self.gzip_mtime is not None else None
            if self.gzip_filename is not None:
                filename = self.gzip_filename
            else:
                filename = os.path.basename(dest_native)
            # GzipFile takes filename via the `filename=` constructor arg.
            with open(tmp_dest, "wb") as raw_out:
                with gzip.GzipFile(
                    filename=filename,
                    mode="wb",
                    compresslevel=level,
                    fileobj=raw_out,
                    mtime=mtime,
                ) as gz_out:
                    gz_out.write(self.fileIO.getvalue())
            os.replace(tmp_dest, dest_native)
            self.fileIO.close()

    def contains(self, name):
        try:
            self.file.getmember(name)
        except KeyError:
            return False
        return True

    def open(self):
        tar_kwargs = self._tar_open_kwargs()
        if self._buffered_gz:
            # Buffer tar in memory; close() writes the gzip layer with a
            # controlled header. Asset tarballs in this repo are <5 MB so
            # the memory cost is trivial.
            self.fileIO = io.BytesIO()
            self.file = tarfile.open(fileobj=self.fileIO, mode="w", **tar_kwargs)
        elif self.format in ("gz", "bz2"):
            self.file = tarfile.open(
                _to_native_ascii(self.destination), f"w|{self.format}", **tar_kwargs
            )
        # python3 tarfile module allows xz format but for python2 we have to create the tarfile
        # in memory and then compress it with lzma.
        elif self.format == "xz":
            self.fileIO = io.BytesIO()
            self.file = tarfile.open(fileobj=self.fileIO, mode="w", **tar_kwargs)
        elif self.format == "tar":
            self.file = tarfile.open(_to_native_ascii(self.destination), "w", **tar_kwargs)
        else:
            self.module.fail_json(msg=f"{self.format} is not a valid archive format")

    def _normalize_tarinfo(self, tarinfo):
        """Apply per-entry overrides in place. Each override is independent;
        any param left as None leaves the corresponding field untouched."""
        if self.entry_owner is not None:
            tarinfo.uname = self.entry_owner
        if self.entry_group is not None:
            tarinfo.gname = self.entry_group
        if self.entry_uid is not None:
            tarinfo.uid = self.entry_uid
        if self.entry_gid is not None:
            tarinfo.gid = self.entry_gid
        if self.entry_mtime is not None:
            tarinfo.mtime = self.entry_mtime
        # Mode handling is per-entry-type so callers can express
        # "all dirs 0755, all regular files 0644, executables 0755" in
        # three independent knobs.
        if tarinfo.isdir():
            if self.entry_dir_mode is not None:
                tarinfo.mode = self.entry_dir_mode
        else:
            if (tarinfo.mode & 0o111) and self.entry_executable_mode is not None:
                tarinfo.mode = self.entry_executable_mode
            elif self.entry_file_mode is not None:
                tarinfo.mode = self.entry_file_mode
        return tarinfo

    def _add(self, path, archive_name):
        def filter(tarinfo):
            if matches_exclusion_patterns(tarinfo.name, self.exclusion_patterns):
                return None
            return self._normalize_tarinfo(tarinfo)

        self.file.add(path, archive_name, recursive=False, filter=filter)

    def _get_checksums(self, path):
        LZMAError = lzma.LZMAError

        try:
            if self.format == "xz":
                with lzma.open(_to_native_ascii(path), "r") as f:
                    archive = tarfile.open(fileobj=f)
                    checksums = {(info.name, info.chksum) for info in archive.getmembers()}
                    archive.close()
            else:
                archive = tarfile.open(_to_native_ascii(path), f"r|{self.format}")
                checksums = {(info.name, info.chksum) for info in archive.getmembers()}
                archive.close()
        except (LZMAError, tarfile.ReadError, tarfile.CompressionError):
            try:
                # The python implementations of gzip, bz2, and lzma do not support restoring compressed files
                # to their original names so only file checksum is returned
                f = self._open_compressed_file(_to_native_ascii(path), "r")
                checksum = 0
                while True:
                    chunk = f.read(16 * 1024 * 1024)
                    if not chunk:
                        break
                    checksum = crc32(chunk, checksum)
                checksums = {(b"", checksum)}
                f.close()
            except Exception:
                checksums = set()
        return checksums


def get_archive(module):
    if module.params["format"] == "zip":
        return ZipArchive(module)
    else:
        return TarArchive(module)


def create_module() -> AnsibleModule:
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="list", elements="path", required=True),
            format=dict(type="str", default="gz", choices=["bz2", "gz", "tar", "xz", "zip"]),
            dest=dict(type="path"),
            exclude_path=dict(type="list", elements="path", default=[]),
            exclusion_patterns=dict(type="list", elements="path"),
            force_archive=dict(type="bool", default=False),
            remove=dict(type="bool", default=False),
            entry_owner=dict(type="str"),
            entry_group=dict(type="str"),
            entry_uid=dict(type="int"),
            entry_gid=dict(type="int"),
            entry_mtime=dict(type="int"),
            entry_file_mode=dict(type="str"),
            entry_dir_mode=dict(type="str"),
            entry_executable_mode=dict(type="str"),
            sort_entries=dict(type="bool", default=False),
            tar_format=dict(type="str", choices=["ustar", "gnu", "pax"]),
            gzip_mtime=dict(type="int"),
            gzip_filename=dict(type="str"),
            gzip_level=dict(type="int"),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )
    return module


def main():
    module = create_module()

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
            archive.changed |= archive.is_different_from_original()
            if archive.remove:
                archive.remove_targets()
    else:
        if check_mode:
            if not archive.destination_exists():
                archive.changed = True
        else:
            path = archive.paths[0]
            archive.add_single_target(path)
            archive.changed |= archive.is_different_from_original()
            if archive.remove:
                archive.remove_single_target(path)

    if archive.destination_exists():
        archive.update_permissions()

    module.exit_json(**archive.result)


if __name__ == "__main__":
    main()
