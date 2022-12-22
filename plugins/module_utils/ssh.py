# -*- coding: utf-8 -*-
# Copyright (c) 2015, Björn Andersson
# Copyright (c) 2021, Ansible Project
# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import os


def determine_config_file(user, config_file):
    if user:
        config_file = os.path.join(os.path.expanduser('~%s' % user), '.ssh', 'config')
    elif config_file is None:
        config_file = '/etc/ssh/ssh_config'
    return config_file
