#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: luks_device

short_description: Manage encrypted (LUKS) devices


description:
    - "Module manages L(LUKS,https://en.wikipedia.org/wiki/Linux_Unified_Key_Setup)
      on given device. Supports creating, destroying, opening and closing of
      LUKS container and adding or removing new keys and passphrases."

options:
    device:
        description:
            - "Device to work with (e.g. C(/dev/sda1)). Needed in most cases.
              Can be omitted only when I(state=closed) together with I(name)
              is provided."
        type: str
    state:
        description:
            - "Desired state of the LUKS container. Based on its value creates,
              destroys, opens or closes the LUKS container on a given device."
            - "I(present) will create LUKS container unless already present.
              Requires I(device) and either I(keyfile) or I(passphrase) options
              to be provided."
            - "I(absent) will remove existing LUKS container if it exists.
              Requires I(device) or I(name) to be specified."
            - "I(opened) will unlock the LUKS container. If it does not exist
              it will be created first.
              Requires I(device) and either I(keyfile) or I(passphrase)
              to be specified. Use the I(name) option to set the name of
              the opened container.  Otherwise the name will be
              generated automatically and returned as a part of the
              result."
            - "I(closed) will lock the LUKS container. However if the container
              does not exist it will be created.
              Requires I(device) and either I(keyfile) or I(passphrase)
              options to be provided. If container does already exist
              I(device) or I(name) will suffice."
        type: str
        default: present
        choices: [present, absent, opened, closed]
    name:
        description:
            - "Sets container name when I(state=opened). Can be used
              instead of I(device) when closing the existing container
              (i.e. when I(state=closed))."
        type: str
    keyfile:
        description:
            - "Used to unlock the container. Either a I(keyfile) or a
              I(passphrase) is needed for most of the operations. Parameter
              value is the path to the keyfile with the passphrase."
            - "BEWARE that working with keyfiles in plaintext is dangerous.
              Make sure that they are protected."
        type: path
    passphrase:
        description:
            - "Used to unlock the container. Either a I(passphrase) or a
              I(keyfile) is needed for most of the operations. Parameter
              value is a string with the passphrase."
        type: str
    keysize:
        description:
            - "Sets the key size only if LUKS container does not exist."
        type: int
    new_keyfile:
        description:
            - "Adds additional key to given container on I(device).
              Needs I(keyfile) or I(passphrase) option for authorization.
              LUKS container supports up to 8 keyslots. Parameter value
              is the path to the keyfile with the passphrase."
            - "NOTE that adding additional keys is *not idempotent*.
              A new keyslot will be used even if another keyslot already
              exists for this keyfile."
            - "BEWARE that working with keyfiles in plaintext is dangerous.
              Make sure that they are protected."
        type: path
    new_passphrase:
        description:
            - "Adds additional passphrase to given container on I(device).
              Needs I(keyfile) or I(passphrase) option for authorization. LUKS
              container supports up to 8 keyslots. Parameter value is a string
              with the new passphrase."
            - "NOTE that adding additional passphrase is *not idempotent*.  A
              new keyslot will be used even if another keyslot already exists
              for this passphrase."
        type: str
    remove_keyfile:
        description:
            - "Removes given key from the container on I(device). Does not
              remove the keyfile from filesystem.
              Parameter value is the path to the keyfile with the passphrase."
            - "NOTE that removing keys is *not idempotent*. Trying to remove
              a key which no longer exists results in an error."
            - "NOTE that to remove the last key from a LUKS container, the
              I(force_remove_last_key) option must be set to C(yes)."
            - "BEWARE that working with keyfiles in plaintext is dangerous.
              Make sure that they are protected."
        type: path
    remove_passphrase:
        description:
            - "Removes given passphrase from the container on I(device).
              Parameter value is a string with the passphrase to remove."
            - "NOTE that removing passphrases is I(not
              idempotent). Trying to remove a passphrase which no longer
              exists results in an error."
            - "NOTE that to remove the last keyslot from a LUKS
              container, the I(force_remove_last_key) option must be set
              to C(yes)."
        type: str
    force_remove_last_key:
        description:
            - "If set to C(yes), allows removing the last key from a container."
            - "BEWARE that when the last key has been removed from a container,
              the container can no longer be opened!"
        type: bool
        default: no
    label:
        description:
            - "This option allow the user to create a LUKS2 format container
              with label support, respectively to identify the container by
              label on later usages."
            - "Will only be used on container creation, or when I(device) is
              not specified."
            - "This cannot be specified if I(type) is set to C(luks1)."
        type: str
    uuid:
        description:
            - "With this option user can identify the LUKS container by UUID."
            - "Will only be used when I(device) and I(label) are not specified."
        type: str
    type:
        description:
            - "This option allow the user explicit define the format of LUKS
              container that wants to work with. Options are C(luks1) or C(luks2)"
        type: str
        choices: [luks1, luks2]



requirements:
    - "cryptsetup"
    - "wipefs (when I(state) is C(absent))"
    - "lsblk"
    - "blkid (when I(label) or I(uuid) options are used)"

author: Jan Pokorny (@japokorn)
'''

EXAMPLES = '''

- name: create LUKS container (remains unchanged if it already exists)
  luks_device:
    device: "/dev/loop0"
    state: "present"
    keyfile: "/vault/keyfile"

- name: create LUKS container with a passphrase
  luks_device:
    device: "/dev/loop0"
    state: "present"
    passphrase: "foo"

- name: (create and) open the LUKS container; name it "mycrypt"
  luks_device:
    device: "/dev/loop0"
    state: "opened"
    name: "mycrypt"
    keyfile: "/vault/keyfile"

- name: close the existing LUKS container "mycrypt"
  luks_device:
    state: "closed"
    name: "mycrypt"

- name: make sure LUKS container exists and is closed
  luks_device:
    device: "/dev/loop0"
    state: "closed"
    keyfile: "/vault/keyfile"

- name: create container if it does not exist and add new key to it
  luks_device:
    device: "/dev/loop0"
    state: "present"
    keyfile: "/vault/keyfile"
    new_keyfile: "/vault/keyfile2"

- name: add new key to the LUKS container (container has to exist)
  luks_device:
    device: "/dev/loop0"
    keyfile: "/vault/keyfile"
    new_keyfile: "/vault/keyfile2"

- name: add new passphrase to the LUKS container
  luks_device:
    device: "/dev/loop0"
    keyfile: "/vault/keyfile"
    new_passphrase: "foo"

- name: remove existing keyfile from the LUKS container
  luks_device:
    device: "/dev/loop0"
    remove_keyfile: "/vault/keyfile2"

- name: remove existing passphrase from the LUKS container
  luks_device:
    device: "/dev/loop0"
    remove_passphrase: "foo"

- name: completely remove the LUKS container and its contents
  luks_device:
    device: "/dev/loop0"
    state: "absent"

- name: create a container with label
  luks_device:
    device: "/dev/loop0"
    state: "present"
    keyfile: "/vault/keyfile"
    label: personalLabelName

- name: open the LUKS container based on label without device; name it "mycrypt"
  luks_device:
    label: "personalLabelName"
    state: "opened"
    name: "mycrypt"
    keyfile: "/vault/keyfile"

- name: close container based on UUID
  luks_device:
    uuid: 03ecd578-fad4-4e6c-9348-842e3e8fa340
    state: "closed"
    name: "mycrypt"

- name: create a container using luks2 format
  luks_device:
    device: "/dev/loop0"
    state: "present"
    keyfile: "/vault/keyfile"
    type: luks2
'''

RETURN = '''
name:
    description:
        When I(state=opened) returns (generated or given) name
        of LUKS container. Returns None if no name is supplied.
    returned: success
    type: str
    sample: "luks-c1da9a58-2fde-4256-9d9f-6ab008b4dd1b"
'''

import os
import re
import stat

from ansible.module_utils.basic import AnsibleModule

RETURN_CODE = 0
STDOUT = 1
STDERR = 2

# used to get <luks-name> out of lsblk output in format 'crypt <luks-name>'
# regex takes care of any possible blank characters
LUKS_NAME_REGEX = re.compile(r'\s*crypt\s+([^\s]*)\s*')
# used to get </luks/device> out of lsblk output
# in format 'device: </luks/device>'
LUKS_DEVICE_REGEX = re.compile(r'\s*device:\s+([^\s]*)\s*')


class Handler(object):

    def __init__(self, module):
        self._module = module
        self._lsblk_bin = self._module.get_bin_path('lsblk', True)

    def _run_command(self, command, data=None):
        return self._module.run_command(command, data=data)

    def get_device_by_uuid(self, uuid):
        ''' Returns the device that holds UUID passed by user
        '''
        self._blkid_bin = self._module.get_bin_path('blkid', True)
        uuid = self._module.params['uuid']
        if uuid is None:
            return None
        result = self._run_command([self._blkid_bin, '--uuid', uuid])
        if result[RETURN_CODE] != 0:
            return None
        return result[STDOUT].strip()

    def get_device_by_label(self, label):
        ''' Returns the device that holds label passed by user
        '''
        self._blkid_bin = self._module.get_bin_path('blkid', True)
        label = self._module.params['label']
        if label is None:
            return None
        result = self._run_command([self._blkid_bin, '--label', label])
        if result[RETURN_CODE] != 0:
            return None
        return result[STDOUT].strip()

    def generate_luks_name(self, device):
        ''' Generate name for luks based on device UUID ('luks-<UUID>').
            Raises ValueError when obtaining of UUID fails.
        '''
        result = self._run_command([self._lsblk_bin, '-n', device, '-o', 'UUID'])

        if result[RETURN_CODE] != 0:
            raise ValueError('Error while generating LUKS name for %s: %s'
                             % (device, result[STDERR]))
        dev_uuid = result[STDOUT].strip()
        return 'luks-%s' % dev_uuid


class CryptHandler(Handler):

    def __init__(self, module):
        super(CryptHandler, self).__init__(module)
        self._cryptsetup_bin = self._module.get_bin_path('cryptsetup', True)

    def get_container_name_by_device(self, device):
        ''' obtain LUKS container name based on the device where it is located
            return None if not found
            raise ValueError if lsblk command fails
        '''
        result = self._run_command([self._lsblk_bin, device, '-nlo', 'type,name'])
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while obtaining LUKS name for %s: %s'
                             % (device, result[STDERR]))

        m = LUKS_NAME_REGEX.search(result[STDOUT])

        try:
            name = m.group(1)
        except AttributeError:
            name = None
        return name

    def get_container_device_by_name(self, name):
        ''' obtain device name based on the LUKS container name
            return None if not found
            raise ValueError if lsblk command fails
        '''
        # apparently each device can have only one LUKS container on it
        result = self._run_command([self._cryptsetup_bin, 'status', name])
        if result[RETURN_CODE] != 0:
            return None

        m = LUKS_DEVICE_REGEX.search(result[STDOUT])
        device = m.group(1)
        return device

    def is_luks(self, device):
        ''' check if the LUKS container does exist
        '''
        result = self._run_command([self._cryptsetup_bin, 'isLuks', device])
        return result[RETURN_CODE] == 0

    def run_luks_create(self, device, keyfile, passphrase, keysize):
        # create a new luks container; use batch mode to auto confirm
        luks_type = self._module.params['type']
        label = self._module.params['label']

        options = []
        if keysize is not None:
            options.append('--key-size=' + str(keysize))
        if label is not None:
            options.extend(['--label', label])
            luks_type = 'luks2'
        if luks_type is not None:
            options.extend(['--type', luks_type])

        args = [self._cryptsetup_bin, 'luksFormat']
        args.extend(options)
        args.extend(['-q', device])
        if keyfile:
            args.append(keyfile)

        result = self._run_command(args, data=passphrase)
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while creating LUKS on %s: %s'
                             % (device, result[STDERR]))

    def run_luks_open(self, device, keyfile, passphrase, name):
        args = [self._cryptsetup_bin]
        if keyfile:
            args.extend(['--key-file', keyfile])
        args.extend(['open', '--type', 'luks', device, name])

        result = self._run_command(args, data=passphrase)
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while opening LUKS container on %s: %s'
                             % (device, result[STDERR]))

    def run_luks_close(self, name):
        result = self._run_command([self._cryptsetup_bin, 'close', name])
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while closing LUKS container %s' % (name))

    def run_luks_remove(self, device):
        wipefs_bin = self._module.get_bin_path('wipefs', True)

        name = self.get_container_name_by_device(device)
        if name is not None:
            self.run_luks_close(name)
        result = self._run_command([wipefs_bin, '--all', device])
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while wiping luks container %s: %s'
                             % (device, result[STDERR]))

    def run_luks_add_key(self, device, keyfile, passphrase, new_keyfile,
                         new_passphrase):
        ''' Add new key from a keyfile or passphrase to given 'device';
            authentication done using 'keyfile' or 'passphrase'.
            Raises ValueError when command fails.
        '''
        data = []
        args = [self._cryptsetup_bin, 'luksAddKey', device]

        if keyfile:
            args.extend(['--key-file', keyfile])
        else:
            data.append(passphrase)

        if new_keyfile:
            args.append(new_keyfile)
        else:
            data.extend([new_passphrase, new_passphrase])

        result = self._run_command(args, data='\n'.join(data) or None)
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while adding new LUKS keyslot to %s: %s'
                             % (device, result[STDERR]))

    def run_luks_remove_key(self, device, keyfile, passphrase,
                            force_remove_last_key=False):
        ''' Remove key from given device
            Raises ValueError when command fails
        '''
        if not force_remove_last_key:
            result = self._run_command([self._cryptsetup_bin, 'luksDump', device])
            if result[RETURN_CODE] != 0:
                raise ValueError('Error while dumping LUKS header from %s'
                                 % (device, ))
            keyslot_count = 0
            keyslot_area = False
            keyslot_re = re.compile(r'^Key Slot [0-9]+: ENABLED')
            for line in result[STDOUT].splitlines():
                if line.startswith('Keyslots:'):
                    keyslot_area = True
                elif line.startswith('  '):
                    # LUKS2 header dumps use human-readable indented output.
                    # Thus we have to look out for 'Keyslots:' and count the
                    # number of indented keyslot numbers.
                    if keyslot_area and line[2] in '0123456789':
                        keyslot_count += 1
                elif line.startswith('\t'):
                    pass
                elif keyslot_re.match(line):
                    # LUKS1 header dumps have one line per keyslot with ENABLED
                    # or DISABLED in them. We count such lines with ENABLED.
                    keyslot_count += 1
                else:
                    keyslot_area = False
            if keyslot_count < 2:
                self._module.fail_json(msg="LUKS device %s has less than two active keyslots. "
                                           "To be able to remove a key, please set "
                                           "`force_remove_last_key` to `yes`." % device)

        args = [self._cryptsetup_bin, 'luksRemoveKey', device, '-q']
        if keyfile:
            args.extend(['--key-file', keyfile])
        result = self._run_command(args, data=passphrase)
        if result[RETURN_CODE] != 0:
            raise ValueError('Error while removing LUKS key from %s: %s'
                             % (device, result[STDERR]))


class ConditionsHandler(Handler):

    def __init__(self, module, crypthandler):
        super(ConditionsHandler, self).__init__(module)
        self._crypthandler = crypthandler
        self.device = self.get_device_name()

    def get_device_name(self):
        device = self._module.params.get('device')
        label = self._module.params.get('label')
        uuid = self._module.params.get('uuid')
        name = self._module.params.get('name')

        if device is None and label is not None:
            device = self.get_device_by_label(label)
        elif device is None and uuid is not None:
            device = self.get_device_by_uuid(uuid)
        elif device is None and name is not None:
            device = self._crypthandler.get_container_device_by_name(name)

        return device

    def luks_create(self):
        return (self.device is not None and
                (self._module.params['keyfile'] is not None or
                 self._module.params['passphrase'] is not None) and
                self._module.params['state'] in ('present',
                                                 'opened',
                                                 'closed') and
                not self._crypthandler.is_luks(self.device))

    def opened_luks_name(self):
        ''' If luks is already opened, return its name.
            If 'name' parameter is specified and differs
            from obtained value, fail.
            Return None otherwise
        '''
        if self._module.params['state'] != 'opened':
            return None

        # try to obtain luks name - it may be already opened
        name = self._crypthandler.get_container_name_by_device(self.device)

        if name is None:
            # container is not open
            return None

        if self._module.params['name'] is None:
            # container is already opened
            return name

        if name != self._module.params['name']:
            # the container is already open but with different name:
            # suspicious. back off
            self._module.fail_json(msg="LUKS container is already opened "
                                   "under different name '%s'." % name)

        # container is opened and the names match
        return name

    def luks_open(self):
        if ((self._module.params['keyfile'] is None and
             self._module.params['passphrase'] is None) or
                self.device is None or
                self._module.params['state'] != 'opened'):
            # conditions for open not fulfilled
            return False

        name = self.opened_luks_name()

        if name is None:
            return True
        return False

    def luks_close(self):
        if ((self._module.params['name'] is None and self.device is None) or
                self._module.params['state'] != 'closed'):
            # conditions for close not fulfilled
            return False

        if self.device is not None:
            name = self._crypthandler.get_container_name_by_device(self.device)
            # successfully getting name based on device means that luks is open
            luks_is_open = name is not None

        if self._module.params['name'] is not None:
            self.device = self._crypthandler.get_container_device_by_name(
                self._module.params['name'])
            # successfully getting device based on name means that luks is open
            luks_is_open = self.device is not None

        return luks_is_open

    def luks_add_key(self):
        if (self.device is None or
                (self._module.params['keyfile'] is None and
                 self._module.params['passphrase'] is None) or
                (self._module.params['new_keyfile'] is None and
                 self._module.params['new_passphrase'] is None)):
            # conditions for adding a key not fulfilled
            return False

        if self._module.params['state'] == 'absent':
            self._module.fail_json(msg="Contradiction in setup: Asking to "
                                   "add a key to absent LUKS.")

        return True

    def luks_remove_key(self):
        if (self.device is None or
            (self._module.params['remove_keyfile'] is None and
             self._module.params['remove_passphrase'] is None)):
            # conditions for removing a key not fulfilled
            return False

        if self._module.params['state'] == 'absent':
            self._module.fail_json(msg="Contradiction in setup: Asking to "
                                   "remove a key from absent LUKS.")

        return True

    def luks_remove(self):
        return (self.device is not None and
                self._module.params['state'] == 'absent' and
                self._crypthandler.is_luks(self.device))


def run_module():
    # available arguments/parameters that a user can pass
    module_args = dict(
        state=dict(type='str', default='present', choices=['present', 'absent', 'opened', 'closed']),
        device=dict(type='str'),
        name=dict(type='str'),
        keyfile=dict(type='path'),
        new_keyfile=dict(type='path'),
        remove_keyfile=dict(type='path'),
        passphrase=dict(type='str', no_log=True),
        new_passphrase=dict(type='str', no_log=True),
        remove_passphrase=dict(type='str', no_log=True),
        force_remove_last_key=dict(type='bool', default=False),
        keysize=dict(type='int'),
        label=dict(type='str'),
        uuid=dict(type='str'),
        type=dict(type='str', choices=['luks1', 'luks2']),
    )

    mutually_exclusive = [
        ('keyfile', 'passphrase'),
        ('new_keyfile', 'new_passphrase'),
        ('remove_keyfile', 'remove_passphrase')
    ]

    # seed the result dict in the object
    result = dict(
        changed=False,
        name=None
    )

    module = AnsibleModule(argument_spec=module_args,
                           supports_check_mode=True,
                           mutually_exclusive=mutually_exclusive)

    if module.params['device'] is not None:
        try:
            statinfo = os.stat(module.params['device'])
            mode = statinfo.st_mode
            if not stat.S_ISBLK(mode) and not stat.S_ISCHR(mode):
                raise Exception('{0} is not a device'.format(module.params['device']))
        except Exception as e:
            module.fail_json(msg=str(e))

    crypt = CryptHandler(module)
    conditions = ConditionsHandler(module, crypt)

    # conditions not allowed to run
    if module.params['label'] is not None and module.params['type'] == 'luks1':
        module.fail_json(msg='You cannot combine type luks1 with the label option.')

    # The conditions are in order to allow more operations in one run.
    # (e.g. create luks and add a key to it)

    # luks create
    if conditions.luks_create():
        if not module.check_mode:
            try:
                crypt.run_luks_create(conditions.device,
                                      module.params['keyfile'],
                                      module.params['passphrase'],
                                      module.params['keysize'])
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # luks open

    name = conditions.opened_luks_name()
    if name is not None:
        result['name'] = name

    if conditions.luks_open():
        name = module.params['name']
        if name is None:
            try:
                name = crypt.generate_luks_name(conditions.device)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        if not module.check_mode:
            try:
                crypt.run_luks_open(conditions.device,
                                    module.params['keyfile'],
                                    module.params['passphrase'],
                                    name)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['name'] = name
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # luks close
    if conditions.luks_close():
        if conditions.device is not None:
            try:
                name = crypt.get_container_name_by_device(
                    conditions.device)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        else:
            name = module.params['name']
        if not module.check_mode:
            try:
                crypt.run_luks_close(name)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['name'] = name
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # luks add key
    if conditions.luks_add_key():
        if not module.check_mode:
            try:
                crypt.run_luks_add_key(conditions.device,
                                       module.params['keyfile'],
                                       module.params['passphrase'],
                                       module.params['new_keyfile'],
                                       module.params['new_passphrase'])
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # luks remove key
    if conditions.luks_remove_key():
        if not module.check_mode:
            try:
                last_key = module.params['force_remove_last_key']
                crypt.run_luks_remove_key(conditions.device,
                                          module.params['remove_keyfile'],
                                          module.params['remove_passphrase'],
                                          force_remove_last_key=last_key)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # luks remove
    if conditions.luks_remove():
        if not module.check_mode:
            try:
                crypt.run_luks_remove(conditions.device)
            except ValueError as e:
                module.fail_json(msg="luks_device error: %s" % e)
        result['changed'] = True
        if module.check_mode:
            module.exit_json(**result)

    # Success - return result
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
