<!--
Copyright (c) 2026, Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# community.general

This file is the primary AI context document for this repository. It is tool-agnostic.
Tool-specific extensions (e.g. Claude Code skills) live in their own locations.

## Identity

This is an Ansible collection, written mostly in Python.

## Commands

- Test: `ansible-test` (users may choose to use `andebox` as a wrapper — see `.agents/rules/andebox.md`)
- Lint:
  - Formatting (with auto fix): `nox -e formatters` (ruff)
  - Code quality: `nox -e codeqa` (ruff)
  - Typing: `nox -e typing` (mypy)

## Architecture

Distributed and agent-less configuration mgmt system. It is run from a controller node,
and the code is dynamically transported and executed in target nodes.

- `plugins/modules` - Ansible modules (run in targets)
- `plugins/module_utils` - shared code for Ansible modules (run in targets)
- `plugins/plugin_utils` - shared code for other plugins (run in the controller)
- `plugins/doc_fragments` - shared documentation for modules - not used in runtime
- `plugins/` - all other subdirectories contain code for specific plugin types (run in the controller)

## Code Style

- Python: as defined in `ruff.toml`
- YAML: indent 2, +2 offset for lists

## Hard Rules

- NEVER commit directly to `main`
- Always keep track of the branch you are making changes to.

## Human Review Required

- All changes before committing

## Project Rules

This project's conventions are defined as separate rule files in `.agents/rules/`.
Read `.agents/INDEX.md` for the complete indexed list — it names every rule file
that applies to this project. Claude Code loads them automatically via the import
below; other tools should read each file listed in `.agents/INDEX.md` at the start
of the session.

@.agents/INDEX.md

## Workflows

Common contributor workflows are described in `.agents/skills/`. Claude Code users
have these registered as invocable skills; other tool users can read those files
directly.
