# -*- coding: utf-8 -*-
#
# Copyright (2016-2017) Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import re
import yaml

from mock import Mock, patch
from .oneview_module_loader import ONEVIEW_MODULE_UTILS_PATH
from hpOneView.oneview_client import OneViewClient


class OneViewBaseTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, mock_ansible_module, mock_ov_client, request):
        marker = request.node.get_marker('resource')
        self.resource = getattr(mock_ov_client, "%s" % (marker.args))
        self.mock_ov_client = mock_ov_client
        self.mock_ansible_module = mock_ansible_module

    @pytest.fixture
    def testing_module(self):
        resource_name = type(self).__name__.replace('Test', '')
        resource_module_path_name = resource_name.replace('Module', '')
        resource_module_path_name = re.findall('[A-Z][^A-Z]*', resource_module_path_name)
        resource_module_path_name = 'oneview_' + str.join('_', resource_module_path_name).lower()

        ansible_collections = __import__('ansible_collections')
        oneview_module = ansible_collections.community.general.plugins.modules.remote_management.oneview
        resource_module = getattr(oneview_module, resource_module_path_name)
        self.testing_class = getattr(resource_module, resource_name)
        testing_module = self.testing_class.__module__.split('.')[-1]
        testing_module = getattr(oneview_module, testing_module)
        try:
            # Load scenarios from module examples (Also checks if it is a valid yaml)
            EXAMPLES = yaml.load(testing_module.EXAMPLES, yaml.SafeLoader)

        except yaml.scanner.ScannerError:
            message = "Something went wrong while parsing yaml from {0}.EXAMPLES".format(self.testing_class.__module__)
            raise Exception(message)
        return testing_module

    def test_main_function_should_call_run_method(self, testing_module, mock_ansible_module):
        mock_ansible_module.params = {'config': 'config.json'}

        main_func = getattr(testing_module, 'main')

        with patch.object(self.testing_class, "run") as mock_run:
            main_func()
            mock_run.assert_called_once()


class FactsParamsTest(OneViewBaseTest):
    def test_should_get_all_using_filters(self, testing_module):
        self.resource.get_all.return_value = []

        params_get_all_with_filters = dict(
            config='config.json',
            name=None,
            params={
                'start': 1,
                'count': 3,
                'sort': 'name:descending',
                'filter': 'purpose=General',
                'query': 'imported eq true'
            })
        self.mock_ansible_module.params = params_get_all_with_filters

        self.testing_class().run()

        self.resource.get_all.assert_called_once_with(start=1, count=3, sort='name:descending', filter='purpose=General', query='imported eq true')

    def test_should_get_all_without_params(self, testing_module):
        self.resource.get_all.return_value = []

        params_get_all_with_filters = dict(
            config='config.json',
            name=None
        )
        self.mock_ansible_module.params = params_get_all_with_filters

        self.testing_class().run()

        self.resource.get_all.assert_called_once_with()


class OneViewBaseTestCase(object):
    mock_ov_client_from_json_file = None
    testing_class = None
    mock_ansible_module = None
    mock_ov_client = None
    testing_module = None
    EXAMPLES = None

    def configure_mocks(self, test_case, testing_class):
        """
        Preload mocked OneViewClient instance and AnsibleModule
        Args:
            test_case (object): class instance (self) that are inheriting from OneViewBaseTestCase
            testing_class (object): class being tested
        """
        self.testing_class = testing_class

        # Define OneView Client Mock (FILE)
        patcher_json_file = patch.object(OneViewClient, 'from_json_file')
        test_case.addCleanup(patcher_json_file.stop)
        self.mock_ov_client_from_json_file = patcher_json_file.start()

        # Define OneView Client Mock
        self.mock_ov_client = self.mock_ov_client_from_json_file.return_value

        # Define Ansible Module Mock
        patcher_ansible = patch(ONEVIEW_MODULE_UTILS_PATH + '.AnsibleModule')
        test_case.addCleanup(patcher_ansible.stop)
        mock_ansible_module = patcher_ansible.start()
        self.mock_ansible_module = Mock()
        mock_ansible_module.return_value = self.mock_ansible_module

        self.__set_module_examples()

    def test_main_function_should_call_run_method(self):
        self.mock_ansible_module.params = {'config': 'config.json'}

        main_func = getattr(self.testing_module, 'main')

        with patch.object(self.testing_class, "run") as mock_run:
            main_func()
            mock_run.assert_called_once()

    def __set_module_examples(self):
        # Load scenarios from module examples (Also checks if it is a valid yaml)
        ansible_collections = __import__('ansible_collections')
        testing_module = self.testing_class.__module__.split('.')[-1]
        self.testing_module = getattr(ansible_collections.community.general.plugins.modules.remote_management.oneview, testing_module)

        try:
            # Load scenarios from module examples (Also checks if it is a valid yaml)
            self.EXAMPLES = yaml.load(self.testing_module.EXAMPLES, yaml.SafeLoader)

        except yaml.scanner.ScannerError:
            message = "Something went wrong while parsing yaml from {0}.EXAMPLES".format(self.testing_class.__module__)
            raise Exception(message)


class FactsParamsTestCase(OneViewBaseTestCase):
    """
    FactsParamsTestCase has common test for classes that support pass additional
        parameters when retrieving all resources.
    """

    def configure_client_mock(self, resorce_client):
        """
        Args:
             resorce_client: Resource client that is being called
        """
        self.resource_client = resorce_client

    def __validations(self):
        if not self.testing_class:
            raise Exception("Mocks are not configured, you must call 'configure_mocks' before running this test.")

        if not self.resource_client:
            raise Exception(
                "Mock for the client not configured, you must call 'configure_client_mock' before running this test.")

    def test_should_get_all_using_filters(self):
        self.__validations()
        self.resource_client.get_all.return_value = []

        params_get_all_with_filters = dict(
            config='config.json',
            name=None,
            params={
                'start': 1,
                'count': 3,
                'sort': 'name:descending',
                'filter': 'purpose=General',
                'query': 'imported eq true'
            })
        self.mock_ansible_module.params = params_get_all_with_filters

        self.testing_class().run()

        self.resource_client.get_all.assert_called_once_with(start=1, count=3, sort='name:descending',
                                                             filter='purpose=General',
                                                             query='imported eq true')

    def test_should_get_all_without_params(self):
        self.__validations()
        self.resource_client.get_all.return_value = []

        params_get_all_with_filters = dict(
            config='config.json',
            name=None
        )
        self.mock_ansible_module.params = params_get_all_with_filters

        self.testing_class().run()

        self.resource_client.get_all.assert_called_once_with()
