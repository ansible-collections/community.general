#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: locale_gen
short_description: Creates or removes locales
description:
  - Manages locales in Debian and Ubuntu systems.
author:
  - Augustus Kling (@AugustusKling)
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: list
    elements: str
    description:
      - Name and encoding of the locales, such as V(en_GB.UTF-8).
      - Before community.general 9.3.0, this was a string. Using a string still works.
    required: true
  state:
    type: str
    description:
      - Whether the locales shall be present.
    choices: [absent, present]
    default: present

notes:
  - Currently the module is B(only supported for Debian, Ubuntu, and Arch Linux) systems.
  - This module requires the package C(locales) installed in Debian and Ubuntu systems.
  - If C(/etc/locale.gen) exists, the module assumes to be using the B(glibc) mechanism, else it raises an error.
    Support for C(/var/lib/locales/supported.d/) (the V(ubuntu_legacy) mechanism) has been removed in community.general 13.0.0.
  - When using V(glibc) mechanism, it manages locales by editing C(/etc/locale.gen) and running C(locale-gen).
  - Please note that the module asserts the availability of the locale by checking the files C(/usr/share/i18n/SUPPORTED) and
    C(/usr/local/share/i18n/SUPPORTED), but the C(/usr/local) one is not supported by Archlinux.
"""

EXAMPLES = r"""
- name: Ensure a locale exists
  community.general.locale_gen:
    name: de_CH.UTF-8
    state: present

- name: Ensure multiple locales exist
  community.general.locale_gen:
    name:
      - en_GB.UTF-8
      - nl_NL.UTF-8
    state: present
"""

RETURN = r"""
mechanism:
  description: Mechanism used to deploy the locales.
  type: str
  choices:
    - glibc
  returned: success
  sample: glibc
  version_added: 10.2.0
"""

import os
import re

from ansible_collections.community.general.plugins.module_utils.locale_gen import locale_gen_runner, locale_runner
from ansible_collections.community.general.plugins.module_utils.mh.deco import check_mode_skip
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper

ETC_LOCALE_GEN = "/etc/locale.gen"
VAR_LIB_LOCALES = "/var/lib/locales/supported.d"
VAR_LIB_LOCALES_LOCAL = os.path.join(VAR_LIB_LOCALES, "local")
SUPPORTED_LOCALES = ["/usr/share/i18n/SUPPORTED", "/usr/local/share/i18n/SUPPORTED"]
RE_LOCALE_ENTRY = re.compile(r"^\s*#?\s*(?P<locale>\S+[\._\S]+) (?P<charset>\S+)\s*$")
LOCALE_NORMALIZATION = {
    ".utf8": ".UTF-8",
    ".eucjp": ".EUC-JP",
    ".iso885915": ".ISO-8859-15",
    ".cp1251": ".CP1251",
    ".koi8r": ".KOI8-R",
    ".armscii8": ".ARMSCII-8",
    ".euckr": ".EUC-KR",
    ".gbk": ".GBK",
    ".gb18030": ".GB18030",
    ".euctw": ".EUC-TW",
}


class LocaleGen(StateModuleHelper):
    output_params = ["name"]
    module = dict(
        argument_spec=dict(
            name=dict(type="list", elements="str", required=True),
            state=dict(type="str", default="present", choices=["absent", "present"]),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.mechanisms = dict(
            glibc=dict(
                available=SUPPORTED_LOCALES,
                apply_change=self.apply_change_glibc,
            ),
        )

        if os.path.exists(ETC_LOCALE_GEN):
            self.vars.ubuntu_mode = False
            self.vars.mechanism = "glibc"
        else:
            self.do_raise(f'{ETC_LOCALE_GEN} is missing. Is the package "locales" installed?')

        self.runner = locale_runner(self.module)

        self.assert_available()
        self.vars.set("is_present", self.is_present(), output=False)
        self.vars.set("state_tracking", self._state_name(self.vars.is_present), output=False, change=True)

    def __quit_module__(self):
        self.vars.state_tracking = self._state_name(self.is_present())

    @staticmethod
    def _state_name(present):
        return "present" if present else "absent"

    def assert_available(self):
        """Check if the given locales are available on the system. This is done by
        checking either :
        * if the locale is present in /etc/locales.gen
        * or if the locale is present in /usr/share/i18n/SUPPORTED"""

        self.vars.set("available_lines", [], verbosity=4)
        available_locale_entry_re_matches = []
        for locale_path in self.mechanisms[self.vars.mechanism]["available"]:
            if os.path.exists(locale_path):
                with open(locale_path) as fd:
                    self.vars.available_lines.extend(fd.readlines())

        available_locale_entry_re_matches.extend([RE_LOCALE_ENTRY.match(line) for line in self.vars.available_lines])

        locales_not_found = []
        for locale in self.vars.name:
            # Check if the locale is not found in any of the matches
            if not any(match and match.group("locale") == locale for match in available_locale_entry_re_matches):
                locales_not_found.append(locale)

        # locale may be installed but not listed in the file, for example C.UTF-8 in some systems
        locales_not_found = self.locale_get_not_present(locales_not_found)

        if locales_not_found:
            self.do_raise(
                f"The following locales you have entered are not available on your system: {', '.join(locales_not_found)}"
            )

    def is_present(self):
        return not self.locale_get_not_present(self.vars.name)

    def locale_get_not_present(self, locales):
        runner = locale_runner(self.module)
        with runner() as ctx:
            rc, out, err = ctx.run()
            if self.verbosity >= 4:
                self.vars.locale_run_info = ctx.run_info

        not_found = []
        for locale in locales:
            if not any(self.fix_case(locale) == self.fix_case(line) for line in out.splitlines()):
                not_found.append(locale)

        return not_found

    def fix_case(self, name):
        """locale -a might return the encoding in either lower or upper case.
        Passing through this function makes them uniform for comparisons."""
        for s, r in LOCALE_NORMALIZATION.items():
            name = name.replace(s, r)
        return name

    def _get_charset_from_supported(self, locale):
        """Look up the charset for a locale from the SUPPORTED files."""
        for locale_path in SUPPORTED_LOCALES:
            if os.path.exists(locale_path):
                with open(locale_path) as fd:
                    for line in fd:
                        match = RE_LOCALE_ENTRY.match(line)
                        if match and match.group("locale") == locale:
                            return match.group("charset")
        return None

    def set_locale_glibc(self, names, enabled=True):
        """Sets the state of the locale. Defaults to enabled."""
        with open(ETC_LOCALE_GEN) as fr:
            lines = fr.readlines()

        locale_regexes = {}
        matched = set()

        for name in names:
            search_string = rf"^#?\s*{re.escape(name)} (?P<charset>.+)"
            if enabled:
                new_string = rf"{name} \g<charset>"
            else:
                new_string = rf"# {name} \g<charset>"
            locale_regexes[name] = (re.compile(search_string), new_string)

        def search_replace(line):
            for name, (search, replace) in locale_regexes.items():
                new_line = search.sub(replace, line)
                if new_line != line:
                    matched.add(name)
                line = new_line
            return line

        lines = [search_replace(line) for line in lines]

        # For locales not found in /etc/locale.gen (e.g. on Gentoo), add them
        if enabled:
            for name in names:
                if name not in matched:
                    charset = self._get_charset_from_supported(name)
                    if charset:
                        lines.append(f"{name} {charset}\n")

        # Write the modified content back to the file
        with open(ETC_LOCALE_GEN, "w") as fw:
            fw.writelines(lines)

    def apply_change_glibc(self, target_state, names):
        """Create or remove locale.

        Keyword arguments:
        target_state -- Desired state, either present or absent.
        names -- Names list including encoding such as de_CH.UTF-8.
        """

        self.set_locale_glibc(names, enabled=(target_state == "present"))

        runner = locale_gen_runner(self.module)
        with runner() as ctx:
            ctx.run()

    @check_mode_skip
    def __state_fallback__(self):
        if self.vars.state_tracking == self.vars.state:
            return
        self.mechanisms[self.vars.mechanism]["apply_change"](self.vars.state, self.vars.name)


def main():
    LocaleGen.execute()


if __name__ == "__main__":
    main()
