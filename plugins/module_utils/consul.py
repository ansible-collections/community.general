# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def get_consul_url(configuration):
    return "%s://%s:%s/v1" % (
        configuration.scheme,
        configuration.host,
        configuration.port,
    )


def get_auth_headers(configuration):
    if configuration.token is None:
        return {}
    else:
        return {"X-Consul-Token": configuration.token}


class RequestError(Exception):
    pass


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError("%d %s" % (response.status_code, response.content))


def auth_argument_spec(token_option_name="token"):
    args = dict(
        host=dict(default="localhost"),
        port=dict(type="int", default=8500),
        scheme=dict(choices=["http", "https"], default="http"),
        validate_certs=dict(type="bool", default=True),
    )
    args[token_option_name] = dict(no_log=True)
    return args


def auth_options(module, token_option_name="token"):
    options = dict(
        host=module.params.get("host"),
        port=module.params.get("port"),
        scheme=module.params.get("scheme"),
        validate_certs=module.params.get("validate_certs"),
    )
    options[token_option_name] = module.params.get(token_option_name)
    return options
