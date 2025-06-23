..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.inventory_guide.inventoy_guide_iocage:

community.general.iocage inventory plugin
-----------------------------------------

The inventory plugin :ansplugin:`community.general.iocage#inventory` gets the inventory hosts from the iocage jail manager.

See:

* `iocage - A FreeBSD Jail Manager <https://iocage.readthedocs.io/en/latest>`_
* `man iocage <https://man.freebsd.org/cgi/man.cgi?query=iocage>`_
* `Jails and Containers <https://docs.freebsd.org/en/books/handbook/jails>`_

.. note::
  The output of the examples is YAML formatted. See the option :ansopt:`ansible.bulitin.default#callback:result_format`.
* Run Ansible in Python virtual environment. See `venv — Creation of virtual environments <https://docs.python.org/3/library/venv.html#module-venv>`_.

.. toctree::
   :caption: Table of Contents
   :maxdepth: 1

   inventory_guide_iocage_basics
   inventory_guide_iocage_dhcp
   inventory_guide_iocage_hooks
   inventory_guide_iocage_properties
   inventory_guide_iocage_tags
   inventory_guide_iocage_aliases
