#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Branko Majic <branko@majic.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: dconf
author:
    - "Branko Majic (@azaghal)"
short_description: Modify and read dconf database
description:
  - This module allows modifications and reading of C(dconf) database. The module
    is implemented as a wrapper around C(dconf) tool. Please see the dconf(1) man
    page for more details.
  - Since C(dconf) requires a running D-Bus session to change values, the module
    will try to detect an existing session and reuse it, or run the tool via
    C(dbus-run-session).
requirements:
  - Optionally the C(gi.repository) Python library (usually included in the OS
    on hosts which have C(dconf)); this will become a non-optional requirement
    in a future major release of community.general.
notes:
  - This module depends on C(psutil) Python library (version 4.0.0 and upwards),
    C(dconf), C(dbus-send), and C(dbus-run-session) binaries. Depending on
    distribution you are using, you may need to install additional packages to
    have these available.
  - This module uses the C(gi.repository) Python library when available for
    accurate comparison of values in C(dconf) to values specified in Ansible
    code. C(gi.repository) is likely to be present on most systems which have
    C(dconf) but may not be present everywhere. When it is missing, a simple
    string comparison between values is used, and there may be false positives,
    that is, Ansible may think that a value is being changed when it is not.
    This fallback will be removed in a future version of this module, at which
    point the module will stop working on hosts without C(gi.repository).
  - Detection of existing, running D-Bus session, required to change settings
    via C(dconf), is not 100% reliable due to implementation details of D-Bus
    daemon itself. This might lead to running applications not picking-up
    changes on the fly if options are changed via Ansible and
    C(dbus-run-session).
  - Keep in mind that the C(dconf) CLI tool, which this module wraps around,
    utilises an unusual syntax for the values (GVariant). For example, if you
    wanted to provide a string value, the correct syntax would be
    O(value="'myvalue'") - with single quotes as part of the Ansible parameter
    value.
  - When using loops in combination with a value like
    V("[('xkb', 'us'\), ('xkb', 'se'\)]"), you need to be aware of possible
    type conversions. Applying a filter V({{ item.value | string }})
    to the parameter variable can avoid potential conversion problems.
  - The easiest way to figure out exact syntax/value you need to provide for a
    key is by making the configuration change in application affected by the
    key, and then having a look at value set via commands C(dconf dump
    /path/to/dir/) or C(dconf read /path/to/key).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  key:
    type: str
    required: true
    description:
      - A dconf key to modify or read from the dconf database.
  value:
    type: raw
    required: false
    description:
      - Value to set for the specified dconf key. Value should be specified in
        GVariant format. Due to complexity of this format, it is best to have a
        look at existing values in the dconf database.
      - Required for O(state=present).
      - Although the type is specified as "raw", it should typically be
        specified as a string. However, boolean values in particular are
        handled properly even when specified as booleans rather than strings
        (in fact, handling booleans properly is why the type of this parameter
        is "raw").
  state:
    type: str
    required: false
    default: present
    choices: [ 'read', 'present', 'absent' ]
    description:
      - The action to take upon the key/value.
'''

RETURN = r"""
value:
    description: value associated with the requested key
    returned: success, state was "read"
    type: str
    sample: "'Default'"
"""

EXAMPLES = r"""
- name: Configure available keyboard layouts in Gnome
  community.general.dconf:
    key: "/org/gnome/desktop/input-sources/sources"
    value: "[('xkb', 'us'), ('xkb', 'se')]"
    state: present

- name: Read currently available keyboard layouts in Gnome
  community.general.dconf:
    key: "/org/gnome/desktop/input-sources/sources"
    state: read
  register: keyboard_layouts

- name: Reset the available keyboard layouts in Gnome
  community.general.dconf:
    key: "/org/gnome/desktop/input-sources/sources"
    state: absent

- name: Configure available keyboard layouts in Cinnamon
  community.general.dconf:
    key: "/org/gnome/libgnomekbd/keyboard/layouts"
    value: "['us', 'se']"
    state: present

- name: Read currently available keyboard layouts in Cinnamon
  community.general.dconf:
    key: "/org/gnome/libgnomekbd/keyboard/layouts"
    state: read
  register: keyboard_layouts

- name: Reset the available keyboard layouts in Cinnamon
  community.general.dconf:
    key: "/org/gnome/libgnomekbd/keyboard/layouts"
    state: absent

- name: Disable desktop effects in Cinnamon
  community.general.dconf:
    key: "/org/cinnamon/desktop-effects"
    value: "false"
    state: present
"""


import os
import sys

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.respawn import (
    has_respawned,
    probe_interpreters_for_module,
    respawn_module,
)
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils import deps

glib_module_name = 'gi.repository.GLib'

try:
    from gi.repository.GLib import Variant, GError
except ImportError:
    Variant = None
    GError = AttributeError

with deps.declare("psutil"):
    import psutil


class DBusWrapper(object):
    """
    Helper class that can be used for running a command with a working D-Bus
    session.

    If possible, command will be run against an existing D-Bus session,
    otherwise the session will be spawned via dbus-run-session.

    Example usage:

    dbus_wrapper = DBusWrapper(ansible_module)
    dbus_wrapper.run_command(["printenv", "DBUS_SESSION_BUS_ADDRESS"])
    """

    def __init__(self, module):
        """
        Initialises an instance of the class.

        :param module: Ansible module instance used to signal failures and run commands.
        :type module: AnsibleModule
        """

        # Store passed-in arguments and set-up some defaults.
        self.module = module

        # Try to extract existing D-Bus session address.
        self.dbus_session_bus_address = self._get_existing_dbus_session()

        # If no existing D-Bus session was detected, check if dbus-run-session
        # is available.
        if self.dbus_session_bus_address is None:
            self.dbus_run_session_cmd = self.module.get_bin_path('dbus-run-session', required=True)

    def _get_existing_dbus_session(self):
        """
        Detects and returns an existing D-Bus session bus address.

        :returns: string -- D-Bus session bus address. If a running D-Bus session was not detected, returns None.
        """

        # We'll be checking the processes of current user only.
        uid = os.getuid()

        # Go through all the pids for this user, try to extract the D-Bus
        # session bus address from environment, and ensure it is possible to
        # connect to it.
        self.module.debug("Trying to detect existing D-Bus user session for user: %d" % uid)

        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                process_real_uid, dummy, dummy = process.uids()
                if process_real_uid == uid and 'DBUS_SESSION_BUS_ADDRESS' in process.environ():
                    dbus_session_bus_address_candidate = process.environ()['DBUS_SESSION_BUS_ADDRESS']
                    self.module.debug("Found D-Bus user session candidate at address: %s" % dbus_session_bus_address_candidate)
                    dbus_send_cmd = self.module.get_bin_path('dbus-send', required=True)
                    command = [dbus_send_cmd, '--address=%s' % dbus_session_bus_address_candidate, '--type=signal', '/', 'com.example.test']
                    rc, dummy, dummy = self.module.run_command(command)

                    if rc == 0:
                        self.module.debug("Verified D-Bus user session candidate as usable at address: %s" % dbus_session_bus_address_candidate)

                        return dbus_session_bus_address_candidate

            # This can happen with things like SSH sessions etc.
            except psutil.AccessDenied:
                pass
            # Process has disappeared while inspecting it
            except psutil.NoSuchProcess:
                pass

        self.module.debug("Failed to find running D-Bus user session, will use dbus-run-session")

        return None

    def run_command(self, command):
        """
        Runs the specified command within a functional D-Bus session. Command is
        effectively passed-on to AnsibleModule.run_command() method, with
        modification for using dbus-run-session if necessary.

        :param command: Command to run, including parameters. Each element of the list should be a string.
        :type module: list

        :returns: tuple(result_code, standard_output, standard_error) -- Result code, standard output, and standard error from running the command.
        """

        if self.dbus_session_bus_address is None:
            self.module.debug("Using dbus-run-session wrapper for running commands.")
            command = [self.dbus_run_session_cmd] + command
            rc, out, err = self.module.run_command(command)

            if self.dbus_session_bus_address is None and rc == 127:
                self.module.fail_json(msg="Failed to run passed-in command, dbus-run-session faced an internal error: %s" % err)
        else:
            extra_environment = {'DBUS_SESSION_BUS_ADDRESS': self.dbus_session_bus_address}
            rc, out, err = self.module.run_command(command, environ_update=extra_environment)

        return rc, out, err


class DconfPreference(object):

    def __init__(self, module, check_mode=False):
        """
        Initialises instance of the class.

        :param module: Ansible module instance used to signal failures and run commands.
        :type module: AnsibleModule

        :param check_mode: Specify whether to only check if a change should be made or if to actually make a change.
        :type check_mode: bool
        """

        self.module = module
        self.check_mode = check_mode
        # Check if dconf binary exists
        self.dconf_bin = self.module.get_bin_path('dconf', required=True)

    @staticmethod
    def variants_are_equal(canonical_value, user_value):
        """Compare two string GVariant representations for equality.

        Assumes `canonical_value` is "canonical" in the sense that the type of
        the variant is specified explicitly if it cannot be inferred; this is
        true for textual representations of variants generated by the `dconf`
        command. The type of `canonical_value` is used to parse `user_value`,
        so the latter does not need to be explicitly typed.

        Returns True if the two values are equal.
        """
        if canonical_value is None:
            # It's unset in dconf database, so anything the user is trying to
            # set is a change.
            return False
        try:
            variant1 = Variant.parse(None, canonical_value)
            variant2 = Variant.parse(variant1.get_type(), user_value)
            return variant1 == variant2
        except GError:
            return canonical_value == user_value

    def read(self, key):
        """
        Retrieves current value associated with the dconf key.

        If an error occurs, a call will be made to AnsibleModule.fail_json.

        :returns: string -- Value assigned to the provided key. If the value is not set for specified key, returns None.
        """
        command = [self.dconf_bin, "read", key]

        rc, out, err = self.module.run_command(command)

        if rc != 0:
            self.module.fail_json(msg='dconf failed while reading the value with error: %s' % err,
                                  out=out,
                                  err=err)

        if out == '':
            value = None
        else:
            value = out.rstrip('\n')

        return value

    def write(self, key, value):
        """
        Writes the value for specified key.

        If an error occurs, a call will be made to AnsibleModule.fail_json.

        :param key: dconf key for which the value should be set. Should be a full path.
        :type key: str

        :param value: Value to set for the specified dconf key. Should be specified in GVariant format.
        :type value: str

        :returns: bool -- True if a change was made, False if no change was required.
        """
        # If no change is needed (or won't be done due to check_mode), notify
        # caller straight away.
        if self.variants_are_equal(self.read(key), value):
            return False
        elif self.check_mode:
            return True

        # Set-up command to run. Since DBus is needed for write operation, wrap
        # dconf command dbus-launch.
        command = [self.dconf_bin, "write", key, value]

        # Run the command and fetch standard return code, stdout, and stderr.
        dbus_wrapper = DBusWrapper(self.module)
        rc, out, err = dbus_wrapper.run_command(command)

        if rc != 0:
            self.module.fail_json(msg='dconf failed while writing key %s, value %s with error: %s' % (key, value, err),
                                  out=out,
                                  err=err)

        # Value was changed.
        return True

    def reset(self, key):
        """
        Returns value for the specified key (removes it from user configuration).

        If an error occurs, a call will be made to AnsibleModule.fail_json.

        :param key: dconf key to reset. Should be a full path.
        :type key: str

        :returns: bool -- True if a change was made, False if no change was required.
        """

        # Read the current value first.
        current_value = self.read(key)

        # No change was needed, key is not set at all, or just notify user if we
        # are in check mode.
        if current_value is None:
            return False
        elif self.check_mode:
            return True

        # Set-up command to run. Since DBus is needed for reset operation, wrap
        # dconf command dbus-launch.
        command = [self.dconf_bin, "reset", key]

        # Run the command and fetch standard return code, stdout, and stderr.
        dbus_wrapper = DBusWrapper(self.module)
        rc, out, err = dbus_wrapper.run_command(command)

        if rc != 0:
            self.module.fail_json(msg='dconf failed while resetting the value with error: %s' % err,
                                  out=out,
                                  err=err)

        # Value was changed.
        return True


def main():
    # Setup the Ansible module
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent', 'read']),
            key=dict(required=True, type='str', no_log=False),
            # Converted to str below after special handling of bool.
            value=dict(required=False, default=None, type='raw'),
        ),
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['value']),
        ],
    )

    if Variant is None:
        # This interpreter can't see the GLib module. To try to fix that, we'll
        # look in common locations for system-owned interpreters that can see
        # it; if we find one, we'll respawn under it. Otherwise we'll proceed
        # with degraded performance, without the ability to parse GVariants.
        # Later (in a different PR) we'll actually deprecate this degraded
        # performance level and fail with an error if the library can't be
        # found.

        if has_respawned():
            # This shouldn't be possible; short-circuit early if it happens.
            module.fail_json(
                msg="%s must be installed and visible from %s." %
                (glib_module_name, sys.executable))

        interpreters = ['/usr/bin/python3', '/usr/bin/python2',
                        '/usr/bin/python']

        interpreter = probe_interpreters_for_module(
            interpreters, glib_module_name)

        if interpreter:
            # Found the Python bindings; respawn this module under the
            # interpreter where we found them.
            respawn_module(interpreter)
            # This is the end of the line for this process, it will exit here
            # once the respawned module has completed.

    # Try to be forgiving about the user specifying a boolean as the value, or
    # more accurately about the fact that YAML and Ansible are quite insistent
    # about converting strings that look like booleans into booleans. Convert
    # the boolean into a string of the type dconf will understand. Any type for
    # the value other than boolean is just converted into a string directly.
    if module.params['value'] is not None:
        if isinstance(module.params['value'], bool):
            module.params['value'] = 'true' if module.params['value'] else 'false'
        else:
            module.params['value'] = to_native(
                module.params['value'], errors='surrogate_or_strict')

    if Variant is None:
        module.warn(
            'WARNING: The gi.repository Python library is not available; '
            'using string comparison to check value equality. This fallback '
            'will be deprecated in a future version of community.general.')

    deps.validate(module)

    # Create wrapper instance.
    dconf = DconfPreference(module, module.check_mode)

    # Process based on different states.
    if module.params['state'] == 'read':
        value = dconf.read(module.params['key'])
        module.exit_json(changed=False, value=value)
    elif module.params['state'] == 'present':
        changed = dconf.write(module.params['key'], module.params['value'])
        module.exit_json(changed=changed)
    elif module.params['state'] == 'absent':
        changed = dconf.reset(module.params['key'])
        module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
