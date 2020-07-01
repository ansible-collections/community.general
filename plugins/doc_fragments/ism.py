# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
options:
  provider:
    description:
      - A dict object containing connection details.
    type: dict
    suboptions:
      host:
        description:
          - Specifies the DNS host name or address for connecting to the remote
            device over the specified transport.  The value of host is used as
            the destination address for the transport.
        type: str
      username:
        description:
          - Configures the username to use to authenticate the connection to
            the remote device. If the value is not specified in the task, the value of environment
            variable C(ANSIBLE_NET_USERNAME) will be used instead.
        type: str
      password:
        description:
          - Specifies the password to use to authenticate the connection to
            the remote device. If the value is not specified in the task, the
            value of environment variable C(ANSIBLE_NET_PASSWORD) will be used instead.
        type: str
  host:
    description:
      - Specifies the DNS host name or address for connecting to the remote
        device over the specified transport.  The value of host is used as
        the destination address for the transport.
    type: str
  username:
    description:
      - Configures the username to use to authenticate the connection to
        the remote device. If the value is not specified in the task, the value of environment
        variable C(ANSIBLE_NET_USERNAME) will be used instead.
    type: str
  password:
    description:
      - Specifies the password to use to authenticate the connection to
        the remote device. If the value is not specified in the task, the
        value of environment variable C(ANSIBLE_NET_PASSWORD) will be used instead.
    type: str
'''
