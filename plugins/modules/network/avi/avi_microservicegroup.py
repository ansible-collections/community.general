#!/usr/bin/python
#
# @author: Gaurav Rastogi (grastogi@avinetworks.com)
#          Eric Anderson (eanderson@avinetworks.com)
# module_check: supported
#
# Copyright: (c) 2017 Gaurav Rastogi, <grastogi@avinetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: avi_microservicegroup
author: Gaurav Rastogi (@grastogi23) <grastogi@avinetworks.com>

short_description: Module for setup of MicroServiceGroup Avi RESTful Object
description:
    - This module is used to configure MicroServiceGroup object
    - more examples at U(https://github.com/avinetworks/devops)
requirements: [ avisdk ]
options:
    state:
        description:
            - The state that should be applied on the entity.
        default: present
        choices: ["absent", "present"]
    avi_api_update_method:
        description:
            - Default method for object update is HTTP PUT.
            - Setting to patch will override that behavior to use HTTP PATCH.
        default: put
        choices: ["put", "patch"]
    avi_api_patch_op:
        description:
            - Patch operation to use when using avi_api_update_method as patch.
        choices: ["add", "replace", "delete"]
    created_by:
        description:
            - Creator name.
    description:
        description:
            - User defined description for the object.
    name:
        description:
            - Name of the microservice group.
        required: true
    service_refs:
        description:
            - Configure microservice(es).
            - It is a reference to an object of type microservice.
    tenant_ref:
        description:
            - It is a reference to an object of type tenant.
    url:
        description:
            - Avi controller URL of the object.
    uuid:
        description:
            - Uuid of the microservice group.
extends_documentation_fragment:
- community.general.avi

'''

EXAMPLES = """
  - name: Create a Microservice Group that can be used for setting up Network security policy
    avi_microservicegroup:
      controller: '{{ controller }}'
      username: '{{ username }}'
      password: '{{ password }}'
      description: Group created by my Secure My App UI.
      name: vs-msg-marketing
      tenant_ref: admin
"""

RETURN = '''
obj:
    description: MicroServiceGroup (api/microservicegroup) object
    returned: success, changed
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from ansible_collections.community.general.plugins.module_utils.network.avi.avi import (
        avi_common_argument_spec, avi_ansible_api, HAS_AVI)
except ImportError:
    HAS_AVI = False


def main():
    argument_specs = dict(
        state=dict(default='present',
                   choices=['absent', 'present']),
        avi_api_update_method=dict(default='put',
                                   choices=['put', 'patch']),
        avi_api_patch_op=dict(choices=['add', 'replace', 'delete']),
        created_by=dict(type='str',),
        description=dict(type='str',),
        name=dict(type='str', required=True),
        service_refs=dict(type='list',),
        tenant_ref=dict(type='str',),
        url=dict(type='str',),
        uuid=dict(type='str',),
    )
    argument_specs.update(avi_common_argument_spec())
    module = AnsibleModule(
        argument_spec=argument_specs, supports_check_mode=True)
    if not HAS_AVI:
        return module.fail_json(msg=(
            'Avi python API SDK (avisdk>=17.1) or requests is not installed. '
            'For more details visit https://github.com/avinetworks/sdk.'))
    return avi_ansible_api(module, 'microservicegroup',
                           set([]))


if __name__ == '__main__':
    main()
