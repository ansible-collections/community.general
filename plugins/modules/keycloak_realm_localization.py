# Python
# !/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Jakub Danek <danek.ja@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_realm_localization

short_description: Manage Keycloak realm localization overrides via the Keycloak API

version_added: 11.4.0

description:
  - Manage per-locale message overrides for a Keycloak realm using the Keycloak Admin REST API.
  - Requires access via OpenID Connect; the connecting user/client must have sufficient privileges.
  - The names of module options are snake_cased versions of the names found in the Keycloak API.

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  append:
    description:
      - If V(true), only the keys listed in the O(overrides) will be modified by this module. Any other pre-existing
        keys will be ignored.
      - If V(false), all locale overrides will be made to match configuration of this module. I.e. any keys
        missing from the O(overrides) will be removed regardless of O(state) value.
    type: bool
    default: true
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
      - On V(present), the set of overrides for the locale will be made to match O(overrides).
        If O(append) is V(false) keys not listed in O(overrides) will be removed,
        and the listed keys will be created or updated.
        If O(append) is V(true)  keys not listed in O(overrides) will be ignored,
        and the listed keys will be created or updated.
      - On V(absent), overrides for the locale will be removed. If O(append) is V(false), all keys will be removed.
        If O(append) is V(true), only the keys listed in O(overrides) will be removed.
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
          - The override value for the message key. If omitted, value will be set to an empty string.
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
    append: false
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
    append: false
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
    append: false
  delegate_to: localhost

- name: Dry run - see what would change for locale "en"
  community.general.keycloak_realm_localization:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parent_id: my-realm
    locale: en
    state: present
    overrides:
      - key: greeting
        value: "Hello again"
  check_mode: true
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


def _normalize_overrides_from_api(current):
    """
    Accepts:
      - dict: {'k1': 'v1', ...}
    Return a sorted list of {'key', 'value'}.

    This helper provides a consistent shape for downstream comparison/diff logic.
    """
    if not current:
        return []

    # Convert mapping to list of key/value dicts
    items = [{"key": k, "value": v} for k, v in sorted(current.items())]

    # Sort for stable comparisons and diff output
    return items


def main():
    """
    Module execution

    :return:
    """
    # Base Keycloak auth/spec fragment common across Keycloak modules
    argument_spec = keycloak_argument_spec()

    # Describe a single override record
    overrides_spec = dict(
        key=dict(type="str", no_log=False, required=True),
        value=dict(type="str", default=""),
    )

    # Module-specific arguments
    meta_args = dict(
        locale=dict(type="str", required=True),
        parent_id=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        overrides=dict(type="list", elements="dict", options=overrides_spec, default=[]),
        append=dict(type="bool", default=True),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        # Require token OR full credential set. This mirrors other Keycloak modules.
        required_one_of=([["token", "auth_realm", "auth_username", "auth_password"]]),
        required_together=([["auth_realm", "auth_username", "auth_password"]]),
    )

    # Initialize the result object used by Ansible
    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Convenience locals for frequently used parameters
    locale = module.params.get("locale")
    state = module.params.get("state")
    parent_id = module.params.get("parent_id")
    append = module.params.get("append")

    desired_raw = module.params.get("overrides") or []
    desired_map = {r["key"]: r.get("value") for r in desired_raw}
    desired_overrides = [{"key": k, "value": v} for k, v in sorted(desired_map.items())]

    # Fetch current overrides and normalize to comparable structure
    old_overrides = _normalize_overrides_from_api(kc.get_localization_values(locale, parent_id) or {})
    before = {
        "locale": locale,
        "overrides": deepcopy(old_overrides),
    }

    # Proposed state used for diff reporting
    changeset = {
        "locale": locale,
        "overrides": [],
    }

    # Default to no change; flip to True when updates/deletes are needed
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

        # ignore any left-overs in to_remove, append is true
        if append:
            changeset["overrides"].extend(to_remove)
            to_remove = []

        # Any leftovers in to_remove must be deleted
        if to_remove:
            result["changed"] = True

        if result["changed"]:
            if module._diff:
                result["diff"] = dict(before=before, after=changeset)

            if module.check_mode:
                # Dry-run: report intent without side effects
                result["msg"] = "Locale %s overrides would be updated." % (locale)

            else:
                for override in to_remove:
                    kc.delete_localization_value(locale, override["key"], parent_id)

                for override in to_update:
                    kc.set_localization_value(locale, override["key"], override["value"], parent_id)

                result["msg"] = "Locale %s overrides have been updated." % (locale)

        else:
            result["msg"] = "Locale %s overrides are in sync." % (locale)

        # For accurate end_state, read back from API unless we are in check_mode
        if not module.check_mode:
            final_overrides = _normalize_overrides_from_api(kc.get_localization_values(locale, parent_id) or {})

        else:
            final_overrides = ["overrides"]

        result["end_state"] = {"locale": locale, "overrides": final_overrides}

    elif state == "absent":
        # touch only overrides listed in parameters, leave the rest be
        if append:
            to_remove = deepcopy(desired_overrides)
            to_keep = deepcopy(old_overrides)

            for override in to_remove:
                found = False
                for keep in to_keep:
                    if override["key"] == keep["key"]:
                        to_keep.remove(keep)
                        found = True
                        break

                # not present
                if not found:
                    to_remove.remove(override)

            changeset["overrides"] = to_keep

        else:
            to_remove = old_overrides

        if to_remove:
            result["changed"] = True

        if module._diff:
            result["diff"] = dict(before=before, after=changeset)

        if module.check_mode:
            if result["changed"]:
                result["msg"] = "Overrides for locale %s would be deleted." % (locale)
            else:
                result["msg"] = "No overrides for locale %s to be deleted." % (locale)

        else:
            for override in to_remove:
                kc.delete_localization_value(locale, override["key"], parent_id)

            result["msg"] = "Locale %s has no overrides." % (locale)

        result["end_state"] = changeset

    module.exit_json(**result)


if __name__ == "__main__":
    main()
