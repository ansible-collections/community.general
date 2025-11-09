#!/usr/bin/python

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: gitlab_project
short_description: Creates/updates/deletes GitLab Projects
description:
  - When the project does not exist in GitLab, it is created.
  - When the project does exist and O(state=absent), the project is deleted.
  - When changes are made to the project, the project is updated.
author:
  - Werner Dijkerman (@dj-wasabi)
  - Guillaume Martinez (@Lunik)
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
  allow_merge_on_skipped_pipeline:
    description:
      - Allow merge when skipped pipelines exist.
    type: bool
    version_added: "3.4.0"
  avatar_path:
    description:
      - Absolute path image to configure avatar. File size should not exceed 200 kb.
      - This option is only used on creation, not for updates.
    type: path
    version_added: "4.2.0"
  build_timeout:
    description:
      - Maximum number of seconds a CI job can run.
      - If not specified on creation, GitLab imposes a default value.
    type: int
    version_added: "10.6.0"
  builds_access_level:
    description:
      - V(private) means that repository CI/CD is allowed only to project members.
      - V(disabled) means that repository CI/CD is disabled.
      - V(enabled) means that repository CI/CD is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.2.0"
  ci_config_path:
    description:
      - Custom path to the CI configuration file for this project.
    type: str
    version_added: "3.7.0"
  container_expiration_policy:
    description:
      - Project cleanup policy for its container registry.
    type: dict
    suboptions:
      cadence:
        description:
          - How often cleanup should be run.
        type: str
        choices: ["1d", "7d", "14d", "1month", "3month"]
      enabled:
        description:
          - Enable the cleanup policy.
        type: bool
      keep_n:
        description:
          - Number of tags kept per image name.
          - V(0) clears the field.
        type: int
        choices: [0, 1, 5, 10, 25, 50, 100]
      older_than:
        description:
          - Destroy tags older than this.
          - V(0d) clears the field.
        type: str
        choices: ["0d", "7d", "14d", "30d", "90d"]
      name_regex:
        description:
          - Destroy tags matching this regular expression.
        type: str
      name_regex_keep:
        description:
          - Keep tags matching this regular expression.
        type: str
    version_added: "9.3.0"
  container_registry_access_level:
    description:
      - V(private) means that container registry is allowed only to project members.
      - V(disabled) means that container registry is disabled.
      - V(enabled) means that container registry is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.2.0"
  default_branch:
    description:
      - The default branch name for this project.
      - For project creation, this option requires O(initialize_with_readme=true).
      - For project update, the branch must exist.
      - Supports project's default branch update since community.general 8.0.0.
    type: str
    version_added: "4.2.0"
  description:
    description:
      - An description for the project.
    type: str
  environments_access_level:
    description:
      - V(private) means that deployment to environment is allowed only to project members.
      - V(disabled) means that deployment to environment is disabled.
      - V(enabled) means that deployment to environment is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  feature_flags_access_level:
    description:
      - V(private) means that feature rollout is allowed only to project members.
      - V(disabled) means that feature rollout is disabled.
      - V(enabled) means that feature rollout is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  forking_access_level:
    description:
      - V(private) means that repository forks is allowed only to project members.
      - V(disabled) means that repository forks are disabled.
      - V(enabled) means that repository forks are enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.2.0"
  group:
    description:
      - ID or the full path of the group of which this projects belongs to.
    type: str
  import_url:
    description:
      - Git repository which is imported into gitlab.
      - GitLab server needs read access to this git repository.
    type: str
  infrastructure_access_level:
    description:
      - V(private) means that configuring infrastructure is allowed only to project members.
      - V(disabled) means that configuring infrastructure is disabled.
      - V(enabled) means that configuring infrastructure is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  initialize_with_readme:
    description:
      - Initializes the project with a default C(README.md).
      - Is only used when the project is created, and ignored otherwise.
    type: bool
    default: false
    version_added: "4.0.0"
  issues_access_level:
    description:
      - V(private) means that accessing issues tab is allowed only to project members.
      - V(disabled) means that accessing issues tab is disabled.
      - V(enabled) means that accessing issues tab is enabled.
      - O(issues_access_level) and O(issues_enabled) are mutually exclusive.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "9.4.0"
  issues_enabled:
    description:
      - Whether you want to create issues or not.
      - O(issues_access_level) and O(issues_enabled) are mutually exclusive.
    type: bool
    default: true
  lfs_enabled:
    description:
      - Enable Git large file systems to manages large files such as audio, video, and graphics files.
    type: bool
    default: false
    version_added: "2.0.0"
  merge_method:
    description:
      - What requirements are placed upon merges.
      - Possible values are V(merge), V(rebase_merge) merge commit with semi-linear history, V(ff) fast-forward merges only.
    type: str
    choices: ["ff", "merge", "rebase_merge"]
    default: merge
    version_added: "1.0.0"
  merge_requests_enabled:
    description:
      - If merge requests can be made or not.
    type: bool
    default: true
  model_registry_access_level:
    description:
      - V(private) means that accessing model registry tab is allowed only to project members.
      - V(disabled) means that accessing model registry tab is disabled.
      - V(enabled) means that accessing model registry tab is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "9.3.0"
  monitor_access_level:
    description:
      - V(private) means that monitoring health is allowed only to project members.
      - V(disabled) means that monitoring health is disabled.
      - V(enabled) means that monitoring health is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  name:
    description:
      - The name of the project.
    required: true
    type: str
  only_allow_merge_if_all_discussions_are_resolved:
    description:
      - All discussions on a merge request (MR) have to be resolved.
    type: bool
    version_added: "3.4.0"
  only_allow_merge_if_pipeline_succeeds:
    description:
      - Only allow merges if pipeline succeeded.
    type: bool
    version_added: "3.4.0"
  packages_enabled:
    description:
      - Enable GitLab package repository.
    type: bool
    version_added: "3.4.0"
  pages_access_level:
    description:
      - V(private) means that accessing pages tab is allowed only to project members.
      - V(disabled) means that accessing pages tab is disabled.
      - V(enabled) means that accessing pages tab is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "9.3.0"
  path:
    description:
      - The path of the project you want to create, this is server_url/O(group)/O(path).
      - If not supplied, O(name) is used.
    type: str
  releases_access_level:
    description:
      - V(private) means that accessing release is allowed only to project members.
      - V(disabled) means that accessing release is disabled.
      - V(enabled) means that accessing release is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  remove_source_branch_after_merge:
    description:
      - Remove the source branch after merge.
    type: bool
    version_added: "3.4.0"
  repository_access_level:
    description:
      - V(private) means that accessing repository is allowed only to project members.
      - V(disabled) means that accessing repository is disabled.
      - V(enabled) means that accessing repository is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "9.3.0"
  security_and_compliance_access_level:
    description:
      - V(private) means that accessing security and complicance tab is allowed only to project members.
      - V(disabled) means that accessing security and complicance tab is disabled.
      - V(enabled) means that accessing security and complicance tab is enabled.
    type: str
    choices: ["private", "disabled", "enabled"]
    version_added: "6.4.0"
  service_desk_enabled:
    description:
      - Enable Service Desk.
    type: bool
    version_added: "9.3.0"
  shared_runners_enabled:
    description:
      - Enable shared runners for this project.
    type: bool
    version_added: "3.7.0"
  snippets_enabled:
    description:
      - If creating snippets should be available or not.
    type: bool
    default: true
  squash_option:
    description:
      - Squash commits when merging.
    type: str
    choices: ["never", "always", "default_off", "default_on"]
    version_added: "3.4.0"
  state:
    description:
      - Create or delete project.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  topics:
    description:
      - A topic or list of topics to be assigned to a project.
      - It is compatible with old GitLab server releases (versions before 14, correspond to C(tag_list)).
    type: list
    elements: str
    version_added: "6.6.0"
  username:
    description:
      - Used to create a personal project under a user's name.
    type: str
    version_added: "3.3.0"
  visibility:
    description:
      - V(private) Project access must be granted explicitly for each user.
      - V(internal) The project can be cloned by any logged in user.
      - V(public) The project can be cloned without any authentication.
    default: private
    type: str
    choices: ["private", "internal", "public"]
    aliases:
      - visibility_level
  wiki_enabled:
    description:
      - If an wiki for this project should be available or not.
    type: bool
    default: true
"""

EXAMPLES = r"""
- name: Create GitLab Project
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    name: my_first_project
    group: "10481470"

- name: Delete GitLab Project
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    name: my_first_project
    state: absent
  delegate_to: localhost

- name: Create GitLab Project in group Ansible
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: my_first_project
    group: ansible
    issues_enabled: false
    merge_method: rebase_merge
    wiki_enabled: true
    snippets_enabled: true
    import_url: http://git.example.com/example/lab.git
    initialize_with_readme: true
    state: present
  delegate_to: localhost

- name: get the initial root password
  ansible.builtin.shell: |
    grep 'Password:' /etc/gitlab/initial_root_password | sed -e 's/Password\: \(.*\)/\1/'
  register: initial_root_password

- name: Create a GitLab Project using a username/password via oauth_token
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    api_username: root
    api_password: "{{ initial_root_password }}"
    name: my_second_project
    group: "10481470"
"""

RETURN = r"""
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

result:
  description: JSON-parsed response from the server.
  returned: always
  type: dict

error:
  description: The error message returned by the GitLab API.
  returned: failed
  type: str
  sample: "400: path is already in use"

project:
  description: API object.
  returned: always
  type: dict
"""


from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec,
    find_group,
    find_project,
    gitlab_authentication,
    gitlab,
)

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


class GitLabProject:
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.project_object = None

    """
    @param project_name Name of the project
    @param namespace Namespace Object (User or Group)
    @param options Options of the project
    """

    def create_or_update_project(self, module, project_name, namespace, options):
        changed = False
        project_options = {
            "allow_merge_on_skipped_pipeline": options["allow_merge_on_skipped_pipeline"],
            "builds_access_level": options["builds_access_level"],
            "build_timeout": options["build_timeout"],
            "ci_config_path": options["ci_config_path"],
            "container_expiration_policy": options["container_expiration_policy"],
            "container_registry_access_level": options["container_registry_access_level"],
            "description": options["description"],
            "environments_access_level": options["environments_access_level"],
            "feature_flags_access_level": options["feature_flags_access_level"],
            "forking_access_level": options["forking_access_level"],
            "infrastructure_access_level": options["infrastructure_access_level"],
            "issues_access_level": options["issues_access_level"],
            "issues_enabled": options["issues_enabled"],
            "lfs_enabled": options["lfs_enabled"],
            "merge_method": options["merge_method"],
            "merge_requests_enabled": options["merge_requests_enabled"],
            "model_registry_access_level": options["model_registry_access_level"],
            "monitor_access_level": options["monitor_access_level"],
            "name": project_name,
            "only_allow_merge_if_all_discussions_are_resolved": options[
                "only_allow_merge_if_all_discussions_are_resolved"
            ],
            "only_allow_merge_if_pipeline_succeeds": options["only_allow_merge_if_pipeline_succeeds"],
            "packages_enabled": options["packages_enabled"],
            "pages_access_level": options["pages_access_level"],
            "releases_access_level": options["releases_access_level"],
            "remove_source_branch_after_merge": options["remove_source_branch_after_merge"],
            "repository_access_level": options["repository_access_level"],
            "security_and_compliance_access_level": options["security_and_compliance_access_level"],
            "service_desk_enabled": options["service_desk_enabled"],
            "shared_runners_enabled": options["shared_runners_enabled"],
            "snippets_enabled": options["snippets_enabled"],
            "squash_option": options["squash_option"],
            "visibility": options["visibility"],
            "wiki_enabled": options["wiki_enabled"],
        }

        # topics was introduced on gitlab >=14 and replace tag_list. We get current gitlab version
        # and check if less than 14. If yes we use tag_list instead topics
        if LooseVersion(self._gitlab.version()[0]) < LooseVersion("14"):
            project_options["tag_list"] = options["topics"]
        else:
            project_options["topics"] = options["topics"]

        # Because we have already call userExists in main()
        if self.project_object is None:
            if options["default_branch"] and not options["initialize_with_readme"]:
                module.fail_json(msg="Param default_branch needs param initialize_with_readme set to true")
            project_options.update(
                {
                    "path": options["path"],
                    "import_url": options["import_url"],
                }
            )
            if options["initialize_with_readme"]:
                project_options["initialize_with_readme"] = options["initialize_with_readme"]
                if options["default_branch"]:
                    project_options["default_branch"] = options["default_branch"]

            project_options = self.get_options_with_value(project_options)
            project = self.create_project(namespace, project_options)

            # add avatar to project
            if options["avatar_path"]:
                try:
                    project.avatar = open(options["avatar_path"], "rb")
                except IOError as e:
                    self._module.fail_json(msg=f"Cannot open {options['avatar_path']}: {e}")

            changed = True
        else:
            if options["default_branch"]:
                project_options["default_branch"] = options["default_branch"]
            changed, project = self.update_project(self.project_object, project_options)

        self.project_object = project
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg=f"Successfully created or updated the project {project_name}")

            try:
                project.save()
            except Exception as e:
                self._module.fail_json(msg=f"Failed to update project: {e} ")
            return True
        return False

    """
    @param namespace Namespace Object (User or Group)
    @param arguments Attributes of the project
    """

    def create_project(self, namespace, arguments):
        if self._module.check_mode:
            return True

        arguments["namespace_id"] = namespace.id
        if "container_expiration_policy" in arguments:
            arguments["container_expiration_policy_attributes"] = arguments["container_expiration_policy"]
        try:
            project = self._gitlab.projects.create(arguments)
        except gitlab.exceptions.GitlabCreateError as e:
            self._module.fail_json(msg=f"Failed to create project: {e} ")

        return project

    """
    @param arguments Attributes of the project
    """

    def get_options_with_value(self, arguments):
        ret_arguments = {k: v for k, v in arguments.items() if v is not None}
        return ret_arguments

    """
    @param project Project Object
    @param arguments Attributes of the project
    """

    def update_project(self, project, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arg_value is not None:
                if getattr(project, arg_key, None) != arg_value:
                    if arg_key == "container_expiration_policy":
                        old_val = getattr(project, arg_key, {})
                        final_val = {key: value for key, value in arg_value.items() if value is not None}

                        if final_val.get("older_than") == "0d":
                            final_val["older_than"] = None
                        if final_val.get("keep_n") == 0:
                            final_val["keep_n"] = None

                        if all(old_val.get(key) == value for key, value in final_val.items()):
                            continue
                        project.container_expiration_policy_attributes = final_val
                    else:
                        setattr(project, arg_key, arg_value)
                    changed = True

        return (changed, project)

    def delete_project(self):
        if self._module.check_mode:
            return True

        project = self.project_object

        return project.delete()

    """
    @param namespace User/Group object
    @param name Name of the project
    """

    def exists_project(self, namespace, path):
        # When project exists, object will be stored in self.project_object.
        project = find_project(self._gitlab, f"{namespace.full_path}/{path}")
        if project:
            self.project_object = project
            return True
        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        dict(
            allow_merge_on_skipped_pipeline=dict(type="bool"),
            avatar_path=dict(type="path"),
            builds_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            build_timeout=dict(type="int"),
            ci_config_path=dict(type="str"),
            container_expiration_policy=dict(
                type="dict",
                options=dict(
                    cadence=dict(type="str", choices=["1d", "7d", "14d", "1month", "3month"]),
                    enabled=dict(type="bool"),
                    keep_n=dict(type="int", choices=[0, 1, 5, 10, 25, 50, 100]),
                    older_than=dict(type="str", choices=["0d", "7d", "14d", "30d", "90d"]),
                    name_regex=dict(type="str"),
                    name_regex_keep=dict(type="str"),
                ),
            ),
            container_registry_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            default_branch=dict(type="str"),
            description=dict(type="str"),
            environments_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            feature_flags_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            forking_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            group=dict(type="str"),
            import_url=dict(type="str"),
            infrastructure_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            initialize_with_readme=dict(type="bool", default=False),
            issues_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            issues_enabled=dict(type="bool", default=True),
            lfs_enabled=dict(default=False, type="bool"),
            merge_method=dict(type="str", default="merge", choices=["merge", "rebase_merge", "ff"]),
            merge_requests_enabled=dict(type="bool", default=True),
            model_registry_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            monitor_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            name=dict(type="str", required=True),
            only_allow_merge_if_all_discussions_are_resolved=dict(type="bool"),
            only_allow_merge_if_pipeline_succeeds=dict(type="bool"),
            packages_enabled=dict(type="bool"),
            pages_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            path=dict(type="str"),
            releases_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            remove_source_branch_after_merge=dict(type="bool"),
            repository_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            security_and_compliance_access_level=dict(type="str", choices=["private", "disabled", "enabled"]),
            service_desk_enabled=dict(type="bool"),
            shared_runners_enabled=dict(type="bool"),
            snippets_enabled=dict(default=True, type="bool"),
            squash_option=dict(type="str", choices=["never", "always", "default_off", "default_on"]),
            state=dict(type="str", default="present", choices=["absent", "present"]),
            topics=dict(type="list", elements="str"),
            username=dict(type="str"),
            visibility=dict(
                type="str", default="private", choices=["internal", "private", "public"], aliases=["visibility_level"]
            ),
            wiki_enabled=dict(type="bool", default=True),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ["api_username", "api_token"],
            ["api_username", "api_oauth_token"],
            ["api_username", "api_job_token"],
            ["api_token", "api_oauth_token"],
            ["api_token", "api_job_token"],
            ["group", "username"],
            ["issues_access_level", "issues_enabled"],
        ],
        required_together=[
            ["api_username", "api_password"],
        ],
        required_one_of=[["api_username", "api_token", "api_oauth_token", "api_job_token"]],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    allow_merge_on_skipped_pipeline = module.params["allow_merge_on_skipped_pipeline"]
    avatar_path = module.params["avatar_path"]
    builds_access_level = module.params["builds_access_level"]
    build_timeout = module.params["build_timeout"]
    ci_config_path = module.params["ci_config_path"]
    container_expiration_policy = module.params["container_expiration_policy"]
    container_registry_access_level = module.params["container_registry_access_level"]
    default_branch = module.params["default_branch"]
    environments_access_level = module.params["environments_access_level"]
    feature_flags_access_level = module.params["feature_flags_access_level"]
    forking_access_level = module.params["forking_access_level"]
    group_identifier = module.params["group"]
    import_url = module.params["import_url"]
    infrastructure_access_level = module.params["infrastructure_access_level"]
    initialize_with_readme = module.params["initialize_with_readme"]
    issues_access_level = module.params["issues_access_level"]
    issues_enabled = module.params["issues_enabled"]
    lfs_enabled = module.params["lfs_enabled"]
    merge_method = module.params["merge_method"]
    merge_requests_enabled = module.params["merge_requests_enabled"]
    model_registry_access_level = module.params["model_registry_access_level"]
    monitor_access_level = module.params["monitor_access_level"]
    only_allow_merge_if_all_discussions_are_resolved = module.params["only_allow_merge_if_all_discussions_are_resolved"]
    only_allow_merge_if_pipeline_succeeds = module.params["only_allow_merge_if_pipeline_succeeds"]
    packages_enabled = module.params["packages_enabled"]
    pages_access_level = module.params["pages_access_level"]
    project_description = module.params["description"]
    project_name = module.params["name"]
    project_path = module.params["path"]
    releases_access_level = module.params["releases_access_level"]
    remove_source_branch_after_merge = module.params["remove_source_branch_after_merge"]
    repository_access_level = module.params["repository_access_level"]
    security_and_compliance_access_level = module.params["security_and_compliance_access_level"]
    service_desk_enabled = module.params["service_desk_enabled"]
    shared_runners_enabled = module.params["shared_runners_enabled"]
    snippets_enabled = module.params["snippets_enabled"]
    squash_option = module.params["squash_option"]
    state = module.params["state"]
    topics = module.params["topics"]
    username = module.params["username"]
    visibility = module.params["visibility"]
    wiki_enabled = module.params["wiki_enabled"]

    # Set project_path to project_name if it is empty.
    if project_path is None:
        project_path = project_name.replace(" ", "_")

    gitlab_project = GitLabProject(module, gitlab_instance)

    namespace = None
    namespace_id = None
    if group_identifier:
        group = find_group(gitlab_instance, group_identifier)
        if group is None:
            module.fail_json(msg=f"Failed to create project: group {group_identifier} doesn't exist")

        namespace_id = group.id
    else:
        if username:
            namespace = gitlab_instance.namespaces.list(search=username, all=False)[0]
        else:
            namespace = gitlab_instance.namespaces.list(search=gitlab_instance.user.username, all=False)[0]
        namespace_id = namespace.id

    if not namespace_id:
        module.fail_json(msg="Failed to find the namespace or group ID which is required to look up the namespace")

    try:
        namespace = gitlab_instance.namespaces.get(namespace_id)
    except gitlab.exceptions.GitlabGetError as e:
        module.fail_json(msg=f"Failed to find the namespace for the given user: {e}")

    if not namespace:
        module.fail_json(msg="Failed to find the namespace for the project")
    project_exists = gitlab_project.exists_project(namespace, project_path)

    if state == "absent":
        if project_exists:
            gitlab_project.delete_project()
            module.exit_json(changed=True, msg=f"Successfully deleted project {project_name}")
        module.exit_json(changed=False, msg="Project deleted or does not exist")

    if state == "present":
        if gitlab_project.create_or_update_project(
            module,
            project_name,
            namespace,
            {
                "allow_merge_on_skipped_pipeline": allow_merge_on_skipped_pipeline,
                "avatar_path": avatar_path,
                "builds_access_level": builds_access_level,
                "build_timeout": build_timeout,
                "ci_config_path": ci_config_path,
                "container_expiration_policy": container_expiration_policy,
                "container_registry_access_level": container_registry_access_level,
                "default_branch": default_branch,
                "description": project_description,
                "environments_access_level": environments_access_level,
                "feature_flags_access_level": feature_flags_access_level,
                "forking_access_level": forking_access_level,
                "import_url": import_url,
                "infrastructure_access_level": infrastructure_access_level,
                "initialize_with_readme": initialize_with_readme,
                "issues_access_level": issues_access_level,
                "issues_enabled": issues_enabled,
                "lfs_enabled": lfs_enabled,
                "merge_method": merge_method,
                "merge_requests_enabled": merge_requests_enabled,
                "model_registry_access_level": model_registry_access_level,
                "monitor_access_level": monitor_access_level,
                "only_allow_merge_if_all_discussions_are_resolved": only_allow_merge_if_all_discussions_are_resolved,
                "only_allow_merge_if_pipeline_succeeds": only_allow_merge_if_pipeline_succeeds,
                "packages_enabled": packages_enabled,
                "pages_access_level": pages_access_level,
                "path": project_path,
                "releases_access_level": releases_access_level,
                "remove_source_branch_after_merge": remove_source_branch_after_merge,
                "repository_access_level": repository_access_level,
                "security_and_compliance_access_level": security_and_compliance_access_level,
                "service_desk_enabled": service_desk_enabled,
                "shared_runners_enabled": shared_runners_enabled,
                "snippets_enabled": snippets_enabled,
                "squash_option": squash_option,
                "topics": topics,
                "visibility": visibility,
                "wiki_enabled": wiki_enabled,
            },
        ):
            module.exit_json(
                changed=True,
                msg=f"Successfully created or updated the project {project_name}",
                project=gitlab_project.project_object._attrs,
            )
        module.exit_json(
            changed=False,
            msg=f"No need to update the project {project_name}",
            project=gitlab_project.project_object._attrs,
        )


if __name__ == "__main__":
    main()
