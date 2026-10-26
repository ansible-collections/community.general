#!/bin/sh
# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Exits on the first two attempts, keeps running on the next ones.
# The attempts are counted in the file given as first argument.
count=$(cat "$1" 2>/dev/null || echo 0)
echo $((count + 1)) > "$1"
[ "$count" -lt 2 ] && exit 1
exec sleep 1000
