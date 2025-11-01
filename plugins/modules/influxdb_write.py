#!/usr/bin/python
# Copyright (c) 2017, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: influxdb_write
short_description: Write data points into InfluxDB
description:
  - Write data points into InfluxDB.
author: "René Moser (@resmo)"
requirements:
  - "influxdb >= 0.9"
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  data_points:
    description:
      - Data points as dict to write into the database.
    required: true
    type: list
    elements: dict
  database_name:
    description:
      - Name of the database.
    required: true
    type: str
extends_documentation_fragment:
  - community.general.influxdb
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Write points into database
  community.general.influxdb_write:
    hostname: "{{influxdb_ip_address}}"
    database_name: "{{influxdb_database_name}}"
    data_points:
      - measurement: connections
        tags:
          host: server01
          region: us-west
        time: "{{ ansible_date_time.iso8601 }}"
        fields:
          value: 2000
      - measurement: connections
        tags:
          host: server02
          region: us-east
        time: "{{ ansible_date_time.iso8601 }}"
        fields:
          value: 3000
"""

RETURN = r"""
# only defaults
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.influxdb import InfluxDb


class AnsibleInfluxDBWrite(InfluxDb):
    def write_data_point(self, data_points):
        client = self.connect_to_influxdb()

        try:
            client.write_points(data_points)
        except Exception as e:
            self.module.fail_json(msg=to_native(e))


def main():
    argument_spec = InfluxDb.influxdb_argument_spec()
    argument_spec.update(
        data_points=dict(required=True, type="list", elements="dict"),
        database_name=dict(required=True, type="str"),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    influx = AnsibleInfluxDBWrite(module)
    data_points = module.params.get("data_points")
    influx.write_data_point(data_points)
    module.exit_json(changed=True)


if __name__ == "__main__":
    main()
