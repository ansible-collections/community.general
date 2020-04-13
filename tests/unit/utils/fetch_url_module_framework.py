# (c) 2019-2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Small framework for testing modules which use ``fetch_url()`` from
``ansible.module_utils.urls`` to communicate with a HTTP service.

The main interface consists of the classes ``FetchUrlCall`` and
``BaseTestModule``.

A test is expected to be inherited from ``BaseTestModule``. The class
provides two methods, ``run_module_success`` and ``run_module_failed``,
which expect next to the module's Python module and the arguments a list
of ``FetchUrlCall`` objects which correspond to the expected ``fetch_url()``
calls made by the module for the given input. The methods return the
result returned by ``module.fail_json()`` and ``module.exit_json()``,
respectively.

An example test could look as follows::

    from ansible_collections.community.general.tests.unit.utils.fetch_url_module_framework import (
        FetchUrlCall,
        BaseTestModule,
    )

    from ansible_collections.community.general.plugins.module_utils.hetzner import BASE_URL
    from ansible_collections.community.general.plugins.modules.net_tools import hetzner_firewall_info

    class TestHetznerFirewallInfo(BaseTestModule):
        MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.general.plugins.modules.net_tools.hetzner_firewall_info.AnsibleModule'
        MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.general.plugins.module_utils.hetzner.fetch_url'

        def test_absent(self, mocker):
            result = self.run_module_success(mocker, hetzner_firewall_info, {
                'hetzner_user': '',
                'hetzner_password': '',
                'server_ip': '1.2.3.4',
            }, [
                FetchUrlCall('GET', 200)
                .result_json({
                    'firewall': {
                        'server_ip': '1.2.3.4',
                        'server_number': 1,
                        'status': 'disabled',
                        'whitelist_hos': False,
                        'port': 'main',
                        'rules': {
                            'input': [],
                        },
                    },
                })
                .expect_url('{0}/firewall/1.2.3.4'.format(BASE_URL)),
            ])
            assert result['changed'] is False
            assert result['firewall']['status'] == 'disabled'
            assert result['firewall']['server_ip'] == '1.2.3.4'
            assert result['firewall']['server_number'] == 1

This test makes sure that if the ``community.general.hetzner_firewall_info``
module is called with the given arguments, one ``fetch_url()`` call is made
to ``GET`` the URL, and if this call is returned with a ``200 OK`` and the
given JSON object, that the module will return ``result`` which is then
checked by the ``assert`` statements.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import json

import pytest

from mock import MagicMock

import ansible.module_utils.basic  # noqa
import ansible.module_utils.urls  # noqa

from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args
from ansible.module_utils.six.moves.urllib.parse import parse_qs


class FetchUrlCall:
    '''
    Describes one call to ``fetch_url()``.

    This class contains information on what ``fetch_url()`` should return, and how to
    validate the data passed to ``fetch_url()``.
    '''

    def __init__(self, method, status):
        '''
        Create a ``fetch_url()`` expected call. Must be passed information on the expected
        HTTP method and the HTTP status returned by the call.
        '''
        assert method == method.upper(), \
            'HTTP method names are case-sensitive and should be upper-case (RFCs 7230 and 7231)'
        self.method = method
        self.status = status
        self.body = None
        self.headers = {}
        self.error_data = {}
        self.expected_url = None
        self.expected_headers = {}
        self.form_parse = False
        self.form_present = set()
        self.form_values = {}
        self.form_values_one = {}

    def result(self, body):
        '''
        Builder method to set return body of the ``fetch_url()`` call. Must be a bytes string.
        '''
        self.body = body
        assert self.error_data.get('body') is None, 'Error body must not be given'
        return self

    def result_str(self, str_body):
        '''
        Builder method to set return body of the ``fetch_url()`` call as a text string.
        '''
        return self.result(str_body.encode('utf-8'))

    def result_json(self, json_body):
        '''
        Builder method to set return body of the ``fetch_url()`` call as a JSON object.
        '''
        return self.result(json.dumps(json_body).encode('utf-8'))

    def result_error(self, msg, body=None):
        '''
        Builder method to set return body of the ``fetch_url()`` call in case of an error.
        '''
        self.error_data['msg'] = msg
        if body is not None:
            self.error_data['body'] = body
            assert self.body is None, 'Result must not be given if error body is provided'
        return self

    def expect_url(self, url):
        '''
        Builder method to set the expected URL for the ``fetch_url()`` call.
        '''
        self.expected_url = url
        return self

    def return_header(self, name, value):
        '''
        Builder method to set a returned header for the ``fetch_url()`` call.
        '''
        assert value is not None
        self.headers[name] = value
        return self

    def expect_header(self, name, value):
        '''
        Builder method to set an expected header value for a ``fetch_url()`` call.
        '''
        self.expected_headers[name] = value
        return self

    def expect_header_unset(self, name):
        '''
        Builder method to set an expected non-set header for a ``fetch_url()`` call.
        '''
        self.expected_headers[name] = None
        return self

    def expect_form_present(self, key):
        '''
        Builder method to set an expected form field for a ``fetch_url()`` call.
        '''
        self.form_parse = True
        self.form_present.append(key)
        return self

    def expect_form_value(self, key, value):
        '''
        Builder method to set an expected form value for a ``fetch_url()`` call.
        '''
        self.form_parse = True
        self.form_values[key] = [value]
        return self

    def expect_form_value_absent(self, key):
        '''
        Builder method to set an expectedly absent form field for a ``fetch_url()`` call.
        '''
        self.form_parse = True
        self.form_values[key] = []
        return self


class _FetchUrlProxy:
    '''
    Internal proxy for ``fetch_url()``.

    Receives a list of expected ``fetch_url()`` calls, and checks the calls made
    to the proxy against the expected ones. Will raise an exception if too many
    calls are made.
    '''
    def __init__(self, calls):
        '''
        Create instance with expected list of calls.
        '''
        self.calls = calls
        self.index = 0

    def _validate_form(self, call, data):
        '''
        Validate form contents.
        '''
        form = {}
        if data is not None:
            form = parse_qs(data, keep_blank_values=True)
        for k in call.form_present:
            assert k in form
        for k, v in call.form_values.items():
            if len(v) == 0:
                assert k not in form
            else:
                assert form[k] == v
        for k, v in call.form_values_one.items():
            assert v <= set(form[k])

    def _validate_headers(self, call, headers):
        '''
        Validate headers of a call.
        '''
        given_headers = {}
        if headers is not None:
            for k, v in headers.items():
                given_headers[k.lower()] = v
        for k, v in call.expected_headers:
            if v is None:
                assert k.lower() not in given_headers, \
                    'Header "{0}" specified for fetch_url call, but should not be'.format(k)
            else:
                assert given_headers.get(k.lower()) == v, \
                    'Header "{0}" specified for fetch_url call, but with wrong value'.format(k)

    def __call__(self, module, url, data=None, headers=None, method=None,
                 use_proxy=True, force=False, last_mod_time=None, timeout=10,
                 use_gssapi=False, unix_socket=None, ca_path=None, cookies=None):
        '''
        A call to ``fetch_url()``.
        '''
        assert self.index < len(self.calls), 'Got more fetch_url calls than expected'
        call = self.calls[self.index]
        self.index += 1

        # Validate call
        assert method == call.method
        if call.expected_url is not None:
            assert url == call.expected_url, \
                'Exepected URL does not match for fetch_url call'
        if call.expected_headers:
            self._validate_headers(call, headers)
        if call.form_parse:
            self._validate_form(call, data)

        # Compose result
        info = dict(status=call.status)
        for k, v in call.headers.items():
            info[k.lower()] = v
        info.update(call.error_data)
        res = object()
        if call.body is not None:
            res = MagicMock()
            res.read = MagicMock(return_value=call.body)
        return (res, info)

    def assert_is_done(self):
        '''
        Assert that all expected ``fetch_url()`` calls have been made.
        '''
        assert self.index == len(self.calls), 'Got less fetch_url calls than expected'


class ModuleExitException(Exception):
    '''
    Sentry exception to track regular module exit.
    '''
    def __init__(self, kwargs):
        self.kwargs = kwargs


class ModuleFailException(Exception):
    '''
    Sentry exception to track regular module failure.
    '''
    def __init__(self, kwargs):
        self.kwargs = kwargs


class BaseTestModule(object):
    '''
    Base class for testing ``fetch_url()`` based modules.

    Provides support methods ``run_module_success()`` and ``run_module_failed()``.
    '''

    # Users of this class need to overwrite this depending on how AnsibleModule was imported in the module
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible.module_utils.basic.AnsibleModule'
    # Users of this class need to overwrite this depending on how fetch_url was imported in the module
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible.module_utils.urls.fetch_url'


    def run_module(self, mocker, module, arguments, fetch_url):
        def exit_json(module, **kwargs):
            module._return_formatted(kwargs)
            raise ModuleExitException(kwargs)

        def fail_json(module, **kwargs):
            module._return_formatted(kwargs)
            raise ModuleFailException(kwargs)

        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL, fetch_url)
        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE + '.exit_json', exit_json)
        mocker.patch(self.MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE + '.fail_json', fail_json)
        set_module_args(arguments)
        module.main()


    def run_module_success(self, mocker, module, arguments, fetch_url_calls):
        '''
        Run module given by Python module ``module`` with the arguments ``arguments``
        and expected ``fetch_url()`` calls ``fetch_url_calls``. Expect module to exit.
        Returns expanded arguments to ``AnsibleModule.exit_json()``.
        '''
        fetch_url = _FetchUrlProxy(fetch_url_calls or [])
        with pytest.raises(ModuleExitException) as e:
            self.run_module(mocker, module, arguments, fetch_url)
        fetch_url.assert_is_done()
        return e.value.kwargs


    def run_module_failed(self, mocker, module, arguments, fetch_url_calls):
        '''
        Run module given by Python module ``module`` with the arguments ``arguments``
        and expected ``fetch_url()`` calls ``fetch_url_calls``. Expect module to fail.
        Returns expanded arguments to ``AnsibleModule.fail_json()``.
        '''
        fetch_url = _FetchUrlProxy(fetch_url_calls or [])
        with pytest.raises(ModuleFailException) as e:
            self.run_module(mocker, module, arguments, fetch_url)
        fetch_url.assert_is_done()
        return e.value.kwargs
