<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

The integration test can be performed as follows:

```
# 1. Start docker-compose:
docker-compose -f tests/integration/targets/keycloak_clientsecret_regenerate/docker-compose.yml stop
docker-compose -f tests/integration/targets/keycloak_clientsecret_regenerate/docker-compose.yml rm -f -v
docker-compose -f tests/integration/targets/keycloak_clientsecret_regenerate/docker-compose.yml up -d

# 2. Run the integration tests:
ansible-test integration keycloak_clientsecret_regenerate --allow-unsupported -v
```
