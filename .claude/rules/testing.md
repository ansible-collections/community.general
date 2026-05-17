# Rules for Tests

- Never invoke `ansible-test` directly; always use `andebox` as the wrapper.
- Run sanity tests with: `andebox test sanity -- --docker default --python 3.13 <files>` - omit files to test sanity of everything
- Run unit tests with: `andebox test units -- --docker default --python 3.13 tests/unit/plugins/<plugin_type>/<test_file.py>` (pytest/unittest) - omit the directory/file to unit test everything
- Run integration tests with: `andebox test integration -- --docker default --python 3.13 <target name>`
  (Ansible code) - target may be omitted to test everything,
  but that is discouraged as it takes a long while
  - Some integration tests must run on a full fledged VM, not in a container, e.g. `snap`.
    In those cases, use: `andebox vagrant -n ubuntu-noble -s -- snap -v`. Use `--help` if needed.
- If you need to run a test with different versions of Ansible, you may use `tox-test`,
  which is nothing more than an `andebox test` executed inside a `tox` venv with
  specific versions of Ansible, for example:
  ```
  andebox tox-test -e ac218 -- units --python 3.8 --docker default tests/unit/plugins/modules/test_*.py
  ```
  The available `tox` envs may be found in the file `.andebox-tox-test.ini`.
- PRs are only merged into `main` if they pass the tests
- Do not re-run a test suite that already passed in the current session unless new code changes have been made since the last run.
