#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) James Laska (jlaska@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: redhat_subscription
short_description: Manage registration and subscriptions to RHSM using C(subscription-manager)
description:
    - Manage registration and subscription to the Red Hat Subscription Management entitlement platform using the C(subscription-manager) command,
      registering using D-Bus if possible.
author: "Barnaby Court (@barnabycourt)"
notes:
    - |
      The module tries to use the D-Bus C(rhsm) service (part of C(subscription-manager))
      to register, starting from community.general 6.5.0: this is done so credentials
      (username, password, activation keys) can be passed to C(rhsm) in a secure way.
      C(subscription-manager) itself gets credentials only as arguments of command line
      parameters, which is I(not) secure, as they can be easily stolen by checking the
      process listing on the system. Due to limitations of the D-Bus interface of C(rhsm),
      the module will I(not) use D-Bus for registration when trying either to register
      using O(token), or when specifying O(environment), or when the system is old
      (typically RHEL 7 older than 7.4, RHEL 6, and older).
    - In order to register a system, subscription-manager requires either a username and password, or an activationkey and an Organization ID.
    - Since 2.5 values for O(server_hostname), O(server_insecure), O(rhsm_baseurl),
      O(server_proxy_hostname), O(server_proxy_port), O(server_proxy_user) and
      O(server_proxy_password) are no longer taken from the C(/etc/rhsm/rhsm.conf)
      config file and default to V(null).
    - It is possible to interact with C(subscription-manager) only as root,
      so root permissions are required to successfully run this module.
    - Since community.general 6.5.0, credentials (that is, O(username) and O(password),
      O(activationkey), or O(token)) are needed only in case the the system is not registered,
      or O(force_register) is specified; this makes it possible to use the module to tweak an
      already registered system, for example attaching pools to it (using O(pool), or O(pool_ids)),
      and modifying the C(syspurpose) attributes (using O(syspurpose)).
requirements:
    - subscription-manager
    - Optionally the C(dbus) Python library; this is usually included in the OS
      as it is used by C(subscription-manager).
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    state:
        description:
          - whether to register and subscribe (V(present)), or unregister (V(absent)) a system
        choices: [ "present", "absent" ]
        default: "present"
        type: str
    username:
        description:
            - access.redhat.com or Red Hat Satellite or Katello username
        type: str
    password:
        description:
            - access.redhat.com or Red Hat Satellite or Katello password
        type: str
    token:
        description:
            - sso.redhat.com API access token.
        type: str
        version_added: 6.3.0
    server_hostname:
        description:
            - Specify an alternative Red Hat Subscription Management or Red Hat Satellite or Katello server.
        type: str
    server_insecure:
        description:
            - Enable or disable https server certificate verification when connecting to O(server_hostname).
        type: str
    server_prefix:
        description:
            - Specify the prefix when registering to the Red Hat Subscription Management or Red Hat Satellite or Katello server.
        type: str
        version_added: 3.3.0
    server_port:
        description:
            - Specify the port when registering to the Red Hat Subscription Management or Red Hat Satellite or Katello server.
        type: str
        version_added: 3.3.0
    rhsm_baseurl:
        description:
            - Specify CDN baseurl
        type: str
    rhsm_repo_ca_cert:
        description:
            - Specify an alternative location for a CA certificate for CDN
        type: str
    server_proxy_hostname:
        description:
            - Specify an HTTP proxy hostname.
        type: str
    server_proxy_scheme:
        description:
            - Specify an HTTP proxy scheme, for example V(http) or V(https).
        type: str
        version_added: 6.2.0
    server_proxy_port:
        description:
            - Specify an HTTP proxy port.
        type: str
    server_proxy_user:
        description:
            - Specify a user for HTTP proxy with basic authentication
        type: str
    server_proxy_password:
        description:
            - Specify a password for HTTP proxy with basic authentication
        type: str
    auto_attach:
        description:
            - Upon successful registration, auto-consume available subscriptions
            - |
              Please note that the alias O(autosubscribe) will be removed in
              community.general 9.0.0.
        type: bool
        aliases: [autosubscribe]
    activationkey:
        description:
            - supply an activation key for use with registration
        type: str
    org_id:
        description:
            - Organization ID to use in conjunction with activationkey
        type: str
    environment:
        description:
            - Register with a specific environment in the destination org. Used with Red Hat Satellite or Katello
        type: str
    pool:
        description:
            - |
              Specify a subscription pool name to consume.  Regular expressions accepted.
              Mutually exclusive with O(pool_ids).
            - |
              Please use O(pool_ids) instead: specifying pool IDs is much faster,
              and it avoids to match new pools that become available for the
              system and are not explicitly wanted.  Also, this option does not
              support quantities.
            - |
              This option is deprecated for the reasons mentioned above,
              and it will be removed in community.general 10.0.0.
        default: '^$'
        type: str
    pool_ids:
        description:
            - |
              Specify subscription pool IDs to consume. Prefer over O(pool) when possible as it is much faster.
              A pool ID may be specified as a C(string) - just the pool ID (for example V(0123456789abcdef0123456789abcdef)),
              or as a C(dict) with the pool ID as the key, and a quantity as the value (for example
              V(0123456789abcdef0123456789abcdef: 2). If the quantity is provided, it is used to consume multiple
              entitlements from a pool (the pool must support this). Mutually exclusive with O(pool).
        default: []
        type: list
        elements: raw
    consumer_type:
        description:
            - The type of unit to register, defaults to system
        type: str
    consumer_name:
        description:
            - Name of the system to register, defaults to the hostname
        type: str
    consumer_id:
        description:
            - |
              References an existing consumer ID to resume using a previous registration
              for this system. If the  system's identity certificate is lost or corrupted,
              this option allows it to resume using its previous identity and subscriptions.
              The default is to not specify a consumer ID so a new ID is created.
        type: str
    force_register:
        description:
            -  Register the system even if it is already registered
        type: bool
        default: false
    release:
        description:
            - Set a release version
        type: str
    syspurpose:
        description:
            - Set syspurpose attributes in file C(/etc/rhsm/syspurpose/syspurpose.json)
              and synchronize these attributes with RHSM server. Syspurpose attributes help attach
              the most appropriate subscriptions to the system automatically. When C(syspurpose.json) file
              already contains some attributes, then new attributes overwrite existing attributes.
              When some attribute is not listed in the new list of attributes, the existing
              attribute will be removed from C(syspurpose.json) file. Unknown attributes are ignored.
        type: dict
        suboptions:
            usage:
                description: Syspurpose attribute usage
                type: str
            role:
                description: Syspurpose attribute role
                type: str
            service_level_agreement:
                description: Syspurpose attribute service_level_agreement
                type: str
            addons:
                description: Syspurpose attribute addons
                type: list
                elements: str
            sync:
                description:
                    - When this option is V(true), then syspurpose attributes are synchronized with
                      RHSM server immediately. When this option is V(false), then syspurpose attributes
                      will be synchronized with RHSM server by rhsmcertd daemon.
                type: bool
                default: false
'''

EXAMPLES = '''
- name: Register as user (joe_user) with password (somepass) and auto-subscribe to available content.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    auto_attach: true

- name: Same as above but subscribe to a specific pool by ID.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    pool_ids: 0123456789abcdef0123456789abcdef

- name: Register and subscribe to multiple pools.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    pool_ids:
      - 0123456789abcdef0123456789abcdef
      - 1123456789abcdef0123456789abcdef

- name: Same as above but consume multiple entitlements.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    pool_ids:
      - 0123456789abcdef0123456789abcdef: 2
      - 1123456789abcdef0123456789abcdef: 4

- name: Register and pull existing system data.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    consumer_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

- name: Register with activationkey and consume subscriptions matching Red Hat Enterprise Server or Red Hat Virtualization
  community.general.redhat_subscription:
    state: present
    activationkey: 1-222333444
    org_id: 222333444
    pool: '^(Red Hat Enterprise Server|Red Hat Virtualization)$'

- name: Update the consumed subscriptions from the previous example (remove Red Hat Virtualization subscription)
  community.general.redhat_subscription:
    state: present
    activationkey: 1-222333444
    org_id: 222333444
    pool: '^Red Hat Enterprise Server$'

- name: Register as user credentials into given environment (against Red Hat Satellite or Katello), and auto-subscribe.
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    environment: Library
    auto_attach: true

- name: Register as user (joe_user) with password (somepass) and a specific release
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    release: 7.4

- name: Register as user (joe_user) with password (somepass), set syspurpose attributes and synchronize them with server
  community.general.redhat_subscription:
    state: present
    username: joe_user
    password: somepass
    auto_attach: true
    syspurpose:
      usage: "Production"
      role: "Red Hat Enterprise Server"
      service_level_agreement: "Premium"
      addons:
        - addon1
        - addon2
      sync: true
'''

RETURN = '''
subscribed_pool_ids:
    description: List of pool IDs to which system is now subscribed
    returned: success
    type: dict
    sample: {
        "8a85f9815ab905d3015ab928c7005de4": "1"
    }
'''

from os.path import isfile
from os import getuid, unlink
import re
import shutil
import tempfile
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six.moves import configparser
from ansible.module_utils import distro


SUBMAN_CMD = None


class Rhsm(object):

    REDHAT_REPO = "/etc/yum.repos.d/redhat.repo"

    def __init__(self, module):
        self.module = module

    def update_plugin_conf(self, plugin, enabled=True):
        plugin_conf = '/etc/yum/pluginconf.d/%s.conf' % plugin

        if isfile(plugin_conf):
            tmpfd, tmpfile = tempfile.mkstemp()
            shutil.copy2(plugin_conf, tmpfile)
            cfg = configparser.ConfigParser()
            cfg.read([tmpfile])

            if enabled:
                cfg.set('main', 'enabled', '1')
            else:
                cfg.set('main', 'enabled', '0')

            fd = open(tmpfile, 'w+')
            cfg.write(fd)
            fd.close()
            self.module.atomic_move(tmpfile, plugin_conf)

    def enable(self):
        '''
            Enable the system to receive updates from subscription-manager.
            This involves updating affected yum plugins and removing any
            conflicting yum repositories.
        '''
        # Remove any existing redhat.repo
        if isfile(self.REDHAT_REPO):
            unlink(self.REDHAT_REPO)
        self.update_plugin_conf('rhnplugin', False)
        self.update_plugin_conf('subscription-manager', True)

    def configure(self, **kwargs):
        '''
            Configure the system as directed for registration with RHSM
            Raises:
              * Exception - if error occurs while running command
        '''

        args = [SUBMAN_CMD, 'config']

        # Pass supplied **kwargs as parameters to subscription-manager.  Ignore
        # non-configuration parameters and replace '_' with '.'.  For example,
        # 'server_hostname' becomes '--server.hostname'.
        options = []
        for k, v in sorted(kwargs.items()):
            if re.search(r'^(server|rhsm)_', k) and v is not None:
                options.append('--%s=%s' % (k.replace('_', '.', 1), v))

        # When there is nothing to configure, then it is not necessary
        # to run config command, because it only returns current
        # content of current configuration file
        if len(options) == 0:
            return

        args.extend(options)

        self.module.run_command(args, check_rc=True)

    @property
    def is_registered(self):
        '''
            Determine whether the current system
            Returns:
              * Boolean - whether the current system is currently registered to
                          RHSM.
        '''

        args = [SUBMAN_CMD, 'identity']
        rc, stdout, stderr = self.module.run_command(args, check_rc=False)
        if rc == 0:
            return True
        else:
            return False

    def _has_dbus_interface(self):
        """
        Checks whether subscription-manager has a D-Bus interface.

        :returns: bool -- whether subscription-manager has a D-Bus interface.
        """

        def str2int(s, default=0):
            try:
                return int(s)
            except ValueError:
                return default

        distro_id = distro.id()
        distro_version = tuple(str2int(p) for p in distro.version_parts())

        # subscription-manager in any supported Fedora version has the interface.
        if distro_id == 'fedora':
            return True
        # Any other distro: assume it is EL;
        # the D-Bus interface was added to subscription-manager in RHEL 7.4.
        return (distro_version[0] == 7 and distro_version[1] >= 4) or \
            distro_version[0] >= 8

    def _can_connect_to_dbus(self):
        """
        Checks whether it is possible to connect to the system D-Bus bus.

        :returns: bool -- whether it is possible to connect to the system D-Bus bus.
        """

        try:
            # Technically speaking, subscription-manager uses dbus-python
            # as D-Bus library, so this ought to work; better be safe than
            # sorry, I guess...
            import dbus
        except ImportError:
            self.module.debug('dbus Python module not available, will use CLI')
            return False

        try:
            bus = dbus.SystemBus()
            msg = dbus.lowlevel.SignalMessage('/', 'com.example', 'test')
            bus.send_message(msg)
            bus.flush()

        except dbus.exceptions.DBusException as e:
            self.module.debug('Failed to connect to system D-Bus bus, will use CLI: %s' % e)
            return False

        self.module.debug('Verified system D-Bus bus as usable')
        return True

    def register(self, was_registered, username, password, token, auto_attach, activationkey, org_id,
                 consumer_type, consumer_name, consumer_id, force_register, environment,
                 release):
        '''
            Register the current system to the provided RHSM or Red Hat Satellite
            or Katello server

            Raises:
              * Exception - if any error occurs during the registration
        '''
        # There is no support for token-based registration in the D-Bus API
        # of rhsm, so always use the CLI in that case;
        # also, since the specified environments are names, and the D-Bus APIs
        # require IDs for the environments, use the CLI also in that case
        if (not token and not environment and self._has_dbus_interface() and
           self._can_connect_to_dbus()):
            self._register_using_dbus(was_registered, username, password, auto_attach,
                                      activationkey, org_id, consumer_type,
                                      consumer_name, consumer_id,
                                      force_register, environment, release)
            return
        self._register_using_cli(username, password, token, auto_attach,
                                 activationkey, org_id, consumer_type,
                                 consumer_name, consumer_id,
                                 force_register, environment, release)

    def _register_using_cli(self, username, password, token, auto_attach,
                            activationkey, org_id, consumer_type, consumer_name,
                            consumer_id, force_register, environment, release):
        '''
            Register using the 'subscription-manager' command

            Raises:
              * Exception - if error occurs while running command
        '''
        args = [SUBMAN_CMD, 'register']

        # Generate command arguments
        if force_register:
            args.extend(['--force'])

        if org_id:
            args.extend(['--org', org_id])

        if auto_attach:
            args.append('--auto-attach')

        if consumer_type:
            args.extend(['--type', consumer_type])

        if consumer_name:
            args.extend(['--name', consumer_name])

        if consumer_id:
            args.extend(['--consumerid', consumer_id])

        if environment:
            args.extend(['--environment', environment])

        if activationkey:
            args.extend(['--activationkey', activationkey])
        elif token:
            args.extend(['--token', token])
        else:
            if username:
                args.extend(['--username', username])
            if password:
                args.extend(['--password', password])

        if release:
            args.extend(['--release', release])

        rc, stderr, stdout = self.module.run_command(args, check_rc=True, expand_user_and_vars=False)

    def _register_using_dbus(self, was_registered, username, password, auto_attach,
                             activationkey, org_id, consumer_type, consumer_name,
                             consumer_id, force_register, environment, release):
        '''
            Register using D-Bus (connecting to the rhsm service)

            Raises:
              * Exception - if error occurs during the D-Bus communication
        '''
        import dbus

        SUBSCRIPTION_MANAGER_LOCALE = 'C'
        # Seconds to wait for Registration to complete over DBus;
        # 10 minutes should be a pretty generous timeout.
        REGISTRATION_TIMEOUT = 600

        def str2int(s, default=0):
            try:
                return int(s)
            except ValueError:
                return default

        distro_id = distro.id()
        distro_version_parts = distro.version_parts()
        distro_version = tuple(str2int(p) for p in distro_version_parts)

        # Stop the rhsm service when using systemd (which means Fedora or
        # RHEL 7+): this is because the service may not use new configuration bits
        # - with subscription-manager < 1.26.5-1 (in RHEL < 8.2);
        #   fixed later by https://github.com/candlepin/subscription-manager/pull/2175
        # - sporadically: https://bugzilla.redhat.com/show_bug.cgi?id=2049296
        if distro_id == 'fedora' or distro_version[0] >= 7:
            cmd = ['systemctl', 'stop', 'rhsm']
            self.module.run_command(cmd, check_rc=True, expand_user_and_vars=False)

        # While there is a 'force' options for the registration, it is actually
        # not implemented (and thus it does not work)
        # - in RHEL 7 and earlier
        # - in RHEL 8 before 8.8: https://bugzilla.redhat.com/show_bug.cgi?id=2118486
        # - in RHEL 9 before 9.2: https://bugzilla.redhat.com/show_bug.cgi?id=2121350
        # Hence, use it only when implemented, manually unregistering otherwise.
        # Match it on RHEL, since we know about it; other distributions
        # will need their own logic.
        dbus_force_option_works = False
        if (distro_id == 'rhel' and
            ((distro_version[0] == 8 and distro_version[1] >= 8) or
             (distro_version[0] == 9 and distro_version[1] >= 2) or
             distro_version[0] > 9)):
            dbus_force_option_works = True

        if force_register and not dbus_force_option_works and was_registered:
            self.unregister()

        register_opts = {}
        if consumer_type:
            # The option for the consumer type used to be 'type' in versions
            # of RHEL before 9 & in RHEL 9 before 9.2, and then it changed to
            # 'consumer_type'; since the Register*() D-Bus functions reject
            # unknown options, we have to pass the right option depending on
            # the version -- funky.
            def supports_option_consumer_type():
                # subscription-manager in any supported Fedora version
                # has the new option.
                if distro_id == 'fedora':
                    return True
                # Check for RHEL 9 >= 9.2, or RHEL >= 10.
                if distro_id == 'rhel' and \
                   ((distro_version[0] == 9 and distro_version[1] >= 2) or
                       distro_version[0] >= 10):
                    return True
                # CentOS: since the change was only done in EL 9, then there is
                # only CentOS Stream for 9, and thus we can assume it has the
                # latest version of subscription-manager.
                if distro_id == 'centos' and distro_version[0] >= 9:
                    return True
                # Unknown or old distro: assume it does not support
                # the new option.
                return False

            consumer_type_key = 'type'
            if supports_option_consumer_type():
                consumer_type_key = 'consumer_type'
            register_opts[consumer_type_key] = consumer_type
        if consumer_name:
            register_opts['name'] = consumer_name
        if consumer_id:
            register_opts['consumerid'] = consumer_id
        if environment:
            # The option for environments used to be 'environment' in versions
            # of RHEL before 8.6, and then it changed to 'environments'; since
            # the Register*() D-Bus functions reject unknown options, we have
            # to pass the right option depending on the version -- funky.
            def supports_option_environments():
                # subscription-manager in any supported Fedora version
                # has the new option.
                if distro_id == 'fedora':
                    return True
                # Check for RHEL 8 >= 8.6, or RHEL >= 9.
                if distro_id == 'rhel' and \
                   ((distro_version[0] == 8 and distro_version[1] >= 6) or
                       distro_version[0] >= 9):
                    return True
                # CentOS: similar checks as for RHEL, with one extra bit:
                # if the 2nd part of the version is empty, it means it is
                # CentOS Stream, and thus we can assume it has the latest
                # version of subscription-manager.
                if distro_id == 'centos' and \
                   ((distro_version[0] == 8 and
                       (distro_version[1] >= 6 or distro_version_parts[1] == '')) or
                       distro_version[0] >= 9):
                    return True
                # Unknown or old distro: assume it does not support
                # the new option.
                return False

            environment_key = 'environment'
            if supports_option_environments():
                environment_key = 'environments'
            register_opts[environment_key] = environment
        if force_register and dbus_force_option_works and was_registered:
            register_opts['force'] = True
        # Wrap it as proper D-Bus dict
        register_opts = dbus.Dictionary(register_opts, signature='sv', variant_level=1)

        connection_opts = {}
        # Wrap it as proper D-Bus dict
        connection_opts = dbus.Dictionary(connection_opts, signature='sv', variant_level=1)

        bus = dbus.SystemBus()
        register_server = bus.get_object('com.redhat.RHSM1',
                                         '/com/redhat/RHSM1/RegisterServer')
        address = register_server.Start(
            SUBSCRIPTION_MANAGER_LOCALE,
            dbus_interface='com.redhat.RHSM1.RegisterServer',
        )

        try:
            # Use the private bus to register the system
            self.module.debug('Connecting to the private DBus')
            private_bus = dbus.connection.Connection(address)

            try:
                if activationkey:
                    args = (
                        org_id,
                        [activationkey],
                        register_opts,
                        connection_opts,
                        SUBSCRIPTION_MANAGER_LOCALE,
                    )
                    private_bus.call_blocking(
                        'com.redhat.RHSM1',
                        '/com/redhat/RHSM1/Register',
                        'com.redhat.RHSM1.Register',
                        'RegisterWithActivationKeys',
                        'sasa{sv}a{sv}s',
                        args,
                        timeout=REGISTRATION_TIMEOUT,
                    )
                else:
                    args = (
                        org_id or '',
                        username,
                        password,
                        register_opts,
                        connection_opts,
                        SUBSCRIPTION_MANAGER_LOCALE,
                    )
                    private_bus.call_blocking(
                        'com.redhat.RHSM1',
                        '/com/redhat/RHSM1/Register',
                        'com.redhat.RHSM1.Register',
                        'Register',
                        'sssa{sv}a{sv}s',
                        args,
                        timeout=REGISTRATION_TIMEOUT,
                    )

            except dbus.exceptions.DBusException as e:
                # Sometimes we get NoReply but the registration has succeeded.
                # Check the registration status before deciding if this is an error.
                if e.get_dbus_name() == 'org.freedesktop.DBus.Error.NoReply':
                    if not self.is_registered():
                        # Host is not registered so re-raise the error
                        raise
                else:
                    raise
                # Host was registered so continue
        finally:
            # Always shut down the private bus
            self.module.debug('Shutting down private DBus instance')
            register_server.Stop(
                SUBSCRIPTION_MANAGER_LOCALE,
                dbus_interface='com.redhat.RHSM1.RegisterServer',
            )

        # Make sure to refresh all the local data: this will fetch all the
        # certificates, update redhat.repo, etc.
        self.module.run_command([SUBMAN_CMD, 'refresh'],
                                check_rc=True, expand_user_and_vars=False)

        if auto_attach:
            args = [SUBMAN_CMD, 'attach', '--auto']
            self.module.run_command(args, check_rc=True, expand_user_and_vars=False)

        # There is no support for setting the release via D-Bus, so invoke
        # the CLI for this.
        if release:
            args = [SUBMAN_CMD, 'release', '--set', release]
            self.module.run_command(args, check_rc=True, expand_user_and_vars=False)

    def unsubscribe(self, serials=None):
        '''
            Unsubscribe a system from subscribed channels
            Args:
              serials(list or None): list of serials to unsubscribe. If
                                     serials is none or an empty list, then
                                     all subscribed channels will be removed.
            Raises:
              * Exception - if error occurs while running command
        '''
        items = []
        if serials is not None and serials:
            items = ["--serial=%s" % s for s in serials]
        if serials is None:
            items = ["--all"]

        if items:
            args = [SUBMAN_CMD, 'remove'] + items
            rc, stderr, stdout = self.module.run_command(args, check_rc=True)
        return serials

    def unregister(self):
        '''
            Unregister a currently registered system
            Raises:
              * Exception - if error occurs while running command
        '''
        args = [SUBMAN_CMD, 'unregister']
        rc, stderr, stdout = self.module.run_command(args, check_rc=True)
        self.update_plugin_conf('rhnplugin', False)
        self.update_plugin_conf('subscription-manager', False)

    def subscribe(self, regexp):
        '''
            Subscribe current system to available pools matching the specified
            regular expression. It matches regexp against available pool ids first.
            If any pool ids match, subscribe to those pools and return.

            If no pool ids match, then match regexp against available pool product
            names. Note this can still easily match many many pools. Then subscribe
            to those pools.

            Since a pool id is a more specific match, we only fallback to matching
            against names if we didn't match pool ids.

            Raises:
              * Exception - if error occurs while running command
        '''
        # See https://github.com/ansible/ansible/issues/19466

        # subscribe to pools whose pool id matches regexp (and only the pool id)
        subscribed_pool_ids = self.subscribe_pool(regexp)

        # If we found any matches, we are done
        # Don't attempt to match pools by product name
        if subscribed_pool_ids:
            return subscribed_pool_ids

        # We didn't match any pool ids.
        # Now try subscribing to pools based on product name match
        # Note: This can match lots of product names.
        subscribed_by_product_pool_ids = self.subscribe_product(regexp)
        if subscribed_by_product_pool_ids:
            return subscribed_by_product_pool_ids

        # no matches
        return []

    def subscribe_by_pool_ids(self, pool_ids):
        """
        Try to subscribe to the list of pool IDs
        """
        available_pools = RhsmPools(self.module)

        available_pool_ids = [p.get_pool_id() for p in available_pools]

        for pool_id, quantity in sorted(pool_ids.items()):
            if pool_id in available_pool_ids:
                args = [SUBMAN_CMD, 'attach', '--pool', pool_id]
                if quantity is not None:
                    args.extend(['--quantity', to_native(quantity)])
                rc, stderr, stdout = self.module.run_command(args, check_rc=True)
            else:
                self.module.fail_json(msg='Pool ID: %s not in list of available pools' % pool_id)
        return pool_ids

    def subscribe_pool(self, regexp):
        '''
            Subscribe current system to available pools matching the specified
            regular expression
            Raises:
              * Exception - if error occurs while running command
        '''

        # Available pools ready for subscription
        available_pools = RhsmPools(self.module)

        subscribed_pool_ids = []
        for pool in available_pools.filter_pools(regexp):
            pool.subscribe()
            subscribed_pool_ids.append(pool.get_pool_id())
        return subscribed_pool_ids

    def subscribe_product(self, regexp):
        '''
            Subscribe current system to available pools matching the specified
            regular expression
            Raises:
              * Exception - if error occurs while running command
        '''

        # Available pools ready for subscription
        available_pools = RhsmPools(self.module)

        subscribed_pool_ids = []
        for pool in available_pools.filter_products(regexp):
            pool.subscribe()
            subscribed_pool_ids.append(pool.get_pool_id())
        return subscribed_pool_ids

    def update_subscriptions(self, regexp):
        changed = False
        consumed_pools = RhsmPools(self.module, consumed=True)
        pool_ids_to_keep = [p.get_pool_id() for p in consumed_pools.filter_pools(regexp)]
        pool_ids_to_keep.extend([p.get_pool_id() for p in consumed_pools.filter_products(regexp)])

        serials_to_remove = [p.Serial for p in consumed_pools if p.get_pool_id() not in pool_ids_to_keep]
        serials = self.unsubscribe(serials=serials_to_remove)

        subscribed_pool_ids = self.subscribe(regexp)

        if subscribed_pool_ids or serials:
            changed = True
        return {'changed': changed, 'subscribed_pool_ids': subscribed_pool_ids,
                'unsubscribed_serials': serials}

    def update_subscriptions_by_pool_ids(self, pool_ids):
        changed = False
        consumed_pools = RhsmPools(self.module, consumed=True)

        existing_pools = {}
        serials_to_remove = []
        for p in consumed_pools:
            pool_id = p.get_pool_id()
            quantity_used = p.get_quantity_used()
            existing_pools[pool_id] = quantity_used

            quantity = pool_ids.get(pool_id, 0)
            if quantity is not None and quantity != quantity_used:
                serials_to_remove.append(p.Serial)

        serials = self.unsubscribe(serials=serials_to_remove)

        missing_pools = {}
        for pool_id, quantity in sorted(pool_ids.items()):
            quantity_used = existing_pools.get(pool_id, 0)
            if quantity is None and quantity_used == 0 or quantity not in (None, 0, quantity_used):
                missing_pools[pool_id] = quantity

        self.subscribe_by_pool_ids(missing_pools)

        if missing_pools or serials:
            changed = True
        return {'changed': changed, 'subscribed_pool_ids': list(missing_pools.keys()),
                'unsubscribed_serials': serials}

    def sync_syspurpose(self):
        """
        Try to synchronize syspurpose attributes with server
        """
        args = [SUBMAN_CMD, 'status']
        rc, stdout, stderr = self.module.run_command(args, check_rc=False)


class RhsmPool(object):
    '''
        Convenience class for housing subscription information
    '''

    def __init__(self, module, **kwargs):
        self.module = module
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return str(self.__getattribute__('_name'))

    def get_pool_id(self):
        return getattr(self, 'PoolId', getattr(self, 'PoolID'))

    def get_quantity_used(self):
        return int(getattr(self, 'QuantityUsed'))

    def subscribe(self):
        args = "subscription-manager attach --pool %s" % self.get_pool_id()
        rc, stdout, stderr = self.module.run_command(args, check_rc=True)
        if rc == 0:
            return True
        else:
            return False


class RhsmPools(object):
    """
        This class is used for manipulating pools subscriptions with RHSM
    """

    def __init__(self, module, consumed=False):
        self.module = module
        self.products = self._load_product_list(consumed)

    def __iter__(self):
        return self.products.__iter__()

    def _load_product_list(self, consumed=False):
        """
            Loads list of all available or consumed pools for system in data structure

            Args:
                consumed(bool): if True list consumed  pools, else list available pools (default False)
        """
        args = "subscription-manager list"
        if consumed:
            args += " --consumed"
        else:
            args += " --available"
        lang_env = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')
        rc, stdout, stderr = self.module.run_command(args, check_rc=True, environ_update=lang_env)

        products = []
        for line in stdout.split('\n'):
            # Remove leading+trailing whitespace
            line = line.strip()
            # An empty line implies the end of a output group
            if len(line) == 0:
                continue
            # If a colon ':' is found, parse
            elif ':' in line:
                (key, value) = line.split(':', 1)
                key = key.strip().replace(" ", "")  # To unify
                value = value.strip()
                if key in ['ProductName', 'SubscriptionName']:
                    # Remember the name for later processing
                    products.append(RhsmPool(self.module, _name=value, key=value))
                elif products:
                    # Associate value with most recently recorded product
                    products[-1].__setattr__(key, value)
                # FIXME - log some warning?
                # else:
                    # warnings.warn("Unhandled subscription key/value: %s/%s" % (key,value))
        return products

    def filter_pools(self, regexp='^$'):
        '''
            Return a list of RhsmPools whose pool id matches the provided regular expression
        '''
        r = re.compile(regexp)
        for product in self.products:
            if r.search(product.get_pool_id()):
                yield product

    def filter_products(self, regexp='^$'):
        '''
            Return a list of RhsmPools whose product name matches the provided regular expression
        '''
        r = re.compile(regexp)
        for product in self.products:
            if r.search(product._name):
                yield product


class SysPurpose(object):
    """
    This class is used for reading and writing to syspurpose.json file
    """

    SYSPURPOSE_FILE_PATH = "/etc/rhsm/syspurpose/syspurpose.json"

    ALLOWED_ATTRIBUTES = ['role', 'usage', 'service_level_agreement', 'addons']

    def __init__(self, path=None):
        """
        Initialize class used for reading syspurpose json file
        """
        self.path = path or self.SYSPURPOSE_FILE_PATH

    def update_syspurpose(self, new_syspurpose):
        """
        Try to update current syspurpose with new attributes from new_syspurpose
        """
        syspurpose = {}
        syspurpose_changed = False
        for key, value in new_syspurpose.items():
            if key in self.ALLOWED_ATTRIBUTES:
                if value is not None:
                    syspurpose[key] = value
            elif key == 'sync':
                pass
            else:
                raise KeyError("Attribute: %s not in list of allowed attributes: %s" %
                               (key, self.ALLOWED_ATTRIBUTES))
        current_syspurpose = self._read_syspurpose()
        if current_syspurpose != syspurpose:
            syspurpose_changed = True
        # Update current syspurpose with new values
        current_syspurpose.update(syspurpose)
        # When some key is not listed in new syspurpose, then delete it from current syspurpose
        # and ignore custom attributes created by user (e.g. "foo": "bar")
        for key in list(current_syspurpose):
            if key in self.ALLOWED_ATTRIBUTES and key not in syspurpose:
                del current_syspurpose[key]
        self._write_syspurpose(current_syspurpose)
        return syspurpose_changed

    def _write_syspurpose(self, new_syspurpose):
        """
        This function tries to update current new_syspurpose attributes to
        json file.
        """
        with open(self.path, "w") as fp:
            fp.write(json.dumps(new_syspurpose, indent=2, ensure_ascii=False, sort_keys=True))

    def _read_syspurpose(self):
        """
        Read current syspurpuse from json file.
        """
        current_syspurpose = {}
        try:
            with open(self.path, "r") as fp:
                content = fp.read()
        except IOError:
            pass
        else:
            current_syspurpose = json.loads(content)
        return current_syspurpose


def main():

    # Note: the default values for parameters are:
    # 'type': 'str', 'default': None, 'required': False
    # So there is no need to repeat these values for each parameter.
    module = AnsibleModule(
        argument_spec={
            'state': {'default': 'present', 'choices': ['present', 'absent']},
            'username': {},
            'password': {'no_log': True},
            'token': {'no_log': True},
            'server_hostname': {},
            'server_insecure': {},
            'server_prefix': {},
            'server_port': {},
            'rhsm_baseurl': {},
            'rhsm_repo_ca_cert': {},
            'auto_attach': {
                'type': 'bool',
                'aliases': ['autosubscribe'],
                'deprecated_aliases': [
                    {
                        'name': 'autosubscribe',
                        'version': '9.0.0',
                        'collection_name': 'community.general',
                    },
                ],
            },
            'activationkey': {'no_log': True},
            'org_id': {},
            'environment': {},
            'pool': {
                'default': '^$',
                'removed_in_version': '10.0.0',
                'removed_from_collection': 'community.general',
            },
            'pool_ids': {'default': [], 'type': 'list', 'elements': 'raw'},
            'consumer_type': {},
            'consumer_name': {},
            'consumer_id': {},
            'force_register': {'default': False, 'type': 'bool'},
            'server_proxy_hostname': {},
            'server_proxy_scheme': {},
            'server_proxy_port': {},
            'server_proxy_user': {},
            'server_proxy_password': {'no_log': True},
            'release': {},
            'syspurpose': {
                'type': 'dict',
                'options': {
                    'role': {},
                    'usage': {},
                    'service_level_agreement': {},
                    'addons': {'type': 'list', 'elements': 'str'},
                    'sync': {'type': 'bool', 'default': False}
                }
            }
        },
        required_together=[['username', 'password'],
                           ['server_proxy_hostname', 'server_proxy_port'],
                           ['server_proxy_user', 'server_proxy_password']],
        mutually_exclusive=[['activationkey', 'username'],
                            ['activationkey', 'token'],
                            ['token', 'username'],
                            ['activationkey', 'consumer_id'],
                            ['activationkey', 'environment'],
                            ['activationkey', 'auto_attach'],
                            ['pool', 'pool_ids']],
        required_if=[['force_register', True, ['username', 'activationkey', 'token'], True]],
    )

    if getuid() != 0:
        module.fail_json(
            msg="Interacting with subscription-manager requires root permissions ('become: true')"
        )

    # Load RHSM configuration from file
    rhsm = Rhsm(module)

    state = module.params['state']
    username = module.params['username']
    password = module.params['password']
    token = module.params['token']
    server_hostname = module.params['server_hostname']
    server_insecure = module.params['server_insecure']
    server_prefix = module.params['server_prefix']
    server_port = module.params['server_port']
    rhsm_baseurl = module.params['rhsm_baseurl']
    rhsm_repo_ca_cert = module.params['rhsm_repo_ca_cert']
    auto_attach = module.params['auto_attach']
    activationkey = module.params['activationkey']
    org_id = module.params['org_id']
    if activationkey and not org_id:
        module.fail_json(msg='org_id is required when using activationkey')
    environment = module.params['environment']
    pool = module.params['pool']
    pool_ids = {}
    for value in module.params['pool_ids']:
        if isinstance(value, dict):
            if len(value) != 1:
                module.fail_json(msg='Unable to parse pool_ids option.')
            pool_id, quantity = list(value.items())[0]
        else:
            pool_id, quantity = value, None
        pool_ids[pool_id] = quantity
    consumer_type = module.params["consumer_type"]
    consumer_name = module.params["consumer_name"]
    consumer_id = module.params["consumer_id"]
    force_register = module.params["force_register"]
    server_proxy_hostname = module.params['server_proxy_hostname']
    server_proxy_port = module.params['server_proxy_port']
    server_proxy_user = module.params['server_proxy_user']
    server_proxy_password = module.params['server_proxy_password']
    release = module.params['release']
    syspurpose = module.params['syspurpose']

    global SUBMAN_CMD
    SUBMAN_CMD = module.get_bin_path('subscription-manager', True)

    syspurpose_changed = False
    if syspurpose is not None:
        try:
            syspurpose_changed = SysPurpose().update_syspurpose(syspurpose)
        except Exception as err:
            module.fail_json(msg="Failed to update syspurpose attributes: %s" % to_native(err))

    # Ensure system is registered
    if state == 'present':

        # Cache the status of the system before the changes
        was_registered = rhsm.is_registered

        # Register system
        if was_registered and not force_register:
            if syspurpose and 'sync' in syspurpose and syspurpose['sync'] is True:
                try:
                    rhsm.sync_syspurpose()
                except Exception as e:
                    module.fail_json(msg="Failed to synchronize syspurpose attributes: %s" % to_native(e))
            if pool != '^$' or pool_ids:
                try:
                    if pool_ids:
                        result = rhsm.update_subscriptions_by_pool_ids(pool_ids)
                    else:
                        result = rhsm.update_subscriptions(pool)
                except Exception as e:
                    module.fail_json(msg="Failed to update subscriptions for '%s': %s" % (server_hostname, to_native(e)))
                else:
                    module.exit_json(**result)
            else:
                if syspurpose_changed is True:
                    module.exit_json(changed=True, msg="Syspurpose attributes changed.")
                else:
                    module.exit_json(changed=False, msg="System already registered.")
        else:
            if not username and not activationkey and not token:
                module.fail_json(msg="state is present but any of the following are missing: username, activationkey, token")
            try:
                rhsm.enable()
                rhsm.configure(**module.params)
                rhsm.register(was_registered, username, password, token, auto_attach, activationkey, org_id,
                              consumer_type, consumer_name, consumer_id, force_register,
                              environment, release)
                if syspurpose and 'sync' in syspurpose and syspurpose['sync'] is True:
                    rhsm.sync_syspurpose()
                if pool_ids:
                    subscribed_pool_ids = rhsm.subscribe_by_pool_ids(pool_ids)
                elif pool != '^$':
                    subscribed_pool_ids = rhsm.subscribe(pool)
                else:
                    subscribed_pool_ids = []
            except Exception as e:
                module.fail_json(msg="Failed to register with '%s': %s" % (server_hostname, to_native(e)))
            else:
                module.exit_json(changed=True,
                                 msg="System successfully registered to '%s'." % server_hostname,
                                 subscribed_pool_ids=subscribed_pool_ids)

    # Ensure system is *not* registered
    if state == 'absent':
        if not rhsm.is_registered:
            module.exit_json(changed=False, msg="System already unregistered.")
        else:
            try:
                rhsm.unsubscribe()
                rhsm.unregister()
            except Exception as e:
                module.fail_json(msg="Failed to unregister: %s" % to_native(e))
            else:
                module.exit_json(changed=True, msg="System successfully unregistered from %s." % server_hostname)


if __name__ == '__main__':
    main()
