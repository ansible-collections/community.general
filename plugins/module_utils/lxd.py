# -*- coding: utf-8 -*-

# Copyright (c) 2016, Hiroaki Nakamura <hnakamur@gmail.com>
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import os
import socket
import ssl
import json

from ansible.module_utils.urls import generic_urlparse
from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.module_utils.six.moves import http_client
from ansible.module_utils.common.text.converters import to_text


# ANSIBLE_LXD_DEFAULT_URL is a default value of the lxd endpoint
ANSIBLE_LXD_DEFAULT_URL = 'unix:/var/lib/lxd/unix.socket'

# ANSIBLE_LXD_STATES is a map of states of lxd containers to the Ansible
# lxc_container module state parameter value.
ANSIBLE_LXD_STATES = {
    'Running': 'started',
    'Stopped': 'stopped',
    'Frozen': 'frozen',
}


# httplib/http.client connection using unix domain socket
HTTPConnection = http_client.HTTPConnection
HTTPSConnection = http_client.HTTPSConnection


class UnixHTTPConnection(HTTPConnection):
    def __init__(self, path):
        HTTPConnection.__init__(self, 'localhost')
        self.path = path

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self.sock = sock


class LXDClientException(Exception):
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.kwargs = kwargs


class LXDClient(object):
    def __init__(self, url, key_file=None, cert_file=None, debug=False):
        """LXD Client.

        :param url: The URL of the LXD server. (e.g. unix:/var/lib/lxd/unix.socket or https://127.0.0.1)
        :type url: ``str``
        :param key_file: The path of the client certificate key file.
        :type key_file: ``str``
        :param cert_file: The path of the client certificate file.
        :type cert_file: ``str``
        :param debug: The debug flag. The request and response are stored in logs when debug is true.
        :type debug: ``bool``
        """
        self.url = url
        self.debug = debug
        self.logs = []
        if url.startswith('https:'):
            self.cert_file = cert_file
            self.key_file = key_file
            parts = generic_urlparse(urlparse(self.url))
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain(cert_file, keyfile=key_file)
            self.connection = HTTPSConnection(parts.get('netloc'), context=ctx)
        elif url.startswith('unix:'):
            unix_socket_path = url[len('unix:'):]
            self.connection = UnixHTTPConnection(unix_socket_path)
        else:
            raise LXDClientException('URL scheme must be unix: or https:')

    def do(self, method, url, body_json=None, ok_error_codes=None, timeout=None, wait_for_container=None):
        resp_json = self._send_request(method, url, body_json=body_json, ok_error_codes=ok_error_codes, timeout=timeout)
        if resp_json['type'] == 'async':
            url = '{0}/wait'.format(resp_json['operation'])
            resp_json = self._send_request('GET', url)
            if wait_for_container:
                while resp_json['metadata']['status'] == 'Running':
                    resp_json = self._send_request('GET', url)
            if resp_json['metadata']['status'] != 'Success':
                self._raise_err_from_json(resp_json)
        return resp_json

    def authenticate(self, trust_password):
        body_json = {'type': 'client', 'password': trust_password}
        return self._send_request('POST', '/1.0/certificates', body_json=body_json)

    def _send_request(self, method, url, body_json=None, ok_error_codes=None, timeout=None):
        try:
            body = json.dumps(body_json)
            self.connection.request(method, url, body=body)
            resp = self.connection.getresponse()
            resp_data = resp.read()
            resp_data = to_text(resp_data, errors='surrogate_or_strict')
            resp_json = json.loads(resp_data)
            self.logs.append({
                'type': 'sent request',
                'request': {'method': method, 'url': url, 'json': body_json, 'timeout': timeout},
                'response': {'json': resp_json}
            })
            resp_type = resp_json.get('type', None)
            if resp_type == 'error':
                if ok_error_codes is not None and resp_json['error_code'] in ok_error_codes:
                    return resp_json
                if resp_json['error'] == "Certificate already in trust store":
                    return resp_json
                self._raise_err_from_json(resp_json)
            return resp_json
        except socket.error as e:
            raise LXDClientException('cannot connect to the LXD server', err=e)

    def _raise_err_from_json(self, resp_json):
        err_params = {}
        if self.debug:
            err_params['logs'] = self.logs
        raise LXDClientException(self._get_err_from_resp_json(resp_json), **err_params)

    @staticmethod
    def _get_err_from_resp_json(resp_json):
        err = None
        metadata = resp_json.get('metadata', None)
        if metadata is not None:
            err = metadata.get('err', None)
        if err is None:
            err = resp_json.get('error', None)
        return err


def default_key_file():
    return os.path.expanduser('~/.config/lxc/client.key')


def default_cert_file():
    return os.path.expanduser('~/.config/lxc/client.crt')


# Copyright (c) 2023, Heino H. Gehlsen <heino.gehlsen@gmail.com>
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import traceback
from ansible.module_utils.basic import missing_required_lib
try:
    from pylxd import Client as PyLxdClient
    from pylxd.exceptions import LXDAPIException, ClientConnectionFailed
except ImportError:
    HAS_PYLXD = False
    PYLXD_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYLXD = True
    PYLXD_IMPORT_ERROR = None


class LxdBase(object):

    def __init__(self, module):
        if not HAS_PYLXD:
            module.fail_json(msg=_get_missing_pylxd_message(), exception=PYLXD_IMPORT_ERROR)

        self.module = module

        self.endpoint = self.module.params['url']
        self.client_cert = self.module.params['client_cert']
        self.client_key = self.module.params['client_key']
        self.trust_password = self.module.params['trust_password']
        self.verify = self.module.params['verify']
        self.timeout = self.module.params['timeout']
        self.project = self.module.params['project']

        self.debug = self.module._verbosity >= 4

        # Snap override
        if self.endpoint == ANSIBLE_LXD_DEFAULT_URL:
            try:
                snap_socket = self.module.params['snap_url']
                if os.path.exists(snap_socket.replace('unix:', '')):
                    self.endpoint = snap_socket
            except Exception as e:
                self.module.fail_json(msg=e.msg)

        try:
            self.client = pylxd_client(
                endpoint=self.endpoint,
                client_cert=self.client_cert,
                client_key=self.client_key,
                password=self.trust_password,
                project=self.project,
                timeout=self.timeout,
                verify=self.verify,
            )
        except LXDClientException as e:
            self.module.fail_json(msg=e.msg)

    def get_instance(self, name, type):
        if type == 'container':
            return self.client.containers.get(name)
        if type == 'virtual-machine':
            return self.client.virtual_machines.get(name)
        raise ValueError(type)



def pylxd_client(endpoint, client_cert=None, client_key=None, password=None, project=None, timeout=None, verify=True):
    if not HAS_PYLXD:
        raise LXDClientException(_get_missing_pylxd_message(), PYLXD_IMPORT_ERROR)

    try:
        # Connecting to the local unix socket
        if endpoint is None or endpoint == '/var/lib/lxd/unix.socket' or endpoint == 'unix:/var/lib/lxd/unix.socket':
            return PyLxdClient(
                timeout=timeout,
                project=project,
            )

        # Connecting to some other local socket
        elif endpoint.startswith('/'):
            return PyLxdClient(
                endpoint=endpoint,
                timeout=timeout,
                project=project,
            )

        # Connecting to remote server
        elif endpoint.startswith('https://'):

            if client_cert is None:
                client_cert = '~/.config/lxc/client.crt'
            if client_key is None:
                client_key = '~/.config/lxc/client.key'

            # Expand an initial '~/'-path component
            client_cert = os.path.expanduser(client_cert)
            client_key = os.path.expanduser(client_key)

            if not os.path.isfile(client_cert):
                raise ValueError("Invalid client_cert path: '{path}' does not exist or is not a file.".format(path=client_cert))
            if not os.path.isfile(client_key):
                raise ValueError("Invalid client_key path: '{path}' does not exist or is not a file.".format(path=client_key))

            client = PyLxdClient(
                endpoint=endpoint,
                cert=(client_cert, client_key),
                verify=verify,
                timeout=timeout,
                project=project,
            )

            if not client.trusted:
                if password is None:
                    raise LXDClientException('The certificate is not yet trusted, but no trusted password provided')
                try:
                    client.authenticate(password)
                except LXDAPIException as e:
                    raise LXDClientException(str(e))

            return client

        # Invalid url
        else:
            raise ValueError('Invalid endpoint: ' + endpoint)

    except ClientConnectionFailed as e:
        raise LXDClientException(
            "Failed to connect to '{endpoint}'   {msg}  !".format(endpoint=endpoint, msg=str(e))
        )
# TODO: Does this actually happen???
#   except TypeError as e:
#       # Happens when the verification failed.
#       raise LXDClientException(
#           f("Failed to connect to '{endpoint}' looks like the SSL verification failed, error was: {e}"
#       )


def _get_missing_pylxd_message():
    return missing_required_lib('pylxd', url='https://pylxd.readthedocs.io/')
