#
# Copyright (c) 2020, SCC France, Eric Belhomme <ebelhomme@fr.scc.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author:
  - Eric Belhomme (@eric-belhomme) <ebelhomme@fr.scc.com>
version_added: '0.2.0'
name: etcd3
short_description: Get key values from etcd3 server
description:
  - Retrieves key values and/or key prefixes from etcd3 server using its native gRPC API.
  - Try to reuse M(community.general.etcd3) options for connection parameters, but add support for some E(ETCDCTL_*) environment
    variables.
  - See U(https://github.com/etcd-io/etcd/tree/master/Documentation/op-guide) for etcd overview.
options:
  _terms:
    description:
      - The list of keys (or key prefixes) to look up on the etcd3 server.
    type: list
    elements: str
    required: true
  prefix:
    description:
      - Look for key or prefix key.
    type: bool
    default: false
  endpoints:
    description:
      - Counterpart of E(ETCDCTL_ENDPOINTS) environment variable. Specify the etcd3 connection with an URL form, for example
        V(https://hostname:2379), or V(<host>:<port>) form.
      - The V(host) part is overwritten by O(host) option, if defined.
      - The V(port) part is overwritten by O(port) option, if defined.
      - Note that specifying V(https://) in the endpoint URL does not by itself enable TLS. To connect to an HTTPS etcd3
        endpoint, you must provide O(ca_cert) (and optionally O(cert_cert) and O(cert_key)).
    env:
      - name: ETCDCTL_ENDPOINTS
    default: '127.0.0.1:2379'
    type: str
  host:
    description:
      - Etcd3 listening client host.
      - Takes precedence over O(endpoints).
      - Must be a bare hostname or IP address without a URL scheme. If a V(https://) or V(http://) prefix is present,
        it will be stripped automatically.
    type: str
  port:
    description:
      - Etcd3 listening client port.
      - Takes precedence over O(endpoints).
    type: int
  ca_cert:
    description:
      - Etcd3 CA authority.
      - Required to enable TLS when connecting to an HTTPS etcd3 endpoint.
    env:
      - name: ETCDCTL_CACERT
    type: str
  cert_cert:
    description:
      - Etcd3 client certificate.
    env:
      - name: ETCDCTL_CERT
    type: str
  cert_key:
    description:
      - Etcd3 client private key.
    env:
      - name: ETCDCTL_KEY
    type: str
  timeout:
    description:
      - Client timeout.
    default: 60
    env:
      - name: ETCDCTL_DIAL_TIMEOUT
    type: int
  user:
    description:
      - Authenticated user name.
    env:
      - name: ETCDCTL_USER
    type: str
  password:
    description:
      - Authenticated user password.
    env:
      - name: ETCDCTL_PASSWORD
    type: str

notes:
  - O(host) and O(port) options take precedence over O(endpoints) option.
  - The recommended way to connect to etcd3 server is using E(ETCDCTL_ENDPOINT) environment variable and keep O(endpoints),
    O(host), and O(port) unused.
  - To connect to an HTTPS etcd3 endpoint, the O(ca_cert) option must be provided. Merely specifying V(https://) in
    O(endpoints) is not sufficient to enable TLS.
seealso:
  - module: community.general.etcd3
  - plugin: community.general.etcd
    plugin_type: lookup

requirements:
  - "etcd3 >= 0.10"
"""

EXAMPLES = r"""
- name: "a value from a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo/bar') }}"

- name: "values from multiple folders on a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo', 'bar', 'baz') }}"

- name: "look for a key prefix"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', '/foo/bar', prefix=True) }}"

- name: "connect to etcd3 with a client certificate"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo/bar', cert_cert='/etc/ssl/etcd/client.pem', cert_key='/etc/ssl/etcd/client.key') }}"

- name: "connect to etcd3 over HTTPS"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo/bar', endpoints='https://etcd.example.com:2379', ca_cert='/etc/ssl/etcd/ca.pem') }}"
"""

RETURN = r"""
_raw:
  description:
    - List of keys and associated values.
  type: list
  elements: dict
  contains:
    key:
      description: The element's key.
      type: str
    value:
      description: The element's value.
      type: str
"""

import re

from ansible.errors import AnsibleLookupError
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

from ansible_collections.community.general.plugins.plugin_utils._lookup import check_for_wrong_terms

try:
    import etcd3

    HAS_ETCD = True
except ImportError:
    HAS_ETCD = False

display = Display()

etcd3_cnx_opts = (
    "host",
    "port",
    "ca_cert",
    "cert_key",
    "cert_cert",
    "timeout",
    "user",
    "password",
    # 'grpc_options' Etcd3Client() option currently not supported by lookup module (maybe in future ?)
)


def etcd3_client(client_params):
    try:
        etcd = etcd3.client(**client_params)
        etcd.status()
    except Exception as exp:
        raise AnsibleLookupError(f"Cannot connect to etcd cluster: {exp}") from exp
    return etcd


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        check_for_wrong_terms(self, direct=kwargs)

        if not HAS_ETCD:
            display.error(missing_required_lib("etcd3"))
            return None

        # create the etcd3 connection parameters dict to pass to etcd3 class
        client_params = {}

        # etcd3 class expects host and port as connection parameters, so endpoints
        # must be mangled a bit to fit in this scheme.
        # so here we use a regex to extract server and port
        is_https = False
        match = re.compile(
            r"^(?P<scheme>https?://)?(?P<host>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([-_\d\w\.]+))(:(?P<port>\d{1,5}))?/?$"
        ).match(self.get_option("endpoints"))
        if match:
            if match.group("host"):
                client_params["host"] = match.group("host")
            if match.group("port"):
                client_params["port"] = match.group("port")
            if match.group("scheme") and match.group("scheme").startswith("https"):
                is_https = True

        for opt in etcd3_cnx_opts:
            if self.get_option(opt):
                client_params[opt] = self.get_option(opt)

        # strip URL scheme from host if present
        if "host" in client_params:
            host_match = re.match(r"^(?P<scheme>https?://)(?P<host>.+)$", client_params["host"])
            if host_match:
                display.warning(
                    f"The host option contained a URL scheme '{host_match.group('scheme')}' which has been removed. "
                    "Use a bare hostname or IP address for the host option. "
                    "To enable TLS, provide the ca_cert option."
                )
                client_params["host"] = host_match.group("host")
                if host_match.group("scheme").startswith("https"):
                    is_https = True

        if is_https and not self.get_option("ca_cert"):
            display.warning(
                "An HTTPS endpoint was specified but ca_cert was not provided. "
                "The connection will be attempted without TLS. "
                "To enable TLS, provide the ca_cert option."
            )

        cnx_log = dict(client_params)
        if "password" in cnx_log:
            cnx_log["password"] = "<redacted>"
        display.verbose(f"etcd3 connection parameters: {cnx_log}")

        # connect to etcd3 server
        etcd = etcd3_client(client_params)

        ret = []
        # we can pass many keys to lookup
        for term in terms:
            if self.get_option("prefix"):
                try:
                    for val, meta in etcd.get_prefix(term):
                        if val and meta:
                            ret.append({"key": to_native(meta.key), "value": to_native(val)})
                except Exception as exp:
                    display.warning(f"Caught except during etcd3.get_prefix: {exp}")
            else:
                try:
                    val, meta = etcd.get(term)
                    if val and meta:
                        ret.append({"key": to_native(meta.key), "value": to_native(val)})
                except Exception as exp:
                    display.warning(f"Caught except during etcd3.get: {exp}")
        return ret
