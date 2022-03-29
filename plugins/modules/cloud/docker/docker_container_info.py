#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: docker_container_info

short_description: Retrieves facts about docker container

description:
  - Retrieves facts about a docker container.
  - Essentially returns the output of C(docker inspect <name>), similar to what M(community.general.docker_container)
    returns for a non-absent container.


options:
  name:
    description:
      - The name of the container to inspect.
      - When identifying an existing container name may be a name or a long or short container ID.
    type: str
    required: yes
extends_documentation_fragment:
- community.general.docker
- community.general.docker.docker_py_1_documentation


author:
  - "Felix Fontein (@felixfontein)"

requirements:
  - "L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 1.8.0 (use L(docker-py,https://pypi.org/project/docker-py/) for Python 2.6)"
  - "Docker API >= 1.20"
'''

EXAMPLES = '''
- name: Get infos on container
  community.general.docker_container_info:
    name: mydata
  register: result

- name: Does container exist?
  ansible.builtin.debug:
    msg: "The container {{ 'exists' if result.exists else 'does not exist' }}"

- name: Print information about container
  ansible.builtin.debug:
    var: result.container
  when: result.exists
'''

RETURN = '''
exists:
    description:
      - Returns whether the container exists.
    type: bool
    returned: always
    sample: true
container:
    description:
      - Facts representing the current state of the container. Matches the docker inspection output.
      - Will be C(none) if container does not exist.
    returned: always
    type: dict
    sample: '{
        "AppArmorProfile": "",
        "Args": [],
        "Config": {
            "AttachStderr": false,
            "AttachStdin": false,
            "AttachStdout": false,
            "Cmd": [
                "/usr/bin/supervisord"
            ],
            "Domainname": "",
            "Entrypoint": null,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            ],
            "ExposedPorts": {
                "443/tcp": {},
                "80/tcp": {}
            },
            "Hostname": "8e47bf643eb9",
            "Image": "lnmp_nginx:v1",
            "Labels": {},
            "OnBuild": null,
            "OpenStdin": false,
            "StdinOnce": false,
            "Tty": false,
            "User": "",
            "Volumes": {
                "/tmp/lnmp/nginx-sites/logs/": {}
            },
            ...
    }'
'''

import traceback

try:
    from docker.errors import DockerException
except ImportError:
    # missing Docker SDK for Python handled in ansible.module_utils.docker.common
    pass

from ansible_collections.community.general.plugins.module_utils.docker.common import (
    AnsibleDockerClient,
    RequestException,
)


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )

    try:
        container = client.get_container(client.module.params['name'])

        client.module.exit_json(
            changed=False,
            exists=(True if container else False),
            container=container,
        )
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
