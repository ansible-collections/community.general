<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

---
paths:
  - "**/*.py"
---

# Python Coding Rules

- The Ansible machinery makes convoluted changes to the importing machinery, so it is common to have unsolved symbols
  during development time, but that will work fine in test time and run time.
