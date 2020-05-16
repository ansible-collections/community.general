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
module: gcp_compute_image_facts
deprecated:
  removed_in: '2.13'
  why: Module has been renamed in Ansible 2.9.
  alternative: Use C(google.cloud.gcp_compute_image_info) instead.
description:
- Gather info for GCP Image
short_description: Gather info for GCP Image
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
- name: Get info on an image
  gcp_compute_image_info:
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
    archiveSizeBytes:
      description:
      - Size of the image tar.gz archive stored in Google Cloud Storage (in bytes).
      returned: success
      type: int
    creationTimestamp:
      description:
      - Creation timestamp in RFC3339 text format.
      returned: success
      type: str
    deprecated:
      description:
      - The deprecation status associated with this image.
      returned: success
      type: complex
      contains:
        deleted:
          description:
          - An optional RFC3339 timestamp on or after which the state of this resource
            is intended to change to DELETED. This is only informational and the status
            will not change unless the client explicitly changes it.
          returned: success
          type: str
        deprecated:
          description:
          - An optional RFC3339 timestamp on or after which the state of this resource
            is intended to change to DEPRECATED. This is only informational and the
            status will not change unless the client explicitly changes it.
          returned: success
          type: str
        obsolete:
          description:
          - An optional RFC3339 timestamp on or after which the state of this resource
            is intended to change to OBSOLETE. This is only informational and the
            status will not change unless the client explicitly changes it.
          returned: success
          type: str
        replacement:
          description:
          - The URL of the suggested replacement for a deprecated resource.
          - The suggested replacement resource must be the same kind of resource as
            the deprecated resource.
          returned: success
          type: str
        state:
          description:
          - The deprecation state of this resource. This can be DEPRECATED, OBSOLETE,
            or DELETED. Operations which create a new resource using a DEPRECATED
            resource will return successfully, but with a warning indicating the deprecated
            resource and recommending its replacement. Operations which use OBSOLETE
            or DELETED resources will be rejected and result in an error.
          returned: success
          type: str
    description:
      description:
      - An optional description of this resource. Provide this property when you create
        the resource.
      returned: success
      type: str
    diskSizeGb:
      description:
      - Size of the image when restored onto a persistent disk (in GB).
      returned: success
      type: int
    family:
      description:
      - The name of the image family to which this image belongs. You can create disks
        by specifying an image family instead of a specific image name. The image
        family always returns its latest image that is not deprecated. The name of
        the image family must comply with RFC1035.
      returned: success
      type: str
    guestOsFeatures:
      description:
      - A list of features to enable on the guest operating system.
      - Applicable only for bootable images.
      returned: success
      type: complex
      contains:
        type:
          description:
          - The type of supported feature.
          returned: success
          type: str
    id:
      description:
      - The unique identifier for the resource. This identifier is defined by the
        server.
      returned: success
      type: int
    imageEncryptionKey:
      description:
      - Encrypts the image using a customer-supplied encryption key.
      - After you encrypt an image with a customer-supplied key, you must provide
        the same key if you use the image later (e.g. to create a disk from the image)
        .
      returned: success
      type: complex
      contains:
        rawKey:
          description:
          - Specifies a 256-bit customer-supplied encryption key, encoded in RFC 4648
            base64 to either encrypt or decrypt this resource.
          returned: success
          type: str
        sha256:
          description:
          - The RFC 4648 base64 encoded SHA-256 hash of the customer-supplied encryption
            key that protects this resource.
          returned: success
          type: str
    labels:
      description:
      - Labels to apply to this Image.
      returned: success
      type: dict
    labelFingerprint:
      description:
      - The fingerprint used for optimistic locking of this resource. Used internally
        during updates.
      returned: success
      type: str
    licenses:
      description:
      - Any applicable license URI.
      returned: success
      type: list
    name:
      description:
      - Name of the resource; provided by the client when the resource is created.
        The name must be 1-63 characters long, and comply with RFC1035. Specifically,
        the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`
        which means the first character must be a lowercase letter, and all following
        characters must be a dash, lowercase letter, or digit, except the last character,
        which cannot be a dash.
      returned: success
      type: str
    rawDisk:
      description:
      - The parameters of the raw disk image.
      returned: success
      type: complex
      contains:
        containerType:
          description:
          - The format used to encode and transmit the block device, which should
            be TAR. This is just a container and transmission format and not a runtime
            format. Provided by the client when the disk image is created.
          returned: success
          type: str
        sha1Checksum:
          description:
          - An optional SHA1 checksum of the disk image before unpackaging.
          - This is provided by the client when the disk image is created.
          returned: success
          type: str
        source:
          description:
          - The full Google Cloud Storage URL where disk storage is stored You must
            provide either this property or the sourceDisk property but not both.
          returned: success
          type: str
    sourceDisk:
      description:
      - The source disk to create this image based on.
      - You must provide either this property or the rawDisk.source property but not
        both to create an image.
      returned: success
      type: dict
    sourceDiskEncryptionKey:
      description:
      - The customer-supplied encryption key of the source disk. Required if the source
        disk is protected by a customer-supplied encryption key.
      returned: success
      type: complex
      contains:
        rawKey:
          description:
          - Specifies a 256-bit customer-supplied encryption key, encoded in RFC 4648
            base64 to either encrypt or decrypt this resource.
          returned: success
          type: str
        sha256:
          description:
          - The RFC 4648 base64 encoded SHA-256 hash of the customer-supplied encryption
            key that protects this resource.
          returned: success
          type: str
    sourceDiskId:
      description:
      - The ID value of the disk used to create this image. This value may be used
        to determine whether the image was taken from the current or a previous instance
        of a given disk name.
      returned: success
      type: str
    sourceType:
      description:
      - The type of the image used to create this disk. The default and only value
        is RAW .
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
    module = GcpModule(argument_spec=dict(filters=dict(type='list', elements='str')))

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/compute']

    return_value = {'resources': fetch_list(module, collection(module), query_options(module.params['filters']))}
    module.exit_json(**return_value)


def collection(module):
    return "https://www.googleapis.com/compute/v1/projects/{project}/global/images".format(**module.params)


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
