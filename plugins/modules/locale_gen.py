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
        type: str
        description:
            - Name and encoding of the locale, such as "en_GB.UTF-8".
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
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.vars.set("ubuntu_mode", False)
        if os.path.exists(self.LOCALE_SUPPORTED):
            self.vars.ubuntu_mode = True
        else:
            if not os.path.exists(self.LOCALE_GEN):
                self.do_raise("{0} and {1} are missing. Is the package \"locales\" installed?".format(
                    self.LOCALE_SUPPORTED, self.LOCALE_GEN
                ))

        if not self.is_available():
            self.do_raise("The locale you've entered is not available on your system.")

        self.vars.set("is_present", self.is_present(), output=False)
        self.vars.set("state_tracking", self._state_name(self.vars.is_present), output=False, change=True)

    def __quit_module__(self):
        self.vars.state_tracking = self._state_name(self.is_present())

    @staticmethod
    def _state_name(present):
        return "present" if present else "absent"

    def is_available(self):
        """Check if the given locale is available on the system. This is done by
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
            if any(r.group("locale") == self.vars.name for r in res if r):
                return True
        # locale may be installed but not listed in the file, for example C.UTF-8 in some systems
        return self.is_present()

    def is_present(self):
        runner = locale_runner(self.module)
        with runner() as ctx:
            rc, out, err = ctx.run()
            if self.verbosity >= 4:
                self.vars.locale_run_info = ctx.run_info
        return any(self.fix_case(self.vars.name) == self.fix_case(line) for line in out.splitlines())

    def fix_case(self, name):
        """locale -a might return the encoding in either lower or upper case.
        Passing through this function makes them uniform for comparisons."""
        for s, r in self.LOCALE_NORMALIZATION.items():
            name = name.replace(s, r)
        return name

    def set_locale(self, name, enabled=True):
        """ Sets the state of the locale. Defaults to enabled. """
        search_string = r'#?\s*%s (?P<charset>.+)' % re.escape(name)
        if enabled:
            new_string = r'%s \g<charset>' % (name)
        else:
            new_string = r'# %s \g<charset>' % (name)
        re_search = re.compile(search_string)
        with open("/etc/locale.gen", "r") as fr:
            lines = [re_search.sub(new_string, line) for line in fr]
        with open("/etc/locale.gen", "w") as fw:
            fw.write("".join(lines))

    def apply_change(self, targetState, name):
        """Create or remove locale.

        Keyword arguments:
        targetState -- Desired state, either present or absent.
        name -- Name including encoding such as de_CH.UTF-8.
        """

        self.set_locale(name, enabled=(targetState == "present"))

        runner = locale_gen_runner(self.module)
        with runner() as ctx:
            ctx.run()

    def apply_change_ubuntu(self, targetState, name):
        """Create or remove locale.

        Keyword arguments:
        targetState -- Desired state, either present or absent.
        name -- Name including encoding such as de_CH.UTF-8.
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
                    if locale != name:
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
