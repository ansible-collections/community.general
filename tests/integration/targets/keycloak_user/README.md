<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->
# Running keycloak_user module integration test

To run Keycloak user module's integration test, start a keycloak server using Docker or Podman:

    podman|docker run -d --rm --name mykeycloak -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=password quay.io/keycloak/keycloak:latest start-dev --http-relative-path /auth

Source Ansible env-setup from ansible github repository

Run integration tests:

    ansible-test integration keycloak_user --python 3.10 --allow-unsupported

Cleanup:

    podman|docker stop mykeycloak

