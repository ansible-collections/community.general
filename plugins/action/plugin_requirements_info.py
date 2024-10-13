# -*- coding: utf-8 -*-
# Copyright (c) 2023, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common._collections_compat import Mapping
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible.plugins.loader import connection_loader

from ansible.constants import DOCUMENTABLE_PLUGINS

from ansible.module_utils.common.validation import (
    check_type_bool,
    check_type_dict,
    check_type_list,
    check_type_str,
)

from ansible_collections.community.general.plugins.plugin_utils._dependencies import (
    LoadingError,
    UnknownPlugin,
    UnknownPluginType,
    retrieve_plugin_dependencies,
    get_needed_facts,
    get_used_facts,
    Requirements,
    RequirementFinder,
)

display = Display()


class TimedOutException(Exception):
    pass


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset((
        'plugins',
        'modules_on_remote',
    ))

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)

    def _load_facts(self, task_vars, hostname):
        display.vvv('<{host}> {action}: running setup module to get facts'.format(host=hostname, action=self._task.action))
        module_output = self._execute_module(
            task_vars=task_vars,
            module_name='ansible.legacy.setup',
            module_args={'gather_subset': 'min'})
        if module_output.get('failed', False):
            raise AnsibleError('Failed to determine system distribution. {0}, {1}'.format(
                to_native(module_output['module_stdout']).strip(),
                to_native(module_output['module_stderr']).strip()))
        result = {}
        used_facts = get_used_facts()
        for k, v in module_output['ansible_facts'].items():
            if k.startswith('ansible_'):
                k = k[8:]
            if k in used_facts:
                result[k] = v
        return result

    def _extract_facts(self, task_vars):
        if not isinstance(task_vars, Mapping):
            return None
        if 'ansible_facts' not in task_vars:
            return None
        ansible_facts = task_vars['ansible_facts']
        needed_facts = get_needed_facts()
        if any(k not in ansible_facts for k in needed_facts):
            return None
        used_facts = get_used_facts()
        return {k: ansible_facts[k] for k in used_facts if k in ansible_facts}

    def _get_facts(self, local, task_vars, hostname):
        if local and self._connection.transport != 'local':
            format_vars = dict(host=hostname, action=self._task.action)
            result = self._extract_facts({'ansible_facts': self._templar.template("{{hostvars['localhost']['ansible_facts']}}")})
            if result:
                display.vvv('<{host}> {action}: already have local facts'.format(**format_vars))
                return result
            original_connection = self._connection
            try:
                display.vvv('<{host}> {action}: getting hold of local connection...'.format(**format_vars))
                self._connection = connection_loader.get('ansible.legacy.local', self._play_context)
                display.vvv('<{host}> {action}: retrieving local facts...'.format(**format_vars))
                return self._load_facts(task_vars, hostname)
            finally:
                self._connection = original_connection
        elif not local and self._connection.transport == 'local':
            raise AnsibleError('Cannot retrieve remote facts if connection is local')

        format_vars = dict(host=hostname, action=self._task.action, local_remote='local' if local else 'remote')
        result = self._extract_facts(task_vars)
        if result:
            display.vvv('<{host}> {action}: already have {local_remote} facts'.format(**format_vars))
            return result
        display.vvv('<{host}> {action}: retrieving {local_remote} facts...'.format(**format_vars))
        return self._load_facts(task_vars, hostname)

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True

        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)

        if result.get('skipped', False) or result.get('failed', False):
            return result

        try:
            if 'plugins' not in self._task.args:
                raise TypeError('missing required arguments: plugins')
            modules_on_remote = check_type_bool(self._task.args.get('modules_on_remote', True))
            plugins = []
            for plugin in [check_type_dict(plug) for plug in check_type_list(self._task.args['plugins'])]:
                if 'name' not in plugin:
                    raise TypeError('missing required arguments: name found in plugins')
                plugin_type = check_type_str(plugin.get('type', 'module'))
                if plugin_type not in DOCUMENTABLE_PLUGINS:
                    raise TypeError('unknown plugin type %s' % plugin_type)
                plugins.append({
                    'name': check_type_str(plugin.get('name')),
                    'type': plugin_type,
                })
        except TypeError as exc:
            result['failed'] = True
            result['msg'] = to_native(exc)
            return result

        hostname = task_vars.get('inventory_hostname')

        need_remote_facts = modules_on_remote and any(plugin['type'] == 'module' for plugin in plugins)
        need_local_facts = (plugins and not modules_on_remote) or any(plugin['type'] != 'module' for plugin in plugins)
        if self._connection.transport == 'local':
            need_remote_facts = False
            need_local_facts = bool(plugins)

        controller_ansible_facts = self._get_facts(local=True, task_vars=task_vars, hostname=hostname) if need_local_facts else {}
        remote_ansible_facts = self._get_facts(local=False, task_vars=task_vars, hostname=hostname) if need_remote_facts else {}

        try:
            requirement_finder = RequirementFinder(self._templar, controller_ansible_facts, remote_ansible_facts)
            all_deps = Requirements()
            for plugin in plugins:
                display.vvv('<{host}> {action}: retrieving installable requirements of {type} {name}'.format(host=hostname, action=self._task.action, **plugin))
                installable_requirements = retrieve_plugin_dependencies(plugin['name'], plugin['type'])
                deps = requirement_finder.find(installable_requirements, modules_for_remote=modules_on_remote and self._connection.transport != 'local')
                all_deps.merge(deps)
            result['python'] = sorted(all_deps.python)
            result['system'] = sorted(all_deps.system)
            result['changed'] = False
            return result
        except UnknownPluginType as exc:
            result['failed'] = True
            result['msg'] = 'Unknown plugin type: %s' % to_native(exc)
            return result
        except UnknownPlugin as exc:
            result['failed'] = True
            result['msg'] = 'Unknown plugin: %s' % to_native(exc)
            return result
        except LoadingError as exc:
            result['failed'] = True
            result['msg'] = to_native(exc)
            return result
