# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from io import BytesIO
import mock
import ansible_collections.community.general.plugins.modules.web_infrastructure.bugzilla as bugzilla

from ansible.module_utils.common._collections_compat import Mapping


BUG_DATA = {"uri": u'https://fake-buzilla.com',
            "username": "test",
            "password": "test",
            "response": b"""
               {
                 "id": "3638964",
                 "name": "ansible",
                 "full_name": "ansible/ansible",
               }"""
            }


bugzilla.handle_request = mock.Mock(return_value=BUG_DATA['response'])


def test_fetch():
    "test fetch bugs data"

    params = {
        'bug': '3638964',
        'timeout': 30,
    }

    json_data = bugzilla.fetch(
        BUG_DATA['uri'],
        BUG_DATA['username'],
        BUG_DATA['password'],
        params
    )

    assert json_data == BUG_DATA['response']


def test_comment():
    "test comment bug"

    params = {
        'bug': '3638964',
        'comment': 'test',
        'timeout': 30,
    }

    json_data = bugzilla.fetch(
        BUG_DATA['uri'],
        BUG_DATA['username'],
        BUG_DATA['password'],
        params
    )

    assert json_data == BUG_DATA['response']


def test_transition():
    "test transition"

    params = {
        'bug': '3638964',
        'status': "Test",
        'timeout': 30,
    }

    json_data = bugzilla.fetch(
        BUG_DATA['uri'],
        BUG_DATA['username'],
        BUG_DATA['password'],
        params
    )

    assert json_data == BUG_DATA['response']
