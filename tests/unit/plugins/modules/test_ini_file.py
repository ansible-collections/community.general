# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

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
