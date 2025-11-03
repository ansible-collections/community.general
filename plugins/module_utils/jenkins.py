# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


import os
import time


def download_updates_file(updates_expiration):
    updates_filename = "jenkins-plugin-cache.json"
    updates_dir = os.path.expanduser("~/.ansible/tmp")
    updates_file = os.path.join(updates_dir, updates_filename)
    download_updates = True

    # Make sure the destination directory exists
    if not os.path.isdir(updates_dir):
        os.makedirs(updates_dir, 0o700)

    # Check if we need to download new updates file
    if os.path.isfile(updates_file):
        # Get timestamp when the file was changed last time
        ts_file = os.stat(updates_file).st_mtime
        ts_now = time.time()

        if ts_now - ts_file < updates_expiration:
            download_updates = False

    return updates_file, download_updates
