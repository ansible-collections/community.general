# -*- coding: utf-8 -*-
# Based on paramiko_ssh.py (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (annotations, absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
    author: Nils Stein (@mietzen) <github.nstein@mailbox.org>
    name: pct_remote
    short_description: Run tasks in Proxmox LXC container instances using pct CLI via ssh
    requirements:
      - paramiko
    description:
      - Run commands or put/fetch files to an existing Proxmox LXC container using pct CLI via ssh.
      - Use the Python SSH implementation (Paramiko) to connect to Proxmox.
    version_added: "9.1.0"
    options:
      remote_addr:
        description:
          - Address of the remote target
        default: inventory_hostname
        type: string
        vars:
          - name: inventory_hostname
          - name: ansible_host
          - name: ansible_ssh_host
          - name: ansible_paramiko_host
      port:
        description: Remote port to connect to.
        type: int
        default: 22
        ini:
          - section: defaults
            key: remote_port
          - section: paramiko_connection
            key: remote_port
        env:
          - name: ANSIBLE_REMOTE_PORT
          - name: ANSIBLE_REMOTE_PARAMIKO_PORT
        vars:
          - name: ansible_port
          - name: ansible_ssh_port
          - name: ansible_paramiko_port
        keyword:
          - name: port
      remote_user:
        description:
          - User to login/authenticate as.
          - It can be set from the CLI via the C(--user) or C(-u) options.
        type: string
        vars:
          - name: ansible_user
          - name: ansible_ssh_user
          - name: ansible_paramiko_user
        env:
          - name: ANSIBLE_REMOTE_USER
          - name: ANSIBLE_PARAMIKO_REMOTE_USER
        ini:
          - section: defaults
            key: remote_user
          - section: paramiko_connection
            key: remote_user
        keyword:
          - name: remote_user
      password:
        description:
          - Secret used to either login the ssh server or as a passphrase for ssh keys that require it.
          - It can be set from the CLI via the C(--ask-pass) option.
        type: string
        vars:
          - name: ansible_password
          - name: ansible_ssh_pass
          - name: ansible_ssh_password
          - name: ansible_paramiko_pass
          - name: ansible_paramiko_password
      use_rsa_sha2_algorithms:
        description:
          - Whether or not to enable RSA SHA2 algorithms for pubkeys and hostkeys.
          - On paramiko versions older than 2.9, this only affects hostkeys.
          - For behavior matching paramiko<2.9 set this to V(False).
        vars:
          - name: ansible_paramiko_use_rsa_sha2_algorithms
        ini:
          - section: paramiko_connection
            key: use_rsa_sha2_algorithms
        env:
          - name: ANSIBLE_PARAMIKO_USE_RSA_SHA2_ALGORITHMS
        default: True
        type: boolean
      host_key_auto_add:
        description: Automatically add host keys.
        env:
          - name: ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD
        ini:
          - section: paramiko_connection
            key: host_key_auto_add
        type: boolean
      look_for_keys:
        default: True
        description: "False to disable searching for private key files in ~/.ssh/."
        env:
          - name: ANSIBLE_PARAMIKO_LOOK_FOR_KEYS
        ini:
          - section: paramiko_connection
            key: look_for_keys
        type: boolean
      proxy_command:
        default: ""
        description:
          - Proxy information for running the connection via a jumphost.
          - Also this plugin will scan 'ssh_args', 'ssh_extra_args' and 'ssh_common_args' from the 'ssh' plugin settings for proxy information if set.
        type: string
        env:
          - name: ANSIBLE_PARAMIKO_PROXY_COMMAND
        ini:
          - section: paramiko_connection
            key: proxy_command
        vars:
          - name: ansible_paramiko_proxy_command
      ssh_args:
        description: Only used in parsing ProxyCommand for use in this plugin.
        default: ""
        type: string
        ini:
          - section: "ssh_connection"
            key: "ssh_args"
        env:
          - name: ANSIBLE_SSH_ARGS
        vars:
          - name: ansible_ssh_args
        deprecated:
          why: In favor of the "proxy_command" option.
          version: "0.1.0"
          alternatives: proxy_command
      ssh_common_args:
        description: Only used in parsing ProxyCommand for use in this plugin.
        type: string
        ini:
          - section: "ssh_connection"
            key: "ssh_common_args"
        env:
          - name: ANSIBLE_SSH_COMMON_ARGS
        vars:
          - name: ansible_ssh_common_args
        cli:
          - name: ssh_common_args
        default: ""
        deprecated:
          why: In favor of the "proxy_command" option.
          version: "0.1.0"
          alternatives: proxy_command
      ssh_extra_args:
        description: Only used in parsing ProxyCommand for use in this plugin.
        type: string
        vars:
          - name: ansible_ssh_extra_args
        env:
          - name: ANSIBLE_SSH_EXTRA_ARGS
        ini:
          - key: ssh_extra_args
            section: ssh_connection
        cli:
          - name: ssh_extra_args
        default: ""
        deprecated:
          why: In favor of the "proxy_command" option.
          version: "0.1.0"
          alternatives: proxy_command
      pty:
        default: True
        description: "SUDO usually requires a PTY, True to give a PTY and False to not give a PTY."
        env:
          - name: ANSIBLE_PARAMIKO_PTY
        ini:
          - key: pty
            section: paramiko_connection
        type: boolean
      record_host_keys:
        default: True
        description: "Save the host keys to a file"
        env:
          - name: ANSIBLE_PARAMIKO_RECORD_HOST_KEYS
        ini:
          - section: paramiko_connection
            key: record_host_keys
        type: boolean
      host_key_checking:
        description: "Set this to V(False) if you want to avoid host key checking by the underlying tools Ansible uses to connect to the host."
        type: boolean
        default: True
        env:
          - name: ANSIBLE_HOST_KEY_CHECKING
          - name: ANSIBLE_SSH_HOST_KEY_CHECKING
          - name: ANSIBLE_PARAMIKO_HOST_KEY_CHECKING
        ini:
          - section: defaults
            key: host_key_checking
          - section: paramiko_connection
            key: host_key_checking
        vars:
          - name: ansible_host_key_checking
          - name: ansible_ssh_host_key_checking
          - name: ansible_paramiko_host_key_checking
      use_persistent_connections:
        description: "Toggles the use of persistence for connections"
        type: boolean
        default: False
        env:
          - name: ANSIBLE_USE_PERSISTENT_CONNECTIONS
        ini:
          - section: defaults
            key: use_persistent_connections
      banner_timeout:
        type: float
        default: 30
        description:
          - Configures, in seconds, the amount of time to wait for the SSH
            banner to be presented. This option is supported by paramiko
            version 1.15.0 or newer.
        ini:
          - section: paramiko_connection
            key: banner_timeout
        env:
          - name: ANSIBLE_PARAMIKO_BANNER_TIMEOUT
      timeout:
        type: int
        default: 10
        description: Number of seconds until the plugin gives up on failing to establish a TCP connection.
        ini:
          - section: defaults
            key: timeout
          - section: ssh_connection
            key: timeout
          - section: paramiko_connection
            key: timeout
        env:
          - name: ANSIBLE_TIMEOUT
          - name: ANSIBLE_SSH_TIMEOUT
          - name: ANSIBLE_PARAMIKO_TIMEOUT
        vars:
          - name: ansible_ssh_timeout
          - name: ansible_paramiko_timeout
        cli:
          - name: timeout
      private_key_file:
        description:
          - Path to private key file to use for authentication.
        type: string
        ini:
          - section: defaults
            key: private_key_file
          - section: paramiko_connection
            key: private_key_file
        env:
          - name: ANSIBLE_PRIVATE_KEY_FILE
          - name: ANSIBLE_PARAMIKO_PRIVATE_KEY_FILE
        vars:
          - name: ansible_private_key_file
          - name: ansible_ssh_private_key_file
          - name: ansible_paramiko_private_key_file
        cli:
          - name: private_key_file
            option: "--private-key"
      vmid:
        description:
          - Container ID
        default: proxmox_vmid
        vars:
          - name: proxmox_vmid
    notes:
      - When NOT using this plugin as root, you need to have sudo installed on proxmox and setup so we can run it without prompting for the password.
"""

EXAMPLES = r"""
# --------------------------------------------------------------
# Setup sudo with passwordless access to pct for user 'ansible':
# --------------------------------------------------------------
# $ echo 'ansible ALL = (root) NOPASSWD: /usr/sbin/pct' > /etc/sudoers.d/ansible_pct
#
#
# --------------------------------
# Static inventory file: hosts.yml
# --------------------------------
# all:
#   children:
#     lxc:
#       hosts:
#         container-1:
#           ansible_host: 10.0.0.10
#           proxmox_vmid: 100
#           ansible_connection: community.general.pct_remote
#           remote_user: ansible
#         container-2:
#           ansible_host: 10.0.0.10
#           proxmox_vmid: 200
#           ansible_connection: community.general.pct_remote
#           remote_user: ansible
#     proxmox:
#       hosts:
#         proxmox-1:
#           ansible_host: 10.0.0.10
#
#
# ---------------------------------------------
# Dynamic inventory file: inventory.proxmox.yml
# ---------------------------------------------
# plugin: community.general.proxmox
# url: https://10.0.0.10:8006
# validate_certs: false
# user: ansible@pam
# token_id: ansible
# token_secret: !vault |
#           $ANSIBLE_VAULT;1.1;AES256
#           ...

# want_facts: true
# exclude_nodes: true
# filters:
#   - proxmox_vmtype == "lxc"
# want_proxmox_nodes_ansible_host: false
# compose:
#   ansible_host: "'10.0.0.10'"
#   ansible_connection: "'community.general.pct_remote'"
#   remote_user: "'ansible'"
#
#
# ----------------------
# Playbook: playbook.yml
# ----------------------
---
- hosts: lxc
  tasks:
    - debug:
        msg: "This is coming from pct environment"
"""

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.plugins.connection.paramiko_ssh import Connection as SSH_Connection
from ansible.utils.display import Display
import uuid
import os


display = Display()


def become_command():
    """Helper function to get become_command """
    return os.getenv('ANSIBLE_BECOME_METHOD', default=C.DEFAULT_BECOME_METHOD)


class Connection(SSH_Connection):
    ''' SSH based connections (paramiko) to Proxmox pct '''
    transport = 'community.general.pct_remote'

    def exec_command(self, cmd: str, in_data: bytes | None = None, sudoable: bool = True) -> tuple[int, bytes, bytes]:
        ''' execute a command inside the proxmox container '''
        cmd = ['/usr/sbin/pct', 'exec',
               self.get_option('vmid'), '--', cmd]
        if self.get_option('remote_user') != 'root':
            cmd = [become_command()] + cmd
        return super().exec_command(' '.join(cmd), in_data=in_data, sudoable=sudoable)

    def put_file(self, in_path: str, out_path: str) -> None:
        ''' transfer a file from local to remote '''
        temp_dir = '/tmp/ansible_pct_' + str(uuid.uuid4()).replace('-', '')[:6]
        temp_file_path = f'{temp_dir}/{os.path.basename(in_path)}'
        try:
            super().exec_command(f'mkdir -p {temp_dir}')
            super().put_file(in_path, temp_file_path)
            cmd = ['/usr/sbin/pct', 'push',
                   self.get_option('vmid'), temp_file_path, out_path]
            if self.get_option('remote_user') != 'root':
                cmd = [become_command()] + cmd
            super().exec_command(' '.join(cmd))
        except Exception as e:
            raise AnsibleError(
                'failed to transfer file to %s!\n%s' % (out_path, e))
        finally:
            super().exec_command(f'rm -rf {temp_dir}')

    def fetch_file(self, in_path: str, out_path: str) -> None:
        ''' save a remote file to the specified path '''
        temp_dir = '/tmp/ansible_pct_' + str(uuid.uuid4()).replace('-', '')[:6]
        temp_file_path = f'{temp_dir}/{os.path.basename(in_path)}'
        try:
            super().exec_command(f'mkdir -p {temp_dir}')
            cmd = ['/usr/sbin/pct', 'pull',
                   self.get_option('vmid'), in_path, temp_file_path]
            if self.get_option('remote_user') != 'root':
                cmd = [become_command()] + cmd
            super().exec_command(' '.join(cmd))
            super().fetch_file(temp_file_path, out_path)
        except Exception as e:
            raise AnsibleError(
                'failed to transfer file from %s!\n%s' % (in_path, e))
        finally:
            super().exec_command(f'rm -rf {temp_dir}')
