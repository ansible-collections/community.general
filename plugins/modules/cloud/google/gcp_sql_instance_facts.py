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
module: gcp_sql_instance_facts
deprecated:
  removed_in: '2.13'
  why: Module has been renamed in Ansible 2.9.
  alternative: Use C(google.cloud.gcp_sql_instance_info) instead.
description:
- Gather info for GCP Instance
short_description: Gather info for GCP Instance
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
- name: Get info on an instance
  gcp_sql_instance_info:
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
    backendType:
      description:
      - "* FIRST_GEN: First Generation instance. MySQL only."
      - "* SECOND_GEN: Second Generation instance or PostgreSQL instance."
      - "* EXTERNAL: A database server that is not managed by Google."
      returned: success
      type: str
    connectionName:
      description:
      - Connection name of the Cloud SQL instance used in connection strings.
      returned: success
      type: str
    databaseVersion:
      description:
      - The database engine type and version. For First Generation instances, can
        be MYSQL_5_5, or MYSQL_5_6. For Second Generation instances, can be MYSQL_5_6
        or MYSQL_5_7. Defaults to MYSQL_5_6.
      - 'PostgreSQL instances: POSTGRES_9_6 The databaseVersion property can not be
        changed after instance creation.'
      returned: success
      type: str
    failoverReplica:
      description:
      - The name and status of the failover replica. This property is applicable only
        to Second Generation instances.
      returned: success
      type: complex
      contains:
        available:
          description:
          - The availability status of the failover replica. A false status indicates
            that the failover replica is out of sync. The master can only failover
            to the failover replica when the status is true.
          returned: success
          type: bool
        name:
          description:
          - The name of the failover replica. If specified at instance creation, a
            failover replica is created for the instance. The name doesn't include
            the project ID. This property is applicable only to Second Generation
            instances.
          returned: success
          type: str
    instanceType:
      description:
      - The instance type. This can be one of the following.
      - "* CLOUD_SQL_INSTANCE: A Cloud SQL instance that is not replicating from a
        master."
      - "* ON_PREMISES_INSTANCE: An instance running on the customer's premises."
      - "* READ_REPLICA_INSTANCE: A Cloud SQL instance configured as a read-replica."
      returned: success
      type: str
    ipAddresses:
      description:
      - The assigned IP addresses for the instance.
      returned: success
      type: complex
      contains:
        ipAddress:
          description:
          - The IP address assigned.
          returned: success
          type: str
        timeToRetire:
          description:
          - The due time for this IP to be retired in RFC 3339 format, for example
            2012-11-15T16:19:00.094Z. This field is only available when the IP is
            scheduled to be retired.
          returned: success
          type: str
        type:
          description:
          - The type of this IP address. A PRIMARY address is an address that can
            accept incoming connections. An OUTGOING address is the source address
            of connections originating from the instance, if supported.
          returned: success
          type: str
    ipv6Address:
      description:
      - The IPv6 address assigned to the instance. This property is applicable only
        to First Generation instances.
      returned: success
      type: str
    masterInstanceName:
      description:
      - The name of the instance which will act as master in the replication setup.
      returned: success
      type: str
    maxDiskSize:
      description:
      - The maximum disk size of the instance in bytes.
      returned: success
      type: int
    name:
      description:
      - Name of the Cloud SQL instance. This does not include the project ID.
      returned: success
      type: str
    region:
      description:
      - The geographical region. Defaults to us-central or us-central1 depending on
        the instance type (First Generation or Second Generation/PostgreSQL).
      returned: success
      type: str
    replicaConfiguration:
      description:
      - Configuration specific to failover replicas and read replicas.
      returned: success
      type: complex
      contains:
        failoverTarget:
          description:
          - Specifies if the replica is the failover target. If the field is set to
            true the replica will be designated as a failover replica.
          - In case the master instance fails, the replica instance will be promoted
            as the new master instance.
          - Only one replica can be specified as failover target, and the replica
            has to be in different zone with the master instance.
          returned: success
          type: bool
        mysqlReplicaConfiguration:
          description:
          - MySQL specific configuration when replicating from a MySQL on-premises
            master. Replication configuration information such as the username, password,
            certificates, and keys are not stored in the instance metadata. The configuration
            information is used only to set up the replication connection and is stored
            by MySQL in a file named master.info in the data directory.
          returned: success
          type: complex
          contains:
            caCertificate:
              description:
              - PEM representation of the trusted CA's x509 certificate.
              returned: success
              type: str
            clientCertificate:
              description:
              - PEM representation of the slave's x509 certificate .
              returned: success
              type: str
            clientKey:
              description:
              - PEM representation of the slave's private key. The corresponding public
                key is encoded in the client's certificate.
              returned: success
              type: str
            connectRetryInterval:
              description:
              - Seconds to wait between connect retries. MySQL's default is 60 seconds.
              returned: success
              type: int
            dumpFilePath:
              description:
              - Path to a SQL dump file in Google Cloud Storage from which the slave
                instance is to be created. The URI is in the form gs://bucketName/fileName.
                Compressed gzip files (.gz) are also supported. Dumps should have
                the binlog coordinates from which replication should begin. This can
                be accomplished by setting --master-data to 1 when using mysqldump.
              returned: success
              type: str
            masterHeartbeatPeriod:
              description:
              - Interval in milliseconds between replication heartbeats.
              returned: success
              type: int
            password:
              description:
              - The password for the replication connection.
              returned: success
              type: str
            sslCipher:
              description:
              - A list of permissible ciphers to use for SSL encryption.
              returned: success
              type: str
            username:
              description:
              - The username for the replication connection.
              returned: success
              type: str
            verifyServerCertificate:
              description:
              - Whether or not to check the master's Common Name value in the certificate
                that it sends during the SSL handshake.
              returned: success
              type: bool
        replicaNames:
          description:
          - The replicas of the instance.
          returned: success
          type: list
        serviceAccountEmailAddress:
          description:
          - The service account email address assigned to the instance. This property
            is applicable only to Second Generation instances.
          returned: success
          type: str
    settings:
      description:
      - The user settings.
      returned: success
      type: complex
      contains:
        databaseFlags:
          description:
          - The database flags passed to the instance at startup.
          returned: success
          type: complex
          contains:
            name:
              description:
              - The name of the flag. These flags are passed at instance startup,
                so include both server options and system variables for MySQL. Flags
                should be specified with underscores, not hyphens.
              returned: success
              type: str
            value:
              description:
              - The value of the flag. Booleans should be set to on for true and off
                for false. This field must be omitted if the flag doesn't take a value.
              returned: success
              type: str
        ipConfiguration:
          description:
          - The settings for IP Management. This allows to enable or disable the instance
            IP and manage which external networks can connect to the instance. The
            IPv4 address cannot be disabled for Second Generation instances.
          returned: success
          type: complex
          contains:
            ipv4Enabled:
              description:
              - Whether the instance should be assigned an IP address or not.
              returned: success
              type: bool
            authorizedNetworks:
              description:
              - The list of external networks that are allowed to connect to the instance
                using the IP. In CIDR notation, also known as 'slash' notation (e.g.
                192.168.100.0/24).
              returned: success
              type: complex
              contains:
                expirationTime:
                  description:
                  - The time when this access control entry expires in RFC 3339 format,
                    for example 2012-11-15T16:19:00.094Z.
                  returned: success
                  type: str
                name:
                  description:
                  - An optional label to identify this entry.
                  returned: success
                  type: str
                value:
                  description:
                  - The whitelisted value for the access control list. For example,
                    to grant access to a client from an external IP (IPv4 or IPv6)
                    address or subnet, use that address or subnet here.
                  returned: success
                  type: str
            requireSsl:
              description:
              - Whether the mysqld should default to 'REQUIRE X509' for users connecting
                over IP.
              returned: success
              type: bool
        tier:
          description:
          - The tier or machine type for this instance, for example db-n1-standard-1.
            For MySQL instances, this field determines whether the instance is Second
            Generation (recommended) or First Generation.
          returned: success
          type: str
        availabilityType:
          description:
          - The availabilityType define if your postgres instance is run zonal or
            regional.
          returned: success
          type: str
        backupConfiguration:
          description:
          - The daily backup configuration for the instance.
          returned: success
          type: complex
          contains:
            enabled:
              description:
              - Enable Autobackup for your instance.
              returned: success
              type: bool
            binaryLogEnabled:
              description:
              - Whether binary log is enabled. If backup configuration is disabled,
                binary log must be disabled as well. MySQL only.
              returned: success
              type: bool
            startTime:
              description:
              - Define the backup start time in UTC (HH:MM) .
              returned: success
              type: str
        settingsVersion:
          description:
          - The version of instance settings. This is a required field for update
            method to make sure concurrent updates are handled properly. During update,
            use the most recent settingsVersion value for this instance and do not
            try to update this value.
          returned: success
          type: int
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
        module.params['scopes'] = ['https://www.googleapis.com/auth/sqlservice.admin']

    return_value = {'resources': fetch_list(module, collection(module))}
    module.exit_json(**return_value)


def collection(module):
    return "https://www.googleapis.com/sql/v1beta4/projects/{project}/instances".format(**module.params)


def fetch_list(module, link):
    auth = GcpSession(module, 'sql')
    return auth.list(link, return_if_object, array_name='items')


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
