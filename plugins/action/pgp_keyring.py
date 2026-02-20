# Copyright: (c) 2025–2026, Eero Aaltonen
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import tempfile

from ansible.errors import AnsibleActionFail, AnsibleError
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.action import ActionBase

try:
    import pgpy
except ImportError as imp_exc:
    PGPY_IMPORT_ERROR = imp_exc
else:
    PGPY_IMPORT_ERROR = None


class ActionModule(ActionBase):

    TRANSFERS_FILES = True

    def run(self, tmp=None, task_vars=None):
        """ Install PGP keyrings in binary format """

        if PGPY_IMPORT_ERROR:
            raise AnsibleError('PGPym~=0.6.1 or apt python3-pgpy must be installed to use pgp_keyring plugin') \
                from PGPY_IMPORT_ERROR

        if task_vars is None:
            task_vars = dict()

        validation_result, new_module_args = self.validate_argument_spec(
            argument_spec=dict(
                src=dict(type='str', required=True),
                dest=dict(type='str', required=True),
                follow=dict(type='bool', default=False)
            )
        )

        super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        # assign to local vars for ease of use
        source = new_module_args['src']
        dest = new_module_args['dest']
        follow = new_module_args['follow']

        try:
            try:
                # find in expected paths
                source = self._find_needle('files', source)
            except AnsibleError as e:
                raise AnsibleActionFail(to_text(e))

            try:
                key, po = pgpy.PGPKey.from_file(source)
            except FileNotFoundError as e:
                raise AnsibleActionFail("could not find src=%s, %s" % (source, to_text(e)))
            except Exception as e:
                raise AnsibleActionFail("%s: %s" % (type(e).__name__, to_text(e)))

            new_task = self._task.copy()

            with tempfile.NamedTemporaryFile('wb', delete=True) as f:
                f.write(bytes(key))
                f.flush()

                new_task.args.update(
                    dict(
                        src=f.file.name,
                        dest=dest,
                        follow=follow,
                    ),
                )
                # call with ansible.legacy prefix to eliminate collisions with collections while still allowing local override
                copy_action = self._shared_loader_obj.action_loader.get(
                    'ansible.legacy.copy',
                    task=new_task,
                    connection=self._connection,
                    play_context=self._play_context,
                    loader=self._loader,
                    templar=self._templar,
                    shared_loader_obj=self._shared_loader_obj)
                return copy_action.run(task_vars=task_vars)

        finally:
            self._remove_tmp_path(self._connection._shell.tmpdir)
