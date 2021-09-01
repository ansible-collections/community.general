#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max-Florian Bidlingmaier (Max-Florian.Bidlingmaier@sap.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from os import truncate
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gitlab_project_mirror
short_description: Creates/updates/deletes GitLab Project Remote Mirror
description:
  - When the remote mirror does not exist for the project, it will be created.
  - When changes are made to the remote mirror, the mirror will be updated.
  - Gitlab API does not allow to delete a remote mirror as of July 2021. There is an request upstream
    (https://gitlab.com/gitlab-org/gitlab/-/issues/287786)
  - Gitlab API does not allow to change (parts) of the URL. As credentials are part of it they can not be checked/changed,
    this limits idempotency.
author:
  - Max-Florian Bidlingmaier (@suukit) Max-Florian.Bidlingmaier@sap.com

requirements:
  - python >= 2.7
  - python-gitlab python module
extends_documentation_fragment:
- community.general.auth_basic

options:
    api_token:
        description:
            - GitLab token for logging in.
      type: str
    validate_certs:
        description:
            - Whether or not to validate TLS/SSL certificates when supplying a HTTPS endpoint.
            - Should only be set to C(false) if you can guarantee that you are talking to the correct server
              and no man-in-the-middle attack can happen.
        default: true
        type: bool
    api_username:
        description:
            - The username to use for authentication against the API.
        type: str
    api_password:
        description:
            - The password to use for authentication against the API.
        type: str
    project:
        description:
            - The name of the project.
        required: true
        type: str
    enabled:
        description:
            - Is this remote mirror currently enabled?
        type: bool
        default: true
    url:
        description:
            - URL to the git repo to mirror to in the form https://<user>:<token>@<fqdn>/<path>/<to>/<repo>.git.
        type: str
        required: true
    only_protected_branches:
        description:
            - Mirror only protected or all branches?
        type: bool
    keep_divergent_refs:
        description:
            - Should divergent refs beeing kept?
        type: bool
    state:
        description:
            - Create/update mirror
            - Due to not beeing able to check the secrets one have to recreate and deactivate on secrets change.
            - Possible values are present and absent.
        default: present
        type: str
        choices: ["present", "absent"]
'''

EXAMPLES = r'''
- name: Create Mirror for Project
  community.general.gitlab_project_mirror:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    name: a project
    url: "https://gituser:gittoken@gitserver.example.com/somerepo.git"
    enabled: true
'''

RETURN = r'''
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

error:
  description: the error message returned by the GitLab API.
  returned: failed
  type: str
  sample: "400: path is already in use"
'''

import traceback

GITLAB_IMP_ERR = None
try:
    import gitlab
    HAS_GITLAB_PACKAGE = True
except Exception:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import findGroup, findProject, gitlabAuthentication


class GitLabProjectMirror(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.projectObject = None

    '''
    @param mirror_url URL to where the mirror should point to
    @param mirror_enabled Is this mirror enabled?
    @param mirror_keep_divergent_refs Keep divergent refs?
    @param mirror_only_protected_branches Mirror only protected banches?
    '''
    def createOrUpdateMirror(self, mirror_url, mirror_enabled, mirror_keep_divergent_refs = None, mirror_only_protected_branches = None):
        changed = False
        mirror_exists = False
        mirrors = self.projectObject.remote_mirrors.list()
        if '@' in mirror_url:
            urlParts = mirror_url.split('@')
        else:
            urlParts = mirror_url.split('//')

        for mirror in mirrors:
            if urlParts[1] in mirror.url:
                mirror_exists = True
                save_mirror = False
                # mirror exists, update if needed
                if mirror.enabled != mirror_enabled:
                    mirror.enabled = mirror_enabled
                    save_mirror = True
                if mirror_keep_divergent_refs != None and mirror.keep_divergent_refs != mirror_keep_divergent_refs:
                    mirror.keep_divergent_refs = mirror_keep_divergent_refs
                    save_mirror = True
                if mirror_only_protected_branches != None and mirror.only_protected_branches != mirror_only_protected_branches:
                    mirror.only_protected_branches = mirror_only_protected_branches
                    save_mirror = True

                if save_mirror:
                    changed = True
                    if self._module.check_mode:
                        self._module.exit_json(changed=True, msg="Successfully updated the project remote mirror %s" % mirror_url)
                    try:
                        mirror.save()
                    except Exception as e:
                        self._module.fail_json(msg="Failed to update remote mirror: %s " % e)

        # create a new mirror
        if not mirror_exists:
            create_data = {'url' : mirror_url,
                           'enabled': mirror_enabled}
            if mirror_keep_divergent_refs is not None:
              create_data['keep_divergent_refs'] = mirror_keep_divergent_refs
            if mirror_only_protected_branches is not None:
              create_data['only_protected_branches'] = mirror_only_protected_branches

            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully updated the project remote mirror %s" % mirror_url)
            try:
                mirror = self.projectObject.remote_mirrors.create(create_data)
            except Exception as e:
                self._module.fail_json(msg="Failed to create remote mirror: %s " % e)

            changed = True

        return changed

    '''
    @param path Name/path of the project
    '''
    def existsProject(self, path):
        # When project exists, object will be stored in self.projectObject.
        project = findProject(self._gitlab, path)
        if project:
            self.projectObject = project
            return True
        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_token=dict(type='str', no_log=True),
        project=dict(type='str', required=True),
        url=dict(type='str', required=True),
        enabled=dict(type='bool'),
        only_protected_branches=dict(type='bool'),
        keep_divergent_refs=dict(type='bool'),
        state=dict(type='str', default="present", choices=["present","absent"]),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_password', 'api_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token']
        ],
        supports_check_mode=True,
    )

    project_name = module.params['project']
    state = module.params['state']
    mirror_url = module.params['url']
    mirror_enabled = module.params['enabled']
    mirror_only_protected_branches = module.params['only_protected_branches']
    mirror_keep_divergent_refs = module.params['keep_divergent_refs']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)

    gitlab_project = GitLabProjectMirror(module, gitlab_instance)

    project_exists = gitlab_project.existsProject(project_name)

    if project_exists:
      if state == 'present':
          if gitlab_project.createOrUpdateMirror(mirror_url, mirror_enabled, mirror_keep_divergent_refs, mirror_only_protected_branches):
              module.exit_json(changed=True, msg="Successfully created or updated the remote mirror to %s" % project_name, project=gitlab_project.projectObject._attrs)
          else:
              module.exit_json(changed=False, msg="No need to update/create the remote mirror to %s" % project_name, project=gitlab_project.projectObject._attrs)
      elif state == 'absent':
          # as GitLab API does currently not support removing remote mirrors return error to user
          module.fail_json(msg="GitLab API does not support removing mirrors. Either do it manually using GUI or update mirror with enabled=false.")

if __name__ == '__main__':
    main()
