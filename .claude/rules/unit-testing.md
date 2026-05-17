---
paths:
  - tests/unit/**/*.py
---

# Rules for Writing Unit Tests

- Prefer `pytest` idioms to write tests
  - Prefer plain functions instead of Test classes
  - Use pytest fixtures when applicable
- Use `mocker` to mock patch symbols
- Use the common tools from `community.internal_test_tools` when applicable, instead of reinventing the wheel.
  - E.g. `ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils.set_module_args`
- When testing modules that call CLI commands, prefer `uthelper`. Other tests can be mixed with the `UTHelper` call.
- Try and avoid adding new entries to the `tests/unit/requirements.txt` file, as it is installed every time,
  for every unit testing, no matter how small or unrelated to the requirements it might be.
- Do not use typing/type hints in the test code, unless requested.
- Tests should:
  - Mock all interaction with external services, APIs, commands
  - NEVER mock the entire module - it defeats the purpose of the testing. Instead, run the module
    and capture the `SystemExit` exception from it.
  - Assert the "happy-path" for the module execution
  - Assert some exception paths (when things go wrong) are handled as gracefully as possible
  - NOT assert Ansible features, e.g. if two parameters are marked in the argument spec as
    mutually exclusive, there is no need to write a test to verify that they cannot be used together.
    It is a given, and `ansible-core` has plenty of tests for those.
