<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

---
name: ship-changes
description: >
  Orchestrates the workflow from local uncommitted changes to an open PR with a
  changelog fragment. Covers branching, committing, pushing, PR creation, and
  changelog authoring. Invoke when changes are ready to be shipped — triggered by
  phrases like "go for the PR", "make the PR", "open the PR", "ship it", or similar.
---

@../../../.agents/skills/ship-changes.md
