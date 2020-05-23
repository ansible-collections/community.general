from __future__ import (absolute_import, division, print_function)
from ansible_collections.community.general.plugins.action.semodule import ActionModule
from ansible.playbook.task import Task
from tests.unit.compat.mock import MagicMock, Mock
from ansible.plugins.loader import connection_loader
import os
import pytest
__metaclass__ = type


SEMODULE_OUTPUT = '''unconfined      3.5.0
unconfineduser  1.0.0
unlabelednet    1.0.0
unprivuser      2.4.0
updfstab        1.6.0
usbmodules      1.3.0
usbmuxd 1.2.0
userdomain      4.9.1
userhelper      1.8.1
usermanage      1.19.0
usernetctl      1.7.0
'''

play_context = Mock()
play_context.shell = 'sh'
connection = connection_loader.get('local', play_context, os.devnull)
task = MagicMock(Task)


def test_module_exist():
    semodule_action = ActionModule(task, connection, play_context, loader=None, templar=None, shared_loader_obj=None)
    assert semodule_action._module_exist('usermanage', SEMODULE_OUTPUT)
    assert not semodule_action._module_exist('notreal', SEMODULE_OUTPUT)
