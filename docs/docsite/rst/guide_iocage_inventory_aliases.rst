..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory.guide_iocage_inventory_aliases:

Aliases
-------

Quoting :ref:`inventory_aliases`:

   The ``inventory_hostname`` is the unique identifier for a host in Ansible, this can be an IP or a hostname, but also just an 'alias' or short name for the host.

As root at the iocage host, stop and destroy all jails:

.. code-block:: console

   shell> iocage stop ALL
   * Stopping srv_1
     + Executing prestop OK
     + Stopping services OK
     + Tearing down VNET OK
     + Removing devfs_ruleset: 1000 OK
     + Removing jail process OK
     + Executing poststop OK
   * Stopping srv_2
     + Executing prestop OK
     + Stopping services OK
     + Tearing down VNET OK
     + Removing devfs_ruleset: 1001 OK
     + Removing jail process OK
     + Executing poststop OK
   * Stopping srv_3
     + Executing prestop OK
     + Stopping services OK
     + Tearing down VNET OK
     + Removing devfs_ruleset: 1002 OK
     + Removing jail process OK
     + Executing poststop OK
   ansible_client is not running!

   shell> iocage destroy -f srv_1 srv_2 srv_3
   Destroying srv_1
   Destroying srv_2
   Destroying srv_3

Create three VNET jails with a DHCP interface from the template *ansible_client*. Use the option ``--count``:

.. code-block:: console

   shell> iocage create --short --template ansible_client --count 3 bpf=1 dhcp=1 vnet=1
   1c11de2d successfully created!
   9d94cc9e successfully created!
   052b9557 successfully created!

The names are random. Start the jails:

.. code-block:: console

   shell> iocage start ALL
   No default gateway found for ipv6.
   * Starting 052b9557
     + Started OK
     + Using devfs_ruleset: 1000 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.137/24
   No default gateway found for ipv6.
   * Starting 1c11de2d
     + Started OK
     + Using devfs_ruleset: 1001 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.146/24
   No default gateway found for ipv6.
   * Starting 9d94cc9e
     + Started OK
     + Using devfs_ruleset: 1002 (iocage generated default)
     + Configuring VNET OK
     + Using IP options: vnet
     + Starting services OK
     + Executing poststart OK
     + DHCP Address: 10.1.0.115/24
   Please convert back to a jail before trying to start ansible_client

List the jails:

.. code-block:: console

   shell> iocage list -l
   +-----+----------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | JID |   NAME   | BOOT | STATE | TYPE |     RELEASE     |        IP4         | IP6 |    TEMPLATE    | BASEJAIL |
   +=====+==========+======+=======+======+=================+====================+=====+================+==========+
   | 207 | 052b9557 | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.137 | -   | ansible_client | no       |
   +-----+----------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 208 | 1c11de2d | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.146 | -   | ansible_client | no       |
   +-----+----------+------+-------+------+-----------------+--------------------+-----+----------------+----------+
   | 209 | 9d94cc9e | off  | up    | jail | 14.2-RELEASE-p3 | epair0b|10.1.0.115 | -   | ansible_client | no       |
   +-----+----------+------+-------+------+-----------------+--------------------+-----+----------------+----------+

Set notes. The tag *alias* will be used to create inventory aliases:

.. code-block:: console

   shell> iocage set notes="vmm=iocage_02 project=foo alias=srv_1" 052b9557
   notes: none -> vmm=iocage_02 project=foo alias=srv_1
   shell> iocage set notes="vmm=iocage_02 project=foo alias=srv_2" 1c11de2d
   notes: none -> vmm=iocage_02 project=foo alias=srv_2
   shell> iocage set notes="vmm=iocage_02 project=bar alias=srv_3" 9d94cc9e
   notes: none -> vmm=iocage_02 project=bar alias=srv_3

Update the inventory configuration. Set the option
:ansopt:`community.general.iocage#inventory:inventory_hostname_tag` to :ansval:`alias`. This tag keeps the
value of the alias. The option :ansopt:`community.general.iocage#inventory:get_properties` must be
enabled. For example, ``hosts/02_iocage.yml`` contains:

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   get_properties: true
   inventory_hostname_tag: alias
   hooks_results:
     - /var/db/dhclient-hook.address.epair0b
   compose:
     ansible_host: (iocage_hooks.0 == '-') | ternary(iocage_ip4, iocage_hooks.0)
     iocage_tags: dict(iocage_properties.notes | split | map('split', '='))
   keyed_groups:
     - prefix: vmm
       key: iocage_tags.vmm
     - prefix: project
       key: iocage_tags.project

Display tags and groups. Create a playbook ``pb-test-groups.yml`` with the following content:

.. code-block:: yaml+jinja

   - hosts: all
     remote_user: admin

     vars:

       ansible_python_interpreter: auto_silent

     tasks:

       - debug:
           var: iocage_tags

       - debug:
           msg: |
             {% for group in groups %}
             {{ group }}: {{ groups[group] }}
             {% endfor %}
         run_once: true

Run the playbook:

.. code-block:: console

   shell> ansible-playbook -i hosts/02_iocage.yml pb-test-groups.yml

   PLAY [all] **********************************************************************************************************

   TASK [debug] ********************************************************************************************************
   ok: [srv_1] =>
       iocage_tags:
           alias: srv_1
           project: foo
           vmm: iocage_02
   ok: [srv_2] =>
       iocage_tags:
           alias: srv_2
           project: foo
           vmm: iocage_02
   ok: [srv_3] =>
       iocage_tags:
           alias: srv_3
           project: bar
           vmm: iocage_02

   TASK [debug] ********************************************************************************************************
   ok: [srv_1] =>
       msg: |-
           all: ['srv_1', 'srv_2', 'srv_3']
           ungrouped: []
           vmm_iocage_02: ['srv_1', 'srv_2', 'srv_3']
           project_foo: ['srv_1', 'srv_2']
           project_bar: ['srv_3']

   PLAY RECAP **********************************************************************************************************
   srv_1                      : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
   srv_2                      : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
   srv_3                      : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
