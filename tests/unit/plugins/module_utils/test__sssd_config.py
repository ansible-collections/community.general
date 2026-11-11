# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import call

import pytest

from ansible_collections.community.general.plugins.module_utils import _sssd_config


@pytest.mark.parametrize(
    "section, name, expected",
    [("sssd", None, "sssd"), ("domain", "example.com", "domain/example.com"), ("service", "pam", "pam")],
)
def test_section_name(section, name, expected):
    target = _sssd_config.SSSDTarget("/etc/sssd/sssd.conf", section, name)
    assert target.section_name == expected


@pytest.mark.parametrize(
    "section, name, message",
    [
        ("invalid", None, "Unsupported SSSD section type"),
        ("sssd", "unexpected", "must not have a name"),
        ("domain", None, "requires a name"),
        ("service", "", "requires a name"),
    ],
)
def test_invalid_target(section, name, message):
    with pytest.raises(ValueError, match=message):
        _sssd_config.SSSDTarget("/etc/sssd/sssd.conf", section, name)


@pytest.mark.parametrize(
    "already_respawned, interpreter",
    [(True, "/usr/bin/python3"), (False, "/usr/bin/python3"), (False, None)],
    ids=["prevent-loop", "compatible-interpreter", "no-compatible-interpreter"],
)
def test_respawn(mocker, already_respawned, interpreter):
    respawn = mocker.patch.object(_sssd_config, "respawn")
    respawn.has_respawned.return_value = already_respawned
    respawn.probe_interpreters_for_module.return_value = interpreter

    _sssd_config._respawn_sssdconfig()

    if already_respawned:
        respawn.probe_interpreters_for_module.assert_not_called()
    else:
        assert respawn.probe_interpreters_for_module.call_args.args[1] == "SSSDConfig"
    if interpreter and not already_respawned:
        respawn.respawn_module.assert_called_once_with(interpreter)
    else:
        respawn.respawn_module.assert_not_called()


def test_explicit_options_use_the_librarys_filtered_records(mocker):
    config = mocker.Mock()
    config.has_section.return_value = True
    config.options.return_value = [
        {"type": "comment", "value": "A comment"},
        {"type": "option", "name": "services", "value": "nss"},
    ]
    config.strip_comments_empty.return_value = [config.options.return_value[1]]

    assert _sssd_config.get_explicit_options(config, "sssd") == {"services": "nss"}
    config.strip_comments_empty.assert_called_once_with(config.options.return_value)


def test_missing_section_has_no_explicit_options(mocker):
    config = mocker.Mock()
    config.has_section.return_value = False

    assert _sssd_config.get_explicit_options(config, "sssd") == {}


@pytest.mark.parametrize(
    "option, value, expected",
    [
        ("services", ["nss", "pam"], "nss, pam"),
        ("debug_level", 16, "16"),
        ("debug_level", 32, "0x20"),
        ("config_file_version", 2, "2"),
    ],
)
def test_serialize_option_value(option, value, expected):
    assert _sssd_config.serialize_option_value(option, value) == expected


def test_sssd_implicit_default_is_written_explicitly(mocker):
    config = mocker.Mock()
    config.has_option.return_value = False
    section = config.get_service.return_value
    section.get_all_options.return_value = {"config_file_version": 2}
    section.get_option.return_value = 2

    assert _sssd_config.set_sssd_options(config, {"config_file_version": 2}) is True
    config.set.assert_called_once_with("sssd", "config_file_version", "2")


@pytest.mark.parametrize(
    "setter", [_sssd_config.set_domain_options, _sssd_config.set_service_options], ids=["domain", "service"]
)
@pytest.mark.parametrize(
    "current, requested, explicit, changed",
    [(0, 6, True, True), (6, 6, True, False), (0, 0, False, True)],
    ids=["update", "unchanged", "implicit-default"],
)
def test_set_options(mocker, setter, current, requested, explicit, changed):
    values = {"debug_level": current}
    section = mocker.Mock()
    section.get_all_options.side_effect = lambda: dict(values)
    section.set_option.side_effect = values.__setitem__
    explicit_options = {"debug_level": str(current)} if explicit else {}

    assert setter(section, {"debug_level": requested}, explicit_options) is changed
    section.set_option.assert_called_once_with("debug_level", requested)
    assert values == {"debug_level": requested}


@pytest.mark.parametrize("provider", [None, "ldap", "ipa"], ids=["new", "unchanged", "replacement"])
def test_domain_sets_provider_before_provider_options(mocker, provider):
    values = {} if provider is None else {"id_provider": provider}
    domain = mocker.Mock()
    domain.get_all_options.side_effect = lambda: dict(values)
    domain.set_option.side_effect = values.__setitem__
    domain.remove_provider.side_effect = lambda name: values.pop(name + "_provider")

    changed = _sssd_config.set_domain_options(
        domain, {"ldap_uri": "ldap://example.com", "id_provider": "ldap"}, dict(values)
    )

    expected_calls = [call.remove_provider("id")] if provider == "ipa" else []
    expected_calls += [call.set_option("id_provider", "ldap"), call.set_option("ldap_uri", "ldap://example.com")]
    assert [
        operation for operation in domain.method_calls if operation[0] in ("remove_provider", "set_option")
    ] == expected_calls
    assert changed is True
    assert values == {"id_provider": "ldap", "ldap_uri": "ldap://example.com"}


@pytest.mark.parametrize(
    "active, created, requested, changed",
    [
        (False, False, True, True),
        (True, False, False, True),
        (True, False, True, False),
        (True, False, None, False),
        (True, True, None, True),
    ],
    ids=["activate", "deactivate", "unchanged", "preserve-existing", "new-defaults-to-inactive"],
)
def test_domain_activation(mocker, active, created, requested, changed):
    domain = mocker.Mock(active=active)

    assert _sssd_config.set_domain_active(domain, created, requested) is changed
    if changed:
        domain.set_active.assert_called_once_with(bool(requested))
    else:
        domain.set_active.assert_not_called()


@pytest.mark.parametrize(
    "active, created, requested, changed",
    [
        (False, False, True, True),
        (True, False, False, True),
        (True, False, True, False),
        (True, False, None, False),
        (True, True, None, True),
    ],
    ids=["activate", "deactivate", "unchanged", "preserve-existing", "new-defaults-to-inactive"],
)
def test_service_activation(mocker, active, created, requested, changed):
    config = mocker.Mock()
    config.list_active_services.return_value = ["pam"] if active else []

    assert _sssd_config.set_service_active(config, "pam", created, requested) is changed
    assert config.activate_service.call_args_list == ([call("pam")] if changed and requested else [])
    assert config.deactivate_service.call_args_list == ([call("pam")] if changed and not requested else [])


@pytest.mark.parametrize("active", [False, True])
def test_delete_service_deactivates_it_first(mocker, active):
    config = mocker.Mock()
    config.list_active_services.return_value = ["pam"] if active else []

    _sssd_config.delete_service(config, "pam")

    if active:
        config.assert_has_calls([call.deactivate_service("pam"), call.delete_service("pam")])
    else:
        config.deactivate_service.assert_not_called()
    config.delete_service.assert_called_once_with("pam")


def test_remove_domain_options_distinguishes_providers(mocker):
    domain = mocker.Mock()

    assert _sssd_config.remove_domain_options(domain, iter(["id_provider", "debug_level"])) is True
    domain.remove_provider.assert_called_once_with("id")
    domain.remove_option.assert_called_once_with("debug_level")


def test_remove_service_options(mocker):
    service = mocker.Mock()

    assert _sssd_config.remove_service_options(service, iter(["pam_verbosity", "debug_level"])) is True
    assert service.remove_option.call_args_list == [call("pam_verbosity"), call("debug_level")]


def test_remove_sssd_options_removes_all_occurrences(mocker):
    config = mocker.Mock()
    config.findOpts.return_value = (0, {"value": mocker.sentinel.options})

    assert _sssd_config.remove_sssd_options(config, iter(["services", "debug_level"])) is True
    assert config.delete_option_subtree.call_args_list == [
        call(mocker.sentinel.options, "option", "services", True),
        call(mocker.sentinel.options, "option", "debug_level", True),
    ]


@pytest.mark.parametrize(
    "remove",
    [_sssd_config.remove_domain_options, _sssd_config.remove_service_options, _sssd_config.remove_sssd_options],
    ids=["domain", "service", "sssd"],
)
def test_removing_no_options_is_a_noop(mocker, remove):
    config = mocker.Mock()

    assert remove(config, iter([])) is False
    assert config.mock_calls == []
