# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.gitlab_user import GitLabUser, ssh_key_value


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         python_version_match_requirement,
                         resp_find_user, resp_get_user, resp_get_user_keys,
                         resp_create_user_keys, resp_create_user, resp_delete_user,
                         resp_get_member, resp_get_group, resp_add_member,
                         resp_update_member, resp_get_member)

    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import User
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object
    resp_find_user = _dummy
    resp_get_user = _dummy
    resp_get_user_keys = _dummy
    resp_create_user_keys = _dummy
    resp_create_user = _dummy
    resp_delete_user = _dummy
    resp_get_member = _dummy
    resp_get_group = _dummy
    resp_add_member = _dummy
    resp_update_member = _dummy
    resp_get_member = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabUser(GitlabModuleTestCase):
    def setUp(self):
        super(TestGitlabUser, self).setUp()

        self.moduleUtil = GitLabUser(module=self.mock_module, gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_find_user)
    def test_exist_user(self):
        rvalue = self.moduleUtil.exists_user("john_smith")

        self.assertEqual(rvalue, True)

        rvalue = self.moduleUtil.exists_user("paul_smith")

        self.assertEqual(rvalue, False)

    @with_httmock(resp_find_user)
    def test_find_user(self):
        user = self.moduleUtil.find_user("john_smith")

        self.assertEqual(type(user), User)
        self.assertEqual(user.name, "John Smith")
        self.assertEqual(user.id, 1)

    @with_httmock(resp_create_user)
    def test_create_user(self):
        user = self.moduleUtil.create_user({'email': 'john@example.com', 'password': 's3cur3s3cr3T',
                                           'username': 'john_smith', 'name': 'John Smith'})
        self.assertEqual(type(user), User)
        self.assertEqual(user.name, "John Smith")
        self.assertEqual(user.id, 1)

    @with_httmock(resp_get_user)
    def test_update_user(self):
        user = self.gitlab_instance.users.get(1)

        changed, newUser = self.moduleUtil.update_user(
            user,
            {'name': {'value': "Jack Smith"}, "is_admin": {'value': "true", 'setter': 'admin'}}, {}
        )

        self.assertEqual(changed, True)
        self.assertEqual(newUser.name, "Jack Smith")
        self.assertEqual(newUser.admin, "true")

        changed, newUser = self.moduleUtil.update_user(user, {'name': {'value': "Jack Smith"}}, {})

        self.assertEqual(changed, False)

        changed, newUser = self.moduleUtil.update_user(
            user,
            {}, {
                'skip_reconfirmation': {'value': True},
                'password': {'value': 'super_secret-super_secret'},
            }
        )

        # note: uncheckable parameters dont set changed state
        self.assertEqual(changed, False)
        self.assertEqual(newUser.skip_reconfirmation, True)
        self.assertEqual(newUser.password, 'super_secret-super_secret')

    @with_httmock(resp_find_user)
    @with_httmock(resp_delete_user)
    def test_delete_user(self):
        self.moduleUtil.exists_user("john_smith")
        rvalue = self.moduleUtil.delete_user()

        self.assertEqual(rvalue, None)

    @with_httmock(resp_get_user)
    @with_httmock(resp_get_user_keys)
    def test_sshkey_exist(self):
        user = self.gitlab_instance.users.get(1)

        exist = self.moduleUtil.ssh_key_exists(
            user,
            "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAiPWx6WM4lhHNedGfBpPJNPpZ7yKu+dnn1SJejgt4596k"
            "6YjzGGphH2TUxwKzxcKDKKezwkpfnxPkSMkuEspGRt/aZZ9wa++Oi7Qkr8prgHc4soW6NUlfDzpvZK2H"
            "5E7eQaSeP3SAwGmQKUFHCddNaP0L+hM7zhFNzjFvpaMgJw0= test_gitlab_user.py")
        self.assertEqual(exist, True)

        notExist = self.moduleUtil.ssh_key_exists(
            user,
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDA1YotVDm2mAyk2tPt4E7AHm01sS6JZmcUdRuSuA5z"
            "szUJzYPPUSRAX3BCgTqLqYx//UuVncK7YqLVSbbwjKR2Ez5lISgCnVfLVEXzwhv+xawxKWmI7hJ5S0tO"
            "v6MJ+IxyTa4xcKwJTwB86z22n9fVOQeJTR2dSOH1WJrf0PvRk+KVNY2jTiGHTi9AIjLnyD/jWRpOgtdf"
            "kLRc8EzAWrWlgNmH2WOKBw6za0az6XoG75obUdFVdW3qcD0xc809OHLi7FDf+E7U4wiZJCFuUizMeXyu"
            "K/SkaE1aee4Qp5R4dxTR4TP9M1XAYkf+kF0W9srZ+mhF069XD/zhUPJsvwEF")
        self.assertEqual(notExist, False)

    @with_httmock(resp_get_user)
    @with_httmock(resp_create_user_keys)
    @with_httmock(resp_get_user_keys)
    def test_create_sshkey(self):
        user = self.gitlab_instance.users.get(1)

        rvalue = self.moduleUtil.add_ssh_key_to_user(user, {
            'name': "Public key",
            'file': "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAiPWx6WM4lhHNedGfBpPJNPpZ7yKu+dnn1SJe"
                    "jgt4596k6YjzGGphH2TUxwKzxcKDKKezwkpfnxPkSMkuEspGRt/aZZ9wa++Oi7Qkr8prgHc4"
                    "soW6NUlfDzpvZK2H5E7eQaSeP3SAwGmQKUFHCddNaP0L+hM7zhFNzjFvpaMgJw0=",
            'expires_at': ""})
        self.assertEqual(rvalue, False)

        rvalue = self.moduleUtil.add_ssh_key_to_user(user, {
            'name': "Not a private key",
            'file': "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDA1YotVDm2mAyk2tPt4E7AHm01sS6JZmcU"
                    "dRuSuA5zszUJzYPPUSRAX3BCgTqLqYx//UuVncK7YqLVSbbwjKR2Ez5lISgCnVfLVEXzwhv+"
                    "xawxKWmI7hJ5S0tOv6MJ+IxyTa4xcKwJTwB86z22n9fVOQeJTR2dSOH1WJrf0PvRk+KVNY2j"
                    "TiGHTi9AIjLnyD/jWRpOgtdfkLRc8EzAWrWlgNmH2WOKBw6za0az6XoG75obUdFVdW3qcD0x"
                    "c809OHLi7FDf+E7U4wiZJCFuUizMeXyuK/SkaE1aee4Qp5R4dxTR4TP9M1XAYkf+kF0W9srZ"
                    "+mhF069XD/zhUPJsvwEF",
            'expires_at': "2027-01-01"})
        self.assertEqual(rvalue, True)

    @with_httmock(resp_get_group)
    @with_httmock(resp_get_member)
    def test_find_member(self):
        group = self.gitlab_instance.groups.get(1)

        user = self.moduleUtil.find_member(group, 1)
        self.assertEqual(user.username, "raymond_smith")

    @with_httmock(resp_get_user)
    @with_httmock(resp_get_group)
    @with_httmock(resp_get_group)
    @with_httmock(resp_get_member)
    @with_httmock(resp_add_member)
    @with_httmock(resp_update_member)
    def test_assign_user_to_group(self):
        group = self.gitlab_instance.groups.get(1)
        user = self.gitlab_instance.users.get(1)

        rvalue = self.moduleUtil.assign_user_to_group(user, group.id, "developer")
        self.assertEqual(rvalue, False)

        rvalue = self.moduleUtil.assign_user_to_group(user, group.id, "guest")
        self.assertEqual(rvalue, True)

    def test_ssh_key_value(self):
        ssh_public_key = (
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCVA7p3quYXJfihdZIrHb/miia7DPL14mQ6wMp2LnJm"
            "BW8QqrFZ0xZDxEIbSZ+cnBhL76+xWi83eBeedeTBHsCUY2teqG8FFIJhB0YwjtSXQqRefgH3x6bincx4"
            "b3Hv8rRTwpKuGw6Q1sHbvzTSL9w5hhAm0iU7wSq67jBTFGvhXmFzcHwRZEh2yI0qIrp79mXF8pVsdUhU"
            "Uzg/pstNUHXQhwMo5ur1yQVZsFPnrwvybzkfZ1rp9UqnJQC7695ILxT+pCOn7vL5PHiRCTw6l37uo/K4"
            "i8JlUf/+Pmc/xnqLBPe5yzTdcJth/lXvP5M0vwjnYK9SaUDIzfpCnMmFGt/Rfa9tOXqhE7c3U6E1Iv7C"
            "ifktSsnYS+87Eif7xkC5Mpk7aBD+b4RjOJ1tNFNcl7xAa0mE6g/qOHbRK1ZNEVtw9ofqe7ycqdg3ojpm"
            "vS9XFmROcikAyOt+f02gyiv07LC0tlBVCKU7QawH+UoN0rKYNDEjq2mLrqMcAH0hmSMM26E="
        )
        self.assertEqual(ssh_public_key, ssh_key_value(ssh_public_key + " test_gitlab_user.py"))
        self.assertEqual(ssh_public_key, ssh_key_value(ssh_public_key + " some comment with more spaces"))
        self.assertEqual(ssh_public_key, ssh_key_value(ssh_public_key))
        self.assertEqual("garbage", ssh_key_value("garbage"))
