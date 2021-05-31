from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.modules.packaging.os import pacman_key
import pytest
import json


@pytest.fixture
def patch_pacman_key_calls(mocker):
    get_bin_path = mocker.patch(
        'ansible.module_utils.basic.AnsibleModule.get_bin_path',
        return_value="/mocked/path",
    )


TEST_FAILING_PARAMS = [
    # state: present, id: absent
    [
        {
            'state': 'present',
        },
        {
            'id': 'state_present_id_missing',
            'msg': 'missing required arguments: id',
        },
    ],
    # state: present, required parameters: missing
    [
        {
            'state': 'present',
            'id': '0xDOESNTMATTER',
        },
        {
            'id': 'state_present_required_param_missing',
            'msg': 'state is present but any of the following are missing: data, file, url, keyserver',
        },
    ],
    # state: present, id: invalid (not full-length)
    [
        {
            # default state: present
            'id': '0xDOESNTMATTER',
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_present_id_invalid',
            'msg': 'identifier is not full-length: DOESNTMATTER',
        },
    ],
    # state: present, fingerprint: invalid (not hexadecimal)
    [
        {
            'state': 'present',
            'id': '01234567890ABCDE01234567890ABCDE12345678',
            'fingerprint': '01234567890ABCDE01234567890ABCDE1234567M',
            'data': 'FAKEDATA',
        },
        {
            'id': 'state_present_fpr_invalid',
            'msg': 'identifier is not hexadecimal: 01234567890ABCDE01234567890ABCDE1234567M',
        },
    ],
    # state: absent, id: absent
    [
        {
            'state': 'absent',
        },
        {
            'id': 'state_absent_id_missing',
            'msg': 'missing required arguments: id',
        },
    ],
]


@pytest.mark.parametrize(
    'patch_ansible_module, expected',
    TEST_FAILING_PARAMS,
    ids=[item[1]['id'] for item in TEST_FAILING_PARAMS],
    indirect=['patch_ansible_module']
)
@pytest.mark.usefixtures('patch_ansible_module')
def test_failing_params(mocker, capfd, patch_pacman_key_calls, expected):
    # invoke module
    with pytest.raises(SystemExit):
        pacman_key.main()

    # capture std{out,err}
    out, err = capfd.readouterr()
    results = json.loads(out)
    print(results)

    # assertion time!
    assert 'failed' in results
    if 'msg' in results:
        assert results['msg'] == expected['msg']
