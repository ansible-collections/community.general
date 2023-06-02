#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2015, Linus Unnebäck <linus@folkdatorn.se>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: make
short_description: Run targets in a Makefile
requirements:
- make
author: Linus Unnebäck (@LinusU) <linus@folkdatorn.se>
description:
  - Run targets in a Makefile.
options:
  target:
    description:
      - The target to run.
      - Typically this would be something like C(install),C(test) or C(all)."
    type: str
  params:
    description:
      - Any extra parameters to pass to make.
    type: dict
  chdir:
    description:
      - Change to this directory before running make.
    type: path
    required: true
  file:
    description:
      - Use a custom Makefile.
    type: path
  make:
    description:
      - Use a specific make binary.
    type: path
    version_added: '0.2.0'
'''

EXAMPLES = r'''
- name: Build the default target
  community.general.make:
    chdir: /home/ubuntu/cool-project

- name: Run 'install' target as root
  community.general.make:
    chdir: /home/ubuntu/cool-project
    target: install
  become: yes

- name: Build 'all' target with extra arguments
  community.general.make:
    chdir: /home/ubuntu/cool-project
    target: all
    params:
      NUM_THREADS: 4
      BACKEND: lapack

- name: Build 'all' target with a custom Makefile
  community.general.make:
    chdir: /home/ubuntu/cool-project
    target: all
    file: /some-project/Makefile
'''

RETURN = r'''# '''

from ansible.module_utils.six import iteritems
from ansible.module_utils.basic import AnsibleModule


def run_command(command, module, check_rc=True):
    """
    Run a command using the module, return
    the result code and std{err,out} content.

    :param command: list of command arguments
    :param module: Ansible make module instance
    :return: return code, stdout content, stderr content
    """
    rc, out, err = module.run_command(command, check_rc=check_rc, cwd=module.params['chdir'])
    return rc, sanitize_output(out), sanitize_output(err)


def sanitize_output(output):
    """
    Sanitize the output string before we
    pass it to module.fail_json. Defaults
    the string to empty if it is None, else
    strips trailing newlines.

    :param output: output to sanitize
    :return: sanitized output
    """
    if output is None:
        return ''
    else:
        return output.rstrip("\r\n")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            target=dict(type='str'),
            params=dict(type='dict'),
            chdir=dict(type='path', required=True),
            file=dict(type='path'),
            make=dict(type='path'),
        ),
        supports_check_mode=True,
    )

    make_path = module.params['make']
    if make_path is None:
        # Build up the invocation of `make` we are going to use
        # For non-Linux OSes, prefer gmake (GNU make) over make
        make_path = module.get_bin_path('gmake', required=False)
        if not make_path:
            # Fall back to system make
            make_path = module.get_bin_path('make', required=True)
    make_target = module.params['target']
    if module.params['params'] is not None:
        make_parameters = [k + '=' + str(v) for k, v in iteritems(module.params['params'])]
    else:
        make_parameters = []

    if module.params['file'] is not None:
        base_command = [make_path, "-f", module.params['file'], make_target]
    else:
        base_command = [make_path, make_target]
    base_command.extend(make_parameters)

    # Check if the target is already up to date
    rc, out, err = run_command(base_command + ['-q'], module, check_rc=False)
    if module.check_mode:
        # If we've been asked to do a dry run, we only need
        # to report whether or not the target is up to date
        changed = (rc != 0)
    else:
        if rc == 0:
            # The target is up to date, so we don't have to
            #  do anything
            changed = False
        else:
            # The target isn't up to date, so we need to run it
            rc, out, err = run_command(base_command, module,
                                       check_rc=True)
            changed = True

    # We don't report the return code, as if this module failed
    # we would be calling fail_json from run_command, so even if
    # we had a non-zero return code, we did not fail. However, if
    # we report a non-zero return code here, we will be marked as
    # failed regardless of what we signal using the failed= kwarg.
    module.exit_json(
        changed=changed,
        failed=False,
        stdout=out,
        stderr=err,
        target=module.params['target'],
        params=module.params['params'],
        chdir=module.params['chdir'],
        file=module.params['file']
    )


if __name__ == '__main__':
    main()
