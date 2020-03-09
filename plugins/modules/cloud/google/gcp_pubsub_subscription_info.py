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

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_pubsub_subscription_info
description:
- Gather info for GCP Subscription
short_description: Gather info for GCP Subscription
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
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
- name: get info on a subscription
  gcp_pubsub_subscription_info:
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
    name:
      description:
      - Name of the subscription.
      returned: success
      type: str
    topic:
      description:
      - A reference to a Topic resource.
      returned: success
      type: dict
    labels:
      description:
      - A set of key/value label pairs to assign to this Subscription.
      returned: success
      type: dict
    pushConfig:
      description:
      - If push delivery is used with this subscription, this field is used to configure
        it. An empty pushConfig signifies that the subscriber will pull and ack messages
        using API methods.
      returned: success
      type: complex
      contains:
        oidcToken:
          description:
          - If specified, Pub/Sub will generate and attach an OIDC JWT token as an
            Authorization header in the HTTP request for every pushed message.
          returned: success
          type: complex
          contains:
            serviceAccountEmail:
              description:
              - Service account email to be used for generating the OIDC token.
              - The caller (for subscriptions.create, subscriptions.patch, and subscriptions.modifyPushConfig
                RPCs) must have the iam.serviceAccounts.actAs permission for the service
                account.
              returned: success
              type: str
            audience:
              description:
              - 'Audience to be used when generating OIDC token. The audience claim
                identifies the recipients that the JWT is intended for. The audience
                value is a single case-sensitive string. Having multiple values (array)
                for the audience field is not supported. More info about the OIDC
                JWT token audience here: U(https://tools.ietf.org/html/rfc7519#section-4.1.3)
                Note: if not specified, the Push endpoint URL will be used.'
              returned: success
              type: str
        pushEndpoint:
          description:
          - A URL locating the endpoint to which messages should be pushed.
          - For example, a Webhook endpoint might use "U(https://example.com/push").
          returned: success
          type: str
        attributes:
          description:
          - Endpoint configuration attributes.
          - Every endpoint has a set of API supported attributes that can be used
            to control different aspects of the message delivery.
          - The currently supported attribute is x-goog-version, which you can use
            to change the format of the pushed message. This attribute indicates the
            version of the data expected by the endpoint. This controls the shape
            of the pushed message (i.e., its fields and metadata). The endpoint version
            is based on the version of the Pub/Sub API.
          - If not present during the subscriptions.create call, it will default to
            the version of the API used to make such call. If not present during a
            subscriptions.modifyPushConfig call, its value will not be changed. subscriptions.get
            calls will always return a valid version, even if the subscription was
            created without this attribute.
          - 'The possible values for this attribute are: - v1beta1: uses the push
            format defined in the v1beta1 Pub/Sub API.'
          - "- v1 or v1beta2: uses the push format defined in the v1 Pub/Sub API."
          returned: success
          type: dict
    ackDeadlineSeconds:
      description:
      - This value is the maximum time after a subscriber receives a message before
        the subscriber should acknowledge the message. After message delivery but
        before the ack deadline expires and before the message is acknowledged, it
        is an outstanding message and will not be delivered again during that time
        (on a best-effort basis).
      - For pull subscriptions, this value is used as the initial value for the ack
        deadline. To override this value for a given message, call subscriptions.modifyAckDeadline
        with the corresponding ackId if using pull. The minimum custom deadline you
        can specify is 10 seconds. The maximum custom deadline you can specify is
        600 seconds (10 minutes).
      - If this parameter is 0, a default value of 10 seconds is used.
      - For push delivery, this value is also used to set the request timeout for
        the call to the push endpoint.
      - If the subscriber never acknowledges the message, the Pub/Sub system will
        eventually redeliver the message.
      returned: success
      type: int
    messageRetentionDuration:
      description:
      - How long to retain unacknowledged messages in the subscription's backlog,
        from the moment a message is published. If retainAckedMessages is true, then
        this also configures the retention of acknowledged messages, and thus configures
        how far back in time a subscriptions.seek can be done. Defaults to 7 days.
        Cannot be more than 7 days (`"604800s"`) or less than 10 minutes (`"600s"`).
      - 'A duration in seconds with up to nine fractional digits, terminated by ''s''.
        Example: `"600.5s"`.'
      returned: success
      type: str
    retainAckedMessages:
      description:
      - Indicates whether to retain acknowledged messages. If `true`, then messages
        are not expunged from the subscription's backlog, even if they are acknowledged,
        until they fall out of the messageRetentionDuration window.
      returned: success
      type: bool
    expirationPolicy:
      description:
      - A policy that specifies the conditions for this subscription's expiration.
      - A subscription is considered active as long as any connected subscriber is
        successfully consuming messages from the subscription or is issuing operations
        on the subscription. If expirationPolicy is not set, a default policy with
        ttl of 31 days will be used. If it is set but ttl is "", the resource never
        expires. The minimum allowed value for expirationPolicy.ttl is 1 day.
      returned: success
      type: complex
      contains:
        ttl:
          description:
          - Specifies the "time-to-live" duration for an associated resource. The
            resource expires if it is not active for a period of ttl.
          - If ttl is not set, the associated resource never expires.
          - A duration in seconds with up to nine fractional digits, terminated by
            's'.
          - Example - "3.5s".
          returned: success
          type: str
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
    module = GcpModule(argument_spec=dict())

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/pubsub']

    return_value = {'resources': fetch_list(module, collection(module))}
    module.exit_json(**return_value)


def collection(module):
    return "https://pubsub.googleapis.com/v1/projects/{project}/subscriptions".format(**module.params)


def fetch_list(module, link):
    auth = GcpSession(module, 'pubsub')
    return auth.list(link, return_if_object, array_name='subscriptions')


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
