---
name: triage-issue
description: >
  Orchestrates the steps to triage an open issue for compliance.
  Invoke ONLY for compliance-focused requests — phrases like "triage the issue",
  "check compliance of the issue", or similar.
  Do NOT invoke for "analyse issue X", "diagnose issue X", or "investigate issue X"
  — those are code-analysis requests, not triage.
---

# triage-issue

Steps to execute in order:

## 1. Check the content of PR
Follow `rules/github-issue.md`. Classify correctly (bugfix vs feature).
Determine whether the PR title or description is compliant with the rules or needs adjustments.

## 2. Changelog fragment
Follow `rules/changelog-fragments.md`. Determine whether a fragment is required.
When it is, determine if the fragment is compliant with the rules or needs adjustments.

## 3. Present/correct non-compliances
Present the non-compliant items from the previous steps to the user.
Ask whether to: fix, comment, or ignore.
Perform the action indicated by the user.
