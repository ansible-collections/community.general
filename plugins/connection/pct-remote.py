# -*- coding: utf-8 -*-
# Based on paramiko_ssh.py (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (annotations, absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    author: Nils Stein (@mietzen) <github.nstein@mailbox.org>
    name: pct-remote
    short_description: Run tasks in Proxmox LXC container instances via pct CLI
    description:
        - Run commands or put/fetch files to an existing Proxmox LXC container instance using pct CLI.
        - Use the Python SSH implementation (Paramiko) to connect to targets
        - The paramiko transport is provided because many distributions, in particular EL6 and before do not support ControlPersist
          in their SSH implementations.
        - This is needed on the Ansible control machine to be reasonably efficient with connections.
          Thus paramiko is faster for most users on these platforms.
          Users with ControlPersist capability can consider using -c ssh or configuring the transport in the configuration file.
        - This plugin also borrows a lot of settings from the ssh plugin as they both cover the same protocol.
    version_added: "0.1"
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
              version_added: '2.15'
          env:
            - name: ANSIBLE_REMOTE_PORT
            - name: ANSIBLE_REMOTE_PARAMIKO_PORT
              version_added: '2.15'
          vars:
            - name: ansible_port
            - name: ansible_ssh_port
            - name: ansible_paramiko_port
              version_added: '2.15'
          keyword:
            - name: port
      remote_user:
        description:
            - User to login/authenticate as
            - Can be set from the CLI via the C(--user) or C(-u) options.
        type: string
        vars:
            - name: ansible_user
            - name: ansible_ssh_user
            - name: ansible_paramiko_user
        env:
            - name: ANSIBLE_REMOTE_USER
            - name: ANSIBLE_PARAMIKO_REMOTE_USER
              version_added: '2.5'
        ini:
            - section: defaults
              key: remote_user
            - section: paramiko_connection
              key: remote_user
              version_added: '2.5'
        keyword:
            - name: remote_user
      password:
        description:
          - Secret used to either login the ssh server or as a passphrase for ssh keys that require it
          - Can be set from the CLI via the C(--ask-pass) option.
        type: string
        vars:
            - name: ansible_password
            - name: ansible_ssh_pass
            - name: ansible_ssh_password
            - name: ansible_paramiko_pass
            - name: ansible_paramiko_password
              version_added: '2.5'
      use_rsa_sha2_algorithms:
        description:
            - Whether or not to enable RSA SHA2 algorithms for pubkeys and hostkeys
            - On paramiko versions older than 2.9, this only affects hostkeys
            - For behavior matching paramiko<2.9 set this to V(False)
        vars:
            - name: ansible_paramiko_use_rsa_sha2_algorithms
        ini:
            - {key: use_rsa_sha2_algorithms, section: paramiko_connection}
        env:
            - {name: ANSIBLE_PARAMIKO_USE_RSA_SHA2_ALGORITHMS}
        default: True
        type: boolean
        version_added: '2.14'
      host_key_auto_add:
        description: 'Automatically add host keys'
        env: [{name: ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD}]
        ini:
          - {key: host_key_auto_add, section: paramiko_connection}
        type: boolean
      look_for_keys:
        default: True
        description: 'False to disable searching for private key files in ~/.ssh/'
        env: [{name: ANSIBLE_PARAMIKO_LOOK_FOR_KEYS}]
        ini:
        - {key: look_for_keys, section: paramiko_connection}
        type: boolean
      proxy_command:
        default: ''
        description:
            - Proxy information for running the connection via a jumphost
            - Also this plugin will scan 'ssh_args', 'ssh_extra_args' and 'ssh_common_args' from the 'ssh' plugin settings for proxy information if set.
        type: string
        env: [{name: ANSIBLE_PARAMIKO_PROXY_COMMAND}]
        ini:
          - {key: proxy_command, section: paramiko_connection}
        vars:
          - name: ansible_paramiko_proxy_command
            version_added: '2.15'
      ssh_args:
          description: Only used in parsing ProxyCommand for use in this plugin.
          default: ''
          type: string
          ini:
              - section: 'ssh_connection'
                key: 'ssh_args'
          env:
              - name: ANSIBLE_SSH_ARGS
          vars:
              - name: ansible_ssh_args
                version_added: '2.7'
          deprecated:
              why: In favor of the "proxy_command" option.
              version: "2.18"
              alternatives: proxy_command
      ssh_common_args:
          description: Only used in parsing ProxyCommand for use in this plugin.
          type: string
          ini:
              - section: 'ssh_connection'
                key: 'ssh_common_args'
                version_added: '2.7'
          env:
              - name: ANSIBLE_SSH_COMMON_ARGS
                version_added: '2.7'
          vars:
              - name: ansible_ssh_common_args
          cli:
              - name: ssh_common_args
          default: ''
          deprecated:
              why: In favor of the "proxy_command" option.
              version: "2.18"
              alternatives: proxy_command
      ssh_extra_args:
          description: Only used in parsing ProxyCommand for use in this plugin.
          type: string
          vars:
              - name: ansible_ssh_extra_args
          env:
            - name: ANSIBLE_SSH_EXTRA_ARGS
              version_added: '2.7'
          ini:
            - key: ssh_extra_args
              section: ssh_connection
              version_added: '2.7'
          cli:
            - name: ssh_extra_args
          default: ''
          deprecated:
              why: In favor of the "proxy_command" option.
              version: "2.18"
              alternatives: proxy_command
      pty:
        default: True
        description: 'SUDO usually requires a PTY, True to give a PTY and False to not give a PTY.'
        env:
          - name: ANSIBLE_PARAMIKO_PTY
        ini:
          - section: paramiko_connection
            key: pty
        type: boolean
      record_host_keys:
        default: True
        description: 'Save the host keys to a file'
        env: [{name: ANSIBLE_PARAMIKO_RECORD_HOST_KEYS}]
        ini:
          - section: paramiko_connection
            key: record_host_keys
        type: boolean
      host_key_checking:
        description: 'Set this to "False" if you want to avoid host key checking by the underlying tools Ansible uses to connect to the host'
        type: boolean
        default: True
        env:
          - name: ANSIBLE_HOST_KEY_CHECKING
          - name: ANSIBLE_SSH_HOST_KEY_CHECKING
            version_added: '2.5'
          - name: ANSIBLE_PARAMIKO_HOST_KEY_CHECKING
            version_added: '2.5'
        ini:
          - section: defaults
            key: host_key_checking
          - section: paramiko_connection
            key: host_key_checking
            version_added: '2.5'
        vars:
          - name: ansible_host_key_checking
            version_added: '2.5'
          - name: ansible_ssh_host_key_checking
            version_added: '2.5'
          - name: ansible_paramiko_host_key_checking
            version_added: '2.5'
      use_persistent_connections:
        description: 'Toggles the use of persistence for connections'
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
        version_added: '2.14'
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
            version_added: '2.11'
          - section: paramiko_connection
            key: timeout
            version_added: '2.15'
        env:
          - name: ANSIBLE_TIMEOUT
          - name: ANSIBLE_SSH_TIMEOUT
            version_added: '2.11'
          - name: ANSIBLE_PARAMIKO_TIMEOUT
            version_added: '2.15'
        vars:
          - name: ansible_ssh_timeout
            version_added: '2.11'
          - name: ansible_paramiko_timeout
            version_added: '2.15'
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
              version_added: '2.15'
          env:
            - name: ANSIBLE_PRIVATE_KEY_FILE
            - name: ANSIBLE_PARAMIKO_PRIVATE_KEY_FILE
              version_added: '2.15'
          vars:
            - name: ansible_private_key_file
            - name: ansible_ssh_private_key_file
            - name: ansible_paramiko_private_key_file
              version_added: '2.15'
          cli:
            - name: private_key_file
              option: '--private-key'
      vmid:
        description:
            - Container ID
        default: proxmox_vmid
        vars:
            - name: proxmox_vmid
"""

import uuid
import os
from ansible.errors import AnsibleError
from ansible.module_utils.common.process import get_bin_path
from ansible.plugins.connection.paramiko_ssh import Connection as SSH_Connection
from ansible.utils.display import Display


display = Display()

class Connection(SSH_Connection):
    ''' SSH based connections (paramiko) to Proxmox pct '''
    transport = 'community.general.pct-remote'

    def __init__(self):
        try:
            self._pct_cmd = get_bin_path("pct")
        except ValueError:
            raise AnsibleError("pct command not found in PATH")
        try:
            self._pvesh_cmd = get_bin_path("pvesh")
        except ValueError:
            raise AnsibleError("pvesh command not found in PATH")

    def exec_command(self, cmd: str, in_data: bytes | None = None, sudoable: bool = True) -> tuple[int, bytes, bytes]:
        ''' execute a command inside the proxmox container '''
        cmd = ' '.join([self._pct_cmd, "exec", self.get_option('vmid'), "--", cmd])
        return super().exec_command(cmd, in_data=in_data, sudoable=sudoable)

    def put_file(self, in_path: str, out_path: str) -> None:
        ''' transfer a file from local to remote '''
        temp_dir = f'/tmp/ansible_pct_{str(uuid.uuid4()).replace('-', '')[:6]}'
        temp_file_path = f'{temp_dir}/{os.path.basename(in_path)}'
        try:
            super().exec_command(f'mkdir -p {temp_dir}')
            super().put_file(in_path, temp_dir)
            super().exec_command(f'{self._pct_cmd} push {self.get_option('vmid')} {temp_file_path} {out_path}')
        except Exception as e:
            raise AnsibleError("failed to transfer file to %s!\n%s" % out_path, e)
        finally:
            super().exec_command(f'rm -rf {temp_dir}')

    def fetch_file(self, in_path: str, out_path: str) -> None:
        ''' save a remote file to the specified path '''
        temp_dir = f'/tmp/ansible_pct_{str(uuid.uuid4()).replace('-', '')[:6]}'
        temp_file_path = f'{temp_dir}/{os.path.basename(in_path)}'
        try:
            super().exec_command(f'mkdir -p {temp_dir}')
            super().exec_command(f'{self._pct_cmd} pull {self.get_option('vmid')} {in_path} {temp_dir}')
            super().fetch_file(temp_file_path, out_path)
        except Exception as e:
            raise AnsibleError("failed to transfer file from %s!\n%s" % in_path, e)
        finally:
            super().exec_command(f'rm -rf {temp_dir}')