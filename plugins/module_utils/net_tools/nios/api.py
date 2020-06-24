# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2018 Red Hat Inc.
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import os
from functools import partial
from ansible.module_utils._text import to_native
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback

try:
    from infoblox_client.connector import Connector
    from infoblox_client.exceptions import InfobloxException
    HAS_INFOBLOX_CLIENT = True
except ImportError:
    HAS_INFOBLOX_CLIENT = False

# defining nios constants
NIOS_DNS_VIEW = 'view'
NIOS_NETWORK_VIEW = 'networkview'
NIOS_HOST_RECORD = 'record:host'
NIOS_IPV4_NETWORK = 'network'
NIOS_IPV6_NETWORK = 'ipv6network'
NIOS_ZONE = 'zone_auth'
NIOS_PTR_RECORD = 'record:ptr'
NIOS_A_RECORD = 'record:a'
NIOS_AAAA_RECORD = 'record:aaaa'
NIOS_CNAME_RECORD = 'record:cname'
NIOS_MX_RECORD = 'record:mx'
NIOS_SRV_RECORD = 'record:srv'
NIOS_NAPTR_RECORD = 'record:naptr'
NIOS_TXT_RECORD = 'record:txt'
NIOS_NSGROUP = 'nsgroup'
NIOS_IPV4_FIXED_ADDRESS = 'fixedaddress'
NIOS_IPV6_FIXED_ADDRESS = 'ipv6fixedaddress'
NIOS_NEXT_AVAILABLE_IP = 'func:nextavailableip'
NIOS_IPV4_NETWORK_CONTAINER = 'networkcontainer'
NIOS_IPV6_NETWORK_CONTAINER = 'ipv6networkcontainer'
NIOS_MEMBER = 'member'

NIOS_PROVIDER_SPEC = {
    'host': dict(fallback=(env_fallback, ['INFOBLOX_HOST'])),
    'username': dict(fallback=(env_fallback, ['INFOBLOX_USERNAME'])),
    'password': dict(fallback=(env_fallback, ['INFOBLOX_PASSWORD']), no_log=True),
    'validate_certs': dict(type='bool', default=False, fallback=(env_fallback, ['INFOBLOX_SSL_VERIFY']), aliases=['ssl_verify']),
    'silent_ssl_warnings': dict(type='bool', default=True),
    'http_request_timeout': dict(type='int', default=10, fallback=(env_fallback, ['INFOBLOX_HTTP_REQUEST_TIMEOUT'])),
    'http_pool_connections': dict(type='int', default=10),
    'http_pool_maxsize': dict(type='int', default=10),
    'max_retries': dict(type='int', default=3, fallback=(env_fallback, ['INFOBLOX_MAX_RETRIES'])),
    'wapi_version': dict(default='2.1', fallback=(env_fallback, ['INFOBLOX_WAP_VERSION'])),
    'max_results': dict(type='int', default=1000, fallback=(env_fallback, ['INFOBLOX_MAX_RETRIES']))
}


def get_connector(*args, **kwargs):
    ''' Returns an instance of infoblox_client.connector.Connector
    :params args: positional arguments are silently ignored
    :params kwargs: dict that is passed to Connector init
    :returns: Connector
    '''
    if not HAS_INFOBLOX_CLIENT:
        raise Exception('infoblox-client is required but does not appear '
                        'to be installed.  It can be installed using the '
                        'command `pip install infoblox-client`')

    if not set(kwargs.keys()).issubset(list(NIOS_PROVIDER_SPEC.keys()) + ['ssl_verify']):
        raise Exception('invalid or unsupported keyword argument for connector')
    for key, value in iteritems(NIOS_PROVIDER_SPEC):
        if key not in kwargs:
            # apply default values from NIOS_PROVIDER_SPEC since we cannot just
            # assume the provider values are coming from AnsibleModule
            if 'default' in value:
                kwargs[key] = value['default']

            # override any values with env variables unless they were
            # explicitly set
            env = ('INFOBLOX_%s' % key).upper()
            if env in os.environ:
                kwargs[key] = os.environ.get(env)

    if 'validate_certs' in kwargs.keys():
        kwargs['ssl_verify'] = kwargs['validate_certs']
        kwargs.pop('validate_certs', None)

    return Connector(kwargs)


def normalize_extattrs(value):
    ''' Normalize extattrs field to expected format
    The module accepts extattrs as key/value pairs.  This method will
    transform the key/value pairs into a structure suitable for
    sending across WAPI in the format of:
        extattrs: {
            key: {
                value: <value>
            }
        }
    '''
    return dict([(k, {'value': v}) for k, v in iteritems(value)])


def flatten_extattrs(value):
    ''' Flatten the key/value struct for extattrs
    WAPI returns extattrs field as a dict in form of:
        extattrs: {
            key: {
                value: <value>
            }
        }
    This method will flatten the structure to:
        extattrs: {
            key: value
        }
    '''
    return dict([(k, v['value']) for k, v in iteritems(value)])


def member_normalize(member_spec):
    ''' Transforms the member module arguments into a valid WAPI struct
    This function will transform the arguments into a structure that
    is a valid WAPI structure in the format of:
        {
            key: <value>,
        }
    It will remove any arguments that are set to None since WAPI will error on
    that condition.
    The remainder of the value validation is performed by WAPI
    Some parameters in ib_spec are passed as a list in order to pass the validation for elements.
    In this function, they are converted to dictionary.
    '''
    member_elements = ['vip_setting', 'ipv6_setting', 'lan2_port_setting', 'mgmt_port_setting',
                       'pre_provisioning', 'network_setting', 'v6_network_setting',
                       'ha_port_setting', 'lan_port_setting', 'lan2_physical_setting',
                       'lan_ha_port_setting', 'mgmt_network_setting', 'v6_mgmt_network_setting']
    for key in member_spec.keys():
        if key in member_elements and member_spec[key] is not None:
            member_spec[key] = member_spec[key][0]
        if isinstance(member_spec[key], dict):
            member_spec[key] = member_normalize(member_spec[key])
        elif isinstance(member_spec[key], list):
            for x in member_spec[key]:
                if isinstance(x, dict):
                    x = member_normalize(x)
        elif member_spec[key] is None:
            del member_spec[key]
    return member_spec


class WapiBase(object):
    ''' Base class for implementing Infoblox WAPI API '''
    provider_spec = {'provider': dict(type='dict', options=NIOS_PROVIDER_SPEC)}

    def __init__(self, provider):
        self.connector = get_connector(**provider)

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            if name.startswith('_'):
                raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
            return partial(self._invoke_method, name)

    def _invoke_method(self, name, *args, **kwargs):
        try:
            method = getattr(self.connector, name)
            return method(*args, **kwargs)
        except InfobloxException as exc:
            if hasattr(self, 'handle_exception'):
                self.handle_exception(name, exc)
            else:
                raise


class WapiLookup(WapiBase):
    ''' Implements WapiBase for lookup plugins '''
    def handle_exception(self, method_name, exc):
        if ('text' in exc.response):
            raise Exception(exc.response['text'])
        else:
            raise Exception(exc)


class WapiInventory(WapiBase):
    ''' Implements WapiBase for dynamic inventory script '''
    pass


class WapiModule(WapiBase):
    ''' Implements WapiBase for executing a NIOS module '''
    def __init__(self, module):
        self.module = module
        provider = module.params['provider']
        try:
            super(WapiModule, self).__init__(provider)
        except Exception as exc:
            self.module.fail_json(msg=to_text(exc))

    def handle_exception(self, method_name, exc):
        ''' Handles any exceptions raised
        This method will be called if an InfobloxException is raised for
        any call to the instance of Connector and also, in case of generic
        exception. This method will then gracefully fail the module.
        :args exc: instance of InfobloxException
        '''
        if ('text' in exc.response):
            self.module.fail_json(
                msg=exc.response['text'],
                type=exc.response['Error'].split(':')[0],
                code=exc.response.get('code'),
                operation=method_name
            )
        else:
            self.module.fail_json(msg=to_native(exc))

    def run(self, ib_obj_type, ib_spec):
        ''' Runs the module and performans configuration tasks
        :args ib_obj_type: the WAPI object type to operate against
        :args ib_spec: the specification for the WAPI object as a dict
        :returns: a results dict
        '''

        update = new_name = None
        state = self.module.params['state']
        if state not in ('present', 'absent'):
            self.module.fail_json(msg='state must be one of `present`, `absent`, got `%s`' % state)

        result = {'changed': False}

        obj_filter = dict([(k, self.module.params[k]) for k, v in iteritems(ib_spec) if v.get('ib_req')])

        # get object reference
        ib_obj_ref, update, new_name = self.get_object_ref(self.module, ib_obj_type, obj_filter, ib_spec)
        proposed_object = {}
        for key, value in iteritems(ib_spec):
            if self.module.params[key] is not None:
                if 'transform' in value:
                    proposed_object[key] = value['transform'](self.module)
                else:
                    proposed_object[key] = self.module.params[key]

        # If configure_by_dns is set to False, then delete the default dns set in the param else throw exception
        if not proposed_object.get('configure_for_dns') and proposed_object.get('view') == 'default'\
                and ib_obj_type == NIOS_HOST_RECORD:
            del proposed_object['view']
        elif not proposed_object.get('configure_for_dns') and proposed_object.get('view') != 'default'\
                and ib_obj_type == NIOS_HOST_RECORD:
            self.module.fail_json(msg='DNS Bypass is not allowed if DNS view is set other than \'default\'')

        if ib_obj_ref:
            if len(ib_obj_ref) > 1:
                for each in ib_obj_ref:
                    # To check for existing A_record with same name with input A_record by IP
                    if each.get('ipv4addr') and each.get('ipv4addr') == proposed_object.get('ipv4addr'):
                        current_object = each
                    # To check for existing Host_record with same name with input Host_record by IP
                    elif each.get('ipv4addrs')[0].get('ipv4addr') and each.get('ipv4addrs')[0].get('ipv4addr')\
                            == proposed_object.get('ipv4addrs')[0].get('ipv4addr'):
                        current_object = each
                    # Else set the current_object with input value
                    else:
                        current_object = obj_filter
                        ref = None
            else:
                current_object = ib_obj_ref[0]
            if 'extattrs' in current_object:
                current_object['extattrs'] = flatten_extattrs(current_object['extattrs'])
            if current_object.get('_ref'):
                ref = current_object.pop('_ref')
        else:
            current_object = obj_filter
            ref = None
        # checks if the object type is member to normalize the attributes being passed
        if (ib_obj_type == NIOS_MEMBER):
            proposed_object = member_normalize(proposed_object)

        # checks if the name's field has been updated
        if update and new_name:
            proposed_object['name'] = new_name

        check_remove = []
        if (ib_obj_type == NIOS_HOST_RECORD):
            # this check is for idempotency, as if the same ip address shall be passed
            # add param will be removed, and same exists true for remove case as well.
            if 'ipv4addrs' in [current_object and proposed_object]:
                for each in current_object['ipv4addrs']:
                    if each['ipv4addr'] == proposed_object['ipv4addrs'][0]['ipv4addr']:
                        if 'add' in proposed_object['ipv4addrs'][0]:
                            del proposed_object['ipv4addrs'][0]['add']
                            break
                    check_remove += each.values()
                if proposed_object['ipv4addrs'][0]['ipv4addr'] not in check_remove:
                    if 'remove' in proposed_object['ipv4addrs'][0]:
                        del proposed_object['ipv4addrs'][0]['remove']

        res = None
        modified = not self.compare_objects(current_object, proposed_object)
        if 'extattrs' in proposed_object:
            proposed_object['extattrs'] = normalize_extattrs(proposed_object['extattrs'])

        # Checks if nios_next_ip param is passed in ipv4addrs/ipv4addr args
        proposed_object = self.check_if_nios_next_ip_exists(proposed_object)

        if state == 'present':
            if ref is None:
                if not self.module.check_mode:
                    self.create_object(ib_obj_type, proposed_object)
                result['changed'] = True
            # Check if NIOS_MEMBER and the flag to call function create_token is set
            elif (ib_obj_type == NIOS_MEMBER) and (proposed_object['create_token']):
                proposed_object = None
                # the function creates a token that can be used by a pre-provisioned member to join the grid
                result['api_results'] = self.call_func('create_token', ref, proposed_object)
                result['changed'] = True
            elif modified:
                if 'ipv4addrs' in proposed_object:
                    if ('add' not in proposed_object['ipv4addrs'][0]) and ('remove' not in proposed_object['ipv4addrs'][0]):
                        self.check_if_recordname_exists(obj_filter, ib_obj_ref, ib_obj_type, current_object, proposed_object)

                if (ib_obj_type in (NIOS_HOST_RECORD, NIOS_NETWORK_VIEW, NIOS_DNS_VIEW)):
                    run_update = True
                    proposed_object = self.on_update(proposed_object, ib_spec)
                    if 'ipv4addrs' in proposed_object:
                        if ('add' or 'remove') in proposed_object['ipv4addrs'][0]:
                            run_update, proposed_object = self.check_if_add_remove_ip_arg_exists(proposed_object)
                            if run_update:
                                res = self.update_object(ref, proposed_object)
                                result['changed'] = True
                            else:
                                res = ref
                if (ib_obj_type in (NIOS_A_RECORD, NIOS_AAAA_RECORD, NIOS_PTR_RECORD, NIOS_SRV_RECORD)):
                    # popping 'view' key as update of 'view' is not supported with respect to a:record/aaaa:record/srv:record/ptr:record
                    proposed_object = self.on_update(proposed_object, ib_spec)
                    del proposed_object['view']
                    if not self.module.check_mode:
                        res = self.update_object(ref, proposed_object)
                    result['changed'] = True
                elif 'network_view' in proposed_object:
                    proposed_object.pop('network_view')
                    result['changed'] = True
                if not self.module.check_mode and res is None:
                    proposed_object = self.on_update(proposed_object, ib_spec)
                    self.update_object(ref, proposed_object)
                    result['changed'] = True

        elif state == 'absent':
            if ref is not None:
                if 'ipv4addrs' in proposed_object:
                    if 'remove' in proposed_object['ipv4addrs'][0]:
                        self.check_if_add_remove_ip_arg_exists(proposed_object)
                        self.update_object(ref, proposed_object)
                        result['changed'] = True
                elif not self.module.check_mode:
                    self.delete_object(ref)
                    result['changed'] = True

        return result

    def check_if_recordname_exists(self, obj_filter, ib_obj_ref, ib_obj_type, current_object, proposed_object):
        ''' Send POST request if host record input name and retrieved ref name is same,
            but input IP and retrieved IP is different'''

        if 'name' in (obj_filter and ib_obj_ref[0]) and ib_obj_type == NIOS_HOST_RECORD:
            obj_host_name = obj_filter['name']
            ref_host_name = ib_obj_ref[0]['name']
            if 'ipv4addrs' in (current_object and proposed_object):
                current_ip_addr = current_object['ipv4addrs'][0]['ipv4addr']
                proposed_ip_addr = proposed_object['ipv4addrs'][0]['ipv4addr']
            elif 'ipv6addrs' in (current_object and proposed_object):
                current_ip_addr = current_object['ipv6addrs'][0]['ipv6addr']
                proposed_ip_addr = proposed_object['ipv6addrs'][0]['ipv6addr']

            if obj_host_name == ref_host_name and current_ip_addr != proposed_ip_addr:
                self.create_object(ib_obj_type, proposed_object)

    def check_if_nios_next_ip_exists(self, proposed_object):
        ''' Check if nios_next_ip argument is passed in ipaddr while creating
            host record, if yes then format proposed object ipv4addrs and pass
            func:nextavailableip and ipaddr range to create hostrecord with next
             available ip in one call to avoid any race condition '''

        if 'ipv4addrs' in proposed_object:
            if 'nios_next_ip' in proposed_object['ipv4addrs'][0]['ipv4addr']:
                ip_range = self.module._check_type_dict(proposed_object['ipv4addrs'][0]['ipv4addr'])['nios_next_ip']
                proposed_object['ipv4addrs'][0]['ipv4addr'] = NIOS_NEXT_AVAILABLE_IP + ':' + ip_range
        elif 'ipv4addr' in proposed_object:
            if 'nios_next_ip' in proposed_object['ipv4addr']:
                ip_range = self.module._check_type_dict(proposed_object['ipv4addr'])['nios_next_ip']
                proposed_object['ipv4addr'] = NIOS_NEXT_AVAILABLE_IP + ':' + ip_range

        return proposed_object

    def check_if_add_remove_ip_arg_exists(self, proposed_object):
        '''
            This function shall check if add/remove param is set to true and
            is passed in the args, then we will update the proposed dictionary
            to add/remove IP to existing host_record, if the user passes false
            param with the argument nothing shall be done.
            :returns: True if param is changed based on add/remove, and also the
            changed proposed_object.
        '''
        update = False
        if 'add' in proposed_object['ipv4addrs'][0]:
            if proposed_object['ipv4addrs'][0]['add']:
                proposed_object['ipv4addrs+'] = proposed_object['ipv4addrs']
                del proposed_object['ipv4addrs']
                del proposed_object['ipv4addrs+'][0]['add']
                update = True
            else:
                del proposed_object['ipv4addrs'][0]['add']
        elif 'remove' in proposed_object['ipv4addrs'][0]:
            if proposed_object['ipv4addrs'][0]['remove']:
                proposed_object['ipv4addrs-'] = proposed_object['ipv4addrs']
                del proposed_object['ipv4addrs']
                del proposed_object['ipv4addrs-'][0]['remove']
                update = True
            else:
                del proposed_object['ipv4addrs'][0]['remove']
        return update, proposed_object

    def issubset(self, item, objects):
        ''' Checks if item is a subset of objects
        :args item: the subset item to validate
        :args objects: superset list of objects to validate against
        :returns: True if item is a subset of one entry in objects otherwise
            this method will return None
        '''
        for obj in objects:
            if isinstance(item, dict):
                if all(entry in obj.items() for entry in item.items()):
                    return True
            else:
                if item in obj:
                    return True

    def compare_objects(self, current_object, proposed_object):
        for key, proposed_item in iteritems(proposed_object):
            current_item = current_object.get(key)

            # if proposed has a key that current doesn't then the objects are
            # not equal and False will be immediately returned
            if current_item is None:
                return False

            elif isinstance(proposed_item, list):
                for subitem in proposed_item:
                    if not self.issubset(subitem, current_item):
                        return False

            elif isinstance(proposed_item, dict):
                return self.compare_objects(current_item, proposed_item)

            else:
                if current_item != proposed_item:
                    return False

        return True

    def get_object_ref(self, module, ib_obj_type, obj_filter, ib_spec):
        ''' this function gets the reference object of pre-existing nios objects '''

        update = False
        old_name = new_name = None
        if ('name' in obj_filter):
            # gets and returns the current object based on name/old_name passed
            try:
                name_obj = self.module._check_type_dict(obj_filter['name'])
                old_name = name_obj['old_name']
                new_name = name_obj['new_name']
            except TypeError:
                name = obj_filter['name']

            if old_name and new_name:
                if (ib_obj_type == NIOS_HOST_RECORD):
                    test_obj_filter = dict([('name', old_name), ('view', obj_filter['view'])])
                elif (ib_obj_type in (NIOS_AAAA_RECORD, NIOS_A_RECORD)):
                    test_obj_filter = obj_filter
                else:
                    test_obj_filter = dict([('name', old_name)])
                # get the object reference
                ib_obj = self.get_object(ib_obj_type, test_obj_filter, return_fields=ib_spec.keys())
                if ib_obj:
                    obj_filter['name'] = new_name
                else:
                    test_obj_filter['name'] = new_name
                    ib_obj = self.get_object(ib_obj_type, test_obj_filter, return_fields=ib_spec.keys())
                update = True
                return ib_obj, update, new_name
            if (ib_obj_type == NIOS_HOST_RECORD):
                # to check only by name if dns bypassing is set
                if not obj_filter['configure_for_dns']:
                    test_obj_filter = dict([('name', name)])
                else:
                    test_obj_filter = dict([('name', name), ('view', obj_filter['view'])])
            elif (ib_obj_type == NIOS_IPV4_FIXED_ADDRESS or ib_obj_type == NIOS_IPV6_FIXED_ADDRESS and 'mac' in obj_filter):
                test_obj_filter = dict([['mac', obj_filter['mac']]])
            elif (ib_obj_type == NIOS_A_RECORD):
                # resolves issue where a_record with uppercase name was returning null and was failing
                test_obj_filter = obj_filter
                test_obj_filter['name'] = test_obj_filter['name'].lower()
                # resolves issue where multiple a_records with same name and different IP address
                try:
                    ipaddr_obj = self.module._check_type_dict(obj_filter['ipv4addr'])
                    ipaddr = ipaddr_obj['old_ipv4addr']
                except TypeError:
                    ipaddr = obj_filter['ipv4addr']
                test_obj_filter['ipv4addr'] = ipaddr
            elif (ib_obj_type == NIOS_TXT_RECORD):
                # resolves issue where multiple txt_records with same name and different text
                test_obj_filter = obj_filter
                try:
                    text_obj = self.module._check_type_dict(obj_filter['text'])
                    txt = text_obj['old_text']
                except TypeError:
                    txt = obj_filter['text']
                test_obj_filter['text'] = txt
            # check if test_obj_filter is empty copy passed obj_filter
            else:
                test_obj_filter = obj_filter
            ib_obj = self.get_object(ib_obj_type, test_obj_filter.copy(), return_fields=ib_spec.keys())
        elif (ib_obj_type == NIOS_A_RECORD):
            # resolves issue where multiple a_records with same name and different IP address
            test_obj_filter = obj_filter
            try:
                ipaddr_obj = self.module._check_type_dict(obj_filter['ipv4addr'])
                ipaddr = ipaddr_obj['old_ipv4addr']
            except TypeError:
                ipaddr = obj_filter['ipv4addr']
            test_obj_filter['ipv4addr'] = ipaddr
            ib_obj = self.get_object(ib_obj_type, test_obj_filter.copy(), return_fields=ib_spec.keys())
        elif (ib_obj_type == NIOS_TXT_RECORD):
            # resolves issue where multiple txt_records with same name and different text
            test_obj_filter = obj_filter
            try:
                text_obj = self.module._check_type_dict(obj_filter['text'])
                txt = text_obj['old_text']
            except TypeError:
                txt = obj_filter['text']
            test_obj_filter['text'] = txt
            ib_obj = self.get_object(ib_obj_type, test_obj_filter.copy(), return_fields=ib_spec.keys())
        elif (ib_obj_type == NIOS_ZONE):
            # del key 'restart_if_needed' as nios_zone get_object fails with the key present
            temp = ib_spec['restart_if_needed']
            del ib_spec['restart_if_needed']
            ib_obj = self.get_object(ib_obj_type, obj_filter.copy(), return_fields=ib_spec.keys())
            # reinstate restart_if_needed if ib_obj is none, meaning there's no existing nios_zone ref
            if not ib_obj:
                ib_spec['restart_if_needed'] = temp
        elif (ib_obj_type == NIOS_MEMBER):
            # del key 'create_token' as nios_member get_object fails with the key present
            temp = ib_spec['create_token']
            del ib_spec['create_token']
            ib_obj = self.get_object(ib_obj_type, obj_filter.copy(), return_fields=ib_spec.keys())
            if temp:
                # reinstate 'create_token' key
                ib_spec['create_token'] = temp
        else:
            ib_obj = self.get_object(ib_obj_type, obj_filter.copy(), return_fields=ib_spec.keys())
        return ib_obj, update, new_name

    def on_update(self, proposed_object, ib_spec):
        ''' Event called before the update is sent to the API endpoing
        This method will allow the final proposed object to be changed
        and/or keys filtered before it is sent to the API endpoint to
        be processed.
        :args proposed_object: A dict item that will be encoded and sent
            the API endpoint with the updated data structure
        :returns: updated object to be sent to API endpoint
        '''
        keys = set()
        for key, value in iteritems(proposed_object):
            update = ib_spec[key].get('update', True)
            if not update:
                keys.add(key)
        return dict([(k, v) for k, v in iteritems(proposed_object) if k not in keys])
