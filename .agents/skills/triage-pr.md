<!--
Copyright (c) 2026, Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# triage-pr

Steps to execute in order:

## 1. Check the content of PR

Follow `.agents/rules/github-pr.md`. Classify correctly (bugfix vs feature).
Determine whether the PR title or description is compliant with the rules or needs adjustments.

## 2. Changelog fragment

Follow `.agents/rules/changelog-fragments.md`. Determine whether a fragment is required.
When it is, determine if the fragment is compliant with the rules or needs adjustments.

## 3. Present/correct non-compliances

Present the non-compliant items from the previous steps to the user.
Ask whether to: fix, comment, or ignore.
Perform the action indicated by the user.
