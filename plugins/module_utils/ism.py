# coding: utf-8 -*-
# Copyright (c), Inspur isib-group, 2020

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from ansible_collections.community.general.plugins.module_utils.inspur_sdk import ism
    ism_temp = True
except ImportError:
    ism_temp = False
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six import iteritems


ism_provider_spec = {
    'host': dict(type='str'),
    'username': dict(type='str', fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
    'password': dict(type='str', fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True),
}
ism_argument_spec = {
    'provider': dict(type='dict', options=ism_provider_spec),
}
ism_top_spec = {
    'host': dict(type='str'),
    'username': dict(type='str'),
    'password': dict(type='str', no_log=True),
}
ism_argument_spec.update(ism_top_spec)


def load_params(module):
    """load_params"""
    provider = module.params.get('provider') or dict()
    for key, value in iteritems(provider):
        if key in ism_argument_spec:
            if module.params.get(key) is None and value is not None:
                module.params[key] = value


def get_connection(module):
    """get_connection"""
    load_params(module)
    dict_cpu = module.params
    if not ism_temp:
        module.fail_json(msg='inspur_sdk must be installed to use this module')
    result = ism.main(dict_cpu)
    return result
