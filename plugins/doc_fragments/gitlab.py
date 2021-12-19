# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
options:
  api_token:
    description:
      - GitLab token for logging in.
    type: str
  api_oauth_token:
    description:
      - GitLab OAuth token for logging in.
    type: str
  api_job_token:
    description:
      - GitLab CI job token for logging in.
    type: str
'''
