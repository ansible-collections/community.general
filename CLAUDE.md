# community.general

## Identity
This is an Ansible collection, written mostly in Python.

## Commands
- Test: use `andebox` as a wrapper around `ansible-test`.
- Lint:
  - Formatting (with auto fix): `nox -e formatters` (ruff)
  - Code quality: `nox -e codeqa` (ruff)
  - Typing: `nox -e typing` (mypy)

## Architecture
Distributed and agent-less configuration mgmt system. It is run from a controller node, and the code is dynamically transported and executed in target nodes.
- `plugins/modules` - Ansible modules (run in targets)
- `plugins/module_utils` - shared code for Ansible modules (run in targets)
- `plugins/plugins_utils` - shared code for other plugins (run in the controller)
- `plugins/doc_fragments` - shared documentation for modules - not used in runtime
- `plugins/` - all other subdirectories contain code for specific plugin types (run in the controller)

## Code Style
- Python: as defined in `ruff.toml`
- YAML: indent 2, +2 offset for lists

## Hard Rules
- NEVER commit directly to `main`
- Always keep track of the branch you are making changes to.

## Human Review Required
- All changes before commiting
