#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Scott Anderson <scottanderson42@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: django_manage
short_description: Manages a Django application.
description:
    - Manages a Django application using the C(manage.py) application frontend to C(django-admin). With the
      C(virtualenv) parameter, all management commands will be executed by the given C(virtualenv) installation.
options:
  command:
    description:
      - The name of the Django management command to run. Built in commands are C(cleanup), C(collectstatic),
        C(flush), C(loaddata), C(migrate), C(syncdb), C(test), and C(validate).
      - Other commands can be entered, but will fail if they're unknown to Django.  Other commands that may
        prompt for user input should be run with the C(--noinput) flag.
      - The module will perform some basic parameter validation (when applicable) to the commands C(cleanup),
        C(collectstatic), C(createcachetable), C(flush), C(loaddata), C(migrate), C(syncdb), C(test), and C(validate).
    type: str
    required: true
  project_path:
    description:
      - The path to the root of the Django application where B(manage.py) lives.
    type: path
    required: true
    aliases: [app_path, chdir]
  settings:
    description:
      - The Python path to the application's settings module, such as C(myapp.settings).
    type: path
    required: false
  pythonpath:
    description:
      - A directory to add to the Python path. Typically used to include the settings module if it is located
        external to the application directory.
    type: path
    required: false
    aliases: [python_path]
  virtualenv:
    description:
      - An optional path to a I(virtualenv) installation to use while running the manage application.
    type: path
    aliases: [virtual_env]
  apps:
    description:
      - A list of space-delimited apps to target. Used by the C(test) command.
    type: str
    required: false
  cache_table:
    description:
      - The name of the table used for database-backed caching. Used by the C(createcachetable) command.
    type: str
    required: false
  clear:
    description:
      - Clear the existing files before trying to copy or link the original file.
      - Used only with the C(collectstatic) command. The C(--noinput) argument will be added automatically.
    required: false
    default: no
    type: bool
  database:
    description:
      - The database to target. Used by the C(createcachetable), C(flush), C(loaddata), C(syncdb),
        and C(migrate) commands.
    type: str
    required: false
  failfast:
    description:
      - Fail the command immediately if a test fails. Used by the C(test) command.
    required: false
    default: false
    type: bool
    aliases: [fail_fast]
  fixtures:
    description:
      - A space-delimited list of fixture file names to load in the database. B(Required) by the C(loaddata) command.
    type: str
    required: false
  skip:
    description:
     - Will skip over out-of-order missing migrations, you can only use this parameter with C(migrate) command.
    required: false
    type: bool
  merge:
    description:
     - Will run out-of-order or missing migrations as they are not rollback migrations, you can only use this
       parameter with C(migrate) command.
    required: false
    type: bool
  link:
    description:
     - Will create links to the files instead of copying them, you can only use this parameter with
       C(collectstatic) command.
    required: false
    type: bool
  testrunner:
    description:
      - "From the Django docs: Controls the test runner class that is used to execute tests."
      - This parameter is passed as-is to C(manage.py).
    type: str
    required: false
    aliases: [test_runner]
notes:
  - C(virtualenv) (U(http://www.virtualenv.org)) must be installed on the remote host if the I(virtualenv) parameter
    is specified.
  - This module will create a virtualenv if the I(virtualenv) parameter is specified and a virtual environment does not already
    exist at the given location.
  - This module assumes English error messages for the C(createcachetable) command to detect table existence,
    unfortunately.
  - To be able to use the C(migrate) command with django versions < 1.7, you must have C(south) installed and added
    as an app in your settings.
  - To be able to use the C(collectstatic) command, you must have enabled staticfiles in your settings.
  - Your C(manage.py) application must be executable (rwxr-xr-x), and must have a valid shebang,
    i.e. C(#!/usr/bin/env python), for invoking the appropriate Python interpreter.
requirements: [ "virtualenv", "django" ]
author: "Scott Anderson (@tastychutney)"
'''

EXAMPLES = """
- name: Run cleanup on the application installed in django_dir
  community.general.django_manage:
    command: cleanup
    project_path: "{{ django_dir }}"

- name: Load the initial_data fixture into the application
  community.general.django_manage:
    command: loaddata
    project_path: "{{ django_dir }}"
    fixtures: "{{ initial_data }}"

- name: Run syncdb on the application
  community.general.django_manage:
    command: syncdb
    project_path: "{{ django_dir }}"
    settings: "{{ settings_app_name }}"
    pythonpath: "{{ settings_dir }}"
    virtualenv: "{{ virtualenv_dir }}"

- name: Run the SmokeTest test case from the main app. Useful for testing deploys
  community.general.django_manage:
    command: test
    project_path: "{{ django_dir }}"
    apps: main.SmokeTest

- name: Create an initial superuser
  community.general.django_manage:
    command: "createsuperuser --noinput --username=admin --email=admin@example.com"
    project_path: "{{ django_dir }}"
"""

import os
import sys
import shlex

from ansible.module_utils.basic import AnsibleModule


def _fail(module, cmd, out, err, **kwargs):
    msg = ''
    if out:
        msg += "stdout: %s" % (out, )
    if err:
        msg += "\n:stderr: %s" % (err, )
    module.fail_json(cmd=cmd, msg=msg, **kwargs)


def _ensure_virtualenv(module):

    venv_param = module.params['virtualenv']
    if venv_param is None:
        return

    vbin = os.path.join(venv_param, 'bin')
    activate = os.path.join(vbin, 'activate')

    if not os.path.exists(activate):
        virtualenv = module.get_bin_path('virtualenv', True)
        vcmd = [virtualenv, venv_param]
        rc, out_venv, err_venv = module.run_command(vcmd)
        if rc != 0:
            _fail(module, vcmd, out_venv, err_venv)

    os.environ["PATH"] = "%s:%s" % (vbin, os.environ["PATH"])
    os.environ["VIRTUAL_ENV"] = venv_param


def createcachetable_check_changed(output):
    return "already exists" not in output


def flush_filter_output(line):
    return "Installed" in line and "Installed 0 object" not in line


def loaddata_filter_output(line):
    return "Installed" in line and "Installed 0 object" not in line


def syncdb_filter_output(line):
    return ("Creating table " in line) \
        or ("Installed" in line and "Installed 0 object" not in line)


def migrate_filter_output(line):
    return ("Migrating forwards " in line) \
        or ("Installed" in line and "Installed 0 object" not in line) \
        or ("Applying" in line)


def collectstatic_filter_output(line):
    return line and "0 static files" not in line


def main():
    command_allowed_param_map = dict(
        cleanup=(),
        createcachetable=('cache_table', 'database', ),
        flush=('database', ),
        loaddata=('database', 'fixtures', ),
        syncdb=('database', ),
        test=('failfast', 'testrunner', 'apps', ),
        validate=(),
        migrate=('apps', 'skip', 'merge', 'database',),
        collectstatic=('clear', 'link', ),
    )

    command_required_param_map = dict(
        loaddata=('fixtures', ),
    )

    # forces --noinput on every command that needs it
    noinput_commands = (
        'flush',
        'syncdb',
        'migrate',
        'test',
        'collectstatic',
    )

    # These params are allowed for certain commands only
    specific_params = ('apps', 'clear', 'database', 'failfast', 'fixtures', 'testrunner')

    # These params are automatically added to the command if present
    general_params = ('settings', 'pythonpath', 'database',)
    specific_boolean_params = ('clear', 'failfast', 'skip', 'merge', 'link')
    end_of_command_params = ('apps', 'cache_table', 'fixtures')

    module = AnsibleModule(
        argument_spec=dict(
            command=dict(required=True, type='str'),
            project_path=dict(required=True, type='path', aliases=['app_path', 'chdir']),
            settings=dict(type='path'),
            pythonpath=dict(type='path', aliases=['python_path']),
            virtualenv=dict(type='path', aliases=['virtual_env']),

            apps=dict(),
            cache_table=dict(type='str'),
            clear=dict(default=False, type='bool'),
            database=dict(type='str'),
            failfast=dict(default=False, type='bool', aliases=['fail_fast']),
            fixtures=dict(type='str'),
            testrunner=dict(type='str', aliases=['test_runner']),
            skip=dict(type='bool'),
            merge=dict(type='bool'),
            link=dict(type='bool'),
        ),
    )

    command_split = shlex.split(module.params['command'])
    command_bin = command_split[0]
    project_path = module.params['project_path']
    virtualenv = module.params['virtualenv']

    for param in specific_params:
        value = module.params[param]
        if value and param not in command_allowed_param_map[command_bin]:
            module.fail_json(msg='%s param is incompatible with command=%s' % (param, command_bin))

    for param in command_required_param_map.get(command_bin, ()):
        if not module.params[param]:
            module.fail_json(msg='%s param is required for command=%s' % (param, command_bin))

    _ensure_virtualenv(module)

    run_cmd_args = ["./manage.py"] + command_split

    if command_bin in noinput_commands and '--noinput' not in command_split:
        run_cmd_args.append("--noinput")

    for param in general_params:
        if module.params[param]:
            run_cmd_args.append('--%s=%s' % (param, module.params[param]))

    for param in specific_boolean_params:
        if module.params[param]:
            run_cmd_args.append('--%s' % param)

    # these params always get tacked on the end of the command
    for param in end_of_command_params:
        if module.params[param]:
            if param in ('fixtures', 'apps'):
                run_cmd_args.extend(shlex.split(module.params[param]))
            else:
                run_cmd_args.append(module.params[param])

    rc, out, err = module.run_command(run_cmd_args, cwd=project_path)
    if rc != 0:
        if command_bin == 'createcachetable' and 'table' in err and 'already exists' in err:
            out = 'already exists.'
        else:
            if "Unknown command:" in err:
                _fail(module, run_cmd_args, err, "Unknown django command: %s" % command_bin)
            _fail(module, run_cmd_args, out, err, path=os.environ["PATH"], syspath=sys.path)

    changed = False

    lines = out.split('\n')
    filt = globals().get(command_bin + "_filter_output", None)
    if filt:
        filtered_output = list(filter(filt, lines))
        if len(filtered_output):
            changed = True
    check_changed = globals().get("{0}_check_changed".format(command_bin), None)
    if check_changed:
        changed = check_changed(out)

    module.exit_json(changed=changed, out=out, cmd=run_cmd_args, app_path=project_path, project_path=project_path,
                     virtualenv=virtualenv, settings=module.params['settings'], pythonpath=module.params['pythonpath'])


if __name__ == '__main__':
    main()
