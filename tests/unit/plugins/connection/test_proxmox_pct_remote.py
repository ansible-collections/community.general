# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (annotations, absolute_import, division, print_function)
__metaclass__ = type

import os
import pytest

from ansible_collections.community.general.plugins.connection.proxmox_pct_remote import authenticity_msg, MyAddPolicy
from ansible_collections.community.general.plugins.module_utils._filelock import FileLock, LockTimeout
from ansible.errors import AnsibleError, AnsibleAuthenticationFailure, AnsibleConnectionFailure
from ansible.module_utils.common.text.converters import to_bytes
from ansible.playbook.play_context import PlayContext
from ansible.plugins.loader import connection_loader
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


paramiko = pytest.importorskip('paramiko')


@pytest.fixture
def connection():
    play_context = PlayContext()
    in_stream = StringIO()
    conn = connection_loader.get('community.general.proxmox_pct_remote', play_context, in_stream)
    conn.set_option('remote_addr', '192.168.1.100')
    conn.set_option('remote_user', 'root')
    conn.set_option('password', 'password')
    return conn


def test_connection_options(connection):
    """ Test that connection options are properly set """
    assert connection.get_option('remote_addr') == '192.168.1.100'
    assert connection.get_option('remote_user') == 'root'
    assert connection.get_option('password') == 'password'


def test_authenticity_msg():
    """ Test authenticity message formatting """
    msg = authenticity_msg('test.host', 'ssh-rsa', 'AA:BB:CC:DD')
    assert 'test.host' in msg
    assert 'ssh-rsa' in msg
    assert 'AA:BB:CC:DD' in msg


def test_missing_host_key(connection):
    """ Test MyAddPolicy missing_host_key method """

    client = MagicMock()
    key = MagicMock()
    key.get_fingerprint.return_value = b'fingerprint'
    key.get_name.return_value = 'ssh-rsa'

    policy = MyAddPolicy(connection)

    connection.set_option('host_key_auto_add', True)
    policy.missing_host_key(client, 'test.host', key)
    assert hasattr(key, '_added_by_ansible_this_time')

    connection.set_option('host_key_auto_add', False)
    connection.set_option('host_key_checking', False)
    policy.missing_host_key(client, 'test.host', key)

    connection.set_option('host_key_checking', True)
    connection.set_option('host_key_auto_add', False)
    connection.set_option('use_persistent_connections', False)

    with patch('ansible.utils.display.Display.prompt_until', return_value='yes'):
        policy.missing_host_key(client, 'test.host', key)

    with patch('ansible.utils.display.Display.prompt_until', return_value='no'):
        with pytest.raises(AnsibleError, match='host connection rejected by user'):
            policy.missing_host_key(client, 'test.host', key)


def test_set_log_channel(connection):
    """ Test setting log channel """
    connection._set_log_channel('test_channel')
    assert connection._log_channel == 'test_channel'


def test_parse_proxy_command(connection):
    """ Test proxy command parsing """
    connection.set_option('proxy_command', 'ssh -W %h:%p proxy.example.com')
    connection.set_option('remote_addr', 'target.example.com')
    connection.set_option('remote_user', 'testuser')

    result = connection._parse_proxy_command(port=2222)
    assert 'sock' in result
    assert isinstance(result['sock'], paramiko.ProxyCommand)


@patch('paramiko.SSHClient')
def test_connect_with_rsa_sha2_disabled(mock_ssh, connection):
    """ Test connection with RSA SHA2 algorithms disabled """
    connection.set_option('use_rsa_sha2_algorithms', False)
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client

    connection._connect()

    call_kwargs = mock_client.connect.call_args[1]
    assert 'disabled_algorithms' in call_kwargs
    assert 'pubkeys' in call_kwargs['disabled_algorithms']


@patch('paramiko.SSHClient')
def test_connect_with_bad_host_key(mock_ssh, connection):
    """ Test connection with bad host key """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_client.connect.side_effect = paramiko.ssh_exception.BadHostKeyException(
        'hostname', MagicMock(), MagicMock())

    with pytest.raises(AnsibleConnectionFailure, match='host key mismatch'):
        connection._connect()


@patch('paramiko.SSHClient')
def test_connect_with_invalid_host_key(mock_ssh, connection):
    """ Test connection with bad host key """
    connection.set_option('host_key_checking', True)
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_client.load_system_host_keys.side_effect = paramiko.hostkeys.InvalidHostKey(
        "Bad Line!", Exception('Something crashed!'))

    with pytest.raises(AnsibleConnectionFailure, match="Invalid host key: Bad Line!"):
        connection._connect()


@patch('paramiko.SSHClient')
def test_connect_success(mock_ssh, connection):
    """ Test successful SSH connection establishment """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client

    connection._connect()

    assert mock_client.connect.called
    assert connection._connected


@patch('paramiko.SSHClient')
def test_connect_authentication_failure(mock_ssh, connection):
    """ Test SSH connection with authentication failure """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_client.connect.side_effect = paramiko.ssh_exception.AuthenticationException('Auth failed')

    with pytest.raises(AnsibleAuthenticationFailure):
        connection._connect()


def test_any_keys_added(connection):
    """ Test checking for added host keys """
    connection.ssh = MagicMock()
    connection.ssh._host_keys = {
        'host1': {
            'ssh-rsa': MagicMock(_added_by_ansible_this_time=True),
            'ssh-ed25519': MagicMock(_added_by_ansible_this_time=False)
        }
    }

    assert connection._any_keys_added() is True

    connection.ssh._host_keys = {
        'host1': {
            'ssh-rsa': MagicMock(_added_by_ansible_this_time=False)
        }
    }
    assert connection._any_keys_added() is False


@patch('os.path.exists')
@patch('os.stat')
@patch('tempfile.NamedTemporaryFile')
def test_save_ssh_host_keys(mock_tempfile, mock_stat, mock_exists, connection):
    """ Test saving SSH host keys """
    mock_exists.return_value = True
    mock_stat.return_value = MagicMock(st_mode=0o644, st_uid=1000, st_gid=1000)
    mock_tempfile.return_value.__enter__.return_value.name = '/tmp/test_keys'

    connection.ssh = MagicMock()
    connection.ssh._host_keys = {
        'host1': {
            'ssh-rsa': MagicMock(
                get_base64=lambda: 'KEY1',
                _added_by_ansible_this_time=True
            )
        }
    }

    mock_open_obj = mock_open()
    with patch('builtins.open', mock_open_obj):
        connection._save_ssh_host_keys('/tmp/test_keys')

    mock_open_obj().write.assert_called_with('host1 ssh-rsa KEY1\n')


def test_build_pct_command(connection):
    """ Test PCT command building with different users """
    connection.set_option('vmid', '100')

    cmd = connection._build_pct_command('/bin/sh -c "ls -la"')
    assert cmd == '/usr/sbin/pct exec 100 -- /bin/sh -c "ls -la"'

    connection.set_option('remote_user', 'user')
    connection.set_option('proxmox_become_method', 'sudo')
    cmd = connection._build_pct_command('/bin/sh -c "ls -la"')
    assert cmd == 'sudo /usr/sbin/pct exec 100 -- /bin/sh -c "ls -la"'


@patch('paramiko.SSHClient')
def test_exec_command_success(mock_ssh, connection):
    """ Test successful command execution """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 0
    mock_channel.makefile.return_value = [to_bytes('stdout')]
    mock_channel.makefile_stderr.return_value = [to_bytes("")]

    connection._connected = True
    connection.ssh = mock_client

    returncode, stdout, stderr = connection.exec_command('ls -la')

    mock_transport.open_session.assert_called_once()
    mock_channel.get_pty.assert_called_once()
    mock_transport.set_keepalive.assert_called_once_with(5)


@patch('paramiko.SSHClient')
def test_exec_command_pct_not_found(mock_ssh, connection):
    """ Test command execution when PCT is not found """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 1
    mock_channel.makefile.return_value = [to_bytes("")]
    mock_channel.makefile_stderr.return_value = [to_bytes('pct: not found')]

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleError, match='pct not found in path of host'):
        connection.exec_command('ls -la')


@patch('paramiko.SSHClient')
def test_exec_command_session_open_failure(mock_ssh, connection):
    """ Test exec_command when session opening fails """
    mock_client = MagicMock()
    mock_transport = MagicMock()
    mock_transport.open_session.side_effect = Exception('Failed to open session')
    mock_client.get_transport.return_value = mock_transport

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleConnectionFailure, match='Failed to open session'):
        connection.exec_command('test command')


@patch('paramiko.SSHClient')
def test_exec_command_with_privilege_escalation(mock_ssh, connection):
    """ Test exec_command with privilege escalation """
    mock_client = MagicMock()
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    connection._connected = True
    connection.ssh = mock_client

    connection.become = MagicMock()
    connection.become.expect_prompt.return_value = True
    connection.become.check_success.return_value = False
    connection.become.check_password_prompt.return_value = True
    connection.become.get_option.return_value = 'sudo_password'

    mock_channel.recv.return_value = b'[sudo] password:'
    mock_channel.recv_exit_status.return_value = 0
    mock_channel.makefile.return_value = [b""]
    mock_channel.makefile_stderr.return_value = [b""]

    returncode, stdout, stderr = connection.exec_command('sudo test command')

    mock_channel.sendall.assert_called_once_with(b'sudo_password\n')


def test_put_file(connection):
    """ Test putting a file to the remote system """
    connection.exec_command = MagicMock()
    connection.exec_command.return_value = (0, b"", b"")

    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b'test content'
        connection.put_file('/local/path', '/remote/path')

    connection.exec_command.assert_called_once_with("/bin/sh -c 'cat > /remote/path'", in_data=b'test content', sudoable=False)


@patch('paramiko.SSHClient')
def test_put_file_general_error(mock_ssh, connection):
    """ Test put_file with general error """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 1
    mock_channel.makefile.return_value = [to_bytes("")]
    mock_channel.makefile_stderr.return_value = [to_bytes('Some error')]

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleError, match='error occurred while putting file from /remote/path to /local/path'):
        connection.put_file('/remote/path', '/local/path')


@patch('paramiko.SSHClient')
def test_put_file_cat_not_found(mock_ssh, connection):
    """ Test command execution when cat is not found """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 1
    mock_channel.makefile.return_value = [to_bytes("")]
    mock_channel.makefile_stderr.return_value = [to_bytes('cat: not found')]

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleError, match='cat not found in path of container:'):
        connection.fetch_file('/remote/path', '/local/path')


def test_fetch_file(connection):
    """ Test fetching a file from the remote system """
    connection.exec_command = MagicMock()
    connection.exec_command.return_value = (0, b'test content', b"")

    with patch('builtins.open', create=True) as mock_open:
        connection.fetch_file('/remote/path', '/local/path')

    connection.exec_command.assert_called_once_with("/bin/sh -c 'cat /remote/path'", sudoable=False)
    mock_open.assert_called_with('/local/path', 'wb')


@patch('paramiko.SSHClient')
def test_fetch_file_general_error(mock_ssh, connection):
    """ Test fetch_file with general error """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 1
    mock_channel.makefile.return_value = [to_bytes("")]
    mock_channel.makefile_stderr.return_value = [to_bytes('Some error')]

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleError, match='error occurred while fetching file from /remote/path to /local/path'):
        connection.fetch_file('/remote/path', '/local/path')


@patch('paramiko.SSHClient')
def test_fetch_file_cat_not_found(mock_ssh, connection):
    """ Test command execution when cat is not found """
    mock_client = MagicMock()
    mock_ssh.return_value = mock_client
    mock_channel = MagicMock()
    mock_transport = MagicMock()

    mock_client.get_transport.return_value = mock_transport
    mock_transport.open_session.return_value = mock_channel
    mock_channel.recv_exit_status.return_value = 1
    mock_channel.makefile.return_value = [to_bytes("")]
    mock_channel.makefile_stderr.return_value = [to_bytes('cat: not found')]

    connection._connected = True
    connection.ssh = mock_client

    with pytest.raises(AnsibleError, match='cat not found in path of container:'):
        connection.fetch_file('/remote/path', '/local/path')


def test_close(connection):
    """ Test connection close """
    mock_ssh = MagicMock()
    connection.ssh = mock_ssh
    connection._connected = True

    connection.close()

    assert mock_ssh.close.called, 'ssh.close was not called'
    assert not connection._connected, 'self._connected is still True'


def test_close_with_lock_file(connection):
    """ Test close method with lock file creation """
    connection._any_keys_added = MagicMock(return_value=True)
    connection._connected = True
    connection.keyfile = '/tmp/pct-remote-known_hosts-test'
    connection.set_option('host_key_checking', True)
    connection.set_option('lock_file_timeout', 5)
    connection.set_option('record_host_keys', True)
    connection.ssh = MagicMock()

    lock_file_path = os.path.join(os.path.dirname(connection.keyfile),
                                  f'ansible-{os.path.basename(connection.keyfile)}.lock')

    try:
        connection.close()
        assert os.path.exists(lock_file_path), 'Lock file was not created'

        lock_stat = os.stat(lock_file_path)
        assert lock_stat.st_mode & 0o777 == 0o600, 'Incorrect lock file permissions'
    finally:
        Path(lock_file_path).unlink(missing_ok=True)


@patch('pathlib.Path.unlink')
@patch('os.path.exists')
def test_close_lock_file_time_out_error_handling(mock_exists, mock_unlink, connection):
    """ Test close method with lock file timeout error """
    connection._any_keys_added = MagicMock(return_value=True)
    connection._connected = True
    connection._save_ssh_host_keys = MagicMock()
    connection.keyfile = '/tmp/pct-remote-known_hosts-test'
    connection.set_option('host_key_checking', True)
    connection.set_option('lock_file_timeout', 5)
    connection.set_option('record_host_keys', True)
    connection.ssh = MagicMock()

    mock_exists.return_value = False
    matcher = f'writing lock file for {connection.keyfile} ran in to the timeout of {connection.get_option("lock_file_timeout")}s'
    with pytest.raises(AnsibleError, match=matcher):
        with patch('os.getuid', return_value=1000), \
             patch('os.getgid', return_value=1000), \
             patch('os.chmod'), patch('os.chown'), \
             patch('os.rename'), \
             patch.object(FileLock, 'lock_file', side_effect=LockTimeout()):
            connection.close()


@patch('ansible_collections.community.general.plugins.module_utils._filelock.FileLock.lock_file')
@patch('tempfile.NamedTemporaryFile')
@patch('os.chmod')
@patch('os.chown')
@patch('os.rename')
@patch('os.path.exists')
def test_tempfile_creation_and_move(mock_exists, mock_rename, mock_chown, mock_chmod, mock_tempfile, mock_lock_file, connection):
    """ Test tempfile creation and move during close """
    connection._any_keys_added = MagicMock(return_value=True)
    connection._connected = True
    connection._save_ssh_host_keys = MagicMock()
    connection.keyfile = '/tmp/pct-remote-known_hosts-test'
    connection.set_option('host_key_checking', True)
    connection.set_option('lock_file_timeout', 5)
    connection.set_option('record_host_keys', True)
    connection.ssh = MagicMock()

    mock_exists.return_value = False

    mock_lock_file_instance = MagicMock()
    mock_lock_file.return_value = mock_lock_file_instance
    mock_lock_file_instance.__enter__.return_value = None

    mock_tempfile_instance = MagicMock()
    mock_tempfile_instance.name = '/tmp/mock_tempfile'
    mock_tempfile.return_value.__enter__.return_value = mock_tempfile_instance

    mode = 0o644
    uid = 1000
    gid = 1000
    key_dir = os.path.dirname(connection.keyfile)

    with patch('os.getuid', return_value=uid), patch('os.getgid', return_value=gid):
        connection.close()

    connection._save_ssh_host_keys.assert_called_once_with('/tmp/mock_tempfile')
    mock_chmod.assert_called_once_with('/tmp/mock_tempfile', mode)
    mock_chown.assert_called_once_with('/tmp/mock_tempfile', uid, gid)
    mock_rename.assert_called_once_with('/tmp/mock_tempfile', connection.keyfile)
    mock_tempfile.assert_called_once_with(dir=key_dir, delete=False)


@patch('pathlib.Path.unlink')
@patch('tempfile.NamedTemporaryFile')
@patch('ansible_collections.community.general.plugins.module_utils._filelock.FileLock.lock_file')
@patch('os.path.exists')
def test_close_tempfile_error_handling(mock_exists, mock_lock_file, mock_tempfile, mock_unlink, connection):
    """ Test tempfile creation error """
    connection._any_keys_added = MagicMock(return_value=True)
    connection._connected = True
    connection._save_ssh_host_keys = MagicMock()
    connection.keyfile = '/tmp/pct-remote-known_hosts-test'
    connection.set_option('host_key_checking', True)
    connection.set_option('lock_file_timeout', 5)
    connection.set_option('record_host_keys', True)
    connection.ssh = MagicMock()

    mock_exists.return_value = False

    mock_lock_file_instance = MagicMock()
    mock_lock_file.return_value = mock_lock_file_instance
    mock_lock_file_instance.__enter__.return_value = None

    mock_tempfile_instance = MagicMock()
    mock_tempfile_instance.name = '/tmp/mock_tempfile'
    mock_tempfile.return_value.__enter__.return_value = mock_tempfile_instance

    with pytest.raises(AnsibleError, match='error occurred while writing SSH host keys!'):
        with patch.object(os, 'chmod', side_effect=Exception()):
            connection.close()
    mock_unlink.assert_called_with(missing_ok=True)


@patch('ansible_collections.community.general.plugins.module_utils._filelock.FileLock.lock_file')
@patch('os.path.exists')
def test_close_with_invalid_host_key(mock_exists, mock_lock_file, connection):
    """ Test load_system_host_keys on close with InvalidHostKey error """
    connection._any_keys_added = MagicMock(return_value=True)
    connection._connected = True
    connection._save_ssh_host_keys = MagicMock()
    connection.keyfile = '/tmp/pct-remote-known_hosts-test'
    connection.set_option('host_key_checking', True)
    connection.set_option('lock_file_timeout', 5)
    connection.set_option('record_host_keys', True)
    connection.ssh = MagicMock()
    connection.ssh.load_system_host_keys.side_effect = paramiko.hostkeys.InvalidHostKey(
        "Bad Line!", Exception('Something crashed!'))

    mock_exists.return_value = False

    mock_lock_file_instance = MagicMock()
    mock_lock_file.return_value = mock_lock_file_instance
    mock_lock_file_instance.__enter__.return_value = None

    with pytest.raises(AnsibleConnectionFailure, match="Invalid host key: Bad Line!"):
        connection.close()


def test_reset(connection):
    """ Test connection reset """
    connection._connected = True
    connection.close = MagicMock()
    connection._connect = MagicMock()

    connection.reset()

    connection.close.assert_called_once()
    connection._connect.assert_called_once()

    connection._connected = False
    connection.reset()
    assert connection.close.call_count == 1
