..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory.guide_iocage_inventory_hooks:

Hooks
-----

The iocage utility internally opens a console to a jail to get the jail's DHCP address. This
requires root. If you run the command ``iocage list -l`` as unprivileged user, you'll see the
message ``DHCP (running -- address requires root)``. If you are not granted the root privilege, use
``/etc/dhclient-exit-hooks``. For example, in the jail *srv_1*, create the file
``/zroot/iocage/jails/srv_1/root/etc/dhclient-exit-hooks``

.. code-block:: shell

   case "$reason" in
       "BOUND"|"REBIND"|"REBOOT"|"RENEW")
       echo $new_ip_address > /var/db/dhclient-hook.address.$interface
       ;;
   esac

where ``/zroot/iocage`` is the activated pool.

.. code-block:: console

   shell> zfs list | grep /zroot/iocage
   zroot/iocage                                4.69G   446G  5.08M  /zroot/iocage
   zroot/iocage/download                        927M   446G   384K  /zroot/iocage/download
   zroot/iocage/download/14.1-RELEASE           465M   446G   465M  /zroot/iocage/download/14.1-RELEASE
   zroot/iocage/download/14.2-RELEASE           462M   446G   462M  /zroot/iocage/download/14.2-RELEASE
   zroot/iocage/images                          384K   446G   384K  /zroot/iocage/images
   zroot/iocage/jails                           189M   446G   480K  /zroot/iocage/jails
   zroot/iocage/jails/srv_1                    62.9M   446G   464K  /zroot/iocage/jails/srv_1
   zroot/iocage/jails/srv_1/root               62.4M   446G  3.53G  /zroot/iocage/jails/srv_1/root
   zroot/iocage/jails/srv_2                    62.8M   446G   464K  /zroot/iocage/jails/srv_2
   zroot/iocage/jails/srv_2/root               62.3M   446G  3.53G  /zroot/iocage/jails/srv_2/root
   zroot/iocage/jails/srv_3                    62.8M   446G   464K  /zroot/iocage/jails/srv_3
   zroot/iocage/jails/srv_3/root               62.3M   446G  3.53G  /zroot/iocage/jails/srv_3/root
   zroot/iocage/log                             688K   446G   688K  /zroot/iocage/log
   zroot/iocage/releases                       2.93G   446G   384K  /zroot/iocage/releases
   zroot/iocage/releases/14.2-RELEASE          2.93G   446G   384K  /zroot/iocage/releases/14.2-RELEASE
   zroot/iocage/releases/14.2-RELEASE/root     2.93G   446G  2.88G  /zroot/iocage/releases/14.2-RELEASE/root
   zroot/iocage/templates                       682M   446G   416K  /zroot/iocage/templates
   zroot/iocage/templates/ansible_client        681M   446G   432K  /zroot/iocage/templates/ansible_client
   zroot/iocage/templates/ansible_client/root   681M   446G  3.53G  /zroot/iocage/templates/ansible_client/root

See: `man dhclient-script <https://man.freebsd.org/cgi/man.cgi?dhclient-script>`_

Create the inventory configuration. Use the option :ansopt:`community.general.iocage#inventory:hooks_results` instead of :ansopt:`community.general.iocage#inventory:sudo`:

.. code-block:: console

   shell> cat hosts/02_iocage.yml

.. code-block:: yaml

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   hooks_results:
     - /var/db/dhclient-hook.address.epair0b

.. note::

   The option :ansopt:`community.general.iocage#inventory:hooks_results` expects the poolname to be mounted to ``/poolname``. For example, if you
   activate the pool iocage, this plugin expects to find the :ansopt:`community.general.iocage#inventory:hooks_results` items in the path
   /iocage/iocage/jails/<name>/root. If you mount the poolname to a different path, the easiest
   remedy is to create a symlink.

As admin at the controller, display the inventory:

.. code-block:: console

   shell> ansible-inventory -i hosts/02_iocage.yml --list --yaml
   all:
     children:
       ungrouped:
         hosts:
           srv_1:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_hooks:
             - 10.1.0.183
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (running -- address requires root)
             iocage_ip6: '-'
             iocage_jid: '204'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail
           srv_2:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_hooks:
             - 10.1.0.204
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (running -- address requires root)
             iocage_ip6: '-'
             iocage_jid: '205'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail
           srv_3:
             iocage_basejail: 'no'
             iocage_boot: 'off'
             iocage_hooks:
             - 10.1.0.169
             iocage_ip4: '-'
             iocage_ip4_dict:
               ip4: []
               msg: DHCP (running -- address requires root)
             iocage_ip6: '-'
             iocage_jid: '206'
             iocage_release: 14.2-RELEASE-p3
             iocage_state: up
             iocage_template: ansible_client
             iocage_type: jail

Compose the variable ``ansible_host``. For example, ``hosts/02_iocage.yml`` could look like:

.. code-block:: yaml+jinja

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   hooks_results:
     - /var/db/dhclient-hook.address.epair0b
   compose:
     ansible_host: (iocage_hooks.0 == '-') | ternary(iocage_ip4, iocage_hooks.0)

Test the jails. Create a playbook ``pb-test-uname.yml``:

.. code-block:: yaml

   - hosts: all
     remote_user: admin

     vars:

       ansible_python_interpreter: auto_silent

     tasks:

       - command: uname -a
         register: out

       - debug:
           var: out.stdout

See: :ref:`working_with_bsd`

Run the playbook:

.. code-block:: console

   shell> ansible-playbook -i hosts/02_iocage.yml pb-test-uname.yml

   PLAY [all] **********************************************************************************************************

   TASK [command] ******************************************************************************************************
   changed: [srv_3]
   changed: [srv_1]
   changed: [srv_2]

   TASK [debug] ********************************************************************************************************
   ok: [srv_1] =>
       out.stdout: FreeBSD srv-1 14.2-RELEASE-p1 FreeBSD 14.2-RELEASE-p1 GENERIC amd64
   ok: [srv_3] =>
       out.stdout: FreeBSD srv-3 14.2-RELEASE-p1 FreeBSD 14.2-RELEASE-p1 GENERIC amd64
   ok: [srv_2] =>
       out.stdout: FreeBSD srv-2 14.2-RELEASE-p1 FreeBSD 14.2-RELEASE-p1 GENERIC amd64

   PLAY RECAP **********************************************************************************************************
   srv_1                      : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
   srv_2                      : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
   srv_3                      : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

Note: This playbook and the inventory configuration works also for the *Shared IP Jails*.
