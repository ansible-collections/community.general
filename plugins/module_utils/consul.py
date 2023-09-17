# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def get_consul_url(configuration):
    return '%s://%s:%s/v1' % (configuration.scheme,
                              configuration.host, configuration.port)


def get_auth_headers(configuration):
    if configuration.token is None:
        return {}
    else:
        return {'X-Consul-Token': configuration.token}


class RequestError(Exception):
    pass


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError('%d %s' % (response.status_code, response.content))
