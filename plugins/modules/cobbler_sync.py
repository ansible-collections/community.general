#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Dag Wieers (dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: cobbler_sync
short_description: Sync Cobbler
description:
- Sync Cobbler to commit changes.
options:
  host:
    description:
    - The name or IP address of the Cobbler system.
    default: 127.0.0.1
    type: str
  port:
    description:
    - Port number to be used for REST connection.
    - The default value depends on parameter C(use_ssl).
    type: int
  username:
    description:
    - The username to log in to Cobbler.
    default: cobbler
    type: str
  password:
    description:
    - The password to log in to Cobbler.
    type: str
  use_ssl:
    description:
    - If C(false), an HTTP connection will be used instead of the default HTTPS connection.
    type: bool
    default: true
  validate_certs:
    description:
    - If C(false), SSL certificates will not be validated.
    - This should only set to C(false) when used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
author:
- Dag Wieers (@dagwieers)
todo:
notes:
- Concurrently syncing Cobbler is bound to fail with weird errors.
- On python 2.7.8 and older (i.e. on RHEL7) you may need to tweak the python behaviour to disable certificate validation.
  More information at L(Certificate verification in Python standard library HTTP clients,https://access.redhat.com/articles/2039753).
'''

EXAMPLES = r'''
- name: Commit Cobbler changes
  community.general.cobbler_sync:
    host: cobbler01
    username: cobbler
    password: MySuperSecureP4sswOrd
  run_once: true
  delegate_to: localhost
'''

RETURN = r'''
# Default return values
'''

import datetime
import ssl

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import xmlrpc_client
from ansible.module_utils.common.text.converters import to_text


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', default='127.0.0.1'),
            port=dict(type='int'),
            username=dict(type='str', default='cobbler'),
            password=dict(type='str', no_log=True),
            use_ssl=dict(type='bool', default=True),
            validate_certs=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    username = module.params['username']
    password = module.params['password']
    port = module.params['port']
    use_ssl = module.params['use_ssl']
    validate_certs = module.params['validate_certs']

    module.params['proto'] = 'https' if use_ssl else 'http'
    if not port:
        module.params['port'] = '443' if use_ssl else '80'

    result = dict(
        changed=True,
    )

    start = datetime.datetime.utcnow()

    ssl_context = None
    if not validate_certs:
        try:
            ssl_context = ssl._create_unverified_context()
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = ssl._create_unverified_context

    url = '{proto}://{host}:{port}/cobbler_api'.format(**module.params)
    if ssl_context:
        conn = xmlrpc_client.ServerProxy(url, context=ssl_context)
    else:
        conn = xmlrpc_client.Server(url)

    try:
        token = conn.login(username, password)
    except xmlrpc_client.Fault as e:
        module.fail_json(msg="Failed to log in to Cobbler '{url}' as '{username}'. {error}".format(url=url, error=to_text(e), **module.params))
    except Exception as e:
        module.fail_json(msg="Connection to '{url}' failed. {error}".format(url=url, error=to_text(e)))

    if not module.check_mode:
        try:
            conn.sync(token)
        except Exception as e:
            module.fail_json(msg="Failed to sync Cobbler. {error}".format(error=to_text(e)))

    elapsed = datetime.datetime.utcnow() - start
    module.exit_json(elapsed=elapsed.seconds, **result)


if __name__ == '__main__':
    main()
