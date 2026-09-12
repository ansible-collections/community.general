# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, call, patch

from ansible_collections.community.general.plugins.module_utils import _sssd_config


class FakeConfiguration:
    def __init__(self, options=None, normalizers=None):
        self._options = dict(options or {})
        self._normalizers = dict(normalizers or {})
        self.set_option_calls = []
        self.remove_option_calls = []

    def get_all_options(self):
        return dict(self._options)

    def get_option(self, option):
        return self._options[option]

    def set_option(self, option, value):
        self.set_option_calls.append(call(option, value))
        normalizer = self._normalizers.get(option, lambda item: item)
        self._options[option] = normalizer(value)

    def remove_option(self, option):
        self.remove_option_calls.append(call(option))
        self._options.pop(option, None)


class FakeDomain(FakeConfiguration):
    def __init__(self, options=None, active=False, normalizers=None):
        super().__init__(options=options, normalizers=normalizers)
        self.active = active
        self.remove_provider_calls = []
        self.set_active_calls = []

    def remove_provider(self, provider_type):
        self.remove_provider_calls.append(call(provider_type))
        self._options.pop(f"{provider_type}_provider", None)

    def set_active(self, active):
        self.set_active_calls.append(call(active))
        self.active = active


class FakeService(FakeConfiguration):
    pass


class TestRequestDataClasses(unittest.TestCase):
    def test_sssd_target_resolves_root_section_name(self):
        target = _sssd_config.SSSDTarget(
            path="/etc/sssd/sssd.conf",
            section="sssd",
        )

        self.assertEqual(target.section_name, "sssd")
        self.assertIsNone(target.name)

    def test_domain_target_resolves_qualified_section_name(self):
        target = _sssd_config.SSSDTarget(
            path="/etc/sssd/sssd.conf",
            section="domain",
            name="example.com",
        )

        self.assertEqual(target.section_name, "domain/example.com")

    def test_service_target_uses_service_name_as_section_name(self):
        target = _sssd_config.SSSDTarget(
            path="/etc/sssd/sssd.conf",
            section="service",
            name="pam",
        )

        self.assertEqual(target.section_name, "pam")

    def test_ensure_present_defaults_optional_activation(self):
        target = _sssd_config.SSSDTarget(
            path="/etc/sssd/sssd.conf",
            section="sssd",
        )
        request = _sssd_config.EnsurePresent(
            target=target,
            options={"services": ["nss", "pam"]},
        )

        self.assertFalse(request.must_exist)
        self.assertIsNone(request.active)

    def test_removal_requests_contain_only_actionable_data(self):
        target = _sssd_config.SSSDTarget(
            path="/etc/sssd/sssd.conf",
            section="service",
            name="pam",
        )
        remove_options = _sssd_config.RemoveOptions(
            target=target,
            option_names=("debug_level",),
        )
        remove_section = _sssd_config.RemoveSection(target=target)

        self.assertEqual(remove_options.option_names, ("debug_level",))
        self.assertIs(remove_section.target, target)
        self.assertFalse(hasattr(remove_options, "must_exist"))
        self.assertFalse(hasattr(remove_section, "must_exist"))


class TestLibraryAdapter(unittest.TestCase):
    def test_create_sssd_config_uses_imported_constructor(self):
        config = object()

        with patch.object(_sssd_config, "_SSSDConfig", return_value=config) as constructor:
            result = _sssd_config.create_sssd_config()

        self.assertIs(result, config)
        constructor.assert_called_once_with()

    def test_get_explicit_options_returns_empty_mapping_when_section_is_absent(self):
        config = MagicMock()
        config.has_section.return_value = False

        result = _sssd_config.get_explicit_options(config, "sssd")

        self.assertEqual(result, {})
        config.options.assert_not_called()

    def test_get_explicit_options_converts_records_to_mapping(self):
        config = MagicMock()
        raw_options = [object(), object()]
        config.has_section.return_value = True
        config.options.return_value = raw_options
        config.strip_comments_empty.return_value = [
            {"name": "services", "value": "nss, pam"},
            {"name": "domains", "value": "example.com"},
        ]

        result = _sssd_config.get_explicit_options(config, "sssd")

        self.assertEqual(
            result,
            {"services": "nss, pam", "domains": "example.com"},
        )
        config.options.assert_called_once_with("sssd")
        config.strip_comments_empty.assert_called_once_with(raw_options)


class TestSetServiceOptions(unittest.TestCase):
    def test_sets_requested_options(self):
        service = FakeService(options={"pam_verbosity": 1})

        changed = _sssd_config.set_service_options(
            service,
            {"pam_verbosity": 2},
            {"pam_verbosity": "1"},
        )

        self.assertTrue(changed)
        self.assertEqual(service.get_all_options()["pam_verbosity"], 2)
        self.assertEqual(service.set_option_calls, [call("pam_verbosity", 2)])

    def test_is_idempotent_when_explicit_value_is_unchanged(self):
        service = FakeService(options={"pam_verbosity": 2})

        changed = _sssd_config.set_service_options(
            service,
            {"pam_verbosity": 2},
            {"pam_verbosity": "2"},
        )

        self.assertFalse(changed)

    def test_materializes_implicit_default_as_explicit_option(self):
        service = FakeService(options={"pam_verbosity": 0})

        changed = _sssd_config.set_service_options(
            service,
            {"pam_verbosity": 0},
            {},
        )

        self.assertTrue(changed)

    def test_empty_request_is_idempotent(self):
        service = FakeService(options={"pam_verbosity": 1})

        changed = _sssd_config.set_service_options(service, {}, {})

        self.assertFalse(changed)
        self.assertEqual(service.set_option_calls, [])


class TestSetDomainOptions(unittest.TestCase):
    def test_changed_provider_is_removed_before_replacement(self):
        domain = FakeDomain(options={"id_provider": "ipa"})

        changed = _sssd_config.set_domain_options(
            domain,
            {"id_provider": "ldap"},
            {"id_provider": "ipa"},
        )

        self.assertTrue(changed)
        self.assertEqual(domain.remove_provider_calls, [call("id")])
        self.assertEqual(domain.set_option_calls, [call("id_provider", "ldap")])
        self.assertEqual(domain.get_all_options()["id_provider"], "ldap")

    def test_unchanged_provider_is_not_removed(self):
        domain = FakeDomain(options={"id_provider": "ldap"})

        changed = _sssd_config.set_domain_options(
            domain,
            {"id_provider": "ldap"},
            {"id_provider": "ldap"},
        )

        self.assertFalse(changed)
        self.assertEqual(domain.remove_provider_calls, [])

    def test_new_provider_does_not_remove_nonexistent_provider(self):
        domain = FakeDomain()

        changed = _sssd_config.set_domain_options(
            domain,
            {"auth_provider": "ldap"},
            {},
        )

        self.assertTrue(changed)
        self.assertEqual(domain.remove_provider_calls, [])

    def test_regular_option_does_not_remove_provider(self):
        domain = FakeDomain(options={"cache_credentials": False})

        changed = _sssd_config.set_domain_options(
            domain,
            {"cache_credentials": True},
            {"cache_credentials": "false"},
        )

        self.assertTrue(changed)
        self.assertEqual(domain.remove_provider_calls, [])

    def test_provider_options_are_processed_before_regular_options(self):
        domain = FakeDomain()

        _sssd_config.set_domain_options(
            domain,
            {
                "cache_credentials": True,
                "id_provider": "ldap",
            },
            {},
        )

        self.assertEqual(
            domain.set_option_calls,
            [
                call("id_provider", "ldap"),
                call("cache_credentials", True),
            ],
        )


class TestActivation(unittest.TestCase):
    def test_domain_is_activated_when_requested(self):
        domain = FakeDomain(active=False)

        changed = _sssd_config.set_domain_active(
            domain,
            created=False,
            requested=True,
        )

        self.assertTrue(changed)
        self.assertTrue(domain.active)
        self.assertEqual(domain.set_active_calls, [call(True)])

    def test_domain_activation_is_idempotent(self):
        domain = FakeDomain(active=True)

        changed = _sssd_config.set_domain_active(
            domain,
            created=False,
            requested=True,
        )

        self.assertFalse(changed)
        self.assertEqual(domain.set_active_calls, [])

    def test_existing_domain_activation_is_unmanaged_when_omitted(self):
        domain = FakeDomain(active=True)

        changed = _sssd_config.set_domain_active(
            domain,
            created=False,
            requested=None,
        )

        self.assertFalse(changed)
        self.assertTrue(domain.active)
        self.assertEqual(domain.set_active_calls, [])

    def test_new_domain_defaults_to_inactive_when_activation_is_omitted(self):
        domain = FakeDomain(active=True)

        changed = _sssd_config.set_domain_active(
            domain,
            created=True,
            requested=None,
        )

        self.assertTrue(changed)
        self.assertFalse(domain.active)
        self.assertEqual(domain.set_active_calls, [call(False)])

    def test_service_is_activated_when_requested(self):
        config = MagicMock()
        config.list_active_services.return_value = []

        changed = _sssd_config.set_service_active(
            config,
            "pam",
            created=False,
            requested=True,
        )

        self.assertTrue(changed)
        config.activate_service.assert_called_once_with("pam")
        config.deactivate_service.assert_not_called()

    def test_service_is_deactivated_when_requested(self):
        config = MagicMock()
        config.list_active_services.return_value = ["pam"]

        changed = _sssd_config.set_service_active(
            config,
            "pam",
            created=False,
            requested=False,
        )

        self.assertTrue(changed)
        config.deactivate_service.assert_called_once_with("pam")
        config.activate_service.assert_not_called()

    def test_service_activation_is_idempotent(self):
        config = MagicMock()
        config.list_active_services.return_value = ["pam"]

        changed = _sssd_config.set_service_active(
            config,
            "pam",
            created=False,
            requested=True,
        )

        self.assertFalse(changed)
        config.activate_service.assert_not_called()
        config.deactivate_service.assert_not_called()

    def test_new_service_defaults_to_inactive_when_activation_is_omitted(self):
        config = MagicMock()
        config.list_active_services.return_value = ["pam"]

        changed = _sssd_config.set_service_active(
            config,
            "pam",
            created=True,
            requested=None,
        )

        self.assertTrue(changed)
        config.deactivate_service.assert_called_once_with("pam")
        config.activate_service.assert_not_called()


class TestDeleteService(unittest.TestCase):
    def test_active_service_is_deactivated_before_deletion(self):
        config = MagicMock()
        config.list_active_services.return_value = ["nss", "pam"]

        _sssd_config.delete_service(config, "pam")

        self.assertEqual(
            config.method_calls,
            [
                call.list_active_services(),
                call.deactivate_service("pam"),
                call.delete_service("pam"),
            ],
        )

    def test_inactive_service_is_deleted_without_deactivation(self):
        config = MagicMock()
        config.list_active_services.return_value = ["nss"]

        _sssd_config.delete_service(config, "pam")

        config.deactivate_service.assert_not_called()
        config.delete_service.assert_called_once_with("pam")


class TestRemoveOptions(unittest.TestCase):
    def test_empty_domain_option_names_are_idempotent(self):
        domain = FakeDomain(options={"id_provider": "ldap"})

        changed = _sssd_config.remove_domain_options(domain, ())

        self.assertFalse(changed)
        self.assertEqual(domain.remove_provider_calls, [])
        self.assertEqual(domain.remove_option_calls, [])

    def test_domain_provider_uses_remove_provider(self):
        domain = FakeDomain(options={"id_provider": "ldap"})

        changed = _sssd_config.remove_domain_options(domain, ("id_provider",))

        self.assertTrue(changed)
        self.assertEqual(domain.remove_provider_calls, [call("id")])
        self.assertEqual(domain.remove_option_calls, [])

    def test_regular_domain_option_uses_remove_option(self):
        domain = FakeDomain(options={"cache_credentials": True})

        changed = _sssd_config.remove_domain_options(domain, ("cache_credentials",))

        self.assertTrue(changed)
        self.assertEqual(domain.remove_provider_calls, [])
        self.assertEqual(domain.remove_option_calls, [call("cache_credentials")])

    def test_service_provider_named_option_uses_remove_option(self):
        service = FakeService(options={"id_provider": "ldap"})

        changed = _sssd_config.remove_service_options(service, ("id_provider",))

        self.assertTrue(changed)
        self.assertEqual(service.remove_option_calls, [call("id_provider")])

    def test_empty_service_option_names_are_idempotent(self):
        service = FakeService(options={"pam_verbosity": 1})

        changed = _sssd_config.remove_service_options(service, ())

        self.assertFalse(changed)
        self.assertEqual(service.remove_option_calls, [])

    def test_empty_sssd_option_names_are_idempotent(self):
        config = MagicMock()

        changed = _sssd_config.remove_sssd_options(config, ())

        self.assertFalse(changed)
        config.findOpts.assert_not_called()
        config.delete_option_subtree.assert_not_called()

    def test_removes_requested_sssd_options(self):
        config = MagicMock()
        config.opts = object()
        section_values = object()
        config.findOpts.return_value = (
            4,
            {"type": "section", "name": "sssd", "value": section_values},
        )

        changed = _sssd_config.remove_sssd_options(
            config,
            ("services", "debug_level"),
        )

        self.assertTrue(changed)
        config.findOpts.assert_called_once_with(config.opts, "section", "sssd")
        self.assertEqual(
            config.delete_option_subtree.call_args_list,
            [
                call(section_values, "option", "services", True),
                call(section_values, "option", "debug_level", True),
            ],
        )


class TestSSSDOptions(unittest.TestCase):
    def test_serialize_list(self):
        self.assertEqual(
            _sssd_config.serialize_option_value("services", ["nss", "pam"]),
            "nss, pam",
        )

    def test_serialize_large_debug_level_as_hexadecimal(self):
        self.assertEqual(
            _sssd_config.serialize_option_value("debug_level", 32),
            "0x20",
        )

    def test_serialize_small_debug_level_as_decimal(self):
        self.assertEqual(
            _sssd_config.serialize_option_value("debug_level", 16),
            "16",
        )

    def test_serialize_regular_scalar_as_string(self):
        self.assertEqual(
            _sssd_config.serialize_option_value("config_file_version", 2),
            "2",
        )

    def test_set_sssd_options_is_idempotent_for_matching_explicit_value(self):
        section = FakeService(options={"config_file_version": 2})
        config = MagicMock()
        config.get_service.return_value = section
        config.has_option.return_value = True

        changed = _sssd_config.set_sssd_options(
            config,
            {"config_file_version": 2},
        )

        self.assertFalse(changed)
        config.set.assert_not_called()

    def test_set_sssd_options_materializes_implicit_default(self):
        section = FakeService(options={"config_file_version": 2})
        config = MagicMock()
        config.get_service.return_value = section
        config.has_option.return_value = False

        changed = _sssd_config.set_sssd_options(
            config,
            {"config_file_version": 2},
        )

        self.assertTrue(changed)
        config.set.assert_called_once_with("sssd", "config_file_version", "2")

    def test_set_sssd_options_writes_normalized_value(self):
        section = FakeService(
            options={"services": ["nss"]},
            normalizers={"services": lambda value: [item.strip() for item in value.split(",")]},
        )
        config = MagicMock()
        config.get_service.return_value = section
        config.has_option.return_value = True

        changed = _sssd_config.set_sssd_options(
            config,
            {"services": "nss, pam"},
        )

        self.assertTrue(changed)
        config.set.assert_called_once_with("sssd", "services", "nss, pam")

    def test_set_sssd_options_serializes_large_debug_level(self):
        section = FakeService(options={"debug_level": 0})
        config = MagicMock()
        config.get_service.return_value = section
        config.has_option.return_value = True

        changed = _sssd_config.set_sssd_options(
            config,
            {"debug_level": 32},
        )

        self.assertTrue(changed)
        config.set.assert_called_once_with("sssd", "debug_level", "0x20")

    def test_set_sssd_options_propagates_schema_validation_error(self):
        section = MagicMock()
        section.get_all_options.return_value = {"config_file_version": 2}
        section.set_option.side_effect = ValueError("invalid value")
        config = MagicMock()
        config.get_service.return_value = section
        config.has_option.return_value = True

        with self.assertRaisesRegex(ValueError, "invalid value"):
            _sssd_config.set_sssd_options(
                config,
                {"config_file_version": "invalid"},
            )

        config.set.assert_not_called()
