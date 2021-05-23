#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Matt Makai <matthew.makai@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: twilio
short_description: Sends a text message to a mobile phone through Twilio.
description:
   - Sends a text message to a phone number through the Twilio messaging API.
notes:
   - This module is non-idempotent because it sends an email through the
     external API. It is idempotent only in the case that the module fails.
   - Like the other notification modules, this one requires an external
     dependency to work. In this case, you'll need a Twilio account with
     a purchased or verified phone number to send the text message.
options:
  account_sid:
    type: str
    description:
      user's Twilio account token found on the account page
    required: true
  auth_token:
    type: str
    description: user's Twilio authentication token
    required: true
  msg:
    type: str
    description:
      the body of the text message
    required: true
  to_numbers:
    type: list
    elements: str
    description:
      one or more phone numbers to send the text message to,
      format +15551112222
    required: true
    aliases: [ to_number ]
  from_number:
    type: str
    description:
      the Twilio number to send the text message from, format +15551112222
    required: true
  media_url:
    type: str
    description:
      a URL with a picture, video or sound clip to send with an MMS
      (multimedia message) instead of a plain SMS
    required: false

author: "Matt Makai (@makaimc)"
'''

EXAMPLES = '''
# send an SMS about the build status to (555) 303 5681
# note: replace account_sid and auth_token values with your credentials
# and you have to have the 'from_number' on your Twilio account
- name: Send a text message to a mobile phone through Twilio
  community.general.twilio:
    msg: All servers with webserver role are now configured.
    account_sid: ACXXXXXXXXXXXXXXXXX
    auth_token: ACXXXXXXXXXXXXXXXXX
    from_number: +15552014545
    to_number: +15553035681
  delegate_to: localhost

# send an SMS to multiple phone numbers about the deployment
# note: replace account_sid and auth_token values with your credentials
# and you have to have the 'from_number' on your Twilio account
- name: Send a text message to a mobile phone through Twilio
  community.general.twilio:
    msg: This server configuration is now complete.
    account_sid: ACXXXXXXXXXXXXXXXXX
    auth_token: ACXXXXXXXXXXXXXXXXX
    from_number: +15553258899
    to_numbers:
      - +15551113232
      - +12025551235
      - +19735559010
  delegate_to: localhost

# send an MMS to a single recipient with an update on the deployment
# and an image of the results
# note: replace account_sid and auth_token values with your credentials
# and you have to have the 'from_number' on your Twilio account
- name: Send a text message to a mobile phone through Twilio
  community.general.twilio:
    msg: Deployment complete!
    account_sid: ACXXXXXXXXXXXXXXXXX
    auth_token: ACXXXXXXXXXXXXXXXXX
    from_number: +15552014545
    to_number: +15553035681
    media_url: https://demo.twilio.com/logo.png
  delegate_to: localhost
'''

# =======================================
# twilio module support methods
#
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import fetch_url


def post_twilio_api(module, account_sid, auth_token, msg, from_number,
                    to_number, media_url=None):
    URI = "https://api.twilio.com/2010-04-01/Accounts/%s/Messages.json" \
        % (account_sid,)
    AGENT = "Ansible"

    data = {'From': from_number, 'To': to_number, 'Body': msg}
    if media_url:
        data['MediaUrl'] = media_url
    encoded_data = urlencode(data)

    headers = {'User-Agent': AGENT,
               'Content-type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json',
               }

    # Hack module params to have the Basic auth params that fetch_url expects
    module.params['url_username'] = account_sid.replace('\n', '')
    module.params['url_password'] = auth_token.replace('\n', '')

    return fetch_url(module, URI, data=encoded_data, headers=headers)


# =======================================
# Main
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            account_sid=dict(required=True),
            auth_token=dict(required=True, no_log=True),
            msg=dict(required=True),
            from_number=dict(required=True),
            to_numbers=dict(required=True, aliases=['to_number'], type='list', elements='str'),
            media_url=dict(default=None, required=False),
        ),
        supports_check_mode=True
    )

    account_sid = module.params['account_sid']
    auth_token = module.params['auth_token']
    msg = module.params['msg']
    from_number = module.params['from_number']
    to_numbers = module.params['to_numbers']
    media_url = module.params['media_url']

    for number in to_numbers:
        r, info = post_twilio_api(module, account_sid, auth_token, msg,
                                  from_number, number, media_url)
        if info['status'] not in [200, 201]:
            body_message = "unknown error"
            if 'body' in info:
                body = module.from_json(info['body'])
                body_message = body['message']
            module.fail_json(msg="unable to send message to %s: %s" % (number, body_message))

    module.exit_json(msg=msg, changed=False)


if __name__ == '__main__':
    main()
