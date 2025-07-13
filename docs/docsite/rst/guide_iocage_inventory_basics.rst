..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory.guide_iocage_inventory_basics:

Basics
------

As root at the iocage host, create three VNET jails with a DHCP interface from the template
*ansible_client*:

.. code-block:: console

   shell> iocage create --template ansible_client --name srv_1 bpf=1 dhcp=1 vnet=1
   srv_1 successfully created!
   shell> iocage create --template ansible_client --name srv_2 bpf=1 dhcp=1 vnet=1
   srv_2 successfully created!
   shell> iocage create --template ansible_client --name srv_3 bpf=1 dhcp=1 vnet=1
   srv_3 successfully created!

See: `Configuring a VNET Jail <https://iocage.readthedocs.io/en/latest/networking.html#configuring-a-vnet-jail>`_.

As admin at the controller, list the jails:

.. code-block:: console

   shell> ssh admin@10.1.0.73 iocage list -l
   +------+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | JID  | NAME  | BOOT | STATE | TYPE |     RELEASE     |        IP4         | IP6 |    TEMPLATE    | BASEJAIL |
   +======+=======+======+=======+======+=================+====================+=====+================+==========+
   | None | srv_1 | off  | down  | jail | 14.2-RELEASE-p3 | DHCP (not running) | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | None | srv_2 | off  | down  | jail | 14.2-RELEASE-p3 | DHCP (not running) | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | None | srv_3 | off  | down  | jail | 14.2-RELEASE-p3 | DHCP (not running) | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+

Create the inventory file ``hosts/02_iocage.yml``

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin

Display the inventory:

.. code-block:: console

   shell> ansible-inventory -i hosts/02_iocage.yml --list --yaml
   all:
     children:
       ungrouped:
         hosts:
           srv_1:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (not running)
             iocage_ip6: '-'
             iocage_jid: None
             iocage_release: 14.2-RELEASE-p3
             iocage_state: down
             iocage_template: ansible_client
             iocage_type: jail
           srv_2:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (not running)
             iocage_ip6: '-'
             iocage_jid: None
             iocage_release: 14.2-RELEASE-p3
             iocage_state: down
             iocage_template: ansible_client
             iocage_type: jail
           srv_3:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (not running)
             iocage_ip6: '-'
             iocage_jid: None
             iocage_release: 14.2-RELEASE-p3
             iocage_state: down
             iocage_template: ansible_client
             iocage_type: jail

Optionally, create shared IP jails:

.. code-block:: console

   shell> iocage create --template ansible_client --name srv_1 ip4_addr="em0|10.1.0.101/24"
   srv_1 successfully created!
   shell> iocage create --template ansible_client --name srv_2 ip4_addr="em0|10.1.0.102/24"
   srv_2 successfully created!
   shell> iocage create --template ansible_client --name srv_3 ip4_addr="em0|10.1.0.103/24"
   srv_3 successfully created!
   shell> iocage list -l
   +------+-------+------+-------+------+-----------------+-------------------+-----+----------------+----------+
   | JID  | NAME  | BOOT | STATE | TYPE |     RELEASE     |        IP4        | IP6 |    TEMPLATE    | BASEJAIL |
   +======+=======+======+=======+======+=================+===================+=====+================+==========+
   | None | srv_1 | off  | down  | jail | 14.2-RELEASE-p3 | em0|10.1.0.101/24 | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+-------------------+-----+----------------+----------+
   | None | srv_2 | off  | down  | jail | 14.2-RELEASE-p3 | em0|10.1.0.102/24 | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+-------------------+-----+----------------+----------+
   | None | srv_3 | off  | down  | jail | 14.2-RELEASE-p3 | em0|10.1.0.103/24 | -   | ansible_client | no       |
   +------+-------+------+-------+------+-----------------+-------------------+-----+----------------+----------+

See: `Configuring a Shared IP Jail <https://iocage.readthedocs.io/en/latest/networking.html#configuring-a-shared-ip-jail>`_

If iocage needs environment variable(s), use the option :ansopt:`community.general.iocage#inventory:env`. For example,

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   env:
     CRYPTOGRAPHY_OPENSSL_NO_LEGACY: 1
