<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

---
name: triage-issue
description: >
  Orchestrates the steps to triage an open issue for compliance.
  Invoke ONLY for compliance-focused requests — phrases like "triage the issue",
  "check compliance of the issue", or similar.
  Do NOT invoke for "analyse issue X", "diagnose issue X", or "investigate issue X"
  — those are code-analysis requests, not triage.
---

@../../../.agents/skills/triage-issue.md
