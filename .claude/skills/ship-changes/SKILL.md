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

# ship-changes

Steps to execute in order:

## 1. Branch and commit
Follow `rules/git.md`. If on `main`, branch off it before committing. Verify tests
pass where applicable before committing.

## 2. Push and open PR
Follow `rules/github.md`. Use the PR template; classify correctly (bugfix vs feature).

## 3. Changelog fragment
Follow `rules/changelog-fragments.md`. Determine whether a fragment is required.
If yes: draft it (now that the PR number is known), present it for user approval,
then commit and push it.
