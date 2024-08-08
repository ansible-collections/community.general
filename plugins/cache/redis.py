# -*- coding: utf-8 -*-
# Copyright (c) 2014, Brian Coca, Josh Drake, et al
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Unknown (!UNKNOWN)
    name: redis
    short_description: Use Redis DB for cache
    description:
        - This cache uses JSON formatted, per host records saved in Redis.
    requirements:
      - redis>=2.4.5 (python lib)
    options:
      _decode_responses:
        description: If set to `true`, returned values from Redis commands get decoded automatically using the client's charset value.
        type: bool
        default: false
        env:
          - name: ANSIBLE_CACHE_REDIS_DECODE_RESPONSES
        ini:
          - key: fact_caching_redis_decode_responses
            section: defaults
      _encoding:
        description: Set the charset to use for facts encoding.
        type: string
        default: utf-8
        env:
          - name: ANSIBLE_CACHE_REDIS_ENCODING
        ini:
          - key: fact_caching_redis_encoding
            section: defaults
      _encoding_errors:
        description:
          - The error handling scheme to use for encoding errors.
          - The default is `strict` meaning that encoding errors raise a `UnicodeEncodeError`.
          - See https://docs.python.org/fr/3/library/stdtypes.html#str.encode for more details.
        type: string
        default: strict
        choices: [ backslashreplace, ignore, replace, strict, xmlcharrefreplace ]
        env:
          - name: ANSIBLE_CACHE_REDIS_ENCODING_ERRORS
        ini:
          - key: fact_caching_redis_encoding_errors
            section: defaults
      _keyset_name:
        description: User defined name for cache keyset name.
        type: string
        default: ansible_cache_keys
        env:
          - name: ANSIBLE_CACHE_REDIS_KEYSET_NAME
        ini:
          - key: fact_caching_redis_keyset_name
            section: defaults
        version_added: 1.3.0
      _prefix:
        description: User defined prefix to use when creating the DB entries
        type: string
        default: ansible_facts
        env:
          - name: ANSIBLE_CACHE_PLUGIN_PREFIX
        ini:
          - key: fact_caching_prefix
            section: defaults
      _retry_on_timeout:
        description:
          - Controls how socket.timeout errors are handled.
          - When set to `false` a TimeoutError will be raised anytime a socket.timeout is encountered.
          - When set to `true`, it enable retries like other `socket.error`s.
        type: bool
        default: false
        env:
          - name: ANSIBLE_CACHE_REDIS_RETRY_ON_TIMEOUT
        ini:
          - key: fact_caching_redis_retry_on_timeout
            section: defaults
      _sentinel_service_name:
        description: The redis sentinel service name (or referenced as cluster name).
        type: string
        env:
          - name: ANSIBLE_CACHE_REDIS_SENTINEL
        ini:
          - key: fact_caching_redis_sentinel
            section: defaults
        version_added: 1.3.0
      _socket_connect_timeout:
        description:
          - Timeout value, in seconds, for Redis socket connection.
          - If not set, connection timeout is disabled.
        type: integer
        env:
          - name: ANSIBLE_CACHE_REDIS_SOCKET_CONNECT_TIMEOUT
        ini:
          - key: fact_caching_redis_socket_connect_timeout
            section: defaults
      _socket_keepalive:
        description:
          - Specifies whether to enable keepalive for Redis socket connection.
        type: bool
        default: false
        env:
          - name: ANSIBLE_CACHE_REDIS_SOCKET_KEEPALIVE
        ini:
          - key: fact_caching_redis_socket_keepalive
            section: defaults
      _socket_keepalive_options:
        description:
          - Finer grain control keepalive options when `_socket_keepalive` is set to `true`.
          - A comma separated socket options string of <key>:<value> pairs, for example V(TCP_KEEPIDLE:600,TCP_KEEPCNT=10,TCP_KEEPINTVL:300).
          - Accepted keys are `TCP_KEEPIDLE`, `TCP_KEEPCNT`, and `TCP_KEEPINTVL`.
          - Integers are expected for values.
        type: string
        env:
          - name: ANSIBLE_CACHE_REDIS_SOCKET_KEEPALIVE_OPTIONS
        ini:
          - key: fact_caching_redis_socket_keepalive_options
            section: defaults
      _socket_timeout:
        description:
          - Timeout value, in seconds, for Redis socket connection.
          - If not set, timeout is disabled.
        type: integer
        env:
          - name: ANSIBLE_CACHE_REDIS_SOCKET_TIMEOUT
        ini:
          - key: fact_caching_redis_socket_timeout
            section: defaults
      _ssl_ca_certs_file:
        description: When using SSL on Redis connection, specifies the SSL CA file path.
        type: string
        env:
          - name: ANSIBLE_CACHE_REDIS_SSL_CA_CERTS_FILE
        ini:
          - key: fact_caching_redis_ssl_ca_certs_file
            section: defaults
      _ssl_cert_file:
        description: When using SSL on Redis connection, specifies the SSL certificate file path.
        type: string
        env:
          - name: ANSIBLE_CACHE_REDIS_SSL_CERT_FILE
        ini:
          - key: fact_caching_redis_ssl_cert_file
            section: defaults
      _ssl_cert_reqs:
        default: none
        type: string
        description:
          - When using SSL on Redis connection, specifies the security mode to use.
          - See https://docs.python.org/3/library/ssl.html#ssl.SSLContext.verify_mode for more details.
        env:
          - name: ANSIBLE_CACHE_REDIS_SSL_CERT_REQ
        ini:
          - key: fact_caching_redis_ssl_cert_req
            section: defaults
        choices: [ none, optionnal, required ]
      _ssl_key_file:
        description: When using SSL on Redis connection, specifies the SSL key file path.
        type: string
        env:
          - name: ANSIBLE_CACHE_REDIS_SSL_KEY_FILE
        ini:
          - key: fact_caching_redis_ssl_key_file
            section: defaults
      _timeout:
        default: 86400
        description: Expiration timeout in seconds for the cache plugin data. Set to 0 to never expire
        type: integer
        # TODO: determine whether it is OK to change to: type: float
        env:
          - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
        ini:
          - key: fact_caching_timeout
            section: defaults
      _uri:
        description:
          - A colon separated string of connection information for Redis.
          - The format is V(host:port:db:password), for example V(localhost:6379:0:changeme).
          - To use encryption in transit, prefix the connection with V(tls://), as in V(tls://localhost:6379:0:changeme).
          - To use redis sentinel, use separator V(;), for example V(localhost:26379;localhost:26379;0:changeme). Requires redis>=2.9.0.
        type: string
        required: true
        env:
          - name: ANSIBLE_CACHE_PLUGIN_CONNECTION
        ini:
          - key: fact_caching_connection
            section: defaults
'''

import re
import time
import json

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_native
from ansible.parsing.ajson import AnsibleJSONEncoder, AnsibleJSONDecoder
from ansible.plugins.cache import BaseCacheModule
from ansible.utils.display import Display

try:
    from redis import StrictRedis, VERSION
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

display = Display()


class CacheModule(BaseCacheModule):
    """
    A caching module backed by redis.

    Keys are maintained in a zset with their score being the timestamp
    when they are inserted. This allows for the usage of 'zremrangebyscore'
    to expire keys. This mechanism is used or a pattern matched 'scan' for
    performance.
    """
    _sentinel_service_name = None
    _encoding_errors_choices = ['backslashreplace', 'ignore', 'replace', 'strict', 'xmlcharrefreplace']
    _socket_keepalive_available_opts = ['TCP_KEEPIDLE', 'TCP_KEEPCNT', 'TCP_KEEPINTVL']
    re_url_conn = re.compile(r'^([^:]+|\[[^]]+\]):(\d+):(\d+)(?::(.*))?$')
    re_sent_conn = re.compile(r'^(.*):(\d+)$')
    re_socket_keepalive_opts = re.compile(r'^(\w+:\d+)(?:,(\w+:\d+))+$')

    def __init__(self, *args, **kwargs):
        uri = ''

        super(CacheModule, self).__init__(*args, **kwargs)
        if self.get_option('_uri'):
            uri = self.get_option('_uri')
        self._timeout = float(self.get_option('_timeout'))
        self._prefix = self.get_option('_prefix')
        self._keys_set = self.get_option('_keyset_name')
        self._sentinel_service_name = self.get_option('_sentinel_service_name')
        self._decode_responses = bool(self.get_option('_decode_responses'))
        self._encoding = self.get_option('_encoding')
        self._encoding_errors = self.get_option('_encoding_errors')
        self._retry_on_timeout = bool(self.get_option('_retry_on_timeout'))
        self._socket_keepalive = self.get_option('_socket_keepalive')
        self._socket_connect_timeout = int(self.get_option('_socket_connect_timeout')) \
            if self._socket_keepalive and self.get_option('_socket_connect_timeout') else None
        self._socket_keepalive_options = self._parse_socket_options(self.get_option('_socket_keepalive_options')) \
            if self._socket_keepalive and self.get_option('_socket_keepalive_options') else None
        self._socket_timeout = int(self.get_option('_socket_timeout')) \
            if self._socket_keepalive and self.get_option('_socket_timeout') else None
        self._ssl_ca_certs_file = self.get_option('_ssl_ca_certs_file')
        self._ssl_cert_file = self.get_option('_ssl_cert_file')
        self._ssl_cert_reqs = self.get_option('_ssl_cert_reqs')
        self._ssl_key_file = self.get_option('_ssl_key_file')

        if not HAS_REDIS:
            raise AnsibleError("The 'redis' python module (version 2.4.5 or newer) is required for the redis fact cache, 'pip install redis'")

        if self._encoding_errors not in self._encoding_errors_choices:
            raise AnsibleError("Unsupported value '%s' for Redis cache plugin parameter '_encoding_errors'" % (self._encoding_errors))

        self._cache = {}
        kw = {
            'decode_responses': self._decode_responses,
            'encoding_errors': self._encoding_errors,
            'encoding': self._encoding,
            'retry_on_timeout': self._retry_on_timeout,
            'socket_connect_timeout': self._socket_connect_timeout,
            'socket_keepalive_options': self._socket_keepalive_options,
            'socket_keepalive': self._socket_keepalive,
            'socket_timeout': self._socket_timeout,
        }

        # tls connection
        tlsprefix = 'tls://'
        if uri.startswith(tlsprefix):
            from os import access, R_OK
            from os.path import isfile
            import ssl

            if not self._ssl_cert_reqs.upper() in list(map(lambda x: x.name.split('_')[1], ssl.VerifyMode)):
                raise AnsibleError("Unsupported value '%s' for Redis cache plugin parameter '_ssl_cert_reqs'" % (self._ssl_cert_reqs))

            if self._ssl_ca_certs_file:
                if not isfile(self._ssl_ca_certs_file) and not access(self._ssl_ca_certs_file, R_OK):
                    raise AnsibleError("File %s doesn't exist or isn't readable for Redis cache plugin parameter '_ssl_ca_certs_file'" %
                                       self._ssl_ca_certs_file)

            if self._ssl_cert_file:
                if not isfile(self._ssl_cert_file) and not access(self._ssl_cert_file, R_OK):
                    raise AnsibleError("File %s doesn't exist or isn't readable for Redis cache plugin parameter '_ssl_cert_file'" % self._ssl_cert_file)

            if self._ssl_key_file:
                if not isfile(self._ssl_key_file) and not access(self._ssl_key_file, R_OK):
                    raise AnsibleError("File %s doesn't exist or isn't readable for Redis cache plugin parameter '_ssl_key_file'" % self._ssl_key_file)

            kw.update({
                'ssl': True,
                'ssl_keyfile': self._ssl_key_file,
                'ssl_certfile': self._ssl_cert_file,
                'ssl_cert_reqs': self._ssl_cert_reqs,
                'ssl_ca_certs': self._ssl_ca_certs_file
            })

            uri = uri[len(tlsprefix):]

        # redis sentinel connection
        if self._sentinel_service_name:
            self._db = self._get_sentinel_connection(uri, kw)
        # normal connection
        else:
            connection = self._parse_connection(self.re_url_conn, uri)
            self._db = StrictRedis(*connection, **kw)

        display.vv('Redis connection: %s' % self._db)
        display.vvv("Redis connection kwargs: %s" % ({**self._db.get_connection_kwargs(), **{'password': '****'}}))

    @staticmethod
    def _parse_connection(re_patt, uri):
        match = re_patt.match(uri)
        if not match:
            raise AnsibleError("Unable to parse connection string")
        return match.groups()

    def _parse_socket_options(self, options):
        if not self.re_socket_keepalive_opts.match(options):
            raise AnsibleError("Unable to parse Redis cache socket keepalive options string")
        import socket
        opts = {}
        for opt in options.split(','):
            key, value = opt.split(':')
            if key not in self._socket_keepalive_available_opts:
                raise AnsibleError("Option '%s' is not available for parameter '_socket_keepalive_options' for Redis cache plugin" % (key))
            opts[getattr(socket, key)] = int(value)
        return opts

    def _get_sentinel_connection(self, uri, kw):
        """
        get sentinel connection details from _uri
        """
        try:
            from redis.sentinel import Sentinel
        except ImportError:
            raise AnsibleError("The 'redis' python module (version 2.9.0 or newer) is required to use redis sentinel.")

        if ';' not in uri:
            raise AnsibleError('_uri does not have sentinel syntax.')

        # format: "localhost:26379;localhost2:26379;0:changeme"
        connections = uri.split(';')
        connection_args = connections.pop(-1)
        if len(connection_args) > 0:  # handle if no db nr is given
            connection_args = connection_args.split(':')
            kw['db'] = connection_args.pop(0)
            try:
                kw['password'] = connection_args.pop(0)
            except IndexError:
                pass  # password is optional

        sentinels = [self._parse_connection(self.re_sent_conn, shost) for shost in connections]
        display.vv('\nUsing redis sentinels: %s' % sentinels)
        scon = Sentinel(sentinels, **kw)
        try:
            return scon.master_for(self._sentinel_service_name, socket_timeout=0.2)
        except Exception as exc:
            raise AnsibleError('Could not connect to redis sentinel: %s' % to_native(exc))

    def _make_key(self, key):
        return self._prefix + key

    def get(self, key):

        if key not in self._cache:
            value = self._db.get(self._make_key(key))
            # guard against the key not being removed from the zset;
            # this could happen in cases where the timeout value is changed
            # between invocations
            if value is None:
                self.delete(key)
                raise KeyError
            self._cache[key] = json.loads(value, cls=AnsibleJSONDecoder)

        return self._cache.get(key)

    def set(self, key, value):

        value2 = json.dumps(value, cls=AnsibleJSONEncoder, sort_keys=True, indent=4)
        if self._timeout > 0:  # a timeout of 0 is handled as meaning 'never expire'
            self._db.setex(self._make_key(key), int(self._timeout), value2)
        else:
            self._db.set(self._make_key(key), value2)

        if VERSION[0] == 2:
            self._db.zadd(self._keys_set, time.time(), key)
        else:
            self._db.zadd(self._keys_set, {key: time.time()})
        self._cache[key] = value

    def _expire_keys(self):
        if self._timeout > 0:
            expiry_age = time.time() - self._timeout
            self._db.zremrangebyscore(self._keys_set, 0, expiry_age)

    def keys(self):
        self._expire_keys()
        return self._db.zrange(self._keys_set, 0, -1)

    def contains(self, key):
        self._expire_keys()
        return (self._db.zrank(self._keys_set, key) is not None)

    def delete(self, key):
        if key in self._cache:
            del self._cache[key]
        self._db.delete(self._make_key(key))
        self._db.zrem(self._keys_set, key)

    def flush(self):
        for key in list(self.keys()):
            self.delete(key)

    def copy(self):
        # TODO: there is probably a better way to do this in redis
        ret = dict([(k, self.get(k)) for k in self.keys()])
        return ret

    def __getstate__(self):
        return dict()

    def __setstate__(self, data):
        self.__init__()
