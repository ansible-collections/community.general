# -*- coding: utf-8 -*-
# Copyright (c) 2014, Brian Coca, Josh Drake, et al
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: redis
short_description: Use Redis DB for cache
description:
  - This cache uses JSON formatted, per host records saved in Redis.
requirements:
  - redis>=2.4.5 (python lib)
options:
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
  _prefix:
    description: User defined prefix to use when creating the DB entries.
    type: string
    default: ansible_facts
    env:
      - name: ANSIBLE_CACHE_PLUGIN_PREFIX
    ini:
      - key: fact_caching_prefix
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
  _sentinel_service_name:
    description: The redis sentinel service name (or referenced as cluster name).
    type: string
    env:
      - name: ANSIBLE_CACHE_REDIS_SENTINEL
    ini:
      - key: fact_caching_redis_sentinel
        section: defaults
    version_added: 1.3.0
  _timeout:
    default: 86400
    type: integer
        # TODO: determine whether it is OK to change to: type: float
    description: Expiration timeout in seconds for the cache plugin data. Set to 0 to never expire.
    env:
      - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
    ini:
      - key: fact_caching_timeout
        section: defaults
"""

import re
import time
import json

from ansible.errors import AnsibleError
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
    re_url_conn = re.compile(r'^([^:]+|\[[^]]+\]):(\d+):(\d+)(?::(.*))?$')
    re_sent_conn = re.compile(r'^(.*):(\d+)$')

    def __init__(self, *args, **kwargs):
        uri = ''

        super(CacheModule, self).__init__(*args, **kwargs)
        if self.get_option('_uri'):
            uri = self.get_option('_uri')
        self._timeout = float(self.get_option('_timeout'))
        self._prefix = self.get_option('_prefix')
        self._keys_set = self.get_option('_keyset_name')
        self._sentinel_service_name = self.get_option('_sentinel_service_name')

        if not HAS_REDIS:
            raise AnsibleError("The 'redis' python module (version 2.4.5 or newer) is required for the redis fact cache, 'pip install redis'")

        self._cache = {}
        kw = {}

        # tls connection
        tlsprefix = 'tls://'
        if uri.startswith(tlsprefix):
            kw['ssl'] = True
            uri = uri[len(tlsprefix):]

        # redis sentinel connection
        if self._sentinel_service_name:
            self._db = self._get_sentinel_connection(uri, kw)
        # normal connection
        else:
            connection = self._parse_connection(self.re_url_conn, uri)
            self._db = StrictRedis(*connection, **kw)

        display.vv(f'Redis connection: {self._db}')

    @staticmethod
    def _parse_connection(re_patt, uri):
        match = re_patt.match(uri)
        if not match:
            raise AnsibleError("Unable to parse connection string")
        return match.groups()

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
        display.vv(f'\nUsing redis sentinels: {sentinels}')
        scon = Sentinel(sentinels, **kw)
        try:
            return scon.master_for(self._sentinel_service_name, socket_timeout=0.2)
        except Exception as exc:
            raise AnsibleError(f'Could not connect to redis sentinel: {exc}')

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
        ret = {k: self.get(k) for k in self.keys()}
        return ret

    def __getstate__(self):
        return dict()

    def __setstate__(self, data):
        self.__init__()
