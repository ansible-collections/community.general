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
from ansible_collections.community.internal_test_tools.tests.unit.compat import mock


@pytest.fixture(autouse=True)
def lxc(request):
    """Fixture to import/load the lxc plugin module.

    The fixture parameter is used to determine the presence of liblxc.
    When true (default), a mocked liblxc module is injected. If False,
    no liblxc will be present.
    """
    liblxc_present = getattr(request, 'param', True)

    class ContainerMock():
        # dict of container name to its state
        _container_states = {}

        def __init__(self, name):
            super(ContainerMock, self).__init__()
            self.name = name

        @property
        def state(self):
            return ContainerMock._container_states.get(self.name, 'STARTED')

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

    def test_error_when_stopped(self, lxc):
        """Test that on connect an error is thrown if the container is stopped."""
        play_context = PlayContext()
        in_stream = StringIO()
        conn = connection_loader.get('lxc', play_context, in_stream)
        conn.set_option('remote_addr', 'my-container')

        lxc._lxc.Container._container_states['my-container'] = 'STOPPED'

        with pytest.raises(AnsibleError, match='my-container is not running'):
            conn._connect()

    def test_container_name_change(self):
        """Test connect method reconnects when remote_addr changes"""
        play_context = PlayContext()
        in_stream = StringIO()
        conn = connection_loader.get('lxc', play_context, in_stream)

        # setting the option does nothing
        container1_name = 'my-container'
        conn.set_option('remote_addr', container1_name)
        assert conn.container_name is None
        assert conn.container is None

        # first call initializes the connection
        conn._connect()
        assert conn.container_name == container1_name
        assert conn.container is not None
        assert conn.container.name == container1_name
        container1 = conn.container

        # second call is basically a no-op
        conn._connect()
        assert conn.container_name == container1_name
        assert conn.container is container1
        assert conn.container.name == container1_name

        # setting the option does again nothing
        container2_name = 'my-other-container'
        conn.set_option('remote_addr', container2_name)
        assert conn.container_name == container1_name
        assert conn.container is container1
        assert conn.container.name == container1_name

        # first call with a different remote_addr changes the connection
        conn._connect()
        assert conn.container_name == container2_name
        assert conn.container is not None
        assert conn.container is not container1
        assert conn.container.name == container2_name
