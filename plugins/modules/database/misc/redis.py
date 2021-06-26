#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis
short_description: Various redis commands, replica and flush
description:
   - Unified utility to interact with redis instances.
options:
    command:
        description:
            - The selected redis command
            - C(config) ensures a configuration setting on an instance.
            - C(flush) flushes all the instance or a specified db.
            - C(replica) sets a redis instance in replica or master mode. (C(slave) is an alias for C(replica).)
        choices: [ config, flush, replica, slave ]
        type: str
    login_password:
        description:
            - The password used to authenticate with (usually not used)
        type: str
    login_host:
        description:
            - The host running the database
        default: localhost
        type: str
    login_port:
        description:
            - The port to connect to
        default: 6379
        type: int
    master_host:
        description:
            - The host of the master instance [replica command]
        type: str
    master_port:
        description:
            - The port of the master instance [replica command]
        type: int
    replica_mode:
        description:
            - The mode of the redis instance [replica command]
            - C(slave) is an alias for C(replica).
        default: replica
        choices: [ master, replica, slave ]
        type: str
        aliases:
            - slave_mode
    db:
        description:
            - The database to flush (used in db mode) [flush command]
        type: int
    flush_mode:
        description:
            - Type of flush (all the dbs in a redis instance or a specific one)
              [flush command]
        default: all
        choices: [ all, db ]
        type: str
    name:
        description:
            - A redis config key.
        type: str
    value:
        description:
            - A redis config value. When memory size is needed, it is possible
              to specify it in the usal form of 1KB, 2M, 400MB where the base is 1024.
              Units are case insensitive i.e. 1m = 1mb = 1M = 1MB.
        type: str

notes:
   - Requires the redis-py Python package on the remote host. You can
     install it with pip (pip install redis) or with a package manager.
     https://github.com/andymccurdy/redis-py
   - If the redis master instance we are making replica of is password protected
     this needs to be in the redis.conf in the masterauth variable

seealso:
    - module: community.general.redis_info
requirements: [ redis ]
author: "Xabier Larrakoetxea (@slok)"
'''

EXAMPLES = '''
- name: Set local redis instance to be a replica of melee.island on port 6377
  community.general.redis:
    command: replica
    master_host: melee.island
    master_port: 6377

- name: Deactivate replica mode
  community.general.redis:
    command: replica
    replica_mode: master

- name: Flush all the redis db
  community.general.redis:
    command: flush
    flush_mode: all

- name: Flush only one db in a redis instance
  community.general.redis:
    command: flush
    db: 1
    flush_mode: db

- name: Configure local redis to have 10000 max clients
  community.general.redis:
    command: config
    name: maxclients
    value: 10000

- name: Configure local redis maxmemory to 4GB
  community.general.redis:
    command: config
    name: maxmemory
    value: 4GB

- name: Configure local redis to have lua time limit of 100 ms
  community.general.redis:
    command: config
    name: lua-time-limit
    value: 100
'''

import traceback

REDIS_IMP_ERR = None
try:
    import redis
except ImportError:
    REDIS_IMP_ERR = traceback.format_exc()
    redis_found = False
else:
    redis_found = True

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.formatters import human_to_bytes
from ansible.module_utils.common.text.converters import to_native
import re


# Redis module specific support methods.
def set_replica_mode(client, master_host, master_port):
    try:
        return client.slaveof(master_host, master_port)
    except Exception:
        return False


def set_master_mode(client):
    try:
        return client.slaveof()
    except Exception:
        return False


def flush(client, db=None):
    try:
        if not isinstance(db, int):
            return client.flushall()
        else:
            # The passed client has been connected to the database already
            return client.flushdb()
    except Exception:
        return False


# Module execution.
def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str', choices=['config', 'flush', 'replica', 'slave']),
            login_password=dict(type='str', no_log=True),
            login_host=dict(type='str', default='localhost'),
            login_port=dict(type='int', default=6379),
            master_host=dict(type='str'),
            master_port=dict(type='int'),
            replica_mode=dict(type='str', default='replica', choices=['master', 'replica', 'slave'], aliases=["slave_mode"]),
            db=dict(type='int'),
            flush_mode=dict(type='str', default='all', choices=['all', 'db']),
            name=dict(type='str'),
            value=dict(type='str')
        ),
        supports_check_mode=True,
    )

    if not redis_found:
        module.fail_json(msg=missing_required_lib('redis'), exception=REDIS_IMP_ERR)

    login_password = module.params['login_password']
    login_host = module.params['login_host']
    login_port = module.params['login_port']
    command = module.params['command']
    if command == "slave":
        command = "replica"

    # Replica Command section -----------
    if command == "replica":
        master_host = module.params['master_host']
        master_port = module.params['master_port']
        mode = module.params['replica_mode']
        if mode == "slave":
            mode = "replica"

        # Check if we have all the data
        if mode == "replica":  # Only need data if we want to be replica
            if not master_host:
                module.fail_json(msg='In replica mode master host must be provided')

            if not master_port:
                module.fail_json(msg='In replica mode master port must be provided')

        # Connect and check
        r = redis.StrictRedis(host=login_host, port=login_port, password=login_password)
        try:
            r.ping()
        except Exception as e:
            module.fail_json(msg="unable to connect to database: %s" % to_native(e), exception=traceback.format_exc())

        # Check if we are already in the mode that we want
        info = r.info()
        if mode == "master" and info["role"] == "master":
            module.exit_json(changed=False, mode=mode)

        elif mode == "replica" and info["role"] == "slave" and info["master_host"] == master_host and info["master_port"] == master_port:
            status = dict(
                status=mode,
                master_host=master_host,
                master_port=master_port,
            )
            module.exit_json(changed=False, mode=status)
        else:
            # Do the stuff
            # (Check Check_mode before commands so the commands aren't evaluated
            # if not necessary)
            if mode == "replica":
                if module.check_mode or set_replica_mode(r, master_host, master_port):
                    info = r.info()
                    status = {
                        'status': mode,
                        'master_host': master_host,
                        'master_port': master_port,
                    }
                    module.exit_json(changed=True, mode=status)
                else:
                    module.fail_json(msg='Unable to set replica mode')

            else:
                if module.check_mode or set_master_mode(r):
                    module.exit_json(changed=True, mode=mode)
                else:
                    module.fail_json(msg='Unable to set master mode')

    # flush Command section -----------
    elif command == "flush":
        db = module.params['db']
        mode = module.params['flush_mode']

        # Check if we have all the data
        if mode == "db":
            if db is None:
                module.fail_json(msg="In db mode the db number must be provided")

        # Connect and check
        r = redis.StrictRedis(host=login_host, port=login_port, password=login_password, db=db)
        try:
            r.ping()
        except Exception as e:
            module.fail_json(msg="unable to connect to database: %s" % to_native(e), exception=traceback.format_exc())

        # Do the stuff
        # (Check Check_mode before commands so the commands aren't evaluated
        # if not necessary)
        if mode == "all":
            if module.check_mode or flush(r):
                module.exit_json(changed=True, flushed=True)
            else:  # Flush never fails :)
                module.fail_json(msg="Unable to flush all databases")

        else:
            if module.check_mode or flush(r, db):
                module.exit_json(changed=True, flushed=True, db=db)
            else:  # Flush never fails :)
                module.fail_json(msg="Unable to flush '%d' database" % db)
    elif command == 'config':
        name = module.params['name']

        try:  # try to parse the value as if it were the memory size
            if re.match(r'^\s*(\d*\.?\d*)\s*([A-Za-z]+)?\s*$', module.params['value'].upper()):
                value = str(human_to_bytes(module.params['value'].upper()))
            else:
                value = module.params['value']
        except ValueError:
            value = module.params['value']

        r = redis.StrictRedis(host=login_host, port=login_port, password=login_password)

        try:
            r.ping()
        except Exception as e:
            module.fail_json(msg="unable to connect to database: %s" % to_native(e), exception=traceback.format_exc())

        try:
            old_value = r.config_get(name)[name]
        except Exception as e:
            module.fail_json(msg="unable to read config: %s" % to_native(e), exception=traceback.format_exc())
        changed = old_value != value

        if module.check_mode or not changed:
            module.exit_json(changed=changed, name=name, value=value)
        else:
            try:
                r.config_set(name, value)
            except Exception as e:
                module.fail_json(msg="unable to write config: %s" % to_native(e), exception=traceback.format_exc())
            module.exit_json(changed=changed, name=name, value=value)
    else:
        module.fail_json(msg='A valid command must be provided')


if __name__ == '__main__':
    main()
