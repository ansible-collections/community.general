---
name: triage-pr
description: >
  Orchestrates the steps to triage an open PR for compliance.
  Invoke when reviewing PRs, triggered by phrases like "triage the PR",
  "check compliance of the PR", or similar.
---

# triage-pr

Steps to execute in order:

## 1. Check the content of PR
Follow `rules/github-pr.md`. Classify correctly (bugfix vs feature).
Determine whether the PR title or description is compliant with the rules or needs adjustments.

## 2. Changelog fragment
Follow `rules/changelog-fragments.md`. Determine whether a fragment is required.
When it is, determine if the fragment is compliant with the rules or needs adjustments.

## 3. Present/correct non-compliances
Present the non-compliant items from the previous steps to the user.
Ask whether to: fix, comment, or ignore.
Perform the action indicated by the user.
