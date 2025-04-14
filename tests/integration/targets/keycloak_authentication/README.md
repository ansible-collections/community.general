<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->
# Running keycloak_authentication module integration test

Run integration tests:

    ansible-test integration -v keycloak_authentication --allow-unsupported --docker fedora35 --docker-network host