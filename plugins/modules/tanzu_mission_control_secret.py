#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Massimo Gengarelli (massimo.gengarelli@proton.me)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: tanzu_mission_control_secret
short_description: Manages Cluster, Cluster Group Secrets and SecretExports in Tanzu Mission Control.
version_added: 11.0.0
description:
  - Create and revokes Cluster and Cluster Group Secrets in Tanzu Mission Control for a given Cluster.
  - Creates and removes SecretExports for the given secret in Tanzu Mission Control.
author:
  - Massimo Gengarelli (@massix)
requirements: [requests]
notes:
  - To obtain an api_token, go into the TMC UI, click on your user, then settings and then generate an API token.
  - The generated API token *must* have the rights to create Secrets and SecretExports in TMC.
  - This has only been tested using TMC SaaS, but it should also work with TMC self hosted.

options:
  api_host:
    description:
      - Full URL of the TMC instance without the protocol (i.e. tmc.example.com)
    required: true
    type: str
  api_token:
    description:
      - Automation token retrieved from TMC to access the API, the token *must* have the `secrets` scope.
    required: true
    type: str
  management_cluster_name:
    description:
      - Name of the management cluster which monitors the cluster_name
      - Not required when using cluster_group
    required: false
    type: str
  provisioner_name:
    description:
      - Name of the provisioner used for the cluster
      - Not required when using cluster_group
    required: false
    type: str
  cluster_name:
    description:
      - Name of an existing cluster where the secret will be created
      - Cannot be used together with cluster_group
    required: false
    type: str
  cluster_group:
    description:
      - Name of an existing cluster group where this secret will be created
      - Cannot be used together with cluster_name
    required: false
    type: str
  cluster_namespace:
    description:
      - An existing namespace inside the cluster (or cluster group) where the secret will be created.
    required: true
    type: str
  secret_type:
    description:
      - Type of the created secret
    type: str
    choices: ["SECRET_TYPE_OPAQUE", "SECRET_TYPE_DOCKERCONFIGJSON"]
    default: SECRET_TYPE_OPAQUE
    required: false
  registry_host:
    description:
      - When creating a secret of type V(SECRET_TYPE_DOCKER), this is the host of the Docker registry.
      - Not accepted when creating a secret of type V(SECRET_TYPE_OPAQUE)
      - One of data or registry_host, registry_username, and registry_password is required
    type: str
    required: false
  registry_username:
    description:
      - When creating a secret of type V(SECRET_TYPE_DOCKER), this is the username of the Docker registry.
      - Not accepted when creating a secret of type V(SECRET_TYPE_OPAQUE)
      - One of data or registry_host, registry_username and registry_password is required
    type: str
    required: false
  registry_password:
    description:
      - When creating a secret of type V(SECRET_TYPE_DOCKER), this is the password of the Docker registry.
      - Not accepted when creating a secret of type V(SECRET_TYPE_OPAQUE)
      - One of data or registry_host, registry_username, and registry_password is required
    type: str
    required: false
  secret_name:
    description:
     - Name of the secret
    type: str
    required: true
  data:
    description:
      - The content of the secret. You do not need to base64_encode the values, the module will do that for you.
      - Not accepted when creating a secret of type V(SECRET_TYPE_DOCKER).
      - One of data or registry_host, registry_username, and registry_password is required.
      - All the values *must* be strings.
    type: dict
    required: false
    default: {}
  export:
    description:
      - Whether or not to create a SecretExport resource too when creating the secret.
    type: bool
    required: false
    default: false
  state:
    description:
      - When V(present) the secret will be added to the cluster if it does not exist.
      - When V(absent) it will be removed if it exists.
      - When V(update) it will be updated if it exists and created if it does not.
      - When V(update) the old fields will be *erased*, so make sure you also specify the old fields!
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
    secret_type: SECRET_TYPE_OPAQUE
    data:
      first_field: with a value
      multiline_field: |
        You can also create multiline fields (if you want to embed files, for examples)
    export: true
    state: present

# This won't actually work, if you want to update a secret you *must* use state=update
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

# This will *erase* the previous fields (there is no way to retrieve the old values)
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
    secret_type: SECRET_TYPE_DOCKERCONFIGJSON
    registry_host: docker.io
    registry_username: some_username
    registry_password: some_password
    export: true
    state: present
"""

RETURN = r"""
"""

from base64 import b64encode
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("requests"):
    from requests import delete, get, post, put


class TMCSecret(object):
    """Represents a generic secret (either Cluster or ClusterGroup) in TMC."""

    def __init__(self, secret_name, secret_type, cluster_namespace):
        self._secret_name = secret_name
        self._secret_type = secret_type
        self._cluster_namespace = cluster_namespace

    def exists(self, api_host, access_token):
        """
        Checks if the secret exists.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.

        Returns:
            bool: Whether the token exists or not.
        """

        raise NotImplementedError("Cannot call this method of the base class")

    def is_exported(self, api_host, access_token):
        """
        Checks if the secret is exported.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.

        Returns:
            bool: Whether the secret is exported or not.
        """

        raise NotImplementedError("Cannot call this method of the base class")

    def create(self, api_host, access_token, payload):
        """
        Creates the given secret in TMC.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.
            payload (dict[str, str]): The secret payload, the values *must not* be encoded in base64.

        Returns:
            tuple[bool, str]: True if the secret was created, False otherwise, the string is a comprehensive message.
        """
        raise NotImplementedError("Cannot call this method of the base class")

    def update(self, api_host, access_token, payload):
        """
        Updates the given secret in TMC, *replacing* the existing data.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.
            payload (dict[str, str]): The secret payload, the values *must not* be encoded in base64.

        Returns:
            tuple[bool, str]: True if the secret was updated, False otherwise, the string is a comprehensive message.
        """
        raise NotImplementedError("Cannot call this method of the base class")

    def delete(self, api_host, access_token):
        """
        Deletes the given secret in TMC.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.

        Returns:
            tuple[bool, str]: True if the secret was deleted, False otherwise, the string is a comprehensive message.
        """
        raise NotImplementedError("Cannot call this method of the base class")

    def create_export(self, api_host, access_token):
        """
        Creates a SecretExport for the given secret in TMC.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.
            export_state (bool): Whether the secret should be exported or not.

        Returns:
            tuple[bool, str]: True if the secret was exported, False otherwise, the string is a comprehensive message.
        """

        raise NotImplementedError("Cannot call this method of the base class")

    def delete_export(self, api_host, access_token):
        """
        Deletes the SecretExport for the given secret in TMC.

        Args:
            api_host (str): TMC API Host for SaaS interaction.
            access_token (str): The access token, retrieved after the exchange.

        Returns:
            tuple[bool, str]: True if the SecretExport was removed, False otherwise, the string is a comprehensive message.
        """

        raise NotImplementedError("Cannot call this method of the base class")


class TMCClusterGroupSecret(TMCSecret):
    """Represents a ClusterGroup secret in TMC."""

    def __init__(self, cluster_group, cluster_namespace, secret_name, secret_type):
        super().__init__(secret_name, secret_type, cluster_namespace)
        self._cluster_group = cluster_group

    def _generate_query_params(self):
        return {
            "fullName.namespaceName": self._cluster_namespace
        }

    def _generate_url(self, api_host):
        return "https://{}/v1alpha1/clustergroups/{}/namespace/secrets".format(api_host, self._cluster_group)

    def _get_current_spec(self, api_host, access_token):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        response = get(url, params=self._generate_query_params(), headers={"Authorization": "Bearer {}".format(access_token)}, timeout=5000)

        return response.json()

    def _generate_export_url(self, api_host):
        return "https://{}/v1alpha1/clustergroups/{}/namespace/secretexports".format(api_host, self._cluster_group)

    def _prepare_request(self, payload):
        new_payload = {}
        for key, value in payload.items():
            new_payload[key] = b64encode(value.encode()).decode()

        complete_payload = {
            "secret": {
                "fullName": {
                    "clusterGroupName": self._cluster_group,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace
                },
                "meta": {},
                "status": {},
                "spec": {
                    "atomicSpec": {
                        "secretType": self._secret_type,
                        "data": new_payload
                    }
                },
            }
        }

        return complete_payload

    def exists(self, api_host, access_token):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        auhorization_header = "Bearer {}".format(access_token)
        result = get(url, headers={"Authorization": auhorization_header}, timeout=5000, params=self._generate_query_params())
        return result.status_code == 200

    def create(self, api_host, access_token, payload):
        url = self._generate_url(api_host)
        all_headers = {"Authorization": "Bearer {}".format(access_token)}
        new_payload = self._prepare_request(payload)

        response = post(url, headers=all_headers, json=new_payload, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} created".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def update(self, api_host, access_token, payload):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = self._prepare_request(payload)
        all_headers = {"Authorization": authorization_header}

        current_spec = self._get_current_spec(api_host, access_token)

        new_payload["secret"]["meta"] = current_spec["secret"]["meta"]
        new_payload["secret"]["type"] = current_spec["secret"]["type"]
        new_payload["secret"]["fullName"] = current_spec["secret"]["fullName"]

        response = put(url, headers=all_headers, json=new_payload, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} updated".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def delete(self, api_host, access_token):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)

        response = delete(url, params=self._generate_query_params(), headers={"Authorization": authorization_header}, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} deleted".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def is_exported(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        response = get(url, headers=authorization_header, timeout=5000)
        return response.status_code == 200

    def create_export(self, api_host, access_token):
        url = self._generate_export_url(api_host)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        payload = {
            "secretExport": {
                "fullName": {
                    "clusterGroupName": self._cluster_group,
                    "name": self._secret_name,
                    "namespaceName": self._cluster_namespace
                }
            }
        }

        response = post(url, headers=authorization_header, json=payload, timeout=5000)
        if response.status_code == 200:
            return True, "SecretExport for {}/{} created".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def delete_export(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        response = delete(url, headers=authorization_header, timeout=5000)
        if response.status_code == 200:
            return True, "SecretExport for {}/{} deleted".format(self._cluster_namespace, self._secret_name)

        return False, response.text


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
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        response = get(url, params=self._generate_query_params(), headers={"Authorization": "Bearer {}".format(access_token)}, timeout=5000)

        return response.json()

    def _generate_export_url(self, api_host):
        return "https://{}/v1alpha1/clusters/{}/namespaces/{}/secretexports".format(api_host, self._cluster_name, self._cluster_namespace)

    def _generate_url(self, api_host):
        return "https://{}/v1alpha1/clusters/{}/namespaces/{}/secrets".format(api_host, self._cluster_name, self._cluster_namespace)

    def _generate_query_params(self):
        return {
            "fullName.managementClusterName": self._management_cluster_name,
            "fullName.provisionerName": self._provisioner_name,
        }

    def _prepare_request(self, payload):
        new_payload = {}
        for key, value in payload.items():
            new_payload[key] = b64encode(value.encode()).decode()

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
                "spec": {
                    "secretType": self._secret_type,
                    "data": new_payload
                },
            }
        }

        return complete_payload

    def exists(self, api_host, access_token):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)
        result = get(url, headers={"Authorization": authorization_header}, timeout=5000, params=self._generate_query_params())
        return result.status_code == 200

    def create(self, api_host, access_token, payload):
        url = self._generate_url(api_host)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = self._prepare_request(payload)
        all_headers = {"Authorization": authorization_header}

        response = post(url, headers=all_headers, json=new_payload, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} created".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def update(self, api_host, access_token, payload):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)
        new_payload = self._prepare_request(payload)
        all_headers = {"Authorization": authorization_header}

        current_spec = self._get_current_spec(api_host, access_token)

        new_payload["secret"]["meta"] = current_spec["secret"]["meta"]
        new_payload["secret"]["type"] = current_spec["secret"]["type"]
        new_payload["secret"]["fullName"] = current_spec["secret"]["fullName"]

        response = put(url, headers=all_headers, json=new_payload, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} updated".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def delete(self, api_host, access_token):
        url = "{}/{}".format(self._generate_url(api_host), self._secret_name)
        authorization_header = "Bearer {}".format(access_token)

        response = delete(url, params=self._generate_query_params(), headers={"Authorization": authorization_header}, timeout=5000)
        if response.status_code == 200:
            return True, "Secret {}/{} deleted".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def is_exported(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        response = get(url, params=self._generate_query_params(), headers=authorization_header, timeout=5000)
        return response.status_code == 200

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
                    "namespaceName": self._cluster_namespace
                }
            }
        }

        response = post(url, headers=authorization_header, json=payload, timeout=5000)
        if response.status_code == 200:
            return True, "SecretExport for {}/{} created".format(self._cluster_namespace, self._secret_name)

        return False, response.text

    def delete_export(self, api_host, access_token):
        url = "{}/{}".format(self._generate_export_url(api_host), self._secret_name)
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        response = delete(url, headers=authorization_header, params=self._generate_query_params(), timeout=5000)
        if response.status_code == 200:
            return True, "SecretExport for {}/{} deleted".format(self._cluster_namespace, self._secret_name)

        return False, response.text


def exchange_token(api_token):
    """
    Exchanges an api_token for an access_token using the Tanzu SaaS API.

    Args:
        api_token (str): The api_token to exchange.

    Returns:
        str | None: The access_token if successful, None otherwise.
    """

    exchange_url = "https://console.tanzu.broadcom.com/csp/gateway/am/api/auth/api-tokens/authorize"
    content_type = "application/x-www-form-urlencoded"
    data = {"api_token": api_token}

    exchange_result = post(exchange_url, data, headers={"Content-Type": content_type}, timeout=5000)
    if exchange_result.status_code == 200:
        raw_data = exchange_result.json()
        return None if "access_token" not in raw_data else raw_data["access_token"]

    return None


def handle_logic(secret_status, wished_state):
    """
    Handles the logic for the module.

    Args:
        secret_status (bool): True if the secret exists, False otherwise.
        wished_state (str): The desired state of the secret.

    Returns:
        str: The action to take.
    """

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
        management_cluster_name=dict(type="str", required=False),
        provisioner_name=dict(type="str", required=False),
        cluster_name=dict(type="str", required=False),
        cluster_namespace=dict(type="str", required=True),
        cluster_group=dict(type="str", required=False),
        secret_name=dict(type="str", required=True),
        registry_host=dict(type="str", required=False),
        registry_username=dict(type="str", required=False),
        registry_password=dict(type="str", required=False, no_log=True),
        secret_type=dict(
            type="str",
            choices=["SECRET_TYPE_OPAQUE", "SECRET_TYPE_DOCKERCONFIGJSON"],
            default="SECRET_TYPE_OPAQUE",
        ),
        data=dict(type="dict", required=False, default={}),
        export=dict(type="bool", default=False),
        state=dict(type="str", default="present", choices=["present", "absent", "update"]),
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
            ["data", "registry_username"],
            ["data", "registry_password"],
            ["data", "registry_password"],
        ],
        required_together=[
            ["cluster_name", "management_cluster_name", "provisioner_name"],
            ["registry_host", "registry_username", "registry_password"],
        ]
    )


def create_dockerconfig(registry_host, registry_username, registry_password):
    """
    When using the Docker secret type, we ignore the data parameter and create a special payload,
    which corresponds to a classic dockerconfig.json file.

    Args:
        registry_host (str): The registry host.
        registry_username (str): The registry username.
        registry_password (str): The registry password.

    Returns:
        dict[str, str]: The payload.
    """
    payload = {
        "auths": {
            registry_host: {
                "username": registry_username,
                "password": registry_password,
                "auth": b64encode("{}:{}".format(registry_username, registry_password).encode()).decode(),
            }
        }
    }
    return {
        ".dockerconfigjson": json.dumps(payload)
    }


def main():
    """Main entrypoint of the module."""

    module = load_module()

    def key_or_none(param_name):
        if param_name in module.params:
            return module.params[param_name]
        return None

    state = module.params["state"]
    api_host = module.params["api_host"]
    api_token = module.params["api_token"]
    cluster_name = key_or_none("cluster_name")
    cluster_namespace = module.params["cluster_namespace"]
    management_cluster_name = key_or_none("management_cluster_name")
    provisioner_name = key_or_none("provisioner_name")
    secret_name = module.params["secret_name"]
    data = module.params["data"]
    cluster_group = key_or_none("cluster_group")
    secret_type = module.params["secret_type"]
    export = module.params["export"]

    access_token = exchange_token(api_token)

    if access_token is None:
        module.fail_json(msg="Failed to exchange token with TMC APIs -- check that the token you provided is valid.")

    tmc_secret = None

    if cluster_name is not None:
        tmc_secret = TMCClusterSecret(
            str(management_cluster_name),
            str(provisioner_name),
            cluster_name,
            cluster_namespace,
            secret_name,
            secret_type,
        )
    else:
        tmc_secret = TMCClusterGroupSecret(
            str(cluster_group),
            cluster_namespace,
            secret_name,
            secret_type
        )

    if secret_type == "SECRET_TYPE_OPAQUE":
        payload = data
    else:
        payload = create_dockerconfig(
            module.params["registry_host"],
            module.params["registry_username"],
            module.params["registry_password"])

    secret_status = tmc_secret.exists(api_host, access_token)
    action = handle_logic(secret_status, state)
    created, create_msg = False, ""

    if action == "do_nothing":
        module.exit_json(changed=False)
    elif action == "force_update":
        changed, msg = tmc_secret.update(api_host, access_token, payload)
        if not changed:
            return module.fail_json(msg=msg)

        created, create_msg = changed, msg
    elif action == "create":
        changed, msg = tmc_secret.create(api_host, access_token, payload)
        if not changed:
            return module.fail_json(msg=msg)

        created, create_msg = changed, msg
    elif action == "delete":
        changed, msg = tmc_secret.delete(api_host, access_token)
        if not changed:
            return module.fail_json(msg=msg)

        return module.exit_json(changed=changed, msg=msg)
    else:
        module.fail_json(msg="Unknown action {}".format(action))

    exported, export_msg = False, ""

    if export and not tmc_secret.is_exported(api_host, access_token):
        exported, export_msg = tmc_secret.create_export(api_host, access_token)

    if not export and tmc_secret.is_exported(api_host, access_token):
        exported, export_msg = tmc_secret.delete_export(api_host, access_token)

    final_changed = created or exported
    final_msg = create_msg if export_msg == "" else create_msg + " and " + export_msg
    return module.exit_json(changed=final_changed, msg=final_msg)


if __name__ == "__main__":
    main()
