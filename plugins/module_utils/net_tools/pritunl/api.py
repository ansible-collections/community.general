# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Pritunl API that offers CRUD operations on Pritunl Organizations and Users
"""

from __future__ import absolute_import, division, print_function

import base64
import hashlib
import hmac
import json
import time
import uuid

from ansible.module_utils.six import iteritems
from ansible.module_utils.urls import open_url

__metaclass__ = type


class PritunlException(Exception):
    pass


def pritunl_argument_spec():
    return dict(
        pritunl_url=dict(required=True, type="str"),
        pritunl_api_token=dict(required=True, type="str", no_log=False),
        pritunl_api_secret=dict(required=True, type="str", no_log=True),
        validate_certs=dict(required=False, type="bool", default=True),
    )


def get_pritunl_settings(module):
    """
    Helper function to set required Pritunl request params from module arguments.
    """
    return {
        "api_token": module.params.get("pritunl_api_token"),
        "api_secret": module.params.get("pritunl_api_secret"),
        "base_url": module.params.get("pritunl_url"),
        "validate_certs": module.params.get("validate_certs"),
    }


def _get_pritunl_organizations(api_token, api_secret, base_url, validate_certs=True):
    return pritunl_auth_request(
        base_url=base_url,
        api_token=api_token,
        api_secret=api_secret,
        method="GET",
        path="/organization",
        validate_certs=validate_certs,
    )


def _delete_pritunl_organization(
    api_token, api_secret, base_url, organization_id, validate_certs=True
):
    return pritunl_auth_request(
        base_url=base_url,
        api_token=api_token,
        api_secret=api_secret,
        method="DELETE",
        path="/organization/%s" % (organization_id),
        validate_certs=validate_certs,
    )


def _post_pritunl_organization(
    api_token, api_secret, base_url, organization_data, validate_certs=True
):
    return pritunl_auth_request(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        method="POST",
        path="/organization/%s",
        headers={"Content-Type": "application/json"},
        data=json.dumps(organization_data),
        validate_certs=validate_certs,
    )


def _get_pritunl_users(
    api_token, api_secret, base_url, organization_id, validate_certs=True
):
    return pritunl_auth_request(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        method="GET",
        path="/user/%s" % organization_id,
        validate_certs=validate_certs,
    )


def _delete_pritunl_user(
    api_token, api_secret, base_url, organization_id, user_id, validate_certs=True
):
    return pritunl_auth_request(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        method="DELETE",
        path="/user/%s/%s" % (organization_id, user_id),
        validate_certs=validate_certs,
    )


def _post_pritunl_user(
    api_token, api_secret, base_url, organization_id, user_data, validate_certs=True
):
    return pritunl_auth_request(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        method="POST",
        path="/user/%s" % organization_id,
        headers={"Content-Type": "application/json"},
        data=json.dumps(user_data),
        validate_certs=validate_certs,
    )


def _put_pritunl_user(
    api_token,
    api_secret,
    base_url,
    organization_id,
    user_id,
    user_data,
    validate_certs=True,
):
    return pritunl_auth_request(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        method="PUT",
        path="/user/%s/%s" % (organization_id, user_id),
        headers={"Content-Type": "application/json"},
        data=json.dumps(user_data),
        validate_certs=validate_certs,
    )


def list_pritunl_organizations(
    api_token, api_secret, base_url, validate_certs=True, filters=None
):
    orgs = []

    response = _get_pritunl_organizations(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        validate_certs=validate_certs,
    )

    if response.getcode() != 200:
        raise PritunlException("Could not retrieve organizations from Pritunl")
    else:
        for org in json.loads(response.read()):
            # No filtering
            if filters is None:
                orgs.append(org)
            else:
                if not any(
                    filter_val != org[filter_key]
                    for filter_key, filter_val in iteritems(filters)
                ):
                    orgs.append(org)

    return orgs


def list_pritunl_users(
    api_token, api_secret, base_url, organization_id, validate_certs=True, filters=None
):
    users = []

    response = _get_pritunl_users(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        validate_certs=validate_certs,
        organization_id=organization_id,
    )

    if response.getcode() != 200:
        raise PritunlException("Could not retrieve users from Pritunl")
    else:
        for user in json.loads(response.read()):
            # No filtering
            if filters is None:
                users.append(user)

            else:
                if not any(
                    filter_val != user[filter_key]
                    for filter_key, filter_val in iteritems(filters)
                ):
                    users.append(user)

    return users


def post_pritunl_organization(
    api_token,
    api_secret,
    base_url,
    organization_name,
    validate_certs=True,
):
    response = _post_pritunl_organization(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        organization_data={"name": organization_name},
        validate_certs=True,
    )

    if response.getcode() != 200:
        raise PritunlException(
            "Could not add organization %s to Pritunl" % (organization_name)
        )
    # The user PUT request returns the updated user object
    return json.loads(response.read())


def post_pritunl_user(
    api_token,
    api_secret,
    base_url,
    organization_id,
    user_data,
    user_id=None,
    validate_certs=True,
):
    # If user_id is provided will do PUT otherwise will do POST
    if user_id is None:
        response = _post_pritunl_user(
            api_token=api_token,
            api_secret=api_secret,
            base_url=base_url,
            organization_id=organization_id,
            user_data=user_data,
            validate_certs=True,
        )

        if response.getcode() != 200:
            raise PritunlException(
                "Could not remove user %s from organization %s from Pritunl"
                % (user_id, organization_id)
            )
        # user POST request returns an array of a single item,
        # so return this item instead of the list
        return json.loads(response.read())[0]
    else:
        response = _put_pritunl_user(
            api_token=api_token,
            api_secret=api_secret,
            base_url=base_url,
            organization_id=organization_id,
            user_data=user_data,
            user_id=user_id,
            validate_certs=True,
        )

        if response.getcode() != 200:
            raise PritunlException(
                "Could not update user %s from organization %s from Pritunl"
                % (user_id, organization_id)
            )
        # The user PUT request returns the updated user object
        return json.loads(response.read())


def delete_pritunl_organization(
    api_token, api_secret, base_url, organization_id, validate_certs=True
):
    response = _delete_pritunl_organization(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        organization_id=organization_id,
        validate_certs=True,
    )

    if response.getcode() != 200:
        raise PritunlException(
            "Could not remove organization %s from Pritunl" % (organization_id)
        )

    return json.loads(response.read())


def delete_pritunl_user(
    api_token, api_secret, base_url, organization_id, user_id, validate_certs=True
):
    response = _delete_pritunl_user(
        api_token=api_token,
        api_secret=api_secret,
        base_url=base_url,
        organization_id=organization_id,
        user_id=user_id,
        validate_certs=True,
    )

    if response.getcode() != 200:
        raise PritunlException(
            "Could not remove user %s from organization %s from Pritunl"
            % (user_id, organization_id)
        )

    return json.loads(response.read())


def pritunl_auth_request(
    api_token,
    api_secret,
    base_url,
    method,
    path,
    validate_certs=True,
    headers=None,
    data=None,
):
    """
    Send an API call to a Pritunl server.
    Taken from https://pritunl.com/api and adaped work with Ansible open_url
    """
    auth_timestamp = str(int(time.time()))
    auth_nonce = uuid.uuid4().hex

    auth_string = "&".join(
        [api_token, auth_timestamp, auth_nonce, method.upper(), path]
        + ([data] if data else [])
    )

    auth_signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"), auth_string.encode("utf-8"), hashlib.sha256
        ).digest()
    )

    auth_headers = {
        "Auth-Token": api_token,
        "Auth-Timestamp": auth_timestamp,
        "Auth-Nonce": auth_nonce,
        "Auth-Signature": auth_signature,
    }

    if headers:
        auth_headers.update(headers)

    try:
        uri = "%s%s" % (base_url, path)

        return open_url(
            uri,
            method=method.upper(),
            headers=auth_headers,
            data=data,
            validate_certs=validate_certs,
        )
    except Exception as e:
        raise PritunlException(e)
