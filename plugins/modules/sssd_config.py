#!/usr/bin/python
# Copyright (c) 2026, Nicholas Brodersen <nicholasbrodersen01@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: sssd_config
short_description: Manage options in the SSSD configuration section
version_added: "13.5.0"
description:
  - Manages options in the top-level C([sssd]) section of an SSSD
    configuration file.
  - Validates and normalizes option names and values according to the
    SSSD schema present on the managed node.
  - The configuration file and its C([sssd]) section must already exist.
  - Unspecified options are preserved.
  - This module does not manage domain or service sections of SSSD configuration files.
author:
  - Nicholas Brodersen (@NicholasBrodersen)
requirements:
  - The SSSDConfig Python library on managed nodes.
  - SSSD configuration schema files on managed nodes.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
    details:
      - Reports whether the requested options would result in a change
        to the specified configuration file.
  diff_mode:
    support: full
    details:
      - Reports changes to configured option names.
      - Option values are omitted because they can contain sensitive data.
options:
  state:
    description:
      - When V(present), the options are added or updated.
      - When V(absent), the option names are removed. Values are ignored.
      - The C([sssd]) section itself is never removed.
    type: str
    choices: [absent, present]
    default: present

  must_exist:
    description:
      - Controls whether options with O(state=present) must already be explicitly configured.
      - When V(true), the module fails instead of adding an option that is not
        currently defined in the C([sssd]) section.
      - Existing option values can still be changed when this is V(true).
      - No effect when O(state=absent).
    type: bool
    default: false

  path:
    description:
      - Path to the SSSD configuration file.
    type: path
    default: /etc/sssd/sssd.conf

  options:
    description:
      - Mapping of C([sssd]) option names to their desired values.
      - Option names and values are validated using the SSSD schema.
      - When O(state=present), options are added or updated while
        unspecified options are preserved.
      - List-valued options such as C(domains) and C(services) are ordered desired values.
        Reordering or omitting a list item changes the final configured value.
      - When O(state=absent), only the mapping keys are used and their values are ignored.
      - Providing an empty mapping results in an idempotent no-operation.
    type: dict
    required: true

notes:
  - The SSSDConfig library and its schema data are normally supplied by operating-system packages.
    Package names differ between distributions.
  - The set of valid options is determined at runtime by the installed SSSD schema.
  - Domain and service sections are outside this module's scope.
  - Restart or reload SSSD separately when the running daemon must consume the updated configuration.
  - Option values are not included in the module return data because an SSSD
    configuration can contain sensitive values.

seealso:
  - module: community.general.sssd_info
"""

EXAMPLES = r"""
- name: Configure top-level SSSD options
  community.general.sssd_config:
    options:
      config_file_version: 2
      services:
        - nss
        - pam
      domains:
        - example.com
      debug_level: 6

- name: Update options only when they are already explicitly configured
  community.general.sssd_config:
    must_exist: true
    options:
      services:
        - nss
        - pam
      domains:
        - example.com

- name: Remove selected options from the sssd section
  community.general.sssd_config:
    state: absent
    options:
      debug_level:
      default_domain_suffix:

- name: Manage an alternate SSSD configuration file
  community.general.sssd_config:
    path: /etc/sssd/sssd-test.conf
    options:
      debug_level: 0x0270
"""

RETURN = r"""
path:
  description:
    - Path to the specified SSSD configuration file.
  returned: always
  type: str
  sample: /etc/sssd/sssd.conf

section_name:
  description:
    - Name of the configuration section.
  returned: always
  type: str
  sample: sssd

exists:
  description:
    - Whether the C([sssd]) section exists after the operation.
  returned: always
  type: bool
  sample: true

option_names:
  description:
    - Names of options defined in the resulting C([sssd]) section.
    - Option values are intentionally omitted because options can contain sensitive data.
    - In check mode, these are the option names predicted if the operation were performed.
  returned: always
  type: list
  elements: str
  sample:
    - config_file_version
    - domains
    - services
"""

from typing import Any, Mapping, Optional, Union, cast

from ansible.module_utils.basic import missing_required_lib

from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils._sssd_config import (
    HAS_SSSD_LIB,
    SSSDCONFIG_IMPORT_ERROR,
    EnsurePresent,
    RemoveOptions,
    SSSDTarget,
    create_sssd_config,
    get_explicit_options,
    remove_sssd_options,
    set_sssd_options,
)

_SSSDRequest = Union[EnsurePresent, RemoveOptions]


def _parse_request(*, state: str, path: str, options: Mapping[str, Any], must_exist: bool) -> _SSSDRequest:
    target = SSSDTarget(path=path, section="sssd")

    if state == "present":
        return EnsurePresent(target=target, options=dict(options), must_exist=must_exist)

    return RemoveOptions(target=target, option_names=tuple(options))


class SSSDConfigModule(StateModuleHelper):
    _result_diff: Optional[dict] = None

    module = dict(
        argument_spec=dict(
            state=dict(
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            must_exist=dict(
                type="bool",
                default=False,
            ),
            path=dict(
                type="path",
                default="/etc/sssd/sssd.conf",
            ),
            options=dict(
                type="dict",
                required=True,
            ),
        ),
        supports_check_mode=True,
    )

    output_params = ("path",)

    def __init_module__(self):
        self.request = _parse_request(
            state=self.vars.state,
            path=self.vars.path,
            options=self.vars.options,
            must_exist=self.vars.must_exist,
        )

        if not HAS_SSSD_LIB:
            self.module.fail_json(
                msg=missing_required_lib("SSSDConfig"),
                exception=SSSDCONFIG_IMPORT_ERROR,
            )

        self.sssd_config = create_sssd_config()
        self.sssd_config.import_config(self.request.target.path)

        if not self.sssd_config.has_section(self.request.target.section_name):
            self.module.fail_json(msg="The sssd section does not exist")

        if self.diff_mode:
            self._diff_before, self._diff_before_options = self._get_diff_state()

    def _get_explicit_options(self) -> dict:
        return get_explicit_options(
            self.sssd_config,
            self.request.target.section_name,
        )

    def _get_diff_state(self):
        options = self._get_explicit_options()

        return {
            "section_name": self.request.target.section_name,
            "exists": True,
            "option_names": sorted(options),
        }, options

    def _set_diff(self) -> None:
        self._result_diff = None

        if not self.diff_mode:
            return

        after, after_options = self._get_diff_state()
        before = dict(self._diff_before)

        changed_option_names = sorted(
            option
            for option in self._diff_before_options.keys() | after_options.keys()
            if (
                option not in self._diff_before_options
                or option not in after_options
                or self._diff_before_options[option] != after_options[option]
            )
        )

        before["changed_option_names"] = []
        after["changed_option_names"] = changed_option_names

        if before != after:
            self._result_diff = {
                "before": before,
                "after": after,
            }

    @property
    def output(self):
        result = super().output

        if self._result_diff is not None:
            result["diff"] = self._result_diff

        return result

    def state_present(self):
        request = cast(EnsurePresent, self.request)
        explicit_options = self._get_explicit_options()

        if request.must_exist:
            missing_options = [option for option in request.options if option not in explicit_options]

            if missing_options:
                self.do_raise(f"The following options must already exist: {', '.join(sorted(missing_options))}")

        if set_sssd_options(self.sssd_config, request.options):
            self.changed = True

    def state_absent(self):
        request = cast(RemoveOptions, self.request)
        explicit_options = self._get_explicit_options()
        options_to_remove = tuple(option for option in request.option_names if option in explicit_options)

        if remove_sssd_options(self.sssd_config, options_to_remove):
            self.changed = True

    def _set_return_values(self) -> None:
        self.update_output(
            section_name=self.request.target.section_name,
            exists=True,
            option_names=sorted(self._get_explicit_options()),
        )

    def __quit_module__(self) -> None:
        self._set_diff()

        if self.changed and not self.check_mode:
            self.sssd_config.write()

        self._set_return_values()


def main():
    SSSDConfigModule().run()


if __name__ == "__main__":
    main()
