<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

---
paths:
  - docs/docsite/rst/**
  - plugins/**
---

# BOTMETA Rules

- Every time a new file is added within the specified paths, an entry must be created in the BOTMETA file.
- The entry should be placed within the existing section where it belongs,
  and within that section, files should be listed on alphabetical order.
- User handles are never removed, unless explicitly requested.
