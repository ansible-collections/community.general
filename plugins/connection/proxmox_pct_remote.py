# -*- coding: utf-8 -*-
# Derived from ansible/plugins/connection/paramiko_ssh.py (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Nils Stein (@mietzen) <github.nstein@mailbox.org>
name: proxmox_pct_remote
short_description: Run tasks in Proxmox LXC container instances using pct CLI via SSH
requirements:
  - paramiko
description:
  - Run commands or put/fetch files to an existing Proxmox LXC container using pct CLI via SSH.
  - Uses the Python SSH implementation (Paramiko) to connect to the Proxmox host.
version_added: "10.3.0"
options:
  remote_addr:
    description:
      - Address of the remote target.
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
      - Can be set from the CLI via the C(--user) or C(-u) options.
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
      - Secret used to either login the SSH server or as a passphrase for SSH keys that require it.
      - Can be set from the CLI via the C(--ask-pass) option.
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
      - For behavior matching paramiko<2.9 set this to V(false).
    vars:
      - name: ansible_paramiko_use_rsa_sha2_algorithms
    ini:
      - {key: use_rsa_sha2_algorithms, section: paramiko_connection}
    env:
      - {name: ANSIBLE_PARAMIKO_USE_RSA_SHA2_ALGORITHMS}
    default: true
    type: boolean
  host_key_auto_add:
    description: "Automatically add host keys to C(~/.ssh/known_hosts)."
    env:
      - name: ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD
    ini:
      - key: host_key_auto_add
        section: paramiko_connection
    type: boolean
  look_for_keys:
    default: True
    description: "Set to V(false) to disable searching for private key files in C(~/.ssh/)."
    env:
      - name: ANSIBLE_PARAMIKO_LOOK_FOR_KEYS
    ini:
      - {key: look_for_keys, section: paramiko_connection}
    type: boolean
  proxy_command:
    default: ""
    description:
      - Proxy information for running the connection via a jumphost.
    type: string
    env:
      - name: ANSIBLE_PARAMIKO_PROXY_COMMAND
    ini:
      - {key: proxy_command, section: paramiko_connection}
    vars:
      - name: ansible_paramiko_proxy_command
  pty:
    default: True
    description: "C(sudo) usually requires a PTY, V(true) to give a PTY and V(false) to not give a PTY."
    env:
      - name: ANSIBLE_PARAMIKO_PTY
    ini:
      - section: paramiko_connection
        key: pty
    type: boolean
  record_host_keys:
    default: True
    description: "Save the host keys to a file."
    env:
      - name: ANSIBLE_PARAMIKO_RECORD_HOST_KEYS
    ini:
      - section: paramiko_connection
        key: record_host_keys
    type: boolean
  host_key_checking:
    description: "Set this to V(false) if you want to avoid host key checking by the underlying tools Ansible uses to connect to the host."
    type: boolean
    default: true
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
    description: "Toggles the use of persistence for connections."
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
  lock_file_timeout:
    type: int
    default: 60
    description: Number of seconds until the plugin gives up on trying to write a lock file when writing SSH known host keys.
    vars:
      - name: ansible_lock_file_timeout
    env:
      - name: ANSIBLE_LOCK_FILE_TIMEOUT
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
      - LXC Container ID
    type: int
    vars:
      - name: proxmox_vmid
  proxmox_become_method:
    description:
      - Become command used in proxmox
    type: str
    default: sudo
    vars:
      - name: proxmox_become_method
notes:
  - >
    When NOT using this plugin as root, you need to have a become mechanism,
    e.g. C(sudo), installed on Proxmox and setup so we can run it without prompting for the password.
    Inside the container, we need a shell, for example C(sh) and the C(cat) command to be available in the C(PATH) for this plugin to work.
"""

EXAMPLES = r"""
# --------------------------------------------------------------
# Setup sudo with password less access to pct for user 'ansible':
# --------------------------------------------------------------
#
# Open a Proxmox root shell and execute:
# $ useradd -d /opt/ansible-pct -r -m -s /bin/sh ansible
# $ mkdir -p /opt/ansible-pct/.ssh
# $ ssh-keygen -t ed25519 -C 'ansible' -N "" -f /opt/ansible-pct/.ssh/ansible <<< y > /dev/null
# $ cat /opt/ansible-pct/.ssh/ansible
# $ mv /opt/ansible-pct/.ssh/ansible.pub /opt/ansible-pct/.ssh/authorized-keys
# $ rm /opt/ansible-pct/.ssh/ansible*
# $ chown -R ansible:ansible /opt/ansible-pct/.ssh
# $ chmod 700 /opt/ansible-pct/.ssh
# $ chmod 600 /opt/ansible-pct/.ssh/authorized-keys
# $ echo 'ansible ALL = (root) NOPASSWD: /usr/sbin/pct' > /etc/sudoers.d/ansible_pct
#
# Save the displayed private key and add it to your ssh-agent
#
# Or use ansible:
# ---
# - name: Setup ansible-pct user and configure environment on Proxmox host
#   hosts: proxmox
#   become: true
#   gather_facts: false
#
#   tasks:
#     - name: Create ansible user
#       ansible.builtin.user:
#         name: ansible
#         comment: Ansible User
#         home: /opt/ansible-pct
#         shell: /bin/sh
#         create_home: true
#         system: true
#
#     - name: Create .ssh directory
#       ansible.builtin.file:
#         path: /opt/ansible-pct/.ssh
#         state: directory
#         owner: ansible
#         group: ansible
#         mode: '0700'
#
#     - name: Generate SSH key for ansible user
#       community.crypto.openssh_keypair:
#         path: /opt/ansible-pct/.ssh/ansible
#         type: ed25519
#         comment: 'ansible'
#         force: true
#         mode: '0600'
#         owner: ansible
#         group: ansible
#
#     - name: Set public key as authorized key
#       ansible.builtin.copy:
#         src: /opt/ansible-pct/.ssh/ansible.pub
#         dest: /opt/ansible-pct/.ssh/authorized-keys
#         remote_src: yes
#         owner: ansible
#         group: ansible
#         mode: '0600'
#
#     - name: Add sudoers entry for ansible user
#       ansible.builtin.copy:
#         content: 'ansible ALL = (root) NOPASSWD: /usr/sbin/pct'
#         dest: /etc/sudoers.d/ansible_pct
#         owner: root
#         group: root
#         mode: '0440'
#
#     - name: Fetch private SSH key to localhost
#       ansible.builtin.fetch:
#         src: /opt/ansible-pct/.ssh/ansible
#         dest: ~/.ssh/proxmox_ansible_private_key
#         flat: yes
#         fail_on_missing: true
#
#     - name: Clean up generated SSH keys
#       ansible.builtin.file:
#         path: /opt/ansible-pct/.ssh/ansible*
#         state: absent
#
# - name: Configure private key permissions on localhost
#   hosts: localhost
#   tasks:
#     - name: Set permissions for fetched private key
#       ansible.builtin.file:
#         path: ~/.ssh/proxmox_ansible_private_key
#         mode: '0600'
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
#           ansible_connection: community.general.proxmox_pct_remote
#           ansible_user: ansible
#         container-2:
#           ansible_host: 10.0.0.10
#           proxmox_vmid: 200
#           ansible_connection: community.general.proxmox_pct_remote
#           ansible_user: ansible
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
#   ansible_connection: "'community.general.proxmox_pct_remote'"
#   ansible_user: "'ansible'"
#
#
# ----------------------
# Playbook: playbook.yml
# ----------------------
---
- hosts: lxc
  # On nodes with many containers you might want to deactivate the devices facts
  # or set `gather_facts: false` if you don't need them.
  # More info on gathering fact subsets:
  # https://docs.ansible.com/ansible/latest/collections/ansible/builtin/setup_module.html
  #
  # gather_facts: true
  #   gather_subset:
  #     - "!devices"
  tasks:
    - name: Ping LXC container
      ansible.builtin.ping:
"""

import os
import pathlib
import socket
import tempfile
import traceback
import typing as t

from ansible.errors import (
    AnsibleAuthenticationFailure,
    AnsibleConnectionFailure,
    AnsibleError,
)
from ansible_collections.community.general.plugins.module_utils._filelock import FileLock, LockTimeout
from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.plugins.connection import ConnectionBase
from ansible.utils.display import Display
from ansible.utils.path import makedirs_safe
from binascii import hexlify

try:
    import paramiko
    PARAMIKO_IMPORT_ERR = None
except ImportError:
    paramiko = None
    PARAMIKO_IMPORT_ERR = traceback.format_exc()


display = Display()


def authenticity_msg(hostname: str, ktype: str, fingerprint: str) -> str:
    msg = f"""
    paramiko: The authenticity of host '{hostname}' can't be established.
    The {ktype} key fingerprint is {fingerprint}.
    Are you sure you want to continue connecting (yes/no)?
    """
    return msg


MissingHostKeyPolicy: type = object
if paramiko:
    MissingHostKeyPolicy = paramiko.MissingHostKeyPolicy


class MyAddPolicy(MissingHostKeyPolicy):
    """
    Based on AutoAddPolicy in paramiko so we can determine when keys are added

    and also prompt for input.

    Policy for automatically adding the hostname and new host key to the
    local L{HostKeys} object, and saving it. This is used by L{SSHClient}.
    """

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self._options = connection._options

    def missing_host_key(self, client, hostname, key) -> None:

        if all((self.connection.get_option('host_key_checking'), not self.connection.get_option('host_key_auto_add'))):

            fingerprint = hexlify(key.get_fingerprint())
            ktype = key.get_name()

            if self.connection.get_option('use_persistent_connections') or self.connection.force_persistence:
                # don't print the prompt string since the user cannot respond
                # to the question anyway
                raise AnsibleError(authenticity_msg(hostname, ktype, fingerprint)[1:92])

            inp = to_text(
                display.prompt_until(authenticity_msg(hostname, ktype, fingerprint), private=False),
                errors='surrogate_or_strict'
            )

            if inp.lower() not in ['yes', 'y', '']:
                raise AnsibleError('host connection rejected by user')

        key._added_by_ansible_this_time = True

        # existing implementation below:
        client._host_keys.add(hostname, key.get_name(), key)

        # host keys are actually saved in close() function below
        # in order to control ordering.


class Connection(ConnectionBase):
    """ SSH based connections (paramiko) to Proxmox pct """

    transport = 'community.general.proxmox_pct_remote'
    _log_channel: str | None = None

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

    def _set_log_channel(self, name: str) -> None:
        """ Mimic paramiko.SSHClient.set_log_channel """
        self._log_channel = name

    def _parse_proxy_command(self, port: int = 22) -> dict[str, t.Any]:
        proxy_command = self.get_option('proxy_command') or None

        sock_kwarg = {}
        if proxy_command:
            replacers = {
                '%h': self.get_option('remote_addr'),
                '%p': port,
                '%r': self.get_option('remote_user')
            }
            for find, replace in replacers.items():
                proxy_command = proxy_command.replace(find, str(replace))
            try:
                sock_kwarg = {'sock': paramiko.ProxyCommand(proxy_command)}
                display.vvv(f'CONFIGURE PROXY COMMAND FOR CONNECTION: {proxy_command}', host=self.get_option('remote_addr'))
            except AttributeError:
                display.warning('Paramiko ProxyCommand support unavailable. '
                                'Please upgrade to Paramiko 1.9.0 or newer. '
                                'Not using configured ProxyCommand')

        return sock_kwarg

    def _connect(self) -> Connection:
        """ activates the connection object """

        if PARAMIKO_IMPORT_ERR is not None:
            raise AnsibleError(f'paramiko is not installed: {to_native(PARAMIKO_IMPORT_ERR)}')

        port = self.get_option('port')
        display.vvv(f'ESTABLISH PARAMIKO SSH CONNECTION FOR USER: {self.get_option("remote_user")} on PORT {to_text(port)} TO {self.get_option("remote_addr")}',
                    host=self.get_option('remote_addr'))

        ssh = paramiko.SSHClient()

        # Set pubkey and hostkey algorithms to disable, the only manipulation allowed currently
        # is keeping or omitting rsa-sha2 algorithms
        # default_keys: t.Tuple[str] = ()
        paramiko_preferred_pubkeys = getattr(paramiko.Transport, '_preferred_pubkeys', ())
        paramiko_preferred_hostkeys = getattr(paramiko.Transport, '_preferred_keys', ())
        use_rsa_sha2_algorithms = self.get_option('use_rsa_sha2_algorithms')
        disabled_algorithms: t.Dict[str, t.Iterable[str]] = {}
        if not use_rsa_sha2_algorithms:
            if paramiko_preferred_pubkeys:
                disabled_algorithms['pubkeys'] = tuple(a for a in paramiko_preferred_pubkeys if 'rsa-sha2' in a)
            if paramiko_preferred_hostkeys:
                disabled_algorithms['keys'] = tuple(a for a in paramiko_preferred_hostkeys if 'rsa-sha2' in a)

        # override paramiko's default logger name
        if self._log_channel is not None:
            ssh.set_log_channel(self._log_channel)

        self.keyfile = os.path.expanduser('~/.ssh/known_hosts')

        if self.get_option('host_key_checking'):
            for ssh_known_hosts in ('/etc/ssh/ssh_known_hosts', '/etc/openssh/ssh_known_hosts'):
                try:
                    ssh.load_system_host_keys(ssh_known_hosts)
                    break
                except IOError:
                    pass  # file was not found, but not required to function
                except paramiko.hostkeys.InvalidHostKey as e:
                    raise AnsibleConnectionFailure(f'Invalid host key: {to_text(e.line)}')
            try:
                ssh.load_system_host_keys()
            except paramiko.hostkeys.InvalidHostKey as e:
                raise AnsibleConnectionFailure(f'Invalid host key: {to_text(e.line)}')

        ssh_connect_kwargs = self._parse_proxy_command(port)
        ssh.set_missing_host_key_policy(MyAddPolicy(self))
        conn_password = self.get_option('password')
        allow_agent = True

        if conn_password is not None:
            allow_agent = False

        try:
            key_filename = None
            if self.get_option('private_key_file'):
                key_filename = os.path.expanduser(self.get_option('private_key_file'))

            # paramiko 2.2 introduced auth_timeout parameter
            if LooseVersion(paramiko.__version__) >= LooseVersion('2.2.0'):
                ssh_connect_kwargs['auth_timeout'] = self.get_option('timeout')

            # paramiko 1.15 introduced banner timeout parameter
            if LooseVersion(paramiko.__version__) >= LooseVersion('1.15.0'):
                ssh_connect_kwargs['banner_timeout'] = self.get_option('banner_timeout')

            ssh.connect(
                self.get_option('remote_addr').lower(),
                username=self.get_option('remote_user'),
                allow_agent=allow_agent,
                look_for_keys=self.get_option('look_for_keys'),
                key_filename=key_filename,
                password=conn_password,
                timeout=self.get_option('timeout'),
                port=port,
                disabled_algorithms=disabled_algorithms,
                **ssh_connect_kwargs,
            )
        except paramiko.ssh_exception.BadHostKeyException as e:
            raise AnsibleConnectionFailure(f'host key mismatch for {to_text(e.hostname)}')
        except paramiko.ssh_exception.AuthenticationException as e:
            msg = f'Failed to authenticate: {e}'
            raise AnsibleAuthenticationFailure(msg)
        except Exception as e:
            msg = to_text(e)
            if u'PID check failed' in msg:
                raise AnsibleError('paramiko version issue, please upgrade paramiko on the machine running ansible')
            elif u'Private key file is encrypted' in msg:
                msg = f'ssh {self.get_option("remote_user")}@{self.get_options("remote_addr")}:{port} : ' + \
                    f'{msg}\nTo connect as a different user, use -u <username>.'
                raise AnsibleConnectionFailure(msg)
            else:
                raise AnsibleConnectionFailure(msg)
        self.ssh = ssh
        self._connected = True
        return self

    def _any_keys_added(self) -> bool:
        for hostname, keys in self.ssh._host_keys.items():
            for keytype, key in keys.items():
                added_this_time = getattr(key, '_added_by_ansible_this_time', False)
                if added_this_time:
                    return True
        return False

    def _save_ssh_host_keys(self, filename: str) -> None:
        """
        not using the paramiko save_ssh_host_keys function as we want to add new SSH keys at the bottom so folks
        don't complain about it :)
        """

        if not self._any_keys_added():
            return

        path = os.path.expanduser('~/.ssh')
        makedirs_safe(path)

        with open(filename, 'w') as f:
            for hostname, keys in self.ssh._host_keys.items():
                for keytype, key in keys.items():
                    # was f.write
                    added_this_time = getattr(key, '_added_by_ansible_this_time', False)
                    if not added_this_time:
                        f.write(f'{hostname} {keytype} {key.get_base64()}\n')

            for hostname, keys in self.ssh._host_keys.items():
                for keytype, key in keys.items():
                    added_this_time = getattr(key, '_added_by_ansible_this_time', False)
                    if added_this_time:
                        f.write(f'{hostname} {keytype} {key.get_base64()}\n')

    def _build_pct_command(self, cmd: str) -> str:
        cmd = ['/usr/sbin/pct', 'exec', str(self.get_option('vmid')), '--', cmd]
        if self.get_option('remote_user') != 'root':
            cmd = [self.get_option('proxmox_become_method')] + cmd
            display.vvv(f'INFO Running as non root user: {self.get_option("remote_user")}, trying to run pct with become method: ' +
                        f'{self.get_option("proxmox_become_method")}',
                        host=self.get_option('remote_addr'))
        return ' '.join(cmd)

    def exec_command(self, cmd: str, in_data: bytes | None = None, sudoable: bool = True) -> tuple[int, bytes, bytes]:
        """ run a command on inside the LXC container """

        cmd = self._build_pct_command(cmd)

        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        bufsize = 4096

        try:
            self.ssh.get_transport().set_keepalive(5)
            chan = self.ssh.get_transport().open_session()
        except Exception as e:
            text_e = to_text(e)
            msg = 'Failed to open session'
            if text_e:
                msg += f': {text_e}'
            raise AnsibleConnectionFailure(to_native(msg))

        # sudo usually requires a PTY (cf. requiretty option), therefore
        # we give it one by default (pty=True in ansible.cfg), and we try
        # to initialise from the calling environment when sudoable is enabled
        if self.get_option('pty') and sudoable:
            chan.get_pty(term=os.getenv('TERM', 'vt100'), width=int(os.getenv('COLUMNS', 0)), height=int(os.getenv('LINES', 0)))

        display.vvv(f'EXEC {cmd}', host=self.get_option('remote_addr'))

        cmd = to_bytes(cmd, errors='surrogate_or_strict')

        no_prompt_out = b''
        no_prompt_err = b''
        become_output = b''

        try:
            chan.exec_command(cmd)
            if self.become and self.become.expect_prompt():
                password_prompt = False
                become_success = False
                while not (become_success or password_prompt):
                    display.debug('Waiting for Privilege Escalation input')

                    chunk = chan.recv(bufsize)
                    display.debug(f'chunk is: {to_text(chunk)}')
                    if not chunk:
                        if b'unknown user' in become_output:
                            n_become_user = to_native(self.become.get_option('become_user'))
                            raise AnsibleError(f'user {n_become_user} does not exist')
                        else:
                            break
                            # raise AnsibleError('ssh connection closed waiting for password prompt')
                    become_output += chunk

                    # need to check every line because we might get lectured
                    # and we might get the middle of a line in a chunk
                    for line in become_output.splitlines(True):
                        if self.become.check_success(line):
                            become_success = True
                            break
                        elif self.become.check_password_prompt(line):
                            password_prompt = True
                            break

                if password_prompt:
                    if self.become:
                        become_pass = self.become.get_option('become_pass')
                        chan.sendall(to_bytes(become_pass, errors='surrogate_or_strict') + b'\n')
                    else:
                        raise AnsibleError('A password is required but none was supplied')
                else:
                    no_prompt_out += become_output
                    no_prompt_err += become_output

            if in_data:
                for i in range(0, len(in_data), bufsize):
                    chan.send(in_data[i:i + bufsize])
                chan.shutdown_write()
            elif in_data == b'':
                chan.shutdown_write()

        except socket.timeout:
            raise AnsibleError('ssh timed out waiting for privilege escalation.\n' + to_text(become_output))

        stdout = b''.join(chan.makefile('rb', bufsize))
        stderr = b''.join(chan.makefile_stderr('rb', bufsize))
        returncode = chan.recv_exit_status()

        if 'pct: not found' in stderr.decode('utf-8'):
            raise AnsibleError(
                f'pct not found in path of host: {to_text(self.get_option("remote_addr"))}')

        return (returncode, no_prompt_out + stdout, no_prompt_out + stderr)

    def put_file(self, in_path: str, out_path: str) -> None:
        """ transfer a file from local to remote """

        display.vvv(f'PUT {in_path} TO {out_path}', host=self.get_option('remote_addr'))
        try:
            with open(in_path, 'rb') as f:
                data = f.read()
                returncode, stdout, stderr = self.exec_command(
                    ' '.join([
                        self._shell.executable, '-c',
                        self._shell.quote(f'cat > {out_path}')]),
                    in_data=data,
                    sudoable=False)
            if returncode != 0:
                if 'cat: not found' in stderr.decode('utf-8'):
                    raise AnsibleError(
                        f'cat not found in path of container: {to_text(self.get_option("vmid"))}')
                raise AnsibleError(
                    f'{to_text(stdout)}\n{to_text(stderr)}')
        except Exception as e:
            raise AnsibleError(
                f'error occurred while putting file from {in_path} to {out_path}!\n{to_text(e)}')

    def fetch_file(self, in_path: str, out_path: str) -> None:
        """ save a remote file to the specified path """

        display.vvv(f'FETCH {in_path} TO {out_path}', host=self.get_option('remote_addr'))
        try:
            returncode, stdout, stderr = self.exec_command(
                ' '.join([
                    self._shell.executable, '-c',
                    self._shell.quote(f'cat {in_path}')]),
                sudoable=False)
            if returncode != 0:
                if 'cat: not found' in stderr.decode('utf-8'):
                    raise AnsibleError(
                        f'cat not found in path of container: {to_text(self.get_option("vmid"))}')
                raise AnsibleError(
                    f'{to_text(stdout)}\n{to_text(stderr)}')
            with open(out_path, 'wb') as f:
                f.write(stdout)
        except Exception as e:
            raise AnsibleError(
                f'error occurred while fetching file from {in_path} to {out_path}!\n{to_text(e)}')

    def reset(self) -> None:
        """ reset the connection """

        if not self._connected:
            return
        self.close()
        self._connect()

    def close(self) -> None:
        """ terminate the connection """

        if self.get_option('host_key_checking') and self.get_option('record_host_keys') and self._any_keys_added():
            # add any new SSH host keys -- warning -- this could be slow
            # (This doesn't acquire the connection lock because it needs
            # to exclude only other known_hosts writers, not connections
            # that are starting up.)
            lockfile = os.path.basename(self.keyfile)
            dirname = os.path.dirname(self.keyfile)
            makedirs_safe(dirname)
            tmp_keyfile_name = None
            try:
                with FileLock().lock_file(lockfile, dirname, self.get_option('lock_file_timeout')):
                    # just in case any were added recently

                    self.ssh.load_system_host_keys()
                    self.ssh._host_keys.update(self.ssh._system_host_keys)

                    # gather information about the current key file, so
                    # we can ensure the new file has the correct mode/owner

                    key_dir = os.path.dirname(self.keyfile)
                    if os.path.exists(self.keyfile):
                        key_stat = os.stat(self.keyfile)
                        mode = key_stat.st_mode & 0o777
                        uid = key_stat.st_uid
                        gid = key_stat.st_gid
                    else:
                        mode = 0o644
                        uid = os.getuid()
                        gid = os.getgid()

                    # Save the new keys to a temporary file and move it into place
                    # rather than rewriting the file. We set delete=False because
                    # the file will be moved into place rather than cleaned up.

                    with tempfile.NamedTemporaryFile(dir=key_dir, delete=False) as tmp_keyfile:
                        tmp_keyfile_name = tmp_keyfile.name
                        os.chmod(tmp_keyfile_name, mode)
                        os.chown(tmp_keyfile_name, uid, gid)
                        self._save_ssh_host_keys(tmp_keyfile_name)

                    os.rename(tmp_keyfile_name, self.keyfile)
            except LockTimeout:
                raise AnsibleError(
                    f'writing lock file for {self.keyfile} ran in to the timeout of {self.get_option("lock_file_timeout")}s')
            except paramiko.hostkeys.InvalidHostKey as e:
                raise AnsibleConnectionFailure(f'Invalid host key: {e.line}')
            except Exception as e:
                # unable to save keys, including scenario when key was invalid
                # and caught earlier
                raise AnsibleError(
                    f'error occurred while writing SSH host keys!\n{to_text(e)}')
            finally:
                if tmp_keyfile_name is not None:
                    pathlib.Path(tmp_keyfile_name).unlink(missing_ok=True)

        self.ssh.close()
        self._connected = False
