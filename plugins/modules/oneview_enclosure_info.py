#!/usr/bin/python

# Copyright (c) 2016-2017, Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: oneview_enclosure_info
short_description: Retrieve information about one or more Enclosures
description:
  - Retrieve information about one or more of the Enclosures from OneView.
requirements:
  - hpOneView >= 2.0.1
author:
  - Felipe Bulsoni (@fgbulsoni)
  - Thiago Miotto (@tmiotto)
  - Adriane Cardozo (@adriane-cardozo)
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  name:
    description:
      - Enclosure name.
    type: str
  options:
    description:
      - 'List with options to gather additional information about an Enclosure and related resources. Options allowed: V(script),
        V(environmentalConfiguration), and V(utilization). For the option V(utilization), you can provide specific parameters.'
    type: list
    elements: raw

extends_documentation_fragment:
  - community.general.oneview
  - community.general.oneview.factsparams
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: Gather information about all Enclosures
  community.general.oneview_enclosure_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Enclosures
  ansible.builtin.debug:
    msg: "{{ result.enclosures }}"

- name: Gather paginated, filtered and sorted information about Enclosures
  community.general.oneview_enclosure_info:
    params:
      start: 0
      count: 3
      sort: name:descending
      filter: status=OK
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about paginated, filtered and sorted list of Enclosures
  ansible.builtin.debug:
    msg: "{{ result.enclosures }}"

- name: Gather information about an Enclosure by name
  community.general.oneview_enclosure_info:
    name: Enclosure-Name
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Enclosure found by name
  ansible.builtin.debug:
    msg: "{{ result.enclosures }}"

- name: Gather information about an Enclosure by name with options
  community.general.oneview_enclosure_info:
    name: Test-Enclosure
    options:
      - script                     # optional
      - environmentalConfiguration # optional
      - utilization                # optional
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Enclosure found by name
  ansible.builtin.debug:
    msg: "{{ result.enclosures }}"

- name: Print fetched information about Enclosure Script
  ansible.builtin.debug:
    msg: "{{ result.enclosure_script }}"

- name: Print fetched information about Enclosure Environmental Configuration
  ansible.builtin.debug:
    msg: "{{ result.enclosure_environmental_configuration }}"

- name: Print fetched information about Enclosure Utilization
  ansible.builtin.debug:
    msg: "{{ result.enclosure_utilization }}"

- name: "Gather information about an Enclosure with temperature data at a resolution of one sample per day, between two
    specified dates"
  community.general.oneview_enclosure_info:
    name: Test-Enclosure
    options:
      - utilization:               # optional
          fields: AmbientTemperature
          filter:
            - startDate=2016-07-01T14:29:42.000Z
            - endDate=2017-07-01T03:29:42.000Z
          view: day
          refresh: false
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Enclosure found by name
  ansible.builtin.debug:
    msg: "{{ result.enclosures }}"

- name: Print fetched information about Enclosure Utilization
  ansible.builtin.debug:
    msg: "{{ result.enclosure_utilization }}"
"""

RETURN = r"""
enclosures:
  description: Has all the OneView information about the Enclosures.
  returned: Always, but can be null.
  type: dict

enclosure_script:
  description: Has all the OneView information about the script of an Enclosure.
  returned: When requested, but can be null.
  type: str

enclosure_environmental_configuration:
  description: Has all the OneView information about the environmental configuration of an Enclosure.
  returned: When requested, but can be null.
  type: dict

enclosure_utilization:
  description: Has all the OneView information about the utilization of an Enclosure.
  returned: When requested, but can be null.
  type: dict
"""

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class EnclosureInfoModule(OneViewModuleBase):
    argument_spec = dict(name=dict(type="str"), options=dict(type="list", elements="raw"), params=dict(type="dict"))

    def __init__(self):
        super().__init__(
            additional_arg_spec=self.argument_spec,
            supports_check_mode=True,
        )

    def execute_module(self):
        info = {}

        if self.module.params["name"]:
            enclosures = self._get_by_name(self.module.params["name"])

            if self.options and enclosures:
                info = self._gather_optional_info(self.options, enclosures[0])
        else:
            enclosures = self.oneview_client.enclosures.get_all(**self.facts_params)

        info["enclosures"] = enclosures

        return dict(changed=False, **info)

    def _gather_optional_info(self, options, enclosure):
        enclosure_client = self.oneview_client.enclosures
        info = {}

        if options.get("script"):
            info["enclosure_script"] = enclosure_client.get_script(enclosure["uri"])
        if options.get("environmentalConfiguration"):
            env_config = enclosure_client.get_environmental_configuration(enclosure["uri"])
            info["enclosure_environmental_configuration"] = env_config
        if options.get("utilization"):
            info["enclosure_utilization"] = self._get_utilization(enclosure, options["utilization"])

        return info

    def _get_utilization(self, enclosure, params):
        fields = view = refresh = filter = ""

        if isinstance(params, dict):
            fields = params.get("fields")
            view = params.get("view")
            refresh = params.get("refresh")
            filter = params.get("filter")

        return self.oneview_client.enclosures.get_utilization(
            enclosure["uri"], fields=fields, filter=filter, refresh=refresh, view=view
        )

    def _get_by_name(self, name):
        return self.oneview_client.enclosures.get_by("name", name)


def main():
    EnclosureInfoModule().run()


if __name__ == "__main__":
    main()
