# Copyright: (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

import pytest

from ansible.module_utils._text import to_text
from ansible_collections.community.general.plugins.modules.net_tools import nmcli

pytestmark = pytest.mark.usefixtures('patch_ansible_module')

TESTCASE_CONNECTION = [
    {
        'type': 'ethernet',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'generic',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'team',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bond',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bond-slave',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'bridge',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'vlan',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'vxlan',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'ipip',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
    {
        'type': 'sit',
        'conn_name': 'non_existent_nw_device',
        'state': 'absent',
        '_ansible_check_mode': True,
    },
]

TESTCASE_GENERIC = [
    {
        'type': 'generic',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'generic_non_existant',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'state': 'present',
        '_ansible_check_mode': False,
    },
]

TESTCASE_GENERIC_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              generic_non_existant
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv6.method:                            auto
"""

TESTCASE_GENERIC_DNS4_SEARCH = [
    {
        'type': 'generic',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'generic_non_existant',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'state': 'present',
        'dns4_search': 'search.redhat.com',
        'dns6_search': 'search6.redhat.com',
        '_ansible_check_mode': False,
    }
]

TESTCASE_GENERIC_DNS4_SEARCH_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              generic_non_existant
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv4.dns-search:                        search.redhat.com
ipv6.dns-search:                        search6.redhat.com
ipv6.method:                            auto
"""

TESTCASE_BOND = [
    {
        'type': 'bond',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'bond_non_existant',
        'mode': 'active-backup',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'state': 'present',
        'primary': 'non_existent_primary',
        '_ansible_check_mode': False,
    }
]

TESTCASE_BOND_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              bond_non_existant
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv6.method:                            auto
bond.options:                           mode=active-backup,primary=non_existent_primary
"""

TESTCASE_BRIDGE = [
    {
        'type': 'bridge',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'br0_non_existant',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'maxage': 100,
        'stp': True,
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_BRIDGE_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              br0_non_existant
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv6.method:                            auto
bridge.stp:                             yes
bridge.max-age:                         100
bridge.ageing-time:                     300
bridge.hello-time:                      2
bridge.priority:                        128
bridge.forward-delay:                   15
"""

TESTCASE_BRIDGE_SLAVE = [
    {
        'type': 'bridge-slave',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'br0_non_existant',
        'path_cost': 100,
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_BRIDGE_SLAVE_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              br0_non_existant
connection.autoconnect:                 yes
bridge-port.path-cost:                  100
bridge-port.hairpin-mode:               yes
bridge-port.priority:                   32
"""

TESTCASE_VLAN = [
    {
        'type': 'vlan',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'vlan_not_exists',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'vlanid': 10,
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_VLAN_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              vlan_not_exists
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv6.method:                            auto
vlan.id:                                10
"""

TESTCASE_VXLAN = [
    {
        'type': 'vxlan',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'vxlan-existent_nw_device',
        'vxlan_id': 11,
        'vxlan_local': '192.168.225.5',
        'vxlan_remote': '192.168.225.6',
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_VXLAN_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              existent_nw_device
connection.autoconnect:                 yes
vxlan.id:                               11
vxlan.local:                            192.168.225.5
vxlan.remote:                           192.168.225.6
"""

TESTCASE_IPIP = [
    {
        'type': 'ipip',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'ipip-existent_nw_device',
        'ip_tunnel_dev': 'non_existent_ipip_device',
        'ip_tunnel_local': '192.168.225.5',
        'ip_tunnel_remote': '192.168.225.6',
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_IPIP_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              ipip-existent_nw_device
connection.autoconnect:                 yes
ip-tunnel.mode:                         ipip
ip-tunnel.parent:                       non_existent_ipip_device
ip-tunnel.local:                        192.168.225.5
ip-tunnel.remote:                       192.168.225.6
"""

TESTCASE_SIT = [
    {
        'type': 'sit',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'sit-existent_nw_device',
        'ip_tunnel_dev': 'non_existent_sit_device',
        'ip_tunnel_local': '192.168.225.5',
        'ip_tunnel_remote': '192.168.225.6',
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_SIT_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              sit-existent_nw_device
connection.autoconnect:                 yes
ip-tunnel.mode:                         sit
ip-tunnel.parent:                       non_existent_sit_device
ip-tunnel.local:                        192.168.225.5
ip-tunnel.remote:                       192.168.225.6
"""

TESTCASE_ETHERNET_DHCP = [
    {
        'type': 'ethernet',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'ethernet_non_existant',
        'dhcp_client_id': '00:11:22:AA:BB:CC:DD',
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_ETHERNET_DHCP_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              ethernet_non_existant
connection.autoconnect:                 yes
ipv4.method:                            auto
ipv4.dhcp-client-id:                    00:11:22:AA:BB:CC:DD
ipv6.method:                            auto
"""

TESTCASE_ETHERNET_STATIC = [
    {
        'type': 'ethernet',
        'conn_name': 'non_existent_nw_device',
        'ifname': 'ethernet_non_existant',
        'ip4': '10.10.10.10/24',
        'gw4': '10.10.10.1',
        'dns4': ['1.1.1.1', '8.8.8.8'],
        'state': 'present',
        '_ansible_check_mode': False,
    }
]

TESTCASE_ETHERNET_STATIC_SHOW_OUTPUT = """\
connection.id:                          non_existent_nw_device
connection.interface-name:              ethernet_non_existant
connection.autoconnect:                 yes
ipv4.method:                            manual
ipv4.addresses:                         10.10.10.10/24
ipv4.gateway:                           10.10.10.1
ipv4.dns:                               1.1.1.1,8.8.8.8
ipv6.method:                            auto
"""


def mocker_set(mocker, connection_exists=False):
    """
    Common mocker object
    """
    mocker.patch('ansible_collections.community.general.plugins.modules.net_tools.nmcli.HAVE_DBUS', True)
    mocker.patch('ansible_collections.community.general.plugins.modules.net_tools.nmcli.HAVE_NM_CLIENT', True)
    get_bin_path = mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')
    get_bin_path.return_value = '/usr/bin/nmcli'
    connection = mocker.patch.object(nmcli.Nmcli, 'connection_exists')
    connection.return_value = connection_exists
    return connection


@pytest.fixture
def mocked_generic_connection_create(mocker):
    mocker_set(mocker)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, "", "")
    return command_result


@pytest.fixture
def mocked_connection_exists(mocker):
    connection = mocker_set(mocker, connection_exists=True)
    return connection


@pytest.fixture
def mocked_generic_connection_modify(mocker):
    mocker_set(mocker, connection_exists=True)
    connection_changed = mocker.patch.object(
        nmcli.Nmcli, 'is_connection_changed')
    connection_changed.return_value = (True, dict())
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, "", "")
    return command_result


@pytest.fixture
def mocked_generic_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_GENERIC_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_generic_connection_dns_search_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (
        0, TESTCASE_GENERIC_DNS4_SEARCH_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_bond_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_BOND_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_bridge_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_BRIDGE_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_bridge_slave_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_BRIDGE_SLAVE_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_vlan_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_VLAN_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_vxlan_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_VXLAN_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_ipip_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_IPIP_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_sit_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_SIT_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_ethernet_connection_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_ETHERNET_DHCP, "")
    return command_result


@pytest.fixture
def mocked_ethernet_connection_dhcp_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_ETHERNET_DHCP_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_ethernet_connection_static_unchanged(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.return_value = (0, TESTCASE_ETHERNET_STATIC_SHOW_OUTPUT, "")
    return command_result


@pytest.fixture
def mocked_ethernet_connection_dhcp_to_static(mocker):
    mocker_set(mocker, connection_exists=True)
    command_result = mocker.patch.object(nmcli.Nmcli, 'execute_command')
    command_result.side_effect = [
        (0, TESTCASE_ETHERNET_DHCP_SHOW_OUTPUT, ""),
        (0, "", ""),
    ]
    return command_result


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BOND, indirect=['patch_ansible_module'])
def test_bond_connection_create(mocked_generic_connection_create, capfd):
    """
    Test : Bond connection created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'bond'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'
    assert args[0][7] == 'ifname'
    assert args[0][8] == 'bond_non_existant'

    for param in ['gw4', 'primary', 'autoconnect', 'mode', 'active-backup', 'ip4']:
        assert param in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BOND, indirect=['patch_ansible_module'])
def test_bond_connection_unchanged(mocked_bond_connection_unchanged, capfd):
    """
    Test : Bond connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC, indirect=['patch_ansible_module'])
def test_generic_connection_create(mocked_generic_connection_create, capfd):
    """
    Test : Generic connection created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'generic'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'

    for param in ['autoconnect', 'gw4', 'ip4']:
        assert param in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC, indirect=['patch_ansible_module'])
def test_generic_connection_modify(mocked_generic_connection_modify, capfd):
    """
    Test : Generic connection modify
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['ipv4.gateway', 'ipv4.address']:
        assert param in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC, indirect=['patch_ansible_module'])
def test_generic_connection_unchanged(mocked_generic_connection_unchanged, capfd):
    """
    Test : Generic connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC_DNS4_SEARCH, indirect=['patch_ansible_module'])
def test_generic_connection_create_dns_search(mocked_generic_connection_create, capfd):
    """
    Test : Generic connection created with dns search
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert 'ipv4.dns-search' in args[0]
    assert 'ipv6.dns-search' in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC_DNS4_SEARCH, indirect=['patch_ansible_module'])
def test_generic_connection_modify_dns_search(mocked_generic_connection_create, capfd):
    """
    Test : Generic connection modified with dns search
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert 'ipv4.dns-search' in args[0]
    assert 'ipv6.dns-search' in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_GENERIC_DNS4_SEARCH, indirect=['patch_ansible_module'])
def test_generic_connection_dns_search_unchanged(mocked_generic_connection_dns_search_unchanged, capfd):
    """
    Test : Generic connection with dns search unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_CONNECTION, indirect=['patch_ansible_module'])
def test_dns4_none(mocked_connection_exists, capfd):
    """
    Test if DNS4 param is None
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE, indirect=['patch_ansible_module'])
def test_create_bridge(mocked_generic_connection_create, capfd):
    """
    Test if Bridge created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'bridge'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'

    for param in ['ip4', '10.10.10.10/24', 'gw4', '10.10.10.1', 'bridge.max-age', '100', 'bridge.stp', 'yes']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE, indirect=['patch_ansible_module'])
def test_mod_bridge(mocked_generic_connection_modify, capfd):
    """
    Test if Bridge modified
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1

    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'
    for param in ['ipv4.address', '10.10.10.10/24', 'ipv4.gateway', '10.10.10.1', 'bridge.max-age', '100', 'bridge.stp', 'yes']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE, indirect=['patch_ansible_module'])
def test_bridge_connection_unchanged(mocked_bridge_connection_unchanged, capfd):
    """
    Test : Bridge connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE_SLAVE, indirect=['patch_ansible_module'])
def test_create_bridge_slave(mocked_generic_connection_create, capfd):
    """
    Test if Bridge_slave created
    """

    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'bridge-slave'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'

    for param in ['bridge-port.path-cost', '100']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE_SLAVE, indirect=['patch_ansible_module'])
def test_mod_bridge_slave(mocked_generic_connection_modify, capfd):
    """
    Test if Bridge_slave modified
    """

    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['bridge-port.path-cost', '100']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_BRIDGE_SLAVE, indirect=['patch_ansible_module'])
def test_bridge_slave_unchanged(mocked_bridge_slave_unchanged, capfd):
    """
    Test : Bridge-slave connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VLAN, indirect=['patch_ansible_module'])
def test_create_vlan_con(mocked_generic_connection_create, capfd):
    """
    Test if VLAN created
    """

    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'vlan'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'

    for param in ['ip4', '10.10.10.10/24', 'gw4', '10.10.10.1', 'id', '10']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VLAN, indirect=['patch_ansible_module'])
def test_mod_vlan_conn(mocked_generic_connection_modify, capfd):
    """
    Test if VLAN modified
    """

    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['ipv4.address', '10.10.10.10/24', 'ipv4.gateway', '10.10.10.1', 'vlan.id', '10']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VLAN, indirect=['patch_ansible_module'])
def test_vlan_connection_unchanged(mocked_vlan_connection_unchanged, capfd):
    """
    Test : VLAN connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VXLAN, indirect=['patch_ansible_module'])
def test_create_vxlan(mocked_generic_connection_create, capfd):
    """
    Test if vxlan created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'vxlan'
    assert args[0][5] == 'con-name'
    assert args[0][6] == 'non_existent_nw_device'
    assert args[0][7] == 'ifname'

    for param in ['vxlan.local', '192.168.225.5', 'vxlan.remote', '192.168.225.6', 'vxlan.id', '11']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VXLAN, indirect=['patch_ansible_module'])
def test_vxlan_mod(mocked_generic_connection_modify, capfd):
    """
    Test if vxlan modified
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['vxlan.local', '192.168.225.5', 'vxlan.remote', '192.168.225.6', 'vxlan.id', '11']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_VXLAN, indirect=['patch_ansible_module'])
def test_vxlan_connection_unchanged(mocked_vxlan_connection_unchanged, capfd):
    """
    Test : VxLAN connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_IPIP, indirect=['patch_ansible_module'])
def test_create_ipip(mocked_generic_connection_create, capfd):
    """
    Test if ipip created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'ip-tunnel'
    assert args[0][5] == 'mode'
    assert args[0][6] == 'ipip'
    assert args[0][7] == 'con-name'
    assert args[0][8] == 'non_existent_nw_device'
    assert args[0][9] == 'ifname'
    assert args[0][10] == 'ipip-existent_nw_device'
    assert args[0][11] == 'dev'
    assert args[0][12] == 'non_existent_ipip_device'

    for param in ['ip-tunnel.local', '192.168.225.5', 'ip-tunnel.remote', '192.168.225.6']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_IPIP, indirect=['patch_ansible_module'])
def test_ipip_mod(mocked_generic_connection_modify, capfd):
    """
    Test if ipip modified
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['ip-tunnel.local', '192.168.225.5', 'ip-tunnel.remote', '192.168.225.6']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_IPIP, indirect=['patch_ansible_module'])
def test_ipip_connection_unchanged(mocked_ipip_connection_unchanged, capfd):
    """
    Test : IPIP connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_SIT, indirect=['patch_ansible_module'])
def test_create_sit(mocked_generic_connection_create, capfd):
    """
    Test if sit created
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'add'
    assert args[0][3] == 'type'
    assert args[0][4] == 'ip-tunnel'
    assert args[0][5] == 'mode'
    assert args[0][6] == 'sit'
    assert args[0][7] == 'con-name'
    assert args[0][8] == 'non_existent_nw_device'
    assert args[0][9] == 'ifname'
    assert args[0][10] == 'sit-existent_nw_device'
    assert args[0][11] == 'dev'
    assert args[0][12] == 'non_existent_sit_device'

    for param in ['ip-tunnel.local', '192.168.225.5', 'ip-tunnel.remote', '192.168.225.6']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_SIT, indirect=['patch_ansible_module'])
def test_sit_mod(mocked_generic_connection_modify, capfd):
    """
    Test if sit modified
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['ip-tunnel.local', '192.168.225.5', 'ip-tunnel.remote', '192.168.225.6']:
        assert param in map(to_text, args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_SIT, indirect=['patch_ansible_module'])
def test_sit_connection_unchanged(mocked_sit_connection_unchanged, capfd):
    """
    Test : SIT connection unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_ETHERNET_DHCP, indirect=['patch_ansible_module'])
def test_eth_dhcp_client_id_con_create(mocked_generic_connection_create, capfd):
    """
    Test : Ethernet connection created with DHCP_CLIENT_ID
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 1
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[0]

    assert 'ipv4.dhcp-client-id' in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_ETHERNET_DHCP, indirect=['patch_ansible_module'])
def test_ethernet_connection_dhcp_unchanged(mocked_ethernet_connection_dhcp_unchanged, capfd):
    """
    Test : Ethernet connection with DHCP_CLIENT_ID unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_ETHERNET_STATIC, indirect=['patch_ansible_module'])
def test_modify_ethernet_dhcp_to_static(mocked_ethernet_connection_dhcp_to_static, capfd):
    """
    Test : Modify ethernet connection from DHCP to static
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 2
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    args, kwargs = arg_list[1]

    assert args[0][0] == '/usr/bin/nmcli'
    assert args[0][1] == 'con'
    assert args[0][2] == 'mod'
    assert args[0][3] == 'non_existent_nw_device'

    for param in ['ipv4.method', 'ipv4.gateway', 'ipv4.address']:
        assert param in args[0]

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_ETHERNET_STATIC, indirect=['patch_ansible_module'])
def test_create_ethernet_static(mocked_generic_connection_create, capfd):
    """
    Test : Create ethernet connection with static IP configuration
    """

    with pytest.raises(SystemExit):
        nmcli.main()

    assert nmcli.Nmcli.execute_command.call_count == 3
    arg_list = nmcli.Nmcli.execute_command.call_args_list
    add_args, add_kw = arg_list[0]
    mod_args, mod_kw = arg_list[1]

    assert add_args[0][0] == '/usr/bin/nmcli'
    assert add_args[0][1] == 'con'
    assert add_args[0][2] == 'add'
    assert add_args[0][3] == 'type'
    assert add_args[0][4] == 'ethernet'
    assert add_args[0][5] == 'con-name'
    assert add_args[0][6] == 'non_existent_nw_device'
    assert add_args[0][7] == 'ifname'
    assert add_args[0][8] == 'ethernet_non_existant'

    for param in ['ip4', '10.10.10.10/24', 'gw4', '10.10.10.1']:
        assert param in map(to_text, add_args[0])

    assert mod_args[0][0] == '/usr/bin/nmcli'
    assert mod_args[0][1] == 'con'
    assert mod_args[0][2] == 'mod'
    assert mod_args[0][3] == 'non_existent_nw_device'

    for param in ['ipv4.dns', '1.1.1.1 8.8.8.8']:
        assert param in map(to_text, mod_args[0])

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert results['changed']


@pytest.mark.parametrize('patch_ansible_module', TESTCASE_ETHERNET_STATIC, indirect=['patch_ansible_module'])
def test_ethernet_connection_static_unchanged(mocked_ethernet_connection_static_unchanged, capfd):
    """
    Test : Ethernet connection with static IP configuration unchanged
    """
    with pytest.raises(SystemExit):
        nmcli.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert not results.get('failed')
    assert not results['changed']
