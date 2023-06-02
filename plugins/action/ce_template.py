#
# Copyright 2015 Peter Sprygada <psprygada@ansible.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import time
import glob
from ansible.module_utils.six.moves.urllib.parse import urlsplit

from ansible.module_utils._text import to_text
from ansible_collections.community.general.plugins.action.ce import ActionModule as _ActionModule


class ActionModule(_ActionModule):

    def run(self, tmp=None, task_vars=None):

        try:
            self._handle_template()
        except (ValueError, AttributeError) as exc:
            return dict(failed=True, msg=exc.message)

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        if self._task.args.get('backup') and result.get('__backup__'):
            # User requested backup and no error occurred in module.
            # NOTE: If there is a parameter error, __backup__ key may not be in results.
            self._write_backup(task_vars['inventory_hostname'], result['__backup__'])

        if '__backup__' in result:
            del result['__backup__']

        return result

    def _get_working_path(self):
        cwd = self._loader.get_basedir()
        if self._task._role is not None:
            cwd = self._task._role._role_path
        return cwd

    def _write_backup(self, host, contents):
        backup_path = self._get_working_path() + '/backup'
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        for fn in glob.glob('%s/%s*' % (backup_path, host)):
            os.remove(fn)
        tstamp = time.strftime("%Y-%m-%d@%H:%M:%S", time.localtime(time.time()))
        filename = '%s/%s_config.%s' % (backup_path, host, tstamp)
        open(filename, 'w').write(contents)

    def _handle_template(self):
        src = self._task.args.get('src')
        if not src:
            raise ValueError('missing required arguments: src')

        working_path = self._get_working_path()

        if os.path.isabs(src) or urlsplit(src).scheme:
            source = src
        else:
            source = self._loader.path_dwim_relative(working_path, 'templates', src)
            if not source:
                source = self._loader.path_dwim_relative(working_path, src)

        if not os.path.exists(source):
            return

        try:
            with open(source, 'r') as f:
                template_data = to_text(f.read())
        except IOError:
            return dict(failed=True, msg='unable to load src file')

        # Create a template search path in the following order:
        # [working_path, self_role_path, dependent_role_paths, dirname(source)]
        searchpath = [working_path]
        if self._task._role is not None:
            searchpath.append(self._task._role._role_path)
            if hasattr(self._task, "_block:"):
                dep_chain = self._task._block.get_dep_chain()
                if dep_chain is not None:
                    for role in dep_chain:
                        searchpath.append(role._role_path)
        searchpath.append(os.path.dirname(source))
        with self._templar.set_temporary_context(searchpath=searchpath):
            self._task.args['src'] = self._templar.template(template_data)
