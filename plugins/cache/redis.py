# (c) 2014, Brian Coca, Josh Drake, et al
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Unknown (!UNKNOWN)
    cache: redis
    short_description: Use Redis DB for cache
    description:
        - This cache uses JSON formatted, per host records saved in Redis.
    requirements:
      - redis>=2.4.5 (python lib)
    options:
      _uri:
        description:
          - A colon separated string of connection information for Redis.
          - The format is C(host:port:db:password), for example C(localhost:6379:0:changeme).
          - To use encryption in transit, prefix the connection with C(tls://), as in C(tls://localhost:6379:0:changeme).
          - To use redis sentinel, use separator C(;), for example C(localhost:26379;localhost:26379;0:changeme). Requires redis>=2.9.0.
        required: True
        env:
          - name: ANSIBLE_CACHE_PLUGIN_CONNECTION
        ini:
          - key: fact_caching_connection
            section: defaults
      _prefix:
        description: User defined prefix to use when creating the DB entries
        default: ansible_facts
        env:
          - name: ANSIBLE_CACHE_PLUGIN_PREFIX
        ini:
          - key: fact_caching_prefix
            section: defaults
      _keyset_name:
        description: User defined name for cache keyset name.
        default: ansible_cache_keys
        env:
          - name: ANSIBLE_CACHE_REDIS_KEYSET_NAME
        ini:
          - key: fact_caching_redis_keyset_name
            section: defaults
        version_added: 1.3.0
      _sentinel_service_name:
        description: The redis sentinel service name (or referenced as cluster name).
        env:
          - name: ANSIBLE_CACHE_REDIS_SENTINEL
        ini:
          - key: fact_caching_redis_sentinel
            section: defaults
        version_added: 1.3.0
      _timeout:
        default: 86400
        description: Expiration timeout in seconds for the cache plugin data. Set to 0 to never expire
        env:
          - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
        ini:
          - key: fact_caching_timeout
            section: defaults
        type: integer
'''

import time
import json

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
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

    def __init__(self, *args, **kwargs):
        uri = ''

        try:
            super(CacheModule, self).__init__(*args, **kwargs)
            if self.get_option('_uri'):
                uri = self.get_option('_uri')
            self._timeout = float(self.get_option('_timeout'))
            self._prefix = self.get_option('_prefix')
            self._keys_set = self.get_option('_keyset_name')
            self._sentinel_service_name = self.get_option('_sentinel_service_name')
        except KeyError:
            display.deprecated('Rather than importing CacheModules directly, '
                               'use ansible.plugins.loader.cache_loader',
                               version='2.0.0', collection_name='community.general')  # was Ansible 2.12
            if C.CACHE_PLUGIN_CONNECTION:
                uri = C.CACHE_PLUGIN_CONNECTION
            self._timeout = float(C.CACHE_PLUGIN_TIMEOUT)
            self._prefix = C.CACHE_PLUGIN_PREFIX
            self._keys_set = 'ansible_cache_keys'

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
            connection = uri.split(':')
            self._db = StrictRedis(*connection, **kw)

        display.vv('Redis connection: %s' % self._db)

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
        if len(connection_args) > 0:  # hanle if no db nr is given
            connection_args = connection_args.split(':')
            kw['db'] = connection_args.pop(0)
            try:
                kw['password'] = connection_args.pop(0)
            except IndexError:
                pass  # password is optional

        sentinels = [tuple(shost.split(':')) for shost in connections]
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
        for key in self.keys():
            self.delete(key)

    def copy(self):
        # TODO: there is probably a better way to do this in redis
        ret = dict()
        for key in self.keys():
            ret[key] = self.get(key)
        return ret

    def __getstate__(self):
        return dict()

    def __setstate__(self, data):
        self.__init__()
