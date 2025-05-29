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
version_added: 11.0.0
description:
  - This module allows managing Jenkins credentials and domain scopes via the Jenkins HTTP API.
  - Create, update, and delete different credential types such as C(username/password), C(secret text), C(SSH key), C(certificates), C(GitHub App), and domains.
  - For scoped domains (type I(scope)), it supports restrictions based on V(hostname), V(hostname:port), V(path), and V(scheme).
requirements:
  - urllib3
author:
  - Youssef Ali (@YoussefKhalidAli)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
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
  state:
    description:
      - The state of the credential.
    choices: [present, absent]
    default: present
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
  jenkins_user:
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
      - Description of the credential or domain.
    default: ''
    type: str
  location:
    description:
      - Location of the credential. Either system or folder.
      - If location is a folder then url must be set to <jenkins-server>/job/<folder_name>.
    choices:
      - system
      - folder
    default: 'system'
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
  file_path:
    description:
      - File path to secret (e.g., private key, certificate).
    type: str
  private_key_path:
    description:
      - Path to private key file for PEM certificates.
    type: str
  passphrase:
    description:
      - SSH passphrase if exists.
    type: str
  inc_hostname:
    description:
      - List of hostnames to include in scope.
    type: list
    elements: str
  exc_hostname:
    description:
      - List of hostnames to exclude from scope.
    type: list
    elements: str
  inc_hostname_port:
    description:
      - List of host:port to include in scope.
    type: list
    elements: str
  exc_hostname_port:
    description:
      - List of host:port to exclude from scope.
    type: list
    elements: str
  inc_path:
    description:
      - List of URL paths to include.
    type: list
    elements: str
  exc_path:
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
        jenkins_user: "admin"
        token: "token"
        description: "Custom scope credential"
        inc_path:
          - "include/path"
          - "include/path2"
        exc_path:
          - "exclude/path"
          - "exclude/path2"
        inc_hostname:
          - "included-hostname"
          - "included-hostname2"
        exc_hostname:
          - "excluded-hostname"
          - "excluded-hostname2"
        schemes:
          - "http"
          - "https"
        inc_hostname_port:
          - "included-hostname:7000"
          - "included-hostname2:7000"
        exc_hostname_port:
          - "excluded-hostname:7000"
          - "excluded-hostname2:7000"

    - name: Add userAndPass credential
      jenkins_credential:
        scope: "CUSTOM"
        id: "userpass-id"
        type: "userAndPass"
        jenkins_user: "admin"
        token: "token"
        description: "User and password credential"
        username: "user1"
        password: "pass1"

    - name: Add file credential
      jenkins_credential:
        id: "file-id"
        type: "file"
        jenkins_user: "admin"
        token: "token"
        description: "File credential"
        file_path: "my-secret.pem"

    - name: Add text credential
      jenkins_credential:
        id: "text-id"
        type: "text"
        jenkins_user: "admin"
        token: "token"
        description: "Text credential"
        secret: "mysecrettext"

    - name: Add githubApp credential
      jenkins_credential:
        id: "githubapp-id"
        type: "githubApp"
        jenkins_user: "admin"
        token: "token"
        description: "GitHub App credential"
        appID: "12345"
        file_path: "my-secret.pem"
        owner: "github_owner"

    - name: Add sshKey credential
      jenkins_credential:
        id: "sshkey-id"
        type: "sshKey"
        jenkins_user: "admin"
        token: "token"
        description: "SSH key credential"
        username: "sshuser"
        file_path: "my-secret.pem"
        passphrase: "passphrase"

    - name: Add certificate credential (p12)
      jenkins_credential:
        id: "certificate-id"
        type: "certificate"
        jenkins_user: "admin"
        token: "token"
        description: "Certificate credential"
        password: "12345678901234"
        file_path: "certificate.p12"

    - name: Add certificate credential (pem)
      jenkins_credential:
        id: "certificate-id-pem"
        type: "certificate"
        jenkins_user: "admin"
        token: "token"
        description: "Certificate credential (pem)"
        file_path: "cert.pem"
        private_key_path: "private.key"

    - name: Delete credential
      jenkins_credential:
        id: "credential-id"
        state: "delete"
        jenkins_user: "admin"
        token: "{{ token }}"

    - name: Delete scope
      jenkins_credential:
        id: "scope-id"
        state: "delete"
        type: "scope"
        jenkins_user: "admin"
        token: "{{ token }}"

"""
# Edit is done the same way as add. (id must be the same as the one used to add the credential)

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
    description: Incase of errors return more details.
    type: str
    returned: Error
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.urls import fetch_url, basic_auth_header

import json
import os
import base64
import traceback
import urllib

try:
    import urllib3
except ImportError:
    HAS_URLLIB3 = False
    URLLIB3_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_URLLIB3 = True
    URLLIB3_IMPORT_ERROR = None


# Function to validate required fields based on credential type and check file existence.
def validate_required_fields(module, cred_type):
    required_fields_map = {
        "userAndPass": ["username", "password"],
        "file": ["file_path"],
        "text": ["secret"],
        "githubApp": ["appID", "file_path"],
        "sshKey": ["username", "file_path"],
        "certificate": ["file_path"],  # special case handled below
    }

    missing = []
    file_check_fields = ["file_path", "private_key_path"]

    # Basic param presence validation
    for field in required_fields_map.get(cred_type, []):
        if not module.params.get(field):
            missing.append(field)

    # Extra logic for certificate type
    if cred_type == "certificate" and module.params["file_path"]:
        ext = os.path.splitext(module.params["file_path"])[1].lower()
        if ext in [".p12", ".pfx"] and not module.params["password"]:
            missing.append("password")
        elif ext in [".pem", ".crt"] and not module.params["private_key_path"]:
            missing.append("private_key_path")

    # Validate file paths exist on disk
    for field in file_check_fields:
        path = module.params.get(field)
        if path and not os.path.exists(path):
            module.fail_json(msg="File not found: {}".format(path))

    if missing:
        module.fail_json(
            msg="Missing required fields for type '{}': {}".format(
                cred_type, ", ".join(missing)
            )
        )


# Gets the Jenkins crumb for CSRF protection which is required for API calls
def get_jenkins_crumb(module, url, user, token):

    if "/job" in url:
        url = url.split("/job")[0]

    crumb_url = "{}/crumbIssuer/api/json".format(url)

    headers = {"Authorization": basic_auth_header(user, token)}

    response, info = fetch_url(module, crumb_url, headers=headers)

    if info["status"] != 200:
        return None, None

    try:
        data = response.read()
        json_data = json.loads(data)
        return json_data["crumbRequestField"], json_data["crumb"]
    except Exception:
        return None, None


# Function to clean the data sent via API by removing unwanted keys and None values
def clean_data(data):
    # Keys to remove (including those with None values)
    keys_to_remove = {
        "url",
        "token",
        "jenkins_user",
        "file_path",
        "type",
        "state",
        "scope",
    }

    # Filter out None values and unwanted keys
    cleaned_data = {
        key: value
        for key, value in data.items()
        if value is not None and key not in keys_to_remove
    }

    return cleaned_data


# Function to check if credentials/domain exists
def target_exists(module, url, location, scope, name, user, token, check_domain=False):

    if module.params["type"] == "scope" or check_domain:
        target_url = "{}/credentials/store/{}/domain/{}/api/json".format(
            url, location, scope if check_domain else name
        )
    else:
        target_url = "{}/credentials/store/{}/domain/{}/credential/{}/api/json".format(
            url, location, scope, name
        )

    headers = {"Authorization": basic_auth_header(user, token)}

    response, info = fetch_url(module, target_url, headers=headers)
    status = info.get("status", 0)

    if status == 200:
        return True
    elif status == 404:
        return False
    else:
        module.fail_json(
            msg="Unexpected status code {} when checking {} existence.".format(
                status, name
            )
        )


# Function to delete the scope or credential provided
def delete_scope_or_credential(module, url, location, headers, id, scope):
    try:
        type = module.params["type"]
        # Remove Content-Type header if present (like your original)
        headers.pop("Content-Type", None)

        if type == "scope":
            delete_url = "{}/credentials/store/{}/domain/{}/doDelete".format(
                url, location, id
            )
        else:
            delete_url = (
                "{}/credentials/store/{}/domain/{}/credential/{}/doDelete".format(
                    url, location, scope, id
                )
            )

        # Add Basic Auth header
        user = module.params["jenkins_user"]
        token = module.params["token"]
        headers["Authorization"] = basic_auth_header(user, token)

        response, info = fetch_url(module, delete_url, headers=headers, method="POST")

        status = info.get("status", 0)
        if status >= 400:
            module.fail_json(
                msg="Failed to delete: HTTP {}, {}, {}".format(
                    status, response, headers
                )
            )

        # Restore Content-Type header for future use
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    except Exception as e:
        module.fail_json(msg="Exception during delete: {}".format(str(e)))


# Function to read the private key for types texts and sshKey
def read_privateKey(module):
    try:
        with open(module.params["file_path"], "r") as f:
            private_key = f.read().strip()
            return private_key
    except Exception as e:
        module.fail_json(msg="Failed to read private key file: {}".format(str(e)))


# Function to builds multipart form-data body and content-type header for file credential upload.
#    Returns:
#        body (bytes): Encoded multipart data
#        content_type (str): Content-Type header including boundary
def embed_file_into_body(module, file_path, credentials):

    filename = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
    except Exception as e:
        module.fail_json(msg="Failed to read file: {}".format(str(e)))

    credentials.update(
        {
            "file": "file0",
            "fileName": filename,
        }
    )

    payload = {"credentials": credentials}

    fields = {"file0": (filename, file_bytes), "json": json.dumps(payload)}

    body, content_type = urllib3.encode_multipart_formdata(fields)
    return body, content_type


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
            state=dict(
                type="str",
                required=False,
                default="present",
                choices=["present", "absent"],
            ),  # State of the credential
            scope=dict(
                type="str", required=False, default="_"
            ),  # Scope of the credential
            url=dict(
                type="str", required=False, default="http://localhost:8080"
            ),  # Jenkins URL
            jenkins_user=dict(type="str", required=True),  # Jenkins username
            token=dict(type="str", required=True, no_log=True),  # Jenkins API token
            description=dict(
                type="str", required=False, default=""
            ),  # Description of the credential
            location=dict(
                type="str",
                required=False,
                default="system",
                choices=["system", "folder"],
            ),  # Location of the credential (not used in this module)
            username=dict(
                type="str", required=False
            ),  # Username for userAndPass and sshKey types
            password=dict(
                type="str", required=False, no_log=True
            ),  # Password for userAndPass type
            file_path=dict(
                type="str", required=False, default=None
            ),  # File path for file and sshKey types
            secret=dict(type="str", required=False, no_log=True),  # Text for text type
            appID=dict(type="str", required=False),  # App ID for githubApp type
            owner=dict(type="str", required=False),  # Owner for githubApp type
            passphrase=dict(
                type="str", required=False, no_log=True
            ),  # Passphrase for sshKey type
            private_key_path=dict(
                type="str", required=False, no_log=True
            ),  # Private key path for certificate type
            # Scope specifications parameters
            inc_hostname=dict(
                type="list", required=False, elements="str"
            ),  # Include hostname for scope type
            exc_hostname=dict(
                type="list", required=False, elements="str"
            ),  # Exclude hostname for scope type
            inc_hostname_port=dict(
                type="list", required=False, elements="str"
            ),  # Include hostname and port for scope type
            exc_hostname_port=dict(
                type="list", required=False, elements="str"
            ),  # Exclude hostname and port for scope type
            inc_path=dict(
                type="list", required=False, elements="str"
            ),  # Include path for scope type
            exc_path=dict(
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
    state = module.params["state"]
    scope = module.params["scope"]
    url = module.params["url"]
    jenkins_user = module.params["jenkins_user"]
    token = module.params["token"]
    description = module.params["description"]
    location = module.params["location"]
    filePath = module.params["file_path"]
    private_key_path = module.params["private_key_path"]
    inc_hostname = module.params["inc_hostname"]
    exc_hostname = module.params["exc_hostname"]
    inc_hostname_port = module.params["inc_hostname_port"]
    exc_hostname_port = module.params["exc_hostname_port"]
    inc_path = module.params["inc_path"]
    exc_path = module.params["exc_path"]
    schemes = module.params["schemes"]

    if not HAS_URLLIB3:
        module.fail_json(
            msg=missing_required_lib("urllib3"), exception=URLLIB3_IMPORT_ERROR
        )

    if state not in ["present", "absent"]:
        module.fail_json(msg="Invalid state. Use 'present' or 'absent'.")

    # Get the crumb for CSRF protection
    crumb_field, crumb_value = get_jenkins_crumb(module, url, jenkins_user, token)
    if not crumb_field or not crumb_value:
        module.fail_json(
            msg="Failed to fetch Jenkins crumb. Check Jenkins URL and credentials."
        )

    result = dict(
        changed=False,
        message="",
    )

    headers = {
        "Authorization": basic_auth_header(jenkins_user, token),
        crumb_field: crumb_value,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    credentials = clean_data(module.params)

    does_exist = target_exists(module, url, location, scope, id, jenkins_user, token)

    # Check if the credential/domain doesn't exist and the user wants to delete
    if not does_exist and state == "absent":
        result["changed"] = False
        result["message"] = "{} does not exist.".format(id)
        module.exit_json(**result)

    if state == "present":
        # Check if credential type is provided
        if type is None:
            module.fail_json(msg="Credential type is required for add or update")

        # If updating, we need to delete the existing credential/domain first
        if target_exists(module, url, location, scope, id, jenkins_user, token):
            delete_scope_or_credential(module, url, location, headers, id, scope)

        if type == "scope":

            specifications = []

            # Create a domain in Jenkins
            if inc_hostname or exc_hostname:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.HostnameSpecification",
                        "includes": ",".join(inc_hostname),
                        "excludes": ",".join(exc_hostname),
                    }
                )

            if inc_hostname_port or exc_hostname_port:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.HostnamePortSpecification",
                        "includes": ",".join(inc_hostname_port),
                        "excludes": ",".join(exc_hostname_port),
                    }
                )

            if schemes:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.SchemeSpecification",
                        "schemes": ",".join(schemes),
                    },
                )

            if inc_path or exc_path:
                specifications.append(
                    {
                        "stapler-class": "com.cloudbees.plugins.credentials.domains.PathSpecification",
                        "includes": ",".join(inc_path),
                        "excludes": ",".join(exc_path),
                    }
                )

            payload = {
                "name": id,
                "description": description,
                "specifications": specifications,
            }

        else:
            validate_required_fields(module, type)

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
                    }
                )

                # Build multipart body and content-type
                body, content_type = embed_file_into_body(module, filePath, credentials)
                headers["Content-Type"] = content_type

            elif type == "text":

                credentials.update(
                    {
                        "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                    }
                )

            elif type == "githubApp":

                private_key = read_privateKey(module)

                credentials.update(
                    {
                        "$class": "org.jenkinsci.plugins.github_branch_source.GitHubAppCredentials",
                        "privateKey": private_key,
                        "apiUri": "https://api.github.com",
                    }
                )

            elif type == "sshKey":

                private_key = read_privateKey(module)

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
                            msg="Failed to read or encode keystore file: {}".format(
                                str(e)
                            )
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
                        with open(private_key_path, "r") as f:
                            private_key = f.read()
                    except Exception as e:
                        module.fail_json(
                            msg="Failed to read PEM files: {}".format(str(e))
                        )

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
            payload = {"credentials": credentials}

        if not type == "file":
            body = urllib.parse.urlencode({"json": json.dumps(payload)})

    else:  # Delete

        # Absent state requires id
        if not id:
            module.fail_json(msg="id is required to delete a credential")

        delete_scope_or_credential(module, url, location, headers, id, scope)

        module.exit_json(changed=True, message="{} deleted successfully.".format(id))

    if not type == "scope" and not scope == "_":  # Check if custom scope exists
        if not target_exists(
            module, url, location, scope, id, jenkins_user, token, True
        ):  # Trigger check scope
            module.fail_json(msg="Domain {} doesn't exists".format(scope))

    if type == "scope":
        post_url = "{}/credentials/store/{}/createDomain".format(url, location)
    else:
        post_url = "{}/credentials/store/{}/domain/{}/createCredentials".format(
            url, location, scope
        )

    try:
        response, info = fetch_url(
            module, post_url, headers=headers, data=body, method="POST"
        )
    except Exception as e:
        module.fail_json(msg="Request to {} failed: {}".format(post_url, str(e)))

    status = info.get("status", 0)

    if status >= 400:
        body = response.read() if response else b""
        module.fail_json(
            msg="Failed to {} credential".format(
                "add/update" if state == "present" else "delete"
            ),
            details=body.decode("utf-8", errors="ignore"),
        )

    result["changed"] = True
    result["message"] = response.read().decode("utf-8")

    module.exit_json(**result)


if __name__ == "__main__":
    run_module()
