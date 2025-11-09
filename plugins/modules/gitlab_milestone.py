#!/usr/bin/python

# Copyright (c) 2023, Gabriele Pongelli (gabriele.pongelli@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: gitlab_milestone
short_description: Creates/updates/deletes GitLab Milestones belonging to project or group
version_added: 8.3.0
description:
  - When a milestone does not exist, it is created.
  - When a milestone does exist, its value is updated when the values are different.
  - Milestones can be purged.
author:
  - "Gabriele Pongelli (@gpongelli)"
requirements:
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
      - Create or delete milestone.
    default: present
    type: str
    choices: ["present", "absent"]
  purge:
    description:
      - When set to V(true), delete all milestone which are not mentioned in the task.
    default: false
    type: bool
  project:
    description:
      - The path and name of the project. Either this or O(group) is required.
    type: str
  group:
    description:
      - The path of the group. Either this or O(project) is required.
    type: str
  milestones:
    description:
      - A list of dictionaries that represents gitlab project's or group's milestones.
    type: list
    elements: dict
    default: []
    suboptions:
      title:
        description:
          - The name of the milestone.
        type: str
        required: true
      due_date:
        description:
          - Milestone due date in YYYY-MM-DD format.
        type: str
        default: null
      start_date:
        description:
          - Milestone start date in YYYY-MM-DD format.
        type: str
        default: null
      description:
        description:
          - Milestone's description.
        type: str
        default: null
"""


EXAMPLES = r"""
# same project's task can be executed for group
- name: Create one milestone
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    milestones:
      - title: milestone_one
        start_date: "2024-01-04"
    state: present

- name: Create many group milestones
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    group: "group1"
    milestones:
      - title: milestone_one
        start_date: "2024-01-04"
        description: this is a milestone
        due_date: "2024-02-04"
      - title: milestone_two
    state: present

- name: Create many project milestones
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    milestones:
      - title: milestone_one
        start_date: "2024-01-04"
        description: this is a milestone
        due_date: "2024-02-04"
      - title: milestone_two
    state: present

- name: Set or update some milestones
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    milestones:
      - title: milestone_one
        start_date: "2024-05-04"
    state: present

- name: Add milestone in check mode
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    milestones:
      - title: milestone_one
        start_date: "2024-05-04"
    check_mode: true

- name: Delete milestone
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    milestones:
      - title: milestone_one
    state: absent

- name: Purge all milestones
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    purge: true

- name: Delete many milestones
  community.general.gitlab_milestone:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    state: absent
    milestones:
      - title: milestone-abc123
      - title: milestone-two
"""

RETURN = r"""
milestones:
  description: Four lists of the milestones which were added, updated, removed or exist.
  returned: success
  type: dict
  contains:
    added:
      description: A list of milestones which were created.
      returned: always
      type: list
      sample: ["abcd", "milestone-one"]
    untouched:
      description: A list of milestones which exist.
      returned: always
      type: list
      sample: ["defg", "new-milestone"]
    removed:
      description: A list of milestones which were deleted.
      returned: always
      type: list
      sample: ["defg", "new-milestone"]
    updated:
      description: A list pre-existing milestones whose values have been set.
      returned: always
      type: list
      sample: ["defg", "new-milestone"]
milestones_obj:
  description: API object.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec,
    gitlab_authentication,
    ensure_gitlab_package,
    find_group,
    find_project,
)
from datetime import datetime


class GitlabMilestones:
    def __init__(self, module, gitlab_instance, group_id, project_id):
        self._gitlab = gitlab_instance
        self.gitlab_object = group_id if group_id else project_id
        self.is_group_milestone = True if group_id else False
        self._module = module

    def list_all_milestones(self):
        page_nb = 1
        milestones = []
        vars_page = self.gitlab_object.milestones.list(page=page_nb)
        while len(vars_page) > 0:
            milestones += vars_page
            page_nb += 1
            vars_page = self.gitlab_object.milestones.list(page=page_nb)
        return milestones

    def create_milestone(self, var_obj):
        if self._module.check_mode:
            return True, True

        var = {
            "title": var_obj.get("title"),
        }

        if var_obj.get("description") is not None:
            var["description"] = var_obj.get("description")

        if var_obj.get("start_date") is not None:
            var["start_date"] = self.check_date(var_obj.get("start_date"))

        if var_obj.get("due_date") is not None:
            var["due_date"] = self.check_date(var_obj.get("due_date"))

        _obj = self.gitlab_object.milestones.create(var)
        return True, _obj.asdict()

    def update_milestone(self, var_obj):
        if self._module.check_mode:
            return True, True
        _milestone = self.gitlab_object.milestones.get(self.get_milestone_id(var_obj.get("title")))

        if var_obj.get("description") is not None:
            _milestone.description = var_obj.get("description")

        if var_obj.get("start_date") is not None:
            _milestone.start_date = var_obj.get("start_date")

        if var_obj.get("due_date") is not None:
            _milestone.due_date = var_obj.get("due_date")

        # save returns None
        _milestone.save()
        return True, _milestone.asdict()

    def get_milestone_id(self, _title):
        _milestone_list = self.gitlab_object.milestones.list()
        _found = [x for x in _milestone_list if x.title == _title]
        if _found:
            return _found[0].id
        else:
            self._module.fail_json(msg=f"milestone '{_title}' not found.")

    def check_date(self, _date):
        try:
            datetime.strptime(_date, "%Y-%m-%d")
        except ValueError:
            self._module.fail_json(msg=f"milestone's date '{_date}' not in correct format.")
        return _date

    def delete_milestone(self, var_obj):
        if self._module.check_mode:
            return True, True
        _milestone = self.gitlab_object.milestones.get(self.get_milestone_id(var_obj.get("title")))
        # delete returns None
        _milestone.delete()
        return True, _milestone.asdict()


def compare(requested_milestones, existing_milestones, state):
    # we need to do this, because it was determined in a previous version - more or less buggy
    # basically it is not necessary and might result in more/other bugs!
    # but it is required  and only relevant for check mode!!
    # logic represents state 'present' when not purge. all other can be derived from that
    # untouched => equal in both
    # updated => title are equal
    # added => title does not exist
    untouched = list()
    updated = list()
    added = list()

    if state == "present":
        _existing_milestones = list()
        for item in existing_milestones:
            _existing_milestones.append({"title": item.get("title")})

        for var in requested_milestones:
            if var in existing_milestones:
                untouched.append(var)
            else:
                compare_item = {"title": var.get("title")}
                if compare_item in _existing_milestones:
                    updated.append(var)
                else:
                    added.append(var)

    return untouched, updated, added


def native_python_main(this_gitlab, purge, requested_milestones, state, module):
    change = False
    return_value = dict(added=[], updated=[], removed=[], untouched=[])
    return_obj = dict(added=[], updated=[], removed=[])

    milestones_before = [x.asdict() for x in this_gitlab.list_all_milestones()]

    # filter out and enrich before compare
    for item in requested_milestones:
        # add defaults when not present
        if item.get("description") is None:
            item["description"] = ""
        if item.get("due_date") is None:
            item["due_date"] = None
        if item.get("start_date") is None:
            item["start_date"] = None

    for item in milestones_before:
        # remove field only from server
        item.pop("id")
        item.pop("iid")
        item.pop("created_at")
        item.pop("expired")
        item.pop("state")
        item.pop("updated_at")
        item.pop("web_url")
        # group milestone has group_id, while project has project_id
        if "group_id" in item:
            item.pop("group_id")
        if "project_id" in item:
            item.pop("project_id")

    if state == "present":
        add_or_update = [x for x in requested_milestones if x not in milestones_before]
        for item in add_or_update:
            try:
                _rv, _obj = this_gitlab.create_milestone(item)
                if _rv:
                    return_value["added"].append(item)
                    return_obj["added"].append(_obj)
            except Exception:
                # create raises exception with following error message when milestone already exists
                _rv, _obj = this_gitlab.update_milestone(item)
                if _rv:
                    return_value["updated"].append(item)
                    return_obj["updated"].append(_obj)

        if purge:
            # re-fetch
            _milestones = this_gitlab.list_all_milestones()

            for item in milestones_before:
                _rv, _obj = this_gitlab.delete_milestone(item)
                if _rv:
                    return_value["removed"].append(item)
                    return_obj["removed"].append(_obj)

    elif state == "absent":
        if not purge:
            _milestone_titles_requested = [x["title"] for x in requested_milestones]
            remove_requested = [x for x in milestones_before if x["title"] in _milestone_titles_requested]
            for item in remove_requested:
                _rv, _obj = this_gitlab.delete_milestone(item)
                if _rv:
                    return_value["removed"].append(item)
                    return_obj["removed"].append(_obj)
        else:
            for item in milestones_before:
                _rv, _obj = this_gitlab.delete_milestone(item)
                if _rv:
                    return_value["removed"].append(item)
                    return_obj["removed"].append(_obj)

    if module.check_mode:
        _untouched, _updated, _added = compare(requested_milestones, milestones_before, state)
        return_value = dict(added=_added, updated=_updated, removed=return_value["removed"], untouched=_untouched)

    if any(return_value[x] for x in ["added", "removed", "updated"]):
        change = True

    milestones_after = [x.asdict() for x in this_gitlab.list_all_milestones()]

    return change, return_value, milestones_before, milestones_after, return_obj


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type="str"),
        group=dict(type="str"),
        purge=dict(type="bool", default=False),
        milestones=dict(
            type="list",
            elements="dict",
            default=[],
            options=dict(
                title=dict(type="str", required=True),
                description=dict(type="str"),
                due_date=dict(type="str"),
                start_date=dict(type="str"),
            ),
        ),
        state=dict(type="str", default="present", choices=["absent", "present"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ["api_username", "api_token"],
            ["api_username", "api_oauth_token"],
            ["api_username", "api_job_token"],
            ["api_token", "api_oauth_token"],
            ["api_token", "api_job_token"],
            ["project", "group"],
        ],
        required_together=[
            ["api_username", "api_password"],
        ],
        required_one_of=[["api_username", "api_token", "api_oauth_token", "api_job_token"], ["project", "group"]],
        supports_check_mode=True,
    )
    ensure_gitlab_package(module)

    gitlab_project = module.params["project"]
    gitlab_group = module.params["group"]
    purge = module.params["purge"]
    milestone_list = module.params["milestones"]
    state = module.params["state"]

    gitlab_instance = gitlab_authentication(module, min_version="3.2.0")

    # find_project can return None, but the other must exist
    gitlab_project_id = find_project(gitlab_instance, gitlab_project)

    # find_group can return None, but the other must exist
    gitlab_group_id = find_group(gitlab_instance, gitlab_group)

    # if both not found, module must exist
    if not gitlab_project_id and not gitlab_group_id:
        if gitlab_project and not gitlab_project_id:
            module.fail_json(msg=f"project '{gitlab_project}' not found.")
        if gitlab_group and not gitlab_group_id:
            module.fail_json(msg=f"group '{gitlab_group}' not found.")

    this_gitlab = GitlabMilestones(
        module=module, gitlab_instance=gitlab_instance, group_id=gitlab_group_id, project_id=gitlab_project_id
    )

    change, raw_return_value, before, after, _obj = native_python_main(
        this_gitlab, purge, milestone_list, state, module
    )

    if not module.check_mode:
        raw_return_value["untouched"] = [x for x in before if x in after]

    added = [x.get("title") for x in raw_return_value["added"]]
    updated = [x.get("title") for x in raw_return_value["updated"]]
    removed = [x.get("title") for x in raw_return_value["removed"]]
    untouched = [x.get("title") for x in raw_return_value["untouched"]]
    return_value = dict(added=added, updated=updated, removed=removed, untouched=untouched)

    module.exit_json(changed=change, milestones=return_value, milestones_obj=_obj)


if __name__ == "__main__":
    main()
