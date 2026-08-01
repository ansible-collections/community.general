..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_iocage.guide_iocage_inventory.guide_iocage_inventory_properties:

Properties
----------

Optionally, in the inventory file ``hosts/02_iocage.yml``, get the iocage properties. Enable
:ansopt:`community.general.iocage#inventory:get_properties`:

.. code-block:: yaml+jinja

   plugin: community.general.iocage
   host: 10.1.0.73
   user: admin
   get_properties: true
   hooks_results:
     - /var/db/dhclient-hook.address.epair0b
   compose:
     ansible_host: (iocage_hooks.0 == '-') | ternary(iocage_ip4, iocage_hooks.0)

Display the properties. Create the playbook ``pb-test-properties.yml``:

.. code-block:: yaml

   - hosts: all
     remote_user: admin

     vars:

       ansible_python_interpreter: auto_silent

     tasks:

       - debug:
           var: iocage_properties

Run the playbook. Limit the inventory to *srv_3*:

.. code-block:: console

   shell> ansible-playbook -i hosts/02_iocage.yml -l srv_3 pb-test-properties.yml

   PLAY [all] **********************************************************************************************************

   TASK [debug] ********************************************************************************************************
   ok: [srv_3] =>
       iocage_properties:
           CONFIG_VERSION: '33'
           allow_chflags: '0'
           allow_mlock: '0'
           allow_mount: '1'
           allow_mount_devfs: '0'
           allow_mount_fdescfs: '0'
           allow_mount_fusefs: '0'
           allow_mount_linprocfs: '0'
           allow_mount_linsysfs: '0'
           allow_mount_nullfs: '0'
           allow_mount_procfs: '0'
           allow_mount_tmpfs: '0'
           allow_mount_zfs: '0'
           allow_nfsd: '0'
           allow_quotas: '0'
           allow_raw_sockets: '0'
           allow_set_hostname: '1'
           allow_socket_af: '0'
           allow_sysvipc: '0'
           allow_tun: '0'
           allow_vmm: '0'
           assign_localhost: '0'
           available: readonly
           basejail: '0'
           boot: '0'
           bpf: '1'
           children_max: '0'
           cloned_release: 14.2-RELEASE
           comment: none
           compression: 'on'
           compressratio: readonly
           coredumpsize: 'off'
           count: '1'
           cpuset: 'off'
           cputime: 'off'
           datasize: 'off'
           dedup: 'off'
           defaultrouter: auto
           defaultrouter6: auto
           depends: none
           devfs_ruleset: '4'
           dhcp: '1'
           enforce_statfs: '2'
           exec_clean: '1'
           exec_created: /usr/bin/true
           exec_fib: '0'
           exec_jail_user: root
           exec_poststart: /usr/bin/true
           exec_poststop: /usr/bin/true
           exec_prestart: /usr/bin/true
           exec_prestop: /usr/bin/true
           exec_start: /bin/sh /etc/rc
           exec_stop: /bin/sh /etc/rc.shutdown
           exec_system_jail_user: '0'
           exec_system_user: root
           exec_timeout: '60'
           host_domainname: none
           host_hostname: srv-3
           host_hostuuid: srv_3
           host_time: '1'
           hostid: ea2ba7d1-4fcd-f13f-82e4-8b32c0a03403
           hostid_strict_check: '0'
           interfaces: vnet0:bridge0
           ip4: new
           ip4_addr: none
           ip4_saddrsel: '1'
           ip6: new
           ip6_addr: none
           ip6_saddrsel: '1'
           ip_hostname: '0'
           jail_zfs: '0'
           jail_zfs_dataset: iocage/jails/srv_3/data
           jail_zfs_mountpoint: none
           last_started: '2025-06-11 04:29:23'
           localhost_ip: none
           login_flags: -f root
           mac_prefix: 02a098
           maxproc: 'off'
           memorylocked: 'off'
           memoryuse: 'off'
           min_dyn_devfs_ruleset: '1000'
           mount_devfs: '1'
           mount_fdescfs: '1'
           mount_linprocfs: '0'
           mount_procfs: '0'
           mountpoint: readonly
           msgqqueued: 'off'
           msgqsize: 'off'
           nat: '0'
           nat_backend: ipfw
           nat_forwards: none
           nat_interface: none
           nat_prefix: '172.16'
           nmsgq: 'off'
           notes: none
           nsem: 'off'
           nsemop: 'off'
           nshm: 'off'
           nthr: 'off'
           openfiles: 'off'
           origin: readonly
           owner: root
           pcpu: 'off'
           plugin_name: none
           plugin_repository: none
           priority: '99'
           pseudoterminals: 'off'
           quota: none
           readbps: 'off'
           readiops: 'off'
           release: 14.2-RELEASE-p3
           reservation: none
           resolver: /etc/resolv.conf
           rlimits: 'off'
           rtsold: '0'
           securelevel: '2'
           shmsize: 'off'
           source_template: ansible_client
           stacksize: 'off'
           state: up
           stop_timeout: '30'
           swapuse: 'off'
           sync_state: none
           sync_target: none
           sync_tgt_zpool: none
           sysvmsg: new
           sysvsem: new
           sysvshm: new
           template: '0'
           type: jail
           used: readonly
           vmemoryuse: 'off'
           vnet: '1'
           vnet0_mac: 02a0983da05d 02a0983da05e
           vnet0_mtu: auto
           vnet1_mac: none
           vnet1_mtu: auto
           vnet2_mac: none
           vnet2_mtu: auto
           vnet3_mac: none
           vnet3_mtu: auto
           vnet_default_interface: auto
           vnet_default_mtu: '1500'
           vnet_interfaces: none
           wallclock: 'off'
           writebps: 'off'
           writeiops: 'off'

   PLAY RECAP **********************************************************************************************************
   srv_3                      : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
