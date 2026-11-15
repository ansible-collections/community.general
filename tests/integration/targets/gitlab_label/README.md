<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Gitlab integration tests

This target depends on `setup_gitlab`, which installs Docker (through `setup_docker`) and starts a GitLab CE container.
GitLab needs about 4 GB of RAM, and its first start takes several minutes.

The target has the `heavy/gitlab` alias, so it does not run in the regular CI.
It runs in the `nox-heavy-gitlab` GitHub workflow, which must be triggered manually, or locally with:

```sh
nox -Re ansible-test-integration-devel-ubuntu-heavy-gitlab
```

`ansible-test` makes the Docker daemon of the host available inside its container, and GitLab is started there.

To run the tests against an existing GitLab instance, set `gitlab_host` and `gitlab_api_token`
in `tests/integration/integration_config.yml`. The GitLab container is started nonetheless.
