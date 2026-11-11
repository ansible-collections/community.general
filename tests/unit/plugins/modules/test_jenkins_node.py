# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import call, patch
from xml.etree import ElementTree as et

import jenkins
import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)
from pytest import fixture, mark, param, raises

from ansible_collections.community.general.plugins.modules import jenkins_node


def xml_equal(x, y):
    # type: (et.Element | str, et.Element | str) -> bool
    if isinstance(x, str):
        x = et.fromstring(x)

    if isinstance(y, str):
        y = et.fromstring(y)

    if x.tag != y.tag:
        return False

    if x.attrib != y.attrib:
        return False

    if (x.text or "").strip() != (y.text or "").strip():
        return False

    x_children = list(x)
    y_children = list(y)

    if len(x_children) != len(y_children):
        return False

    return all(xml_equal(x, y) for x, y in zip(x_children, y_children))


def assert_xml_equal(x, y):
    if xml_equal(x, y):
        return True

    if not isinstance(x, str):
        x = et.tostring(x)

    if not isinstance(y, str):
        y = et.tostring(y)

    raise AssertionError(f"{x} != {y}")


@fixture(autouse=True)
def module():
    with patch.multiple(
        "ansible.module_utils.basic.AnsibleModule",
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


@fixture
def instance():
    with patch("jenkins.Jenkins", autospec=True) as instance:
        yield instance


@fixture
def get_instance(instance):
    with patch(
        "ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_jenkins_instance",
        autospec=True,
    ) as mock:
        mock.return_value = instance
        yield mock


def test_get_jenkins_instance_with_user_and_token(instance):
    instance.node_exists.return_value = False

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
            "url": "https://localhost:8080",
            "user": "admin",
            "token": "password",
        }
    ):
        with pytest.raises(AnsibleExitJson):
            jenkins_node.main()

    assert instance.call_args == call("https://localhost:8080", "admin", "password")


def test_get_jenkins_instance_with_user(instance):
    instance.node_exists.return_value = False

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
            "url": "https://localhost:8080",
            "user": "admin",
        }
    ):
        with pytest.raises(AnsibleExitJson):
            jenkins_node.main()

    assert instance.call_args == call("https://localhost:8080", "admin")


def test_get_jenkins_instance_with_no_credential(instance):
    instance.node_exists.return_value = False

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
            "url": "https://localhost:8080",
        }
    ):
        with pytest.raises(AnsibleExitJson):
            jenkins_node.main()

    assert instance.call_args == call("https://localhost:8080")


PRESENT_STATES = ["present", "enabled", "disabled"]


@mark.parametrize(["state"], [param(state) for state in PRESENT_STATES])
def test_state_present_when_absent(get_instance, instance, state):
    instance.node_exists.return_value = False
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": state,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.create_node.call_args == call("my-node", launcher=jenkins.LAUNCHER_SSH)

    assert result.value.args[0]["created"] is True
    assert result.value.args[0]["changed"] is True


@mark.parametrize(["state"], [param(state) for state in PRESENT_STATES])
def test_state_present_when_absent_check_mode(get_instance, instance, state):
    instance.node_exists.return_value = False
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": state,
            "_ansible_check_mode": True,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.create_node.called

    assert result.value.args[0]["created"] is True
    assert result.value.args[0]["changed"] is True


@mark.parametrize(["state"], [param(state) for state in PRESENT_STATES])
def test_state_present_when_absent_redirect_auth_error_handled(get_instance, instance, state):
    instance.node_exists.side_effect = [False, True]
    instance.get_node_config.return_value = "<slave />"
    instance.create_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": state,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.create_node.call_args == call("my-node", launcher=jenkins.LAUNCHER_SSH)

    assert result.value.args[0]["created"] is True
    assert result.value.args[0]["changed"] is True


@mark.parametrize(["state"], [param(state) for state in PRESENT_STATES])
def test_state_present_when_absent_other_error_raised(get_instance, instance, state):
    instance.node_exists.side_effect = [False, False]
    instance.get_node_config.return_value = "<slave />"
    instance.create_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": state,
        }
    ):
        with raises(AnsibleFailJson) as result:
            jenkins_node.main()

    assert instance.create_node.call_args == call("my-node", launcher=jenkins.LAUNCHER_SSH)

    assert "Create node failed" in str(result.value.args[0])


def test_state_present_when_present(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.create_node.called

    assert result.value.args[0]["created"] is False
    assert result.value.args[0]["changed"] is False


def test_state_absent_when_present(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.delete_node.call_args == call("my-node")

    assert result.value.args[0]["deleted"] is True
    assert result.value.args[0]["changed"] is True


def test_state_absent_when_present_check_mode(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
            "_ansible_check_mode": True,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.delete_node.called

    assert result.value.args[0]["deleted"] is True
    assert result.value.args[0]["changed"] is True


def test_state_absent_when_present_redirect_auth_error_handled(get_instance, instance):
    instance.node_exists.side_effect = [True, False]
    instance.get_node_config.return_value = "<slave />"
    instance.delete_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.delete_node.call_args == call("my-node")

    assert result.value.args[0]["deleted"] is True
    assert result.value.args[0]["changed"] is True


def test_state_absent_when_present_other_error_raised(get_instance, instance):
    instance.node_exists.side_effect = [True, True]
    instance.get_node_config.return_value = "<slave />"
    instance.delete_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
        }
    ):
        with raises(AnsibleFailJson) as result:
            jenkins_node.main()

    assert instance.delete_node.call_args == call("my-node")

    assert "Delete node failed" in str(result.value.args[0])


def test_state_absent_when_absent(get_instance, instance):
    instance.node_exists.return_value = False
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "absent",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.delete_node.called

    assert result.value.args[0]["deleted"] is False
    assert result.value.args[0]["changed"] is False


def test_state_enabled_when_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {"offline": True}

    with set_module_args(
        {
            "name": "my-node",
            "state": "enabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.enable_node.call_args == call("my-node")

    assert result.value.args[0]["enabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_enabled_when_offline_check_mode(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {"offline": True}

    with set_module_args(
        {
            "name": "my-node",
            "state": "enabled",
            "_ansible_check_mode": True,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.enable_node.called

    assert result.value.args[0]["enabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_enabled_when_offline_redirect_auth_error_handled(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.side_effect = [{"offline": True}, {"offline": False}]
    instance.enable_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "enabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.enable_node.call_args == call("my-node")

    assert result.value.args[0]["enabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_enabled_when_offline_other_error_raised(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.side_effect = [{"offline": True}, {"offline": True}]
    instance.enable_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "enabled",
        }
    ):
        with raises(AnsibleFailJson) as result:
            jenkins_node.main()

    assert instance.enable_node.call_args == call("my-node")

    assert "Enable node failed" in str(result.value.args[0])


def test_state_enabled_when_not_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {"offline": False}

    with set_module_args(
        {
            "name": "my-node",
            "state": "enabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.enable_node.called

    assert result.value.args[0]["enabled"] is False
    assert result.value.args[0]["changed"] is False


def test_state_disabled_when_not_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": False,
        "offlineCauseReason": "",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.disable_node.call_args == call("my-node", "")

    assert result.value.args[0]["disabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_disabled_when_not_offline_redirect_auth_error_handled(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.side_effect = [
        {
            "offline": False,
            "offlineCauseReason": "",
        },
        {
            "offline": True,
            "offlineCauseReason": "",
        },
    ]
    instance.disable_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.disable_node.call_args == call("my-node", "")

    assert result.value.args[0]["disabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_disabled_when_not_offline_other_error_raised(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.side_effect = [
        {
            "offline": False,
            "offlineCauseReason": "",
        },
        {
            "offline": False,
            "offlineCauseReason": "",
        },
    ]
    instance.disable_node.side_effect = jenkins.JenkinsException

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
        }
    ):
        with raises(AnsibleFailJson) as result:
            jenkins_node.main()

    assert instance.disable_node.call_args == call("my-node", "")

    assert "Disable node failed" in str(result.value.args[0])


def test_state_disabled_when_not_offline_check_mode(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": False,
        "offlineCauseReason": "",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
            "_ansible_check_mode": True,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.disable_node.called

    assert result.value.args[0]["disabled"] is True
    assert result.value.args[0]["changed"] is True


def test_state_disabled_when_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": True,
        "offlineCauseReason": "",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.disable_node.called

    assert result.value.args[0]["disabled"] is False
    assert result.value.args[0]["changed"] is False


def test_configure_num_executors_when_not_configured(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "num_executors": 3,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.reconfig_node.call_args[0][0] == "my-node"
    assert_xml_equal(
        instance.reconfig_node.call_args[0][1],
        """
<slave>
  <numExecutors>3</numExecutors>
</slave>
""",
    )

    assert result.value.args[0]["configured"] is True
    assert result.value.args[0]["changed"] is True


def test_configure_num_executors_when_not_equal(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = """
<slave>
  <numExecutors>3</numExecutors>
</slave>
"""

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "num_executors": 2,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert_xml_equal(
        instance.reconfig_node.call_args[0][1],
        """
<slave>
  <numExecutors>2</numExecutors>
</slave>
""",
    )

    assert result.value.args[0]["configured"] is True
    assert result.value.args[0]["changed"] is True


def test_configure_num_executors_when_equal(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = """
<slave>
  <numExecutors>2</numExecutors>
</slave>
"""

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "num_executors": 2,
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.reconfig_node.called

    assert result.value.args[0]["configured"] is False
    assert result.value.args[0]["changed"] is False


def test_configure_labels_when_not_configured(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "labels": [
                "a",
                "b",
                "c",
            ],
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.reconfig_node.call_args[0][0] == "my-node"
    assert_xml_equal(
        instance.reconfig_node.call_args[0][1],
        """
<slave>
  <label>a b c</label>
</slave>
""",
    )

    assert result.value.args[0]["configured"] is True
    assert result.value.args[0]["changed"] is True


def test_configure_labels_when_not_equal(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = """
<slave>
  <label>a b c</label>
</slave>
"""

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "labels": [
                "a",
                "z",
                "c",
            ],
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.reconfig_node.call_args[0][0] == "my-node"
    assert_xml_equal(
        instance.reconfig_node.call_args[0][1],
        """
<slave>
  <label>a z c</label>
</slave>
""",
    )

    assert result.value.args[0]["configured"] is True
    assert result.value.args[0]["changed"] is True


def test_configure_labels_when_equal(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = """
<slave>
  <label>a b c</label>
</slave>
"""

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "labels": [
                "a",
                "b",
                "c",
            ],
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.reconfig_node.called

    assert result.value.args[0]["configured"] is False
    assert result.value.args[0]["changed"] is False


def test_configure_labels_fail_when_contains_space(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"

    with set_module_args(
        {
            "name": "my-node",
            "state": "present",
            "labels": [
                "a error",
            ],
        }
    ):
        with raises(AnsibleFailJson):
            jenkins_node.main()

    assert not instance.reconfig_node.called


@mark.parametrize(["state"], [param(state) for state in ["enabled", "present", "absent"]])
def test_raises_error_if_offline_message_when_state_not_disabled(get_instance, instance, state):
    with set_module_args(
        {
            "name": "my-node",
            "state": state,
            "offline_message": "This is a message...",
        }
    ):
        with raises(AnsibleFailJson):
            jenkins_node.main()

    assert not instance.disable_node.called


def test_set_offline_message_when_equal(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": True,
        "offlineCauseReason": "This is an old message...",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
            "offline_message": "This is an old message...",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.disable_node.called

    assert result.value.args[0]["changed"] is False


def test_set_offline_message_when_not_equal_not_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": False,
        "offlineCauseReason": "This is an old message...",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
            "offline_message": "This is a new message...",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert instance.disable_node.call_args == call("my-node", "This is a new message...")

    assert result.value.args[0]["changed"] is True


# Not calling disable_node when already offline seems like a sensible thing to do.
# However, we need to call disable_node to set the offline message, so check that
# we do even when already offline.
def test_set_offline_message_when_not_equal_offline(get_instance, instance):
    instance.node_exists.return_value = True
    instance.get_node_config.return_value = "<slave />"
    instance.get_node_info.return_value = {
        "offline": True,
        "offlineCauseReason": "This is an old message...",
    }

    with set_module_args(
        {
            "name": "my-node",
            "state": "disabled",
            "offline_message": "This is a new message...",
        }
    ):
        with raises(AnsibleExitJson) as result:
            jenkins_node.main()

    assert not instance.disable_node.called

    assert result.value.args[0]["changed"] is False


class TestConfigureRemoteRootDir:
    @fixture(autouse=True)
    def node_exists(self, get_instance, instance):
        instance.node_exists.return_value = True

    def test_configure_remote_root_dir_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <remoteFS>/var/lib/jenkins</remoteFS>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "remote_root_dir": "/custom/agent/dir",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <remoteFS>/custom/agent/dir</remoteFS>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_remote_root_dir_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <remoteFS>/custom/agent/dir</remoteFS>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "remote_root_dir": "/custom/agent/dir",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_remote_fs_alias(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <remoteFS>/var/lib/jenkins</remoteFS>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "remote_fs": "/aliased/path",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <remoteFS>/aliased/path</remoteFS>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True


class TestConfigureDescription:
    @fixture(autouse=True)
    def node_exists(self, get_instance, instance):
        instance.node_exists.return_value = True

    def test_configure_description_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <description>Old description</description>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "description": "New description",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <description>New description</description>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_description_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <description>My agent description</description>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "description": "My agent description",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False


class TestConfigureMode:
    @fixture(autouse=True)
    def node_exists(self, get_instance, instance):
        instance.node_exists.return_value = True

    def test_configure_mode_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <mode>NORMAL</mode>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "mode": "exclusive",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <mode>EXCLUSIVE</mode>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_mode_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <mode>EXCLUSIVE</mode>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "mode": "exclusive",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False


class TestConfigureLaunchers:
    @fixture(autouse=True)
    def node_exists(self, get_instance, instance):
        instance.node_exists.return_value = True

    def test_configure_inbound_launcher(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher" />
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launcher": "inbound",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            f"""
<slave>
  {jenkins_node.InboundLauncherConfig.TEMPLATE}
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_command_launcher(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher" />
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launcher": "command",
                "launch_command": {
                    "command": "/usr/local/bin/launch-agent.sh",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.slaves.CommandLauncher">
    <agentCommand>/usr/local/bin/launch-agent.sh</agentCommand>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_create_node_with_inbound_launcher(self, get_instance, instance):
        instance.node_exists.return_value = False
        instance.get_node_config.return_value = "<slave />"

        with set_module_args(
            {
                "name": "inbound-node",
                "state": "present",
                "launcher": "inbound",
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert instance.create_node.call_args == call("inbound-node", launcher=jenkins.LAUNCHER_JNLP)
        assert result.value.args[0]["created"] is True


class TestConfigureLaunchSSH:
    @fixture(autouse=True)
    def node_exists(self, get_instance, instance):
        instance.node_exists.return_value = True

    def test_configure_when_launcher_is_not_ssh(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.DummyLauncher" />
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {},
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            f"""
<slave>
  {jenkins_node.SSHLauncherConfig.TEMPLATE}
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_when_not_configured(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher" />
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {},
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_port_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <port>22</port>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "port": 23,
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <port>23</port>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_port_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <port>22</port>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "port": 22,
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_when_unset(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host": "my-host.test",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <host>my-host.test</host>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <host>my-host.test</host>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host": "my-host.test",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <host>my-host.test</host>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host": "other-host.test",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <host>other-host.test</host>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_credentials_id_when_unset(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "credentials_id": "my-credentials-id",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <credentialsId>my-credentials-id</credentialsId>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_credentials_id_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <credentialsId>my-credentials-id</credentialsId>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "credentials_id": "my-credentials-id",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_credentials_id_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <credentialsId>my-credentials-id</credentialsId>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "credentials_id": "other-credentials-id",
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <credentialsId>other-credentials-id</credentialsId>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_known_hosts_when_host_key_verify_is_not_known_hosts(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.DummyKeyVerificationStrategy" />
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_known_hosts": True,
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy" />
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_none_when_host_key_verify_is_not_none(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.DummyKeyVerificationStrategy" />
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_none": True,
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy" />
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_trusted_when_host_key_verify_is_not_trusted(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.DummyKeyVerificationStrategy" />
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_trusted": {},
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            f"""
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    {jenkins_node.TrustedSSHHostKeyVerifyConfig.TEMPLATE}
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_trusted_when_not_configured(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy" />
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_trusted": {},
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_key_verify_trusted_allow_initial_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">
      <requireInitialManualTrust>false</requireInitialManualTrust>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_trusted": {
                        "allow_initial": False,
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_key_verify_trusted_allow_initial_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">
      <requireInitialManualTrust>false</requireInitialManualTrust>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_trusted": {
                        "allow_initial": True,
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">
      <requireInitialManualTrust>true</requireInitialManualTrust>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_provided_when_host_key_verify_is_not_provided(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.DummyKeyVerificationStrategy" />
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_provided": {
                        "algorithm": "dummy-algorithm",
                        "key": "dummy-key",
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_provided_algorithm_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_provided": {
                        "algorithm": "dummy-algorithm",
                        "key": "dummy-key",
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_key_verify_provided_algorithm_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_provided": {
                        "algorithm": "other-dummy-algorithm",
                        "key": "dummy-key",
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>other-dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True

    def test_configure_host_key_verify_provided_key_when_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_provided": {
                        "algorithm": "dummy-algorithm",
                        "key": "dummy-key",
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert not instance.reconfig_node.called
        assert result.value.args[0]["configured"] is False

    def test_configure_host_key_verify_provided_key_when_not_equal(self, instance):
        instance.get_node_config.return_value = """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
"""
        with set_module_args(
            {
                "name": "my-node",
                "state": "present",
                "launch_ssh": {
                    "host_key_verify_provided": {
                        "algorithm": "dummy-algorithm",
                        "key": "other-dummy-key",
                    },
                },
            }
        ):
            with raises(AnsibleExitJson) as result:
                jenkins_node.main()

        assert_xml_equal(
            instance.reconfig_node.call_args[0][1],
            """
<slave>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
      <key>
        <algorithm>dummy-algorithm</algorithm>
        <key>other-dummy-key</key>
      </key>
    </sshHostKeyVerificationStrategy>
  </launcher>
</slave>
""",
        )
        assert result.value.args[0]["configured"] is True
