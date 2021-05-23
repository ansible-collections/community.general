# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils.six.moves import xmlrpc_client

import pytest


def get_method_name(request_body):
    return xmlrpc_client.loads(request_body)[1]


@pytest.fixture
def mock_request(request, mocker):
    responses = request.getfixturevalue('testcase')['calls']
    module_name = request.module.TESTED_MODULE

    def transport_request(host, handler, request_body, verbose=0):
        """Fake request"""
        method_name = get_method_name(request_body)
        excepted_name, response = responses.pop(0)
        if method_name == excepted_name:
            if isinstance(response, Exception):
                raise response
            else:
                return response
        else:
            raise Exception('Expected call: %r, called with: %r' % (excepted_name, method_name))

    target = '{0}.xmlrpc_client.Transport.request'.format(module_name)
    mocker.patch(target, side_effect=transport_request)
