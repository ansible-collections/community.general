#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: statsd
short_description: Send metrics to StatsD
description:
  - The C(statsd) module sends metrics to StatsD
  - Supported metric types are C(counter) and C(gauge)
  - Currently unupported metric types are C(timer), C(set), and C(gaugedelta)
author: "Mark Mercado (@mamercad)"
options:
  state:
    type: str
    description:
      - State of the check, only C(present) makes sense.
    choices: ["present"]
    default: present
  host:
    type: str
    default: localhost
    description:
      - StatsD host (hostname or IP).
  port:
    type: int
    default: 8125
    description:
      - StatsD port.
  protocol:
    type: str
    default: udp
    choices: ["udp", "tcp"]
    description:
      - StatsD protocol.
  timeout:
    type: float
    default: 1.0
    description:
      - StatsD timeout (only applicable if protocol is C(tcp)).
  metric:
    type: str
    required: true
    description:
      - StatsD metric name.
  metric_type:
    type: str
    required: true
    description:
      - StatsD metric value.
  mtype:
    type: str
    required: true
    choices: ["counter", "gauge"]
    description:
      - StatsD metric type.
  value:
    type: int
    required: true
    description:
      - StatsD metric value.
  delta:
    type: bool
    required: false
    description:
      - If the metric is of type C(gauge), change the value by C(delta).
'''

EXAMPLES = '''
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
'''

import traceback
from statsd import StatsClient, TCPStatsClient

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.urls import fetch_url


def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present']),
            host=dict(type=str, default='localhost'),
            port=dict(type=int, default=8125),
            protocol=dict(type=str, default='udp', choices=['udp', 'tcp']),
            timeout=dict(type=float, default=1.0),
            metric=dict(type=str, required=True),
            mtype=dict(type=str, choices=['counter', 'gauge']),
            value=dict(type=str, required=True),
       ),
        supports_check_mode=True
    )

    host = module.params.get('host')
    port = module.params.get('port')
    protocol = module.params.get('protocol')
    timeout = module.params.get('timeout')
    metric = module.params.get('metric')
    value = module.params.get('value')
    mtype = module.params.get('type')

    result = dict()

    try:
      if protocol == 'udp':
        statsd = StatsClient(host=host, port=port, prefix=None, maxudpsize=512, ipv6=False)
      elif protocol == 'tcp':
        statsd = TCPStatsClient(host=host, port=port, timeout=timeout, prefix=None, ipv6=False)

      if mtype == 'counter':
          statsd.incr(metric)


    except Exception as exc:
        module.fail_json(error='Failed to sending to StatsD %s' % to_native(exc), exception=traceback.format_exc(), **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
