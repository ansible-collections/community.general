#!/usr/bin/python
#
# (c) 2020 Matt Clay <mclay@redhat.com>
# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This module properly lives in community.docker; it has been vendored here
# to support the 1.x.y docker integration tests.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: current_container_facts
short_description: Return facts about whether the module runs in a Docker container
description:
  - Return facts about whether the module runs in a Docker container.
author:
  - Felix Fontein (@felixfontein)
'''

EXAMPLES = '''
- name: Get facts on current container
  community.docker.current_container_facts:
- name: Print information on current container when running in a container
  ansible.builtin.debug:
    msg: "Container ID is {{ ansible_module_container_id }}"
  when: ansible_module_running_in_container
'''

RETURN = '''
ansible_facts:
    description: Ansible facts returned by the module
    type: dict
    returned: always
    contains:
        ansible_module_running_in_container:
            description:
              - Whether the module was able to detect that it runs in a container or not.
            returned: always
            type: bool
        ansible_module_container_id:
            description:
              - The detected container ID.
              - Contains an empty string if no container was detected.
            returned: always
            type: str
        ansible_module_container_type:
            description:
              - The detected container environment.
              - Contains an empty string if no container was detected.
              - Otherwise, will be one of C(docker) or C(azure_pipelines).
            returned: always
            type: str
            # choices:
            #   - docker
            #   - azure_pipelines
'''

import os

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(dict(), supports_check_mode=True)

    path = '/proc/self/cpuset'
    container_id = ''
    container_type = ''

    if os.path.exists(path):
        # File content varies based on the environment:
        #   No Container: /
        #   Docker: /docker/c86f3732b5ba3d28bb83b6e14af767ab96abbc52de31313dcb1176a62d91a507
        #   Azure Pipelines (Docker): /azpl_job/0f2edfed602dd6ec9f2e42c867f4d5ee640ebf4c058e6d3196d4393bb8fd0891
        #   Podman: /../../../../../..
        with open(path, 'rb') as f:
            contents = f.read().decode('utf-8')

        cgroup_path, cgroup_name = os.path.split(contents.strip())

        if cgroup_path == '/docker':
            container_id = cgroup_name
            container_type = 'docker'

        if cgroup_path == '/azpl_job':
            container_id = cgroup_name
            container_type = 'azure_pipelines'

    module.exit_json(ansible_facts=dict(
        ansible_module_running_in_container=container_id != '',
        ansible_module_container_id=container_id,
        ansible_module_container_type=container_type,
    ))


if __name__ == '__main__':
    main()
