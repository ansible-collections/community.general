import pytest
from ansible.module_utils import basic

from ansible_collections.community.general.plugins.modules import decompress
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleFailJson, set_module_args, \
    fail_json, exit_json


class TestDecompress:
    @pytest.fixture(autouse=True)
    def common(self, mocker):
        self.mock_module = mocker.patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json
        )

    def test_fail(self):
        with pytest.raises(AnsibleFailJson) as e:
            set_module_args({})
            decompress.main()
        assert e.match("missing required arguments: dest, src")
