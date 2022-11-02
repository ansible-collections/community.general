# -*- coding: utf-8 -*-
# Copyright (c) 2017, Patrick Deelman <patrick@patrickdeelman.nl>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
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
      - To avoid problems when accessing multiple secrets at once, add C(auto-expand-secmem) to
        C(~/.gnupg/gpg-agent.conf). Where this is not possible, consider using I(lock=readwrite) instead.
    options:
      _terms:
        description: query key.
        required: true
      directory:
        description:
          - The directory of the password store.
          - If I(backend=pass), the default is C(~/.password-store) is used.
          - If I(backend=gopass), then the default is the C(path) field in C(~/.config/gopass/config.yml),
            falling back to C(~/.local/share/gopass/stores/root) if C(path) is not defined in the gopass config.
        type: path
        vars:
          - name: passwordstore
        env:
          - name: PASSWORD_STORE_DIR
      create:
        description: Create the password if it does not already exist. Takes precedence over C(missing).
        type: bool
        default: false
      overwrite:
        description: Overwrite the password if it does already exist.
        type: bool
        default: false
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
        default: false
      subkey:
        description: Return a specific subkey of the password. When set to C(password), always returns the first line.
        type: str
        default: password
      userpass:
        description: Specify a password to save, instead of a generated one.
        type: str
      length:
        description: The length of the generated password.
        type: integer
        default: 16
      backup:
        description: Used with C(overwrite=true). Backup the previous password in a subkey.
        type: bool
        default: false
      nosymbols:
        description: Use alphanumeric characters.
        type: bool
        default: false
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
      lock:
        description:
          - How to synchronize operations.
          - The default of C(write) only synchronizes write operations.
          - C(readwrite) synchronizes all operations (including read). This makes sure that gpg-agent is never called in parallel.
          - C(none) does not do any synchronization.
        ini:
          - section: passwordstore_lookup
            key: lock
        type: str
        default: write
        choices:
          - readwrite
          - write
          - none
        version_added: 4.5.0
      locktimeout:
        description:
          - Lock timeout applied when I(lock) is not C(none).
          - Time with a unit suffix, C(s), C(m), C(h) for seconds, minutes, and hours, respectively. For example, C(900s) equals C(15m).
          - Correlates with C(pinentry-timeout) in C(~/.gnupg/gpg-agent.conf), see C(man gpg-agent) for details.
        ini:
          - section: passwordstore_lookup
            key: locktimeout
        type: str
        default: 15m
        version_added: 4.5.0
      backend:
        description:
          - Specify which backend to use.
          - Defaults to C(pass), passwordstore.org's original pass utility.
          - C(gopass) support is incomplete.
        ini:
          - section: passwordstore_lookup
            key: backend
        vars:
          - name: passwordstore_backend
        type: str
        default: pass
        choices:
          - pass
          - gopass
        version_added: 5.2.0
    notes:
      - The lookup supports passing all options as lookup parameters since community.general 6.0.0.
'''
EXAMPLES = """
ansible.cfg: |
  [passwordstore_lookup]
  lock=readwrite
  locktimeout=45s

tasks.yml: |
  ---

  # Debug is used for examples, BAD IDEA to show passwords on screen
  - name: Basic lookup. Fails if example/test does not exist
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test')}}"

  - name: Basic lookup. Warns if example/test does not exist and returns empty string
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test', missing='warn')}}"

  - name: Create pass with random 16 character password. If password exists just give the password
    ansible.builtin.debug:
      var: mypassword
    vars:
      mypassword: "{{ lookup('community.general.passwordstore', 'example/test', create=true)}}"

  - name: Create pass with random 16 character password. If password exists just give the password
    ansible.builtin.debug:
      var: mypassword
    vars:
      mypassword: "{{ lookup('community.general.passwordstore', 'example/test', missing='create')}}"

  - name: Prints 'abc' if example/test does not exist, just give the password otherwise
    ansible.builtin.debug:
      var: mypassword
    vars:
      mypassword: >-
        {{ lookup('community.general.passwordstore', 'example/test', missing='empty')
           | default('abc', true) }}

  - name: Different size password
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test', create=true, length=42)}}"

  - name: >-
      Create password and overwrite the password if it exists.
      As a bonus, this module includes the old password inside the pass file
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test', create=true, overwrite=true)}}"

  - name: Create an alphanumeric password
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test', create=true, nosymbols=true) }}"

  - name: Return the value for user in the KV pair user, username
    ansible.builtin.debug:
      msg: "{{ lookup('community.general.passwordstore', 'example/test', subkey='user')}}"

  - name: Return the entire password file content
    ansible.builtin.set_fact:
      passfilecontent: "{{ lookup('community.general.passwordstore', 'example/test', returnall=true)}}"
"""

RETURN = """
_raw:
  description:
    - a password
  type: list
  elements: str
"""

from contextlib import contextmanager
import os
import re
import subprocess
import time
import yaml

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils.common.file import FileLock
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.utils.display import Display
from ansible.utils.encrypt import random_password
from ansible.plugins.lookup import LookupBase
from ansible import constants as C

display = Display()


# backhacked check_output with input for python 2.7
# http://stackoverflow.com/questions/10103551/passing-data-to-subprocess-check-output
# note: contains special logic for calling 'pass', so not a drop-in replacement for check_output
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
    if retcode == 0 and (b'encryption failed: Unusable public key' in b_out or
                         b'encryption failed: Unusable public key' in b_err):
        retcode = 78  # os.EX_CONFIG
    if retcode != 0:
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
    def __init__(self, loader=None, templar=None, **kwargs):

        super(LookupModule, self).__init__(loader, templar, **kwargs)
        self.realpass = None

    def is_real_pass(self):
        if self.realpass is None:
            try:
                passoutput = to_text(
                    check_output2([self.pass_cmd, "--version"], env=self.env),
                    errors='surrogate_or_strict'
                )
                self.realpass = 'pass: the standard unix password manager' in passoutput
            except (subprocess.CalledProcessError) as e:
                raise AnsibleError('exit code {0} while running {1}. Error output: {2}'.format(e.returncode, e.cmd, e.output))

        return self.realpass

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
                        self.paramvals[key] = boolean(self.paramvals[key])
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
            self.env['LANGUAGE'] = 'C'  # make sure to get errors in English as required by check_output2

            if self.backend == 'gopass':
                self.env['GOPASS_NO_REMINDER'] = "YES"
            elif os.path.isdir(self.paramvals['directory']):
                # Set PASSWORD_STORE_DIR
                self.env['PASSWORD_STORE_DIR'] = self.paramvals['directory']
            elif self.is_real_pass():
                raise AnsibleError('Passwordstore directory \'{0}\' does not exist'.format(self.paramvals['directory']))

            # Set PASSWORD_STORE_UMASK if umask is set
            if self.paramvals.get('umask') is not None:
                if len(self.paramvals['umask']) != 3:
                    raise AnsibleError('Passwordstore umask must have a length of 3.')
                elif int(self.paramvals['umask'][0]) > 3:
                    raise AnsibleError('Passwordstore umask not allowed (password not user readable).')
                else:
                    self.env['PASSWORD_STORE_UMASK'] = self.paramvals['umask']

    def check_pass(self):
        try:
            self.passoutput = to_text(
                check_output2([self.pass_cmd, 'show'] +
                              [self.passname], env=self.env),
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
            if (self.backend == 'gopass' or
                    os.path.isfile(os.path.join(self.paramvals['directory'], self.passname + ".gpg"))
                    or not self.is_real_pass()):
                # When using real pass, only accept password as found if there is a .gpg file for it (might be a tree node otherwise)
                return True
        except (subprocess.CalledProcessError) as e:
            # 'not in password store' is the expected error if a password wasn't found
            if 'not in the password store' not in e.output:
                raise AnsibleError('exit code {0} while running {1}. Error output: {2}'.format(e.returncode, e.cmd, e.output))

        if self.paramvals['missing'] == 'error':
            raise AnsibleError('passwordstore: passname {0} not found and missing=error is set'.format(self.passname))
        elif self.paramvals['missing'] == 'warn':
            display.warning('passwordstore: passname {0} not found'.format(self.passname))

        return False

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
            check_output2([self.pass_cmd, 'insert', '-f', '-m', self.passname], input=msg, env=self.env)
        except (subprocess.CalledProcessError) as e:
            raise AnsibleError('exit code {0} while running {1}. Error output: {2}'.format(e.returncode, e.cmd, e.output))
        return newpass

    def generate_password(self):
        # generate new file and insert lookup_pass: Generated by Ansible on {date}
        # use pwgen to generate the password and insert values with pass -m
        newpass = self.get_newpass()
        datetime = time.strftime("%d/%m/%Y %H:%M:%S")
        msg = newpass + '\n' + "lookup_pass: First generated by ansible on {0}\n".format(datetime)
        try:
            check_output2([self.pass_cmd, 'insert', '-f', '-m', self.passname], input=msg, env=self.env)
        except (subprocess.CalledProcessError) as e:
            raise AnsibleError('exit code {0} while running {1}. Error output: {2}'.format(e.returncode, e.cmd, e.output))
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

    @contextmanager
    def opt_lock(self, type):
        if self.get_option('lock') == type:
            tmpdir = os.environ.get('TMPDIR', '/tmp')
            lockfile = os.path.join(tmpdir, '.passwordstore.lock')
            with FileLock().lock_file(lockfile, tmpdir, self.lock_timeout):
                self.locked = type
                yield
            self.locked = None
        else:
            yield

    def setup(self, variables):
        self.backend = self.get_option('backend')
        self.pass_cmd = self.backend  # pass and gopass are commands as well
        self.locked = None
        timeout = self.get_option('locktimeout')
        if not re.match('^[0-9]+[smh]$', timeout):
            raise AnsibleError("{0} is not a correct value for locktimeout".format(timeout))
        unit_to_seconds = {"s": 1, "m": 60, "h": 3600}
        self.lock_timeout = int(timeout[:-1]) * unit_to_seconds[timeout[-1]]

        directory = self.get_option('directory')
        if directory is None:
            if self.backend == 'gopass':
                try:
                    with open(os.path.expanduser('~/.config/gopass/config.yml')) as f:
                        directory = yaml.safe_load(f)['path']
                except (FileNotFoundError, KeyError, yaml.YAMLError):
                    directory = os.path.expanduser('~/.local/share/gopass/stores/root')
            else:
                directory = os.path.expanduser('~/.password-store')

        self.paramvals = {
            'subkey': self.get_option('subkey'),
            'directory': directory,
            'create': self.get_option('create'),
            'returnall': self.get_option('returnall'),
            'overwrite': self.get_option('overwrite'),
            'nosymbols': self.get_option('nosymbols'),
            'userpass': self.get_option('userpass') or '',
            'length': self.get_option('length'),
            'backup': self.get_option('backup'),
            'missing': self.get_option('missing'),
            'umask': self.get_option('umask'),
        }

    def run(self, terms, variables, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        self.setup(variables)
        result = []

        for term in terms:
            self.parse_params(term)   # parse the input into paramvals
            with self.opt_lock('readwrite'):
                if self.check_pass():     # password exists
                    if self.paramvals['overwrite'] and self.paramvals['subkey'] == 'password':
                        with self.opt_lock('write'):
                            result.append(self.update_password())
                    else:
                        result.append(self.get_passresult())
                else:                     # password does not exist
                    if self.paramvals['missing'] == 'create':
                        with self.opt_lock('write'):
                            if self.locked == 'write' and self.check_pass():  # lookup password again if under write lock
                                result.append(self.get_passresult())
                            else:
                                result.append(self.generate_password())
                    else:
                        result.append(None)

        return result
