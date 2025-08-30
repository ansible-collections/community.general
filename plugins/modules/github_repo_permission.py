#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, community.general contributors
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: github_repo_permission
short_description: Manage team or user permissions for a GitHub repository
version_added: 10.3.0
description:
  - Grants or revokes repository permissions for a team within an organization or for a specific user (collaborator).
  - Works with both GitHub.com and GitHub Enterprise Server installations.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  access_token:
    description:
      - GitHub access token with permission to manage repository access.
    type: str
    required: true
  repository:
    description:
      - Fully qualified repository name in the form C(owner/repo).
      - The owner must be an organization when managing team permissions.
    type: str
    required: true
    aliases: [ repo ]
  team_slug:
    description:
      - Team slug within the organization for which to set repository permissions.
      - Mutually exclusive with O(username).
    type: str
  username:
    description:
      - GitHub username (login) of the user to add as a collaborator on the repository.
      - Mutually exclusive with O(team_slug).
    type: str
    permission:
        description:
            - Permission to grant when O(state=present).
            - Supports built-ins C(pull), C(triage), C(push), C(maintain), C(admin) and custom repository roles (GitHub Enterprise).
            - Synonyms C(read) -> C(pull) and C(write) -> C(push) are accepted.
        type: str
  state:
    description:
      - Whether the permission should be present or absent.
    type: str
    default: present
    choices: [ present, absent ]
  api_url:
    description:
      - Base URL of the GitHub API. Use this when targeting GitHub Enterprise Server.
    type: str
    default: https://api.github.com

author:
  - "Daniel Marcocci (@danielino)"
"""

EXAMPLES = r"""
- name: Grant push permission to a team on a repository (organization repo)
  community.general.github_repo_permission:
    access_token: "{{ github_token }}"
    repository: myorg/myrepo
    team_slug: backend
    permission: push
    state: present

- name: Revoke a team's access to a repository
  community.general.github_repo_permission:
    access_token: "{{ github_token }}"
    repository: myorg/myrepo
    team_slug: contractors
    state: absent

- name: Ensure a user has triage permission on a repository
  community.general.github_repo_permission:
    access_token: "{{ github_token }}"
    repository: myorg/myrepo
    username: octocat
    permission: triage
    state: present

- name: Remove a user as a collaborator from a repository
  community.general.github_repo_permission:
    access_token: "{{ github_token }}"
    repository: myorg/myrepo
    username: former-user
    state: absent
"""

RETURN = r"""
result:
  description: Summary of the applied state, including subject type and current permission.
  returned: always
  type: dict
  sample:
    subject: team
    subject_identifier: backend
    repository: myorg/myrepo
    permission: push
    state: present
"""

import json
import time
import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


class GitHubResponse(object):
    def __init__(self, response, info):
        self.response = response
        self.info = info
        self._content = None

    @property
    def status(self):
        return int(self.info.get('status', 0))

    def json(self):
        if self._content is None:
            self._content = self.response.read()
        if not self._content:
            return {}
        return json.loads(self._content)

    def links(self):
        links = {}
        if 'link' in self.info:
            link_header = self.info['link']
            matches = re.findall(r'<([^>]+)>; rel=\"([^\"]+)\"', link_header)
            for url, rel in matches:
                links[rel] = url
        return links


class GitHubSession(object):
    def __init__(self, module, token, api_url):
        self.module = module
        self.token = token
        self.api_url = api_url.rstrip('/')

    def request(self, method, url, data=None, headers=None):
        base_headers = {
            'Authorization': 'token %s' % self.token,
            'Content-Type': 'application/json',
            # Use the recommended media type that supports newer fields and features
            'Accept': 'application/vnd.github+json',
            # Pin to a stable API version when available
            'X-GitHub-Api-Version': '2022-11-28',
        }
        if headers:
            base_headers.update(headers)
        response, info = fetch_url(self.module, url, method=method, data=data, headers=base_headers)
        return GitHubResponse(response, info)

    def request_json(self, method, url, body=None):
        data = json.dumps(body) if body is not None else None
        r = self.request(method, url, data=data)
        # Treat 2xx and 3xx as success
        if not (200 <= r.status < 400):
            self.module.fail_json(msg=("GitHub API %s %s failed: %s" % (method, url, r.info.get('msg'))))
        return r

    def paginated_get(self, url):
        results = []
        next_url = url
        while next_url:
            r = self.request_json('GET', next_url)
            results.extend(r.json())
            next_url = r.links().get('next')
        return results

    def get_custom_repo_roles(self, org):
        """Return list of custom repository roles for org or [] if not available."""
        url = '%s/orgs/%s/custom-repository-roles' % (self.api_url, org)
        r = self.request('GET', url)
        if r.status in (403, 404):
            return []
        if not (200 <= r.status < 400):
            return []
        data = r.json()
        # GitHub returns {roles: [...]} or a list; handle both
        if isinstance(data, dict) and 'roles' in data:
            return data['roles'] or []
        if isinstance(data, list):
            return data
        return []


def parse_repo_full_name(full_name):
    if not full_name or '/' not in full_name:
        return None, None
    owner, repo = full_name.split('/', 1)
    return owner, repo


BUILTIN_PERMISSIONS = {"pull", "triage", "push", "maintain", "admin"}


def normalize_desired_permission(p):
    if p is None:
        return None
    low = p.lower()
    if low == 'read':
        return 'pull'
    if low == 'write':
        return 'push'
    if low in BUILTIN_PERMISSIONS:
        return low
    # Custom role: keep original for API calls
    return p


def resolve_permission_for_org(session, org, desired):
    """Return a tuple (resolved, is_builtin) for the desired permission within org.
    Resolved is the exact string to send to the API. Accepts custom roles.
    """
    if desired is None:
        return None, True
    norm = normalize_desired_permission(desired)
    if isinstance(norm, str) and norm.lower() in BUILTIN_PERMISSIONS:
        return norm.lower(), True
    # Attempt to match custom role by case-insensitive name
    roles = session.get_custom_repo_roles(org)
    match = None
    desired_lower = str(desired).lower()
    for r in roles:
        name = r.get('name') or r.get('display_name') or ''
        if name.lower() == desired_lower:
            match = name
            break
    if match:
        return match, False
    # If no roles are returned (endpoint not supported), fall back to sending the original string
    if not roles:
        return desired, False
    # Otherwise fail helpfully listing available custom roles
    available = ', '.join([str(r.get('name') or r.get('display_name')) for r in roles if (r.get('name') or r.get('display_name'))])
    session.module.fail_json(msg=(
        "Permission '%s' not found among builtin permissions or custom repository roles for org '%s'. "
        "Available custom roles: %s" % (desired, org, available)
    ))


def get_team_repo_permission(session, org, team_slug, owner, repo):
    """Return (role_name, builtin_permission) for team's access to repo.
    Tries team-repo endpoint (role_name aware) then falls back to repo teams list.
    """
    # Prefer role_name-aware endpoint
    r = session.request('GET', '%s/orgs/%s/teams/%s/repos/%s/%s' % (session.api_url, org, team_slug, owner, repo))
    if 200 <= r.status < 400:
        data = r.json() or {}
        role_name = data.get('role_name')
        perm = data.get('permission')
        if not role_name and not perm and isinstance(data.get('permissions'), dict):
            perms = data['permissions']
            if perms.get('admin'):
                perm = 'admin'
            elif perms.get('maintain'):
                perm = 'maintain'
            elif perms.get('push'):
                perm = 'push'
            elif perms.get('triage'):
                perm = 'triage'
            elif perms.get('pull'):
                perm = 'pull'
        return role_name, perm
    # Fallback to repo teams list
    teams = session.paginated_get('%s/repos/%s/%s/teams' % (session.api_url, owner, repo))
    for t in teams:
        slug = (t.get('slug') or '').lower()
        if slug == (team_slug or '').lower():
            return None, t.get('permission')
    return None, None


def team_has_access(session, owner, repo, team_slug):
    """Return True if team appears in repo team list, regardless of permission visibility."""
    teams = session.paginated_get('%s/repos/%s/%s/teams' % (session.api_url, owner, repo))
    for t in teams:
        slug = (t.get('slug') or '').lower()
        if slug == (team_slug or '').lower():
            return True
    return False


def ensure_team_permission(module, session, owner, repo, team_slug, desired_permission, state):
    # Get current teams on repo and find team's current permission
    role_name, current_builtin = get_team_repo_permission(session, owner, team_slug, owner, repo)
    current_display = role_name or current_builtin

    changed = False
    if state == 'present':
        # Compare: if desired is builtin, use lowercase compare; else, compare to role_name (case-insensitive)
        resolved_perm, is_builtin = resolve_permission_for_org(session, owner, desired_permission)
        equal = False
        if is_builtin:
            equal = (current_builtin or '').lower() == (resolved_perm or '').lower()
        else:
            # custom role: if role_name matches, equal; otherwise, when API doesn't expose role_name,
            # consider equal if the team already has any access (idempotency for custom roles)
            if (role_name or '').lower() == (resolved_perm or '').lower():
                equal = True
            else:
                equal = team_has_access(session, owner, repo, team_slug)
        if not equal:
            if not module.check_mode:
                resp = session.request_json(
                    'PUT',
                    '%s/orgs/%s/teams/%s/repos/%s/%s' % (session.api_url, owner, team_slug, owner, repo),
                    body={'permission': resolved_perm}
                )
                # Re-read to verify change applied (with small retries for propagation)
                attempts = 3
                verified = False
                last_role_name = None
                last_builtin = None
                for i in range(attempts):
                    new_role_name, new_builtin = get_team_repo_permission(session, owner, team_slug, owner, repo)
                    last_role_name, last_builtin = new_role_name, new_builtin
                    if resolved_perm.lower() in BUILTIN_PERMISSIONS:
                        if (new_builtin or '').lower() == resolved_perm.lower():
                            verified = True
                            break
                    else:
                        # Custom role: accept if any permission is present or role_name matches
                        if (new_role_name and new_role_name.lower() == resolved_perm.lower()) or bool(new_builtin) or team_has_access(session, owner, repo, team_slug):
                            verified = True
                            break
                    time.sleep(0.5)
                if not verified:
                    if resolved_perm.lower() in BUILTIN_PERMISSIONS:
                        module.fail_json(msg=(
                            "Applied team permission not reflected on server. Requested '%s', got role_name='%s', permission='%s'."
                            % (resolved_perm, last_role_name, last_builtin)
                        ))
                    else:
                        # Custom role not visible via API; warn and continue.
                        module.warn(
                            "Applied custom team role but could not verify via API (role_name/permission not reported). Proceeding as changed."
                        )
            changed = True
        result_perm = resolved_perm
    else:  # absent
        if current_display is not None:
            if not module.check_mode:
                # Remove team access
                r = session.request('DELETE', '%s/orgs/%s/teams/%s/repos/%s/%s' % (session.api_url, owner, team_slug, owner, repo))
                if not (200 <= r.status < 400 or r.status == 204 or r.status == 404):
                    module.fail_json(msg=(
                        "GitHub API DELETE failed for team '%s' on %s/%s: %s" % (team_slug, owner, repo, r.info.get('msg'))
                    ))
            changed = True
        result_perm = None

    return changed, {
        'subject': 'team',
        'subject_identifier': team_slug,
        'repository': owner + '/' + repo,
        'permission': result_perm,
        'state': state,
    }


def get_user_permission(session, owner, repo, username):
    r = session.request('GET', '%s/repos/%s/%s/collaborators/%s/permission' % (session.api_url, owner, repo, username))
    if r.status == 404:
        return 'none'
    if not (200 <= r.status < 400):
        # Fallback to treating as none on 403 when lacking visibility
        return 'none'
    data = r.json()
    # Prefer explicit role_name for custom roles if available
    role_name = data.get('role_name')
    if role_name:
        return role_name
    perm = data.get('permission', 'none')
    # Normalize to module's choices
    if perm == 'read':
        return 'pull'
    if perm == 'write':
        return 'push'
    return perm


def ensure_user_permission(module, session, owner, repo, username, desired_permission, state):
    current = get_user_permission(session, owner, repo, username)
    changed = False

    if state == 'present':
        resolved_perm, _ = resolve_permission_for_org(session, owner, desired_permission)
        # Compare with case-insensitive match (role_name or builtin value)
        if (current or '').lower() != (resolved_perm or '').lower():
            if not module.check_mode:
                r = session.request_json(
                    'PUT',
                    '%s/repos/%s/%s/collaborators/%s' % (session.api_url, owner, repo, username),
                    body={'permission': resolved_perm}
                )
                # Accept 201 Created, 204 No Content, 202 Accepted
                if r.status not in (200, 201, 202, 204):
                    module.fail_json(msg=(
                        "Failed to add/update collaborator '%s' on %s/%s: %s" % (username, owner, repo, r.info.get('msg'))
                    ))
                # Re-read to verify change applied
                new_current = get_user_permission(session, owner, repo, username)
                if (new_current or '').lower() != (resolved_perm or '').lower():
                    module.fail_json(msg=(
                        "Applied collaborator permission not reflected on server. Requested '%s', got '%s'."
                        % (resolved_perm, new_current)
                    ))
            changed = True
        result_perm = resolved_perm
    else:  # absent
        if current != 'none':
            if not module.check_mode:
                r = session.request('DELETE', '%s/repos/%s/%s/collaborators/%s' % (session.api_url, owner, repo, username))
                if r.status not in (204, 404):
                    module.fail_json(msg=(
                        "Failed to remove collaborator '%s' from %s/%s: %s" % (username, owner, repo, r.info.get('msg'))
                    ))
            changed = True
        result_perm = None

    return changed, {
        'subject': 'user',
        'subject_identifier': username,
        'repository': owner + '/' + repo,
        'permission': result_perm,
        'state': state,
    }


def main():
    module_args = dict(
        access_token=dict(type='str', required=True, no_log=True),
        repository=dict(type='str', required=True, aliases=['repo']),
        team_slug=dict(type='str'),
        username=dict(type='str'),
        permission=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        api_url=dict(type='str', default='https://api.github.com'),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[('team_slug', 'username')],
        required_one_of=[('team_slug', 'username')],
        required_if=[('state', 'present', ['permission'])],
    )

    access_token = module.params['access_token']
    repository = module.params['repository']
    team_slug = module.params['team_slug']
    username = module.params['username']
    permission = normalize_desired_permission(module.params.get('permission'))
    state = module.params['state']
    api_url = module.params['api_url']

    owner, repo = parse_repo_full_name(repository)
    if not owner or not repo:
        module.fail_json(msg="'repository' must be in the form 'owner/repo'")

    session = GitHubSession(module, access_token, api_url)

    # Heuristic warning: api_url '/api/v4' is typical of GitLab, not GitHub Enterprise
    if '/api/v4' in (api_url or ''):
        module.warn("The configured api_url ends with '/api/v4', which looks like a GitLab endpoint. For GitHub Enterprise Server, api_url usually ends with '/api/v3'.")

    try:
        if team_slug:
            changed, data = ensure_team_permission(module, session, owner, repo, team_slug, permission, state)
        else:
            changed, data = ensure_user_permission(module, session, owner, repo, username, permission, state)
    except Exception as e:
        module.fail_json(msg="Unexpected error: %s" % e)

    module.exit_json(changed=changed, result=data)


if __name__ == '__main__':
    main()
