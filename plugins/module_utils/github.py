# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright: (c) 2020, Andrea Tartaglia <andrea@braingap.uk>
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import abc
import traceback
import re

GITHUB_IMP_ERR = None
try:
    from github import Github
    from github import GithubException, BadCredentialsException, UnknownObjectException

    HAS_GITHUB = True
except ImportError:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB = False

from ansible.module_utils import six
from ansible.module_utils._text import to_native


class GithubError(Exception):
    pass


class GitHubBadCredentialsError(Exception):
    pass


class GithubUnknownObjectError(Exception):
    pass


def github_common_argument_spec():
    return dict(
        user=dict(type="str", default=None, aliases=["username"]),
        password=dict(type="str", default=None, no_log=True),
        token=dict(type="str", default=None, no_log=True),
        server=dict(
            type="str", default="https://api.github.com", aliases=["github_url"]
        ),
    )


@six.add_metaclass(abc.ABCMeta)
class GitHubBase(object):
    def __init__(
        self,
        username=None,
        password=None,
        token=None,
        otp=None,
        server="https://api.github.com",
        repo=None,
        organization=None,
    ):
        self.username = username
        self.password = password
        self.token = token
        self.otp = otp
        self.server = re.sub("/$", "", server)
        self.repo_name = repo
        self.organization = organization
        self.github_conn = None
        if self.organization:
            self.repo_full_name = "/".join([self.organization, self.repo_name])
        else:
            self.repo_full_name = "/".join([self.username, self.repo_name])

    def auth(self):
        try:
            if self.username and self.password:
                self.github_conn = Github(
                    self.username, self.password, base_url=self.server
                )
            else:
                self.github_conn = Github(self.token, base_url=self.server)
        except GithubException as err:
            raise GithubError(
                "Could not connect to GitHub at {0}: {1}".format(
                    self.server, to_native(err)
                )
            )

    @property
    def repository(self):
        try:
            return self.github_conn.get_repo(self.repo_full_name)
        except BadCredentialsException as err:
            raise GitHubBadCredentialsError(
                "Unable to authenticate to GiHub at {0}: {1}".format(
                    self.server, to_native(err)
                )
            )
        except UnknownObjectException as err:
            raise GithubUnknownObjectError(
                "Unable to find repository {0} in GitHub at {1}: {2}".format(
                    self.repo_full_name, self.server, to_native(err)
                )
            )
        except GithubException as err:
            raise GithubError(err)
