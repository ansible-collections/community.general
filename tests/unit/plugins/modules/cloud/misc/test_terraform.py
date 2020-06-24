# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from ansible_collections.community.general.plugins.modules.cloud.misc import terraform
import mock
import os

from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def fail_json(*args, **kwargs):
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


def exit_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False

    raise AnsibleExitJson(kwargs)


def test_state_args():
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    with pytest.raises(AnsibleFailJson):
        terraform._state_args(module, '/rrrr')
    module.fail_json.assert_called()


def test_returned_value_state_args(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.txt")
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    value = terraform._state_args(module, test_file.dirname)
    assert value == ['-state', test_file.dirname]


def test_return_empty_list_state_args():
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    value = terraform._state_args(module, '')
    assert value == []


def test_fail_json_preflight_validation_with_project_path_not_provided():
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    with pytest.raises(AnsibleFailJson):
        terraform.preflight_validation(module, '', '/rri')

    module.fail_json.assert_called()


def test_preflight_validation_with_arguments_satisfied_but_with_error_code_returned(tmpdir):
    test_project_path = tmpdir.mkdir("project-path")
    test_file = test_project_path.join("test_file.txt")
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (1, '', '')
    with pytest.raises(AnsibleFailJson) as result:
        terraform.preflight_validation(module, '/', test_file.dirname, [''])
    module.fail_json.assert_called()


def test_preflight_validation_with_arguments_satisfied_without_error_code(tmpdir):
    test_project_path = tmpdir.mkdir("project-path")
    test_file = test_project_path.join("test_file.txt")
    module = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (0, '', '')
    terraform.preflight_validation(module, '/', test_file.dirname, [''])

    module.fail_json.assert_not_called()


def test_get_workspace_context(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.txt")
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    out = '''
    default
    * turntabl
    office
    '''
    module.run_command.return_value = (0, out, '')
    returned_results = terraform.get_workspace_context(module, test_file.dirname, test_file.dirname)
    expected_results = {'current': 'turntabl', 'all': ['default', 'office']}
    assert returned_results == expected_results


def test_build_plan_with_state_planned(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (0, '', '')
    returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'planned', full_path)
    print(returned_tuple_results)
    assert returned_tuple_results == (full_path, False, '', '', [test_file.dirname, 'plan', '-input=false',
                                                                 '-no-color', '-detailed-exitcode', '-out', full_path])


def test_build_plan_with_state_not_planned_and_return_code_zero(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (0, '', '')
    returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'present', full_path)
    assert returned_tuple_results == (full_path, False, '', '', [test_file.dirname])


def test_build_plan_with_state_planned_with_returned_code_one(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    module.run_command.return_value = (1, '', '')
    with pytest.raises(AnsibleFailJson) as result:
        returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'planned', full_path)
    module.fail_json.assert_called()


def test_build_plan_with_state_planned_with_return_code_two(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (2, '', '')
    returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'planned', full_path)
    assert returned_tuple_results == (full_path, True, '', '', [test_file.dirname, 'plan', '-input=false', '-no-color',
                                                                '-detailed-exitcode', '-out', full_path])


def test_build_plan_with_state_not_planned_with_return_code_two(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.run_command.return_value = (2, '', '')
    returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'absent', full_path)
    assert returned_tuple_results == (full_path, True, '', '', [test_file.dirname])


def test_build_plan_with_return_code_greater_than_two(tmpdir):
    test_temp_folder_for_project_path = tmpdir.mkdir("project-path")
    test_file = test_temp_folder_for_project_path.join("test_file.tfplan")
    full_path = os.path.join(test_file.dirname, test_file.basename)
    module = mock.MagicMock()
    module.run_command = mock.MagicMock()
    module.fail_json.side_effect = AnsibleFailJson(Exception)
    module.run_command.return_value = (3, '', '')
    with pytest.raises(AnsibleFailJson) as result:
        returned_tuple_results = terraform.build_plan(module, [test_file.dirname], test_file.dirname, [], '', [], 'absent', full_path)
    module.fail_json.assert_called()


def test_get_plan_file_name_without_extension():
    returned_result = terraform.get_plan_file_name_without_extension('./heroku-test/tmpNY45T.tfplan')
    expected_result = 'tmpNY45T'
    assert returned_result == expected_result


def test_terraform_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        terraform.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']
    assert 'project_path' in json.loads(out)['msg']
