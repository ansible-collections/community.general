# (C) 2020, Turntabl, <info@turtabl.io>
# (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: callback plugin to receive log streams
    type: locking
    short_description: creates a daemonized UDP socket server
    description:
      - Creates a socket server that is daemonized and  receives logs from terraform module
    requirements:
     - Whitelist in configuration
     - A writeable /var/log/ansible/hosts directory by the user executing Ansible on the controller
'''

import time
import sys
import os
import re
import socket
import multiprocessing
import random
from ansible import constants as C
from ansible import context
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


def sample_server(display_self):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_port = int(os.environ.get('ANSIBLE_TERRAFORM_STREAM_PORT'))
    socket_host = os.environ.get('ANSIBLE_TERRAFORM_STREAM_HOST')
    server_socket.bind((socket_host, socket_port))

    while True:
        message, address = server_socket.recvfrom(1024)
        message = message
        msg = "{}".format(message.decode('utf-8'))
        display_self.display(msg, color=C.COLOR_OK, stderr=False)


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.terraform_stream'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._task_type_cache = {}

    def v2_playbook_on_start(self, playbook):
        self.serve = multiprocessing.Process(name='stdout_stream', target=sample_server, args=(self._display,))
        self.set_option('server', self.serve)
        self.server = self.get_option("server")
        self.server.daemon = True
        self.server.start()
        self._display.display("Terraform logs initializing", color=C.COLOR_OK, stderr=False)

    def v2_playbook_on_stats(self, stats):
        self.server.terminate()
