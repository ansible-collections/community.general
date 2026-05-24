<!--
Copyright (c) 2026, Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# ship-changes

Steps to execute in order:

## 1. Branch and commit

Follow `.agents/rules/git.md`. If on `main`, branch off it before committing. Verify tests
pass where applicable before committing.

## 2. Push and open PR

Follow `.agents/rules/github.md`. Use the PR template; classify correctly (bugfix vs feature).

## 3. Changelog fragment

Follow `.agents/rules/changelog-fragments.md`. Determine whether a fragment is required.
If yes: draft it (now that the PR number is known), present it for user approval,
then commit and push it.
