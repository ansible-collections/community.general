..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory.guide_iocage_inventory_dhcp:

DHCP
----

As root at the iocage host, start the jails:

.. code-block:: console

   shell> iocage start ALL
   No default gateway found for ipv6.
   * Starting srv_1
     + Started OK
     + Using devfs_ruleset: 1000 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.183/24
   No default gateway found for ipv6.
   * Starting srv_2
     + Started OK
     + Using devfs_ruleset: 1001 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.204/24
   No default gateway found for ipv6.
   * Starting srv_3
     + Started OK
     + Using devfs_ruleset: 1002 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.169/24
   Please convert back to a jail before trying to start ansible_client

List the jails:

.. code-block:: console

   shell> iocage list -l
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | JID | NAME  | BOOT | STATE | TYPE |     RELEASE     |        IP4         | IP6 |    TEMPLATE    | BASEJAIL |
   +=====+=======+======+=======+======+=================+====================+=====+================+==========+
   | 204 | srv_1 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.183 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 205 | srv_2 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.204 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 206 | srv_3 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.169 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+

As admin at the controller, list the jails. The IP4 tab says "... address requires root":

.. code-block:: console

   shell> ssh admin@10.1.0.73 iocage list -l
   +-----+-------+------+-------+------+-----------------+-----------------------------------------+-----+----------------+----------+
   | JID | NAME  | BOOT | STATE | TYPE |     RELEASE     |                   IP4                   | IP6 |    TEMPLATE    | BASEJAIL |
   +=====+=======+======+=======+======+=================+=========================================+=====+================+==========+
   | 204 | srv_1 | off  | up    | jail | 14.2-RELEASE-p3 | DHCP (running -- address requires root) | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+-----------------------------------------+-----+----------------+----------+
   | 205 | srv_2 | off  | up    | jail | 14.2-RELEASE-p3 | DHCP (running -- address requires root) | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+-----------------------------------------+-----+----------------+----------+
   | 206 | srv_3 | off  | up    | jail | 14.2-RELEASE-p3 | DHCP (running -- address requires root) | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+-----------------------------------------+-----+----------------+----------+

Use sudo if enabled:

.. code-block:: console

   shell> ssh admin@10.1.0.73 sudo iocage list -l
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | JID | NAME  | BOOT | STATE | TYPE |     RELEASE     |        IP4         | IP6 |    TEMPLATE    | BASEJAIL |
   +=====+=======+======+=======+======+=================+====================+=====+================+==========+
   | 204 | srv_1 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.183 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 205 | srv_2 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.204 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 206 | srv_3 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.169 | -   | ansible_client | no       |
   +-----+-------+------+-------+------+-----------------+--------------------+-----+----------------+----------+

Create the inventory file ``hosts/02_iocage.yml``. Use the option
:ansopt:`community.general.iocage#inventory:sudo`:

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   sudo: true

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
             iocage_ip4: 10.1.0.183
             iocage_ip4_dict:
               ip4:
               - ifc: epair0b
                 ip: 10.1.0.183
                 mask: '-'
               msg: ''
             iocage_ip6: '-'
             iocage_jid: '204'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail
           srv_2:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_ip4: 10.1.0.204
             iocage_ip4_dict:
               ip4:
               - ifc: epair0b
                 ip: 10.1.0.204
                 mask: '-'
               msg: ''
             iocage_ip6: '-'
             iocage_jid: '205'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail
           srv_3:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_ip4: 10.1.0.169
             iocage_ip4_dict:
               ip4:
               - ifc: epair0b
                 ip: 10.1.0.169
                 mask: '-'
               msg: ''
             iocage_ip6: '-'
             iocage_jid: '206'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail

Note: If the option :ansopt:`community.general.iocage#inventory:env` is used and :ansopt:`community.general.iocage#inventory:sudo` is enabled, enable also :ansopt:`community.general.iocage#inventory:sudo_preserve_env`. For example,

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   env:
     CRYPTOGRAPHY_OPENSSL_NO_LEGACY: 1
   sudo: true
   sudo_preserve_env: true

In this case, make sure the sudo tag ``SETENV`` is used:

.. code-block:: console

   shell> ssh admin@10.1.0.73 sudo cat /usr/local/etc/sudoers | grep admin
   admin ALL=(ALL) NOPASSWD:SETENV: ALL
