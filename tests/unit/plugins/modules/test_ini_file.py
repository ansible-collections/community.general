# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import shutil
import tempfile

import pytest

from ansible_collections.community.general.plugins.modules import ini_file


def do_test(option, ignore_spaces, newline, before, expected_after, expected_changed, expected_msg):
    section_lines = [before]
    changed_lines = [0]
    changed, msg = ini_file.update_section_line(
        option, None, section_lines, 0, changed_lines, ignore_spaces, newline, None
    )
    assert section_lines[0] == expected_after
    assert changed == expected_changed
    assert changed_lines[0] == 1
    assert msg == expected_msg


def test_ignore_spaces_comment():
    oldline = ";foobar=baz"
    newline = "foobar = baz"
    do_test("foobar", True, newline, oldline, newline, True, "option changed")


def test_ignore_spaces_changed():
    oldline = "foobar=baz"
    newline = "foobar = freeble"
    do_test("foobar", True, newline, oldline, newline, True, "option changed")


def test_ignore_spaces_unchanged():
    oldline = "foobar=baz"
    newline = "foobar = baz"
    do_test("foobar", True, newline, oldline, oldline, False, None)


def test_no_ignore_spaces_changed():
    oldline = "foobar=baz"
    newline = "foobar = baz"
    do_test("foobar", False, newline, oldline, newline, True, "option changed")


def test_no_ignore_spaces_unchanged():
    newline = "foobar=baz"
    do_test("foobar", False, newline, newline, newline, False, None)


class FakeModule:
    """Minimal AnsibleModule stub for do_ini unit tests."""

    _diff = False
    check_mode = False
    tmpdir = tempfile.gettempdir()

    def fail_json(self, **kw):
        raise AssertionError(kw)

    def backup_local(self, f):
        return f + ".bak"

    def atomic_move(self, src, dst):
        shutil.move(src, dst)


@pytest.fixture()
def ini_file_path(tmp_path):
    """Return a factory that writes content to a temp ini file and yields the path."""

    def _make(content):
        p = tmp_path / "test.ini"
        p.write_text(content)
        return str(p)

    return _make


def test_ini_file_doc_comment_lines_not_deleted_gh11919(ini_file_path):
    """Regression test for https://github.com/ansible-collections/community.general/issues/11919.

    Pure doc comment lines containing the option name (e.g. '; output_buffering')
    must not be deleted when state=present and exclusive=True.
    Only the actual commented config line (';output_buffering = 4096') should be
    replaced by the active config line.
    """
    content = (
        "[PHP]\n"
        ";   Integer = Enables the buffer and sets its maximum size in bytes.\n"
        "; Note: This directive is hardcoded to Off for the CLI SAPI\n"
        "; Default Value: Off\n"
        "; output_buffering\n"
        "; Development Value: 4096\n"
        "; Production Value: 4096\n"
        "; https://php.net/output-buffering\n"
        ";output_buffering = 4096\n"
    )
    path = ini_file_path(content)

    ini_file.do_ini(
        module=FakeModule(),
        filename=path,
        section="PHP",
        option="output_buffering",
        values=["123"],
        state="present",
        exclusive=True,
        backup=False,
        no_extra_spaces=False,
        ignore_spaces=False,
        create=True,
        allow_no_value=False,
        modify_inactive_option=True,
    )

    result = open(path).read()

    assert "; output_buffering\n" in result, "Doc comment '; output_buffering' must not be deleted"
    assert "output_buffering = 123\n" in result, "Active config 'output_buffering = 123' must be present"
    assert ";output_buffering = 4096\n" not in result, (
        "Old commented config ';output_buffering = 4096' must be replaced"
    )


def test_ini_file_commented_config_replaced_not_duplicated_gh11919(ini_file_path):
    """Companion to gh11919: the commented config line must be replaced in-place,
    not left behind alongside the new active line."""
    content = "[PHP]\n;output_buffering = 4096\n"
    path = ini_file_path(content)

    ini_file.do_ini(
        module=FakeModule(),
        filename=path,
        section="PHP",
        option="output_buffering",
        values=["123"],
        state="present",
        exclusive=True,
        backup=False,
        no_extra_spaces=False,
        ignore_spaces=False,
        create=True,
        allow_no_value=False,
        modify_inactive_option=True,
    )

    result = open(path).read()

    assert "output_buffering = 123\n" in result
    assert ";output_buffering = 4096\n" not in result
