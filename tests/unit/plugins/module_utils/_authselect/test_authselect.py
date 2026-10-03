# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import errno
from contextlib import nullcontext

import pytest

from ansible_collections.community.general.plugins.module_utils._authselect import authselect


@pytest.fixture
def library(mocker):
    lib = mocker.Mock()
    mocker.patch.object(authselect, "get_authselect_lib", return_value=lib)
    # observe cleanup without calling free()
    for pointer_type in (
        authselect.AllocatedCString,
        authselect.NullTerminatedStringArray,
        authselect.AuthselectProfile,
    ):
        mocker.patch.object(pointer_type, "_free")
    return lib


@pytest.fixture
def wrapper(library):
    return authselect.Authselect()


def set_output(output, value):
    """Fill a real ctypes output parameter and return native success."""
    ctypes.cast(output, ctypes.POINTER(type(value)))[0] = value
    return 0


def c_string(value):
    if value is None:
        return authselect.AllocatedCString()
    return ctypes.cast(ctypes.create_string_buffer(value.encode("utf-8")), authselect.AllocatedCString)


def c_array(values):
    if values is None:
        return authselect.NullTerminatedStringArray()
    buffer = (ctypes.c_char_p * (len(values) + 1))(*values, None)
    return ctypes.cast(buffer, authselect.NullTerminatedStringArray)


@pytest.mark.parametrize(
    "values, expected, error",
    [
        ([], [], None),
        ([b"sssd", "custom/ü".encode("utf-8")], ["sssd", "custom/ü"], None),
        ([b"\xff"], None, UnicodeDecodeError),
    ],
    ids=["empty", "profiles", "decoding-failure"],
)
def test_get_profiles_list_releases_array(wrapper, library, values, expected, error):
    profiles = c_array(values)
    library.authselect_list.return_value = profiles

    with pytest.raises(error) if error else nullcontext():
        assert wrapper.get_profiles_list() == expected

    library.authselect_list.assert_called_once_with()
    authselect.NullTerminatedStringArray._free.assert_called_once_with(profiles)


def test_get_profile_returns_owned_pointer(wrapper, library):
    profile = ctypes.cast(ctypes.pointer(authselect.AuthselectProfile._type_()), authselect.AuthselectProfile)
    library.authselect_profile.side_effect = lambda name, output: set_output(output, profile)

    result = wrapper.get_profile("custom/ü")

    assert isinstance(result, authselect.AuthselectProfile)
    assert ctypes.addressof(result.contents) == ctypes.addressof(profile.contents)
    assert library.authselect_profile.call_args.args[0] == "custom/ü".encode("utf-8")
    # ownership passes to the caller.
    # `get_profile`` must not free this pointer.
    authselect.AuthselectProfile._free.assert_not_called()


@pytest.mark.parametrize(
    "method, profile_id, features, expected, error",
    [
        ("get_current_profile_id", "custom/ü", None, "custom/ü", None),
        ("get_current_features", "sssd", [], [], None),
        (
            "get_current_features",
            "sssd",
            [b"with-faillock", b"with-mkhomedir"],
            ["with-faillock", "with-mkhomedir"],
            None,
        ),
        ("get_current_features", None, [b"with-faillock"], ["with-faillock"], None),
        ("get_current_features", "sssd", None, None, RuntimeError),
        ("get_current_features", "sssd", [b"\xff"], None, UnicodeDecodeError),
    ],
    ids=["profile-id", "empty-features", "features", "no-profile-output", "null-features", "decoding-failure"],
)
def test_current_configuration_releases_outputs(wrapper, library, method, profile_id, features, expected, error):
    profile, feature_array = c_string(profile_id), c_array(features)

    def current_configuration(profile_output, features_output):
        assert (features_output is not None) == (method == "get_current_features")
        set_output(profile_output, profile)
        if features_output is not None:
            set_output(features_output, feature_array)
        return 0

    library.authselect_current_configuration.side_effect = current_configuration

    with pytest.raises(error) if error else nullcontext():
        assert getattr(wrapper, method)() == expected

    library.authselect_current_configuration.assert_called_once()
    assert authselect.AllocatedCString._free.call_count == int(profile_id is not None)
    assert authselect.NullTerminatedStringArray._free.call_count == int(features is not None)


@pytest.mark.parametrize("method", ["get_current_profile_id", "get_current_features"])
def test_missing_configuration_returns_none(wrapper, library, method):
    library.authselect_current_configuration.return_value = errno.ENOENT

    assert getattr(wrapper, method)() is None


@pytest.mark.parametrize(
    "method, native, args",
    [
        ("get_profile", "authselect_profile", ("sssd",)),
        ("get_current_profile_id", "authselect_current_configuration", ()),
        ("create_profile_backup", "authselect_backup", ()),
    ],
)
def test_success_with_null_output_is_rejected(wrapper, library, method, native, args):
    getattr(library, native).return_value = 0

    with pytest.raises(RuntimeError):
        getattr(wrapper, method)(*args)


@pytest.mark.parametrize("features, force", [(None, False), ([], True), (["with-faillock", "with-mkhomedir"], True)])
def test_activate_profile_passes_requested_options(wrapper, library, mocker, features, force):
    convert = mocker.patch.object(authselect.CStringArray, "from_strings", return_value=mocker.sentinel.features)
    library.authselect_activate.return_value = 0

    assert wrapper.activate_profile("custom/ü", features, force_overwrite=force) is None

    convert.assert_called_once_with(features or [])
    library.authselect_activate.assert_called_once_with("custom/ü".encode("utf-8"), mocker.sentinel.features, force)


@pytest.mark.parametrize(
    "status, exception",
    [
        (errno.ENOENT, RuntimeError),
        (errno.EINVAL, RuntimeError),
        (errno.EEXIST, RuntimeError),
        (errno.EACCES, PermissionError),
    ],
)
def test_activate_profile_translates_native_errors(wrapper, library, status, exception):
    library.authselect_activate.return_value = status

    with pytest.raises(exception):
        wrapper.activate_profile("sssd")


@pytest.mark.parametrize(
    "result, valid, expected_status",
    [
        (0, True, authselect.AuthselectValidationStatus.VALIDATION_COMPLETE),
        (0, False, authselect.AuthselectValidationStatus.VALIDATION_COMPLETE),
        (errno.ENOENT, False, authselect.AuthselectValidationStatus.NO_CONFIGURATION),
        (errno.EEXIST, False, authselect.AuthselectValidationStatus.NOT_MANAGED),
    ],
)
def test_validate_configuration_returns_status_and_flag(wrapper, library, result, valid, expected_status):
    def validate(output):
        set_output(output, ctypes.c_bool(valid))
        return result

    library.authselect_validate_configuration.side_effect = validate

    status, is_valid = wrapper.validate_configuration()

    assert status is expected_status
    assert is_valid is valid


@pytest.mark.parametrize("name", [None, "backup-ü"])
def test_create_backup_returns_path_and_releases_string(wrapper, library, name):
    expected = "/var/lib/authselect/backups/backup-ü"
    path = c_string(expected)
    library.authselect_backup.side_effect = lambda name, output: set_output(output, path)

    assert wrapper.create_profile_backup(name) == expected

    assert library.authselect_backup.call_args.args[0] == (None if name is None else name.encode("utf-8"))
    authselect.AllocatedCString._free.assert_called_once()


@pytest.mark.parametrize(
    "method, native",
    [("remove_profile_backup", "authselect_backup_remove"), ("restore_profile_backup", "authselect_backup_restore")],
)
def test_backup_operation_passes_encoded_name(wrapper, library, method, native):
    operation = getattr(library, native)
    operation.return_value = 0

    assert getattr(wrapper, method)("backup-ü") is None

    operation.assert_called_once_with("backup-ü".encode("utf-8"))


@pytest.mark.parametrize(
    "method, native, args",
    [
        ("get_profile", "authselect_profile", ("sssd",)),
        ("get_current_profile_id", "authselect_current_configuration", ()),
        ("get_current_features", "authselect_current_configuration", ()),
        ("activate_profile", "authselect_activate", ("sssd",)),
        ("validate_configuration", "authselect_validate_configuration", ()),
        ("create_profile_backup", "authselect_backup", ()),
        ("remove_profile_backup", "authselect_backup_remove", ("backup",)),
        ("restore_profile_backup", "authselect_backup_restore", ("backup",)),
    ],
)
def test_native_failure_reports_status(wrapper, library, method, native, args):
    getattr(library, native).return_value = errno.EIO

    with pytest.raises(RuntimeError) as exc:
        getattr(wrapper, method)(*args)

    # Check the reported status, not fixed wording or platform-specific strerror text
    assert str(errno.EIO) in str(exc.value)
