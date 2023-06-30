#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2013, Scott Anderson <scottanderson42@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: django_manage
short_description: Manages a Django application
description:
  - Manages a Django application using the C(manage.py) application frontend to C(django-admin). With the
    O(virtualenv) parameter, all management commands will be executed by the given C(virtualenv) installation.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  command:
    description:
      - The name of the Django management command to run. The commands listed below are built in this module and have some basic parameter validation.
      - >
        V(cleanup) - clean up old data from the database (deprecated in Django 1.5). This parameter will be
        removed in community.general 9.0.0. Use V(clearsessions) instead.
      - V(collectstatic) - Collects the static files into C(STATIC_ROOT).
      - V(createcachetable) - Creates the cache tables for use with the database cache backend.
      - V(flush) - Removes all data from the database.
      - V(loaddata) - Searches for and loads the contents of the named O(fixtures) into the database.
      - V(migrate) - Synchronizes the database state with models and migrations.
      - >
        V(syncdb) - Synchronizes the database state with models and migrations (deprecated in Django 1.7).
        This parameter will be removed in community.general 9.0.0. Use V(migrate) instead.
      - V(test) - Runs tests for all installed apps.
      - >
        V(validate) - Validates all installed models (deprecated in Django 1.7). This parameter will be
        removed in community.general 9.0.0. Use V(check) instead.
      - Other commands can be entered, but will fail if they are unknown to Django.  Other commands that may
        prompt for user input should be run with the C(--noinput) flag.
    type: str
    required: true
  project_path:
    description:
      - The path to the root of the Django application where C(manage.py) lives.
    type: path
    required: true
    aliases: [app_path, chdir]
  settings:
    description:
      - The Python path to the application's settings module, such as V(myapp.settings).
    type: path
    required: false
  pythonpath:
    description:
      - A directory to add to the Python path. Typically used to include the settings module if it is located
        external to the application directory.
      - This would be equivalent to adding O(pythonpath)'s value to the E(PYTHONPATH) environment variable.
    type: path
    required: false
    aliases: [python_path]
  virtualenv:
    description:
      - An optional path to a C(virtualenv) installation to use while running the manage application.
    type: path
    aliases: [virtual_env]
  apps:
    description:
      - A list of space-delimited apps to target. Used by the V(test) command.
    type: str
    required: false
  cache_table:
    description:
      - The name of the table used for database-backed caching. Used by the V(createcachetable) command.
    type: str
    required: false
  clear:
    description:
      - Clear the existing files before trying to copy or link the original file.
      - Used only with the V(collectstatic) command. The C(--noinput) argument will be added automatically.
    required: false
    default: false
    type: bool
  database:
    description:
      - The database to target. Used by the V(createcachetable), V(flush), V(loaddata), V(syncdb),
        and V(migrate) commands.
    type: str
    required: false
  failfast:
    description:
      - Fail the command immediately if a test fails. Used by the V(test) command.
    required: false
    default: false
    type: bool
    aliases: [fail_fast]
  fixtures:
    description:
      - A space-delimited list of fixture file names to load in the database. B(Required) by the V(loaddata) command.
    type: str
    required: false
  skip:
    description:
      - Will skip over out-of-order missing migrations, you can only use this parameter with V(migrate) command.
    required: false
    type: bool
  merge:
    description:
      - Will run out-of-order or missing migrations as they are not rollback migrations, you can only use this
        parameter with V(migrate) command.
    required: false
    type: bool
  link:
    description:
      - Will create links to the files instead of copying them, you can only use this parameter with
        V(collectstatic) command.
    required: false
    type: bool
  testrunner:
    description:
      - Controls the test runner class that is used to execute tests.
      - This parameter is passed as-is to C(manage.py).
    type: str
    required: false
    aliases: [test_runner]
  ack_venv_creation_deprecation:
    description:
      - >-
        When a O(virtualenv) is set but the virtual environment does not exist, the current behavior is
        to create a new virtual environment. That behavior is deprecated and if that case happens it will
        generate a deprecation warning. Set this flag to V(true) to suppress the deprecation warning.
      - Please note that you will receive no further warning about this being removed until the module
        will start failing in such cases from community.general 9.0.0 on.
    type: bool
    version_added: 5.8.0

notes:
  - >
    B(ATTENTION - DEPRECATION): Support for Django releases older than 4.1 will be removed in
    community.general version 9.0.0 (estimated to be released in May 2024).
    Please notice that Django 4.1 requires Python 3.8 or greater.
  - C(virtualenv) (U(http://www.virtualenv.org)) must be installed on the remote host if the O(virtualenv) parameter
    is specified. This requirement is deprecated and will be removed in community.general version 9.0.0.
  - This module will create a virtualenv if the O(virtualenv) parameter is specified and a virtual environment does not already
    exist at the given location. This behavior is deprecated and will be removed in community.general version 9.0.0.
  - The parameter O(virtualenv) will remain in use, but it will require the specified virtualenv to exist.
    The recommended way to create one in Ansible is by using M(ansible.builtin.pip).
  - This module assumes English error messages for the V(createcachetable) command to detect table existence,
    unfortunately.
  - To be able to use the V(migrate) command with django versions < 1.7, you must have C(south) installed and added
    as an app in your settings.
  - To be able to use the V(collectstatic) command, you must have enabled staticfiles in your settings.
  - Your C(manage.py) application must be executable (C(rwxr-xr-x)), and must have a valid shebang,
    for example C(#!/usr/bin/env python), for invoking the appropriate Python interpreter.
seealso:
  - name: django-admin and manage.py Reference
    description: Reference for C(django-admin) or C(manage.py) commands.
    link: https://docs.djangoproject.com/en/4.1/ref/django-admin/
  - name: Django Download page
    description: The page showing how to get Django and the timeline of supported releases.
    link: https://www.djangoproject.com/download/
  - name: What Python version can I use with Django?
    description: From the Django FAQ, the response to Python requirements for the framework.
    link: https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django
requirements: [ "virtualenv", "django" ]
author:
  - Alexei Znamensky (@russoz)
  - Scott Anderson (@tastychutney)
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
        # In version 9.0.0, if the venv is not found, it should fail_json() here.
        if not module.params['ack_venv_creation_deprecation']:
            module.deprecate(
                'The behavior of "creating the virtual environment when missing" is being '
                'deprecated and will be removed in community.general version 9.0.0. '
                'Set the module parameter `ack_venv_creation_deprecation: true` to '
                'prevent this message from showing up when creating a virtualenv.',
                version='9.0.0',
                collection_name='community.general',
            )

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
            ack_venv_creation_deprecation=dict(type='bool'),
        ),
    )

    command_split = shlex.split(module.params['command'])
    command_bin = command_split[0]
    project_path = module.params['project_path']
    virtualenv = module.params['virtualenv']

    try:
        _deprecation = dict(
            cleanup="clearsessions",
            syncdb="migrate",
            validate="check",
        )
        module.deprecate(
            'The command {0} has been deprecated as it is no longer supported in recent Django versions.'
            'Please use the command {1} instead that provide similar capability.'.format(command_bin, _deprecation[command_bin]),
            version='9.0.0',
            collection_name='community.general'
        )
    except KeyError:
        pass

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
