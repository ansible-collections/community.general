# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import os
import traceback

from ansible.module_utils.basic import missing_required_lib

CLIENT_IMP_ERR = None
try:
    from manageiq_client.api import ManageIQClient
    HAS_CLIENT = True
except ImportError:
    CLIENT_IMP_ERR = traceback.format_exc()
    HAS_CLIENT = False


def manageiq_argument_spec():
    options = dict(
        url=dict(default=os.environ.get('MIQ_URL', None)),
        username=dict(default=os.environ.get('MIQ_USERNAME', None)),
        password=dict(default=os.environ.get('MIQ_PASSWORD', None), no_log=True),
        token=dict(default=os.environ.get('MIQ_TOKEN', None), no_log=True),
        validate_certs=dict(default=True, type='bool', aliases=['verify_ssl']),
        ca_cert=dict(required=False, default=None, aliases=['ca_bundle_path']),
    )

    return dict(
        manageiq_connection=dict(type='dict',
                                 apply_defaults=True,
                                 options=options),
    )


def check_client(module):
    if not HAS_CLIENT:
        module.fail_json(msg=missing_required_lib('manageiq-client'), exception=CLIENT_IMP_ERR)


def validate_connection_params(module):
    params = module.params['manageiq_connection']
    error_str = "missing required argument: manageiq_connection[{}]"
    url = params['url']
    token = params['token']
    username = params['username']
    password = params['password']

    if (url and username and password) or (url and token):
        return params
    for arg in ['url', 'username', 'password']:
        if params[arg] in (None, ''):
            module.fail_json(msg=error_str.format(arg))


def manageiq_entities():
    return {
        'provider': 'providers', 'host': 'hosts', 'vm': 'vms',
        'category': 'categories', 'cluster': 'clusters', 'data store': 'data_stores',
        'group': 'groups', 'resource pool': 'resource_pools', 'service': 'services',
        'service template': 'service_templates', 'template': 'templates',
        'tenant': 'tenants', 'user': 'users', 'blueprint': 'blueprints'
    }


class ManageIQ(object):
    """
        class encapsulating ManageIQ API client.
    """

    def __init__(self, module):
        # handle import errors
        check_client(module)

        params = validate_connection_params(module)

        url = params['url']
        username = params['username']
        password = params['password']
        token = params['token']
        verify_ssl = params['validate_certs']
        ca_bundle_path = params['ca_cert']

        self._module = module
        self._api_url = url + '/api'
        self._auth = dict(user=username, password=password, token=token)
        try:
            self._client = ManageIQClient(self._api_url, self._auth, verify_ssl=verify_ssl, ca_bundle_path=ca_bundle_path)
        except Exception as e:
            self.module.fail_json(msg="failed to open connection (%s): %s" % (url, str(e)))

    @property
    def module(self):
        """ Ansible module module

        Returns:
            the ansible module
        """
        return self._module

    @property
    def api_url(self):
        """ Base ManageIQ API

        Returns:
            the base ManageIQ API
        """
        return self._api_url

    @property
    def client(self):
        """ ManageIQ client

        Returns:
            the ManageIQ client
        """
        return self._client

    def find_collection_resource_by(self, collection_name, **params):
        """ Searches the collection resource by the collection name and the param passed.

        Returns:
            the resource as an object if it exists in manageiq, None otherwise.
        """
        try:
            entity = self.client.collections.__getattribute__(collection_name).get(**params)
        except ValueError:
            return None
        except Exception as e:
            self.module.fail_json(msg="failed to find resource {error}".format(error=e))
        return vars(entity)

    def find_collection_resource_or_fail(self, collection_name, **params):
        """ Searches the collection resource by the collection name and the param passed.

        Returns:
            the resource as an object if it exists in manageiq, Fail otherwise.
        """
        resource = self.find_collection_resource_by(collection_name, **params)
        if resource:
            return resource
        else:
            msg = "{collection_name} where {params} does not exist in manageiq".format(
                collection_name=collection_name, params=str(params))
            self.module.fail_json(msg=msg)

    def policies(self, resource_id, resource_type, resource_name):
        manageiq = ManageIQ(self.module)

        # query resource id, fail if resource does not exist
        if resource_id is None:
            resource_id = manageiq.find_collection_resource_or_fail(resource_type, name=resource_name)['id']

        return ManageIQPolicies(manageiq, resource_type, resource_id)

    def query_resource_id(self, resource_type, resource_name):
        """ Query the resource name in ManageIQ.

        Returns:
            the resource ID if it exists in ManageIQ, Fail otherwise.
        """
        resource = self.find_collection_resource_by(resource_type, name=resource_name)
        if resource:
            return resource["id"]
        else:
            msg = "{resource_name} {resource_type} does not exist in manageiq".format(
                resource_name=resource_name, resource_type=resource_type)
            self.module.fail_json(msg=msg)


class ManageIQPolicies(object):
    """
        Object to execute policies management operations of manageiq resources.
    """

    def __init__(self, manageiq, resource_type, resource_id):
        self.manageiq = manageiq

        self.module = self.manageiq.module
        self.api_url = self.manageiq.api_url
        self.client = self.manageiq.client

        self.resource_type = resource_type
        self.resource_id = resource_id
        self.resource_url = '{api_url}/{resource_type}/{resource_id}'.format(
            api_url=self.api_url,
            resource_type=resource_type,
            resource_id=resource_id)

    def query_profile_href(self, profile):
        """ Add or Update the policy_profile href field

        Example:
            {name: STR, ...} => {name: STR, href: STR}
        """
        resource = self.manageiq.find_collection_resource_or_fail(
            "policy_profiles", **profile)
        return dict(name=profile['name'], href=resource['href'])

    def query_resource_profiles(self):
        """ Returns a set of the profile objects objects assigned to the resource
        """
        url = '{resource_url}/policy_profiles?expand=resources'
        try:
            response = self.client.get(url.format(resource_url=self.resource_url))
        except Exception as e:
            msg = "Failed to query {resource_type} policies: {error}".format(
                resource_type=self.resource_type,
                error=e)
            self.module.fail_json(msg=msg)

        resources = response.get('resources', [])

        # clean the returned rest api profile object to look like:
        # {profile_name: STR, profile_description: STR, policies: ARR<POLICIES>}
        profiles = [self.clean_profile_object(profile) for profile in resources]

        return profiles

    def query_profile_policies(self, profile_id):
        """ Returns a set of the policy objects assigned to the resource
        """
        url = '{api_url}/policy_profiles/{profile_id}?expand=policies'
        try:
            response = self.client.get(url.format(api_url=self.api_url, profile_id=profile_id))
        except Exception as e:
            msg = "Failed to query {resource_type} policies: {error}".format(
                resource_type=self.resource_type,
                error=e)
            self.module.fail_json(msg=msg)

        resources = response.get('policies', [])

        # clean the returned rest api policy object to look like:
        # {name: STR, description: STR, active: BOOL}
        policies = [self.clean_policy_object(policy) for policy in resources]

        return policies

    def clean_policy_object(self, policy):
        """ Clean a policy object to have human readable form of:
        {
            name: STR,
            description: STR,
            active: BOOL
        }
        """
        name = policy.get('name')
        description = policy.get('description')
        active = policy.get('active')

        return dict(
            name=name,
            description=description,
            active=active)

    def clean_profile_object(self, profile):
        """ Clean a profile object to have human readable form of:
        {
            profile_name: STR,
            profile_description: STR,
            policies: ARR<POLICIES>
        }
        """
        profile_id = profile['id']
        name = profile.get('name')
        description = profile.get('description')
        policies = self.query_profile_policies(profile_id)

        return dict(
            profile_name=name,
            profile_description=description,
            policies=policies)

    def profiles_to_update(self, profiles, action):
        """ Create a list of policies we need to update in ManageIQ.

        Returns:
            Whether or not a change took place and a message describing the
            operation executed.
        """
        profiles_to_post = []
        assigned_profiles = self.query_resource_profiles()

        # make a list of assigned full profile names strings
        # e.g. ['openscap profile', ...]
        assigned_profiles_set = set([profile['profile_name'] for profile in assigned_profiles])

        for profile in profiles:
            assigned = profile.get('name') in assigned_profiles_set

            if (action == 'unassign' and assigned) or (action == 'assign' and not assigned):
                # add/update the policy profile href field
                # {name: STR, ...} => {name: STR, href: STR}
                profile = self.query_profile_href(profile)
                profiles_to_post.append(profile)

        return profiles_to_post

    def assign_or_unassign_profiles(self, profiles, action):
        """ Perform assign/unassign action
        """
        # get a list of profiles needed to be changed
        profiles_to_post = self.profiles_to_update(profiles, action)
        if not profiles_to_post:
            return dict(
                changed=False,
                msg="Profiles {profiles} already {action}ed, nothing to do".format(
                    action=action,
                    profiles=profiles))

        # try to assign or unassign profiles to resource
        url = '{resource_url}/policy_profiles'.format(resource_url=self.resource_url)
        try:
            response = self.client.post(url, action=action, resources=profiles_to_post)
        except Exception as e:
            msg = "Failed to {action} profile: {error}".format(
                action=action,
                error=e)
            self.module.fail_json(msg=msg)

        # check all entities in result to be successful
        for result in response['results']:
            if not result['success']:
                msg = "Failed to {action}: {message}".format(
                    action=action,
                    message=result['message'])
                self.module.fail_json(msg=msg)

        # successfully changed all needed profiles
        return dict(
            changed=True,
            msg="Successfully {action}ed profiles: {profiles}".format(
                action=action,
                profiles=profiles))


class ManageIQTags(object):
    """
        Object to execute tags management operations of manageiq resources.
    """

    def __init__(self, manageiq, resource_type, resource_id):
        self.manageiq = manageiq

        self.module = self.manageiq.module
        self.api_url = self.manageiq.api_url
        self.client = self.manageiq.client

        self.resource_type = resource_type
        self.resource_id = resource_id
        self.resource_url = '{api_url}/{resource_type}/{resource_id}'.format(
            api_url=self.api_url,
            resource_type=resource_type,
            resource_id=resource_id)

    def full_tag_name(self, tag):
        """ Returns the full tag name in manageiq
        """
        return '/managed/{tag_category}/{tag_name}'.format(
            tag_category=tag['category'],
            tag_name=tag['name'])

    def clean_tag_object(self, tag):
        """ Clean a tag object to have human readable form of:
        {
            full_name: STR,
            name: STR,
            display_name: STR,
            category: STR
        }
        """
        full_name = tag.get('name')
        categorization = tag.get('categorization', {})

        return dict(
            full_name=full_name,
            name=categorization.get('name'),
            display_name=categorization.get('display_name'),
            category=categorization.get('category', {}).get('name'))

    def query_resource_tags(self):
        """ Returns a set of the tag objects assigned to the resource
        """
        url = '{resource_url}/tags?expand=resources&attributes=categorization'
        try:
            response = self.client.get(url.format(resource_url=self.resource_url))
        except Exception as e:
            msg = "Failed to query {resource_type} tags: {error}".format(
                resource_type=self.resource_type,
                error=e)
            self.module.fail_json(msg=msg)

        resources = response.get('resources', [])

        # clean the returned rest api tag object to look like:
        # {full_name: STR, name: STR, display_name: STR, category: STR}
        tags = [self.clean_tag_object(tag) for tag in resources]

        return tags

    def tags_to_update(self, tags, action):
        """ Create a list of tags we need to update in ManageIQ.

        Returns:
            Whether or not a change took place and a message describing the
            operation executed.
        """
        tags_to_post = []
        assigned_tags = self.query_resource_tags()

        # make a list of assigned full tag names strings
        # e.g. ['/managed/environment/prod', ...]
        assigned_tags_set = set([tag['full_name'] for tag in assigned_tags])

        for tag in tags:
            assigned = self.full_tag_name(tag) in assigned_tags_set

            if assigned and action == 'unassign':
                tags_to_post.append(tag)
            elif (not assigned) and action == 'assign':
                tags_to_post.append(tag)

        return tags_to_post

    def assign_or_unassign_tags(self, tags, action):
        """ Perform assign/unassign action
        """
        # get a list of tags needed to be changed
        tags_to_post = self.tags_to_update(tags, action)
        if not tags_to_post:
            return dict(
                changed=False,
                msg="Tags already {action}ed, nothing to do".format(action=action))

        # try to assign or unassign tags to resource
        url = '{resource_url}/tags'.format(resource_url=self.resource_url)
        try:
            response = self.client.post(url, action=action, resources=tags)
        except Exception as e:
            msg = "Failed to {action} tag: {error}".format(
                action=action,
                error=e)
            self.module.fail_json(msg=msg)

        # check all entities in result to be successful
        for result in response['results']:
            if not result['success']:
                msg = "Failed to {action}: {message}".format(
                    action=action,
                    message=result['message'])
                self.module.fail_json(msg=msg)

        # successfully changed all needed tags
        return dict(
            changed=True,
            msg="Successfully {action}ed tags".format(action=action))
