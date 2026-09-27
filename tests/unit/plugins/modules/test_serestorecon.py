# Copyright (c) 2026, Nicholas Brodersen <nicholasbrodersen01@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import errno
import stat
from os import stat_result
from pathlib import Path

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import serestorecon

DESIRED = "system_u:object_r:tmp_t:s0"
PREVIOUS = "system_u:object_r:var_t:s0"


@pytest.fixture
def selinux_mock(mocker, monkeypatch):
    selinux = mocker.Mock()
    # Distinct bits make flag composition testable without installed bindings.
    selinux.SELINUX_RESTORECON_REALPATH = 1
    selinux.SELINUX_RESTORECON_IGNORE_DIGEST = 2
    selinux.SELINUX_RESTORECON_ABORT_ON_ERROR = 4
    selinux.SELINUX_RESTORECON_SET_USER_ROLE = 8
    selinux.SELINUX_RESTORECON_SET_SPECFILE_CTX = 16
    selinux.SELABEL_CTX_FILE = 0
    selinux.selabel_open.return_value = object()
    selinux.selabel_lookup_raw.return_value = (0, DESIRED)
    # lgetfilecon_raw returns the label length on success, not necessarily zero.
    selinux.lgetfilecon_raw.return_value = (len(PREVIOUS), PREVIOUS)
    selinux.selinux_restorecon.return_value = 0
    monkeypatch.setattr(serestorecon, "selinux", selinux, raising=False)
    return selinux


@pytest.fixture
def make_module(mocker, selinux_mock, tmp_path):
    mocker.patch.object(serestorecon.deps, "validate")
    mocker.patch("ansible.module_utils.basic.AnsibleModule.selinux_enabled", return_value=True)
    path = tmp_path / "file"
    path.touch()

    def make(**overrides):
        args = {"path": str(path)}
        args.update(overrides)
        with set_module_args(args):
            module = serestorecon.SERestoreconModule()
        module.__init_module__()
        return module

    return make


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "root"
    for name in ("keep/file", "skip/nested/file", "skip-sibling/file"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return root


@pytest.mark.parametrize(
    ("context", "current", "expected"),
    [
        pytest.param("type", DESIRED, False, id="type-unchanged"),
        pytest.param("type", PREVIOUS, True, id="type-differs"),
        pytest.param("type", "unconfined_u:system_r:tmp_t:s0:c0.c3", False, id="type-ignores-other-components"),
        pytest.param("user_role", DESIRED, False, id="user-role-unchanged"),
        pytest.param("user_role", PREVIOUS, True, id="user-role-includes-type"),
        pytest.param("user_role", "unconfined_u:object_r:tmp_t:s0", True, id="user-differs"),
        pytest.param("user_role", "system_u:system_r:tmp_t:s0", True, id="role-differs"),
        pytest.param("user_role", "system_u:object_r:tmp_t:s0:c0.c3", False, id="user-role-ignores-range"),
        pytest.param("full", DESIRED, False, id="full-unchanged"),
        pytest.param("full", PREVIOUS, True, id="full-includes-type"),
        pytest.param("full", "unconfined_u:object_r:tmp_t:s0", True, id="full-includes-user"),
        pytest.param("full", "system_u:system_r:tmp_t:s0", True, id="full-includes-role"),
        pytest.param("full", "system_u:object_r:tmp_t:s0:c0.c3", True, id="full-includes-range"),
    ],
)
def test_comparison_uses_requested_context_components(make_module, context, current, expected):
    module = make_module(context=context)

    assert module.labels_differ(DESIRED, current) is expected


@pytest.mark.parametrize(
    ("context", "expected_flags", "supports_user_role"),
    [
        ("type", 1 | 2 | 4, True),
        ("user_role", 1 | 2 | 4 | 8, True),
        ("full", 1 | 2 | 4 | 16, True),
        ("type", 1 | 2 | 4, False),
        ("full", 1 | 2 | 4 | 16, False),
    ],
)
def test_restore_passes_requested_flags_to_selinux(
    make_module, selinux_mock, context, expected_flags, supports_user_role
):
    if not supports_user_role:
        del selinux_mock.SELINUX_RESTORECON_SET_USER_ROLE
    module = make_module(context=context)

    module.__run__()

    selinux_mock.selinux_restorecon.assert_called_once_with(module.module.params["path"], expected_flags)


@pytest.mark.parametrize("check_mode", [False, True])
def test_user_role_requires_binding_support(make_module, selinux_mock, check_mode):
    del selinux_mock.SELINUX_RESTORECON_SET_USER_ROLE

    with pytest.raises(serestorecon.SERestoreconModule.ModuleHelperException) as exc:
        make_module(context="user_role", _ansible_check_mode=check_mode)

    selinux_mock.selinux_restorecon.assert_not_called()


def test_restore_reports_the_changed_path(make_module, selinux_mock):
    previous = "unconfined_u:system_r:var_t:s0:c0.c3"
    restored = "unconfined_u:system_r:tmp_t:s0:c0.c3"
    selinux_mock.lgetfilecon_raw.side_effect = [(len(previous), previous), (len(restored), restored)]
    module = make_module()

    module.__run__()
    module.__quit_module__()

    assert module.output["changed_paths"] == [
        {"path": module.module.params["path"], "previous": previous, "restored": restored},
    ]
    assert module.changed is True
    selinux_mock.selabel_close.assert_called_once_with(selinux_mock.selabel_open.return_value)


def test_matching_context_is_unchanged(make_module, selinux_mock):
    selinux_mock.lgetfilecon_raw.return_value = (len(DESIRED), DESIRED)
    module = make_module()

    module.__run__()
    module.__quit_module__()

    assert module.changed is False
    assert module.output["changed_paths"] == []
    selinux_mock.selinux_restorecon.assert_not_called()


@pytest.mark.parametrize(
    ("context", "restored"),
    [
        ("type", "unconfined_u:system_r:tmp_t:s0:c0.c3"),
        ("user_role", "system_u:object_r:tmp_t:s0:c0.c3"),
        ("full", DESIRED),
    ],
)
def test_check_mode_reports_change_without_restoring(make_module, selinux_mock, context, restored):
    previous = "unconfined_u:system_r:var_t:s0:c0.c3"
    selinux_mock.lgetfilecon_raw.return_value = (len(previous), previous)
    module = make_module(context=context)
    module.module.check_mode = True

    module.__run__()
    module.__quit_module__()

    assert module.output["changed_paths"] == [
        {"path": module.module.params["path"], "previous": previous, "restored": restored},
    ]
    assert module.changed is True
    selinux_mock.selinux_restorecon.assert_not_called()


def test_successful_restore_with_no_label_change_is_unchanged(make_module, selinux_mock):
    module = make_module()

    module.__run__()
    module.__quit_module__()

    selinux_mock.selinux_restorecon.assert_called_once()
    assert module.changed is False
    assert module.output["changed_paths"] == []


def test_path_without_a_policy_match_is_unchanged(make_module, selinux_mock):
    selinux_mock.selabel_lookup_raw.side_effect = OSError(errno.ENOENT, "No policy match")
    module = make_module()

    module.__run__()
    module.__quit_module__()

    assert module.changed is False
    assert module.output["changed_paths"] == []
    selinux_mock.selinux_restorecon.assert_not_called()


def test_policy_lookup_uses_the_symlinks_file_type(make_module, selinux_mock, tmp_path):
    target = tmp_path / "target"
    target.touch()
    link = tmp_path / "link"
    link.symlink_to(target)
    module = make_module()
    handle = selinux_mock.selabel_open.return_value

    module.get_desired_label(handle, link)

    selinux_mock.selabel_lookup_raw.assert_called_once_with(handle, str(link), stat.S_IFLNK)


@pytest.mark.parametrize(
    ("operation", "result", "message"),
    [
        pytest.param("selabel_lookup_raw", (-1, None), "Failed to get desired label for", id="policy-lookup"),
        pytest.param("lgetfilecon_raw", (-1, None), "Failed to get current SELinux context for", id="current-label"),
        pytest.param("selinux_restorecon", -1, "Failed to restore SELinux context for", id="restore"),
    ],
)
def test_selinux_failure_is_reported_and_handle_closed(make_module, selinux_mock, operation, result, message):
    getattr(selinux_mock, operation).return_value = result
    module = make_module()

    with pytest.raises(module.ModuleHelperException) as exc:
        module.__run__()

    assert exc.value.msg == f"{message} {module.module.params['path']}"
    selinux_mock.selabel_close.assert_called_once_with(selinux_mock.selabel_open.return_value)


def test_permission_error_is_not_treated_as_a_missing_policy(make_module, selinux_mock):
    error = OSError(errno.EACCES, "Permission denied")
    selinux_mock.selabel_lookup_raw.side_effect = error
    module = make_module()

    with pytest.raises(OSError) as exc:
        module.__run__()

    assert exc.value is error
    selinux_mock.selabel_close.assert_called_once_with(selinux_mock.selabel_open.return_value)


def test_nonrecursive_traversal_yields_only_the_requested_path(make_module, tree):
    module = make_module(path=str(tree), recurse=False)

    assert list(module.iter_paths()) == [tree]


def test_recursive_traversal_includes_files_and_directories(make_module, tree):
    module = make_module(path=str(tree), recurse=True)

    assert set(module.iter_paths()) == {
        tree,
        tree / "keep",
        tree / "keep/file",
        tree / "skip",
        tree / "skip/nested",
        tree / "skip/nested/file",
        tree / "skip-sibling",
        tree / "skip-sibling/file",
    }


def test_exclusion_removes_descendants_but_keeps_similarly_named_siblings(make_module, tree):
    module = make_module(path=str(tree), recurse=True, exclude_paths=[str(tree / "skip")])

    assert set(module.iter_paths()) == {
        tree,
        tree / "keep",
        tree / "keep/file",
        tree / "skip-sibling",
        tree / "skip-sibling/file",
    }


def test_excluding_the_requested_root_still_processes_the_root(make_module, tree):
    module = make_module(path=str(tree), recurse=True, exclude_paths=[str(tree)])

    assert list(module.iter_paths()) == [tree]


@pytest.mark.parametrize(
    ("cross_filesystems", "expected_names"),
    [(False, {"same"}), (True, {"same", "other"})],
)
def test_traversal_respects_filesystem_boundaries(make_module, mocker, tmp_path, cross_filesystems, expected_names):
    root = tmp_path / "mounts"
    root.mkdir()
    (root / "same").touch()
    other = root / "other"
    other.touch()
    module = make_module(path=str(root), recurse=True, cross_filesystems=cross_filesystems)
    real_lstat = Path.lstat

    def lstat(path):
        values = list(real_lstat(path))
        if path == other:
            values[stat.ST_DEV] += 1
        return stat_result(values)

    # Keep real traversal and metadata; simulate only the second device number.
    mocker.patch.object(Path, "lstat", autospec=True, side_effect=lstat)

    assert set(module.iter_paths()) == {root} | {root / name for name in expected_names}


def test_quit_registers_previous_and_restored_contexts_for_diff(make_module, mocker):
    module = make_module()
    module.changed_paths = [
        {"path": "/tmp/first", "previous": PREVIOUS, "restored": DESIRED},
        {"path": "/tmp/second", "previous": "system_u:object_r:user_tmp_t:s0", "restored": DESIRED},
    ]
    variables = mocker.patch.object(module, "vars")

    module.__quit_module__()

    variables.set.assert_has_calls(
        [
            mocker.call(
                "file_contexts",
                [
                    {"path": "/tmp/first", "context": PREVIOUS},
                    {"path": "/tmp/second", "context": "system_u:object_r:user_tmp_t:s0"},
                ],
                output=False,
                diff=True,
                change=True,
            ),
            mocker.call(
                "file_contexts",
                [
                    {"path": "/tmp/first", "context": DESIRED},
                    {"path": "/tmp/second", "context": DESIRED},
                ],
            ),
        ]
    )


def test_disabled_selinux_is_rejected(make_module, mocker):
    mocker.patch("ansible.module_utils.basic.AnsibleModule.selinux_enabled", return_value=False)

    with pytest.raises(serestorecon.SERestoreconModule.ModuleHelperException) as exc:
        make_module()

    assert exc.value.msg == "SELinux is not enabled"
