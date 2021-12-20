# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
requirements:
  - requests (Python library U(https://pypi.org/project/requests/))

options:
  api_token:
    description:
      - GitLab access token with API permissions.
    type: str
  api_oauth_token:
    description:
      - GitLab OAuth token for logging in.
    type: str
    version_added: 4.2.0
  api_job_token:
    description:
      - GitLab CI job token for logging in.
    type: str
    version_added: 4.2.0
'''
