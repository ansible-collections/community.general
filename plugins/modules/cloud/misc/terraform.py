#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Ryan Scott Brown <ryansb@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: terraform
short_description: Manages a Terraform deployment (and plans)
description:
     - Provides support for deploying resources with Terraform and pulling
       resource information back into Ansible.
options:
  state:
    choices: ['planned', 'present', 'absent']
    description:
      - Goal state of given stage/project
    default: present
  binary_path:
    description:
      - The path of a terraform binary to use, relative to the 'service_path'
        unless you supply an absolute path.
  project_path:
    description:
      - The path to the root of the Terraform directory with the
        vars.tf/main.tf/etc to use.
    required: true
  workspace:
    description:
      - The terraform workspace to work with.
    default: default
  purge_workspace:
    description:
      - Only works with state = absent
      - If true, the workspace will be deleted after the "terraform destroy" action.
      - The 'default' workspace will not be deleted.
    default: false
    type: bool
  plan_file:
    description:
      - The path to an existing Terraform plan file to apply. If this is not
        specified, Ansible will build a new TF plan and execute it.
        Note that this option is required if 'state' has the 'planned' value.
  state_file:
    description:
      - The path to an existing Terraform state file to use when building plan.
        If this is not specified, the default `terraform.tfstate` will be used.
      - This option is ignored when plan is specified.
  variables_files:
    description:
      - The path to a variables file for Terraform to fill into the TF
        configurations. This can accept a list of paths to multiple variables files.
      - Up until Ansible 2.9, this option was usable as I(variables_file).
    type: list
    elements: path
    aliases: [ 'variables_file' ]
  variables:
    description:
      - A group of key-values to override template variables or those in
        variables files.
  targets:
    description:
      - A list of specific resources to target in this plan/application. The
        resources selected here will also auto-include any dependencies.
  lock:
    description:
      - Enable statefile locking, if you use a service that accepts locks (such
        as S3+DynamoDB) to store your statefile.
    type: bool
  lock_timeout:
    description:
      - How long to maintain the lock on the statefile, if you use a service
        that accepts locks (such as S3+DynamoDB).
  force_init:
    description:
      - To avoid duplicating infra, if a state file can't be found this will
        force a `terraform init`. Generally, this should be turned off unless
        you intend to provision an entirely new Terraform deployment.
    default: false
    type: bool
  backend_config:
    description:
      - A group of key-values to provide at init stage to the -backend-config parameter.
  backend_config_files:
    description:
      - The path to a configuration file to provide at init state to the -backend-config parameter.
        This can accept a list of paths to multiple configuration files.
    type: list
    elements: path
    version_added: '0.2.0'
  plan_id:
    description:
      - A plan_id linked to a temporary plan file created if no plan_path
        is specified.
    required: false
    version_added: '1.0.0'
  log_activity_folder:
    description:
      - The path to a folder to create the logging file. If path does not exist,it is created.
        If not specified, the current directory will be used to store the logging file.
    required: false
    version_added: '1.0.0'
  file_name:
    description:
      - A string to name the logging file with. If not specified,
        a default name 'audit' will be specified.
    required: false
    version_added: '1.0.0'
notes:
   - To just run a `terraform plan`, use check mode.
requirements: [ "terraform" ]
author: "Ryan Scott Brown (@ryansb)"
'''

EXAMPLES = """
- name: Basic deploy of a service
  terraform:
    project_path: '{{ project_dir }}'
    state: present

- name: Define the backend configuration at init
  terraform:
    project_path: 'project/'
    state: "{{ state }}"
    force_init: true
    backend_config:
      region: "eu-west-1"
      bucket: "some-bucket"
      key: "random.tfstate"

- name: Define the backend configuration with one or more files at init
  terraform:
    project_path: 'project/'
    state: "{{ state }}"
    force_init: true
    backend_config_files:
      - /path/to/backend_config_file_1
      - /path/to/backend_config_file_2

- name: Define the plan_id, log_activity folder and file name for audit
  terraform:
    project_path: 'project/'
    state: "{{ state }}"
    force_init: true
    plan_id: 'tmpER44'
    log_activity_folder: '/path/to/folder/'
    file_name: 'process'

"""

RETURN = """
outputs:
  type: complex
  description: A dictionary of all the TF outputs by their assigned name. Use `.outputs.MyOutputName.value` to access the value.
  returned: on success
  sample: '{"bukkit_arn": {"sensitive": false, "type": "string", "value": "arn:aws:s3:::tf-test-bukkit"}'
  contains:
    sensitive:
      type: bool
      returned: always
      description: Whether Terraform has marked this value as sensitive
    type:
      type: str
      returned: always
      description: The type of the value (string, int, etc)
    value:
      returned: always
      description: The value of the output as interpolated by Terraform
stdout:
  type: str
  description: Full `terraform` command stdout, in case you want to display it or examine the event log
  returned: always
  sample: ''
command:
  type: str
  description: Full `terraform` command built by this module, in case you want to re-run the command outside the module or debug a problem.
  returned: always
  sample: terraform apply ...
"""

import os
import json
import tempfile
import time
import traceback
from ansible.module_utils.six.moves import shlex_quote

from ansible.module_utils.basic import AnsibleModule

DESTROY_ARGS = ('destroy', '-no-color', '-force')
APPLY_ARGS = ('apply', '-no-color', '-input=false', '-auto-approve=true')
module = None


def preflight_validation(module, bin_path, project_path, variables_args=None, plan_file=None):
    if project_path in [None, ''] or '/' not in project_path:
        module.fail_json(msg="Path for Terraform project can not be None or ''.")
    if not os.path.exists(bin_path):
        module.fail_json(msg="Path for Terraform binary '{0}' doesn't exist on this host - check the path and try again please.".format(bin_path))
    if not os.path.isdir(project_path):
        module.fail_json(msg="Path for Terraform project '{0}' doesn't exist on this host - check the path and try again please.".format(project_path))

    rc, out, err = module.run_command([bin_path, 'validate'] + variables_args, cwd=project_path, use_unsafe_shell=True)
    if rc != 0:
        module.fail_json(msg="Failed to validate Terraform configuration files:\r\n{0}".format(err))


def _state_args(module, state_file):
    if state_file and os.path.exists(state_file):
        return ['-state', state_file]
    if state_file and not os.path.exists(state_file):
        module.fail_json(msg='Could not find state_file "{0}", check the path and try again.'.format(state_file))
    return []


def init_plugins(bin_path, project_path, backend_config, backend_config_files):
    command = [bin_path, 'init', '-input=false']
    if backend_config:
        for key, val in backend_config.items():
            command.extend([
                '-backend-config',
                shlex_quote('{0}={1}'.format(key, val))
            ])
    if backend_config_files:
        for f in backend_config_files:
            command.extend(['-backend-config', f])
    rc, out, err = module.run_command(command, cwd=project_path)
    if rc != 0:
        module.fail_json(msg="Failed to initialize Terraform modules:\r\n{0}".format(err))


def get_workspace_context(module, bin_path, project_path):
    workspace_ctx = {"current": "default", "all": []}
    command = [bin_path, 'workspace', 'list', '-no-color']
    rc, out, err = module.run_command(command, cwd=project_path)
    if rc != 0:
        module.warn("Failed to list Terraform workspaces:\r\n{0}".format(err))
    for item in out.split('\n'):
        stripped_item = item.strip()
        if not stripped_item:
            continue
        elif stripped_item.startswith('* '):
            workspace_ctx["current"] = stripped_item.replace('* ', '')
        else:
            workspace_ctx["all"].append(stripped_item)
    return workspace_ctx


def _workspace_cmd(module, bin_path, project_path, action, workspace):
    command = [bin_path, 'workspace', action, workspace, '-no-color']
    rc, out, err = module.run_command(command, cwd=project_path)
    if rc != 0:
        module.fail_json(msg="Failed to {0} workspace:\r\n{1}".format(action, err))
    return rc, out, err


def create_workspace(bin_path, project_path, workspace):
    _workspace_cmd(bin_path, project_path, 'new', workspace)


def select_workspace(bin_path, project_path, workspace):
    _workspace_cmd(bin_path, project_path, 'select', workspace)


def remove_workspace(bin_path, project_path, workspace):
    _workspace_cmd(bin_path, project_path, 'delete', workspace)


def build_plan(module, command, project_path, variables_args, state_file, targets, state, plan_path=None):
    if plan_path is None:
        f, plan_path = tempfile.mkstemp(suffix='.tfplan')

    plan_command = [command[0], 'plan', '-input=false', '-no-color', '-detailed-exitcode', '-out', plan_path]

    for t in (module.params.get('targets') or []):
        plan_command.extend(['-target', t])

    plan_command.extend(_state_args(module, state_file))

    rc, out, err = module.run_command(plan_command + variables_args, cwd=project_path, use_unsafe_shell=True)

    if rc == 0:
        # no changes
        return plan_path, False, out, err, plan_command if state == 'planned' else command
    elif rc == 1:
        # failure to plan
        module.fail_json(msg='Terraform plan could not be created\r\nSTDOUT: {0}\r\n\r\nSTDERR: {1}'.format(out, err))
    elif rc == 2:
        # changes, but successful
        return plan_path, True, out, err, plan_command if state == 'planned' else command

    module.fail_json(msg='Terraform plan failed with unexpected exit code {0}. \r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(rc, out, err))


def return_full_path(log_activity_folder, file_name):
    if log_activity_folder[-1] != '/':
        full_path = log_activity_folder + '/' + file_name + '.json'
    else:
        full_path = log_activity_folder + file_name + '.json'

    return full_path


def create_logging_file_and_directory(log_activity_folder, file_name):
    full_path = return_full_path(log_activity_folder, file_name)
    if not os.path.exists(log_activity_folder):
        os.makedirs(log_activity_folder)

    if not os.path.exists(full_path):
        with open(full_path, 'w') as file_created:
            json.dump([], file_created, indent=4)


def logging(log_activity_folder, file_name, plan_used, command_run, stdout):
    path_to_audit_file = return_full_path(log_activity_folder, file_name)
    timestamp = time.strftime('%d-%m-%Y %H:%M:%S')
    command_used = command_run[1]
    outcome = ''
    list_destruction = []
    list_creation = []
    list_modification = []
    if command_used == "apply" or command_used == "destroy":
        for line in stdout.split('\n'):
            if line.startswith('Apply complete!') or line.startswith('No changes') or line.startswith('Destroy complete!'):
                outcome = line
                break
            else:
                try:
                    if line.split(':')[1].startswith(" Destruction"):
                        list_destruction.append(line.split(':')[0])
                    if line.split(':')[1].startswith(" Creation"):
                        list_creation.append(line.split(':')[0])
                    if line.split(':')[1].startswith(" Modification"):
                        list_modification.append(line.split(':')[0])
                except IndexError:
                    pass
    elif command_used == "plan":
        for line in stdout.split('\n'):
            if line.startswith('Plan:') or line.startswith('No changes'):
                outcome = line
    items_to_write = {
        'time': timestamp,
        'plan_used': plan_used,
        'command_run': command_used,
        'outcome': outcome,
        'resources_added': list_creation,
        'resources_changed': list_modification,
        'resources_destroyed': list_destruction}

    with open(path_to_audit_file, 'r') as file_opened:
        data_stored = json.load(file_opened)

    data_stored.append(items_to_write)

    with open(path_to_audit_file, 'w') as file_opened:
        json.dump(data_stored, file_opened, indent=4)


def get_plan_file_name_without_extension(plan_file_path):
    file_name, extension = os.path.basename(plan_file_path).split(".")
    return file_name


def get_plans_used(log_activity_folder, file_name):
    log_activity_path = return_full_path(log_activity_folder, file_name)
    plans = []
    with open(log_activity_path, 'r') as file_opened:
        data_stored = json.load(file_opened)
    for record in data_stored:
        if 'plan' in record.values():
            plans.append(record)
    return plans


def get_plan_file_from_logging_file(log_activity_folder, file_name, plan_id):
    all_entries_with_file = []
    search_file_path = '/tmp/{0}.tfplan'.format(plan_id)
    for i in get_plans_used(log_activity_folder, file_name):
        if search_file_path in i.values():
            all_entries_with_file.append(i)
    if all_entries_with_file:
        return all_entries_with_file[0]['plan_used']
    else:
        return ''


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            project_path=dict(required=True, type='path'),
            binary_path=dict(type='path'),
            workspace=dict(required=False, type='str', default='default'),
            purge_workspace=dict(type='bool', default=False),
            state=dict(default='present', choices=['present', 'absent', 'planned']),
            variables=dict(type='dict'),
            variables_files=dict(aliases=['variables_file'], type='list', elements='path', default=None),
            plan_file=dict(type='path'),
            state_file=dict(type='path'),
            targets=dict(type='list', default=[]),
            lock=dict(type='bool', default=True),
            lock_timeout=dict(type='int',),
            force_init=dict(type='bool', default=False),
            backend_config=dict(type='dict', default=None),
            backend_config_files=dict(type='list', elements='path', default=None),
            plan_id=dict(type='str'),
            log_activity_folder=dict(type='path', default='./'),
            file_name=dict(type='str', default='audit'),
        ),
        supports_check_mode=True,
    )

    project_path = module.params.get('project_path')
    bin_path = module.params.get('binary_path')
    workspace = module.params.get('workspace')
    purge_workspace = module.params.get('purge_workspace')
    state = module.params.get('state')
    variables = module.params.get('variables') or {}
    variables_files = module.params.get('variables_files')
    plan_file = module.params.get('plan_file')
    state_file = module.params.get('state_file')
    force_init = module.params.get('force_init')
    backend_config = module.params.get('backend_config')
    backend_config_files = module.params.get('backend_config_files')
    plan_id = module.params.get('plan_id')
    log_activity_folder = module.params.get('log_activity_folder')
    file_name = module.params.get('file_name')

    if bin_path is not None:
        command = [bin_path]
    else:
        command = [module.get_bin_path('terraform', required=True)]

    if force_init:
        init_plugins(command[0], project_path, backend_config, backend_config_files)

    workspace_ctx = get_workspace_context(module, command[0], project_path)
    if workspace_ctx["current"] != workspace:
        if workspace not in workspace_ctx["all"]:
            create_workspace(command[0], project_path, workspace)
        else:
            select_workspace(command[0], project_path, workspace)

    if state == 'present':
        command.extend(APPLY_ARGS)
    elif state == 'absent':
        command.extend(DESTROY_ARGS)

    variables_args = []
    for k, v in variables.items():
        variables_args.extend([
            '-var',
            '{0}={1}'.format(k, v)
        ])
    if variables_files:
        for f in variables_files:
            variables_args.extend(['-var-file', f])

    preflight_validation(module, command[0], project_path, variables_args)

    if module.params.get('lock') is not None:
        if module.params.get('lock'):
            command.append('-lock=true')
        else:
            command.append('-lock=false')
    if module.params.get('lock_timeout') is not None:
        command.append('-lock-timeout=%ds' % module.params.get('lock_timeout'))

    for t in (module.params.get('targets') or []):
        command.extend(['-target', t])

    # we aren't sure if this plan will result in changes, so assume yes
    needs_application, changed = True, False

    out, err = '', ''

    create_logging_file_and_directory(log_activity_folder, file_name)

    if state == 'absent':
        command.extend(variables_args)
    elif state == 'present' and plan_file:
        if any([os.path.isfile(project_path + "/" + plan_file), os.path.isfile(plan_file)]):
            command.append(plan_file)
        else:
            module.fail_json(msg='Could not find plan_file "{0}", check the path and try again.'.format(plan_file))
    elif state == 'planned' and plan_file:
        if any([os.path.isfile(project_path + "/" + plan_file), os.path.isfile(plan_file)]):
            command.append(plan_file)
        else:
            module.fail_json(msg='Could not find plan_file "{0}", check the path and try again.'.format(plan_file))
    elif state == 'present' and plan_id:
        plan_file = get_plan_file_from_logging_file(log_activity_folder, file_name, plan_id)
        if plan_file:
            command.append(plan_file)
            message = "running apply with plan_id: {0}".format(plan_id)
        else:
            module.fail_json(msg="plan file with id does not exist!")
    elif state == 'present' and not plan_id:
        last_plan_used = get_plans_used(log_activity_folder, file_name)
        if last_plan_used:
            message = "no plan file specified. running 'apply' with plan created from recently run 'plan' \
            command with id: {0}".format(get_plan_file_name_without_extension(last_plan_used[-1]['plan_used']))
            command.append(last_plan_used[-1]['plan_used'])
            plan_file = last_plan_used[-1]['plan_used']
        else:
            # no plan command run yet
            plan_file, needs_application, out, err, command = build_plan(
                module, command, project_path,
                variables_args, state_file, module.params.get('targets'), state, plan_file)
            command.append(plan_file)
            message = "running apply without having run plan before"

    else:
        plan_file, needs_application, out, err, command = build_plan(
            module, command, project_path,
            variables_args, state_file, module.params.get('targets'), state, plan_file)
        command.append(plan_file)
        message = "plan command executed. plan_id generated: {0}".format(get_plan_file_name_without_extension(plan_file))

    if needs_application and not module.check_mode and not state == 'planned':
        rc, out, err = module.run_command(command, cwd=project_path)
        # checks out to decide if changes were made during execution
        if '0 added, 0 changed' not in out and not state == "absent" or '0 destroyed' not in out:
            changed = True
        if rc != 0:
            module.fail_json(
                msg="Failure when executing Terraform command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
                command=' '.join(command)
            )

    outputs_command = [command[0], 'output', '-no-color', '-json'] + _state_args(module, state_file)
    rc, outputs_text, outputs_err = module.run_command(outputs_command, cwd=project_path)
    if rc == 1:
        module.warn("Could not get Terraform outputs. This usually means none have been defined.\nstdout: {0}\nstderr: {1}".format(outputs_text, outputs_err))
        outputs = {}
    elif rc != 0:
        module.fail_json(
            msg="Failure when getting Terraform outputs. "
                "Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, outputs_text, outputs_err),
            command=' '.join(outputs_command))
    else:
        outputs = json.loads(outputs_text)

    # Restore the Terraform workspace found when running the module
    if workspace_ctx["current"] != workspace:
        select_workspace(command[0], project_path, workspace_ctx["current"])
    if state == 'absent' and workspace != 'default' and purge_workspace is True:
        remove_workspace(command[0], project_path, workspace)

    logging(log_activity_folder, file_name, plan_file, command, out)

    module.exit_json(changed=changed, message=message, state=state, workspace=workspace, outputs=outputs, stdout=out, stderr=err, command=' '.join(command))


if __name__ == '__main__':
    main()
