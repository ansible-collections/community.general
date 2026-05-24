<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Rules for Tests

Users may choose to use `andebox` as a wrapper around `ansible-test` — see
`.agents/rules/andebox.md` for details and commands.

- Run sanity tests with: `ansible-test sanity --docker default --python 3.13 <files>`
  (omit files to test everything)
- Run unit tests with: `ansible-test units --docker default --python 3.13 tests/unit/plugins/<plugin_type>/<test_file.py>`
  (omit the path to test everything)
- Run integration tests with: `ansible-test integration --docker default --python 3.13 <target name>`
  (omit target to test everything, but that is discouraged as it takes a long while)
  - Some integration tests must run on a full VM, not in a container (e.g. `snap`)
- To test against multiple Ansible versions, see `.agents/rules/andebox.md`
- PRs are only merged into `main` if they pass the tests
- Do not re-run a test suite that already passed in the current session unless new code changes have been made since the last run.
