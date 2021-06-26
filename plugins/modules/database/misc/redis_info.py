#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Pavlo Bashynskyi (@levonet) <levonet@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: redis_info
short_description: Gather information about Redis servers
version_added: '0.2.0'
description:
- Gathers information and statistics about Redis servers.
options:
  login_host:
    description:
    - The host running the database.
    type: str
    default: localhost
  login_port:
    description:
    - The port to connect to.
    type: int
    default: 6379
  login_password:
    description:
    - The password used to authenticate with, when authentication is enabled for the Redis server.
    type: str
notes:
- Requires the redis-py Python package on the remote host. You can
  install it with pip (C(pip install redis)) or with a package manager.
  U(https://github.com/andymccurdy/redis-py)
seealso:
- module: community.general.redis
requirements: [ redis ]
author: "Pavlo Bashynskyi (@levonet)"
'''

EXAMPLES = r'''
- name: Get server information
  community.general.redis_info:
  register: result

- name: Print server information
  ansible.builtin.debug:
    var: result.info
'''

RETURN = r'''
info:
  description: The default set of server information sections U(https://redis.io/commands/info).
  returned: success
  type: dict
  sample: {
      "active_defrag_hits": 0,
      "active_defrag_key_hits": 0,
      "active_defrag_key_misses": 0,
      "active_defrag_misses": 0,
      "active_defrag_running": 0,
      "allocator_active": 932409344,
      "allocator_allocated": 932062792,
      "allocator_frag_bytes": 346552,
      "allocator_frag_ratio": 1.0,
      "allocator_resident": 947253248,
      "allocator_rss_bytes": 14843904,
      "allocator_rss_ratio": 1.02,
      "aof_current_rewrite_time_sec": -1,
      "aof_enabled": 0,
      "aof_last_bgrewrite_status": "ok",
      "aof_last_cow_size": 0,
      "aof_last_rewrite_time_sec": -1,
      "aof_last_write_status": "ok",
      "aof_rewrite_in_progress": 0,
      "aof_rewrite_scheduled": 0,
      "arch_bits": 64,
      "atomicvar_api": "atomic-builtin",
      "blocked_clients": 0,
      "client_recent_max_input_buffer": 4,
      "client_recent_max_output_buffer": 0,
      "cluster_enabled": 0,
      "config_file": "",
      "configured_hz": 10,
      "connected_clients": 4,
      "connected_slaves": 0,
      "db0": {
        "avg_ttl": 1945628530,
        "expires": 16,
        "keys": 3341411
      },
      "evicted_keys": 0,
      "executable": "/data/redis-server",
      "expired_keys": 9,
      "expired_stale_perc": 1.72,
      "expired_time_cap_reached_count": 0,
      "gcc_version": "9.2.0",
      "hz": 10,
      "instantaneous_input_kbps": 0.0,
      "instantaneous_ops_per_sec": 0,
      "instantaneous_output_kbps": 0.0,
      "keyspace_hits": 0,
      "keyspace_misses": 0,
      "latest_fork_usec": 0,
      "lazyfree_pending_objects": 0,
      "loading": 0,
      "lru_clock": 11603632,
      "master_repl_offset": 118831417,
      "master_replid": "0d904704e424e38c3cd896783e9f9d28d4836e5e",
      "master_replid2": "0000000000000000000000000000000000000000",
      "maxmemory": 0,
      "maxmemory_human": "0B",
      "maxmemory_policy": "noeviction",
      "mem_allocator": "jemalloc-5.1.0",
      "mem_aof_buffer": 0,
      "mem_clients_normal": 49694,
      "mem_clients_slaves": 0,
      "mem_fragmentation_bytes": 12355480,
      "mem_fragmentation_ratio": 1.01,
      "mem_not_counted_for_evict": 0,
      "mem_replication_backlog": 1048576,
      "migrate_cached_sockets": 0,
      "multiplexing_api": "epoll",
      "number_of_cached_scripts": 0,
      "os": "Linux 3.10.0-862.14.4.el7.x86_64 x86_64",
      "process_id": 1,
      "pubsub_channels": 0,
      "pubsub_patterns": 0,
      "rdb_bgsave_in_progress": 0,
      "rdb_changes_since_last_save": 671,
      "rdb_current_bgsave_time_sec": -1,
      "rdb_last_bgsave_status": "ok",
      "rdb_last_bgsave_time_sec": -1,
      "rdb_last_cow_size": 0,
      "rdb_last_save_time": 1588702236,
      "redis_build_id": "a31260535f820267",
      "redis_git_dirty": 0,
      "redis_git_sha1": 0,
      "redis_mode": "standalone",
      "redis_version": "999.999.999",
      "rejected_connections": 0,
      "repl_backlog_active": 1,
      "repl_backlog_first_byte_offset": 118707937,
      "repl_backlog_histlen": 123481,
      "repl_backlog_size": 1048576,
      "role": "master",
      "rss_overhead_bytes": -3051520,
      "rss_overhead_ratio": 1.0,
      "run_id": "8d252f66c3ef89bd60a060cf8dc5cfe3d511c5e4",
      "second_repl_offset": 118830003,
      "slave_expires_tracked_keys": 0,
      "sync_full": 0,
      "sync_partial_err": 0,
      "sync_partial_ok": 0,
      "tcp_port": 6379,
      "total_commands_processed": 885,
      "total_connections_received": 10,
      "total_net_input_bytes": 802709255,
      "total_net_output_bytes": 31754,
      "total_system_memory": 135029538816,
      "total_system_memory_human": "125.76G",
      "uptime_in_days": 53,
      "uptime_in_seconds": 4631778,
      "used_cpu_sys": 4.668282,
      "used_cpu_sys_children": 0.002191,
      "used_cpu_user": 4.21088,
      "used_cpu_user_children": 0.0,
      "used_memory": 931908760,
      "used_memory_dataset": 910774306,
      "used_memory_dataset_perc": "97.82%",
      "used_memory_human": "888.74M",
      "used_memory_lua": 37888,
      "used_memory_lua_human": "37.00K",
      "used_memory_overhead": 21134454,
      "used_memory_peak": 932015216,
      "used_memory_peak_human": "888.84M",
      "used_memory_peak_perc": "99.99%",
      "used_memory_rss": 944201728,
      "used_memory_rss_human": "900.46M",
      "used_memory_scripts": 0,
      "used_memory_scripts_human": "0B",
      "used_memory_startup": 791264
    }
'''

import traceback

REDIS_IMP_ERR = None
try:
    from redis import StrictRedis
    HAS_REDIS_PACKAGE = True
except ImportError:
    REDIS_IMP_ERR = traceback.format_exc()
    HAS_REDIS_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def redis_client(**client_params):
    return StrictRedis(**client_params)


# Module execution.
def main():
    module = AnsibleModule(
        argument_spec=dict(
            login_host=dict(type='str', default='localhost'),
            login_port=dict(type='int', default=6379),
            login_password=dict(type='str', no_log=True),
        ),
        supports_check_mode=True,
    )

    if not HAS_REDIS_PACKAGE:
        module.fail_json(msg=missing_required_lib('redis'), exception=REDIS_IMP_ERR)

    login_host = module.params['login_host']
    login_port = module.params['login_port']
    login_password = module.params['login_password']

    # Connect and check
    client = redis_client(host=login_host, port=login_port, password=login_password)
    try:
        client.ping()
    except Exception as e:
        module.fail_json(msg="unable to connect to database: %s" % to_native(e), exception=traceback.format_exc())

    info = client.info()
    module.exit_json(changed=False, info=info)


if __name__ == '__main__':
    main()
