#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: jenkins_credential
short_description: Manage Jenkins credentials and domains via API
version_added: 1.0.0
description:
  - This module allows managing Jenkins credentials and domain scopes via Jenkins HTTP API.
  - You can create, update, and delete different credential types such as username/password, secret text, SSH key, certificates, GitHub App, and scoped domains.
  - For scoped credentials, it supports hostname, hostname:port, path, and scheme-based restrictions.
requirements:
  - requests
author:
  - Youssef Ali (@YoussefKhalidAli)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
    details:
      - Module fully supports check mode and will report changes without making them
  diff_mode:
    support: none
options:
  id:
    description:
      - The ID the Jenkins credential or domain.
    required: true
    type: str
  type:
    description:
      - Type of the credential or action.
    choices:
      - userAndPass
      - file
      - text
      - githubApp
      - sshKey
      - certificate
      - scope
    type: str
  command:
    description:
      - The operation to perform.
    choices: [add, delete, update]
    default: add
    type: str
  scope:
    description:
      - Jenkins credential domain scope.
    type: str
    default: '_'
  url:
    description:
      - Jenkins server URL.
    type: str
    default: http://localhost:8080
  jenkinsUser:
    description:
      - Jenkins user for authentication.
    required: true
    type: str
  token:
    description:
      - Jenkins API token.
    required: true
    type: str
  description:
    description:
      - Optional description of the credential or domain.
    default: ''
    type: str
  username:
    description:
      - Username for credentials that require it (e.g., sshKey, userAndPass).
    type: str
  password:
    description:
      - Password or secret text.
    type: str
  secret:
    description:
      - Secret text (used in "text" type).
    type: str
  appID:
    description:
      - GitHub App ID.
    type: str
  owner:
    description:
      - GitHub App owner.
    type: str
  filePath:
    description:
      - File path to secret (e.g., private key, certificate).
    type: str
  privateKeyPath:
    description:
      - Path to private key file for PEM certificates.
    type: str
  passphrase:
    description:
      - SSH passphrase if exists.
    type: str
  incHostName:
    description:
      - List of hostnames to include in scope.
    type: list
    elements: str
  excHostName:
    description:
      - List of hostnames to exclude from scope.
    type: list
    elements: str
  incHostNamePort:
    description:
      - List of host:port to include in scope.
    type: list
    elements: str
  excHostNamePort:
    description:
      - List of host:port to exclude from scope.
    type: list
    elements: str
  incPath:
    description:
      - List of URL paths to include.
    type: list
    elements: str
  excPath:
    description:
      - List of URL paths to exclude.
    type: list
    elements: str
  schemes:
    description:
      - List of schemes (e.g., http, https) to match.
    type: list
    elements: str
"""

EXAMPLES = r"""
    - name: Add CUSTOM scope credential
      jenkins_credential:
        id: "CUSTOM"
        type: "scope"
        jenkinsUser: "admin"
        token: "token"
        description: "Custom scope credential"
        incPath:
          - "include/path"
          - "include/path2"
        excPath:
          - "exclude/path"
          - "exclude/path2"
        incHostName:
          - "included-hostname"
          - "included-hostname2"
        excHostName:
          - "excluded-hostname"
          - "excluded-hostname2"
        schemes:
          - "http"
          - "https"
        incHostNamePort:
          - "included-hostname:7000"
          - "included-hostname2:7000"
        excHostNamePort:
          - "excluded-hostname:7000"
          - "excluded-hostname2:7000"

    - name: Add userAndPass credential
      jenkins_credential:
        scope: "CUSTOM"
        id: "userpass-id"
        type: "userAndPass"
        jenkinsUser: "admin"
        token: "token"
        description: "User and password credential"
        username: "user1"
        password: "pass1"

    - name: Add file credential
      jenkins_credential:
        id: "file-id"
        type: "file"
        jenkinsUser: "admin"
        token: "token"
        description: "File credential"
        filePath: "my-secret.pem"

    - name: Add text credential
      jenkins_credential:
        id: "text-id"
        type: "text"
        jenkinsUser: "admin"
        token: "token"
        description: "Text credential"
        secret: "mysecrettext"

    - name: Add githubApp credential
      jenkins_credential:
        id: "githubapp-id"
        type: "githubApp"
        jenkinsUser: "admin"
        token: "token"
        description: "GitHub App credential"
        appID: "12345"
        filePath: "my-secret.pem"
        owner: "github_owner"

    - name: Add sshKey credential
      jenkins_credential:
        id: "sshkey-id"
        type: "sshKey"
        jenkinsUser: "admin"
        token: "token"
        description: "SSH key credential"
        username: "sshuser"
        filePath: "my-secret.pem"
        passphrase: "passphrase"

    - name: Add certificate credential (p12)
      jenkins_credential:
        id: "certificate-id"
        type: "certificate"
        jenkinsUser: "admin"
        token: "token"
        description: "Certificate credential"
        password: "12345678901234"
        filePath: "certificate.p12"

    - name: Add certificate credential (pem)
      jenkins_credential:
        id: "certificate-id-pem"
        type: "certificate"
        jenkinsUser: "admin"
        token: "token"
        description: "Certificate credential (pem)"
        filePath: "cert.pem"
        privateKeyPath: "private.key"

    - name: Delete credential
      jenkins_credential:
        id: "credential-id"
        command: "delete"
        jenkinsUser: "admin"
        token: "{{ token }}"

    - name: Delete scope
      jenkins_credential:
        id: "scope-id"
        command: "delete"
        type: "scope"
        jenkinsUser: "ruff"
        token: "{{ token }}"

"""
# Edit is done the same way as the add command except that the "command" parameter is set to "update".
# The rest of the parameters are the same as for the add command.(id must be the same as the one used to add the credential)

RETURN = r"""
changed:
    description: Whether a change was made.
    type: bool
    returned: always
message:
    description: Message of the result of the operation.
    type: str
    returned: always
details:
    description: Incase of errors return more details
    type: str
    returned: Error
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

import json
import os
import base64
import urllib
import traceback

REQUESTS_IMP_ERR = None
try:
    import requests
    from requests.auth import HTTPBasicAuth

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS = False


# Gets the Jenkins crumb for CSRF protection which is required for API calls
def get_jenkins_crumb(url, user, token):
    # Fetch Jenkins crumb from the crumb issuer API using requests.
    crumb_url = f"{url}/crumbIssuer/api/json"

    try:
        response = requests.get(crumb_url, auth=HTTPBasicAuth(user, token))
        response.raise_for_status()
        data = response.json()
        return data["crumbRequestField"], data["crumb"]
    except requests.RequestException as e:
        return None, None


# Function to check if credential exists
def credential_exists(url, scope, name, user, token):
    # Check if a Jenkins credential exists using requests.
    check_url = (
        f"{url}/credentials/store/system/domain/{scope}/credential/{name}/api/json"
    )

    try:
        response = requests.get(check_url, auth=HTTPBasicAuth(user, token))
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        raise


# Function to check if domain (scope) exists
def domain_exists(url, name, user, token):
    # Check if a Jenkins domain (scope) exists using requests.
    check_url = f"{url}/credentials/store/system/domain/{name}/api/json"

    try:
        response = requests.get(check_url, auth=HTTPBasicAuth(user, token))
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        raise


# Function to clean the data sent via API by removing unwanted keys and None values
def clean_data(data):
    # Keys to remove (including those with None values)
    keys_to_remove = {
        "url",
        "token",
        "jenkinsUser",
        "filePath",
        "type",
        "command",
        "scope",
    }

    # Filter out None values and unwanted keys
    cleaned_data = {
        key: value
        for key, value in data.items()
        if value is not None and key not in keys_to_remove
    }

    return cleaned_data


def validate_required_fields(module, cred_type):
    # Validate required fields based on credential type and check file existence.
    required_fields_map = {
        "userAndPass": ["username", "password"],
        "file": ["filePath"],
        "text": ["secret"],
        "githubApp": ["appID", "filePath"],
        "sshKey": ["username", "filePath"],
        "certificate": ["filePath"],  # special case handled below
    }

    params = module.params
    missing = []
    file_check_fields = ["filePath", "privateKeyPath"]

    # Basic param presence validation
    for field in required_fields_map.get(cred_type, []):
        if not params.get(field):
            missing.append(field)

    # Extra logic for certificate type
    if cred_type == "certificate" and params.get("filePath"):
        ext = os.path.splitext(params["filePath"])[1].lower()
        if ext in [".p12", ".pfx"] and not params.get("password"):
            missing.append("password")
        elif ext in [".pem", ".crt"] and not params.get("privateKeyPath"):
            missing.append("privateKeyPath")

    # Validate file paths exist on disk
    for field in file_check_fields:
        path = params.get(field)
        if path and not os.path.exists(path):
            module.fail_json(msg=f"File not found: {path}")

    if missing:
        module.fail_json(
            msg=f"Missing required fields for type '{cred_type}': {', '.join(missing)}"
        )


def delete_scope_or_credential(module, url, headers, auth, id, scope, command):
    try:
        if module.params["type"] == "scope":
            delete_url = f"{url}/credentials/store/system/domain/{id}/doDelete"
            headers.pop("Content-Type", None)
            # For deleting a domain (scope), Jenkins expects a POST to doDelete
            response = requests.post(delete_url, headers=headers, auth=auth)

        else:
            delete_url = f"{url}/credentials/store/system/domain/{scope}/credential/{id}/config.xml"
            # For deleting a credential, Jenkins expects a DELETE request
            response = requests.delete(
                delete_url,
                headers=headers,
                auth=auth,
            )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        module.fail_json(
            msg=f"Failed to delete {id} {'before updating' if command == 'update' else ''}",
            details=response.text,
        )


# Main function to run the Ansible module
def run_module():

    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type="str", required=True),  # Id
            type=dict(
                type="str",
                required=False,
                choices=[
                    "userAndPass",
                    "file",
                    "text",
                    "githubApp",
                    "sshKey",
                    "certificate",
                    "scope",
                ],
            ),  # Credential type
            command=dict(
                type="str",
                required=False,
                default="add",
                choices=["add", "delete", "update"],
            ),  # Command to execute
            scope=dict(
                type="str", required=False, default="_"
            ),  # Scope of the credential
            url=dict(
                type="str", required=False, default="http://localhost:8080"
            ),  # Jenkins URL
            jenkinsUser=dict(type="str", required=True),  # Jenkins username
            token=dict(type="str", required=True, no_log=True),  # Jenkins API token
            description=dict(
                type="str", required=False, default=""
            ),  # Description of the credential
            username=dict(
                type="str", required=False
            ),  # Username for userAndPass and sshKey types
            password=dict(
                type="str", required=False, no_log=True
            ),  # Password for userAndPass type
            filePath=dict(
                type="str", required=False, default=None
            ),  # File path for file and sshKey types
            secret=dict(type="str", required=False, no_log=True),  # Text for text type
            appID=dict(type="str", required=False),  # App ID for githubApp type
            owner=dict(type="str", required=False),  # Owner for githubApp type
            passphrase=dict(
                type="str", required=False, no_log=True
            ),  # Passphrase for sshKey type
            privateKeyPath=dict(
                type="str", required=False, no_log=True
            ),  # Private key path for certificate type
            # Scope specifications parameters
            incHostName=dict(
                type="list", required=False, elements="str"
            ),  # Include hostname for scope type
            excHostName=dict(
                type="list", required=False, elements="str"
            ),  # Exclude hostname for scope type
            incHostNamePort=dict(
                type="list", required=False, elements="str"
            ),  # Include hostname and port for scope type
            excHostNamePort=dict(
                type="list", required=False, elements="str"
            ),  # Exclude hostname and port for scope type
            incPath=dict(
                type="list", required=False, elements="str"
            ),  # Include path for scope type
            excPath=dict(
                type="list", required=False, elements="str"
            ),  # Exclude path for scope type
            schemes=dict(
                type="list", required=False, elements="str"
            ),  # Schemes for scope type
        ),
        supports_check_mode=True,
    )

    # Parameters
    id = module.params["id"]
    type = module.params["type"]
    command = module.params["command"]
    scope = module.params["scope"]
    url = module.params["url"]
    jenkinsUser = module.params["jenkinsUser"]
    token = module.params["token"]
    description = module.params["description"]
    filePath = module.params["filePath"]
    privateKeyPath = module.params["privateKeyPath"]
    incHostName = module.params["incHostName"]
    excHostName = module.params["excHostName"]
    incHostNamePort = module.params["incHostNamePort"]
    excHostNamePort = module.params["excHostNamePort"]
    incPath = module.params["incPath"]
    excPath = module.params["excPath"]
    schemes = module.params["schemes"]

    if not HAS_REQUESTS:
        module.fail_json(
            msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR
        )

    if command not in ["add", "delete", "update"]:
        module.fail_json(msg="Invalid command. Use 'add', 'delete', or 'update'.")

    # Get the crumb for CSRF protection
    crumb_field, crumb_value = get_jenkins_crumb(url, jenkinsUser, token)
    if not crumb_field or not crumb_value:
        module.fail_json(
            msg="Failed to fetch Jenkins crumb. Check Jenkins URL and credentials."
        )

    result = dict(
        changed=False,
        message="",
    )

    auth = HTTPBasicAuth(jenkinsUser, token)
    headers = {
        crumb_field: crumb_value,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    credentials = {}

    if not type == "scope":
        does_credential_exist = credential_exists(url, scope, id, jenkinsUser, token)
        # Check if the credential already exists and user want to add
        if does_credential_exist and command == "add":
            result["message"] = f"Credential {id} already exists."
            module.exit_json(**result)

        # Check if the credential doesn't exist and the user wants to delete
        elif not does_credential_exist and command == "delete":
            result["message"] = f"Credential {id} doesn't exist."
            module.exit_json(**result)

    else:
        does_domain_exist = domain_exists(url, id, jenkinsUser, token)
        # Check if the domain already exists and user wants to add
        if does_domain_exist and command == "add":
            result["changed"] = False
            result["message"] = f"Domain {id} already exists."
            module.exit_json(**result)

        # Check if the domain doesn't exist and user wants to delete
        elif not does_domain_exist and command == "delete":
            result["changed"] = False
            result["message"] = f"Domain {id} doesn't exist."
            module.exit_json(**result)

    if command in ["add", "update"]:
        # Check if credential type is provided
        if type is None:
            module.fail_json(msg="Credential type is required for add or update")

        # If updating, we need to delete the existing credential first
        if command == "update":
            if credential_exists(  # Check if credentials exists
                url, scope, id, jenkinsUser, token
            ) or domain_exists(
                url, id, jenkinsUser, token
            ):  # Check if domain exists
                delete_scope_or_credential(
                    module, url, headers, auth, id, scope, command
                )

        if type == "scope":

            specifications = []

            # Create a domain in Jenkins
            if incHostName or excHostName:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.HostnameSpecification",
                        "includes": ",".join(incHostName),
                        "excludes": ",".join(excHostName),
                    }
                )

            if incHostNamePort or excHostNamePort:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.HostnamePortSpecification",
                        "includes": ",".join(incHostNamePort),
                        "excludes": ",".join(excHostNamePort),
                    }
                )

            if schemes:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.SchemeSpecification",
                        "schemes": ",".join(schemes),
                    },
                )

            if incPath or excPath:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.PathSpecification",
                        "includes": ",".join(incPath),
                        "excludes": ",".join(excPath),
                    }
                )

            payload = {
                "name": id,
                "description": description,
                "specifications": specifications,
            }

        else:
            validate_required_fields(module, type)

            credentials = clean_data(module.params)

            if type == "userAndPass":

                credentials.update(
                    {
                        "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
                    }
                )

            elif type == "file":

                credentials.update(
                    {
                        "$class": "org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl",
                        "file": "file0",
                        "fileName": os.path.basename(filePath),
                    }
                )

                headers.pop("Content-Type", None)

                payload = {"": "0", "credentials": credentials}

                with open(filePath, "rb") as f:
                    file_content = f.read()

                    files = {"file0": (os.path.basename(filePath), file_content)}
                    data = {"json": json.dumps(payload)}

            elif type == "text":

                credentials.update(
                    {
                        "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                    }
                )

            elif type == "githubApp":

                try:
                    with open(filePath, "r") as f:
                        private_key = f.read().strip()
                except Exception as e:
                    module.fail_json(msg=f"Failed to read private key file: {str(e)}")

                credentials.update(
                    {
                        "$class": "org.jenkinsci.plugins.github_branch_source.GitHubAppCredentials",
                        "privateKey": private_key,
                        "apiUri": "https://api.github.com",
                    }
                )

            elif type == "sshKey":

                try:
                    with open(filePath, "r") as f:
                        private_key = f.read().strip()
                except Exception as e:
                    module.fail_json(msg=f"Failed to read private key file: {str(e)}")

                credentials.update(
                    {
                        "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
                        "privateKeySource": {
                            "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
                            "privateKey": private_key,
                        },
                    }
                )

            elif type == "certificate":

                name, ext = os.path.splitext(filePath)

                if ext.lower() in [".p12", ".pfx"]:
                    try:
                        with open(filePath, "rb") as f:
                            file_content = f.read()
                        uploaded_keystore = base64.b64encode(file_content).decode(
                            "utf-8"
                        )
                    except Exception as e:
                        module.fail_json(
                            msg=f"Failed to read or encode keystore file: {str(e)}"
                        )

                    credentials.update(
                        {
                            "$class": "com.cloudbees.plugins.credentials.impl.CertificateCredentialsImpl",
                            "keyStoreSource": {
                                "$class": "com.cloudbees.plugins.credentials.impl.CertificateCredentialsImpl$UploadedKeyStoreSource",
                                "uploadedKeystore": uploaded_keystore,
                            },
                        }
                    )

                elif ext.lower() in [".pem", ".crt"]:  # PEM mode
                    try:
                        with open(filePath, "r") as f:
                            cert_chain = f.read()
                        with open(privateKeyPath, "r") as f:
                            private_key = f.read()
                    except Exception as e:
                        module.fail_json(msg=f"Failed to read PEM files: {str(e)}")

                    credentials.update(
                        {
                            "$class": "com.cloudbees.plugins.credentials.impl.CertificateCredentialsImpl",
                            "keyStoreSource": {
                                "$class": "com.cloudbees.plugins.credentials.impl.CertificateCredentialsImpl$PEMEntryKeyStoreSource",
                                "certChain": cert_chain,
                                "privateKey": private_key,
                            },
                        }
                    )

                else:
                    module.fail_json(
                        msg="Unsupported certificate file type. Only .p12, .pfx, .pem or .crt are supported."
                    )
            payload = {"": "0", "credentials": credentials}

    else:  # Delete

        # Delete command requires id
        if not id:
            module.fail_json(msg="id is required to delete a credential")

        delete_scope_or_credential(module, url, headers, auth, id, scope, command)

        module.exit_json(changed=True, message=f"{id} deleted successfully.")

    if not type == "file":
        data = urllib.parse.urlencode({"json": json.dumps(payload)})

    if not type == "scope" and not scope == "_":  # Check if custom scope exists
        if not domain_exists(url, scope, jenkinsUser, token):
            module.fail_json(msg=f"Domain {scope} doesn't exists")
    try:
        response = requests.post(
            (
                f"{url}/credentials/store/system/domain/{scope}/createCredentials"
                if not type == "scope"
                else f"{url}/credentials/store/system/createDomain"
            ),  # Create scope or domain
            headers=headers,
            auth=auth,
            data=data,
            files=files if type == "file" else None,
        )

        response.raise_for_status()
        result["changed"] = True
        result["message"] = response.text

    except requests.exceptions.RequestException as e:
        module.fail_json(
            msg="Failed to create/update credential", details=response.text
        )

    module.exit_json(**result)


if __name__ == "__main__":
    run_module()
