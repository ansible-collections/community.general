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
  socket_host:
    description:
      - The IP address of the control node to stream terraform output during long running tasks.
        It should match the one set to be used by the terraform_ stream plugin
    type: str
  socket_port:
    description:
      - The port to stream long running terraform tasks from
    type: str
    version_added: '0.2.0'
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
import traceback
from ansible.module_utils.six.moves import shlex_quote

from ansible.module_utils.basic import AnsibleModule
import socket
import datetime
import subprocess
import re
import select
import threading
from ansible.module_utils.six import (
    PY2,
    PY3,
    b,
    binary_type,
    integer_types,
    iteritems,
    string_types,
    text_type,
)
from ansible.module_utils._text import to_native, to_bytes, to_text
import shlex
from ansible.module_utils.basic import heuristic_log_sanitize

DESTROY_ARGS = ('destroy', '-no-color', '-force')
APPLY_ARGS = ('apply', '-no-color', '-input=false', '-auto-approve=true')
module = None
PASSWD_ARG_RE = re.compile(r'^[-]{0,2}pass[-]?(word|wd)?')


def socket_client(data, port, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if not isinstance(data, bytes):
        try:
            data = data.encode('utf-8')
        except Exception:
            data = repr(data).encode('utf-8')
    outln = b'%s' % (data)
    sock.sendto(outln, (host, port))


def custom_run_command(self, args, socket_host, socket_port, check_rc=False, close_fds=True, executable=None, data=None, binary_data=False, path_prefix=None,
                       cwd=None, use_unsafe_shell=False, prompt_regex=None, environ_update=None, umask=None, encoding='utf-8', errors='surrogate_or_strict',
                       expand_user_and_vars=True, pass_fds=None, before_communicate_callback=None):
    '''
        This is a fork lifted run_command function from ansible core
        https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/basic.py

        The only difference is it sends output from subprocess command to a socket
        server which is a callback plugin(terraform_stream).
    '''

    self._clean = None

    if not isinstance(args, (list, binary_type, text_type)):
        msg = "Argument 'args' to run_command must be list or string"
        self.fail_json(rc=257, cmd=args, msg=msg)

    shell = False
    if use_unsafe_shell:

        # stringify args for unsafe/direct shell usage
        if isinstance(args, list):
            args = b" ".join([to_bytes(shlex_quote(x), errors='surrogate_or_strict') for x in args])
        # removed the next 2 lines
        else:
            args = to_bytes(args, errors='surrogate_or_strict')

        # not set explicitly, check if set by controller
        if executable:
            executable = to_bytes(executable, errors='surrogate_or_strict')
            args = [executable, b'-c', args]
        elif self._shell not in (None, '/bin/sh'):
            args = [to_bytes(self._shell, errors='surrogate_or_strict'), b'-c', args]
        else:
            shell = True
    else:
        # ensure args are a list
        if isinstance(args, (binary_type, text_type)):
            # On python2.6 and below, shlex has problems with text type
            # On python3, shlex needs a text type.
            if PY2:
                args = to_bytes(args, errors='surrogate_or_strict')
            elif PY3:
                args = to_text(args, errors='surrogateescape')
            args = shlex.split(args)

        # expand ``~`` in paths, and all environment vars
        if expand_user_and_vars:
            args = [to_bytes(os.path.expanduser(os.path.expandvars(x)), errors='surrogate_or_strict') for x in args if x is not None]
        else:
            args = [to_bytes(x, errors='surrogate_or_strict') for x in args if x is not None]

    prompt_re = None
    if prompt_regex:
        if isinstance(prompt_regex, text_type):
            if PY3:
                prompt_regex = to_bytes(prompt_regex, errors='surrogateescape')
            elif PY2:
                prompt_regex = to_bytes(prompt_regex, errors='surrogate_or_strict')
        try:
            prompt_re = re.compile(prompt_regex, re.MULTILINE)
        except re.error:
            self.fail_json(msg="invalid prompt regular expression given to run_command")

    rc = 0
    msg = None
    st_in = None

    # Manipulate the environ we'll send to the new process
    old_env_vals = {}
    # We can set this from both an attribute and per call
    for key, val in self.run_command_environ_update.items():
        old_env_vals[key] = os.environ.get(key, None)
        os.environ[key] = val
    if environ_update:
        for key, val in environ_update.items():
            old_env_vals[key] = os.environ.get(key, None)
            os.environ[key] = val
    if path_prefix:
        old_env_vals['PATH'] = os.environ['PATH']
        os.environ['PATH'] = "%s:%s" % (path_prefix, os.environ['PATH'])

    # If using test-module.py and explode, the remote lib path will resemble:
    #   /tmp/test_module_scratch/debug_dir/ansible/module_utils/basic.py
    # If using ansible or ansible-playbook with a remote system:
    #   /tmp/ansible_vmweLQ/ansible_modlib.zip/ansible/module_utils/basic.py

    # Clean out python paths set by ansiballz
    to_clean_args = args
    if 'PYTHONPATH' in os.environ:
        pypaths = os.environ['PYTHONPATH'].split(':')
        pypaths = [x for x in pypaths
                   if not x.endswith('/ansible_modlib.zip') and
                   not x.endswith('/debug_dir')]
        os.environ['PYTHONPATH'] = ':'.join(pypaths)
        if not os.environ['PYTHONPATH']:
            del os.environ['PYTHONPATH']

    # added
    clean_args = []
    is_passwd = False
    for arg in (to_native(a) for a in to_clean_args):
        if is_passwd:
            is_passwd = False
            clean_args.append('********')
            continue
        if PASSWD_ARG_RE.match(arg):
            sep_idx = arg.find('=')
            if sep_idx > -1:
                clean_args.append('%s=********' % arg[:sep_idx])
                continue
            else:
                is_passwd = True
        arg = heuristic_log_sanitize(arg, self.no_log_values)
        clean_args.append(arg)
    clean_args = ' '.join(shlex_quote(arg) for arg in clean_args)

    if data:
        st_in = subprocess.PIPE

    kwargs = dict(
        executable=executable,
        shell=shell,
        close_fds=close_fds,
        stdin=st_in,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=self._restore_signal_handlers,
    )

    if PY3 and pass_fds:
        kwargs["pass_fds"] = pass_fds
    elif PY2 and pass_fds:
        kwargs['close_fds'] = False

    # store the pwd
    prev_dir = os.getcwd()

    # make sure we're in the right working directory
    if cwd and os.path.isdir(cwd):
        cwd = to_bytes(os.path.abspath(os.path.expanduser(cwd)), errors='surrogate_or_strict')
        kwargs['cwd'] = cwd
        try:
            os.chdir(cwd)
        except (OSError, IOError) as e:
            self.fail_json(rc=e.errno, msg="Could not open %s, %s" % (cwd, to_native(e)),
                           exception=traceback.format_exc())

    old_umask = None
    if umask:
        old_umask = os.umask(umask)

    try:
        if self._debug:
            self.log('Executing: ' + clean_args)

        cmd = subprocess.Popen(args, **kwargs)
        while True:
            line = cmd.stdout.readline()
            if not line:
                break
            socket_client(line, socket_port, socket_host)

        if before_communicate_callback:
            before_communicate_callback(cmd)

            # the communication logic here is essentially taken from that
            # of the _communicate() function in ssh.py

        stdout = b('')
        stderr = b('')
        rpipes = [cmd.stdout, cmd.stderr]

        if data:
            if not binary_data:
                data += '\n'
            if isinstance(data, text_type):
                data = to_bytes(data)
            cmd.stdin.write(data)
            cmd.stdin.close()

        while True:
            rfds, wfds, efds = select.select(rpipes, [], rpipes, 1)
            stdout += self._read_from_pipes(rpipes, rfds, cmd.stdout)
            stderr += self._read_from_pipes(rpipes, rfds, cmd.stderr)
            # if we're checking for prompts, do it now
            if prompt_re:
                if prompt_re.search(stdout) and not data:
                    if encoding:
                        stdout = to_native(stdout, encoding=encoding, errors=errors)
                    return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
            # only break out if no pipes are left to read or
            # the pipes are completely read and
            # the process is terminated
            if (not rpipes or not rfds) and cmd.poll() is not None:
                break
            # No pipes are left to read but process is not yet terminated
            # Only then it is safe to wait for the process to be finished
            # NOTE: Actually cmd.poll() is always None here if rpipes is empty
            elif not rpipes and cmd.poll() is None:
                cmd.wait()
                # The process is terminated. Since no pipes to read from are
                # left, there is no need to call select() again.
                break

        cmd.stdout.close()
        cmd.stderr.close()

        rc = cmd.returncode

    except (OSError, IOError) as e:
        self.log("Error Executing CMD:%s Exception:%s" % (self._clean_args(args), to_native(e)))
        self.fail_json(rc=e.errno, msg=to_native(e), cmd=self._clean_args(args))
    except Exception as e:
        self.log("Error Executing CMD:%s Exception:%s" % (self._clean_args(args), to_native(traceback.format_exc())))
        self.fail_json(rc=257, msg=to_native(e), exception=traceback.format_exc(), cmd=self._clean_args(args))

    # Restore env settings
    for key, val in old_env_vals.items():
        if val is None:
            del os.environ[key]
        else:
            os.environ[key] = val

    if old_umask:
        os.umask(old_umask)

    if rc != 0 and check_rc:
        msg = heuristic_log_sanitize(stderr.rstrip(), self.no_log_values)
        self.fail_json(cmd=self._clean_args(args), rc=rc, stdout=stdout, stderr=stderr, msg=msg)

    # reset the pwd
    os.chdir(prev_dir)

    if encoding is not None:
        return (rc, to_native(stdout, encoding=encoding, errors=errors),
                to_native(stderr, encoding=encoding, errors=errors))

    return (rc, stdout, stderr)


def preflight_validation(bin_path, project_path, variables_args=None, plan_file=None):
    if project_path in [None, ''] or '/' not in project_path:
        module.fail_json(msg="Path for Terraform project can not be None or ''.")
    if not os.path.exists(bin_path):
        module.fail_json(msg="Path for Terraform binary '{0}' doesn't exist on this host - check the path and try again please.".format(bin_path))
    if not os.path.isdir(project_path):
        module.fail_json(msg="Path for Terraform project '{0}' doesn't exist on this host - check the path and try again please.".format(project_path))

    rc, out, err = module.run_command([bin_path, 'validate'] + variables_args, cwd=project_path, use_unsafe_shell=True)
    if rc != 0:
        module.fail_json(msg="Failed to validate Terraform configuration files:\r\n{0}".format(err))


def _state_args(state_file):
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


def get_workspace_context(bin_path, project_path):
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


def _workspace_cmd(bin_path, project_path, action, workspace):
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


def build_plan(command, project_path, variables_args, state_file, targets, state, plan_path=None):
    if plan_path is None:
        f, plan_path = tempfile.mkstemp(suffix='.tfplan')

    plan_command = [command[0], 'plan', '-input=false', '-no-color', '-detailed-exitcode', '-out', plan_path]

    for t in (module.params.get('targets') or []):
        plan_command.extend(['-target', t])

    plan_command.extend(_state_args(state_file))

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
            socket_port=dict(type='int'),
            socket_host=dict(type='str')
        ),
        required_if=[('state', 'planned', ['plan_file'])],
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
    socket_port = module.params.get('socket_port')
    socket_host = module.params.get('socket_host')

    if bin_path is not None:
        command = [bin_path]
    else:
        command = [module.get_bin_path('terraform', required=True)]

    if force_init:
        init_plugins(command[0], project_path, backend_config, backend_config_files)

    workspace_ctx = get_workspace_context(command[0], project_path)
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

    preflight_validation(command[0], project_path, variables_args)

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

    if state == 'absent':
        command.extend(variables_args)
    elif state == 'present' and plan_file:
        if any([os.path.isfile(project_path + "/" + plan_file), os.path.isfile(plan_file)]):
            command.append(plan_file)
        else:
            module.fail_json(msg='Could not find plan_file "{0}", check the path and try again.'.format(plan_file))
    else:
        plan_file, needs_application, out, err, command = build_plan(command, project_path, variables_args, state_file,
                                                                     module.params.get('targets'), state, plan_file)
        command.append(plan_file)

    if needs_application and not module.check_mode and not state == 'planned':
        if socket_port is None and socket_host is None:
            rc, out, err = module.run_command(command, cwd=project_path)
        else:
            rc, out, err = custom_run_command(module, command, cwd=project_path, socket_host=socket_host, socket_port=socket_port)
        # checks out to decide if changes were made during execution
        if '0 added, 0 changed' not in out and not state == "absent" or '0 destroyed' not in out:
            changed = True
        if rc != 0:
            module.fail_json(
                msg="Failure when executing Terraform command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
                command=' '.join(command)
            )

    outputs_command = [command[0], 'output', '-no-color', '-json'] + _state_args(state_file)
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

    module.exit_json(changed=changed, state=state, workspace=workspace, outputs=outputs, stdout=out, stderr=err, command=' '.join(command))


if __name__ == '__main__':
    main()
