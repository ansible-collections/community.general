---
paths:
  - "plugins/*.py"
---

# Plugins Coding Rules

Use all the **Python Coding Rules**, plus:

- By the beginning of the session, you check what is the version in `galaxy.yml`.
  Based on that, you check in https://github.com/ansible-collections/community.general/issues/11482 what are
  the minimum Python version supported for controller nodes and target nodes.
  For each plugin edited or created, use the idiom corresponding to the supported Python version.
- Use type hints.
- Documentation string contain YAML content - that content should be indented with 2 spaces,
  plus extra 2 offset for lists.
- Every plugin file should be structured in the following sequence:
  - copyright and license markers
  - a single import line with `from __future__ import annotations`
  - documentation strings
  - the plugin imports, in the conventional order
  - the actual code
- Documentation strings are `DOCUMENTATION`, `EXAMPLES`, and `RETURN` strings.
  `DOCUMENTATION` is mandatory.
  `EXAMPLES` and `RETURN` are encouraged where applicable.
  Every time you make a change in the code, update the documentation as needed.
  Conversely, when docs are updated, check if the code needs changing as well.
  After all the editing, make sure the docs are synchronized with the code.
- Use American English spelling in documentation strings (e.g. "behavior" not "behaviour", "customize" not "customise").
- Plugins other than `module_utils` and `plugin_utils` are not supposed to be imported elsewhere.
  They are not a public API and there is usually no need to use docstrings.
