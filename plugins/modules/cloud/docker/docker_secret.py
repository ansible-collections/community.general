#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: docker_secret

short_description: Manage docker secrets.


description:
     - Create and remove Docker secrets in a Swarm environment. Similar to C(docker secret create) and C(docker secret rm).
     - Adds to the metadata of new secrets 'ansible_key', an encrypted hash representation of the data, which is then used
       in future runs to test if a secret has changed. If 'ansible_key is not present, then a secret will not be updated
       unless the I(force) option is set.
     - Updates to secrets are performed by removing the secret and creating it again.
options:
  data:
    description:
      - The value of the secret. Required when state is C(present).
    type: str
  data_is_b64:
    description:
      - If set to C(true), the data is assumed to be Base64 encoded and will be
        decoded before being used.
      - To use binary I(data), it is better to keep it Base64 encoded and let it
        be decoded by this option.
    type: bool
    default: no
  labels:
    description:
      - "A map of key:value meta data, where both key and value are expected to be strings."
      - If new meta data is provided, or existing meta data is modified, the secret will be updated by removing it and creating it again.
    type: dict
  force:
    description:
      - Use with state C(present) to always remove and recreate an existing secret.
      - If C(true), an existing secret will be replaced, even if it has not changed.
    type: bool
    default: no
  name:
    description:
      - The name of the secret.
    type: str
    required: yes
  state:
    description:
      - Set to C(present), if the secret should exist, and C(absent), if it should not.
    type: str
    default: present
    choices:
      - absent
      - present

extends_documentation_fragment:
- community.general.docker
- community.general.docker.docker_py_2_documentation


requirements:
  - "L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 2.1.0"
  - "Docker API >= 1.25"

author:
  - Chris Houseknecht (@chouseknecht)
'''

EXAMPLES = '''

- name: Create secret foo (from a file on the control machine)
  community.general.docker_secret:
    name: foo
    # If the file is JSON or binary, Ansible might modify it (because
    # it is first decoded and later re-encoded). Base64-encoding the
    # file directly after reading it prevents this to happen.
    data: "{{ lookup('file', '/path/to/secret/file') | b64encode }}"
    data_is_b64: true
    state: present

- name: Change the secret data
  community.general.docker_secret:
    name: foo
    data: Goodnight everyone!
    labels:
      bar: baz
      one: '1'
    state: present

- name: Add a new label
  community.general.docker_secret:
    name: foo
    data: Goodnight everyone!
    labels:
      bar: baz
      one: '1'
      # Adding a new label will cause a remove/create of the secret
      two: '2'
    state: present

- name: No change
  community.general.docker_secret:
    name: foo
    data: Goodnight everyone!
    labels:
      bar: baz
      one: '1'
      # Even though 'two' is missing, there is no change to the existing secret
    state: present

- name: Update an existing label
  community.general.docker_secret:
    name: foo
    data: Goodnight everyone!
    labels:
      bar: monkey   # Changing a label will cause a remove/create of the secret
      one: '1'
    state: present

- name: Force the removal/creation of the secret
  community.general.docker_secret:
    name: foo
    data: Goodnight everyone!
    force: yes
    state: present

- name: Remove secret foo
  community.general.docker_secret:
    name: foo
    state: absent
'''

RETURN = '''
secret_id:
  description:
    - The ID assigned by Docker to the secret object.
  returned: success and I(state) is C(present)
  type: str
  sample: 'hzehrmyjigmcp2gb6nlhmjqcv'
'''

import base64
import hashlib
import traceback

try:
    from docker.errors import DockerException, APIError
except ImportError:
    # missing Docker SDK for Python handled in ansible.module_utils.docker.common
    pass

from ansible_collections.community.general.plugins.module_utils.docker.common import (
    AnsibleDockerClient,
    DockerBaseClass,
    compare_generic,
    RequestException,
)
from ansible.module_utils._text import to_native, to_bytes


class SecretManager(DockerBaseClass):

    def __init__(self, client, results):

        super(SecretManager, self).__init__()

        self.client = client
        self.results = results
        self.check_mode = self.client.check_mode

        parameters = self.client.module.params
        self.name = parameters.get('name')
        self.state = parameters.get('state')
        self.data = parameters.get('data')
        if self.data is not None:
            if parameters.get('data_is_b64'):
                self.data = base64.b64decode(self.data)
            else:
                self.data = to_bytes(self.data)
        self.labels = parameters.get('labels')
        self.force = parameters.get('force')
        self.data_key = None

    def __call__(self):
        if self.state == 'present':
            self.data_key = hashlib.sha224(self.data).hexdigest()
            self.present()
        elif self.state == 'absent':
            self.absent()

    def get_secret(self):
        ''' Find an existing secret. '''
        try:
            secrets = self.client.secrets(filters={'name': self.name})
        except APIError as exc:
            self.client.fail("Error accessing secret %s: %s" % (self.name, to_native(exc)))

        for secret in secrets:
            if secret['Spec']['Name'] == self.name:
                return secret
        return None

    def create_secret(self):
        ''' Create a new secret '''
        secret_id = None
        # We can't see the data after creation, so adding a label we can use for idempotency check
        labels = {
            'ansible_key': self.data_key
        }
        if self.labels:
            labels.update(self.labels)

        try:
            if not self.check_mode:
                secret_id = self.client.create_secret(self.name, self.data, labels=labels)
        except APIError as exc:
            self.client.fail("Error creating secret: %s" % to_native(exc))

        if isinstance(secret_id, dict):
            secret_id = secret_id['ID']

        return secret_id

    def present(self):
        ''' Handles state == 'present', creating or updating the secret '''
        secret = self.get_secret()
        if secret:
            self.results['secret_id'] = secret['ID']
            data_changed = False
            attrs = secret.get('Spec', {})
            if attrs.get('Labels', {}).get('ansible_key'):
                if attrs['Labels']['ansible_key'] != self.data_key:
                    data_changed = True
            labels_changed = not compare_generic(self.labels, attrs.get('Labels'), 'allow_more_present', 'dict')
            if data_changed or labels_changed or self.force:
                # if something changed or force, delete and re-create the secret
                self.absent()
                secret_id = self.create_secret()
                self.results['changed'] = True
                self.results['secret_id'] = secret_id
        else:
            self.results['changed'] = True
            self.results['secret_id'] = self.create_secret()

    def absent(self):
        ''' Handles state == 'absent', removing the secret '''
        secret = self.get_secret()
        if secret:
            try:
                if not self.check_mode:
                    self.client.remove_secret(secret['ID'])
            except APIError as exc:
                self.client.fail("Error removing secret %s: %s" % (self.name, to_native(exc)))
            self.results['changed'] = True


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        data=dict(type='str', no_log=True),
        data_is_b64=dict(type='bool', default=False),
        labels=dict(type='dict'),
        force=dict(type='bool', default=False)
    )

    required_if = [
        ('state', 'present', ['data'])
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
        min_docker_version='2.1.0',
        min_docker_api_version='1.25',
    )

    try:
        results = dict(
            changed=False,
            secret_id=''
        )

        SecretManager(client, results)()
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
