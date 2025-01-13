# -*- coding: utf-8 -*-

# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  global:
    description:
      - The module will pass the C(--global) argument to C(pipx), to execute actions in global scope.
      - The C(--global) is only available in C(pipx>=1.6.0), so make sure to have a compatible version when using this option.
        Moreover, a nasty bug with C(--global) was fixed in C(pipx==1.7.0), so it is strongly recommended you used that version
        or newer.
    type: bool
    default: false
  executable:
    description:
      - Path to the C(pipx) installed in the system.
      - If not specified, the module will use C(python -m pipx) to run the tool, using the same Python interpreter as ansible
        itself.
    type: path
notes:
  - This module requires C(pipx) version 0.16.2.1 or above. From community.general 11.0.0 onwards, the module will require
    C(pipx>=1.7.0).
  - Please note that C(pipx) requires Python 3.6 or above.
  - This module does not install the C(pipx) python package, however that can be easily done with the module M(ansible.builtin.pip).
  - This module does not require C(pipx) to be in the shell C(PATH), but it must be loadable by Python as a module.
  - This module will honor C(pipx) environment variables such as but not limited to E(PIPX_HOME) and E(PIPX_BIN_DIR) passed
    using the R(environment Ansible keyword, playbooks_environment).
seealso:
  - name: C(pipx) command manual page
    description: Manual page for the command.
    link: https://pipx.pypa.io/latest/docs/
"""
