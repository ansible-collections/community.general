<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->
# Running keycloak_authentication_v2 module integration test

Run integration tests:

    ansible-test integration -v keycloak_authentication_v2 --allow-unsupported --docker fedora --docker-network host