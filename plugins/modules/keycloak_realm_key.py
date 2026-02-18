#!/usr/bin/python

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_realm_key

short_description: Allows administration of Keycloak realm keys using Keycloak API

version_added: 7.5.0

description:
  - This module allows the administration of Keycloak realm keys using the Keycloak REST API. It requires access to the REST
    API using OpenID Connect; the user connecting and the realm being used must have the requisite access rights. In a default
    Keycloak installation, admin-cli and an admin user would work, as would a separate realm definition with the scope tailored
    to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html). Aliases are provided so camelCased versions can be used
    as well.
  - This module is unable to detect changes to the actual cryptographic key after importing it. However, if some other property
    is changed alongside the cryptographic key, then the key also changes as a side-effect, as the JSON payload needs to include
    the private key. This can be considered either a bug or a feature, as the alternative would be to always update the realm
    key whether it has changed or not.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the keycloak realm key.
      - On V(present), the realm key is created (or updated if it exists already).
      - On V(absent), the realm key is removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  name:
    description:
      - Name of the realm key to create.
    type: str
    required: true
  force:
    description:
      - Enforce the state of the private key and certificate. This is not automatically the case as this module is unable
        to determine the current state of the private key and thus cannot trigger an update based on an actual divergence.
        That said, a private key update may happen even if force is false as a side-effect of other changes.
    default: false
    type: bool
  parent_id:
    description:
      - The parent_id of the realm key. In practice the name of the realm.
    type: str
    required: true
  provider_id:
    description:
      - The name of the "provider ID" for the key.
      - The value V(rsa-enc) has been added in community.general 8.2.0.
      - The value V(java-keystore) has been added in community.general 12.4.0. This provider imports keys from
        a Java Keystore (JKS or PKCS12) file located on the Keycloak server filesystem.
      - The values V(rsa-generated), V(hmac-generated), V(aes-generated), and V(ecdsa-generated) have been added in
        community.general 12.4.0. These are auto-generated key providers where Keycloak manages the key material.
      - The values V(rsa-enc-generated), V(ecdh-generated), and V(eddsa-generated) have been added in
        community.general 12.4.0. These correspond to the auto-generated key providers available in Keycloak 26.
    choices:
      - rsa
      - rsa-enc
      - java-keystore
      - rsa-generated
      - rsa-enc-generated
      - hmac-generated
      - aes-generated
      - ecdsa-generated
      - ecdh-generated
      - eddsa-generated
    default: 'rsa'
    type: str
  config:
    description:
      - Dict specifying the key and its properties.
    type: dict
    suboptions:
      active:
        description:
          - Whether they key is active or inactive. Not to be confused with the state of the Ansible resource managed by the
            O(state) parameter.
        default: true
        type: bool
      enabled:
        description:
          - Whether the key is enabled or disabled. Not to be confused with the state of the Ansible resource managed by the
            O(state) parameter.
        default: true
        type: bool
      priority:
        description:
          - The priority of the key.
        type: int
        required: true
      algorithm:
        description:
          - Key algorithm.
          - The values V(RS384), V(RS512), V(PS256), V(PS384), V(PS512), V(RSA1_5), V(RSA-OAEP), V(RSA-OAEP-256) have been
            added in community.general 8.2.0.
          - The values V(HS256), V(HS384), V(HS512) (for HMAC), V(ES256), V(ES384), V(ES512) (for ECDSA), and V(AES)
            have been added in community.general 12.4.0.
          - The values V(ECDH_ES), V(ECDH_ES_A128KW), V(ECDH_ES_A192KW), V(ECDH_ES_A256KW) (for ECDH key exchange),
            and V(Ed25519), V(Ed448) (for EdDSA signing) have been added in community.general 12.4.0.
          - For O(provider_id=rsa), O(provider_id=rsa-generated), and O(provider_id=java-keystore), defaults to V(RS256).
          - For O(provider_id=rsa-enc) and O(provider_id=rsa-enc-generated), must be one of V(RSA1_5), V(RSA-OAEP), V(RSA-OAEP-256) (required, no default).
          - For O(provider_id=hmac-generated), must be one of V(HS256), V(HS384), V(HS512) (required, no default).
          - For O(provider_id=ecdsa-generated), must be one of V(ES256), V(ES384), V(ES512) (required, no default).
          - For O(provider_id=ecdh-generated), must be one of V(ECDH_ES), V(ECDH_ES_A128KW), V(ECDH_ES_A192KW), V(ECDH_ES_A256KW) (required, no default).
          - For O(provider_id=eddsa-generated), this option is not used (the algorithm is determined by O(config.elliptic_curve)).
          - For O(provider_id=aes-generated), this option is not used (AES is always used).
        choices:
          - RS256
          - RS384
          - RS512
          - PS256
          - PS384
          - PS512
          - RSA1_5
          - RSA-OAEP
          - RSA-OAEP-256
          - HS256
          - HS384
          - HS512
          - ES256
          - ES384
          - ES512
          - AES
          - ECDH_ES
          - ECDH_ES_A128KW
          - ECDH_ES_A192KW
          - ECDH_ES_A256KW
          - Ed25519
          - Ed448
        default: RS256
        type: str
      private_key:
        description:
          - The private key as an ASCII string. Contents of the key must match O(config.algorithm) and O(provider_id).
          - Please note that the module cannot detect whether the private key specified differs from the current state's private
            key. Use O(force=true) to force the module to update the private key if you expect it to be updated.
          - Required when O(provider_id) is V(rsa) or V(rsa-enc). Not used for auto-generated providers.
        type: str
      certificate:
        description:
          - A certificate signed with the private key as an ASCII string. Contents of the key must match O(config.algorithm)
            and O(provider_id).
          - If you want Keycloak to automatically generate a certificate using your private key then set this to an empty
            string.
          - Required when O(provider_id) is V(rsa) or V(rsa-enc). Not used for auto-generated providers.
        type: str
      secret_size:
        description:
          - The size of the generated secret key in bytes.
          - Only applicable to O(provider_id=hmac-generated) and O(provider_id=aes-generated).
          - Valid values are V(16), V(24), V(32), V(64), V(128), V(256), V(512).
          - Default is V(64) for HMAC, V(16) for AES.
        type: int
        version_added: 12.4.0
      key_size:
        description:
          - The size of the generated key in bits.
          - Only applicable to O(provider_id=rsa-generated) and O(provider_id=rsa-enc-generated).
          - Valid values are V(1024), V(2048), V(4096). Default is V(2048).
        type: int
        version_added: 12.4.0
      elliptic_curve:
        description:
          - The elliptic curve to use for ECDSA, ECDH, or EdDSA keys.
          - For O(provider_id=ecdsa-generated) and O(provider_id=ecdh-generated), valid values are V(P-256), V(P-384), V(P-521). Default is V(P-256).
          - For O(provider_id=eddsa-generated), valid values are V(Ed25519), V(Ed448). Default is V(Ed25519).
        type: str
        choices: ['P-256', 'P-384', 'P-521', 'Ed25519', 'Ed448']
        version_added: 12.4.0
      keystore:
        description:
          - Path to the Java Keystore file on the Keycloak server filesystem.
          - Required when O(provider_id=java-keystore).
        type: str
        version_added: 12.4.0
      keystore_password:
        description:
          - Password for the Java Keystore.
          - Required when O(provider_id=java-keystore).
        type: str
        version_added: 12.4.0
      key_alias:
        description:
          - Alias of the key within the keystore.
          - Required when O(provider_id=java-keystore).
        type: str
        version_added: 12.4.0
      key_password:
        description:
          - Password for the key within the keystore.
          - If not specified, the O(config.keystore_password) is used.
          - Only applicable to O(provider_id=java-keystore).
        type: str
        version_added: 12.4.0
  update_password:
    description:
      - Controls when passwords are sent to Keycloak for V(java-keystore) provider.
      - V(always) - Always send passwords. Keycloak will update the component even if passwords
        have not changed. Use when you need to ensure passwords are updated.
      - V(on_create) - Only send passwords when creating a new component. When updating an
        existing component, send the masked value to preserve existing passwords. This makes
        the module idempotent for password fields.
      - This is necessary because Keycloak masks passwords in API responses (returns C(**********)),
        making comparison impossible.
      - Has no effect for providers other than V(java-keystore).
    type: str
    choices: ['always', 'on_create']
    default: always
    version_added: 12.4.0
notes:
  - Current value of the private key cannot be fetched from Keycloak. Therefore comparing its desired state to the current
    state is not possible.
  - If O(config.certificate) is not explicitly provided it is dynamically created by Keycloak. Therefore comparing the current
    state of the certificate to the desired state (which may be empty) is not possible.
  - Due to the private key and certificate options the module is B(not fully idempotent). You can use O(force=true) to force
    the module to ensure updating if you know that the private key might have changed.
  - For auto-generated providers (V(rsa-generated), V(rsa-enc-generated), V(hmac-generated), V(aes-generated), V(ecdsa-generated),
    V(ecdh-generated), V(eddsa-generated)), Keycloak manages the key material automatically. The O(config.private_key) and
    O(config.certificate) options are not used.
  - For V(java-keystore) provider, the O(config.keystore_password) and O(config.key_password) values are returned masked by
    Keycloak. Therefore comparing their current state to the desired state is not possible. Use O(update_password=on_create)
    for idempotent playbooks, or use O(update_password=always) (default) if you need to ensure passwords are updated.
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Samuli Seppänen (@mattock)
"""

EXAMPLES = r"""
- name: Manage Keycloak realm key (certificate autogenerated by Keycloak)
  community.general.keycloak_realm_key:
    name: custom
    state: present
    parent_id: master
    provider_id: rsa
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      private_key: "{{ private_key }}"
      certificate: ""
      enabled: true
      active: true
      priority: 120
      algorithm: RS256

- name: Manage Keycloak realm key and certificate
  community.general.keycloak_realm_key:
    name: custom
    state: present
    parent_id: master
    provider_id: rsa
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      private_key: "{{ private_key }}"
      certificate: "{{ certificate }}"
      enabled: true
      active: true
      priority: 120
      algorithm: RS256

- name: Create HMAC signing key (auto-generated)
  community.general.keycloak_realm_key:
    name: hmac-custom
    state: present
    parent_id: master
    provider_id: hmac-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: HS256
      secret_size: 64

- name: Create AES encryption key (auto-generated)
  community.general.keycloak_realm_key:
    name: aes-custom
    state: present
    parent_id: master
    provider_id: aes-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      secret_size: 16

- name: Create ECDSA signing key (auto-generated)
  community.general.keycloak_realm_key:
    name: ecdsa-custom
    state: present
    parent_id: master
    provider_id: ecdsa-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: ES256
      elliptic_curve: P-256

- name: Create RSA signing key (auto-generated)
  community.general.keycloak_realm_key:
    name: rsa-auto
    state: present
    parent_id: master
    provider_id: rsa-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: RS256
      key_size: 2048

- name: Remove default HMAC key
  community.general.keycloak_realm_key:
    name: hmac-generated
    state: absent
    parent_id: myrealm
    provider_id: hmac-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      priority: 100

- name: Create RSA encryption key (auto-generated)
  community.general.keycloak_realm_key:
    name: rsa-enc-auto
    state: present
    parent_id: master
    provider_id: rsa-enc-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: RSA-OAEP
      key_size: 2048

- name: Create ECDH key exchange key (auto-generated)
  community.general.keycloak_realm_key:
    name: ecdh-custom
    state: present
    parent_id: master
    provider_id: ecdh-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: ECDH_ES
      elliptic_curve: P-256

- name: Create EdDSA signing key (auto-generated)
  community.general.keycloak_realm_key:
    name: eddsa-custom
    state: present
    parent_id: master
    provider_id: eddsa-generated
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      enabled: true
      active: true
      priority: 100
      elliptic_curve: Ed25519

- name: Import key from Java Keystore (always update passwords)
  community.general.keycloak_realm_key:
    name: jks-imported
    state: present
    parent_id: master
    provider_id: java-keystore
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    # update_password: always is the default - passwords are always sent to Keycloak
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: RS256
      keystore: /opt/keycloak/conf/keystore.jks
      keystore_password: "{{ keystore_password }}"
      key_alias: mykey
      key_password: "{{ key_password }}"

- name: Import key from Java Keystore (idempotent - only set password on create)
  community.general.keycloak_realm_key:
    name: jks-idempotent
    state: present
    parent_id: master
    provider_id: java-keystore
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    update_password: on_create  # Only send passwords when creating, preserve existing on update
    config:
      enabled: true
      active: true
      priority: 100
      algorithm: RS256
      keystore: /opt/keycloak/conf/keystore.jks
      keystore_password: "{{ keystore_password }}"
      key_alias: mykey
      key_password: "{{ key_password }}"
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str

end_state:
  description: Representation of the keycloak_realm_key after module execution.
  returned: on success
  type: dict
  contains:
    id:
      description: ID of the realm key.
      type: str
      returned: when O(state=present)
      sample: 5b7ec13f-99da-46ad-8326-ab4c73cf4ce4
    name:
      description: Name of the realm key.
      type: str
      returned: when O(state=present)
      sample: mykey
    parentId:
      description: ID of the realm this key belongs to.
      type: str
      returned: when O(state=present)
      sample: myrealm
    providerId:
      description: The ID of the key provider.
      type: str
      returned: when O(state=present)
      sample: rsa
    providerType:
      description: The type of provider.
      type: str
      returned: when O(state=present)
    config:
      description: Realm key configuration.
      type: dict
      returned: when O(state=present)
      sample:
        {
          "active": [
            "true"
          ],
          "algorithm": [
            "RS256"
          ],
          "enabled": [
            "true"
          ],
          "priority": [
            "140"
          ]
        }
    key_info:
      description:
        - Cryptographic key metadata fetched from the realm keys endpoint.
        - Only returned for V(java-keystore) provider when O(state=present) and not in check mode.
        - This includes the key ID (kid) and certificate fingerprint, which can be used to detect
          if the actual cryptographic key changed.
      type: dict
      returned: when O(provider_id=java-keystore) and O(state=present)
      version_added: 12.4.0
      contains:
        kid:
          description: The key ID (kid) - unique identifier for the cryptographic key.
          type: str
          sample: bN7p5Nc_V2M7N_-mb5vVSRVPKq5qD_OuARInB9ofsJ0
        certificate_fingerprint:
          description: SHA256 fingerprint of the certificate in colon-separated hex format.
          type: str
          sample: "A1:B2:C3:D4:E5:F6:..."
        status:
          description: The key status (ACTIVE, PASSIVE, DISABLED).
          type: str
          sample: ACTIVE
        valid_to:
          description: Certificate expiration timestamp in milliseconds since epoch.
          type: int
          sample: 1801789047000
"""

import base64
import binascii
import hashlib
from copy import deepcopy
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    KeycloakError,
    camel,
    get_token,
    keycloak_argument_spec,
)

# Provider IDs that require private_key and certificate
IMPORTED_KEY_PROVIDERS = ["rsa", "rsa-enc"]
# Provider IDs that import keys from Java Keystore
KEYSTORE_PROVIDERS = ["java-keystore"]
# Provider IDs that auto-generate keys
GENERATED_KEY_PROVIDERS = [
    "rsa-generated",
    "rsa-enc-generated",
    "hmac-generated",
    "aes-generated",
    "ecdsa-generated",
    "ecdh-generated",
    "eddsa-generated",
]

# Mapping of Ansible parameter names to Keycloak config property names
# for cases where camel() conversion doesn't produce the correct result.
# Each provider type may use a different config key for elliptic curve.
CONFIG_PARAM_MAPPING = {
    "elliptic_curve": "ecdsaEllipticCurveKey",
}

# Provider-specific config key names for elliptic_curve parameter
# ECDSA and ECDH both use the same curves (P-256, P-384, P-521) but different config keys
# EdDSA uses different curves (Ed25519, Ed448) with its own config key
ELLIPTIC_CURVE_CONFIG_KEYS = {
    "ecdsa-generated": "ecdsaEllipticCurveKey",
    "ecdh-generated": "ecdhEllipticCurveKey",
    "eddsa-generated": "eddsaEllipticCurveKey",
}

# Valid algorithm choices per provider type
# Note: aes-generated and eddsa-generated don't use algorithm config
PROVIDER_ALGORITHMS = {
    "rsa": ["RS256", "RS384", "RS512", "PS256", "PS384", "PS512"],
    "rsa-enc": ["RSA1_5", "RSA-OAEP", "RSA-OAEP-256"],
    "java-keystore": ["RS256", "RS384", "RS512", "PS256", "PS384", "PS512"],
    "rsa-generated": ["RS256", "RS384", "RS512", "PS256", "PS384", "PS512"],
    "rsa-enc-generated": ["RSA1_5", "RSA-OAEP", "RSA-OAEP-256"],
    "hmac-generated": ["HS256", "HS384", "HS512"],
    "ecdsa-generated": ["ES256", "ES384", "ES512"],
    "ecdh-generated": ["ECDH_ES", "ECDH_ES_A128KW", "ECDH_ES_A192KW", "ECDH_ES_A256KW"],
}

# Providers that don't use the algorithm config parameter
# eddsa-generated: algorithm is determined by the elliptic curve (Ed25519 or Ed448)
# aes-generated: always uses AES algorithm
PROVIDERS_WITHOUT_ALGORITHM = ["aes-generated", "eddsa-generated"]

# Providers where the RS256 default is valid (for backward compatibility)
PROVIDERS_WITH_RS256_DEFAULT = ["rsa", "rsa-generated", "java-keystore"]

# Config keys that cannot be compared and must be removed from changesets/diffs.
# privateKey/certificate: Keycloak doesn't return private keys, certificates are generated dynamically.
# keystorePassword/keyPassword: Keycloak masks these with "**********" in API responses.
SENSITIVE_CONFIG_KEYS = ["privateKey", "certificate", "keystorePassword", "keyPassword"]


def remove_sensitive_config_keys(config):
    for key in SENSITIVE_CONFIG_KEYS:
        config.pop(key, None)


def get_keycloak_config_key(param_name, provider_id=None):
    """Convert Ansible parameter name to Keycloak config key.

    Uses explicit mapping if available, otherwise applies camelCase conversion.
    For elliptic_curve, the config key depends on the provider type.
    """
    # Handle elliptic_curve specially - each provider uses a different config key
    if param_name == "elliptic_curve" and provider_id in ELLIPTIC_CURVE_CONFIG_KEYS:
        return ELLIPTIC_CURVE_CONFIG_KEYS[param_name]
    if param_name in CONFIG_PARAM_MAPPING:
        return CONFIG_PARAM_MAPPING[param_name]
    return camel(param_name)


def compute_certificate_fingerprint(certificate_pem):
    try:
        cert_der = base64.b64decode(certificate_pem)
        fingerprint = hashlib.sha256(cert_der).hexdigest().upper()
        return ":".join(fingerprint[i : i + 2] for i in range(0, len(fingerprint), 2))
    except (ValueError, binascii.Error, TypeError):
        return None


def get_key_info_for_component(kc, realm, component_id):
    try:
        keys_response = kc.get_realm_keys_metadata_by_id(realm)
        if not keys_response or "keys" not in keys_response:
            return None

        for key in keys_response.get("keys", []):
            if key.get("providerId") == component_id:
                return {
                    "kid": key.get("kid"),
                    "certificate_fingerprint": compute_certificate_fingerprint(key.get("certificate")),
                    "public_key": key.get("publicKey"),
                    "valid_to": key.get("validTo"),
                    "status": key.get("status"),
                    "algorithm": key.get("algorithm"),
                    "type": key.get("type"),
                }
        return None
    except (KeyError, TypeError):
        return None


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        name=dict(type="str", required=True),
        force=dict(type="bool", default=False),
        parent_id=dict(type="str", required=True),
        provider_id=dict(
            type="str",
            default="rsa",
            choices=[
                "rsa",
                "rsa-enc",
                "java-keystore",
                "rsa-generated",
                "rsa-enc-generated",
                "hmac-generated",
                "aes-generated",
                "ecdsa-generated",
                "ecdh-generated",
                "eddsa-generated",
            ],
        ),
        config=dict(
            type="dict",
            options=dict(
                active=dict(type="bool", default=True),
                enabled=dict(type="bool", default=True),
                priority=dict(type="int", required=True),
                algorithm=dict(
                    type="str",
                    default="RS256",
                    choices=[
                        "RS256",
                        "RS384",
                        "RS512",
                        "PS256",
                        "PS384",
                        "PS512",
                        "RSA1_5",
                        "RSA-OAEP",
                        "RSA-OAEP-256",
                        "HS256",
                        "HS384",
                        "HS512",
                        "ES256",
                        "ES384",
                        "ES512",
                        "AES",
                        "ECDH_ES",
                        "ECDH_ES_A128KW",
                        "ECDH_ES_A192KW",
                        "ECDH_ES_A256KW",
                        "Ed25519",
                        "Ed448",
                    ],
                ),
                private_key=dict(type="str", no_log=True),
                certificate=dict(type="str"),
                secret_size=dict(type="int", no_log=False),
                key_size=dict(type="int"),
                elliptic_curve=dict(type="str", choices=["P-256", "P-384", "P-521", "Ed25519", "Ed448"]),
                keystore=dict(type="str", no_log=False),
                keystore_password=dict(type="str", no_log=True),
                key_alias=dict(type="str", no_log=False),
                key_password=dict(type="str", no_log=True),
            ),
        ),
        update_password=dict(
            type="str",
            default="always",
            choices=["always", "on_create"],
            no_log=False,
        ),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"]]
        ),
        required_together=([["auth_username", "auth_password"]]),
        required_by={"refresh_token": "auth_realm"},
    )

    provider_id = module.params["provider_id"]
    config = module.params["config"] or {}
    state = module.params["state"]

    # Validate that imported key providers have the required parameters
    if state == "present" and provider_id in IMPORTED_KEY_PROVIDERS:
        if not config.get("private_key"):
            module.fail_json(msg=f"config.private_key is required for provider_id '{provider_id}'")
        if config.get("certificate") is None:
            module.fail_json(
                msg=f"config.certificate is required for provider_id '{provider_id}' (use empty string for auto-generation)"
            )

    # Validate that java-keystore providers have the required parameters
    if state == "present" and provider_id in KEYSTORE_PROVIDERS:
        required_params = ["keystore", "keystore_password", "key_alias"]
        missing = [p for p in required_params if not config.get(p)]
        if missing:
            module.fail_json(
                msg=f"For provider_id=java-keystore, the following config options are required: {', '.join(missing)}"
            )

    # Validate algorithm for providers that use it
    if state == "present":
        algorithm = config.get("algorithm")
        if provider_id in PROVIDER_ALGORITHMS:
            valid_algorithms = PROVIDER_ALGORITHMS[provider_id]
            if algorithm not in valid_algorithms:
                msg = f"algorithm '{algorithm}' is not valid for provider_id '{provider_id}'."
                if algorithm == "RS256" and provider_id not in PROVIDERS_WITH_RS256_DEFAULT:
                    msg += " The default 'RS256' is not valid for this provider."
                msg += f" Valid choices are: {', '.join(valid_algorithms)}"
                module.fail_json(msg=msg)
        elif provider_id in PROVIDERS_WITHOUT_ALGORITHM and algorithm is not None and algorithm != "RS256":
            # aes-generated and eddsa-generated don't use algorithm - only warn if user explicitly set a non-default value
            module.warn(f"algorithm is ignored for provider_id '{provider_id}'")

    # Validate elliptic curve for providers that use it
    if state == "present":
        elliptic_curve = config.get("elliptic_curve")
        if provider_id in ["ecdsa-generated", "ecdh-generated"] and elliptic_curve is not None:
            valid_curves = ["P-256", "P-384", "P-521"]
            if elliptic_curve not in valid_curves:
                module.fail_json(
                    msg=f"elliptic_curve '{elliptic_curve}' is not valid for provider_id '{provider_id}'. "
                    f"Valid choices are: {', '.join(valid_curves)}"
                )
        elif provider_id == "eddsa-generated" and elliptic_curve is not None:
            valid_curves = ["Ed25519", "Ed448"]
            if elliptic_curve not in valid_curves:
                module.fail_json(
                    msg=f"elliptic_curve '{elliptic_curve}' is not valid for provider_id '{provider_id}'. "
                    f"Valid choices are: {', '.join(valid_curves)}"
                )

    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # This will include the current state of the realm key if it is already
    # present. This is only used for diff-mode.
    before_realm_key = {}
    before_realm_key["config"] = {}

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    params_to_ignore = list(keycloak_argument_spec().keys()) + ["state", "force", "parent_id", "update_password"]

    # Filter and map the parameters names that apply to the role
    component_params = [x for x in module.params if x not in params_to_ignore and module.params.get(x) is not None]

    # We only support one component provider type in this module
    provider_type = "org.keycloak.keys.KeyProvider"

    # Build a proposed changeset from parameters given to this module
    changeset = {}
    changeset["config"] = {}

    # Generate a JSON payload for Keycloak Admin API from the module
    # parameters.  Parameters that do not belong to the JSON payload (e.g.
    # "state" or "auth_keycloal_url") have been filtered away earlier (see
    # above).
    #
    # This loop converts Ansible module parameters (snake-case) into
    # Keycloak-compatible format (camel-case). For example private_key
    # becomes privateKey.
    #
    # It also converts bool, str and int parameters into lists with a single
    # entry of 'str' type. Bool values are also lowercased. This is required
    # by Keycloak.
    #
    for component_param in component_params:
        if component_param == "config":
            for config_param in module.params["config"]:
                raw_value = module.params["config"][config_param]
                # Optional params (secret_size, key_size, elliptic_curve) default to None.
                # Skip them to avoid sending str(None) = "None" as a config value to Keycloak.
                if raw_value is None:
                    continue
                # Use custom mapping if available, otherwise camelCase
                # Pass provider_id for elliptic_curve which uses different config keys per provider
                keycloak_key = get_keycloak_config_key(config_param, provider_id)
                changeset["config"][keycloak_key] = []
                if isinstance(raw_value, bool):
                    value = str(raw_value).lower()
                else:
                    value = str(raw_value)

                changeset["config"][keycloak_key].append(value)
        else:
            # No need for camelcase in here as these are one word parameters
            new_param_value = module.params[component_param]
            changeset[camel(component_param)] = new_param_value

    # As provider_type is not a module parameter we have to add it to the
    # changeset explicitly.
    changeset["providerType"] = provider_type

    # Make a deep copy of the changeset. This is use when determining
    # changes to the current state.
    changeset_copy = deepcopy(changeset)

    # Remove keys that cannot be compared: privateKey/certificate (not returned
    # by Keycloak API) and keystore passwords (masked with "**********").
    # The actual values remain in 'changeset' for the API payload.
    remove_sensitive_config_keys(changeset_copy["config"])

    name = module.params["name"]
    force = module.params["force"]
    parent_id = module.params["parent_id"]

    # Get a list of all Keycloak components that are of keyprovider type.
    realm_keys = kc.get_components(urlencode(dict(type=provider_type)), parent_id)

    # If this component is present get its key ID. Confusingly the key ID is
    # also known as the Provider ID.
    key_id = None

    # Track individual parameter changes
    changes = ""

    # This tells Ansible whether the key was changed (added, removed, modified)
    result["changed"] = False

    # Loop through the list of components. If we encounter a component whose
    # name matches the value of the name parameter then assume the key is
    # already present.
    for key in realm_keys:
        if key["name"] == name:
            key_id = key["id"]
            changeset["id"] = key_id
            changeset_copy["id"] = key_id

            # Compare top-level parameters
            for param in changeset:
                before_realm_key[param] = key[param]

                if changeset_copy[param] != key[param] and param != "config":
                    changes += f"{param}: {key[param]} -> {changeset_copy[param]}, "
                    result["changed"] = True

            # Compare parameters under the "config" key
            # Note: Keycloak API may not return all config fields for default keys
            # (e.g., 'active', 'enabled', 'algorithm' may be missing). Handle this
            # gracefully by using .get() with defaults.
            for p, v in changeset_copy["config"].items():
                # Get the current value, defaulting to our expected value if not present
                # This handles the case where Keycloak doesn't return certain fields
                # for default/generated keys
                current_value = key["config"].get(p, v)
                before_realm_key["config"][p] = current_value
                if v != current_value:
                    changes += f"config.{p}: {current_value} -> {v}, "
                    result["changed"] = True

            # For java-keystore provider, also fetch and compare key info (kid)
            # This detects if the actual cryptographic key changed even when
            # other config parameters remain the same
            if provider_id in KEYSTORE_PROVIDERS:
                current_key_info = get_key_info_for_component(kc, parent_id, key_id)
                if current_key_info:
                    before_realm_key["key_info"] = {
                        "kid": current_key_info.get("kid"),
                        "certificate_fingerprint": current_key_info.get("certificate_fingerprint"),
                    }

    # Sanitize linefeeds for the privateKey and certificate (only for imported providers).
    # Without this the JSON payload will be invalid.
    if "privateKey" in changeset["config"]:
        changeset["config"]["privateKey"][0] = changeset["config"]["privateKey"][0].replace("\\n", "\n")
    if "certificate" in changeset["config"]:
        changeset["config"]["certificate"][0] = changeset["config"]["certificate"][0].replace("\\n", "\n")

    # For java-keystore provider: handle update_password parameter
    # When update_password=on_create and we're updating an existing component,
    # replace actual passwords with the masked value ("**********") that Keycloak
    # returns in API responses. When Keycloak receives this masked value, it
    # preserves the existing password instead of updating it.
    # This makes the module idempotent for password fields.
    update_password = module.params["update_password"]
    if provider_id in KEYSTORE_PROVIDERS and key_id and update_password == "on_create":
        SECRET_VALUE = "**********"
        if "keystorePassword" in changeset["config"]:
            changeset["config"]["keystorePassword"] = [SECRET_VALUE]
        if "keyPassword" in changeset["config"]:
            changeset["config"]["keyPassword"] = [SECRET_VALUE]

    # Check all the possible states of the resource and do what is needed to
    # converge current state with desired state (create, update or delete
    # the key).
    if key_id and state == "present":
        if result["changed"]:
            if module._diff:
                remove_sensitive_config_keys(before_realm_key["config"])
                result["diff"] = dict(before=before_realm_key, after=changeset_copy)

            if module.check_mode:
                result["msg"] = f"Realm key {name} would be changed: {changes.strip(', ')}"
            else:
                kc.update_component(changeset, parent_id)
                result["msg"] = f"Realm key {name} changed: {changes.strip(', ')}"
        elif not result["changed"] and force:
            kc.update_component(changeset, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} was forcibly updated"
        else:
            result["msg"] = f"Realm key {name} was in sync"

        result["end_state"] = changeset_copy

        # For java-keystore provider, include key info in end_state
        if provider_id in KEYSTORE_PROVIDERS:
            if not module.check_mode:
                key_info = get_key_info_for_component(kc, parent_id, key_id)
                if key_info:
                    result["end_state"]["key_info"] = {
                        "kid": key_info.get("kid"),
                        "certificate_fingerprint": key_info.get("certificate_fingerprint"),
                        "status": key_info.get("status"),
                        "valid_to": key_info.get("valid_to"),
                    }
                else:
                    module.warn(
                        f"Key component '{name}' exists but no active key was found. "
                        "This may indicate an incorrect keystore password, path, or alias."
                    )
    elif key_id and state == "absent":
        if module._diff:
            remove_sensitive_config_keys(before_realm_key["config"])
            result["diff"] = dict(before=before_realm_key, after={})

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Realm key {name} would be deleted"
        else:
            kc.delete_component(key_id, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} deleted"

        result["end_state"] = {}
    elif not key_id and state == "present":
        if module._diff:
            result["diff"] = dict(before={}, after=changeset_copy)

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Realm key {name} would be created"
        else:
            kc.create_component(changeset, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} created"

            # For java-keystore provider, fetch and include key info after creation
            if provider_id in KEYSTORE_PROVIDERS:
                # We need to get the component ID first (it was just created)
                realm_keys_after = kc.get_components(urlencode(dict(type=provider_type)), parent_id)
                for k in realm_keys_after:
                    if k["name"] == name:
                        new_key_id = k["id"]
                        key_info = get_key_info_for_component(kc, parent_id, new_key_id)
                        if key_info:
                            changeset_copy["key_info"] = {
                                "kid": key_info.get("kid"),
                                "certificate_fingerprint": key_info.get("certificate_fingerprint"),
                                "status": key_info.get("status"),
                                "valid_to": key_info.get("valid_to"),
                            }
                        else:
                            module.warn(
                                f"Key component '{name}' was created but no active key was found. "
                                "This may indicate an incorrect keystore password, path, or alias."
                            )
                        break

        result["end_state"] = changeset_copy
    elif not key_id and state == "absent":
        result["changed"] = False
        result["msg"] = f"Realm key {name} not present"
        result["end_state"] = {}

    module.exit_json(**result)


if __name__ == "__main__":
    main()
