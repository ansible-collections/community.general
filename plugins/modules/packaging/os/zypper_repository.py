#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Matthias Vogelgesang <matthias.vogelgesang@gmail.com>
# (c) 2014, Justin Lecher <jlec@gentoo.org>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: zypper_repository
author: "Matthias Vogelgesang (@matze)"
short_description: Add and remove Zypper repositories
description:
    - Add or remove Zypper repositories on SUSE and openSUSE
options:
    name:
        description:
            - A name for the repository. Not required when adding repofiles.
        type: str
    repo:
        description:
            - URI of the repository or .repo file. Required when state=present.
        type: str
    state:
        description:
            - A source string state.
        choices: [ "absent", "present" ]
        default: "present"
        type: str
    description:
        description:
            - A description of the repository
        type: str
    disable_gpg_check:
        description:
            - Whether to disable GPG signature checking of
              all packages. Has an effect only if state is
              I(present).
            - Needs zypper version >= 1.6.2.
        type: bool
        default: no
    autorefresh:
        description:
            - Enable autorefresh of the repository.
        type: bool
        default: yes
        aliases: [ "refresh" ]
    priority:
        description:
            - Set priority of repository. Packages will always be installed
              from the repository with the smallest priority number.
            - Needs zypper version >= 1.12.25.
        type: int
    overwrite_multiple:
        description:
            - Overwrite multiple repository entries, if repositories with both name and
              URL already exist.
        type: bool
        default: no
    auto_import_keys:
        description:
            - Automatically import the gpg signing key of the new or changed repository.
            - Has an effect only if state is I(present). Has no effect on existing (unchanged) repositories or in combination with I(absent).
            - Implies runrefresh.
            - Only works with C(.repo) files if `name` is given explicitly.
        type: bool
        default: no
    runrefresh:
        description:
            - Refresh the package list of the given repository.
            - Can be used with repo=* to refresh all repositories.
        type: bool
        default: no
    enabled:
        description:
            - Set repository to enabled (or disabled).
        type: bool
        default: yes


requirements:
    - "zypper >= 1.0  # included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0"
    - python-xml
'''

EXAMPLES = '''
- name: Add NVIDIA repository for graphics drivers
  community.general.zypper_repository:
    name: nvidia-repo
    repo: 'ftp://download.nvidia.com/opensuse/12.2'
    state: present

- name: Remove NVIDIA repository
  community.general.zypper_repository:
    name: nvidia-repo
    repo: 'ftp://download.nvidia.com/opensuse/12.2'
    state: absent

- name: Add python development repository
  community.general.zypper_repository:
    repo: 'http://download.opensuse.org/repositories/devel:/languages:/python/SLE_11_SP3/devel:languages:python.repo'

- name: Refresh all repos
  community.general.zypper_repository:
    repo: '*'
    runrefresh: yes

- name: Add a repo and add its gpg key
  community.general.zypper_repository:
    repo: 'http://download.opensuse.org/repositories/systemsmanagement/openSUSE_Leap_42.1/'
    auto_import_keys: yes

- name: Force refresh of a repository
  community.general.zypper_repository:
    repo: 'http://my_internal_ci_repo/repo'
    name: my_ci_repo
    state: present
    runrefresh: yes
'''

import traceback

XML_IMP_ERR = None
try:
    from xml.dom.minidom import parseString as parseXML
    HAS_XML = True
except ImportError:
    XML_IMP_ERR = traceback.format_exc()
    HAS_XML = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.six.moves import configparser, StringIO
from io import open

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

REPO_OPTS = ['alias', 'name', 'priority', 'enabled', 'autorefresh', 'gpgcheck']


def _get_cmd(module, *args):
    """Combines the non-interactive zypper command with arguments/subcommands"""
    cmd = [module.get_bin_path('zypper', required=True), '--quiet', '--non-interactive']
    cmd.extend(args)

    return cmd


def _parse_repos(module):
    """parses the output of zypper --xmlout repos and return a parse repo dictionary"""
    cmd = _get_cmd(module, '--xmlout', 'repos')

    if not HAS_XML:
        module.fail_json(msg=missing_required_lib("python-xml"), exception=XML_IMP_ERR)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc == 0:
        repos = []
        dom = parseXML(stdout)
        repo_list = dom.getElementsByTagName('repo')
        for repo in repo_list:
            opts = {}
            for o in REPO_OPTS:
                opts[o] = repo.getAttribute(o)
            opts['url'] = repo.getElementsByTagName('url')[0].firstChild.data
            # A repo can be uniquely identified by an alias + url
            repos.append(opts)
        return repos
    # exit code 6 is ZYPPER_EXIT_NO_REPOS (no repositories defined)
    elif rc == 6:
        return []
    else:
        module.fail_json(msg='Failed to execute "%s"' % " ".join(cmd), rc=rc, stdout=stdout, stderr=stderr)


def _repo_changes(module, realrepo, repocmp):
    "Check whether the 2 given repos have different settings."
    for k in repocmp:
        if repocmp[k] and k not in realrepo:
            return True

    for k, v in realrepo.items():
        if k in repocmp and repocmp[k]:
            valold = str(repocmp[k] or "")
            valnew = v or ""
            if k == "url":
                if '$releasever' in valold or '$releasever' in valnew:
                    cmd = ['rpm', '-q', '--qf', '%{version}', '-f', '/etc/os-release']
                    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
                    valnew = valnew.replace('$releasever', stdout)
                    valold = valold.replace('$releasever', stdout)
                if '$basearch' in valold or '$basearch' in valnew:
                    cmd = ['rpm', '-q', '--qf', '%{arch}', '-f', '/etc/os-release']
                    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
                    valnew = valnew.replace('$basearch', stdout)
                    valold = valold.replace('$basearch', stdout)
                valold, valnew = valold.rstrip("/"), valnew.rstrip("/")
            if valold != valnew:
                return True
    return False


def repo_exists(module, repodata, overwrite_multiple):
    """Check whether the repository already exists.

        returns (exists, mod, old_repos)
            exists: whether a matching (name, URL) repo exists
            mod: whether there are changes compared to the existing repo
            old_repos: list of matching repos
    """
    existing_repos = _parse_repos(module)

    # look for repos that have matching alias or url to the one searched
    repos = []
    for kw in ['alias', 'url']:
        name = repodata[kw]
        for oldr in existing_repos:
            if repodata[kw] == oldr[kw] and oldr not in repos:
                repos.append(oldr)

    if len(repos) == 0:
        # Repo does not exist yet
        return (False, False, None)
    elif len(repos) == 1:
        # Found an existing repo, look for changes
        has_changes = _repo_changes(module, repos[0], repodata)
        return (True, has_changes, repos)
    elif len(repos) >= 2:
        if overwrite_multiple:
            # Found two repos and want to overwrite_multiple
            return (True, True, repos)
        else:
            errmsg = 'More than one repo matched "%s": "%s".' % (name, repos)
            errmsg += ' Use overwrite_multiple to allow more than one repo to be overwritten'
            module.fail_json(msg=errmsg)


def addmodify_repo(module, repodata, old_repos, zypper_version, warnings):
    "Adds the repo, removes old repos before, that would conflict."
    repo = repodata['url']
    cmd = _get_cmd(module, 'addrepo', '--check')
    if repodata['name']:
        cmd.extend(['--name', repodata['name']])

    # priority on addrepo available since 1.12.25
    # https://github.com/openSUSE/zypper/blob/b9b3cb6db76c47dc4c47e26f6a4d2d4a0d12b06d/package/zypper.changes#L327-L336
    if repodata['priority']:
        if zypper_version >= LooseVersion('1.12.25'):
            cmd.extend(['--priority', str(repodata['priority'])])
        else:
            warnings.append("Setting priority only available for zypper >= 1.12.25. Ignoring priority argument.")

    if repodata['enabled'] == '0':
        cmd.append('--disable')

    # gpgcheck available since 1.6.2
    # https://github.com/openSUSE/zypper/blob/b9b3cb6db76c47dc4c47e26f6a4d2d4a0d12b06d/package/zypper.changes#L2446-L2449
    # the default changed in the past, so don't assume a default here and show warning for old zypper versions
    if zypper_version >= LooseVersion('1.6.2'):
        if repodata['gpgcheck'] == '1':
            cmd.append('--gpgcheck')
        else:
            cmd.append('--no-gpgcheck')
    else:
        warnings.append("Enabling/disabling gpgcheck only available for zypper >= 1.6.2. Using zypper default value.")

    if repodata['autorefresh'] == '1':
        cmd.append('--refresh')

    cmd.append(repo)

    if not repo.endswith('.repo'):
        cmd.append(repodata['alias'])

    if old_repos is not None:
        for oldrepo in old_repos:
            remove_repo(module, oldrepo['url'])

    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    return rc, stdout, stderr


def remove_repo(module, repo):
    "Removes the repo."
    cmd = _get_cmd(module, 'removerepo', repo)

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    return rc, stdout, stderr


def get_zypper_version(module):
    rc, stdout, stderr = module.run_command([module.get_bin_path('zypper', required=True), '--version'])
    if rc != 0 or not stdout.startswith('zypper '):
        return LooseVersion('1.0')
    return LooseVersion(stdout.split()[1])


def runrefreshrepo(module, auto_import_keys=False, shortname=None):
    "Forces zypper to refresh repo metadata."
    if auto_import_keys:
        cmd = _get_cmd(module, '--gpg-auto-import-keys', 'refresh', '--force')
    else:
        cmd = _get_cmd(module, 'refresh', '--force')
    if shortname is not None:
        cmd.extend(['-r', shortname])

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    return rc, stdout, stderr


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=False),
            repo=dict(required=False),
            state=dict(choices=['present', 'absent'], default='present'),
            runrefresh=dict(required=False, default=False, type='bool'),
            description=dict(required=False),
            disable_gpg_check=dict(required=False, default=False, type='bool'),
            autorefresh=dict(required=False, default=True, type='bool', aliases=['refresh']),
            priority=dict(required=False, type='int'),
            enabled=dict(required=False, default=True, type='bool'),
            overwrite_multiple=dict(required=False, default=False, type='bool'),
            auto_import_keys=dict(required=False, default=False, type='bool'),
        ),
        supports_check_mode=False,
        required_one_of=[['state', 'runrefresh']],
    )

    repo = module.params['repo']
    alias = module.params['name']
    state = module.params['state']
    overwrite_multiple = module.params['overwrite_multiple']
    auto_import_keys = module.params['auto_import_keys']
    runrefresh = module.params['runrefresh']

    zypper_version = get_zypper_version(module)
    warnings = []  # collect warning messages for final output

    repodata = {
        'url': repo,
        'alias': alias,
        'name': module.params['description'],
        'priority': module.params['priority'],
    }
    # rewrite bools in the language that zypper lr -x provides for easier comparison
    if module.params['enabled']:
        repodata['enabled'] = '1'
    else:
        repodata['enabled'] = '0'
    if module.params['disable_gpg_check']:
        repodata['gpgcheck'] = '0'
    else:
        repodata['gpgcheck'] = '1'
    if module.params['autorefresh']:
        repodata['autorefresh'] = '1'
    else:
        repodata['autorefresh'] = '0'

    def exit_unchanged():
        module.exit_json(changed=False, repodata=repodata, state=state)

    # Check run-time module parameters
    if repo == '*' or alias == '*':
        if runrefresh:
            runrefreshrepo(module, auto_import_keys)
            module.exit_json(changed=False, runrefresh=True)
        else:
            module.fail_json(msg='repo=* can only be used with the runrefresh option.')

    if state == 'present' and not repo:
        module.fail_json(msg='Module option state=present requires repo')
    if state == 'absent' and not repo and not alias:
        module.fail_json(msg='Alias or repo parameter required when state=absent')

    if repo and repo.endswith('.repo'):
        if alias:
            module.fail_json(msg='Incompatible option: \'name\'. Do not use name when adding .repo files')
    else:
        if not alias and state == "present":
            module.fail_json(msg='Name required when adding non-repo files.')

    # Download / Open and parse .repo file to ensure idempotency
    if repo and repo.endswith('.repo'):
        if repo.startswith(('http://', 'https://')):
            response, info = fetch_url(module=module, url=repo, force=True)
            if not response or info['status'] != 200:
                module.fail_json(msg='Error downloading .repo file from provided URL')
            repofile_text = to_text(response.read(), errors='surrogate_or_strict')
        else:
            try:
                with open(repo, encoding='utf-8') as file:
                    repofile_text = file.read()
            except IOError:
                module.fail_json(msg='Error opening .repo file from provided path')

        repofile = configparser.ConfigParser()
        try:
            repofile.readfp(StringIO(repofile_text))
        except configparser.Error:
            module.fail_json(msg='Invalid format, .repo file could not be parsed')

        # No support for .repo file with zero or more than one repository
        if len(repofile.sections()) != 1:
            err = "Invalid format, .repo file contains %s repositories, expected 1" % len(repofile.sections())
            module.fail_json(msg=err)

        section = repofile.sections()[0]
        repofile_items = dict(repofile.items(section))
        # Only proceed if at least baseurl is available
        if 'baseurl' not in repofile_items:
            module.fail_json(msg='No baseurl found in .repo file')

        # Set alias (name) and url based on values from .repo file
        alias = section
        repodata['alias'] = section
        repodata['url'] = repofile_items['baseurl']

        # If gpgkey is part of the .repo file, auto import key
        if 'gpgkey' in repofile_items:
            auto_import_keys = True

        # Map additional values, if available
        if 'name' in repofile_items:
            repodata['name'] = repofile_items['name']
        if 'enabled' in repofile_items:
            repodata['enabled'] = repofile_items['enabled']
        if 'autorefresh' in repofile_items:
            repodata['autorefresh'] = repofile_items['autorefresh']
        if 'gpgcheck' in repofile_items:
            repodata['gpgcheck'] = repofile_items['gpgcheck']

    exists, mod, old_repos = repo_exists(module, repodata, overwrite_multiple)

    if alias:
        shortname = alias
    else:
        shortname = repo

    if state == 'present':
        if exists and not mod:
            if runrefresh:
                runrefreshrepo(module, auto_import_keys, shortname)
            exit_unchanged()
        rc, stdout, stderr = addmodify_repo(module, repodata, old_repos, zypper_version, warnings)
        if rc == 0 and (runrefresh or auto_import_keys):
            runrefreshrepo(module, auto_import_keys, shortname)
    elif state == 'absent':
        if not exists:
            exit_unchanged()
        rc, stdout, stderr = remove_repo(module, shortname)

    if rc == 0:
        module.exit_json(changed=True, repodata=repodata, state=state, warnings=warnings)
    else:
        module.fail_json(msg="Zypper failed with rc %s" % rc, rc=rc, stdout=stdout, stderr=stderr, repodata=repodata, state=state, warnings=warnings)


if __name__ == '__main__':
    main()
