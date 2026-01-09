# Copyright (c) 2014, Kevin Carter <kevin.carter@rackspace.com>
# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import subprocess
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

# This is used to attach to a running container and execute commands from
# within the container on the host.  This will provide local access to a
# container without using SSH.  The template will attempt to work within the
# home directory of the user that was attached to the container and source
# that users environment variables by default.
ATTACH_TEMPLATE = """#!/usr/bin/env bash
pushd "$(getent passwd $(whoami)|cut -f6 -d':')"
    if [[ -f ".bashrc" ]];then
        source .bashrc
        unset HOSTNAME
    fi
popd

# User defined command
{}
"""


def create_script(command: str, module: AnsibleModule) -> None:
    """Write out a script onto a target.

    This method should be backward compatible with Python when executing
    from within the container.

    :param command: command to run, this can be a script and can use spacing
                    with newlines as separation.
    :param module: AnsibleModule to run commands with.
    """

    script_file = ""
    try:
        f = tempfile.NamedTemporaryFile(prefix="lxc-attach-script", delete=False, mode="wb")
        f.write(to_bytes(ATTACH_TEMPLATE.format(command), errors="surrogate_or_strict"))
        script_file = f.name
        f.flush()
        f.close()

        os.chmod(script_file, 0o0700)

        with tempfile.NamedTemporaryFile(prefix="lxc-attach-script-log", delete=False, mode="ab") as stdout_file:
            with tempfile.NamedTemporaryFile(prefix="lxc-attach-script-err", delete=False, mode="ab") as stderr_file:
                subprocess.Popen([script_file], stdout=stdout_file, stderr=stderr_file).communicate()

    finally:
        if script_file:
            os.remove(script_file)
