# Copyright (c) 2026, Nicholas Brodersen <nicholasbrodersen01@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from ansible.module_utils.common import respawn

from ansible_collections.community.general.plugins.module_utils import _deps as deps

with deps.declare("SSSDConfig"):
    from SSSDConfig import SSSDConfig  # type: ignore[import-not-found]


SSSDOptionMapping = t.Mapping[str, object]


@dataclass(frozen=True)
class SSSDTarget:
    path: str
    section: str
    name: str | None = None

    def __post_init__(self) -> None:
        # Validation here so that other modules like sssd_domain and sssd_service can use this and be used safely
        if self.section not in ("sssd", "domain", "service"):
            raise ValueError(f"Unsupported SSSD section type: {self.section}")

        if self.section == "sssd":
            if self.name is not None:
                raise ValueError("The sssd section must not have a name")
        elif not self.name:
            raise ValueError(f"The {self.section} section requires a name")

    @property
    def section_name(self) -> str:
        if self.section == "sssd":
            return "sssd"

        name = self.name
        if name is None:
            raise ValueError(f"The {self.section} section requires a name")

        if self.section == "domain":
            return f"domain/{name}"

        return name


@dataclass(frozen=True)
class EnsurePresent:
    target: SSSDTarget
    options: SSSDOptionMapping
    must_exist: bool = False
    active: bool | None = None


@dataclass(frozen=True)
class RemoveOptions:
    target: SSSDTarget
    option_names: tuple[str, ...]


@dataclass(frozen=True)
class RemoveSection:
    target: SSSDTarget


SSSDRequest = t.Union[EnsurePresent, RemoveOptions, RemoveSection]


def _respawn_sssdconfig() -> None:
    if respawn.has_respawned():
        return
    system_interpreters = (
        "/usr/libexec/platform-python",
        "/usr/bin/python3",
        "/usr/bin/python",
    )
    interpreter = respawn.probe_interpreters_for_module(system_interpreters, "SSSDConfig")
    if interpreter:
        respawn.respawn_module(interpreter)


def create_sssd_config() -> SSSDConfig:
    return SSSDConfig()


def get_explicit_options(sssd_config, section_name: str) -> dict[str, object]:
    if not sssd_config.has_section(section_name):
        return {}

    return {
        option["name"]: option["value"]
        for option in sssd_config.strip_comments_empty(sssd_config.options(section_name))
    }


def set_domain_options(domain, requested_options: SSSDOptionMapping, explicit_options: SSSDOptionMapping) -> bool:
    before = dict(domain.get_all_options())

    provider_options = {name: value for name, value in requested_options.items() if name.endswith("_provider")}

    regular_options = {name: value for name, value in requested_options.items() if not name.endswith("_provider")}

    for option, value in provider_options.items():
        current_value = domain.get_all_options().get(option)

        if current_value is not None and current_value != value:
            provider_type = option[:-9]
            domain.remove_provider(provider_type)

        domain.set_option(option, value)

    for option, value in regular_options.items():
        domain.set_option(option, value)

    after = domain.get_all_options()

    return before != after or any(option not in explicit_options for option in requested_options)


def set_service_options(service, requested_options: SSSDOptionMapping, explicit_options: SSSDOptionMapping) -> bool:
    before = dict(service.get_all_options())

    for option, value in requested_options.items():
        service.set_option(option, value)

    after = service.get_all_options()

    return before != after or any(option not in explicit_options for option in requested_options)


def set_domain_active(domain, created: bool, requested: bool | None) -> bool:
    if requested is None:
        if not created:
            return False

        requested = False

    if domain.active == requested:
        return False

    domain.set_active(requested)
    return True


def set_service_active(sssd_config, name: str, created: bool, requested: bool | None) -> bool:
    if requested is None:
        if not created:
            return False

        requested = False

    currently_active = name in sssd_config.list_active_services()

    if currently_active == requested:
        return False

    if requested:
        sssd_config.activate_service(name)
    else:
        sssd_config.deactivate_service(name)

    return True


def delete_service(sssd_config, name: str) -> None:
    if name in sssd_config.list_active_services():
        sssd_config.deactivate_service(name)

    sssd_config.delete_service(name)


def serialize_option_value(option: str, value: object) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)

    if option == "debug_level" and isinstance(value, int) and value > 16:
        value = hex(value)

    return str(value)


def set_sssd_options(sssd_config, requested_options: SSSDOptionMapping) -> bool:
    # the SSSDConfig class exposes the [sssd] section schema through its SSSDService class
    # writing the [sssd] section itself requires SSSDConfig
    sssd_section = sssd_config.get_service("sssd")
    current_options = dict(sssd_section.get_all_options())

    changed = False

    for option, requested_value in requested_options.items():
        explicitly_present = sssd_config.has_option("sssd", option)
        current_value = current_options.get(option)

        # SSSDConfig class validates and normalizes the requested value.
        sssd_section.set_option(option, requested_value)
        normalized_value = sssd_section.get_option(option)

        if not explicitly_present or current_value != normalized_value:
            sssd_config.set(
                "sssd",
                option,
                serialize_option_value(option, normalized_value),
            )
            changed = True

    return changed


def remove_domain_options(domain, option_names: t.Iterable[str]) -> bool:
    changed = False
    for option in option_names:
        if option.endswith("_provider"):
            domain.remove_provider(option[:-9])
        else:
            domain.remove_option(option)
        changed = True
    return changed


def remove_service_options(service, option_names: t.Iterable[str]) -> bool:
    changed = False
    for option in option_names:
        service.remove_option(option)
        changed = True
    return changed


def remove_sssd_options(sssd_config, option_names: t.Iterable[str]) -> bool:
    sssd_section = None
    changed = False

    for option in option_names:
        if sssd_section is None:
            sssd_section = sssd_config.findOpts(
                sssd_config.opts,
                "section",
                "sssd",
            )[1]

        sssd_config.delete_option_subtree(
            sssd_section["value"],
            "option",
            option,
            True,
        )
        changed = True

    return changed
