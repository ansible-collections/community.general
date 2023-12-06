<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->
# Running keycloak_component_info module integration test

To run Keycloak component info module's integration test, start a keycloak server using Docker:

    docker run -d --rm --name myldap -p 389:389 minkwe/389ds:latest
    docker run -d --rm --name mykeycloak --link myldap:ldap.example.com -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=password quay.io/keycloak/keycloak:latest start-dev --http-relative-path /auth

Run integration tests:
    ansible-test integration -v keycloak_component_info --allow-unsupported --docker fedora35 --docker-network host

Cleanup:

    docker stop myldap mykeycloak


