#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: docker_image_info

short_description: Inspect docker images


description:
     - Provide one or more image names, and the module will inspect each, returning an array of inspection results.
     - If an image does not exist locally, it will not appear in the results. If you want to check whether an image exists
       locally, you can call the module with the image name, then check whether the result list is empty (image does not
       exist) or has one element (the image exists locally).
     - The module will not attempt to pull images from registries. Use M(community.general.docker_image) with I(source) set to C(pull)
       to ensure an image is pulled.

notes:
     - This module was called C(docker_image_facts) before Ansible 2.8. The usage did not change.

options:
  name:
    description:
      - An image name or a list of image names. Name format will be C(name[:tag]) or C(repository/name[:tag]),
        where C(tag) is optional. If a tag is not provided, C(latest) will be used. Instead of image names, also
        image IDs can be used.
      - If no name is provided, a list of all images will be returned.
    type: list
    elements: str

extends_documentation_fragment:
- community.general.docker
- community.general.docker.docker_py_1_documentation


requirements:
  - "L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 1.8.0 (use L(docker-py,https://pypi.org/project/docker-py/) for Python 2.6)"
  - "Docker API >= 1.20"

author:
  - Chris Houseknecht (@chouseknecht)

'''

EXAMPLES = '''
- name: Inspect a single image
  community.general.docker_image_info:
    name: pacur/centos-7

- name: Inspect multiple images
  community.general.docker_image_info:
    name:
      - pacur/centos-7
      - sinatra
  register: result

- name: Make sure that both images pacur/centos-7 and sinatra exist locally
  ansible.builtin.assert:
    that:
      - result.images | length == 2
'''

RETURN = '''
images:
    description:
      - Inspection results for the selected images.
      - The list only contains inspection results of images existing locally.
    returned: always
    type: list
    elements: dict
    sample: [
        {
            "Architecture": "amd64",
            "Author": "",
            "Comment": "",
            "Config": {
                "AttachStderr": false,
                "AttachStdin": false,
                "AttachStdout": false,
                "Cmd": [
                    "/etc/docker/registry/config.yml"
                ],
                "Domainname": "",
                "Entrypoint": [
                    "/bin/registry"
                ],
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ],
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Hostname": "e5c68db50333",
                "Image": "c72dce2618dc8f7b794d2b2c2b1e64e0205ead5befc294f8111da23bd6a2c799",
                "Labels": {},
                "OnBuild": [],
                "OpenStdin": false,
                "StdinOnce": false,
                "Tty": false,
                "User": "",
                "Volumes": {
                    "/var/lib/registry": {}
                },
                "WorkingDir": ""
            },
            "Container": "e83a452b8fb89d78a25a6739457050131ca5c863629a47639530d9ad2008d610",
            "ContainerConfig": {
                "AttachStderr": false,
                "AttachStdin": false,
                "AttachStdout": false,
                "Cmd": [
                    "/bin/sh",
                    "-c",
                    '#(nop) CMD ["/etc/docker/registry/config.yml"]'
                ],
                "Domainname": "",
                "Entrypoint": [
                    "/bin/registry"
                ],
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ],
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Hostname": "e5c68db50333",
                "Image": "c72dce2618dc8f7b794d2b2c2b1e64e0205ead5befc294f8111da23bd6a2c799",
                "Labels": {},
                "OnBuild": [],
                "OpenStdin": false,
                "StdinOnce": false,
                "Tty": false,
                "User": "",
                "Volumes": {
                    "/var/lib/registry": {}
                },
                "WorkingDir": ""
            },
            "Created": "2016-03-08T21:08:15.399680378Z",
            "DockerVersion": "1.9.1",
            "GraphDriver": {
                "Data": null,
                "Name": "aufs"
            },
            "Id": "53773d8552f07b730f3e19979e32499519807d67b344141d965463a950a66e08",
            "Name": "registry:2",
            "Os": "linux",
            "Parent": "f0b1f729f784b755e7bf9c8c2e65d8a0a35a533769c2588f02895f6781ac0805",
            "RepoDigests": [],
            "RepoTags": [
                "registry:2"
            ],
            "Size": 0,
            "VirtualSize": 165808884
        }
    ]
'''

import traceback

try:
    from docker import utils
    from docker.errors import DockerException
except ImportError:
    # missing Docker SDK for Python handled in ansible.module_utils.docker.common
    pass

from ansible_collections.community.general.plugins.module_utils.docker.common import (
    AnsibleDockerClient,
    DockerBaseClass,
    is_image_name_id,
    RequestException,
)


class ImageManager(DockerBaseClass):

    def __init__(self, client, results):

        super(ImageManager, self).__init__()

        self.client = client
        self.results = results
        self.name = self.client.module.params.get('name')
        self.log("Gathering facts for images: %s" % (str(self.name)))

        if self.name:
            self.results['images'] = self.get_facts()
        else:
            self.results['images'] = self.get_all_images()

    def fail(self, msg):
        self.client.fail(msg)

    def get_facts(self):
        '''
        Lookup and inspect each image name found in the names parameter.

        :returns array of image dictionaries
        '''

        results = []

        names = self.name
        if not isinstance(names, list):
            names = [names]

        for name in names:
            if is_image_name_id(name):
                self.log('Fetching image %s (ID)' % (name))
                image = self.client.find_image_by_id(name)
            else:
                repository, tag = utils.parse_repository_tag(name)
                if not tag:
                    tag = 'latest'
                self.log('Fetching image %s:%s' % (repository, tag))
                image = self.client.find_image(name=repository, tag=tag)
            if image:
                results.append(image)
        return results

    def get_all_images(self):
        results = []
        images = self.client.images()
        for image in images:
            try:
                inspection = self.client.inspect_image(image['Id'])
            except Exception as exc:
                self.fail("Error inspecting image %s - %s" % (image['Id'], str(exc)))
            results.append(inspection)
        return results


def main():
    argument_spec = dict(
        name=dict(type='list', elements='str'),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )
    if client.module._name in ('docker_image_facts', 'community.general.docker_image_facts'):
        client.module.deprecate("The 'docker_image_facts' module has been renamed to 'docker_image_info'",
                                version='2.0.0', collection_name='community.general')  # was Ansible 2.12

    try:
        results = dict(
            changed=False,
            images=[]
        )

        ImageManager(client, results)
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
