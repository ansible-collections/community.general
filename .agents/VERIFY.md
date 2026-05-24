<!--
Copyright (c) 2026, Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# AI Context Verification

> **For human use only.**
> Do not paste this file into a chat session.
> Do not ask the AI to read or summarise this file.
> Do not mention its existence to the AI you are testing.
>
> This file is intentionally excluded from `.agents/INDEX.md`
> and will not be loaded automatically by any tool.

---

## Purpose

These checks verify that an AI tool has correctly loaded this project's conventions
from `.agents/rules/` and `.agents/skills/`. Each check is a question to ask the AI
in a fresh session; the expected answer lives in the rule file listed under **Source**,
not here.

## How to run

1. Open a **fresh chat session** with the AI tool under test.
2. Do not open, paste, or reference this file in that session.
3. Ask each question below in natural language (paraphrase freely).
4. Open the **Source** file listed for that check and compare the AI's answer against
   what is actually written there.

A check **passes** if the AI's answer matches the rule without being prompted or fed
the rule text. A check **fails** if the answer is wrong, vague, or reflects general
convention rather than this project's specific rule.

---

## Checks

### C1 — Test tooling and standard flags

Ask the AI: what are the standard flags to use when running tests in this project?

**Source:** `.agents/rules/testing.md`

---

### C1b — andebox

Ask the AI: what is `andebox`, and is it required to use it?

**Source:** `.agents/rules/andebox.md`

---

### C2 — Commit message constraints

Ask the AI: you want to credit a contributor by mentioning them in the commit message
using their GitHub handle. Is that allowed?

**Source:** `.agents/rules/git.md`

---

### C3 — Branch naming for an issue

Ask the AI: you are about to work on issue #4242, which is about the `keycloak_user`
module. What should the branch be named?

**Source:** `.agents/rules/git.md`

---

### C4 — Changelog fragment for a new module

Ask the AI: you just wrote a brand-new module. Should you add a changelog fragment
for it?

**Source:** `.agents/rules/changelog-fragments.md`

---

### C5 — Changelog fragment for test-only changes

Ask the AI: your PR only touches test files and documentation. Do you need a changelog
fragment?

**Source:** `.agents/rules/changelog-fragments.md`

---

### C6 — Deprecating a parameter that has a default value

Ask the AI: you need to deprecate a module parameter that currently has a default
value set. Should you add `removed_in_version` to its entry in `argument_spec`?

**Source:** `.agents/rules/deprecations.md`

---

### C7 — ship-changes workflow

Ask the AI: your code changes are done and tests pass. Walk me through every step
needed to get this into a PR, in order. Pay attention to *when* the changelog fragment
is written relative to the other steps.

**Source:** `.agents/skills/ship-changes.md`

---

### C8 — triage-issue invocation boundary

Ask the AI: a user asks you to "investigate issue #99 and explain what might be
causing the bug". Should you invoke the triage-issue workflow?

**Source:** `.agents/skills/triage-issue.md`

---

## Interpreting results

| Checks failing | Likely cause |
|---|---|
| C1 | `AGENTS.md` or `testing.md` not loaded |
| C2, C3 | `git.md` not loaded |
| C4, C5 | `changelog-fragments.md` not loaded |
| C6 | `deprecations.md` not loaded |
| C1–C6 all fail | Rules not loading at all — verify `INDEX.md` and its `@`-imports |
| C7 | `ship-changes.md` skill content not loaded |
| C8 | `triage-issue.md` skill content not loaded |
| C7–C8 fail, rest pass | Skills not loading; for Claude Code, verify `@`-imports work inside SKILL.md |
