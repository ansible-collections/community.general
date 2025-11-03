# Copyright (c) 2012-2015, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

import pytest

pytest.importorskip("redis")

from ansible.plugins.loader import cache_loader
from ansible_collections.community.general.plugins.cache.redis import CacheModule as RedisCache


def test_redis_cachemodule():
    # The _uri option is required for the redis plugin
    connection = "127.0.0.1:6379:1"
    assert isinstance(cache_loader.get("community.general.redis", **{"_uri": connection}), RedisCache)


def test_redis_cachemodule_2():
    # The _uri option is required for the redis plugin
    connection = "[::1]:6379:1"
    assert isinstance(cache_loader.get("community.general.redis", **{"_uri": connection}), RedisCache)
