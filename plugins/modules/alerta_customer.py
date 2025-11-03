#!/usr/bin/python

# Copyright (c) 2022, Christian Wollinger <@cwollinger>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: alerta_customer
short_description: Manage customers in Alerta
version_added: 4.8.0
description:
  - Create or delete customers in Alerta with the REST API.
author: Christian Wollinger (@cwollinger)
seealso:
  - name: API documentation
    description: Documentation for Alerta API.
    link: https://docs.alerta.io/api/reference.html#customers
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  customer:
    description:
      - Name of the customer.
    required: true
    type: str
  match:
    description:
      - The matching logged in user for the customer.
    required: true
    type: str
  alerta_url:
    description:
      - The Alerta API endpoint.
    required: true
    type: str
  api_username:
    description:
      - The username for the API using basic auth.
    type: str
  api_password:
    description:
      - The password for the API using basic auth.
    type: str
  api_key:
    description:
      - The access token for the API.
    type: str
  state:
    description:
      - Whether the customer should exist or not.
      - Both O(customer) and O(match) identify a customer that should be added or removed.
    type: str
    choices: [absent, present]
    default: present
"""

EXAMPLES = r"""
- name: Create customer
  community.general.alerta_customer:
    alerta_url: https://alerta.example.com
    api_username: admin@example.com
    api_password: password
    customer: Developer
    match: dev@example.com

- name: Delete customer
  community.general.alerta_customer:
    alerta_url: https://alerta.example.com
    api_username: admin@example.com
    api_password: password
    customer: Developer
    match: dev@example.com
    state: absent
"""

RETURN = r"""
msg:
  description:
    - Success or failure message.
  returned: always
  type: str
  sample: Customer customer1 created
response:
  description:
    - The response from the API.
  returned: always
  type: dict
"""

from ansible.module_utils.urls import fetch_url, basic_auth_header
from ansible.module_utils.basic import AnsibleModule


class AlertaInterface:
    def __init__(self, module):
        self.module = module
        self.state = module.params["state"]
        self.customer = module.params["customer"]
        self.match = module.params["match"]
        self.alerta_url = module.params["alerta_url"]
        self.headers = {"Content-Type": "application/json"}

        if module.params.get("api_key", None):
            self.headers["Authorization"] = f"Key {module.params['api_key']}"
        else:
            self.headers["Authorization"] = basic_auth_header(
                module.params["api_username"], module.params["api_password"]
            )

    def send_request(self, url, data=None, method="GET"):
        response, info = fetch_url(self.module, url, data=data, headers=self.headers, method=method)

        status_code = info["status"]
        if status_code == 401:
            self.module.fail_json(failed=True, response=info, msg=f"Unauthorized to request '{method}' on '{url}'")
        elif status_code == 403:
            self.module.fail_json(failed=True, response=info, msg=f"Permission Denied for '{method}' on '{url}'")
        elif status_code == 404:
            self.module.fail_json(failed=True, response=info, msg=f"Not found for request '{method}' on '{url}'")
        elif status_code in (200, 201):
            return self.module.from_json(response.read())
        self.module.fail_json(failed=True, response=info, msg=f"Alerta API error with HTTP {status_code} for {url}")

    def get_customers(self):
        url = f"{self.alerta_url}/api/customers"
        response = self.send_request(url)
        pages = response["pages"]
        if pages > 1:
            for page in range(2, pages + 1):
                page_url = f"{url}?page={page}"
                new_results = self.send_request(page_url)
                response.update(new_results)
        return response

    def create_customer(self):
        url = f"{self.alerta_url}/api/customer"

        payload = {
            "customer": self.customer,
            "match": self.match,
        }

        payload = self.module.jsonify(payload)
        response = self.send_request(url, payload, "POST")
        return response

    def delete_customer(self, id):
        url = f"{self.alerta_url}/api/customer/{id}"

        response = self.send_request(url, None, "DELETE")
        return response

    def find_customer_id(self, customer):
        for i in customer["customers"]:
            if self.customer == i["customer"] and self.match == i["match"]:
                return i["id"]
        return None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=["present", "absent"], default="present"),
            customer=dict(type="str", required=True),
            match=dict(type="str", required=True),
            alerta_url=dict(type="str", required=True),
            api_username=dict(type="str"),
            api_password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
        ),
        required_together=[["api_username", "api_password"]],
        mutually_exclusive=[["api_username", "api_key"]],
        supports_check_mode=True,
    )

    alerta_iface = AlertaInterface(module)

    if alerta_iface.state == "present":
        response = alerta_iface.get_customers()
        if alerta_iface.find_customer_id(response):
            module.exit_json(changed=False, response=response, msg=f"Customer {alerta_iface.customer} already exists")
        else:
            if not module.check_mode:
                response = alerta_iface.create_customer()
            module.exit_json(changed=True, response=response, msg=f"Customer {alerta_iface.customer} created")
    else:
        response = alerta_iface.get_customers()
        id = alerta_iface.find_customer_id(response)
        if id:
            if not module.check_mode:
                alerta_iface.delete_customer(id)
            module.exit_json(
                changed=True, response=response, msg=f"Customer {alerta_iface.customer} with id {id} deleted"
            )
        else:
            module.exit_json(changed=False, response=response, msg=f"Customer {alerta_iface.customer} does not exists")


if __name__ == "__main__":
    main()
