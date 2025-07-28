#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: jenkins_credential
short_description: Manage Jenkins credentials and domains through API
version_added: 11.1.0
description:
  - This module allows managing Jenkins credentials and domain scopes through the Jenkins HTTP API.
  - Create, update, and delete different credential types such as C(username/password), C(secret text), C(SSH key), C(certificates),
    C(GitHub App), and domains.
  - For scoped domains (O(type=scope)), it supports restrictions based on V(hostname), V(hostname:port), V(path), and V(scheme).
requirements:
  - urllib3 >= 1.26.0
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
      - The ID of the Jenkins credential or domain.
    type: str
  type:
    description:
      - Type of the credential or action.
    choices:
      - user_and_pass
      - file
      - text
      - github_app
      - ssh_key
      - certificate
      - scope
      - token
    type: str
  state:
    description:
      - The state of the credential.
    choices:
      - present
      - absent
    default: present
    type: str
  scope:
    description:
      - Jenkins credential domain scope.
      - Deleting a domain scope deletes all credentials within it.
    type: str
    default: '_'
  force:
    description:
      - Force update if the credential already exists, used with O(state=present).
      - If set to V(true), it deletes the existing credential before creating a new one.
      - Always returns RV(ignore:changed=true).
    type: bool
    default: false
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
  jenkins_password:
    description:
      - Jenkins password for token creation. Required if O(type=token).
    type: str
  token:
    description:
      - Jenkins API token. Required unless O(type=token).
    type: str
  description:
    description:
      - Description of the credential or domain.
    default: ''
    type: str
  location:
    description:
      - Location of the credential. Either V(system) or V(folder).
      - If O(location=folder) then O(url) must be set to V(<jenkins-server>/job/<folder_name>).
    choices:
      - system
      - folder
    default: 'system'
    type: str
  name:
    description:
      - Name of the token to generate. Required if O(type=token).
      - When generating a new token, do not pass O(id). It is generated automatically.
      - Creating two tokens with the same name generates two distinct tokens with different RV(token_uuid) values.
      - Replacing a token with another one of the same name requires deleting the original first using O(force=True).
    type: str
  username:
    description:
      - Username for credentials types that require it (for example O(type=ssh_key) or O(type=user_and_pass)).
    type: str
  password:
    description:
      - Password for credentials types that require it (for example O(type=user_and_passs) or O(type=certificate)).
    type: str
  secret:
    description:
      - Secret text (used when O(type=text)).
    type: str
  appID:
    description:
      - GitHub App ID.
    type: str
  api_uri:
    description:
      - Link to Github API.
    default: 'https://api.github.com'
    type: str
  owner:
    description:
      - GitHub App owner.
    type: str
  file_path:
    description:
      - File path to secret file (for example O(type=file) or O(type=certificate)).
      - For O(type=certificate), this can be a V(.p12) or V(.pem) file.
    type: path
  private_key_path:
    description:
      - Path to private key file for PEM certificates or GitHub Apps.
    type: path
  passphrase:
    description:
      - SSH passphrase if needed.
    type: str
  inc_hostname:
    description:
      - List of hostnames to include in scope.
    type: list
    elements: str
  exc_hostname:
    description:
      - List of hostnames to exclude from scope.
      - If a hostname appears in both this list and O(inc_hostname), the hostname is excluded.
    type: list
    elements: str
  inc_hostname_port:
    description:
      - List of V(host:port) to include in scope.
    type: list
    elements: str
  exc_hostname_port:
    description:
      - List of host:port to exclude from scope.
      - If a hostname and port appears in both this list and O(inc_hostname_port), it is excluded.
    type: list
    elements: str
  inc_path:
    description:
      - List of URL paths to include when matching credentials to domains.
      - 'B(Matching is hierarchical): subpaths of excluded paths are also excluded, even if explicitly included.'
    type: list
    elements: str
  exc_path:
    description:
      - List of URL paths to exclude.
      - If a path is also matched by O(exc_path), it is excluded.
      - If you exclude a subpath of a path previously included, that subpath alone is excluded.
    type: list
    elements: str
  schemes:
    description:
      - List of schemes (for example V(http) or V(https)) to match.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Generate token
  community.general.jenkins_credential:
    id: "test-token"
    jenkins_user: "admin"
    jenkins_password: "password"
    type: "token"
  register: token_result

- name: Add CUSTOM scope credential
  community.general.jenkins_credential:
    id: "CUSTOM"
    type: "scope"
    jenkins_user: "admin"
    token: "{{ token }}"
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

- name: Add user_and_pass credential
  community.general.jenkins_credential:
    id: "userpass-id"
    type: "user_and_pass"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "User and password credential"
    username: "user1"
    password: "pass1"

- name: Add file credential to custom scope
  community.general.jenkins_credential:
    id: "file-id"
    type: "file"
    jenkins_user: "admin"
    token: "{{ token }}"
    scope: "CUSTOM"
    description: "File credential"
    file_path: "../vars/my-secret.pem"

- name: Add text credential to folder
  community.general.jenkins_credential:
    id: "text-id"
    type: "text"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "Text credential"
    secret: "mysecrettext"
    location: "folder"
    url: "http://localhost:8080/job/test"

- name: Add githubApp credential
  community.general.jenkins_credential:
    id: "githubapp-id"
    type: "github_app"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "GitHub app credential"
    appID: "12345"
    file_path: "../vars/github.pem"
    owner: "github_owner"

- name: Add sshKey credential
  community.general.jenkins_credential:
    id: "sshkey-id"
    type: "ssh_key"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "SSH key credential"
    username: "sshuser"
    file_path: "../vars/ssh_key"
    passphrase: 1234

- name: Add certificate credential (p12)
  community.general.jenkins_credential:
    id: "certificate-id"
    type: "certificate"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "Certificate credential"
    password: "12345678901234"
    file_path: "../vars/certificate.p12"

- name: Add certificate credential (pem)
  community.general.jenkins_credential:
    id: "certificate-id-pem"
    type: "certificate"
    jenkins_user: "admin"
    token: "{{ token }}"
    description: "Certificate credential (pem)"
    file_path: "../vars/cert.pem"
    private_key_path: "../vars/private.key"
"""
RETURN = r"""
details:
  description: Return more details in case of errors.
  type: str
  returned: failed
token:
  description:
    - The generated API token if O(type=token).
    - This is needed to authenticate API calls later.
    - This should be stored securely, as it is the only time it is returned.
  type: str
  returned: success
token_uuid:
  description:
    - The generated ID of the token.
    - You pass this value back to the module as O(id) to edit or revoke the token later.
    - This should be stored securely, as it is the only time it is returned.
  type: str
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, basic_auth_header
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible_collections.community.general.plugins.module_utils import deps

import json
import os
import base64

with deps.declare("urllib3", reason="urllib3 is required to embed files into requests"):
    import urllib3


# Function to validate file paths exist on disk
def validate_file_exist(module, path):

    if path and not os.path.exists(path):
        module.fail_json(msg="File not found: {}".format(path))


# Gets the Jenkins crumb for CSRF protection which is required for API calls
def get_jenkins_crumb(module, headers):
    type = module.params["type"]
    url = module.params["url"]

    if "/job" in url:
        url = url.split("/job")[0]

    crumb_url = "{}/crumbIssuer/api/json".format(url)

    response, info = fetch_url(module, crumb_url, headers=headers)

    if info["status"] != 200:
        module.fail_json(msg="Failed to fetch Jenkins crumb. Confirm token is real.")

    # Cookie is needed to generate API token
    cookie = info.get("set-cookie", "")
    session_cookie = cookie.split(";")[0] if cookie else None

    try:
        data = response.read()
        json_data = json.loads(data)
        crumb_request_field = json_data["crumbRequestField"]
        crumb = json_data["crumb"]
        headers[crumb_request_field] = crumb  # Set the crumb in headers
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded"  # Set Content-Type for form data
        )
        if type == "token":
            headers["Cookie"] = (
                session_cookie  # Set session cookie for token operations
            )
        return crumb_request_field, crumb, session_cookie  # Return for test purposes

    except Exception:
        return None


# Function to clean the data sent via API by removing unwanted keys and None values
def clean_data(data):
    # Keys to remove (including those with None values)
    keys_to_remove = {
        "url",
        "token",
        "jenkins_user",
        "jenkins_password",
        "file_path",
        "private_key_path",
        "type",
        "state",
        "force",
        "name",
        "scope",
        "location",
        "api_uri",
    }

    # Filter out None values and unwanted keys
    cleaned_data = {
        key: value
        for key, value in data.items()
        if value is not None and key not in keys_to_remove
    }

    return cleaned_data


# Function to check if credentials/domain exists
def target_exists(module, check_domain=False):
    url = module.params["url"]
    location = module.params["location"]
    scope = module.params["scope"]
    name = module.params["id"]
    user = module.params["jenkins_user"]
    token = module.params["token"]

    headers = {"Authorization": basic_auth_header(user, token)}

    if module.params["type"] == "scope" or check_domain:
        target_url = "{}/credentials/store/{}/domain/{}/api/json".format(
            url, location, scope if check_domain else name
        )
    elif module.params["type"] == "token":
        return False  # Can't check token
    else:
        target_url = "{}/credentials/store/{}/domain/{}/credential/{}/api/json".format(
            url, location, scope, name
        )

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
def delete_target(module, headers):
    user = module.params["jenkins_user"]
    type = module.params["type"]
    url = module.params["url"]
    location = module.params["location"]
    id = module.params["id"]
    scope = module.params["scope"]

    body = False

    try:

        if type == "token":
            delete_url = "{}/user/{}/descriptorByName/jenkins.security.ApiTokenProperty/revoke".format(
                url, user
            )
            body = urlencode({"tokenUuid": id})

        elif type == "scope":
            delete_url = "{}/credentials/store/{}/domain/{}/doDelete".format(
                url, location, id
            )

        else:
            delete_url = (
                "{}/credentials/store/{}/domain/{}/credential/{}/doDelete".format(
                    url, location, scope, id
                )
            )

        response, info = fetch_url(
            module,
            delete_url,
            headers=headers,
            data=body if body else None,
            method="POST",
        )

        status = info.get("status", 0)
        if not status == 200:
            module.fail_json(
                msg="Failed to delete: HTTP {}, {}, {}".format(
                    status, response, headers
                )
            )

    except Exception as e:
        module.fail_json(msg="Exception during delete: {}".format(str(e)))


# Function to read the private key for types texts and ssh_key
def read_privateKey(module):
    try:
        with open(module.params["private_key_path"], "r") as f:
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
        return "", ""  # Return for test purposes

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
            id=dict(type="str"),
            type=dict(
                type="str",
                choices=[
                    "user_and_pass",
                    "file",
                    "text",
                    "github_app",
                    "ssh_key",
                    "certificate",
                    "scope",
                    "token",
                ],
            ),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            force=dict(type="bool", default=False),
            scope=dict(type="str", default="_"),
            url=dict(type="str", default="http://localhost:8080"),
            jenkins_user=dict(type="str", required=True),
            jenkins_password=dict(type="str", no_log=True),
            token=dict(type="str", no_log=True),
            description=dict(type="str", default=""),
            location=dict(type="str", default="system", choices=["system", "folder"]),
            name=dict(type="str"),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            file_path=dict(type="path"),
            secret=dict(type="str", no_log=True),
            appID=dict(type="str"),
            api_uri=dict(type="str", default="https://api.github.com"),
            owner=dict(type="str"),
            passphrase=dict(type="str", no_log=True),
            private_key_path=dict(type="path", no_log=True),
            # Scope specifications parameters
            inc_hostname=dict(type="list", elements="str"),
            exc_hostname=dict(type="list", elements="str"),
            inc_hostname_port=dict(type="list", elements="str"),
            exc_hostname_port=dict(type="list", elements="str"),
            inc_path=dict(type="list", elements="str"),
            exc_path=dict(type="list", elements="str"),
            schemes=dict(type="list", elements="str"),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "present", ["type"]),
            ("state", "absent", ["id"]),
            ("type", "token", ["name", "jenkins_password"]),
            ("type", "user_and_pass", ["username", "password", "id", "token"]),
            ("type", "file", ["file_path", "id", "token"]),
            ("type", "text", ["secret", "id", "token"]),
            ("type", "github_app", ["appID", "private_key_path", "id", "token"]),
            ("type", "ssh_key", ["username", "private_key_path", "id", "token"]),
            ("type", "certificate", ["file_path", "id", "token"]),
            ("type", "scope", ["id", "token"]),
        ],
    )

    # Parameters
    id = module.params["id"]
    type = module.params["type"]
    state = module.params["state"]
    force = module.params["force"]
    scope = module.params["scope"]
    url = module.params["url"]
    jenkins_user = module.params["jenkins_user"]
    jenkins_password = module.params["jenkins_password"]
    name = module.params["name"]
    token = module.params["token"]
    description = module.params["description"]
    location = module.params["location"]
    filePath = module.params["file_path"]
    private_key_path = module.params["private_key_path"]
    api_uri = module.params["api_uri"]
    inc_hostname = module.params["inc_hostname"]
    exc_hostname = module.params["exc_hostname"]
    inc_hostname_port = module.params["inc_hostname_port"]
    exc_hostname_port = module.params["exc_hostname_port"]
    inc_path = module.params["inc_path"]
    exc_path = module.params["exc_path"]
    schemes = module.params["schemes"]

    deps.validate(module)

    headers = {
        "Authorization": basic_auth_header(jenkins_user, token or jenkins_password),
    }

    # Get the crumb for CSRF protection
    get_jenkins_crumb(module, headers)

    result = dict(
        changed=False,
        msg="",
    )

    credentials = clean_data(module.params)

    does_exist = target_exists(module)

    # Check if the credential/domain doesn't exist and the user wants to delete
    if not does_exist and state == "absent" and not type == "token":
        result["changed"] = False
        result["msg"] = "{} does not exist.".format(id)
        module.exit_json(**result)

    if state == "present":

        # If updating, we need to delete the existing credential/domain first based on force parameter
        if force and (does_exist or type == "token"):
            delete_target(module, headers)
        elif does_exist and not force:
            result["changed"] = False
            result["msg"] = "{} already exists. Use force=True to update.".format(id)
            module.exit_json(**result)

        if type == "token":

            post_url = "{}/user/{}/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken".format(
                url, jenkins_user
            )

            body = "newTokenName={}".format(name)

        elif type == "scope":

            post_url = "{}/credentials/store/{}/createDomain".format(url, location)

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
            if filePath:
                validate_file_exist(module, filePath)
            elif private_key_path:
                validate_file_exist(module, private_key_path)

            post_url = "{}/credentials/store/{}/domain/{}/createCredentials".format(
                url, location, scope
            )

            cred_class = {
                "user_and_pass": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
                "file": "org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl",
                "text": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                "github_app": "org.jenkinsci.plugins.github_branch_source.GitHubAppCredentials",
                "ssh_key": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
                "certificate": "com.cloudbees.plugins.credentials.impl.CertificateCredentialsImpl",
            }
            credentials.update({"$class": cred_class[type]})

            if type == "file":

                # Build multipart body and content-type
                body, content_type = embed_file_into_body(module, filePath, credentials)
                headers["Content-Type"] = content_type

            elif type == "github_app":

                private_key = read_privateKey(module)

                credentials.update(
                    {
                        "privateKey": private_key,
                        "apiUri": api_uri,
                    }
                )

            elif type == "ssh_key":

                private_key = read_privateKey(module)

                credentials.update(
                    {
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

        if not type == "file" and not type == "token":
            body = urlencode({"json": json.dumps(payload)})

    else:  # Delete

        delete_target(module, headers)

        module.exit_json(changed=True, msg="{} deleted successfully.".format(id))

    if (
        not type == "scope" and not scope == "_"
    ):  # Check if custom scope exists if adding to a custom scope
        if not target_exists(module, True):
            module.fail_json(msg="Domain {} doesn't exists".format(scope))

    try:
        response, info = fetch_url(
            module, post_url, headers=headers, data=body, method="POST"
        )
    except Exception as e:
        module.fail_json(msg="Request to {} failed: {}".format(post_url, str(e)))

    status = info.get("status", 0)

    if not status == 200:
        body = response.read() if response else b""
        module.fail_json(
            msg="Failed to {} credential".format(
                "add/update" if state == "present" else "delete"
            ),
            details=body.decode("utf-8", errors="ignore"),
        )

    if type == "token":
        response_data = json.loads(response.read())
        result["token"] = response_data["data"]["tokenValue"]
        result["token_uuid"] = response_data["data"]["tokenUuid"]

    result["changed"] = True
    result["msg"] = response.read().decode("utf-8")

    module.exit_json(**result)


if __name__ == "__main__":
    run_module()
