<!--
Copyright (c) 2026, Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Using andebox

`andebox` is a third-party wrapper around `ansible-test` that simplifies running
tests for Ansible collections. It is not required, but contributors who have it
installed can use the commands below instead of the equivalent `ansible-test` ones.

## Running tests

- Sanity: `andebox test sanity -- --docker default --python 3.13 <files>`
  (omit files to test everything)
- Unit: `andebox test units -- --docker default --python 3.13 tests/unit/plugins/<plugin_type>/<test_file.py>`
  (omit the path to test everything)
- Integration: `andebox test integration -- --docker default --python 3.13 <target name>`
  (omit target to test everything, but that takes a long time)

## VM-based integration tests

Some integration tests require a full VM rather than a container (e.g. `snap`).
Use `andebox vagrant`:

```
andebox vagrant -n ubuntu-noble -s -- snap -v
```

Use `--help` if needed.

## Testing against multiple Ansible versions

`andebox nox-test` runs an `andebox test` inside a `nox` session with a specific
Ansible version (available since andebox 2.0.0):

```
andebox nox-test -e ac218 -- units --python 3.8 --docker default tests/unit/plugins/modules/test_*.py
```

Available sessions are listed in `.andebox-nox-test.ini`.
