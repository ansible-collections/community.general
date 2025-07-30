#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Massimo Gengarelli (massimo.gengarelli@proton.me)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: tanzu_mission_control_secret
short_description: Manages Cluster, Cluster Group Secrets and SecretExports in Tanzu Mission Control
version_added: 11.0.0
description:
  - Create and revokes Cluster and Cluster Group Secrets in Tanzu Mission Control for a given Cluster.
  - Creates and removes SecretExports for the given secret in Tanzu Mission Control.
author:
  - Massimo Gengarelli (@massix)
notes:
  - To obtain an O(api_token), login to Tanzu Mission Control, click on your user, then I(Settings) and then I(Generate an
    API token).
  - The generated API token B(must) have the rights to create I(Secrets) and I(SecretExports) in Tanzu Mission Control.
  - The rights are granted by the administrator of the TMC Instance to single users or groups.
  - When creating the token, make sure you select the C(tmc_user) service role for all the required organizations.
  - This has only been tested with I(TMC SaaS), but it should also work with TMC Self Hosted.
options:
  api_host:
    description:
      - 'Full URL of the TMC instance without the protocol, for example: V(my-organization.tmc.tanzu.broadcom.com).'
    required: true
    type: str
  api_token:
    description:
      - API Token used to access the APIs.
    required: true
    type: str
  management_cluster_name:
    description:
      - When creating a secret for a single cluster, this is the name of the management cluster.
      - Required only when using O(cluster_name).
      - Ignored when using O(cluster_group).
    required: false
    type: str
  provisioner_name:
    description:
      - When creating a secret for a single cluster, this is the name of the provisioner.
      - Required only when using O(cluster_name).
      - Ignored when using O(cluster_group).
    required: false
    type: str
  cluster_name:
    description:
      - Name of the existing cluster where the secret will be created.
      - Mutually exclusive with O(cluster_group).
    required: false
    type: str
  cluster_group:
    description:
      - Name of the existing cluster group where the secret will be created.
      - Mutually exclusive with O(cluster_name).
    required: false
    type: str
  cluster_namespace:
    description:
      - The namespace where the secret will be created.
    required: true
    type: str
  secret_type:
    description:
      - Set this to V(opaque) to create an opaque secret (key/value pairs) or V(docker_config) to create a Docker Config secret.
      - When O(secret_type=docker_config), O(registry_host), O(registry_username), and O(registry_password) are required.
      - When O(secret_type=opaque), O(data) is required.
    type: str
    choices: ["opaque", "docker_config"]
    default: opaque
    required: false
  registry_host:
    description:
      - Required when O(secret_type=docker_config), this is the Docker registry host.
      - Mutually exclusive with O(data).
    type: str
    required: false
  registry_username:
    description:
      - Required when O(secret_type=docker_config), this is the username of the Docker registry.
      - Mutually exclusive with O(data).
    type: str
    required: false
  registry_password:
    description:
      - Required when O(secret_type=docker_config), this is the password of the Docker registry.
      - Mutually exclusive with O(data).
    type: str
    required: false
  secret_name:
    description:
      - Name of the secret.
    type: str
    required: true
  data:
    description:
      - Dictionary of key/value pairs for the secret.
      - The values B(must not) be encoded in C(base64), the module will do that for you.
      - Required when O(secret_type=opaque).
      - Mutually exclusive with O(registry_host), O(registry_username), and O(registry_password).
    type: dict
    required: false
    default: {}
  export:
    description:
      - Whether or not to export the secret across all namespaces, using a C(SecretExport).
    type: bool
    required: false
    default: false
  state:
    description:
      - When V(present) the secret will be added to the cluster if it does not exist.
      - When V(absent) it will be removed if it exists.
      - When V(update) it will be updated if it exists and created if it does not.
      - When V(update) the old fields will be B(erased), so make sure you also specify the old fields!
    default: present
    type: str
    choices: ["present", "absent", "update"]
"""

EXAMPLES = r"""
# Create a new secret at Cluster level
- name: Create and export a new cluster secret
  community.general.tanzu_mission_control_secret:
    api_host: example.tmc.tanzu.broadcom.com
    api_token: "super-secret-api-token"
    cluster_name: test-cluster
    cluster_namespace: default
    management_cluster_name: management-cluster
    provisioner_name: provisioner-name
    secret_name: my-very-secret-secret
    secret_type: opaque
    data:
      first_field: with a value
      multiline_field: |
        You can also create multiline fields (if you want to embed files, for examples)
    export: true
    state: present

# This will lead to a no change, if you want to update a secret you *must* use state=update
- name: Try to recreate the same secret
  community.general.tanzu_mission_control_secret:
    api_host: example.tmc.tanzu.broadcom.com
    api_token: "super-secret-api-token"
    cluster_name: test-cluster
    cluster_namespace: default
    management_cluster_name: management-cluster
    provisioner_name: provisioner-name
    secret_name: my-very-secret-secret
    data:
      some_new_field: some new value
    state: present

# This will erase the previous fields (there is no way to retrieve the old values)
- name: Update a secret
  community.general.tanzu_mission_control_secret:
    api_host: example.tmc.tanzu.broadcom.com
    api_token: "super-secret-api-token"
    cluster_name: test-cluster
    cluster_namespace: default
    management_cluster_name: management-cluster
    provisioner_name: provisioner-name
    secret_name: my-very-secret-secret
    data:
      first_field: with a value
      some_new_field: some new value
    state: update

- name: Delete a secret
  community.general.tanzu_mission_control_secret:
    api_host: example.tmc.tanzu.broadcom.com
    api_token: "super-secret-api-token"
    cluster_name: test-cluster
    cluster_namespace: default
    management_cluster_name: management-cluster
    provisioner_name: provisioner-name
    secret_name: my-very-secret-secret
    state: absent

# This will create a secret of type "kubernetes.io/dockerconfigjson" with the .dockerconfigjson field
- name: Create and export a ClusterGroup Registry secret
  community.general.tanzu_mission_control_secret:
    api_host: example.tmc.tanzu.broadcom.com
    api_token: "super-secret-api-token"
    cluster_group: test-cluster-group
    cluster_namespace: default
    secret_name: my-very-secret-secret
    secret_type: docker_config
    registry_host: docker.io
    registry_username: some_username
    registry_password: some_password
    export: true
    state: present
"""

RETURN = ""

import json
from base64 import b64encode
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url
from ansible.module_utils.common.text.converters import to_bytes, to_native


class TMCSecret(object):
    """Represents a generic secret (either Cluster or ClusterGroup) in TMC."""

    def __init__(self, secret_name, secret_type, cluster_namespace):
        self._secret_name = secret_name
        self._secret_type = (
            "SECRET_TYPE_OPAQUE"
            if secret_type == "opaque"
            else "SECRET_TYPE_DOCKERCONFIGJSON"
        )
        self._cluster_namespace = cluster_namespace

    def exists(self, api_host, access_token):
        raise NotImplementedError()

    def is_exported(self, api_host, access_token):
        raise NotImplementedError()

    def create(self, api_host, access_token, payload):
        raise NotImplementedError()

    def update(self, api_host, access_token, payload):
        raise NotImplementedError()

    def delete(self, api_host, access_token):
        raise NotImplementedError()

    def create_export(self, api_host, access_token):
        raise NotImplementedError()

    def delete_export(self, api_host, access_token):
        raise NotImplementedError()


class TMCClusterGroupSecret(TMCSecret):
    """Represents a ClusterGroup secret in TMC."""

    def __init__(self, cluster_group, cluster_namespace, secret_name, secret_type):
        super().__init__(secret_name, secret_type, cluster_namespace)
        self._cluster_group = cluster_group

    def _generate_query_params(self):
        return urlencode({"fullName.namespaceName": self._cluster_namespace})

    def _generate_url(self, api_host):
        return "https://{}/v1alpha1/clustergroups/{}/namespace/secrets".format(
            api_host, self._cluster_group
        )

    def _get_current_spec(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        response = open_url(
            url,
            headers={"Authorization": "Bearer {}".format(access_token)},
        )

        return json.loads(response.read())

    def _generate_export_url(self, api_host, operation="get"):
        if operation == "get":
            return "https://{}/v1alpha1/clustergroups/{}/namespaces/{}/secretexports".format(
                api_host, self._cluster_namespace, self._cluster_group
            )
        else:
            return (
                "https://{}/v1alpha1/clustergroups/{}/namespace/secretexports".format(
                    api_host, self._cluster_group
                )
            )

    def _prepare_request(self, payload):
        new_payload = {}
        for key, value in payload.items():
            new_payload[key] = to_native(b64encode(to_bytes(value)))

        complete_payload = {
            "secret": {
                "fullName": {
                    "clusterGroupName": self._cluster_group,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace,
                },
                "meta": {},
                "status": {},
                "spec": {
                    "atomicSpec": {"secretType": self._secret_type, "data": new_payload}
                },
            }
        }

        return complete_payload

    def exists(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        auhorization_header = "Bearer {}".format(access_token)
        try:
            open_url(
                url,
                headers={"Authorization": auhorization_header},
            )
            return True
        except HTTPError as e:
            if e.getcode() == 404:
                return False
            raise e

    def create(self, api_host, access_token, payload):
        url = self._generate_url(api_host)
        all_headers = {"Authorization": "Bearer {}".format(access_token)}
        new_payload = to_bytes(json.dumps(self._prepare_request(payload)))

        open_url(url, headers=all_headers, data=new_payload)
        return True, "Secret {}/{} created".format(
            self._cluster_namespace, self._secret_name
        )

    def update(self, api_host, access_token, payload):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = self._prepare_request(payload)
        all_headers = {"Authorization": authorization_header}

        current_spec = self._get_current_spec(api_host, access_token)

        new_payload["secret"]["meta"] = current_spec["secret"]["meta"]
        new_payload["secret"]["type"] = current_spec["secret"]["type"]
        new_payload["secret"]["fullName"] = current_spec["secret"]["fullName"]

        new_payload = to_bytes(json.dumps(new_payload))

        open_url(url, method="PUT", headers=all_headers, data=new_payload)
        return True, "Secret {}/{} updated".format(
            self._cluster_namespace, self._secret_name
        )

    def delete(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        authorization_header = "Bearer {}".format(access_token)

        open_url(
            url,
            method="DELETE",
            headers={"Authorization": authorization_header},
        )
        return True, "Secret {}/{} deleted".format(
            self._cluster_namespace, self._secret_name
        )

    def is_exported(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        try:
            open_url(url, headers=authorization_header)
            return True
        except HTTPError as e:
            if e.getcode() == 404:
                return False
            raise e

    def create_export(self, api_host, access_token):
        url = self._generate_export_url(api_host, operation="create")
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        payload = {
            "secretExport": {
                "fullName": {
                    "clusterGroupName": self._cluster_group,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace,
                }
            }
        }

        payload = to_bytes(json.dumps(payload))

        open_url(url, headers=authorization_header, data=payload)
        return True, "SecretExport for {}/{} created".format(
            self._cluster_namespace, self._secret_name
        )

    def delete_export(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        open_url(url, method="DELETE", headers=authorization_header)
        return True, "SecretExport for {}/{} deleted".format(
            self._cluster_namespace, self._secret_name
        )


class TMCClusterSecret(TMCSecret):
    """Represents a Cluster Secret in TMC."""

    def __init__(
        self,
        management_cluster_name,
        provisioner_name,
        cluster_name,
        cluster_namespace,
        secret_name,
        secret_type,
    ):
        super().__init__(secret_name, secret_type, cluster_namespace)
        self._management_cluster_name = management_cluster_name
        self._provisioner_name = provisioner_name
        self._cluster_name = cluster_name

    def _get_current_spec(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        response = open_url(
            url,
            headers={"Authorization": "Bearer {}".format(access_token)},
        )

        return json.loads(response.read())

    def _generate_export_url(self, api_host):
        return "https://{}/v1alpha1/clusters/{}/namespaces/{}/secretexports".format(
            api_host, self._cluster_name, self._cluster_namespace
        )

    def _generate_url(self, api_host):
        return "https://{}/v1alpha1/clusters/{}/namespaces/{}/secrets".format(
            api_host, self._cluster_name, self._cluster_namespace
        )

    def _generate_query_params(self):
        return urlencode(
            {
                "fullName.managementClusterName": self._management_cluster_name,
                "fullName.provisionerName": self._provisioner_name,
            }
        )

    def _prepare_request(self, payload):
        new_payload = {}
        for key, value in payload.items():
            new_payload[key] = to_native(b64encode(to_bytes(value)))

        complete_payload = {
            "secret": {
                "fullName": {
                    "clusterName": self._cluster_name,
                    "managementClusterName": self._management_cluster_name,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace,
                    "provisionerName": self._provisioner_name,
                },
                "meta": {},
                "status": {},
                "spec": {"secretType": self._secret_type, "data": new_payload},
            }
        }

        return complete_payload

    def exists(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        authorization_header = "Bearer {}".format(access_token)
        try:
            open_url(
                url,
                headers={"Authorization": authorization_header},
            )
            return True
        except HTTPError as e:
            if e.getcode() == 404:
                return False
            raise e

    def create(self, api_host, access_token, payload):
        url = self._generate_url(api_host)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = to_bytes(json.dumps(self._prepare_request(payload)))
        all_headers = {"Authorization": authorization_header}

        open_url(url, headers=all_headers, data=new_payload)
        return True, "Secret {}/{} created".format(
            self._cluster_namespace, self._secret_name
        )

    def update(self, api_host, access_token, payload):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = self._prepare_request(payload)
        all_headers = {"Authorization": authorization_header}

        current_spec = self._get_current_spec(api_host, access_token)

        new_payload["secret"]["meta"] = current_spec["secret"]["meta"]
        new_payload["secret"]["type"] = current_spec["secret"]["type"]
        new_payload["secret"]["fullName"] = current_spec["secret"]["fullName"]

        new_payload = to_bytes(json.dumps(new_payload))

        open_url(url, method="PUT", headers=all_headers, data=new_payload)
        return True, "Secret {}/{} updated".format(
            self._cluster_namespace, self._secret_name
        )

    def delete(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        authorization_header = "Bearer {}".format(access_token)

        open_url(
            url,
            method="DELETE",
            headers={"Authorization": authorization_header},
        )
        return True, "Secret {}/{} deleted".format(
            self._cluster_namespace, self._secret_name
        )

    def is_exported(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_export_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        try:
            open_url(
                url,
                headers=authorization_header,
            )
            return True
        except HTTPError as e:
            if e.getcode() == 404:
                return False
            raise e

    def create_export(self, api_host, access_token):
        url = self._generate_export_url(api_host)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        payload = {
            "secretExport": {
                "fullName": {
                    "clusterName": self._cluster_name,
                    "managementClusterName": self._management_cluster_name,
                    "provisionerName": self._provisioner_name,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace,
                }
            }
        }

        payload = to_bytes(json.dumps(payload))

        open_url(url, headers=authorization_header, data=payload)
        return True, "SecretExport for {}/{} created".format(
            self._cluster_namespace, self._secret_name
        )

    def delete_export(self, api_host, access_token):
        url = "{}/{}?{}".format(
            self._generate_export_url(api_host),
            self._secret_name,
            self._generate_query_params(),
        )
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        open_url(
            url,
            method="DELETE",
            headers=authorization_header,
        )
        return True, "SecretExport for {}/{} deleted".format(
            self._cluster_namespace, self._secret_name
        )


def exchange_token(api_token):
    exchange_url = "https://console.tanzu.broadcom.com/csp/gateway/am/api/auth/api-tokens/authorize"
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    data = urlencode({"api_token": api_token})

    exchange_result = open_url(
        exchange_url,
        data=data,
        headers=headers,
    )

    raw_data = json.loads(exchange_result.read())
    return None if "access_token" not in raw_data else raw_data["access_token"]


def handle_logic(secret_status, wished_state):
    if secret_status and wished_state == "present":
        return "do_nothing"

    if secret_status and wished_state == "update":
        return "force_update"

    if secret_status and wished_state == "absent":
        return "delete"

    if not secret_status and wished_state == "present" or wished_state == "update":
        return "create"

    if not secret_status and wished_state == "absent":
        return "do_nothing"

    return "error"


def load_module():
    argument_spec = dict(
        api_host=dict(type="str", required=True),
        api_token=dict(type="str", required=True, no_log=True),
        management_cluster_name=dict(type="str"),
        provisioner_name=dict(type="str"),
        cluster_name=dict(type="str"),
        cluster_namespace=dict(type="str", required=True),
        cluster_group=dict(type="str"),
        secret_name=dict(type="str", required=True),
        registry_host=dict(type="str"),
        registry_username=dict(type="str"),
        registry_password=dict(type="str", no_log=True),
        secret_type=dict(
            type="str",
            choices=["opaque", "docker_config"],
            default="opaque",
        ),
        data=dict(type="dict", default={}),
        export=dict(type="bool", default=False),
        state=dict(
            type="str", default="present", choices=["present", "absent", "update"]
        ),
    )

    return AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ["cluster_group", "cluster_name"],
            ["cluster_group", "management_cluster_name"],
            ["cluster_group", "provisioner_name"],
            ["data", "registry_host"],
            ["data", "registry_username"],
            ["data", "registry_password"],
        ],
        required_one_of=[
            ["cluster_name", "cluster_group"],
            ["data", "registry_host"],
            ["data", "registry_username"],
            ["data", "registry_password"],
        ],
        required_together=[
            ["cluster_name", "management_cluster_name", "provisioner_name"],
            ["registry_host", "registry_username", "registry_password"],
        ],
    )


def create_dockerconfig(registry_host, registry_username, registry_password):
    payload = {
        "auths": {
            registry_host: {
                "username": registry_username,
                "password": registry_password,
                "auth": to_native(
                    b64encode(
                        to_bytes("{}:{}".format(registry_username, registry_password))
                    )
                ),
            }
        }
    }
    return {".dockerconfigjson": json.dumps(payload)}


def main():
    module = load_module()

    state = module.params["state"]
    api_host = module.params["api_host"]
    api_token = module.params["api_token"]
    cluster_name = module.params["cluster_name"]
    cluster_namespace = module.params["cluster_namespace"]
    management_cluster_name = module.params["management_cluster_name"]
    provisioner_name = module.params["provisioner_name"]
    secret_name = module.params["secret_name"]
    data = module.params["data"]
    cluster_group = module.params["cluster_group"]
    secret_type = module.params["secret_type"]
    export = module.params["export"]

    try:
        access_token = exchange_token(api_token)
        if access_token is None:
            return module.fail_json(msg="Failed to exchange token, check credentials")
    except HTTPError as e:
        return module.fail_json(msg=to_native(e.read()))

    tmc_secret = None

    if cluster_name is not None:
        tmc_secret = TMCClusterSecret(
            management_cluster_name,
            provisioner_name,
            cluster_name,
            cluster_namespace,
            secret_name,
            secret_type,
        )
    else:
        tmc_secret = TMCClusterGroupSecret(
            cluster_group, cluster_namespace, secret_name, secret_type
        )

    if secret_type == "SECRET_TYPE_OPAQUE":
        payload = data
    else:
        payload = create_dockerconfig(
            module.params["registry_host"],
            module.params["registry_username"],
            module.params["registry_password"],
        )

    secret_status = tmc_secret.exists(api_host, access_token)
    action = handle_logic(secret_status, state)
    created, create_msg = False, ""

    try:
        if action == "do_nothing":
            return module.exit_json(changed=False)

        if action == "delete":
            changed, msg = tmc_secret.delete(api_host, access_token)
            return module.exit_json(changed=changed, msg=msg)

        if action == "force_update":
            created, create_msg = tmc_secret.update(api_host, access_token, payload)
        elif action == "create":
            created, create_msg = tmc_secret.create(api_host, access_token, payload)
        else:
            return module.fail_json(msg="Unknown action {}".format(action))

        exported, export_msg = False, ""

        if export and not tmc_secret.is_exported(api_host, access_token):
            exported, export_msg = tmc_secret.create_export(api_host, access_token)

        if not export and tmc_secret.is_exported(api_host, access_token):
            exported, export_msg = tmc_secret.delete_export(api_host, access_token)

        final_changed = created or exported
        final_msg = (
            create_msg
            if export_msg == ""
            else "{} and {}".format(create_msg, export_msg)
        )
        return module.exit_json(changed=final_changed, msg=final_msg)
    except HTTPError as e:
        return module.fail_json(msg=to_native(e.read()))


if __name__ == "__main__":
    main()
