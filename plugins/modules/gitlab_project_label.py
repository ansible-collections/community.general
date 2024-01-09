#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Gabriele Pongelli (gabriele.pongelli@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_project_label
short_description: Creates/updates/deletes GitLab Projects Labels
description:
  - When a project label does not exist, it will be created.
  - When a project label does exist, its value will be updated when the values are different.
author:
  - "Gabriele Pongelli (@gpongelli)"
requirements:
  - python >= 2.7
  - python-gitlab python module
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  state:
    description:
      - Create or delete project label.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  purge:
    description:
      - When set to V(true), delete all variables which are not mentioned in the task.
    default: false
    type: bool
    required: false
  project:
    description:
      - The path and name of the project.
    required: true
    type: str
  labels:
    version_added: 1.0.0
    description:
      - A list of dictionaries that represents gitlab project's labels.
    type: list
    elements: dict
    required: false
    default: []
    suboptions:
      name:
        description:
          - The name of the label.
        type: str
        required: true
      color:
        description:
          - The color of the label.
          - Required when O(state=present).
        type: str
      priority:
        description:
          - Integer value to give priority to the label.
        type: int
        required: false
        default: null
      description:
        description:
          - Label's description
        type: str
        default: null
      new_name:
        description:
          - Optional field to change label's name
        type: str
        default: null
'''


EXAMPLES = '''
- name: Create one Label
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
        color: #123456
    state: present

- name: Create many Labels
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
        color: #123456
        description: this is a label
        priority: 20
      - name: label_two
        color: #554422
    state: present

- name: Set or update some labels
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
        color: #224488
    state: present

- name: Add label in check mode
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
        color: #224488
    check_mode: true

- name: Delete Label
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
    state: absent

- name: Change Label name
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
        new_name: label_two
    state: absent

- name: Purge all labels
  gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    purge: true

- name: Delete many labels
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    state: absent
    labels:
      - name: label-abc123
      - name: label-two
'''

RETURN = '''
project_label:
  description: Four lists of the labels which were added, updated, removed or exist.
  returned: always
  type: dict
  contains:
    added:
      description: A list of labels which were created.
      returned: always
      type: list
      sample: ['abcd', 'label-one']
    untouched:
      description: A list of labels which exist.
      returned: always
      type: list
      sample: ['defg', 'new-label']
    removed:
      description: A list of labels which were deleted.
      returned: always
      type: list
      sample: ['defg', 'new-label']
    updated:
      description: A list pre-existing labels whose values have been set.
      returned: always
      type: list
      sample: ['defg', 'new-label']
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, ensure_gitlab_package, find_group, find_project, gitlab
)


class GitlabProjectLabels(object):

    def __init__(self, module, gitlab_instance, group_id, project_id):
        self._gitlab = gitlab_instance
        self.gitlab_object = group_id if group_id else project_id
        self._module = module

    def list_all_labels(self):
        page_nb = 1
        labels = []
        vars_page = self.gitlab_object.labels.list(page=page_nb)
        while len(vars_page) > 0:
            labels += vars_page
            page_nb += 1
            vars_page = self.gitlab_object.labels.list(page=page_nb)
        return labels

    def create_label(self, var_obj):
        if self._module.check_mode:
            return True

        var = {
            "name": var_obj.get('name'),
            "color": var_obj.get('color'),
        }

        if var_obj.get('description') is not None:
            var["description"] = var_obj.get('description')

        if var_obj.get('priority') is not None:
            var["priority"] = var_obj.get('priority')

        self.gitlab_object.labels.create(var)
        return True

    def update_label(self, var_obj):
        if self._module.check_mode:
            return True
        _label = self.gitlab_object.labels.get(var_obj.get('name'))

        if var_obj.get('new_name') is not None:
            _label.new_name = var_obj.get('new_name')

        if var_obj.get('description') is not None:
            _label.description = var_obj.get('description')
        if var_obj.get('priority') is not None:
            _label.priority = var_obj.get('priority')

        _label.save()
        return True

    def delete_label(self, var_obj):
        if self._module.check_mode:
            return True
        _label = self.gitlab_object.labels.get(var_obj.get('name'))
        _label.delete()
        return True


def compare(requested_labels, existing_labels, state):
    # we need to do this, because it was determined in a previous version - more or less buggy
    # basically it is not necessary and might result in more/other bugs!
    # but it is required  and only relevant for check mode!!
    # logic represents state 'present' when not purge. all other can be derived from that
    # untouched => equal in both
    # updated => name and scope are equal
    # added => name and scope does not exist
    untouched = list()
    updated = list()
    added = list()

    if state == 'present':
        _existing_labels = list()
        for item in existing_labels:
            _existing_labels.append({'name': item.get('name')})

        for var in requested_labels:
            if var in existing_labels:
                untouched.append(var)
            else:
                compare_item = {'name': var.get('name')}
                if compare_item in _existing_labels:
                    updated.append(var)
                else:
                    added.append(var)

    return untouched, updated, added


def native_python_main(this_gitlab, purge, requested_labels, state, module):
    change = False
    return_value = dict(added=[], updated=[], removed=[], untouched=[])

    labels_before = [x.asdict() for x in this_gitlab.list_all_labels()]

    # filter out and enrich before compare
    for item in requested_labels:
        # add defaults when not present
        if item.get('description') is None:
            item['description'] = ""
        if item.get('new_name') is None:
            item['new_name'] = None
        if item.get('priority') is None:
            item['priority'] = None

    for item in labels_before:
        # remove field only from server
        item.pop('id')
        item.pop('description_html')
        item.pop('text_color')
        item.pop('subscribed')
        item.pop('is_project_label')
        item['new_name'] = None

    if state == 'present':
        add_or_update = [x for x in requested_labels if x not in labels_before]
        for item in add_or_update:
            try:
                if this_gitlab.create_label(item):
                    return_value['added'].append(item)
            except Exception:
                # create raises exception with following error message when label already exists
                if this_gitlab.update_label(item):
                    return_value['updated'].append(item)

        if purge:
            # re-fetch
            _labels = this_gitlab.list_all_labels()

            for item in labels_before:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)

    elif state == 'absent':
        if not purge:
            _label_names_requested = [x['name'] for x in requested_labels]
            remove_requested = [x for x in labels_before if x['name'] in _label_names_requested]
            for item in remove_requested:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)
        else:
            for item in labels_before:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)

    if module.check_mode:
        _untouched, _updated, _added = compare(requested_labels, labels_before, state)
        return_value = dict(added=_added, updated=_updated, removed=return_value['removed'], untouched=_untouched)

    if any(return_value[x] for x in ['added', 'removed', 'updated']):
        change = True

    labels_after = [x.asdict() for x in this_gitlab.list_all_labels()]

    return change, return_value, labels_before, labels_after


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type='str', required=False, default=None),
        group=dict(type='str', required=False, default=None),
        purge=dict(type='bool', required=False, default=False),
        labels=dict(type='list', elements='dict', required=False, default=list(),
                    options=dict(
                        name=dict(type='str', required=True),
                        color=dict(type='str', required=False),
                        description=dict(type='str', required=False),
                        priority=dict(type='int', required=False),
                        new_name=dict(type='str', required=False),)
                    ),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
            ['project', 'group'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
            ['project', 'group']
        ],
        supports_check_mode=True
    )
    ensure_gitlab_package(module)

    gitlab_project = module.params['project']
    gitlab_group = module.params['group']
    purge = module.params['purge']
    label_list = module.params['labels']
    state = module.params['state']

    gitlab_version = gitlab.__version__
    _min_gitlab = '3.2.0'
    if LooseVersion(gitlab_version) < LooseVersion(_min_gitlab):
        module.fail_json(msg="community.general.gitlab_project_label requires python-gitlab Python module >= %s "
                             "(installed version: [%s]). Please upgrade "
                             "python-gitlab to version %s or above." % (_min_gitlab, gitlab_version, _min_gitlab))

    gitlab_instance = gitlab_authentication(module)

    # find_project can return None, but the other must exist
    gitlab_project_id = find_project(gitlab_instance, gitlab_project)

    # find_group can return None, but the other must exist
    gitlab_group_id = find_group(gitlab_instance, gitlab_group)

    # if both not found, module must exist
    if not gitlab_project_id and not gitlab_group_id:
        if not gitlab_project_id:
            module.fail_json(msg="project '%s' not found." % gitlab_project)
        if not gitlab_group_id:
            module.fail_json(msg="group '%s' not found." % gitlab_group)

    this_gitlab = GitlabProjectLabels(module=module, gitlab_instance=gitlab_instance, group_id=gitlab_group_id,
                                      project_id=gitlab_project_id)

    if state == 'present':
        _existing_labels = [x.asdict()['name'] for x in this_gitlab.list_all_labels()]

        # color is mandatory when creating label, but it's optional when changing name or updating other fields
        if any(x['color'] is None and x['new_name'] is None and x['name'] not in _existing_labels for x in label_list):
            module.fail_json(msg='color parameter is required for new labels')

    change, raw_return_value, before, after = native_python_main(this_gitlab, purge, label_list, state, module)

    if not module.check_mode:
        raw_return_value['untouched'] = [x for x in before if x in after]

    added = [x.get('name') for x in raw_return_value['added']]
    updated = [x.get('name') for x in raw_return_value['updated']]
    removed = [x.get('name') for x in raw_return_value['removed']]
    untouched = [x.get('name') for x in raw_return_value['untouched']]
    return_value = dict(added=added, updated=updated, removed=removed, untouched=untouched)

    module.exit_json(changed=change, project_label=return_value)


if __name__ == '__main__':
    main()
