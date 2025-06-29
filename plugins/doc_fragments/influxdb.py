# -*- coding: utf-8 -*-

# Copyright (c) 2017, Ansible Project
# Copyright (c) 2017, Abhijeet Kasurde (akasurde@redhat.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Parameters for influxdb modules
    DOCUMENTATION = r"""
options:
  hostname:
    description:
      - The hostname or IP address on which InfluxDB server is listening.
    type: str
    default: localhost
  username:
    description:
      - Username that is used to authenticate against InfluxDB server.
    type: str
    default: root
    aliases: [login_username]
  password:
    description:
      - Password that is used to authenticate against InfluxDB server.
    type: str
    default: root
    aliases: [login_password]
  port:
    description:
      - The port on which InfluxDB server is listening.
    type: int
    default: 8086
  path:
    description:
      - The path on which InfluxDB server is accessible.
      - Only available when using python-influxdb >= 5.1.0.
    type: str
    default: ''
    version_added: '0.2.0'
  validate_certs:
    description:
      - If set to V(false), the SSL certificates are not validated.
      - This should only set to V(false) used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
  ssl:
    description:
      - Use https instead of http to connect to InfluxDB server.
    type: bool
    default: false
  timeout:
    description:
      - Number of seconds Requests waits for client to establish a connection.
    type: int
  retries:
    description:
      - Number of retries client performs before aborting.
      - V(0) indicates try until success.
      - Only available when using C(python-influxdb) >= 4.1.0.
    type: int
    default: 3
  use_udp:
    description:
      - Use UDP to connect to InfluxDB server.
    type: bool
    default: false
  udp_port:
    description:
      - UDP port to connect to InfluxDB server.
    type: int
    default: 4444
  proxies:
    description:
      - HTTP(S) proxy to use for Requests to connect to InfluxDB server.
    type: dict
    default: {}
"""
