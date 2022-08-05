#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_otptoken
author: justchris1 (@justchris1)
short_description: Manage FreeIPA OTPs
version_added: 2.5.0
description:
- Add, modify, and delete One Time Passwords in IPA.
options:
  uniqueid:
    description: Unique ID of the token in IPA.
    required: true
    aliases: ["name"]
    type: str
  newuniqueid:
    description: If specified, the unique id specified will be changed to this.
    type: str
  otptype:
    description:
    - Type of OTP.
    - "B(Note:) Cannot be modified after OTP is created."
    type: str
    choices: [ totp, hotp ]
  secretkey:
    description:
    - Token secret (Base64).
    - If OTP is created and this is not specified, a random secret will be generated by IPA.
    - "B(Note:) Cannot be modified after OTP is created."
    type: str
  description:
    description: Description of the token (informational only).
    type: str
  owner:
    description:  Assigned user of the token.
    type: str
  enabled:
    description: Mark the token as enabled (default C(true)).
    default: true
    type: bool
  notbefore:
    description:
    - First date/time the token can be used.
    - In the format C(YYYYMMddHHmmss).
    - For example, C(20180121182022) will allow the token to be used starting on 21 January 2018 at 18:20:22.
    type: str
  notafter:
    description:
    - Last date/time the token can be used.
    - In the format C(YYYYMMddHHmmss).
    - For example, C(20200121182022) will allow the token to be used until 21 January 2020 at 18:20:22.
    type: str
  vendor:
    description: Token vendor name (informational only).
    type: str
  model:
    description: Token model (informational only).
    type: str
  serial:
    description: Token serial (informational only).
    type: str
  state:
    description: State to ensure.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  algorithm:
    description:
    - Token hash algorithm.
    - "B(Note:) Cannot be modified after OTP is created."
    choices: ['sha1', 'sha256', 'sha384', 'sha512']
    type: str
  digits:
    description:
    - Number of digits each token code will have.
    - "B(Note:) Cannot be modified after OTP is created."
    choices: [ 6, 8 ]
    type: int
  offset:
    description:
    - TOTP token / IPA server time difference.
    - "B(Note:) Cannot be modified after OTP is created."
    type: int
  interval:
    description:
    - Length of TOTP token code validity in seconds.
    - "B(Note:) Cannot be modified after OTP is created."
    type: int
  counter:
    description:
    - Initial counter for the HOTP token.
    - "B(Note:) Cannot be modified after OTP is created."
    type: int
extends_documentation_fragment:
- community.general.ipa.documentation
'''

EXAMPLES = r'''
- name: Create a totp for pinky, allowing the IPA server to generate using defaults
  community.general.ipa_otptoken:
    uniqueid: Token123
    otptype: totp
    owner: pinky
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Create a 8 digit hotp for pinky with sha256 with specified validity times
  community.general.ipa_otptoken:
    uniqueid: Token123
    enabled: true
    otptype: hotp
    digits: 8
    secretkey: UMKSIER00zT2T2tWMUlTRmNlekRCbFQvWFBVZUh2dElHWGR6T3VUR3IzK2xjaFk9
    algorithm: sha256
    notbefore: 20180121182123
    notafter: 20220121182123
    owner: pinky
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Update Token123 to indicate a vendor, model, serial number (info only), and description
  community.general.ipa_otptoken:
    uniqueid: Token123
    vendor: Acme
    model: acme101
    serial: SerialNumber1
    description: Acme OTP device
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Disable Token123
  community.general.ipa_otptoken:
    uniqueid: Token123
    enabled: false
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Rename Token123 to TokenABC and enable it
  community.general.ipa_otptoken:
    uniqueid: Token123
    newuniqueid: TokenABC
    enabled: true
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
'''

RETURN = r'''
otptoken:
  description: OTP Token as returned by IPA API
  returned: always
  type: dict
'''

import base64
import traceback

from ansible.module_utils.basic import AnsibleModule, sanitize_keys
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class OTPTokenIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(OTPTokenIPAClient, self).__init__(module, host, port, protocol)

    def otptoken_find(self, name):
        return self._post_json(method='otptoken_find', name=None, item={'all': True,
                                                                        'ipatokenuniqueid': name,
                                                                        'timelimit': '0',
                                                                        'sizelimit': '0'})

    def otptoken_add(self, name, item):
        return self._post_json(method='otptoken_add', name=name, item=item)

    def otptoken_mod(self, name, item):
        return self._post_json(method='otptoken_mod', name=name, item=item)

    def otptoken_del(self, name):
        return self._post_json(method='otptoken_del', name=name)


def base64_to_base32(base64_string):
    """Converts base64 string to base32 string"""
    b32_string = base64.b32encode(base64.b64decode(base64_string)).decode('ascii')
    return b32_string


def base32_to_base64(base32_string):
    """Converts base32 string to base64 string"""
    b64_string = base64.b64encode(base64.b32decode(base32_string)).decode('ascii')
    return b64_string


def get_otptoken_dict(ansible_to_ipa, uniqueid=None, newuniqueid=None, otptype=None, secretkey=None, description=None, owner=None,
                      enabled=None, notbefore=None, notafter=None, vendor=None,
                      model=None, serial=None, algorithm=None, digits=None, offset=None,
                      interval=None, counter=None):
    """Create the dictionary of settings passed in"""

    otptoken = {}
    if uniqueid is not None:
        otptoken[ansible_to_ipa['uniqueid']] = uniqueid
    if newuniqueid is not None:
        otptoken[ansible_to_ipa['newuniqueid']] = newuniqueid
    if otptype is not None:
        otptoken[ansible_to_ipa['otptype']] = otptype.upper()
    if secretkey is not None:
        # For some unknown reason, while IPA returns the secret in base64,
        # it wants the secret passed in as base32.  This makes it more difficult
        # for comparison (does 'current' equal to 'new').  Moreover, this may
        # cause some subtle issue in a playbook as the output is encoded
        # in a different way than if it was passed in as a parameter.  For
        # these reasons, have the module standardize on base64 input (as parameter)
        # and output (from IPA).
        otptoken[ansible_to_ipa['secretkey']] = base64_to_base32(secretkey)
    if description is not None:
        otptoken[ansible_to_ipa['description']] = description
    if owner is not None:
        otptoken[ansible_to_ipa['owner']] = owner
    if enabled is not None:
        otptoken[ansible_to_ipa['enabled']] = 'FALSE' if enabled else 'TRUE'
    if notbefore is not None:
        otptoken[ansible_to_ipa['notbefore']] = notbefore + 'Z'
    if notafter is not None:
        otptoken[ansible_to_ipa['notafter']] = notafter + 'Z'
    if vendor is not None:
        otptoken[ansible_to_ipa['vendor']] = vendor
    if model is not None:
        otptoken[ansible_to_ipa['model']] = model
    if serial is not None:
        otptoken[ansible_to_ipa['serial']] = serial
    if algorithm is not None:
        otptoken[ansible_to_ipa['algorithm']] = algorithm
    if digits is not None:
        otptoken[ansible_to_ipa['digits']] = str(digits)
    if offset is not None:
        otptoken[ansible_to_ipa['offset']] = str(offset)
    if interval is not None:
        otptoken[ansible_to_ipa['interval']] = str(interval)
    if counter is not None:
        otptoken[ansible_to_ipa['counter']] = str(counter)

    return otptoken


def transform_output(ipa_otptoken, ansible_to_ipa, ipa_to_ansible):
    """Transform the output received by IPA to a format more friendly
       before it is returned to the user.  IPA returns even simple
       strings as a list of strings.  It also returns bools and
       int as string.  This function cleans that up before return.
    """
    updated_otptoken = ipa_otptoken

    # Used to hold values that will be sanitized from output as no_log.
    # For the case where secretkey is not specified at the module, but
    # is passed back from IPA.
    sanitize_strings = set()

    # Rename the IPA parameters to the more friendly ansible module names for them
    for ipa_parameter in ipa_to_ansible:
        if ipa_parameter in ipa_otptoken:
            updated_otptoken[ipa_to_ansible[ipa_parameter]] = ipa_otptoken[ipa_parameter]
            updated_otptoken.pop(ipa_parameter)

    # Change the type from IPA's list of string to the appropriate return value type
    # based on field.  By default, assume they should be strings.
    for ansible_parameter in ansible_to_ipa:
        if ansible_parameter in updated_otptoken:
            if isinstance(updated_otptoken[ansible_parameter], list) and len(updated_otptoken[ansible_parameter]) == 1:
                if ansible_parameter in ['digits', 'offset', 'interval', 'counter']:
                    updated_otptoken[ansible_parameter] = int(updated_otptoken[ansible_parameter][0])
                elif ansible_parameter == 'enabled':
                    updated_otptoken[ansible_parameter] = bool(updated_otptoken[ansible_parameter][0])
                else:
                    updated_otptoken[ansible_parameter] = updated_otptoken[ansible_parameter][0]

    if 'secretkey' in updated_otptoken:
        if isinstance(updated_otptoken['secretkey'], dict):
            if '__base64__' in updated_otptoken['secretkey']:
                sanitize_strings.add(updated_otptoken['secretkey']['__base64__'])
                b64key = updated_otptoken['secretkey']['__base64__']
                updated_otptoken.pop('secretkey')
                updated_otptoken['secretkey'] = b64key
                sanitize_strings.add(b64key)
            elif '__base32__' in updated_otptoken['secretkey']:
                sanitize_strings.add(updated_otptoken['secretkey']['__base32__'])
                b32key = updated_otptoken['secretkey']['__base32__']
                b64key = base32_to_base64(b32key)
                updated_otptoken.pop('secretkey')
                updated_otptoken['secretkey'] = b64key
                sanitize_strings.add(b32key)
                sanitize_strings.add(b64key)

    return updated_otptoken, sanitize_strings


def validate_modifications(ansible_to_ipa, module, ipa_otptoken,
                           module_otptoken, unmodifiable_after_creation):
    """Checks to see if the requested modifications are valid.  Some elements
       cannot be modified after initial creation.  However, we still want to
       validate arguments that are specified, but are not different than what
       is currently set on the server.
    """

    modifications_valid = True

    for parameter in unmodifiable_after_creation:
        if ansible_to_ipa[parameter] in module_otptoken and ansible_to_ipa[parameter] in ipa_otptoken:
            mod_value = module_otptoken[ansible_to_ipa[parameter]]

            # For someone unknown reason, the returns from IPA put almost all
            # values in a list, even though passing them in a list (even of
            # length 1) will be rejected.  The module values for all elements
            # other than type (totp or hotp) have this happen.
            if parameter == 'otptype':
                ipa_value = ipa_otptoken[ansible_to_ipa[parameter]]
            else:
                if len(ipa_otptoken[ansible_to_ipa[parameter]]) != 1:
                    module.fail_json(msg=("Invariant fail: Return value from IPA is not a list " +
                                          "of length 1.  Please open a bug report for the module."))
                if parameter == 'secretkey':
                    # We stored the secret key in base32 since we had assumed that would need to
                    # be the format if we were contacting IPA to create it.  However, we are
                    # now comparing it against what is already set in the IPA server, so convert
                    # back to base64 for comparison.
                    mod_value = base32_to_base64(mod_value)

                    # For the secret key, it is even more specific in that the key is returned
                    # in a dict, in the list, as the __base64__ entry for the IPA response.
                    ipa_value = ipa_otptoken[ansible_to_ipa[parameter]][0]['__base64__']
                    if '__base64__' in ipa_otptoken[ansible_to_ipa[parameter]][0]:
                        ipa_value = ipa_otptoken[ansible_to_ipa[parameter]][0]['__base64__']
                    elif '__base32__' in ipa_otptoken[ansible_to_ipa[parameter]][0]:
                        b32key = ipa_otptoken[ansible_to_ipa[parameter]][0]['__base32__']
                        b64key = base32_to_base64(b32key)
                        ipa_value = b64key
                    else:
                        ipa_value = None
                else:
                    ipa_value = ipa_otptoken[ansible_to_ipa[parameter]][0]

            if mod_value != ipa_value:
                modifications_valid = False
                fail_message = ("Parameter '" + parameter + "' cannot be changed once " +
                                "the OTP is created and the requested value specified here (" +
                                str(mod_value) +
                                ") differs from what is set in the IPA server ("
                                + str(ipa_value) + ")")
                module.fail_json(msg=fail_message)

    return modifications_valid


def ensure(module, client):
    # dict to map from ansible parameter names to attribute names
    # used by IPA (which are not so friendly).
    ansible_to_ipa = {'uniqueid': 'ipatokenuniqueid',
                      'newuniqueid': 'rename',
                      'otptype': 'type',
                      'secretkey': 'ipatokenotpkey',
                      'description': 'description',
                      'owner': 'ipatokenowner',
                      'enabled': 'ipatokendisabled',
                      'notbefore': 'ipatokennotbefore',
                      'notafter': 'ipatokennotafter',
                      'vendor': 'ipatokenvendor',
                      'model': 'ipatokenmodel',
                      'serial': 'ipatokenserial',
                      'algorithm': 'ipatokenotpalgorithm',
                      'digits': 'ipatokenotpdigits',
                      'offset': 'ipatokentotpclockoffset',
                      'interval': 'ipatokentotptimestep',
                      'counter': 'ipatokenhotpcounter'}

    # Create inverse dictionary for mapping return values
    ipa_to_ansible = {}
    for (k, v) in ansible_to_ipa.items():
        ipa_to_ansible[v] = k

    unmodifiable_after_creation = ['otptype', 'secretkey', 'algorithm',
                                   'digits', 'offset', 'interval', 'counter']
    state = module.params['state']
    uniqueid = module.params['uniqueid']

    module_otptoken = get_otptoken_dict(ansible_to_ipa=ansible_to_ipa,
                                        uniqueid=module.params.get('uniqueid'),
                                        newuniqueid=module.params.get('newuniqueid'),
                                        otptype=module.params.get('otptype'),
                                        secretkey=module.params.get('secretkey'),
                                        description=module.params.get('description'),
                                        owner=module.params.get('owner'),
                                        enabled=module.params.get('enabled'),
                                        notbefore=module.params.get('notbefore'),
                                        notafter=module.params.get('notafter'),
                                        vendor=module.params.get('vendor'),
                                        model=module.params.get('model'),
                                        serial=module.params.get('serial'),
                                        algorithm=module.params.get('algorithm'),
                                        digits=module.params.get('digits'),
                                        offset=module.params.get('offset'),
                                        interval=module.params.get('interval'),
                                        counter=module.params.get('counter'))

    ipa_otptoken = client.otptoken_find(name=uniqueid)

    if ansible_to_ipa['newuniqueid'] in module_otptoken:
        # Check to see if the new unique id is already taken in use
        ipa_otptoken_new = client.otptoken_find(name=module_otptoken[ansible_to_ipa['newuniqueid']])
        if ipa_otptoken_new:
            module.fail_json(msg=("Requested rename through newuniqueid to " +
                                  module_otptoken[ansible_to_ipa['newuniqueid']] +
                                  " failed because the new unique id is already in use"))

    changed = False
    if state == 'present':
        if not ipa_otptoken:
            changed = True
            if not module.check_mode:
                # It would not make sense to have a rename after creation, so if the user
                # specified a newuniqueid, just replace the uniqueid with the updated one
                # before creation
                if ansible_to_ipa['newuniqueid'] in module_otptoken:
                    module_otptoken[ansible_to_ipa['uniqueid']] = module_otptoken[ansible_to_ipa['newuniqueid']]
                    uniqueid = module_otptoken[ansible_to_ipa['newuniqueid']]
                    module_otptoken.pop(ansible_to_ipa['newuniqueid'])

                # IPA wants the unique id in the first position and not as a key/value pair.
                # Get rid of it from the otptoken dict and just specify it in the name field
                # for otptoken_add.
                if ansible_to_ipa['uniqueid'] in module_otptoken:
                    module_otptoken.pop(ansible_to_ipa['uniqueid'])

                module_otptoken['all'] = True
                ipa_otptoken = client.otptoken_add(name=uniqueid, item=module_otptoken)
        else:
            if not(validate_modifications(ansible_to_ipa, module, ipa_otptoken,
                                          module_otptoken, unmodifiable_after_creation)):
                module.fail_json(msg="Modifications requested in module are not valid")

            # IPA will reject 'modifications' that do not actually modify anything
            # if any of the unmodifiable elements are specified.  Explicitly
            # get rid of them here.  They were not different or else the
            # we would have failed out in validate_modifications.
            for x in unmodifiable_after_creation:
                if ansible_to_ipa[x] in module_otptoken:
                    module_otptoken.pop(ansible_to_ipa[x])

            diff = client.get_diff(ipa_data=ipa_otptoken, module_data=module_otptoken)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:

                    # IPA wants the unique id in the first position and not as a key/value pair.
                    # Get rid of it from the otptoken dict and just specify it in the name field
                    # for otptoken_mod.
                    if ansible_to_ipa['uniqueid'] in module_otptoken:
                        module_otptoken.pop(ansible_to_ipa['uniqueid'])

                    module_otptoken['all'] = True
                    ipa_otptoken = client.otptoken_mod(name=uniqueid, item=module_otptoken)
    else:
        if ipa_otptoken:
            changed = True
            if not module.check_mode:
                client.otptoken_del(name=uniqueid)

    # Transform the output to use ansible keywords (not the IPA keywords) and
    # sanitize any key values in the output.
    ipa_otptoken, sanitize_strings = transform_output(ipa_otptoken, ansible_to_ipa, ipa_to_ansible)
    module.no_log_values = module.no_log_values.union(sanitize_strings)
    sanitized_otptoken = sanitize_keys(obj=ipa_otptoken, no_log_strings=module.no_log_values)
    return changed, sanitized_otptoken


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(uniqueid=dict(type='str', aliases=['name'], required=True),
                         newuniqueid=dict(type='str'),
                         otptype=dict(type='str', choices=['totp', 'hotp']),
                         secretkey=dict(type='str', no_log=True),
                         description=dict(type='str'),
                         owner=dict(type='str'),
                         enabled=dict(type='bool', default=True),
                         notbefore=dict(type='str'),
                         notafter=dict(type='str'),
                         vendor=dict(type='str'),
                         model=dict(type='str'),
                         serial=dict(type='str'),
                         state=dict(type='str', choices=['present', 'absent'], default='present'),
                         algorithm=dict(type='str', choices=['sha1', 'sha256', 'sha384', 'sha512']),
                         digits=dict(type='int', choices=[6, 8]),
                         offset=dict(type='int'),
                         interval=dict(type='int'),
                         counter=dict(type='int'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = OTPTokenIPAClient(module=module,
                               host=module.params['ipa_host'],
                               port=module.params['ipa_port'],
                               protocol=module.params['ipa_prot'])

    try:
        client.login(username=module.params['ipa_user'],
                     password=module.params['ipa_pass'])
        changed, otptoken = ensure(module, client)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, otptoken=otptoken)


if __name__ == '__main__':
    main()
