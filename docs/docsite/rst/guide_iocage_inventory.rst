..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory:

community.general.iocage inventory plugin
=========================================

The inventory plugin :ansplugin:`community.general.iocage#inventory` gets the inventory hosts from the iocage jail manager.

See:

* `iocage - A FreeBSD Jail Manager <https://iocage.readthedocs.io/en/latest>`_
* `man iocage <https://man.freebsd.org/cgi/man.cgi?query=iocage>`_
* `Jails and Containers <https://docs.freebsd.org/en/books/handbook/jails>`_

.. note::
  The output of the examples is YAML formatted. See the option :ansopt:`ansible.builtin.default#callback:result_format`.

.. toctree::
   :caption: Table of Contents
   :maxdepth: 1

   guide_iocage_inventory_basics
   guide_iocage_inventory_dhcp
   guide_iocage_inventory_hooks
   guide_iocage_inventory_properties
   guide_iocage_inventory_tags
   guide_iocage_inventory_aliases
