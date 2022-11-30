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
short_description: Manage registration and subscriptions to RHSM using the C(subscription-manager) command
description:
    - Manage registration and subscription to the Red Hat Subscription Management entitlement platform using the C(subscription-manager) command
author: "Barnaby Court (@barnabycourt)"
notes:
    - In order to register a system, subscription-manager requires either a username and password, or an activationkey and an Organization ID.
    - Since 2.5 values for I(server_hostname), I(server_insecure), I(rhsm_baseurl),
      I(server_proxy_hostname), I(server_proxy_port), I(server_proxy_user) and
      I(server_proxy_password) are no longer taken from the C(/etc/rhsm/rhsm.conf)
      config file and default to None.
requirements:
    - subscription-manager
options:
    state:
        description:
          - whether to register and subscribe (C(present)), or unregister (C(absent)) a system
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
    server_hostname:
        description:
            - Specify an alternative Red Hat Subscription Management or Red Hat Satellite or Katello server
        type: str
    server_insecure:
        description:
            - Enable or disable https server certificate verification when connecting to C(server_hostname)
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
            - Added in favor of deprecated autosubscribe in 2.5.
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
              Specify a subscription pool name to consume.  Regular expressions accepted. Use I(pool_ids) instead if
              possible, as it is much faster. Mutually exclusive with I(pool_ids).
        default: '^$'
        type: str
    pool_ids:
        description:
            - |
              Specify subscription pool IDs to consume. Prefer over I(pool) when possible as it is much faster.
              A pool ID may be specified as a C(string) - just the pool ID (ex. C(0123456789abcdef0123456789abcdef)),
              or as a C(dict) with the pool ID as the key, and a quantity as the value (ex.
              C(0123456789abcdef0123456789abcdef: 2). If the quantity is provided, it is used to consume multiple
              entitlements from a pool (the pool must support this). Mutually exclusive with I(pool).
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
                    - When this option is true, then syspurpose attributes are synchronized with
                      RHSM server immediately. When this option is false, then syspurpose attributes
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
from os import unlink
import re
import shutil
import tempfile
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six.moves import configparser


SUBMAN_CMD = None


class RegistrationBase(object):

    REDHAT_REPO = "/etc/yum.repos.d/redhat.repo"

    def __init__(self, module, username=None, password=None):
        self.module = module
        self.username = username
        self.password = password

    def configure(self):
        raise NotImplementedError("Must be implemented by a sub-class")

    def enable(self):
        # Remove any existing redhat.repo
        if isfile(self.REDHAT_REPO):
            unlink(self.REDHAT_REPO)

    def register(self):
        raise NotImplementedError("Must be implemented by a sub-class")

    def unregister(self):
        raise NotImplementedError("Must be implemented by a sub-class")

    def unsubscribe(self):
        raise NotImplementedError("Must be implemented by a sub-class")

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

    def subscribe(self, **kwargs):
        raise NotImplementedError("Must be implemented by a sub-class")


class Rhsm(RegistrationBase):
    def __init__(self, module, username=None, password=None):
        RegistrationBase.__init__(self, module, username, password)
        self.module = module

    def enable(self):
        '''
            Enable the system to receive updates from subscription-manager.
            This involves updating affected yum plugins and removing any
            conflicting yum repositories.
        '''
        RegistrationBase.enable(self)
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

    def register(self, username, password, auto_attach, activationkey, org_id,
                 consumer_type, consumer_name, consumer_id, force_register, environment,
                 release):
        '''
            Register the current system to the provided RHSM or Red Hat Satellite
            or Katello server

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
        else:
            if username:
                args.extend(['--username', username])
            if password:
                args.extend(['--password', password])

        if release:
            args.extend(['--release', release])

        rc, stderr, stdout = self.module.run_command(args, check_rc=True, expand_user_and_vars=False)

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

    # Load RHSM configuration from file
    rhsm = Rhsm(None)

    # Note: the default values for parameters are:
    # 'type': 'str', 'default': None, 'required': False
    # So there is no need to repeat these values for each parameter.
    module = AnsibleModule(
        argument_spec={
            'state': {'default': 'present', 'choices': ['present', 'absent']},
            'username': {},
            'password': {'no_log': True},
            'server_hostname': {},
            'server_insecure': {},
            'server_prefix': {},
            'server_port': {},
            'rhsm_baseurl': {},
            'rhsm_repo_ca_cert': {},
            'auto_attach': {'aliases': ['autosubscribe'], 'type': 'bool'},
            'activationkey': {'no_log': True},
            'org_id': {},
            'environment': {},
            'pool': {'default': '^$'},
            'pool_ids': {'default': [], 'type': 'list', 'elements': 'raw'},
            'consumer_type': {},
            'consumer_name': {},
            'consumer_id': {},
            'force_register': {'default': False, 'type': 'bool'},
            'server_proxy_hostname': {},
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
                            ['activationkey', 'consumer_id'],
                            ['activationkey', 'environment'],
                            ['activationkey', 'auto_attach'],
                            ['pool', 'pool_ids']],
        required_if=[['state', 'present', ['username', 'activationkey'], True]],
    )

    rhsm.module = module
    state = module.params['state']
    username = module.params['username']
    password = module.params['password']
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

        # Register system
        if rhsm.is_registered and not force_register:
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
            try:
                rhsm.enable()
                rhsm.configure(**module.params)
                rhsm.register(username, password, auto_attach, activationkey, org_id,
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
