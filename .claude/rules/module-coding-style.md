<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

---
paths:
  - plugins/modules/**.py
  - plugins/module_utils/**.py
  - tests/unit/plugins/modules/**.py
  - tests/unit/plugins/module_utils/**.py
---

# Coding Style for Modules

These rules should be used in new modules.
Do not change the structure of existing modules unless asked to.
Check the documentation guides for more info about these.

- Prefer using `ModuleHelper` or `StateModuleHelper`.
  - Implicitly using `vardict`
- For modules that rely on running CLI commands, prefer using `CmdRunner`,
  or `PythonRunner` if the commands are Python-based.
  - For these modules, prefer writing unit tests with `uthelper`.
  - CmdRunner idioms:
    - Do not pass an arg name that matches the module param name — it is implicit.
    - Use inline `.run()` when the command output is not processed; reserve the
      context manager form for when you need to inspect stdout/stderr.
    - Use `shlex.split()` to expand free-form user-provided args into a list.
- For importing external dependencies, prefer using `deps`.
- Avoid creating module parameters that permit "free-form" args (some modules
  have those, often called `extra_args`) to be passed by the user.
  Those are hard to validate, maintain, and may pose a security risk.
