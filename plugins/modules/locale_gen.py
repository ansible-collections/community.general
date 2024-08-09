#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: locale_gen
short_description: Creates or removes locales
description:
    - Manages locales by editing /etc/locale.gen and invoking locale-gen.
author:
    - Augustus Kling (@AugustusKling)
extends_documentation_fragment:
    - community.general.attributes
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
            - Whether the locale shall be present.
        choices: [ absent, present ]
        default: present
notes:
    - This module does not support RHEL-based systems.
'''

EXAMPLES = '''
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
'''

import os
import re

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.mh.deco import check_mode_skip

from ansible_collections.community.general.plugins.module_utils.locale_gen import locale_runner, locale_gen_runner


class LocaleGen(StateModuleHelper):
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
    LOCALE_GEN = "/etc/locale.gen"
    LOCALE_SUPPORTED = "/var/lib/locales/supported.d/"

    output_params = ["name"]
    module = dict(
        argument_spec=dict(
            name=dict(type="list", elements="str", required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
    )
    use_old_vardict = False

    def __init_module__(self):
        self.vars.set("ubuntu_mode", False)
        if os.path.exists(self.LOCALE_SUPPORTED):
            self.vars.ubuntu_mode = True
        else:
            if not os.path.exists(self.LOCALE_GEN):
                self.do_raise("{0} and {1} are missing. Is the package \"locales\" installed?".format(
                    self.LOCALE_SUPPORTED, self.LOCALE_GEN
                ))

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
        __regexp = r'^#?\s*(?P<locale>\S+[\._\S]+) (?P<charset>\S+)\s*$'
        if self.vars.ubuntu_mode:
            __locales_available = '/usr/share/i18n/SUPPORTED'
        else:
            __locales_available = '/etc/locale.gen'

        re_compiled = re.compile(__regexp)
        with open(__locales_available, 'r') as fd:
            lines = fd.readlines()
            res = [re_compiled.match(line) for line in lines]
            if self.verbosity >= 4:
                self.vars.available_lines = lines

            locales_not_found = []
            for locale in self.vars.name:
                # Check if the locale is not found in any of the matches
                if not any(match and match.group("locale") == locale for match in res):
                    locales_not_found.append(locale)

        # locale may be installed but not listed in the file, for example C.UTF-8 in some systems
        locales_not_found = self.locale_get_not_present(locales_not_found)

        if locales_not_found:
            self.do_raise("The following locales you've entered are not available on your system: {0}".format(', '.join(locales_not_found)))

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
        for s, r in self.LOCALE_NORMALIZATION.items():
            name = name.replace(s, r)
        return name

    def set_locale(self, names, enabled=True):
        """ Sets the state of the locale. Defaults to enabled. """
        with open("/etc/locale.gen", 'r') as fr:
            lines = fr.readlines()

        locale_regexes = []

        for name in names:
            search_string = r'^#?\s*%s (?P<charset>.+)' % re.escape(name)
            if enabled:
                new_string = r'%s \g<charset>' % (name)
            else:
                new_string = r'# %s \g<charset>' % (name)
            re_search = re.compile(search_string)
            locale_regexes.append([re_search, new_string])

        for i in range(len(lines)):
            for [search, replace] in locale_regexes:
                lines[i] = search.sub(replace, lines[i])

        # Write the modified content back to the file
        with open("/etc/locale.gen", 'w') as fw:
            fw.writelines(lines)

    def apply_change(self, targetState, names):
        """Create or remove locale.

        Keyword arguments:
        targetState -- Desired state, either present or absent.
        names -- Names list including encoding such as de_CH.UTF-8.
        """

        self.set_locale(names, enabled=(targetState == "present"))

        runner = locale_gen_runner(self.module)
        with runner() as ctx:
            ctx.run()

    def apply_change_ubuntu(self, targetState, names):
        """Create or remove locale.

        Keyword arguments:
        targetState -- Desired state, either present or absent.
        names -- Name list including encoding such as de_CH.UTF-8.
        """
        runner = locale_gen_runner(self.module)

        if targetState == "present":
            # Create locale.
            # Ubuntu's patched locale-gen automatically adds the new locale to /var/lib/locales/supported.d/local
            with runner() as ctx:
                ctx.run()
        else:
            # Delete locale involves discarding the locale from /var/lib/locales/supported.d/local and regenerating all locales.
            with open("/var/lib/locales/supported.d/local", "r") as fr:
                content = fr.readlines()
            with open("/var/lib/locales/supported.d/local", "w") as fw:
                for line in content:
                    locale, charset = line.split(' ')
                    if locale not in names:
                        fw.write(line)
            # Purge locales and regenerate.
            # Please provide a patch if you know how to avoid regenerating the locales to keep!
            with runner("purge") as ctx:
                ctx.run()

    @check_mode_skip
    def __state_fallback__(self):
        if self.vars.state_tracking == self.vars.state:
            return
        if self.vars.ubuntu_mode:
            self.apply_change_ubuntu(self.vars.state, self.vars.name)
        else:
            self.apply_change(self.vars.state, self.vars.name)


def main():
    LocaleGen.execute()


if __name__ == '__main__':
    main()
