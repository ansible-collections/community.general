# Copyright: (c) 2019, Philip Bove <phil@bove.online>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text
from ansible.module_utils.six import string_types
import ansible_collections.community.general.plugins.module_utils.semodule as semodule
from ansible.utils.hashing import checksum
import traceback


class ActionModule(ActionBase):

    def _module_exist(self, name, semodule_info):
        if name in semodule_info:
            return True
        return False

    def _get_semodule_info(self):
        result = self._low_level_execute_command('semodule -l')
        if result['rc'] != 0:
            raise AnsibleError('semodule command failed')
        return to_text(result['stdout'])

    def _remove_module(self, name):
        result = self._low_level_execute_command('semodule -r {module}'.format(module=name))
        if result['rc'] != 0:
            raise AnsibleError('failed to remove policy')

    def _check_mode(self, changed, policy_def, result):
        if self._play_context.check_mode:
            result['changed'] = changed
            return result
        return None

    def _copy_te_file(self, file, dest, task_vars):
        local_checksum = checksum(file)
        remote_path = self._transfer_file(file, dest)
        self._fixup_perms2((self._connection._shell.tmpdir, remote_path))
        remote_checksum = self._execute_remote_stat(dest, all_vars=task_vars, follow=False)
        if local_checksum != remote_checksum['checksum']:
            raise AnsibleError('.te file copy failed, checksum does not match')

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        try:
            self._make_tmp_path()
            new_module = self._task.copy()
            new_module_args = self._task.args.copy()
            state = self._task.args.get('state', 'present')
            if state not in ['present', 'absent']:
                raise AnsibleError('state can only be present or absent')
            file_name = self._task.args.get('src', None)
            if not isinstance(file_name, string_types):
                raise AnsibleError('src parameter cannot be null')
            force = self._task.args.get('force', None)
            tmp_src = self._connection._shell.join_path(self._connection._shell.tmpdir, 'source')
            te_file = self._find_needle('files', file_name)
            try:
                policy_def = semodule.parse_module_info(semodule.read_te_file(te_file))
            except IndexError:
                raise AnsibleError('Module is missing module definition line')
            semodule_info = self._get_semodule_info()
            module_installed = self._module_exist(policy_def['name'], semodule_info)
            if state == 'present':
                if not module_installed or force:
                    check_res = self._check_mode(True, policy_def, result)
                    if check_res:
                        return check_res
                    self._copy_te_file(te_file, tmp_src, task_vars)
                    new_module_args.update(dict(src=tmp_src))
                    module_return = self._execute_module(module_name='semodule', module_args=new_module_args, task_vars=task_vars)
                    result.update(module_return)
            # no need to copy extra files over to target
            # when we can remove it from here
            elif state == 'absent':
                if module_installed:
                    check_res = self._check_mode(True, policy_def['name'], result)
                    if check_res:
                        return check_res
                    self._remove_module(policy_def['name'])
                    result['changed'] = True
                else:
                    result['changed'] = False
        except AnsibleError as error:
            result['failed'] = True
            result['msg'] = to_text(error)
            result['exception'] = traceback.format_exc()
        finally:
            # clean up temp path
            self._remove_tmp_path(self._connection._shell.tmpdir)
        return result
