#!/usr/bin/env bash
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

# Connection tests for POSIX platforms use this script by linking to it from the appropriate 'connection_' target dir.
# The name of the inventory group to test is extracted from the directory name following the 'connection_' prefix.

cp files/pct /usr/sbin/pct
chown root:root /usr/sbin/pct
chmod 755 /usr/sbin/pct

"pip$ANSIBLE_TEST_PYTHON_VERSION" install paramiko

./test.sh "$@"
