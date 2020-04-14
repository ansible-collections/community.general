# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Andrea Tartaglia <andrea@braingap.uk>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    # Shared GitHub documentation fragment

    DOCUMENTATION = r"""
requirements:
  - "PyGithub >= 1.3.5"
options:
  user:
    description:
      - The username to authenticate with. Should not be set when using personal access token
    type: str
    aliases: [username]
  password:
    description:
      - The password to authenticate with. Alternatively, a personal access token can be used instead of I(username) and I(password) combination.
    type: str
  token:
    description:
      - The OAuth2 token or personal access token to authenticate with. Mutually exclusive with I(password).
    type: str
  server:
    description:
      - Base URL of the GitHub API
    default: https://api.github.com
    aliases: [github_url]
    type: str
    """
