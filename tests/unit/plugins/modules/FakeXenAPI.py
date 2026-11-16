#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

FAKE_API_VERSION = "1.1"#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

FAKE_API_VERSION = "1.1"


class FakeTransport:
        def __init__(self):
                    self.user_agent = None
                    self.verbose = 0
                    self.timeout = None
                    self._connection = None

    def close(self):
                """Close the connection."""
                self._connection = None

    def send(self, data):
                """Send data (stub for XML-RPC protocol)."""
                pass

    def request(self, method, handler, body, headers=None):
                """Handle HTTP request (stub for XML-RPC)."""
                pass

    def getresponse(self):
                """Get response (stub for XML-RPC)."""
                return None

    def set_tunnel(self, host, port=None, headers=None):
                """Set tunnel for proxy (stub)."""
                pass


class Failure(Exception):
        def __init__(self, details):
                    self.details = details

    def __str__(self):
                return str(self.details)


class Session:
        def __init__(self, uri, transport=None, encoding=None, verbose=0, allow_none=1, ignore_ssl=False):
                    self.transport = transport if transport is not None else FakeTransport()
                    self._session = None
                    self.last_login_method = None
                    self.last_login_params = None
                    self.API_version = FAKE_API_VERSION

    def _get_api_version(self):
                return FAKE_API_VERSION

    def _login(self, method, params):
                self._session = "OpaqueRef:fake-xenapi-session-ref"
                self.last_login_method = method
                self.last_login_params = params
                self.API_version = self._get_api_version()

    def _logout(self):
                self._session = None
                self.last_login_method = None
                self.last_login_params = None
                self.API_version = FAKE_API_VERSION

    def xenapi_request(self, methodname, params):
                if methodname.startswith("login"):
                                self._login(methodname, params)
                                return None
elif methodname == "logout" or methodname == "session.logout":
            self._logout()
            return None
else:
            # Should be patched with mocker.patch().
            return None

    def __getattr__(self, name):
                if name == "handle":
                                return self._session
elif name == "xenapi":
            # Should be patched with mocker.patch().
            return None
elif name.startswith("login") or name.startswith("slave_local"):
            return lambda *params: self._login(name, params)
elif name == "logout":
            return self._logout

    def __call__(self, name):
                # Mimics xmlrpc.client.ServerProxy.__call__ to support session("transport")
                if name == "transport":
                                return self.transport
                            raise AttributeError(f"Session object is not callable for attribute '{name}'")


def xapi_local():
        return Session("http://_var_lib_xcp_xapi/")


class FakeTransport:
    def __init__(self):
        self.user_agent = None


class Failure(Exception):
    def __init__(self, details):
        self.details = details

    def __str__(self):
        return str(self.details)


class Session:
    def __init__(self, uri, transport=None, encoding=None, verbose=0, allow_none=1, ignore_ssl=False):
        self.transport = transport if transport is not None else FakeTransport()
        self._session = None
        self.last_login_method = None
        self.last_login_params = None
        self.API_version = FAKE_API_VERSION

    def _get_api_version(self):
        return FAKE_API_VERSION

    def _login(self, method, params):
        self._session = "OpaqueRef:fake-xenapi-session-ref"
        self.last_login_method = method
        self.last_login_params = params
        self.API_version = self._get_api_version()

    def _logout(self):
        self._session = None
        self.last_login_method = None
        self.last_login_params = None
        self.API_version = FAKE_API_VERSION

    def xenapi_request(self, methodname, params):
        if methodname.startswith("login"):
            self._login(methodname, params)
            return None
        elif methodname == "logout" or methodname == "session.logout":
            self._logout()
            return None
        else:
            # Should be patched with mocker.patch().
            return None

    def __getattr__(self, name):
        if name == "handle":
            return self._session
        elif name == "xenapi":
            # Should be patched with mocker.patch().
            return None
        elif name.startswith("login") or name.startswith("slave_local"):
            return lambda *params: self._login(name, params)
        elif name == "logout":
            return self._logout

    def __call__(self, name):
        # Mimics xmlrpc.client.ServerProxy.__call__ to support session("transport")
        if name == "transport":
            return self.transport
        raise AttributeError(f"Session object is not callable for attribute '{name}'")


def xapi_local():
    return Session("http://_var_lib_xcp_xapi/")
