# !/usr/bin/python
# Copyright Jakub Danek <danek.ja@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_realm_localization

short_description: Allows management of Keycloak realm localization overrides via the Keycloak API

version_added: 12.4.0

description:
  - This module allows you to manage per-locale message overrides for a Keycloak realm using the Keycloak Admin REST API.
  - Requires access via OpenID Connect; the connecting user/client must have sufficient privileges.
  - The names of module options are snake_cased versions of the names found in the Keycloak API.

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  force:
    description:
      - If V(false), only the keys listed in the O(overrides) are modified by this module. Any other pre-existing
        keys are ignored.
      - If V(true), all locale overrides are made to match configuration of this module. For example any keys
        missing from the O(overrides) are removed regardless of O(state) value.
    type: bool
    default: false
  locale:
    description:
      - Locale code for which the overrides apply (for example, V(en), V(fi), V(de)).
    type: str
    required: true
  parent_id:
    description:
      - Name of the realm that owns the locale overrides.
    type: str
    required: true
  state:
    description:
      - Desired state of localization overrides for the given locale.
      - On V(present), the set of overrides for the locale are made to match O(overrides).
        If O(force) is V(true) keys not listed in O(overrides) are removed,
        and the listed keys are created or updated.
        If O(force) is V(false)  keys not listed in O(overrides) are ignored,
        and the listed keys are created or updated.
      - On V(absent), overrides for the locale is removed. If O(force) is V(true), all keys are removed.
        If O(force) is V(false), only the keys listed in O(overrides) are removed.
    type: str
    choices: ['present', 'absent']
    default: present
  overrides:
    description:
      - List of overrides to ensure for the locale when O(state=present). Each item is a mapping with
        the record's O(overrides[].key) and its O(overrides[].value).
      - Ignored when O(state=absent).
    type: list
    elements: dict
    default: []
    suboptions:
      key:
        description:
          - The message key to override.
        type: str
        required: true
      value:
        description:
          - The override value for the message key. If omitted, value defaults to an empty string.
        type: str
        default: ""
        required: false

seealso:
  - module: community.general.keycloak_realm
    description: You can specify list of supported locales using O(community.general.keycloak_realm#module:supported_locales).

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author: Jakub Danek (@danekja)
"""

EXAMPLES = r"""
- name: Replace all overrides for locale "en" (credentials auth)
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parent_id: my-realm
    locale: en
    state: present
    force: true
    overrides:
      - key: greeting
        value: "Hello"
      - key: farewell
        value: "Bye"
  delegate_to: localhost

- name: Replace listed overrides for locale "en" (credentials auth)
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parent_id: my-realm
    locale: en
    state: present
    force: false
    overrides:
      - key: greeting
        value: "Hello"
      - key: farewell
        value: "Bye"
  delegate_to: localhost

- name: Ensure only one override exists for locale "fi" (token auth)
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    parent_id: my-realm
    locale: fi
    state: present
    force: true
    overrides:
      - key: app.title
        value: "Sovellukseni"
  delegate_to: localhost

- name: Remove all overrides for locale "de"
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parent_id: my-realm
    locale: de
    state: absent
    force: true
  delegate_to: localhost

- name: Remove only the listed overrides for locale "de"
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parent_id: my-realm
    locale: de
    state: absent
    force: false
    overrides:
      - key: app.title
      - key: foo
      - key: bar
  delegate_to: localhost
"""

RETURN = r"""
end_state:
  description:
    - Final state of localization overrides for the locale after module execution.
    - Contains the O(locale) and the list of O(overrides) as key/value items.
  returned: on success
  type: dict
  contains:
    locale:
      description: The locale code affected.
      type: str
      sample: en
    overrides:
      description: The list of overrides that exist after execution.
      type: list
      elements: dict
      sample:
        - key: greeting
          value: Hello
        - key: farewell
          value: Bye
"""

from copy import deepcopy

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    KeycloakError,
    get_token,
    keycloak_argument_spec,
)


def _normalize_overrides(current: dict | None) -> list[dict]:
    """
    Accepts:
      - dict: {'k1': 'v1', ...}
    Return a sorted list of {'key', 'value'}.

    This helper provides a consistent shape for downstream comparison/diff logic.
    """
    if not current:
        return []

    return [{"key": k, "value": v} for k, v in sorted(current.items())]


def main():
    argument_spec = keycloak_argument_spec()

    # Single override record structure
    overrides_spec = dict(
        key=dict(type="str", no_log=False, required=True),
        value=dict(type="str", default=""),
    )

    meta_args = dict(
        locale=dict(type="str", required=True),
        parent_id=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        overrides=dict(type="list", elements="dict", options=overrides_spec, default=[]),
        force=dict(type="bool", default=False),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=([["token", "auth_realm", "auth_username", "auth_password"]]),
        required_together=([["auth_realm", "auth_username", "auth_password"]]),
    )

    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Convenience locals for frequently used parameters
    locale = module.params["locale"]
    state = module.params["state"]
    parent_id = module.params["parent_id"]
    force = module.params["force"]

    desired_raw = module.params["overrides"]
    desired_overrides = _normalize_overrides({r["key"]: r.get("value") for r in desired_raw})

    old_overrides = _normalize_overrides(kc.get_localization_values(locale, parent_id) or {})
    before = {
        "locale": locale,
        "overrides": deepcopy(old_overrides),
    }

    # Proposed state used for diff reporting
    changeset = {
        "locale": locale,
        "overrides": [],
    }

    result["changed"] = False

    if state == "present":
        changeset["overrides"] = deepcopy(desired_overrides)

        # Compute two sets:
        # - to_update: keys missing or with different values
        # - to_remove: keys existing in current state but not in desired
        to_update = []
        to_remove = deepcopy(old_overrides)

        # Mark updates and remove matched ones from to_remove
        for record in desired_overrides:
            override_found = False

            for override in to_remove:
                if override["key"] == record["key"]:
                    override_found = True

                    # Value differs -> update needed
                    if override["value"] != record["value"]:
                        result["changed"] = True
                        to_update.append(record)

                    # Remove processed item so what's left in to_remove are deletions
                    to_remove.remove(override)
                    break

            if not override_found:
                # New key, must be created
                to_update.append(record)
                result["changed"] = True

        # ignore any left-overs in to_remove, force is false
        if not force:
            changeset["overrides"].extend(to_remove)
            to_remove = []

        if to_remove:
            result["changed"] = True

        if result["changed"]:
            if module._diff:
                result["diff"] = dict(before=before, after=changeset)

            if module.check_mode:
                result["msg"] = f"Locale {locale} overrides would be updated."

            else:
                for override in to_remove:
                    kc.delete_localization_value(locale, override["key"], parent_id)

                for override in to_update:
                    kc.set_localization_value(locale, override["key"], override["value"], parent_id)

                result["msg"] = f"Locale {locale} overrides have been updated."

        else:
            result["msg"] = f"Locale {locale} overrides are in sync."

        # For accurate end_state, read back from API unless we are in check_mode
        if not module.check_mode:
            final_overrides = _normalize_overrides(kc.get_localization_values(locale, parent_id) or {})

        else:
            final_overrides = ["overrides"]

        result["end_state"] = {"locale": locale, "overrides": final_overrides}

    elif state == "absent":
        if force:
            to_remove = old_overrides

        else:
            # touch only overrides listed in parameters, leave the rest be
            to_remove = deepcopy(desired_overrides)
            to_keep = deepcopy(old_overrides)

            for override in to_remove:
                found = False
                for keep in to_keep:
                    if override["key"] == keep["key"]:
                        to_keep.remove(keep)
                        found = True
                        break

                if not found:
                    to_remove.remove(override)

            changeset["overrides"] = to_keep

        if to_remove:
            result["changed"] = True

        if module._diff:
            result["diff"] = dict(before=before, after=changeset)

        if module.check_mode:
            if result["changed"]:
                result["msg"] = f"{len(to_remove)} overrides for locale {locale} would be deleted."
            else:
                result["msg"] = f"No overrides for locale {locale} to be deleted."

        else:
            for override in to_remove:
                kc.delete_localization_value(locale, override["key"], parent_id)

            if result["changed"]:
                result["msg"] = f"{len(to_remove)} overrides for locale {locale} deleted."
            else:
                result["msg"] = f"No overrides for locale {locale} to be deleted."

        result["end_state"] = changeset

    module.exit_json(**result)


if __name__ == "__main__":
    main()
