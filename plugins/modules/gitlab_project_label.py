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
    required: true
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
- name: Create Label
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

- name: Delete Label
  community.general.gitlab_project_label:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    labels:
      - name: label_one
    state: absent

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
    auth_argument_spec, gitlab_authentication, ensure_gitlab_package, find_project, gitlab
)


class GitlabProjectLabels(object):

    def __init__(self, module, gitlab_instance):
        self._gitlab = gitlab_instance
        self.project = find_project(self._gitlab, module.params['project'])
        self._module = module

    def list_all_project_labels(self):
        page_nb = 1
        labels = []
        vars_page = self.project.labels.list(page=page_nb)
        while len(vars_page) > 0:
            labels += vars_page
            page_nb += 1
            vars_page = self.project.labels.list(page=page_nb)
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

        self.project.labels.create(var)
        return True

    def update_label(self, var_obj):
        if self._module.check_mode:
            return True
        _label = self.project.labels.get(var_obj.get('name'))

        if var_obj.get('new_name') is not None:
            _label.new_name = var_obj.get('new_name')

        if var_obj.get('description') is not None:
            _label["description"] = var_obj.get('description')
        if var_obj.get('priority') is not None:
            _label["priority"] = var_obj.get('priority')

        _label.save()
        return True

    def delete_label(self, var_obj):
        if self._module.check_mode:
            return True
        self.project.labels.delete(var_obj.get('name'))
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

    existing_labels = this_gitlab.list_all_project_labels()
    before = [x.attributes for x in existing_labels]

    # filter out and enrich before compare
    for item in requested_labels:
        item['name'] = item.pop('name')
        item['color'] = str(item.get('color'))
        if item.get('description') is None:
            item['description'] = ""
        if item.get('new_name') is None:
            item['new_name'] = None
        if item.get('priority') is None:
            item['priority'] = None

    if module.check_mode:
        _untouched, _updated, _added = compare(requested_labels, existing_labels, state)

    if state == 'present':
        add_or_update = [x for x in requested_labels if x not in existing_labels]
        for item in add_or_update:
            try:
                if this_gitlab.create_label(item):
                    return_value['added'].append(item)

            except Exception:
                if this_gitlab.update_label(item):
                    return_value['updated'].append(item)

        if purge:
            # refetch and filter
            existing_labels = this_gitlab.list_all_project_labels()

            remove = [x for x in existing_labels if x not in requested_labels]
            for item in remove:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)

    elif state == 'absent':
        # value does not matter on removing labels.
        for item in existing_labels:
            item.pop('name')
        for item in requested_labels:
            item.pop('name')

        if not purge:
            remove_requested = [x for x in requested_labels if x in existing_labels]
            for item in remove_requested:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)
        else:
            for item in existing_labels:
                if this_gitlab.delete_label(item):
                    return_value['removed'].append(item)

    if module.check_mode:
        return_value = dict(added=_added, updated=_updated, removed=return_value['removed'], untouched=_untouched)

    if any(return_value[x] for x in ['added', 'removed', 'updated']):
        change = True

    existing_labels = this_gitlab.list_all_project_labels()
    after = [x.attributes for x in existing_labels]

    return change, return_value, before, after


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type='str', required=True),
        purge=dict(type='bool', required=False, default=False),
        labels=dict(type='list', elements='dict', required=True, default=list(),
                    options=dict(
                        name=dict(type='str', required=True),
                        color=dict(type='str', required=False),
                        description=dict(type='str', required=False),
                        priority=dict(type='int', required=False),
                        new_name=dict(type='str', required=False),
        )),
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
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True
    )
    ensure_gitlab_package(module)

    gitlab_project = module.params['project']
    purge = module.params['purge']
    label_list = module.params['labels']
    state = module.params['state']

    gitlab_version = gitlab.__version__
    _min_gitlab = '3.2.0'
    if LooseVersion(gitlab_version) < LooseVersion(_min_gitlab):
        module.fail_json(msg="community.general.gitlab_project_label requires python-gitlab Python module >= %s "
                             "(installed version: [%s]). Please upgrade "
                             "python-gitlab to version %s or above." % (_min_gitlab, gitlab_version, _min_gitlab))

    if state == 'present':
        # color is mandatory when creating label
        if any(x['color'] is None for x in label_list):
            module.fail_json(msg='color parameter is required for all labels in state present')

    gitlab_instance = gitlab_authentication(module)

    gitlab_project_id = find_project(gitlab_instance, gitlab_project)
    if not gitlab_project_id:
        module.fail_json(msg="project '%s' not found." % gitlab_project)

    this_gitlab = GitlabProjectLabels(module=module, gitlab_instance=gitlab_instance)

    change, raw_return_value, before, after = native_python_main(this_gitlab, purge, label_list, state, module)

    if not module.check_mode:
        raw_return_value['untouched'] = [x for x in before if x in after]

    added = [x.get('name') for x in raw_return_value['added']]
    updated = [x.get('name') for x in raw_return_value['updated']]
    removed = [x.get('name') for x in raw_return_value['removed']]
    untouched = [x.get('name') for x in raw_return_value['untouched']]
    return_value = dict(added=added, updated=updated, removed=removed, untouched=untouched)

    module.exit_json(changed=change, project_variable=return_value)


if __name__ == '__main__':
    main()
