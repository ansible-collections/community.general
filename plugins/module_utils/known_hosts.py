# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Michael DeHaan <michael.dehaan@gmail.com>, 2012-2013
#
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import os
import hmac
import re

from urllib.parse import urlparse

try:
    from hashlib import sha1
except ImportError:
    import sha as sha1  # type: ignore[no-redef]

HASHED_KEY_MAGIC = "|1|"


def is_ssh_url(url):
    """check if url is ssh"""

    if "@" in url and "://" not in url:
        return True
    for scheme in "ssh://", "git+ssh://", "ssh+git://":
        if url.startswith(scheme):
            return True
    return False


def get_fqdn_and_port(repo_url):
    """chop the hostname and port out of a url"""

    fqdn = None
    port = None
    ipv6_re = re.compile(r"(\[[^]]*\])(?::([0-9]+))?")
    if "@" in repo_url and "://" not in repo_url:
        # most likely an user@host:path or user@host/path type URL
        repo_url = repo_url.split("@", 1)[1]
        match = ipv6_re.match(repo_url)
        # For this type of URL, colon specifies the path, not the port
        if match:
            fqdn, path = match.groups()
        elif ":" in repo_url:
            fqdn = repo_url.split(":")[0]
        elif "/" in repo_url:
            fqdn = repo_url.split("/")[0]
    elif "://" in repo_url:
        # this should be something we can parse with urlparse
        parts = urlparse(repo_url)
        fqdn = parts[1]
        if "@" in fqdn:
            fqdn = fqdn.split("@", 1)[1]
        match = ipv6_re.match(fqdn)
        if match:
            fqdn, port = match.groups()
        elif ":" in fqdn:
            fqdn, port = fqdn.split(":")[0:2]
    return fqdn, port


def check_hostkey(module, fqdn):
    return not not_in_host_file(module, fqdn)


# this is a variant of code found in connection_plugins/paramiko.py and we should modify
# the paramiko code to import and use this.


def not_in_host_file(self, host):
    if "USER" in os.environ:
        user_host_file = os.path.expandvars("~${USER}/.ssh/known_hosts")
    else:
        user_host_file = "~/.ssh/known_hosts"
    user_host_file = os.path.expanduser(user_host_file)

    host_file_list = [
        user_host_file,
        "/etc/ssh/ssh_known_hosts",
        "/etc/ssh/ssh_known_hosts2",
        "/etc/openssh/ssh_known_hosts",
    ]

    hfiles_not_found = 0
    for hf in host_file_list:
        if not os.path.exists(hf):
            hfiles_not_found += 1
            continue

        try:
            with open(hf) as host_fh:
                data = host_fh.read()
        except IOError:
            hfiles_not_found += 1
            continue

        for line in data.split("\n"):
            if line is None or " " not in line:
                continue
            tokens = line.split()
            if tokens[0].find(HASHED_KEY_MAGIC) == 0:
                # this is a hashed known host entry
                try:
                    (kn_salt, kn_host) = tokens[0][len(HASHED_KEY_MAGIC) :].split("|", 2)
                    hash = hmac.new(kn_salt.decode("base64"), digestmod=sha1)
                    hash.update(host)
                    if hash.digest() == kn_host.decode("base64"):
                        return False
                except Exception:
                    # invalid hashed host key, skip it
                    continue
            else:
                # standard host file entry
                if host in tokens[0]:
                    return False

    return True


def add_host_key(module, fqdn, port=22, key_type="rsa", create_dir=False):
    """use ssh-keyscan to add the hostkey"""

    keyscan_cmd = module.get_bin_path("ssh-keyscan", True)

    if "USER" in os.environ:
        user_ssh_dir = os.path.expandvars("~${USER}/.ssh/")
        user_host_file = os.path.expandvars("~${USER}/.ssh/known_hosts")
    else:
        user_ssh_dir = "~/.ssh/"
        user_host_file = "~/.ssh/known_hosts"
    user_ssh_dir = os.path.expanduser(user_ssh_dir)

    if not os.path.exists(user_ssh_dir):
        if create_dir:
            try:
                os.makedirs(user_ssh_dir, int("700", 8))
            except Exception:
                module.fail_json(msg=f"failed to create host key directory: {user_ssh_dir}")
        else:
            module.fail_json(msg=f"{user_ssh_dir} does not exist")
    elif not os.path.isdir(user_ssh_dir):
        module.fail_json(msg=f"{user_ssh_dir} is not a directory")

    if port:
        this_cmd = f"{keyscan_cmd} -t {key_type} -p {port} {fqdn}"
    else:
        this_cmd = f"{keyscan_cmd} -t {key_type} {fqdn}"

    rc, out, err = module.run_command(this_cmd)
    # ssh-keyscan gives a 0 exit code and prints nothing on timeout
    if rc != 0 or not out:
        msg = "failed to retrieve hostkey"
        if not out:
            msg += f'. "{this_cmd}" returned no matches.'
        else:
            msg += f' using command "{this_cmd}". [stdout]: {out}'

        if err:
            msg += f" [stderr]: {err}"

        module.fail_json(msg=msg)

    module.append_to_file(user_host_file, out)

    return rc, out, err
