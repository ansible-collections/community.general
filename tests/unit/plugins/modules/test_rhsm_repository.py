# -*- coding: utf-8 -*-
# Author: Pino Toscano (ptoscano@redhat.com)
# Largely adapted from test_rhsm_repository by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Pino Toscano (ptoscano@redhat.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import fnmatch
import itertools
import json

from ansible.module_utils import basic
from ansible_collections.community.general.plugins.modules import rhsm_repository

import pytest

TESTED_MODULE = rhsm_repository.__name__


@pytest.fixture
def patch_rhsm_repository(mocker):
    """
    Function used for mocking some parts of rhsm_repository module
    """
    mocker.patch('ansible_collections.community.general.plugins.modules.rhsm_repository.AnsibleModule.get_bin_path',
                 return_value='/testbin/subscription-manager')
    mocker.patch('ansible_collections.community.general.plugins.modules.rhsm_repository.os.getuid',
                 return_value=0)


class Repos(object):
    """
    Helper class to represent a list of repositories

    Each repository is an object with few properties.
    """

    _SUBMAN_OUT_HEADER = """+----------------------------------------------------------+
    Available Repositories in /etc/yum.repos.d/redhat.repo
+----------------------------------------------------------+
"""
    _SUBMAN_OUT_ENTRY = """Repo ID:   %s
Repo Name: %s
Repo URL:  %s
Enabled:   %s

"""

    def __init__(self, repos):
        self.repos = repos

    def to_subman_list_output(self):
        """
        Return a string mimicking the output of `subscription-manager repos --list`
        """
        out = self._SUBMAN_OUT_HEADER
        for repo in self.repos:
            out += self._SUBMAN_OUT_ENTRY % (
                repo["id"],
                repo["name"],
                repo["url"],
                "1" if repo["enabled"] else "0",
            )

        return out

    def copy(self):
        """
        Clone the object; used to do changes (enable(), disable()) without
        affecting the original object.
        """
        return copy.deepcopy(self)

    def _set_status(self, repo_id, status):
        for repo in self.repos:
            if fnmatch.fnmatch(repo['id'], repo_id):
                repo['enabled'] = status

    def enable(self, repo_ids):
        """
        Enable the specified IDs.

        'repo_ids' can be either a string or a list of strings representing
        an ID (wildcard included).

        Returns the same object, so calls to this can be chained.
        """
        if not isinstance(repo_ids, list):
            repo_ids = [repo_ids]
        for repo_id in repo_ids:
            self._set_status(repo_id, True)
        return self

    def disable(self, repo_ids):
        """
        Disable the specified IDs.

        'repo_ids' can be either a string or a list of strings representing
        an ID (wildcard included).

        Returns the same object, so calls to this can be chained.
        """
        if not isinstance(repo_ids, list):
            repo_ids = [repo_ids]
        for repo_id in repo_ids:
            self._set_status(repo_id, False)
        return self

    def _filter_by_status(self, filter, status):
        return [
            repo['id']
            for repo in self.repos
            if repo['enabled'] == status and fnmatch.fnmatch(repo['id'], filter)
        ]

    def ids_enabled(self, filter='*'):
        """
        Get a list with the enabled repositories.

        'filter' is a wildcard expression.
        """
        return self._filter_by_status(filter, True)

    def ids_disabled(self, filter='*'):
        """
        Get a list with the disabled repositories.

        'filter' is a wildcard expression.
        """
        return self._filter_by_status(filter, False)

    def to_list(self):
        """
        Get the list of repositories.
        """
        return self.repos


def flatten(iter_of_iters):
    return list(itertools.chain.from_iterable(iter_of_iters))


# List with test repositories, directly from the Candlepin test data.
REPOS_LIST = [
    {
        "id": "never-enabled-content-801",
        "name": "never-enabled-content-801",
        "url": "https://candlepin.local/foo/path/never_enabled/801-100",
        "enabled": False,
    },
    {
        "id": "never-enabled-content-100000000000060",
        "name": "never-enabled-content-100000000000060",
        "url": "https://candlepin.local/foo/path/never_enabled/100000000000060-100",
        "enabled": False,
    },
    {
        "id": "awesomeos-x86_64-1000000000000023",
        "name": "awesomeos-x86_64-1000000000000023",
        "url": "https://candlepin.local/path/to/awesomeos/x86_64/1000000000000023-11124",
        "enabled": False,
    },
    {
        "id": "awesomeos-ppc64-100000000000011",
        "name": "awesomeos-ppc64-100000000000011",
        "url": "https://candlepin.local/path/to/awesomeos/ppc64/100000000000011-11126",
        "enabled": False,
    },
    {
        "id": "awesomeos-99000",
        "name": "awesomeos-99000",
        "url": "https://candlepin.local/path/to/generic/awesomeos/99000-11113",
        "enabled": True,
    },
    {
        "id": "content-label-27060",
        "name": "content-27060",
        "url": "https://candlepin.local/foo/path/common/27060-1111",
        "enabled": True,
    },
    {
        "id": "content-label-no-gpg-32060",
        "name": "content-nogpg-32060",
        "url": "https://candlepin.local/foo/path/no_gpg/32060-234",
        "enabled": False,
    },
    {
        "id": "awesomeos-1000000000000023",
        "name": "awesomeos-1000000000000023",
        "url": "https://candlepin.local/path/to/generic/awesomeos/1000000000000023-11113",
        "enabled": False,
    },
    {
        "id": "awesomeos-x86-100000000000020",
        "name": "awesomeos-x86-100000000000020",
        "url": "https://candlepin.local/path/to/awesomeos/x86/100000000000020-11120",
        "enabled": False,
    },
    {
        "id": "awesomeos-x86_64-99000",
        "name": "awesomeos-x86_64-99000",
        "url": "https://candlepin.local/path/to/awesomeos/x86_64/99000-11124",
        "enabled": True,
    },
    {
        "id": "awesomeos-s390x-99000",
        "name": "awesomeos-s390x-99000",
        "url": "https://candlepin.local/path/to/awesomeos/s390x/99000-11121",
        "enabled": False,
    },
    {
        "id": "awesomeos-modifier-37080",
        "name": "awesomeos-modifier-37080",
        "url": "https://candlepin.local/example.com/awesomeos-modifier/37080-1112",
        "enabled": False,
    },
    {
        "id": "awesomeos-i686-99000",
        "name": "awesomeos-i686-99000",
        "url": "https://candlepin.local/path/to/awesomeos/i686/99000-11123",
        "enabled": False,
    },
    {
        "id": "fake-content-38072",
        "name": "fake-content-38072",
        "url": "https://candlepin.local/path/to/fake-content/38072-3902",
        "enabled": True,
    },
]


# A static object with the list of repositories, used as reference to query
# the repositories, and create (by copy()) new Repos objects.
REPOS = Repos(REPOS_LIST)

# The mock string for the output of `subscription-manager repos --list`.
REPOS_LIST_OUTPUT = REPOS.to_subman_list_output()

# MUST match what's in the Rhsm class in the module.
SUBMAN_KWARGS = {
    'environ_update': dict(LANG='C', LC_ALL='C', LC_MESSAGES='C'),
    'expand_user_and_vars': False,
    'use_unsafe_shell': False,
}


TEST_CASES = [
    # enable a disabled repository
    [
        {
            'name': 'awesomeos-1000000000000023',
        },
        {
            'id': 'test_enable_single',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-1000000000000023',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().enable('awesomeos-1000000000000023'),
        }
    ],
    # enable an already enabled repository
    [
        {
            'name': 'fake-content-38072',
        },
        {
            'id': 'test_enable_already_enabled',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
            ],
            'changed': False,
            'repositories': REPOS.copy(),
        }
    ],
    # enable two disabled repositories
    [
        {
            'name': ['awesomeos-1000000000000023', 'content-label-no-gpg-32060'],
        },
        {
            'id': 'test_enable_multiple',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-1000000000000023',
                        '--enable',
                        'content-label-no-gpg-32060',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().enable('awesomeos-1000000000000023').enable('content-label-no-gpg-32060'),
        }
    ],
    # enable two repositories, one disabled and one already enabled
    [
        {
            'name': ['awesomeos-1000000000000023', 'fake-content-38072'],
        },
        {
            'id': 'test_enable_multiple_mixed',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-1000000000000023',
                        '--enable',
                        'fake-content-38072',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().enable('awesomeos-1000000000000023'),
        }
    ],
    # purge everything but never-enabled-content-801 (disabled)
    [
        {
            'name': 'never-enabled-content-801',
            'purge': True,
        },
        {
            'id': 'test_purge_everything_but_one_disabled',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'never-enabled-content-801',
                    ] + flatten([['--disable', i] for i in REPOS.ids_enabled() if i != 'never-enabled-content-801']),
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*').enable('never-enabled-content-801'),
        }
    ],
    # purge everything but awesomeos-99000 (already enabled)
    [
        {
            'name': 'awesomeos-99000',
            'purge': True,
        },
        {
            'id': 'test_purge_everything_but_one_enabled',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-99000',
                        '--disable',
                        'content-label-27060',
                        '--disable',
                        'awesomeos-x86_64-99000',
                        '--disable',
                        'fake-content-38072',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*').enable('awesomeos-99000'),
        }
    ],
    # enable everything, then purge everything but content-label-27060
    [
        {
            'name': 'content-label-27060',
            'purge': True,
        },
        {
            'id': 'test_enable_everything_purge_everything_but_one_enabled',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS.copy().enable('*').to_subman_list_output(), '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'content-label-27060',
                        '--disable',
                        'never-enabled-content-801',
                        '--disable',
                        'never-enabled-content-100000000000060',
                        '--disable',
                        'awesomeos-x86_64-1000000000000023',
                        '--disable',
                        'awesomeos-ppc64-100000000000011',
                        '--disable',
                        'awesomeos-99000',
                        '--disable',
                        'content-label-no-gpg-32060',
                        '--disable',
                        'awesomeos-1000000000000023',
                        '--disable',
                        'awesomeos-x86-100000000000020',
                        '--disable',
                        'awesomeos-x86_64-99000',
                        '--disable',
                        'awesomeos-s390x-99000',
                        '--disable',
                        'awesomeos-modifier-37080',
                        '--disable',
                        'awesomeos-i686-99000',
                        '--disable',
                        'fake-content-38072',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*').enable('content-label-27060'),
        }
    ],
    # enable all awesomeos-*
    [
        {
            'name': 'awesomeos-*',
        },
        {
            'id': 'test_enable_all_awesomeos_star',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-x86_64-1000000000000023',
                        '--enable',
                        'awesomeos-ppc64-100000000000011',
                        '--enable',
                        'awesomeos-99000',
                        '--enable',
                        'awesomeos-1000000000000023',
                        '--enable',
                        'awesomeos-x86-100000000000020',
                        '--enable',
                        'awesomeos-x86_64-99000',
                        '--enable',
                        'awesomeos-s390x-99000',
                        '--enable',
                        'awesomeos-modifier-37080',
                        '--enable',
                        'awesomeos-i686-99000',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().enable('awesomeos-*'),
        }
    ],
    # purge everything but awesomeos-*
    [
        {
            'name': REPOS.ids_enabled('awesomeos-*'),
            'purge': True,
        },
        {
            'id': 'test_purge_everything_but_awesomeos_list',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--enable',
                        'awesomeos-99000',
                        '--enable',
                        'awesomeos-x86_64-99000',
                        '--disable',
                        'content-label-27060',
                        '--disable',
                        'fake-content-38072',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*').enable(REPOS.ids_enabled('awesomeos-*')),
        }
    ],
    # enable a repository that does not exist
    [
        {
            'name': 'repo-that-does-not-exist',
        },
        {
            'id': 'test_enable_nonexisting',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
            ],
            'failed': True,
            'msg': 'repo-that-does-not-exist is not a valid repository ID',
        }
    ],
    # disable an enabled repository
    [
        {
            'name': 'awesomeos-99000',
            'state': 'disabled',
        },
        {
            'id': 'test_disable_single',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--disable',
                        'awesomeos-99000',
                    ],
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('awesomeos-99000'),
        }
    ],
    # disable an already disabled repository
    [
        {
            'name': 'never-enabled-content-801',
            'state': 'disabled',
        },
        {
            'id': 'test_disable_already_disabled',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
            ],
            'changed': False,
            'repositories': REPOS.copy(),
        }
    ],
    # disable an already disabled repository, and purge
    [
        {
            'name': 'never-enabled-content-801',
            'state': 'disabled',
            'purge': True,
        },
        {
            'id': 'test_disable_already_disabled_and_purge',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                    ] + flatten([['--disable', i] for i in REPOS.ids_enabled()]),
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*'),
        }
    ],
    # disable an enabled repository, and purge
    [
        {
            'name': 'awesomeos-99000',
            'state': 'disabled',
            'purge': True,
        },
        {
            'id': 'test_disable_single_and_purge',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                    ] + flatten([['--disable', i] for i in REPOS.ids_enabled()]),
                    SUBMAN_KWARGS,
                    (0, '', '')
                ),
            ],
            'changed': True,
            'repositories': REPOS.copy().disable('*'),
        }
    ],
    # disable a repository that does not exist
    [
        {
            'name': 'repo-that-does-not-exist',
            'state': 'disabled',
        },
        {
            'id': 'test_disable_nonexisting',
            'run_command.calls': [
                (
                    [
                        '/testbin/subscription-manager',
                        'repos',
                        '--list',
                    ],
                    SUBMAN_KWARGS,
                    (0, REPOS_LIST_OUTPUT, '')
                ),
            ],
            'failed': True,
            'msg': 'repo-that-does-not-exist is not a valid repository ID',
        }
    ],
]


TEST_CASES_IDS = [item[1]['id'] for item in TEST_CASES]


@pytest.mark.parametrize('patch_ansible_module, testcase', TEST_CASES, ids=TEST_CASES_IDS, indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_rhsm_repository(mocker, capfd, patch_rhsm_repository, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    # Mock function used for running commands first
    call_results = [item[2] for item in testcase['run_command.calls']]
    mock_run_command = mocker.patch.object(
        basic.AnsibleModule,
        'run_command',
        side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        rhsm_repository.main()

    out, err = capfd.readouterr()
    results = json.loads(out)

    if 'failed' in testcase:
        assert results['failed'] == testcase['failed']
        assert results['msg'] == testcase['msg']
    else:
        assert 'changed' in results
        assert results['changed'] == testcase['changed']
        assert results['repositories'] == testcase['repositories'].to_list()

    assert basic.AnsibleModule.run_command.call_count == len(testcase['run_command.calls'])
    # FIXME ideally we need also to compare the actual calls with the expected
    # ones; the problem is that the module uses a dict to collect the repositories
    # to enable and disable, so the order of the --enable/--disable parameters to
    # `subscription-manager repos` is not stable
