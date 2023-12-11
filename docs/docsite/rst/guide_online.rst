..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_online:

****************
Online.net Guide
****************

Introduction
============

Online is a French hosting company mainly known for providing bare-metal servers named Dedibox.
Check it out: `https://www.online.net/en <https://www.online.net/en>`_

Dynamic inventory for Online resources
--------------------------------------

Ansible has a dynamic inventory plugin that can list your resources.

1. Create a YAML configuration such as ``online_inventory.yml`` with this content:

   .. code-block:: yaml

       plugin: community.general.online

2. Set your ``ONLINE_TOKEN`` environment variable with your token.

   You need to open an account and log into it before you can get a token.
   You can find your token at the following page: `https://console.online.net/en/api/access <https://console.online.net/en/api/access>`_

3. You can test that your inventory is working by running:

   .. code-block:: console

       $ ansible-inventory -v -i online_inventory.yml --list


4. Now you can run your playbook or any other module with this inventory:

   .. code-block:: ansible-output

       $ ansible all -i online_inventory.yml -m ping
       sd-96735 | SUCCESS => {
           "changed": false,
           "ping": "pong"
       }
