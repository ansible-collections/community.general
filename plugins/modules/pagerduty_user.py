#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pagerduty_user
short_description: Manage a user account on PagerDuty
description:
    - This module manages the creation/removal of a user account on PagerDuty.
version_added: '1.3.0'
author: Zainab Alsaffar (@zanssa)
requirements:
    - pdpyras python module = 4.1.1
    - PagerDuty API Access
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    access_token:
        description:
            - An API access token to authenticate with the PagerDuty REST API.
        required: true
        type: str
    pd_user:
        description:
            - Name of the user in PagerDuty.
        required: true
        type: str
    pd_email:
        description:
            - The user's email address.
            - I(pd_email) is the unique identifier used and cannot be updated using this module.
        required: true
        type: str
    pd_role:
        description:
            - The user's role.
        choices: ['global_admin', 'manager', 'responder', 'observer', 'stakeholder', 'limited_stakeholder', 'restricted_access']
        default: 'responder'
        type: str
    state:
        description:
            - State of the user.
            - On C(present), it creates a user if the user doesn't exist.
            - On C(absent), it removes a user if the account exists.
        choices: ['present', 'absent']
        default: 'present'
        type: str
    pd_teams:
        description:
            - The teams to which the user belongs.
            - Required if I(state=present).
        type: list
        elements: str
'''

EXAMPLES = r'''
- name: Create a user account on PagerDuty
  community.general.pagerduty_user:
    access_token: 'Your_Access_token'
    pd_user: user_full_name
    pd_email: user_email
    pd_role: user_pd_role
    pd_teams: user_pd_teams
    state: "present"

- name: Remove a user account from PagerDuty
  community.general.pagerduty_user:
    access_token: 'Your_Access_token'
    pd_user: user_full_name
    pd_email: user_email
    state: "absent"
'''

RETURN = r''' # '''

from os import path
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("pdpyras", url="https://github.com/PagerDuty/pdpyras"):
    from pdpyras import APISession, PDClientError


class PagerDutyUser(object):
    def __init__(self, module, session):
        self._module = module
        self._apisession = session

    # check if the user exists
    def does_user_exist(self, pd_email):
        for user in self._apisession.iter_all('users'):
            if user['email'] == pd_email:
                return user['id']

    # create a user account on PD
    def add_pd_user(self, pd_name, pd_email, pd_role):
        try:
            user = self._apisession.persist('users', 'email', {
                "name": pd_name,
                "email": pd_email,
                "type": "user",
                "role": pd_role,
            })
            return user

        except PDClientError as e:
            if e.response.status_code == 400:
                self._module.fail_json(
                    msg="Failed to add %s due to invalid argument" % (pd_name))
            if e.response.status_code == 401:
                self._module.fail_json(msg="Failed to add %s due to invalid API key" % (pd_name))
            if e.response.status_code == 402:
                self._module.fail_json(
                    msg="Failed to add %s due to inability to perform the action within the API token" % (pd_name))
            if e.response.status_code == 403:
                self._module.fail_json(
                    msg="Failed to add %s due to inability to review the requested resource within the API token" % (pd_name))
            if e.response.status_code == 429:
                self._module.fail_json(
                    msg="Failed to add %s due to reaching the limit of making requests" % (pd_name))

    # delete a user account from PD
    def delete_user(self, pd_user_id, pd_name):
        try:
            user_path = path.join('/users/', pd_user_id)
            self._apisession.rdelete(user_path)

        except PDClientError as e:
            if e.response.status_code == 404:
                self._module.fail_json(
                    msg="Failed to remove %s as user was not found" % (pd_name))
            if e.response.status_code == 403:
                self._module.fail_json(
                    msg="Failed to remove %s due to inability to review the requested resource within the API token" % (pd_name))
            if e.response.status_code == 401:
                # print out the list of incidents
                pd_incidents = self.get_incidents_assigned_to_user(pd_user_id)
                self._module.fail_json(msg="Failed to remove %s as user has assigned incidents %s" % (pd_name, pd_incidents))
            if e.response.status_code == 429:
                self._module.fail_json(
                    msg="Failed to remove %s due to reaching the limit of making requests" % (pd_name))

    # get incidents assigned to a user
    def get_incidents_assigned_to_user(self, pd_user_id):
        incident_info = {}
        incidents = self._apisession.list_all('incidents', params={'user_ids[]': [pd_user_id]})

        for incident in incidents:
            incident_info = {
                'title': incident['title'],
                'key': incident['incident_key'],
                'status': incident['status']
            }
        return incident_info

    # add a user to a team/teams
    def add_user_to_teams(self, pd_user_id, pd_teams, pd_role):
        updated_team = None
        for team in pd_teams:
            team_info = self._apisession.find('teams', team, attribute='name')
            if team_info is not None:
                try:
                    updated_team = self._apisession.rput('/teams/' + team_info['id'] + '/users/' + pd_user_id, json={
                        'role': pd_role
                    })
                except PDClientError:
                    updated_team = None
        return updated_team


def main():
    module = AnsibleModule(
        argument_spec=dict(
            access_token=dict(type='str', required=True, no_log=True),
            pd_user=dict(type='str', required=True),
            pd_email=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            pd_role=dict(type='str', default='responder',
                         choices=['global_admin', 'manager', 'responder', 'observer', 'stakeholder', 'limited_stakeholder', 'restricted_access']),
            pd_teams=dict(type='list', elements='str', required=False)),
        required_if=[['state', 'present', ['pd_teams']], ],
        supports_check_mode=True,
    )

    deps.validate(module)

    access_token = module.params['access_token']
    pd_user = module.params['pd_user']
    pd_email = module.params['pd_email']
    state = module.params['state']
    pd_role = module.params['pd_role']
    pd_teams = module.params['pd_teams']

    if pd_role:
        pd_role_gui_value = {
            'global_admin': 'admin',
            'manager': 'user',
            'responder': 'limited_user',
            'observer': 'observer',
            'stakeholder': 'read_only_user',
            'limited_stakeholder': 'read_only_limited_user',
            'restricted_access': 'restricted_access'
        }
        pd_role = pd_role_gui_value[pd_role]

    # authenticate with PD API
    try:
        session = APISession(access_token)
    except PDClientError as e:
        module.fail_json(msg="Failed to authenticate with PagerDuty: %s" % e)

    user = PagerDutyUser(module, session)

    user_exists = user.does_user_exist(pd_email)

    if user_exists:
        if state == "absent":
            # remove user
            if not module.check_mode:
                user.delete_user(user_exists, pd_user)
            module.exit_json(changed=True, result="Successfully deleted user %s" % pd_user)
        else:
            module.exit_json(changed=False, result="User %s already exists." % pd_user)

        # in case that the user does not exist
    else:
        if state == "absent":
            module.exit_json(changed=False, result="User %s was not found." % pd_user)

        else:
            # add user, adds user with the default notification rule and contact info (email)
            if not module.check_mode:
                user.add_pd_user(pd_user, pd_email, pd_role)
                # get user's id
                pd_user_id = user.does_user_exist(pd_email)
                # add a user to the team/s
                user.add_user_to_teams(pd_user_id, pd_teams, pd_role)
            module.exit_json(changed=True, result="Successfully created & added user %s to team %s" % (pd_user, pd_teams))


if __name__ == "__main__":
    main()
