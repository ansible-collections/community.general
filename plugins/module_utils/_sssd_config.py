# Copyright (c) 2026, Nicholas Brodersen <nicholasbrodersen01@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Union, cast

HAS_SSSD_LIB = False
SSSDCONFIG_IMPORT_ERROR = ""
_SSSDConfig: Any = None

try:
    from SSSDConfig import SSSDConfig as _ImportedSSSDConfig  # type: ignore[import-not-found]

    _SSSDConfig = _ImportedSSSDConfig
    HAS_SSSD_LIB = True
except ImportError:
    SSSDCONFIG_IMPORT_ERROR = traceback.format_exc()


@dataclass(frozen=True)
class SSSDTarget:
    path: str
    section: str
    name: Optional[str] = None

    @property
    def section_name(self) -> str:
        if self.section == "domain":
            return f"domain/{self.name}"

        if self.section == "service":
            return cast(str, self.name)

        return "sssd"


@dataclass(frozen=True)
class EnsurePresent:
    target: SSSDTarget
    options: Mapping[str, Any]
    must_exist: bool = False
    active: Optional[bool] = None


@dataclass(frozen=True)
class RemoveOptions:
    target: SSSDTarget
    option_names: tuple[str, ...]


@dataclass(frozen=True)
class RemoveSection:
    target: SSSDTarget


SSSDRequest = Union[EnsurePresent, RemoveOptions, RemoveSection]


def create_sssd_config():
    if _SSSDConfig is None:
        raise ImportError("the SSSDConfig Python library is unavailable")

    return _SSSDConfig()


def get_explicit_options(sssd_config, section_name: str) -> dict:
    if not sssd_config.has_section(section_name):
        return {}

    return {
        option["name"]: option["value"]
        for option in sssd_config.strip_comments_empty(sssd_config.options(section_name))
    }


def set_domain_options(domain, requested_options: Mapping[str, Any], explicit_options: Mapping[str, Any]) -> bool:
    before = dict(domain.get_all_options())

    provider_options = {name: value for name, value in requested_options.items() if name.endswith("_provider")}

    regular_options = {name: value for name, value in requested_options.items() if not name.endswith("_provider")}

    for option, value in provider_options.items():
        current_value = domain.get_all_options().get(option)

        if current_value is not None and current_value != value:
            provider_type = option[: -len("_provider")]
            domain.remove_provider(provider_type)

        domain.set_option(option, value)

    for option, value in regular_options.items():
        domain.set_option(option, value)

    after = domain.get_all_options()

    return before != after or any(option not in explicit_options for option in requested_options)


def set_service_options(service, requested_options: Mapping[str, Any], explicit_options: Mapping[str, Any]) -> bool:
    before = dict(service.get_all_options())

    for option, value in requested_options.items():
        service.set_option(option, value)

    after = service.get_all_options()

    return before != after or any(option not in explicit_options for option in requested_options)


def set_domain_active(domain, created: bool, requested: Optional[bool]) -> bool:
    if requested is None:
        if not created:
            return False

        requested = False

    if domain.active == requested:
        return False

    domain.set_active(requested)
    return True


def set_service_active(sssd_config, name: str, created: bool, requested: Optional[bool]) -> bool:
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


def serialize_option_value(option: str, value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)

    if option == "debug_level" and isinstance(value, int) and value > 16:
        value = hex(value)

    return str(value)


def set_sssd_options(sssd_config, requested_options: Mapping[str, Any]) -> bool:
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


def remove_domain_options(domain, option_names: Iterable[str]) -> bool:
    option_names = tuple(option_names)

    for option in option_names:
        if option.endswith("_provider"):
            domain.remove_provider(option[: -len("_provider")])
        else:
            domain.remove_option(option)

    return bool(option_names)


def remove_service_options(service, option_names: Iterable[str]) -> bool:
    option_names = tuple(option_names)

    for option in option_names:
        service.remove_option(option)

    return bool(option_names)


def remove_sssd_options(sssd_config, option_names: Iterable[str]) -> bool:
    option_names = tuple(option_names)

    if not option_names:
        return False

    sssd_section = sssd_config.findOpts(
        sssd_config.opts,
        "section",
        "sssd",
    )[1]

    for option in option_names:
        sssd_config.delete_option_subtree(
            sssd_section["value"],
            "option",
            option,
            True,
        )

    return True
