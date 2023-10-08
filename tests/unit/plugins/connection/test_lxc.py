# Copyright (c) 2020 Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import sys

from io import StringIO

from ansible.errors import AnsibleError
from ansible.playbook.play_context import PlayContext
from ansible.plugins.loader import connection_loader
from ansible_collections.community.general.tests.unit.compat import mock


@pytest.fixture(autouse=True)
def lxc(request):
    """Fixture to import/load the lxc plugin module.

    The fixture parameter is used to determine the presence of liblxc.
    When true (default), a mocked liblxc module is injected. If False,
    no liblxc will be present.
    """
    liblxc_present = getattr(request, 'param', True)

    class ContainerMock(mock.MagicMock):
        def __init__(self, name):
            super(ContainerMock, self).__init__()
            self.name = name
            self.state = 'STARTED'

    liblxc_module_mock = mock.MagicMock()
    liblxc_module_mock.Container = ContainerMock

    with mock.patch.dict('sys.modules'):
        if liblxc_present:
            sys.modules['lxc'] = liblxc_module_mock
        elif 'lxc' in sys.modules:
            del sys.modules['lxc']

        from ansible_collections.community.general.plugins.connection import lxc as lxc_plugin_module

        assert lxc_plugin_module.HAS_LIBLXC == liblxc_present
        assert bool(getattr(lxc_plugin_module, '_lxc', None)) == liblxc_present

        yield lxc_plugin_module


class TestLXCConnectionClass():

    @pytest.mark.parametrize('lxc', [True, False], indirect=True)
    def test_lxc_connection_module(self, lxc):
        """Test that a connection can be created with the plugin."""
        play_context = PlayContext()
        in_stream = StringIO()

        conn = connection_loader.get('lxc', play_context, in_stream)
        assert conn
        assert isinstance(conn, lxc.Connection)

    @pytest.mark.parametrize('lxc', [False], indirect=True)
    def test_lxc_connection_liblxc_error(self, lxc):
        """Test that on connect an error is thrown if liblxc is not present."""
        play_context = PlayContext()
        in_stream = StringIO()
        conn = connection_loader.get('lxc', play_context, in_stream)

        with pytest.raises(AnsibleError, match='lxc python bindings are not installed'):
            conn._connect()

    def test_remote_addr_option(self):
        """Test that the remote_addr option is used"""
        play_context = PlayContext()
        in_stream = StringIO()
        conn = connection_loader.get('lxc', play_context, in_stream)

        container_name = 'my-container'
        conn.set_option('remote_addr', container_name)
        assert conn.get_option('remote_addr') == container_name

        conn._connect()
        assert conn.container_name == container_name
