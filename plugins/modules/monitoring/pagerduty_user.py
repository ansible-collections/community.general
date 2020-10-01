#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pagerduty_user
short_description: Manage a user account on PagerDuty
description:
    - This module manages the creation/removal of a user account on PagerDuty.
version_added: '1.2.0'
author: Zainab Alsaffar (@zanssa)
requirments:
    - pdpyras python module = 4.1.1
    - PagerDuty API Access
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
        choices: ['global admin', 'manager', 'responder', 'observer', 'stakeholder', 'limited skateholder', 'restricted access']
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
    pd_team:
        description:
            - The team to which the user belongs.
        type: list
        elements: str
notes:
    - Supports C(check_mode).
'''

EXAMPLES = r'''
- name: Create a user account on PagerDuty
  community.general.pagerduty_user:
    access_token: 'Your_Access_token'
    pd_user: user_full_name
    pd_email: user_email
    pd_role: user_pd_role
    pd_team: user_pd_team
    state: present

- name: Remove a user account from PagerDuty
  community.general.pagerduty_user:
    access_token: 'Your_Access_token'
    pd_user: user_full_name
    pd_email: user_email
    state: absent
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
from os import path

try:
    from pdpyras import APISession
    HAS_PD_PY = True
except ImportError:
    HAS_PD_PY = False
    PD_IMPORT_ERR = traceback.format_exc()

try:
    from pdpyras import PDClientError
    HAS_PD_CLIENT_ERR = True
except ImportError:
    HAS_PD_CLIENT_ERR = False
    PD_CLIENT_ERR_IMPORT_ERR = traceback.format_exc()


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
                "role": pd_role
                })
            return user

        except PDClientError as e:
            if e.response.status_code == 400:
                self._module.fail_json(msg="Failed to add user, %s in PagerDuty due to invalid argument %s" % (pd_name, e))
            if e.response.status_code == 401:
                self._module.fail_json(msg="Failed to add user, %s in PagerDuty due to invalid API key %s" % (pd_name, e))
            if e.response.status_code == 402:
                self._module.fail_json(msg="Failed to add user, %s in PagerDuty due to inabilities to perform the action within the API Access token provided %s" % (pd_name, e))
            if e.response.status_code == 403:
                self._module.fail_json(msg="Failed to add user, %s in PagerDuty due to inabilities to review the requested resource within the API Access token provided %s" % (pd_name, e))
            if e.response.status_code == 429:
                self._module.fail_json(msg="Failed to add user, %s in PagerDuty due to reaching the rate limit of making requests %s" % (pd_name, e))

    # delete a user account from PD
    def delete_user(self, pd_user_id, pd_name):
        try:
            user_path = path.join('/users/',pd_user_id)
            self._apisession.rdelete(user_path)

        except PDClientError as e:
            if e.response.status_code == 404:
                self._module.fail_json(msg="Failed to remove user from PagerDuty as user was not found %s: %s" % (pd_name, e))
            if e.response.status_code == 403:
                self._module.fail_json(msg="Failed to remove user from PagerDuty due to inabilities to review the requested resource within the API Access token provided %s: %s" % (pd_name, e))
            if e.response.status_code == 401:
                # print out the list of incidents
                pd_incidents = self.get_incidents_assigned_to_user(pd_user_id)
                self._module.fail_json(msg="Failed to remove user from PagerDuty as user has assigned incidents %s, %s: %s" % (pd_name, pd_incidents,e))
            if e.response.status_code == 429:
                self._module.fail_json(msg="Failed to remove user in PagerDuty due to reaching the rate limit of making requests %s: %s" % (pd_name, e))    

    # get incidents assigned to a user
    def get_incidents_assigned_to_user(self, pd_user_id):
        incident_info = {}
        incidents = self._apisession.list_all('incidents',
            params={'user_ids[]':[pd_user_id]})

        for incident in incidents:
            incident_info = {
                'title': incident['title'],
                'key': incident['incident_key'],
                'status': incident['status']
            }
        return incident_info

    # add a user to a team/teams
    def add_user_to_teams(self, pd_user_id, pd_team, pd_role):
        updated_team = None
        for team in pd_team:
            team_info = self._apisession.find('teams', team , attribute='name')
            if team_info is not None:
                try:
                    updated_team = self._apisession.rput('/teams/'+team_info['id']+'/users/'+pd_user_id, json={
                        'role':pd_role
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
            pd_role=dict(typr='str', default='responder', required=False, choices=['global admin', 'manager', 'responder', 'observer', 'stakeholder', 'limited skateholder', 'restricted access']),
            pd_team=dict(type='list', required=False)
            ),
        required_if=[['state', 'present', ['pd_team']],
        ],
        supports_check_mode=True,
    )

    if not HAS_PD_PY:
        module.fail_json(msg=missing_required_lib('pdpyras', url='https://github.com/PagerDuty/pdpyras'), exception=PD_IMPORT_ERR)

    if not HAS_PD_CLIENT_ERR:
        module.fail_json(msg=missing_required_lib('PDClientError', url='https://github.com/PagerDuty/pdpyras'), exception=PD_CLIENT_ERR_IMPORT_ERR)

    access_token = module.params['access_token']
    pd_user = module.params['pd_user']
    pd_email = module.params['pd_email']
    state = module.params['state']
    pd_role = module.params['pd_role']
    pd_team = module.params['pd_team']

    if pd_role:
        pd_role_gui_value = {
            'global admin': 'admin',
            'manager': 'user',
            'responder': 'limited_user',
            'observer': 'observer',
            'stakeholder': 'read_only_user',
            'limited stakeholder': 'read_only_limited_user',
            'restricted access': 'restricted_access'
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
            module.exit_json(changed=False, result="User account, '%s', already exists in PagerDuty. No change to report." % pd_user)

        # in case that the user does not exist
    else:
        if state == "absent":
            module.exit_json(changed=False, result="User account, '%s', was not found on PagerDuty. No change to report." % pd_user)

        else:
            # add user, adds user with the default notification rule and contact info (email)
            if not module.check_mode:
                user.add_pd_user(pd_user, pd_email, pd_role)
                # get user's id
                pd_user_id = user.does_user_exist(pd_email)
                # add a user to the team/s
                user.add_user_to_teams(pd_user_id, pd_team, pd_role)
            module.exit_json(changed=True, result="Successfully created and added the user: %s to team: %s" % (pd_user, pd_team))


if __name__=="__main__":
    main()
