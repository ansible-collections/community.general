#!/usr/bin/python

# Copyright (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nomad_job_info
author: FERREIRA Christophe (@chris93111)
version_added: "1.3.0"
short_description: Get Nomad Jobs info
description:
  - Get info for one Nomad job.
  - List Nomad jobs.
requirements:
  - python-nomad
extends_documentation_fragment:
  - community.general._nomad
  - community.general._attributes
  - community.general._attributes.info_module
options:
  name:
    description:
      - Name of job for Get info.
      - If not specified, lists all jobs.
    type: str
seealso:
  - name: Nomad jobs documentation
    description: Complete documentation for Nomad API jobs.
    link: https://www.nomadproject.io/api-docs/jobs/
"""

EXAMPLES = r"""
- name: Get info for job awx
  community.general.nomad_job_info:
    host: localhost
    name: awx
  register: result

- name: List Nomad jobs
  community.general.nomad_job_info:
    host: localhost
  register: result
"""

RETURN = r"""
result:
  description: List with dictionary contains jobs info.
  returned: success
  type: list
  sample:
    [
      {
        "Affinities": null,
        "AllAtOnce": false,
        "Constraints": null,
        "ConsulToken": "",
        "CreateIndex": 13,
        "Datacenters": [
          "dc1"
        ],
        "Dispatched": false,
        "ID": "example",
        "JobModifyIndex": 13,
        "Meta": null,
        "ModifyIndex": 13,
        "Multiregion": null,
        "Name": "example",
        "Namespace": "default",
        "NomadTokenID": "",
        "ParameterizedJob": null,
        "ParentID": "",
        "Payload": null,
        "Periodic": null,
        "Priority": 50,
        "Region": "global",
        "Spreads": null,
        "Stable": false,
        "Status": "pending",
        "StatusDescription": "",
        "Stop": false,
        "SubmitTime": 1602244370615307000,
        "TaskGroups": [
          {
            "Affinities": null,
            "Constraints": null,
            "Count": 1,
            "EphemeralDisk": {
              "Migrate": false,
              "SizeMB": 300,
              "Sticky": false
            },
            "Meta": null,
            "Migrate": {
              "HealthCheck": "checks",
              "HealthyDeadline": 300000000000,
              "MaxParallel": 1,
              "MinHealthyTime": 10000000000
            },
            "Name": "cache",
            "Networks": null,
            "ReschedulePolicy": {
              "Attempts": 0,
              "Delay": 30000000000,
              "DelayFunction": "exponential",
              "Interval": 0,
              "MaxDelay": 3600000000000,
              "Unlimited": true
            },
            "RestartPolicy": {
              "Attempts": 3,
              "Delay": 15000000000,
              "Interval": 1800000000000,
              "Mode": "fail"
            },
            "Scaling": null,
            "Services": null,
            "ShutdownDelay": null,
            "Spreads": null,
            "StopAfterClientDisconnect": null,
            "Tasks": [
              {
                "Affinities": null,
                "Artifacts": null,
                "CSIPluginConfig": null,
                "Config": {
                  "image": "redis:3.2",
                  "port_map": [
                    {
                      "db": 6379.0
                    }
                  ]
                },
                "Constraints": null,
                "DispatchPayload": null,
                "Driver": "docker",
                "Env": null,
                "KillSignal": "",
                "KillTimeout": 5000000000,
                "Kind": "",
                "Leader": false,
                "Lifecycle": null,
                "LogConfig": {
                  "MaxFileSizeMB": 10,
                  "MaxFiles": 10
                },
                "Meta": null,
                "Name": "redis",
                "Resources": {
                  "CPU": 500,
                  "Devices": null,
                  "DiskMB": 0,
                  "IOPS": 0,
                  "MemoryMB": 256,
                  "Networks": [
                    {
                      "CIDR": "",
                      "DNS": null,
                      "Device": "",
                      "DynamicPorts": [
                        {
                          "HostNetwork": "default",
                          "Label": "db",
                          "To": 0,
                          "Value": 0
                        }
                      ],
                      "IP": "",
                      "MBits": 10,
                      "Mode": "",
                      "ReservedPorts": null
                    }
                  ]
                },
                "RestartPolicy": {
                  "Attempts": 3,
                  "Delay": 15000000000,
                  "Interval": 1800000000000,
                  "Mode": "fail"
                },
                "Services": [
                  {
                    "AddressMode": "auto",
                    "CanaryMeta": null,
                    "CanaryTags": null,
                    "Checks": [
                      {
                        "AddressMode": "",
                        "Args": null,
                        "CheckRestart": null,
                        "Command": "",
                        "Expose": false,
                        "FailuresBeforeCritical": 0,
                        "GRPCService": "",
                        "GRPCUseTLS": false,
                        "Header": null,
                        "InitialStatus": "",
                        "Interval": 10000000000,
                        "Method": "",
                        "Name": "alive",
                        "Path": "",
                        "PortLabel": "",
                        "Protocol": "",
                        "SuccessBeforePassing": 0,
                        "TLSSkipVerify": false,
                        "TaskName": "",
                        "Timeout": 2000000000,
                        "Type": "tcp"
                      }
                    ],
                    "Connect": null,
                    "EnableTagOverride": false,
                    "Meta": null,
                    "Name": "redis-cache",
                    "PortLabel": "db",
                    "Tags": [
                      "global",
                      "cache"
                    ],
                    "TaskName": ""
                  }
                ],
                "ShutdownDelay": 0,
                "Templates": null,
                "User": "",
                "Vault": null,
                "VolumeMounts": null
              }
            ],
            "Update": {
              "AutoPromote": false,
              "AutoRevert": false,
              "Canary": 0,
              "HealthCheck": "checks",
              "HealthyDeadline": 180000000000,
              "MaxParallel": 1,
              "MinHealthyTime": 10000000000,
              "ProgressDeadline": 600000000000,
              "Stagger": 30000000000
            },
            "Volumes": null
          }
        ],
        "Type": "service",
        "Update": {
          "AutoPromote": false,
          "AutoRevert": false,
          "Canary": 0,
          "HealthCheck": "",
          "HealthyDeadline": 0,
          "MaxParallel": 1,
          "MinHealthyTime": 0,
          "ProgressDeadline": 0,
          "Stagger": 30000000000
        },
        "VaultNamespace": "",
        "VaultToken": "",
        "Version": 0
      }
    ]
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._nomad import argument_spec as nomad_argument_spec
from ansible_collections.community.general.plugins.module_utils._nomad import setup_nomad_client


def run():
    module = AnsibleModule(
        argument_spec={
            **nomad_argument_spec,
            "name": dict(type="str"),
        },
        supports_check_mode=True,
    )

    nomad_client = setup_nomad_client(module)

    changed = False
    result = list()
    try:
        job_list = nomad_client.jobs.get_jobs()
        for job in job_list:
            result.append(nomad_client.job.get_job(job.get("ID")))
    except Exception as e:
        module.fail_json(msg=f"{e}")

    if module.params["name"]:
        filter = list()
        try:
            for job in result:
                if job.get("ID") == module.params["name"]:
                    filter.append(job)
                    result = filter
            if not filter:
                module.fail_json(msg=f"Couldn't find Job with id {module.params['name']}")
        except Exception as e:
            module.fail_json(msg=f"{e}")

    module.exit_json(changed=changed, result=result)


def main():
    run()


if __name__ == "__main__":
    main()
