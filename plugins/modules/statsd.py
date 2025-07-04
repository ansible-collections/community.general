#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: statsd
short_description: Send metrics to StatsD
version_added: 2.1.0
description:
  - The C(statsd) module sends metrics to StatsD.
  - For more information, see U(https://statsd-metrics.readthedocs.io/en/latest/).
  - Supported metric types are V(counter) and V(gauge). Currently unupported metric types are V(timer), V(set), and V(gaugedelta).
author: "Mark Mercado (@mamercad)"
requirements:
  - statsd
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    type: str
    description:
      - State of the check, only V(present) makes sense.
    choices: ["present"]
    default: present
  host:
    type: str
    default: localhost
    description:
      - StatsD host (hostname or IP) to send metrics to.
  port:
    type: int
    default: 8125
    description:
      - The port on O(host) which StatsD is listening on.
  protocol:
    type: str
    default: udp
    choices: ["udp", "tcp"]
    description:
      - The transport protocol to send metrics over.
  timeout:
    type: float
    default: 1.0
    description:
      - Sender timeout, only applicable if O(protocol) is V(tcp).
  metric:
    type: str
    required: true
    description:
      - The name of the metric.
  metric_type:
    type: str
    required: true
    choices: ["counter", "gauge"]
    description:
      - The type of metric.
  metric_prefix:
    type: str
    description:
      - The prefix to add to the metric.
    default: ''
  value:
    type: int
    required: true
    description:
      - The value of the metric.
  delta:
    type: bool
    default: false
    description:
      - If the metric is of type V(gauge), change the value by O(delta).
"""

EXAMPLES = r"""
- name: Increment the metric my_counter by 1
  community.general.statsd:
    host: localhost
    port: 9125
    protocol: tcp
    metric: my_counter
    metric_type: counter
    value: 1

- name: Set the gauge my_gauge to 7
  community.general.statsd:
    host: localhost
    port: 9125
    protocol: tcp
    metric: my_gauge
    metric_type: gauge
    value: 7
"""


from ansible.module_utils.basic import (AnsibleModule, missing_required_lib)

try:
    from statsd import StatsClient, TCPStatsClient
    HAS_STATSD = True
except ImportError:
    HAS_STATSD = False


def udp_statsd_client(**client_params):
    return StatsClient(**client_params)


def tcp_statsd_client(**client_params):
    return TCPStatsClient(**client_params)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present']),
            host=dict(type='str', default='localhost'),
            port=dict(type='int', default=8125),
            protocol=dict(type='str', default='udp', choices=['udp', 'tcp']),
            timeout=dict(type='float', default=1.0),
            metric=dict(type='str', required=True),
            metric_type=dict(type='str', required=True, choices=['counter', 'gauge']),
            metric_prefix=dict(type='str', default=''),
            value=dict(type='int', required=True),
            delta=dict(type='bool', default=False),
        ),
        supports_check_mode=False
    )

    if not HAS_STATSD:
        module.fail_json(msg=missing_required_lib('statsd'))

    host = module.params.get('host')
    port = module.params.get('port')
    protocol = module.params.get('protocol')
    timeout = module.params.get('timeout')
    metric = module.params.get('metric')
    metric_type = module.params.get('metric_type')
    metric_prefix = module.params.get('metric_prefix')
    value = module.params.get('value')
    delta = module.params.get('delta')

    if protocol == 'udp':
        client = udp_statsd_client(host=host, port=port, prefix=metric_prefix, maxudpsize=512, ipv6=False)
    elif protocol == 'tcp':
        client = tcp_statsd_client(host=host, port=port, timeout=timeout, prefix=metric_prefix, ipv6=False)

    metric_name = '%s/%s' % (metric_prefix, metric) if metric_prefix else metric
    metric_display_value = '%s (delta=%s)' % (value, delta) if metric_type == 'gauge' else value

    try:
        if metric_type == 'counter':
            client.incr(metric, value)
        elif metric_type == 'gauge':
            client.gauge(metric, value, delta=delta)

    except Exception as exc:
        module.fail_json(msg='Failed sending to StatsD %s' % str(exc))

    finally:
        if protocol == 'tcp':
            client.close()

    module.exit_json(msg="Sent %s %s -> %s to StatsD" % (metric_type, metric_name, str(metric_display_value)), changed=True)


if __name__ == '__main__':
    main()
