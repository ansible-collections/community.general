# Copyright (c) 2012-2015, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

import pytest

pytest.importorskip("memcache")

from ansible.plugins.loader import cache_loader
from ansible_collections.community.general.plugins.cache.memcached import CacheModule as MemcachedCache


def test_memcached_cachemodule():
    assert isinstance(cache_loader.get("community.general.memcached"), MemcachedCache)
