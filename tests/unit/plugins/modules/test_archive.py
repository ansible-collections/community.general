# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import io
from unittest.mock import MagicMock, Mock, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.module_utils import _deps as deps
from ansible_collections.community.general.plugins.modules.archive import (
    common_path,
    create_module,
    get_archive,
    is_archive,
)


@pytest.fixture(autouse=True)
def register_deps():
    """Re-register the zstandard dep after deps_cleanup clears _deps before each test."""
    with deps.declare("zstandard"):
        pass


class TestArchive(ModuleTestCase):
    def setUp(self):
        super().setUp()

        self.mock_os_path_isdir = patch("os.path.isdir")
        self.os_path_isdir = self.mock_os_path_isdir.start()

    def tearDown(self):
        self.os_path_isdir = self.mock_os_path_isdir.stop()

    def test_archive_removal_safety(self):
        with set_module_args(dict(path=["/foo", "/bar", "/baz"], dest="/foo/destination.tgz", remove=True)):
            module = create_module()

        self.os_path_isdir.side_effect = [True, False, False, True]

        module.fail_json = Mock()

        archive = get_archive(module)

        module.fail_json.assert_called_once_with(
            path=b", ".join(archive.paths),
            msg="Error, created archive can not be contained in source paths when remove=true",
        )


PATHS: tuple[tuple[list[str | bytes], str | bytes], ...] = (
    ([], ""),
    (["/"], "/"),
    ([b"/"], b"/"),
    (["/foo", "/bar", "/baz", "/foobar", "/barbaz", "/foo/bar"], "/"),
    ([b"/foo", b"/bar", b"/baz", b"/foobar", b"/barbaz", b"/foo/bar"], b"/"),
    (["/foo/bar/baz", "/foo/bar"], "/foo/"),
    (["/foo/bar/baz", "/foo/bar/"], "/foo/bar/"),
)


@pytest.mark.parametrize("paths,root", PATHS)
def test_common_path(paths: list[str | bytes], root: str | bytes) -> None:
    assert common_path(paths) == root


class TestIsArchiveZstd:
    def test_tar_zst(self):
        assert is_archive(b"file.tar.zst")

    def test_tzst(self):
        assert is_archive(b"file.tzst")


class TestZstdFormatAccepted(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_os_path_isdir = patch("os.path.isdir")
        self.os_path_isdir = self.mock_os_path_isdir.start()
        self.os_path_isdir.return_value = False

        self.mock_os_path_exists = patch("os.path.exists")
        self.os_path_exists = self.mock_os_path_exists.start()
        self.os_path_exists.return_value = False

        self.mock_os_path_islink = patch("os.path.lexists")
        self.os_path_islink = self.mock_os_path_islink.start()
        self.os_path_islink.return_value = True

    def tearDown(self):
        self.os_path_isdir.stop()
        self.os_path_exists.stop()
        self.os_path_islink.stop()
        super().tearDown()

    def test_zstd_is_valid_format_choice(self):
        with set_module_args(dict(path=["/foo/bar"], dest="/foo/bar.tar.zst", format="zstd")):
            module = create_module()
            assert "zstd" in module.argument_spec["format"]["choices"]
            assert module.params["format"] == "zstd"


class TestOpenCompressedFileZstd(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_os_path_isdir = patch("os.path.isdir")
        self.os_path_isdir = self.mock_os_path_isdir.start()
        self.os_path_isdir.return_value = False

        self.mock_os_path_exists = patch("os.path.exists")
        self.os_path_exists = self.mock_os_path_exists.start()
        self.os_path_exists.return_value = False

        self.mock_os_path_islink = patch("os.path.lexists")
        self.os_path_islink = self.mock_os_path_islink.start()
        self.os_path_islink.return_value = True

    def tearDown(self):
        self.os_path_isdir.stop()
        self.os_path_exists.stop()
        self.os_path_islink.stop()
        super().tearDown()

    @patch("ansible_collections.community.general.plugins.modules.archive.deps.validate")
    @patch("ansible_collections.community.general.plugins.modules.archive.zstandard", create=True)
    def test_open_compressed_file_zstd(self, mock_zstandard, mock_deps_validate):
        mock_file = MagicMock()
        mock_zstandard.open.return_value = mock_file

        with set_module_args(dict(path=["/foo/bar"], dest="/foo/bar.zst", format="zstd")):
            module = create_module()
            archive = get_archive(module)

            result = archive._open_compressed_file("/foo/bar.zst", "wb")
            mock_zstandard.open.assert_called_once_with("/foo/bar.zst", "wb")
            assert result == mock_file

    @patch("ansible_collections.community.general.plugins.modules.archive.deps.validate")
    def test_open_compressed_file_zstd_missing(self, mock_deps_validate):
        def fail_on_validate(module, spec=None):
            module.fail_json(msg="The zstandard Python library is required for zstd compression")

        mock_deps_validate.side_effect = fail_on_validate

        with set_module_args(dict(path=["/foo/bar"], dest="/foo/bar.zst", format="zstd")):
            module = create_module()
            module.fail_json = Mock()
            get_archive(module)

            module.fail_json.assert_called_once()
            call_kwargs = module.fail_json.call_args[1]
            assert "zstandard" in call_kwargs["msg"]


class TestTarArchiveZstd(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_os_path_isdir = patch("os.path.isdir")
        self.os_path_isdir = self.mock_os_path_isdir.start()
        self.os_path_isdir.return_value = False

        self.mock_os_path_exists = patch("os.path.exists")
        self.os_path_exists = self.mock_os_path_exists.start()
        self.os_path_exists.return_value = False

        self.mock_os_path_islink = patch("os.path.lexists")
        self.os_path_islink = self.mock_os_path_islink.start()
        self.os_path_islink.return_value = True

    def tearDown(self):
        self.os_path_isdir.stop()
        self.os_path_exists.stop()
        self.os_path_islink.stop()
        super().tearDown()

    @patch("ansible_collections.community.general.plugins.modules.archive.deps.validate")
    @patch("ansible_collections.community.general.plugins.modules.archive.tarfile")
    def test_tar_archive_open_zstd(self, mock_tarfile, mock_deps_validate):
        with set_module_args(dict(path=["/foo/bar", "/foo/baz"], dest="/foo/out.tar.zst", format="zstd")):
            module = create_module()
            archive = get_archive(module)

            mock_tar = MagicMock()
            mock_tarfile.open.return_value = mock_tar

            archive.open()

            assert archive.fileIO is not None
            assert isinstance(archive.fileIO, io.BytesIO)
            mock_tarfile.open.assert_called_once_with(fileobj=archive.fileIO, mode="w")

    @patch("ansible_collections.community.general.plugins.modules.archive.deps.validate")
    @patch("ansible_collections.community.general.plugins.modules.archive.zstandard", create=True)
    @patch("ansible_collections.community.general.plugins.modules.archive.tarfile")
    def test_tar_archive_close_zstd(self, mock_tarfile, mock_zstandard, mock_deps_validate):
        with set_module_args(dict(path=["/foo/bar", "/foo/baz"], dest="/foo/out.tar.zst", format="zstd")):
            module = create_module()
            archive = get_archive(module)

            archive.file = MagicMock()
            archive.fileIO = io.BytesIO(b"fake tar data")

            mock_zstd_file = MagicMock()
            mock_zstandard.open.return_value = mock_zstd_file

            archive.close()

            archive.file.close.assert_called_once()
            mock_zstandard.open.assert_called_once()

    @patch("ansible_collections.community.general.plugins.modules.archive.deps.validate")
    @patch("ansible_collections.community.general.plugins.modules.archive.zstandard", create=True)
    @patch("ansible_collections.community.general.plugins.modules.archive.tarfile")
    def test_tar_archive_get_checksums_zstd(self, mock_tarfile, mock_zstandard, mock_deps_validate):
        with set_module_args(dict(path=["/foo/bar", "/foo/baz"], dest="/foo/out.tar.zst", format="zstd")):
            module = create_module()
            archive = get_archive(module)

            mock_tar = MagicMock()
            mock_info = MagicMock()
            mock_info.name = "file.txt"
            mock_info.chksum = 12345
            mock_tar.getmembers.return_value = [mock_info]
            mock_tarfile.open.return_value.__enter__.return_value = mock_tar

            mock_zstd_file = MagicMock()
            mock_zstd_file.__enter__ = Mock(return_value=mock_zstd_file)
            mock_zstandard.open.return_value = mock_zstd_file

            checksums = archive._get_checksums("/foo/out.tar.zst")

            mock_zstandard.open.assert_called_once()
            mock_tarfile.open.assert_called_once_with(fileobj=mock_zstd_file, mode="r|")
            assert checksums == {("file.txt", 12345)}
