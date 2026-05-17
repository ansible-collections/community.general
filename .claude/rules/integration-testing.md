---
paths:
  - tests/integration/**
---

# Rules for Writing Integration Tests

- The generic documentation on integration tests is found at: https://docs.ansible.com/projects/ansible/latest/dev_guide/testing_integration.html
- Each directory under `tests/integration/targets` is akin to an Ansible role
- The `aliases` files contains directives that control how/where the tests are executed.
  - More info on the alises is found at: https://docs.ansible.com/projects/ansible/latest/dev_guide/testing/sanity/integration-aliases.html
- Targets named `setup_*` are actual supporting roles. Some noteworthy ones:
  - `setup_remote_tmp_dir`
  - `setup_snap`
  - `setup_docker`
  - `setup_pkg_mgr`
- Tests should:
  - Interact with the actual external services, APIs, commands
    - This may not be feasible for some third party services requiring authentication, paid services, etc
  - Use local alternatives as possible, e.g. docker images (use `setup_docker`)
  - Be implemented in a "black-box" style: we provide inputs and assert the outputs, not interested in the internal details
  - Assert idempotency, i.e. run the same command twice and assert the second time bears no change
- For modules with larget sets of functions, break the tests into smaller files and use `include_tasks`
