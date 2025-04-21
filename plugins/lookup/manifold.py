# -*- coding: utf-8 -*-
# Copyright (c) 2018, Arigato Machine Inc.
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author:
        - Kyrylo Galanov (!UNKNOWN) <galanoff@gmail.com>
    name: manifold
    short_description: get credentials from Manifold.co
    description:
        - Retrieves resources' credentials from Manifold.co
    deprecated:
        removed_in: 11.0.0
        why: Manifold (the company) has been acquired in 2021 and the services used by this plugin are no longer operational.
        alternative: There is none.
    options:
        _terms:
            description:
                - Optional list of resource labels to lookup on Manifold.co. If no resources are specified, all
                  matched resources will be returned.
            type: list
            elements: string
            required: false
        api_token:
            description:
                - manifold API token
            type: string
            required: true
            env:
              - name: MANIFOLD_API_TOKEN
        project:
            description:
                - The project label you want to get the resource for.
            type: string
            required: false
        team:
            description:
                - The team label you want to get the resource for.
            type: string
            required: false
'''

EXAMPLES = '''
    - name: all available resources
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.manifold', api_token='SecretToken') }}"
    - name: all available resources for a specific project in specific team
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.manifold', api_token='SecretToken', project='poject-1', team='team-2') }}"
    - name: two specific resources
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.manifold', 'resource-1', 'resource-2') }}"
'''

RETURN = '''
    _raw:
        description:
            - dictionary of credentials ready to be consumed as environment variables. If multiple resources define
              the same environment variable(s), the last one returned by the Manifold API will take precedence.
        type: dict
'''
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url, ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils import six
from ansible.utils.display import Display
from traceback import format_exception
import json
import sys

display = Display()


class ApiError(Exception):
    pass


class ManifoldApiClient(object):
    http_agent = 'python-manifold-ansible-1.0.0'

    def __init__(self, token):
        self._token = token

    def _make_url(self, api, endpoint):
        return f'https://api.{api}.manifold.co/v1/{endpoint}'

    def request(self, api, endpoint, *args, **kwargs):
        """
        Send a request to API backend and pre-process a response.
        :param api: API to send a request to
        :type api: str
        :param endpoint: API endpoint to fetch data from
        :type endpoint: str
        :param args: other args for open_url
        :param kwargs: other kwargs for open_url
        :return: server response. JSON response is automatically deserialized.
        :rtype: dict | list | str
        """

        default_headers = {
            'Authorization': f"Bearer {self._token}",
            'Accept': "*/*"  # Otherwise server doesn't set content-type header
        }

        url = self._make_url(api, endpoint)

        headers = default_headers
        arg_headers = kwargs.pop('headers', None)
        if arg_headers:
            headers.update(arg_headers)

        try:
            display.vvvv(f'manifold lookup connecting to {url}')
            response = open_url(url, headers=headers, http_agent=self.http_agent, *args, **kwargs)
            data = response.read()
            if response.headers.get('content-type') == 'application/json':
                data = json.loads(data)
            return data
        except ValueError:
            raise ApiError(f'JSON response can\'t be parsed while requesting {url}:\n{data}')
        except HTTPError as e:
            raise ApiError(f'Server returned: {e} while requesting {url}:\n{e.read()}')
        except URLError as e:
            raise ApiError(f'Failed lookup url for {url} : {e}')
        except SSLValidationError as e:
            raise ApiError(f'Error validating the server\'s certificate for {url}: {e}')
        except ConnectionError as e:
            raise ApiError(f'Error connecting to {url}: {e}')

    def get_resources(self, team_id=None, project_id=None, label=None):
        """
        Get resources list
        :param team_id: ID of the Team to filter resources by
        :type team_id: str
        :param project_id: ID of the project to filter resources by
        :type project_id: str
        :param label: filter resources by a label, returns a list with one or zero elements
        :type label: str
        :return: list of resources
        :rtype: list
        """
        api = 'marketplace'
        endpoint = 'resources'
        query_params = {}

        if team_id:
            query_params['team_id'] = team_id
        if project_id:
            query_params['project_id'] = project_id
        if label:
            query_params['label'] = label

        if query_params:
            endpoint += f"?{urlencode(query_params)}"

        return self.request(api, endpoint)

    def get_teams(self, label=None):
        """
        Get teams list
        :param label: filter teams by a label, returns a list with one or zero elements
        :type label: str
        :return: list of teams
        :rtype: list
        """
        api = 'identity'
        endpoint = 'teams'
        data = self.request(api, endpoint)
        # Label filtering is not supported by API, however this function provides uniform interface
        if label:
            data = list(filter(lambda x: x['body']['label'] == label, data))
        return data

    def get_projects(self, label=None):
        """
        Get projects list
        :param label: filter projects by a label, returns a list with one or zero elements
        :type label: str
        :return: list of projects
        :rtype: list
        """
        api = 'marketplace'
        endpoint = 'projects'
        query_params = {}

        if label:
            query_params['label'] = label

        if query_params:
            endpoint += f"?{urlencode(query_params)}"

        return self.request(api, endpoint)

    def get_credentials(self, resource_id):
        """
        Get resource credentials
        :param resource_id: ID of the resource to filter credentials by
        :type resource_id: str
        :return:
        """
        api = 'marketplace'
        endpoint = f"credentials?{urlencode({'resource_id': resource_id})}"
        return self.request(api, endpoint)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """
        :param terms: a list of resources lookups to run.
        :param variables: ansible variables active at the time of the lookup
        :param api_token: API token
        :param project: optional project label
        :param team: optional team label
        :return: a dictionary of resources credentials
        """

        self.set_options(var_options=variables, direct=kwargs)

        api_token = self.get_option('api_token')
        project = self.get_option('project')
        team = self.get_option('team')

        try:
            labels = terms
            client = ManifoldApiClient(api_token)

            if team:
                team_data = client.get_teams(team)
                if len(team_data) == 0:
                    raise AnsibleError(f"Team '{team}' does not exist")
                team_id = team_data[0]['id']
            else:
                team_id = None

            if project:
                project_data = client.get_projects(project)
                if len(project_data) == 0:
                    raise AnsibleError(f"Project '{project}' does not exist")
                project_id = project_data[0]['id']
            else:
                project_id = None

            if len(labels) == 1:  # Use server-side filtering if one resource is requested
                resources_data = client.get_resources(team_id=team_id, project_id=project_id, label=labels[0])
            else:  # Get all resources and optionally filter labels
                resources_data = client.get_resources(team_id=team_id, project_id=project_id)
                if labels:
                    resources_data = list(filter(lambda x: x['body']['label'] in labels, resources_data))

            if labels and len(resources_data) < len(labels):
                fetched_labels = [r['body']['label'] for r in resources_data]
                not_found_labels = [label for label in labels if label not in fetched_labels]
                raise AnsibleError(f"Resource(s) {', '.join(not_found_labels)} do not exist")

            credentials = {}
            cred_map = {}
            for resource in resources_data:
                resource_credentials = client.get_credentials(resource['id'])
                if len(resource_credentials) and resource_credentials[0]['body']['values']:
                    for cred_key, cred_val in six.iteritems(resource_credentials[0]['body']['values']):
                        label = resource['body']['label']
                        if cred_key in credentials:
                            display.warning(f"'{cred_key}' with label '{cred_map[cred_key]}' was replaced by resource data with label '{label}'")
                        credentials[cred_key] = cred_val
                        cred_map[cred_key] = label

            ret = [credentials]
            return ret
        except ApiError as e:
            raise AnsibleError(f'API Error: {e}')
        except AnsibleError as e:
            raise e
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise AnsibleError(format_exception(exc_type, exc_value, exc_traceback))
