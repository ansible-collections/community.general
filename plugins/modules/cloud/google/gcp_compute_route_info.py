#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# ----------------------------------------------------------------------------
#
#     ***     AUTO GENERATED CODE    ***    AUTO GENERATED CODE     ***
#
# ----------------------------------------------------------------------------
#
#     This file is automatically generated by Magic Modules and manual
#     changes will be clobbered when the file is regenerated.
#
#     Please read more about how to change this file at
#     https://www.github.com/GoogleCloudPlatform/magic-modules
#
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

DOCUMENTATION = '''
---
module: gcp_compute_route_info
description:
- Gather info for GCP Route
short_description: Gather info for GCP Route
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  filters:
    description:
    - A list of filter value pairs. Available filters are listed here U(https://cloud.google.com/sdk/gcloud/reference/topic/filters).
    - Each additional filter in the list will act be added as an AND condition (filter1
      and filter2) .
    type: list
  project:
    description:
    - The Google Cloud Platform project to use.
    type: str
  auth_kind:
    description:
    - The type of credential used.
    type: str
    required: true
    choices:
    - application
    - machineaccount
    - serviceaccount
  service_account_contents:
    description:
    - The contents of a Service Account JSON file, either in a dictionary or as a
      JSON string that represents it.
    type: jsonarg
  service_account_file:
    description:
    - The path of a Service Account JSON file if serviceaccount is selected as type.
    type: path
  service_account_email:
    description:
    - An optional service account email address if machineaccount is selected and
      the user does not wish to use the default email.
    type: str
  scopes:
    description:
    - Array of scopes to be used
    type: list
  env_type:
    description:
    - Specifies which Ansible environment you're running this module within.
    - This should not be set unless you know what you're doing.
    - This only alters the User Agent string for any API requests.
    type: str
notes:
- for authentication, you can set service_account_file using the C(gcp_service_account_file)
  env variable.
- for authentication, you can set service_account_contents using the C(GCP_SERVICE_ACCOUNT_CONTENTS)
  env variable.
- For authentication, you can set service_account_email using the C(GCP_SERVICE_ACCOUNT_EMAIL)
  env variable.
- For authentication, you can set auth_kind using the C(GCP_AUTH_KIND) env variable.
- For authentication, you can set scopes using the C(GCP_SCOPES) env variable.
- Environment variables values will only be used if the playbook values are not set.
- The I(service_account_email) and I(service_account_file) options are mutually exclusive.
'''

EXAMPLES = '''
- name: Get info on a route
  gcp_compute_route_info:
    filters:
    - name = test_object
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
resources:
  description: List of resources
  returned: always
  type: complex
  contains:
    destRange:
      description:
      - The destination range of outgoing packets that this route applies to.
      - Only IPv4 is supported.
      returned: success
      type: str
    description:
      description:
      - An optional description of this resource. Provide this property when you create
        the resource.
      returned: success
      type: str
    name:
      description:
      - Name of the resource. Provided by the client when the resource is created.
        The name must be 1-63 characters long, and comply with RFC1035. Specifically,
        the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`
        which means the first character must be a lowercase letter, and all following
        characters must be a dash, lowercase letter, or digit, except the last character,
        which cannot be a dash.
      returned: success
      type: str
    network:
      description:
      - The network that this route applies to.
      returned: success
      type: dict
    priority:
      description:
      - The priority of this route. Priority is used to break ties in cases where
        there is more than one matching route of equal prefix length.
      - In the case of two routes with equal prefix length, the one with the lowest-numbered
        priority value wins.
      - Default value is 1000. Valid range is 0 through 65535.
      returned: success
      type: int
    tags:
      description:
      - A list of instance tags to which this route applies.
      returned: success
      type: list
    nextHopGateway:
      description:
      - URL to a gateway that should handle matching packets.
      - 'Currently, you can only specify the internet gateway, using a full or partial valid URL:'
      - ' * https://www.googleapis.com/compute/v1/projects/project/global/gateways/default-internet-gateway'
      - ' * projects/project/global/gateways/default-internet-gateway'
      - ' * global/gateways/default-internet-gateway'
      returned: success
      type: str
    nextHopInstance:
      description:
      - URL to an instance that should handle matching packets.
      - 'You can specify this as a full or partial URL. For example:'
      - ' * https://www.googleapis.com/compute/v1/projects/project/zones/zone/instances/instance'
      - ' * projects/project/zones/zone/instances/instance'
      - ' * zones/zone/instances/instance'
      returned: success
      type: dict
    nextHopIp:
      description:
      - Network IP address of an instance that should handle matching packets.
      returned: success
      type: str
    nextHopVpnTunnel:
      description:
      - URL to a VpnTunnel that should handle matching packets.
      returned: success
      type: dict
    nextHopNetwork:
      description:
      - URL to a Network that should handle matching packets.
      returned: success
      type: str
    nextHopIlb:
      description:
      - The URL to a forwarding rule of type loadBalancingScheme=INTERNAL that should
        handle matching packets.
      - 'You can only specify the forwarding rule as a partial or full URL. For example,
        the following are all valid URLs: U(https://www.googleapis.com/compute/v1/projects/project/regions/region/forwardingRules/forwardingRule)
        regions/region/forwardingRules/forwardingRule Note that this can only be used
        when the destinationRange is a public (non-RFC 1918) IP CIDR range.'
      returned: success
      type: dict
'''

################################################################################
# Imports
################################################################################
from ansible_collections.google.cloud.plugins.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest
import json

################################################################################
# Main
################################################################################


def main():
    module = GcpModule(argument_spec=dict(filters=dict(type='list', elements='str')))

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/compute']

    return_value = {'resources': fetch_list(module, collection(module), query_options(module.params['filters']))}
    module.exit_json(**return_value)


def collection(module):
    return "https://www.googleapis.com/compute/v1/projects/{project}/global/routes".format(**module.params)


def fetch_list(module, link, query):
    auth = GcpSession(module, 'compute')
    return auth.list(link, return_if_object, array_name='items', params={'filter': query})


def query_options(filters):
    if not filters:
        return ''

    if len(filters) == 1:
        return filters[0]
    else:
        queries = []
        for f in filters:
            # For multiple queries, all queries should have ()
            if f[0] != '(' and f[-1] != ')':
                queries.append("(%s)" % ''.join(f))
            else:
                queries.append(f)

        return ' '.join(queries)


def return_if_object(module, response):
    # If not found, return nothing.
    if response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    return result


if __name__ == "__main__":
    main()
