..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.test_guide:

community.general Test (Plugin) Guide
=====================================

The :ref:`community.general collection <plugins_in_community.general>` offers currently one test plugin.

.. contents:: Topics

Feature Tests
-------------

The :ansplugin:`community.general.a_module test <community.general.a_module#test>` allows to check whether a given string refers to an existing module or action plugin. This can be useful in roles, which can use this to ensure that required modules are present ahead of time.

.. code-block:: yaml+jinja

    - name: Make sure that community.aws.route53 is available
      assert:
        that:
          - >
            'community.aws.route53' is community.general.a_module

    - name: Make sure that community.general.does_not_exist is not a module or action plugin
      assert:
        that:
          - "'community.general.does_not_exist' is not community.general.a_module"

.. versionadded:: 4.0.0
