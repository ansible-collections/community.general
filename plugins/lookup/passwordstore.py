# -*- coding: utf-8 -*-
# (c) 2017, Patrick Deelman <patrick@patrickdeelman.nl>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
    name: passwordstore
    author:
      - Patrick Deelman (!UNKNOWN) <patrick@patrickdeelman.nl>
    short_description: manage passwords with passwordstore.org's pass utility
    description:
      - Enables Ansible to retrieve, create or update passwords from the passwordstore.org pass utility.
        It also retrieves YAML style keys stored as multilines in the passwordfile.
    options:
      _terms:
        description: query key.
        required: True
      passwordstore:
        description: location of the password store.
        default: '~/.password-store'
      directory:
        description: The directory of the password store.
        env:
          - name: PASSWORD_STORE_DIR
      create:
        description: Create the password if it does not already exist. Takes precedence over C(missing).
        type: bool
        default: false
      overwrite:
        description: Overwrite the password if it does already exist.
        type: bool
        default: 'no'
      umask:
        description:
          - Sets the umask for the created .gpg files. The first octed must be greater than 3 (user readable).
          - Note pass' default value is C('077').
        env:
          - name: PASSWORD_STORE_UMASK
        version_added: 1.3.0
      returnall:
        description: Return all the content of the password, not only the first line.
        type: bool
        default: 'no'
      subkey:
        description: Return a specific subkey of the password. When set to C(password), always returns the first line.
        default: password
      userpass:
        description: Specify a password to save, instead of a generated one.
      length:
        description: The length of the generated password.
        type: integer
        default: 16
      backup:
        description: Used with C(overwrite=yes). Backup the previous password in a subkey.
        type: bool
        default: 'no'
      nosymbols:
        description: use alphanumeric characters.
        type: bool
        default: 'no'
      missing:
        description:
          - List of preference about what to do if the password file is missing.
          - If I(create=true), the value for this option is ignored and assumed to be C(create).
          - If set to C(error), the lookup will error out if the passname does not exist.
          - If set to C(create), the passname will be created with the provided length I(length) if it does not exist.
          - If set to C(empty) or C(warn), will return a C(none) in case the passname does not exist.
            When using C(lookup) and not C(query), this will be translated to an empty string.
        version_added: 3.1.0
        type: str
        default: error
        choices:
          - error
          - warn
          - empty
          - create
'''
EXAMPLES = """
# Debug is used for examples, BAD IDEA to show passwords on screen
- name: Basic lookup. Fails if example/test doesn't exist
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test')}}"

- name: Basic lookup. Warns if example/test does not exist and returns empty string
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test missing=warn')}}"

- name: Create pass with random 16 character password. If password exists just give the password
  ansible.builtin.debug:
    var: mypassword
  vars:
    mypassword: "{{ lookup('community.general.passwordstore', 'example/test create=true')}}"

- name: Create pass with random 16 character password. If password exists just give the password
  ansible.builtin.debug:
    var: mypassword
  vars:
    mypassword: "{{ lookup('community.general.passwordstore', 'example/test missing=create')}}"

- name: Prints 'abc' if example/test does not exist, just give the password otherwise
  ansible.builtin.debug:
    var: mypassword
  vars:
    mypassword: "{{ lookup('community.general.passwordstore', 'example/test missing=empty') | default('abc', true) }}"

- name: Different size password
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test create=true length=42')}}"

- name: Create password and overwrite the password if it exists. As a bonus, this module includes the old password inside the pass file
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test create=true overwrite=true')}}"

- name: Create an alphanumeric password
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test create=true nosymbols=true') }}"

- name: Return the value for user in the KV pair user, username
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.passwordstore', 'example/test subkey=user')}}"

- name: Return the entire password file content
  ansible.builtin.set_fact:
    passfilecontent: "{{ lookup('community.general.passwordstore', 'example/test returnall=true')}}"
"""

RETURN = """
_raw:
  description:
    - a password
  type: list
  elements: str
"""

import os
import subprocess
import time
import yaml


from distutils import util
from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.utils.display import Display
from ansible.utils.encrypt import random_password
from ansible.plugins.lookup import LookupBase
from ansible import constants as C

display = Display()


# backhacked check_output with input for python 2.7
# http://stackoverflow.com/questions/10103551/passing-data-to-subprocess-check-output
def check_output2(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    if 'stderr' in kwargs:
        raise ValueError('stderr argument not allowed, it will be overridden.')
    if 'input' in kwargs:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        b_inputdata = to_bytes(kwargs['input'], errors='surrogate_or_strict')
        del kwargs['input']
        kwargs['stdin'] = subprocess.PIPE
    else:
        b_inputdata = None
    process = subprocess.Popen(*popenargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    try:
        b_out, b_err = process.communicate(b_inputdata)
    except Exception:
        process.kill()
        process.wait()
        raise
    retcode = process.poll()
    if retcode != 0 or \
            b'encryption failed: Unusable public key' in b_out or \
            b'encryption failed: Unusable public key' in b_err:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(
            retcode,
            cmd,
            to_native(b_out + b_err, errors='surrogate_or_strict')
        )
    return b_out


class LookupModule(LookupBase):
    def parse_params(self, term):
        # I went with the "traditional" param followed with space separated KV pairs.
        # Waiting for final implementation of lookup parameter parsing.
        # See: https://github.com/ansible/ansible/issues/12255
        params = term.split()
        if len(params) > 0:
            # the first param is the pass-name
            self.passname = params[0]
            # next parse the optional parameters in keyvalue pairs
            try:
                for param in params[1:]:
                    name, value = param.split('=', 1)
                    if name not in self.paramvals:
                        raise AnsibleAssertionError('%s not in paramvals' % name)
                    self.paramvals[name] = value
            except (ValueError, AssertionError) as e:
                raise AnsibleError(e)
            # check and convert values
            try:
                for key in ['create', 'returnall', 'overwrite', 'backup', 'nosymbols']:
                    if not isinstance(self.paramvals[key], bool):
                        self.paramvals[key] = util.strtobool(self.paramvals[key])
            except (ValueError, AssertionError) as e:
                raise AnsibleError(e)
            if self.paramvals['missing'] not in ['error', 'warn', 'create', 'empty']:
                raise AnsibleError("{0} is not a valid option for missing".format(self.paramvals['missing']))
            if not isinstance(self.paramvals['length'], int):
                if self.paramvals['length'].isdigit():
                    self.paramvals['length'] = int(self.paramvals['length'])
                else:
                    raise AnsibleError("{0} is not a correct value for length".format(self.paramvals['length']))

            if self.paramvals['create']:
                self.paramvals['missing'] = 'create'

            # Collect pass environment variables from the plugin's parameters.
            self.env = os.environ.copy()

            # Set PASSWORD_STORE_DIR if directory is set
            if self.paramvals['directory']:
                if os.path.isdir(self.paramvals['directory']):
                    self.env['PASSWORD_STORE_DIR'] = self.paramvals['directory']
                else:
                    raise AnsibleError('Passwordstore directory \'{0}\' does not exist'.format(self.paramvals['directory']))

            # Set PASSWORD_STORE_UMASK if umask is set
            if 'umask' in self.paramvals:
                if len(self.paramvals['umask']) != 3:
                    raise AnsibleError('Passwordstore umask must have a length of 3.')
                elif int(self.paramvals['umask'][0]) > 3:
                    raise AnsibleError('Passwordstore umask not allowed (password not user readable).')
                else:
                    self.env['PASSWORD_STORE_UMASK'] = self.paramvals['umask']

    def check_pass(self):
        try:
            self.passoutput = to_text(
                check_output2(["pass", "show", self.passname], env=self.env),
                errors='surrogate_or_strict'
            ).splitlines()
            self.password = self.passoutput[0]
            self.passdict = {}
            try:
                values = yaml.safe_load('\n'.join(self.passoutput[1:]))
                for key, item in values.items():
                    self.passdict[key] = item
            except (yaml.YAMLError, AttributeError):
                for line in self.passoutput[1:]:
                    if ':' in line:
                        name, value = line.split(':', 1)
                        self.passdict[name.strip()] = value.strip()
        except (subprocess.CalledProcessError) as e:
            if e.returncode != 0 and 'not in the password store' in e.output:
                # if pass returns 1 and return string contains 'is not in the password store.'
                # We need to determine if this is valid or Error.
                if self.paramvals['missing'] == 'error':
                    raise AnsibleError('passwordstore: passname {0} not found and missing=error is set'.format(self.passname))
                else:
                    if self.paramvals['missing'] == 'warn':
                        display.warning('passwordstore: passname {0} not found'.format(self.passname))
                    return False
            else:
                raise AnsibleError(e)
        return True

    def get_newpass(self):
        if self.paramvals['nosymbols']:
            chars = C.DEFAULT_PASSWORD_CHARS[:62]
        else:
            chars = C.DEFAULT_PASSWORD_CHARS

        if self.paramvals['userpass']:
            newpass = self.paramvals['userpass']
        else:
            newpass = random_password(length=self.paramvals['length'], chars=chars)
        return newpass

    def update_password(self):
        # generate new password, insert old lines from current result and return new password
        newpass = self.get_newpass()
        datetime = time.strftime("%d/%m/%Y %H:%M:%S")
        msg = newpass + '\n'
        if self.passoutput[1:]:
            msg += '\n'.join(self.passoutput[1:]) + '\n'
        if self.paramvals['backup']:
            msg += "lookup_pass: old password was {0} (Updated on {1})\n".format(self.password, datetime)
        try:
            check_output2(['pass', 'insert', '-f', '-m', self.passname], input=msg, env=self.env)
        except (subprocess.CalledProcessError) as e:
            raise AnsibleError(e)
        return newpass

    def generate_password(self):
        # generate new file and insert lookup_pass: Generated by Ansible on {date}
        # use pwgen to generate the password and insert values with pass -m
        newpass = self.get_newpass()
        datetime = time.strftime("%d/%m/%Y %H:%M:%S")
        msg = newpass + '\n' + "lookup_pass: First generated by ansible on {0}\n".format(datetime)
        try:
            check_output2(['pass', 'insert', '-f', '-m', self.passname], input=msg, env=self.env)
        except (subprocess.CalledProcessError) as e:
            raise AnsibleError(e)
        return newpass

    def get_passresult(self):
        if self.paramvals['returnall']:
            return os.linesep.join(self.passoutput)
        if self.paramvals['subkey'] == 'password':
            return self.password
        else:
            if self.paramvals['subkey'] in self.passdict:
                return self.passdict[self.paramvals['subkey']]
            else:
                return None

    def run(self, terms, variables, **kwargs):
        result = []
        self.paramvals = {
            'subkey': 'password',
            'directory': variables.get('passwordstore'),
            'create': False,
            'returnall': False,
            'overwrite': False,
            'nosymbols': False,
            'userpass': '',
            'length': 16,
            'backup': False,
            'missing': 'error',
        }

        for term in terms:
            self.parse_params(term)   # parse the input into paramvals
            if self.check_pass():     # password exists
                if self.paramvals['overwrite'] and self.paramvals['subkey'] == 'password':
                    result.append(self.update_password())
                else:
                    result.append(self.get_passresult())
            else:                     # password does not exist
                if self.paramvals['missing'] == 'create':
                    result.append(self.generate_password())
                else:
                    result.append(None)

        return result
