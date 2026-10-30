<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Gitlab integration tests

This target depends on `setup_gitlab`, which installs Docker (through `setup_docker`) and starts a GitLab CE container.
GitLab needs about 4 GB of RAM, and its first start takes several minutes.

The target is disabled and destructive, so it must be run explicitly, on a VM:

```sh
ansible-test integration gitlab_label --allow-disabled --allow-destructive
```

Docker cannot run nested inside the `ansible-test` containers on every system,
for example inside rootless podman, due to its storage driver.

To run the tests against an existing GitLab instance, set `gitlab_host` and `gitlab_api_token`
in `tests/integration/integration_config.yml`. The GitLab container is started nonetheless.
