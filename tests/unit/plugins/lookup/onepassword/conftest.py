import pytest

from ansible_collections.community.general.plugins.lookup.onepassword import OnePass


@pytest.fixture
def fake_op(mocker):
    def _fake_op(version):
        mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase.get_current_version", return_value=version)
        op = OnePass(None, None, None, None, None)
        op._config._config_file_path = "/home/jin/.op/config"
        mocker.patch.object(op._cli, "_run")

        return op

    return _fake_op


@pytest.fixture
def opv1(fake_op):
    return fake_op("1.17.2")


@pytest.fixture
def opv2(fake_op):
    return fake_op("2.27.2")
