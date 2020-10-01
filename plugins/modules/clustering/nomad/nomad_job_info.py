#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nomad_job_info
author: FERREIRA Christophe (@chris93111)
version_added: "1.3.0"
short_description: Get Nomad Jobs info
description:
    - Get info for one Nomad job.
    - List Nomad jobs.
requirements:
  - python-nomad
options:
    host:
      description:
        - FQDN of Nomad server.
      required: true
      type: str
    use_ssl:
      description:
        - Use TLS/SSL connection.
      type: bool
      default: true
    timeout:
      description:
        - Timeout (in seconds) for the request to Nomad.
      type: int
      default: 5
    validate_certs:
      description:
        - Enable TLS/SSL certificate validation.
      type: bool
      default: true
    client_cert:
      description:
        - Path of certificate for TLS/SSL.
      type: path
    client_key:
      description:
        - Path of certificate's private key for TLS/SSL.
      type: path
    namespace:
      description:
        - Namespace for Nomad.
      type: str
    token:
      description:
        - ACL token for authentification.
      type: str
    name:
      description:
        - Name of job for Get info.
        - If not specified, lists all jobs.
      type: str
notes:
  - C(check_mode) is supported.
seealso:
  - name: Nomad jobs documentation
    description: Complete documentation for Nomad API jobs.
    link: https://www.nomadproject.io/api-docs/jobs/
'''

EXAMPLES = '''
- name: Get info for job awx
  community.general.nomad_job:
    host: localhost
    name: awx
  register: result

- name: List Nomad jobs
  community.general.nomad_job:
    host: localhost
  register: result

'''


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native

import_nomad = None
try:
    import nomad
    import_nomad = True
except ImportError:
    import_nomad = False


def run():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            use_ssl=dict(type='bool', default=True),
            timeout=dict(type='int', default=5),
            validate_certs=dict(type='bool', default=True),
            client_cert=dict(type='path', default=None),
            client_key=dict(type='path', default=None),
            namespace=dict(type='str', default=None),
            token=dict(type='str', default=None, no_log=True),
            name=dict(type='str', default=None)
        ),
        supports_check_mode=True
    )

    if not import_nomad:
        module.fail_json(msg=missing_required_lib("python-nomad"))

    certificate_ssl = (module.params.get('client_cert'), module.params.get('client_key'))

    nomad_client = nomad.Nomad(
        host=module.params.get('host'),
        secure=module.params.get('use_ssl'),
        timeout=module.params.get('timeout'),
        verify=module.params.get('validate_certs'),
        cert=certificate_ssl,
        namespace=module.params.get('namespace'),
        token=module.params.get('token')
    )

    if module.params.get('name'):

        try:
            result = nomad_client.job.get_job(module.params.get('name'))
            changed = False
        except Exception as e:
            module.fail_json(msg=to_native(e))
    else:

        try:
            result = nomad_client.jobs.get_jobs()
            changed = False
        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, result=result)


def main():

    run()


if __name__ == "__main__":
    main()
