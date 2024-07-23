# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import missing_required_lib
__metaclass__ = type

import traceback

REDIS_IMP_ERR = None
try:
    from redis import Redis
    from redis import __version__ as redis_version
    HAS_REDIS_PACKAGE = True
    REDIS_IMP_ERR = None
except ImportError:
    REDIS_IMP_ERR = traceback.format_exc()
    HAS_REDIS_PACKAGE = False

try:
    import certifi
    HAS_CERTIFI_PACKAGE = True
    CERTIFI_IMPORT_ERROR = None
except ImportError:
    CERTIFI_IMPORT_ERROR = traceback.format_exc()
    HAS_CERTIFI_PACKAGE = False


def fail_imports(module, needs_certifi=True):
    errors = []
    traceback = []
    if not HAS_REDIS_PACKAGE:
        errors.append(missing_required_lib('redis'))
        traceback.append(REDIS_IMP_ERR)
    if not HAS_CERTIFI_PACKAGE and needs_certifi:
        errors.append(missing_required_lib('certifi'))
        traceback.append(CERTIFI_IMPORT_ERROR)
    if errors:
        module.fail_json(msg='\n'.join(errors), traceback='\n'.join(traceback))


def redis_auth_argument_spec(tls_default=True):
    return dict(
        login_host=dict(type='str',
                        default='localhost',),
        login_user=dict(type='str'),
        login_password=dict(type='str',
                            no_log=True
                            ),
        login_port=dict(type='int', default=6379),
        tls=dict(type='bool',
                 default=tls_default),
        validate_certs=dict(type='bool',
                            default=True
                            ),
        ca_certs=dict(type='str'),
        client_cert_file=dict(type='str'),
        client_key_file=dict(type='str'),
    )


def redis_auth_params(module):
    login_host = module.params['login_host']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_port = module.params['login_port']
    tls = module.params['tls']
    validate_certs = 'required' if module.params['validate_certs'] else None
    ca_certs = module.params['ca_certs']
    if tls and ca_certs is None:
        ca_certs = str(certifi.where())
    client_cert_file = module.params['client_cert_file']
    client_key_file = module.params['client_key_file']
    if tuple(map(int, redis_version.split('.'))) < (3, 4, 0) and login_user is not None:
        module.fail_json(
            msg='The option `username` in only supported with redis >= 3.4.0.')
    params = {'host': login_host,
              'port': login_port,
              'password': login_password,
              'ssl_ca_certs': ca_certs,
              'ssl_certfile': client_cert_file,
              'ssl_keyfile': client_key_file,
              'ssl_cert_reqs': validate_certs,
              'ssl': tls}
    if login_user is not None:
        params['username'] = login_user
    return params


class RedisAnsible(object):
    '''Base class for Redis module'''

    def __init__(self, module):
        self.module = module
        self.connection = self._connect()

    def _connect(self):
        try:
            return Redis(**redis_auth_params(self.module))
        except Exception as e:
            self.module.fail_json(msg='{0}'.format(str(e)))
        return None
