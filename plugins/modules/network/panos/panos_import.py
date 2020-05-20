#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage PaloAltoNetworks Firewall
# (c) 2016, techbizdev <techbizdev@paloaltonetworks.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: panos_import
short_description: import file on PAN-OS devices
description:
    - Import file on PAN-OS device
notes:
    - API reference documentation can be read from the C(/api/) directory of your appliance
    - Certificate validation is enabled by default as of Ansible 2.6. This may break existing playbooks but should be disabled with caution.
author: "Luigi Mori (@jtschichold), Ivan Bojer (@ivanbojer)"
requirements:
    - pan-python
    - requests
    - requests_toolbelt
deprecated:
    alternative: Use U(https://galaxy.ansible.com/PaloAltoNetworks/paloaltonetworks) instead.
    removed_in: "2.12"
    why: Consolidating code base.
options:
    category:
        description:
            - Category of file uploaded. The default is software.
            - See API > Import section of the API reference for category options.
        default: software
    file:
        description:
            - Location of the file to import into device.
    url:
        description:
            - URL of the file that will be imported to device.
    validate_certs:
        description:
            - If C(no), SSL certificates will not be validated. Disabling certificate validation is not recommended.
        default: yes
        type: bool
extends_documentation_fragment:
- community.general.panos

'''

EXAMPLES = '''
# import software image PanOS_vm-6.1.1 on 192.168.1.1
- name: import software image into PAN-OS
  panos_import:
    ip_address: 192.168.1.1
    username: admin
    password: admin
    file: /tmp/PanOS_vm-6.1.1
    category: software
'''

RETURN = '''
# Default return values
'''

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['deprecated'],
                    'supported_by': 'community'}


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

import os.path
import xml.etree
import tempfile
import shutil
import os

try:
    import pan.xapi
    import requests
    import requests_toolbelt
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def import_file(xapi, module, ip_address, file_, category):
    xapi.keygen()

    params = {
        'type': 'import',
        'category': category,
        'key': xapi.api_key
    }

    filename = os.path.basename(file_)

    mef = requests_toolbelt.MultipartEncoder(
        fields={
            'file': (filename, open(file_, 'rb'), 'application/octet-stream')
        }
    )

    r = requests.post(
        'https://' + ip_address + '/api/',
        verify=module.params['validate_certs'],
        params=params,
        headers={'Content-Type': mef.content_type},
        data=mef
    )

    # if something goes wrong just raise an exception
    r.raise_for_status()

    resp = xml.etree.ElementTree.fromstring(r.content)

    if resp.attrib['status'] == 'error':
        module.fail_json(msg=r.content)

    return True, filename


def download_file(url):
    r = requests.get(url, stream=True)
    fo = tempfile.NamedTemporaryFile(prefix='ai', delete=False)
    shutil.copyfileobj(r.raw, fo)
    fo.close()

    return fo.name


def delete_file(path):
    os.remove(path)


def main():
    argument_spec = dict(
        ip_address=dict(required=True),
        password=dict(required=True, no_log=True),
        username=dict(default='admin'),
        category=dict(default='software'),
        file=dict(),
        url=dict(),
        validate_certs=dict(type='bool', default=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False, required_one_of=[['file', 'url']])
    if not HAS_LIB:
        module.fail_json(msg='pan-python, requests, and requests_toolbelt are required for this module')

    ip_address = module.params["ip_address"]
    password = module.params["password"]
    username = module.params['username']

    xapi = pan.xapi.PanXapi(
        hostname=ip_address,
        api_username=username,
        api_password=password
    )

    file_ = module.params['file']
    url = module.params['url']

    category = module.params['category']

    # we can get file from URL or local storage
    if url is not None:
        file_ = download_file(url)

    try:
        changed, filename = import_file(xapi, module, ip_address, file_, category)
    except Exception as exc:
        module.fail_json(msg=to_native(exc))

    # cleanup and delete file if local
    if url is not None:
        delete_file(file_)

    module.exit_json(changed=changed, filename=filename, msg="okey dokey")


if __name__ == '__main__':
    main()
