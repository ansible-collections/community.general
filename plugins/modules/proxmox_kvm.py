#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Abdoul Bah (@helldorado) <bahabdoul at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_kvm
short_description: Management of Qemu(KVM) Virtual Machines in Proxmox VE cluster
description:
  - Allows you to create/delete/stop Qemu(KVM) Virtual Machines in Proxmox VE cluster.
  - Since community.general 4.0.0 on, there are no more default values.
author: "Abdoul Bah (@helldorado) <bahabdoul at gmail.com>"
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
  action_group:
    version_added: 9.0.0
options:
  archive:
    description:
      - Specify a path to an archive to restore (instead of creating or cloning a VM).
    type: str
    version_added: 6.5.0
  acpi:
    description:
      - Specify if ACPI should be enabled/disabled.
    type: bool
  agent:
    description:
      - Specify if the QEMU Guest Agent should be enabled/disabled.
      - Since community.general 5.5.0, this can also be a string instead of a boolean.
        This allows to specify values such as V(enabled=1,fstrim_cloned_disks=1).
    type: str
  args:
    description:
      - Pass arbitrary arguments to kvm.
      - This option is for experts only!
    type: str
  autostart:
    description:
      - Specify if the VM should be automatically restarted after crash (currently ignored in PVE API).
    type: bool
  balloon:
    description:
      - Specify the amount of RAM for the VM in MB.
      - Using zero disables the balloon driver.
    type: int
  bios:
    description:
      - Specify the BIOS implementation.
    type: str
    choices: ['seabios', 'ovmf']
  boot:
    description:
      - Specify the boot order -> boot on floppy V(a), hard disk V(c), CD-ROM V(d), or network V(n).
      - For newer versions of Proxmox VE, use a boot order like V(order=scsi0;net0;hostpci0).
      - You can combine to set order.
    type: str
  bootdisk:
    description:
      - 'Enable booting from specified disk. Format V((ide|sata|scsi|virtio\)\\d+).'
    type: str
  cicustom:
    description:
      - 'cloud-init: Specify custom files to replace the automatically generated ones at start.'
    type: str
    version_added: 1.3.0
  cipassword:
    description:
      - 'cloud-init: password of default user to create.'
    type: str
    version_added: 1.3.0
  citype:
    description:
      - 'cloud-init: Specifies the cloud-init configuration format.'
      - The default depends on the configured operating system type (V(ostype)).
      - We use the V(nocloud) format for Linux, and V(configdrive2) for Windows.
    type: str
    choices: ['nocloud', 'configdrive2']
    version_added: 1.3.0
  ciuser:
    description:
      - 'cloud-init: username of default user to create.'
    type: str
    version_added: 1.3.0
  clone:
    description:
      - Name of VM to be cloned. If O(vmid) is set, O(clone) can take an arbitrary value but is required for initiating the clone.
    type: str
  cores:
    description:
      - Specify number of cores per socket.
    type: int
  cpu:
    description:
      - Specify emulated CPU type.
    type: str
  cpulimit:
    description:
      - Specify if CPU usage will be limited. Value 0 indicates no CPU limit.
      - If the computer has 2 CPUs, it has total of '2' CPU time
    type: int
  cpuunits:
    description:
      - Specify CPU weight for a VM.
      - You can disable fair-scheduler configuration by setting this to 0
    type: int
  delete:
    description:
      - Specify a list of settings you want to delete.
    type: str
  description:
    description:
      - Specify the description for the VM. Only used on the configuration web interface.
      - This is saved as comment inside the configuration file.
    type: str
  digest:
    description:
      - Specify if to prevent changes if current configuration file has different SHA1 digest.
      - This can be used to prevent concurrent modifications.
    type: str
  efidisk0:
    description:
      - Specify a hash/dictionary of EFI disk options.
      - Requires O(bios=ovmf) to be set to be able to use it.
    type: dict
    suboptions:
      storage:
        description:
          - V(storage) is the storage identifier where to create the disk.
        type: str
      format:
        description:
          - V(format) is the drive's backing file's data format. Please refer to the Proxmox VE Administrator Guide,
           section Proxmox VE Storage (see U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html) for the latest
           version, tables 3 to 14) to find out format supported by the provided storage backend.
        type: str
      efitype:
        description:
          - V(efitype) indicates the size of the EFI disk.
          - V(2m) will allow for a 2MB EFI disk, which will be enough to persist boot order and new boot entries.
          - V(4m) will allow for a 4MB EFI disk, which will additionally allow to store EFI keys in order to enable
           Secure Boot
        type: str
        choices:
          - 2m
          - 4m
      pre_enrolled_keys:
        description:
          - V(pre_enrolled_keys) indicates whether EFI keys for Secure Boot should be enrolled V(1) in the VM firmware
           upon creation or not (0).
          - If set to V(1), Secure Boot will also be enabled by default when the VM is created.
        type: bool
    version_added: 4.5.0
  force:
    description:
      - Allow to force stop VM.
      - Can be used with states V(stopped), V(restarted), and V(absent).
      - Requires parameter O(archive).
    type: bool
  format:
    description:
      - Target drive's backing file's data format.
      - Used only with clone
      - Use O(format=unspecified) and O(full=false) for a linked clone.
      - Please refer to the Proxmox VE Administrator Guide, section Proxmox VE Storage (see
        U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html) for the latest version, tables 3 to 14) to find out format
        supported by the provided storage backend.
      - Not specifying this option is equivalent to setting it to V(unspecified).
    type: str
    choices: [ "cloop", "cow", "qcow", "qcow2", "qed", "raw", "vmdk", "unspecified" ]
  freeze:
    description:
      - Specify if PVE should freeze CPU at startup (use 'c' monitor command to start execution).
    type: bool
  full:
    description:
      - Create a full copy of all disk. This is always done when you clone a normal VM.
      - For VM templates, we try to create a linked clone by default.
      - Used only with clone
    type: bool
    default: true
  hookscript:
    description:
      - Script that will be executed during various steps in the containers lifetime.
    type: str
    version_added: 8.1.0
  hostpci:
    description:
      - Specify a hash/dictionary of map host pci devices into guest. O(hostpci='{"key":"value", "key":"value"}').
      - Keys allowed are - C(hostpci[n]) where 0 ≤ n ≤ N.
      - Values allowed are -  C("host="HOSTPCIID[;HOSTPCIID2...]",pcie="1|0",rombar="1|0",x-vga="1|0"").
      - The C(host) parameter is Host PCI device pass through. HOSTPCIID syntax is C(bus:dev.func) (hexadecimal numbers).
      - C(pcie=boolean) C(default=0) Choose the PCI-express bus (needs the q35 machine model).
      - C(rombar=boolean) C(default=1) Specify whether or not the device's ROM will be visible in the guest's memory map.
      - C(x-vga=boolean) C(default=0) Enable vfio-vga device support.
      - /!\ This option allows direct access to host hardware. So it is no longer possible to migrate such machines - use with special care.
    type: dict
  hotplug:
    description:
      - Selectively enable hotplug features.
      - This is a comma separated list of hotplug features V(network), V(disk), V(cpu), V(memory), and V(usb).
      - Value 0 disables hotplug completely and value 1 is an alias for the default V(network,disk,usb).
    type: str
  hugepages:
    description:
      - Enable/disable hugepages memory.
    type: str
    choices: ['any', '2', '1024']
  ide:
    description:
      - A hash/dictionary of volume used as IDE hard disk or CD-ROM. O(ide='{"key":"value", "key":"value"}').
      - Keys allowed are - C(ide[n]) where 0 ≤ n ≤ 3.
      - Values allowed are - C("storage:size,format=value").
      - C(storage) is the storage identifier where to create the disk.
      - C(size) is the size of the disk in GB.
      - C(format) is the drive's backing file's data format. C(qcow2|raw|subvol). Please refer to the Proxmox VE
        Administrator Guide, section Proxmox VE Storage (see U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html) for
        the latest version, tables 3 to 14) to find out format supported by the provided storage backend.
    type: dict
  ipconfig:
    description:
      - 'cloud-init: Set the IP configuration.'
      - A hash/dictionary of network ip configurations. O(ipconfig='{"key":"value", "key":"value"}').
      - Keys allowed are - C(ipconfig[n]) where 0 ≤ n ≤ network interfaces.
      - Values allowed are -  C("[gw=<GatewayIPv4>] [,gw6=<GatewayIPv6>] [,ip=<IPv4Format/CIDR>] [,ip6=<IPv6Format/CIDR>]").
      - 'cloud-init: Specify IP addresses and gateways for the corresponding interface.'
      - IP addresses use CIDR notation, gateways are optional but they should be in the same subnet of specified IP address.
      - The special string 'dhcp' can be used for IP addresses to use DHCP, in which case no explicit gateway should be provided.
      - For IPv6 the special string 'auto' can be used to use stateless autoconfiguration.
      - If cloud-init is enabled and neither an IPv4 nor an IPv6 address is specified, it defaults to using dhcp on IPv4.
    type: dict
    version_added: 1.3.0
  keyboard:
    description:
      - Sets the keyboard layout for VNC server.
    type: str
  kvm:
    description:
      - Enable/disable KVM hardware virtualization.
    type: bool
  localtime:
    description:
      - Sets the real time clock to local time.
      - This is enabled by default if ostype indicates a Microsoft OS.
    type: bool
  lock:
    description:
      - Lock/unlock the VM.
    type: str
    choices: ['migrate', 'backup', 'snapshot', 'rollback']
  machine:
    description:
      - Specifies the Qemu machine type.
      - 'Type => V((pc|pc(-i440fx\)?-\\d+\\.\\d+(\\.pxe\)?|q35|pc-q35-\\d+\\.\\d+(\\.pxe\)?\)).'
    type: str
  memory:
    description:
      - Memory size in MB for instance.
    type: int
  migrate:
    description:
      - Migrate the VM to O(node) if it is on another node.
    type: bool
    default: false
    version_added: 7.0.0
  migrate_downtime:
    description:
      - Sets maximum tolerated downtime (in seconds) for migrations.
    type: int
  migrate_speed:
    description:
      - Sets maximum speed (in MB/s) for migrations.
      - A value of 0 is no limit.
    type: int
  name:
    description:
      - Specifies the VM name. Name could be non-unique across the cluster.
      - Required only for O(state=present).
      - With O(state=present) if O(vmid) not provided and VM with name exists in the cluster then no changes will be made.
    type: str
  nameservers:
    description:
      - 'cloud-init: DNS server IP address(es).'
      - If unset, PVE host settings are used.
    type: list
    elements: str
    version_added: 1.3.0
  net:
    description:
      - A hash/dictionary of network interfaces for the VM. O(net='{"key":"value", "key":"value"}').
      - Keys allowed are - C(net[n]) where 0 ≤ n ≤ N.
      - Values allowed are - C("model="XX:XX:XX:XX:XX:XX",bridge="value",rate="value",tag="value",firewall="1|0",trunks="vlanid"").
      - Model is one of C(e1000 e1000-82540em e1000-82544gc e1000-82545em i82551 i82557b i82559er ne2k_isa ne2k_pci pcnet rtl8139 virtio vmxnet3).
      - C(XX:XX:XX:XX:XX:XX) should be an unique MAC address. This is automatically generated if not specified.
      - The C(bridge) parameter can be used to automatically add the interface to a bridge device. The Proxmox VE standard bridge is called 'vmbr0'.
      - Option C(rate) is used to limit traffic bandwidth from and to this interface. It is specified as floating point number, unit is 'Megabytes per second'.
      - If you specify no bridge, we create a kvm 'user' (NATed) network device, which provides DHCP and DNS services.
    type: dict
  newid:
    description:
      - VMID for the clone. Used only with clone.
      - If newid is not set, the next available VM ID will be fetched from ProxmoxAPI.
    type: int
  numa:
    description:
      - A hash/dictionaries of NUMA topology. O(numa='{"key":"value", "key":"value"}').
      - Keys allowed are - C(numa[n]) where 0 ≤ n ≤ N.
      - Values allowed are - C("cpu="<id[-id];...>",hostnodes="<id[-id];...>",memory="number",policy="(bind|interleave|preferred)"").
      - C(cpus) CPUs accessing this NUMA node.
      - C(hostnodes) Host NUMA nodes to use.
      - C(memory) Amount of memory this NUMA node provides.
      - C(policy) NUMA allocation policy.
    type: dict
  numa_enabled:
    description:
      - Enables NUMA.
    type: bool
  onboot:
    description:
      - Specifies whether a VM will be started during system bootup.
    type: bool
  ostype:
    description:
      - Specifies guest operating system. This is used to enable special optimization/features for specific operating systems.
      - The l26 is Linux 2.6/3.X Kernel.
    type: str
    choices: ['other', 'wxp', 'w2k', 'w2k3', 'w2k8', 'wvista', 'win7', 'win8', 'win10', 'win11', 'l24', 'l26', 'solaris']
  parallel:
    description:
      - A hash/dictionary of map host parallel devices. O(parallel='{"key":"value", "key":"value"}').
      - Keys allowed are - (parallel[n]) where 0 ≤ n ≤ 2.
      - Values allowed are - C("/dev/parport\d+|/dev/usb/lp\d+").
    type: dict
  protection:
    description:
      - Enable/disable the protection flag of the VM. This will enable/disable the remove VM and remove disk operations.
    type: bool
  reboot:
    description:
      - Allow reboot. If set to V(true), the VM exit on reboot.
    type: bool
  revert:
    description:
      - Revert a pending change.
    type: str
  sata:
    description:
      - A hash/dictionary of volume used as sata hard disk or CD-ROM. O(sata='{"key":"value", "key":"value"}').
      - Keys allowed are - C(sata[n]) where 0 ≤ n ≤ 5.
      - Values allowed are -  C("storage:size,format=value").
      - C(storage) is the storage identifier where to create the disk.
      - C(size) is the size of the disk in GB.
      - C(format) is the drive's backing file's data format. C(qcow2|raw|subvol). Please refer to the Proxmox VE
        Administrator Guide, section Proxmox VE Storage (see U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html) for
        the latest version, tables 3 to 14) to find out format supported by the provided storage backend.
    type: dict
  scsi:
    description:
      - A hash/dictionary of volume used as SCSI hard disk or CD-ROM. O(scsi='{"key":"value", "key":"value"}').
      - Keys allowed are - C(scsi[n]) where 0 ≤ n ≤ 13.
      - Values allowed are -  C("storage:size,format=value").
      - C(storage) is the storage identifier where to create the disk.
      - C(size) is the size of the disk in GB.
      - C(format) is the drive's backing file's data format. C(qcow2|raw|subvol). Please refer to the Proxmox VE
        Administrator Guide, section Proxmox VE Storage (see U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html) for
        the latest version, tables 3 to 14) to find out format supported by the provided storage backend.
    type: dict
  scsihw:
    description:
      - Specifies the SCSI controller model.
    type: str
    choices: ['lsi', 'lsi53c810', 'virtio-scsi-pci', 'virtio-scsi-single', 'megasas', 'pvscsi']
  searchdomains:
    description:
      - 'cloud-init: Sets DNS search domain(s).'
      - If unset, PVE host settings are used.
    type: list
    elements: str
    version_added: 1.3.0
  serial:
    description:
      - A hash/dictionary of serial device to create inside the VM. V('{"key":"value", "key":"value"}').
      - Keys allowed are - serial[n](str; required) where 0 ≤ n ≤ 3.
      - Values allowed are - V((/dev/.+|socket\)).
      - /!\ If you pass through a host serial device, it is no longer possible to migrate such machines - use with special care.
    type: dict
  shares:
    description:
      - Rets amount of memory shares for auto-ballooning. (0 - 50000).
      - The larger the number is, the more memory this VM gets.
      - The number is relative to weights of all other running VMs.
      - Using 0 disables auto-ballooning, this means no limit.
    type: int
  skiplock:
    description:
      - Ignore locks
      - Only root is allowed to use this option.
    type: bool
  smbios:
    description:
      - Specifies SMBIOS type 1 fields.
      - "Comma separated, Base64 encoded (optional) SMBIOS properties:"
      - V([base64=<1|0>] [,family=<Base64 encoded string>])
      - V([,manufacturer=<Base64 encoded string>])
      - V([,product=<Base64 encoded string>])
      - V([,serial=<Base64 encoded string>])
      - V([,sku=<Base64 encoded string>])
      - V([,uuid=<UUID>])
      - V([,version=<Base64 encoded string>])
    type: str
  snapname:
    description:
      - The name of the snapshot. Used only with clone.
    type: str
  sockets:
    description:
      - Sets the number of CPU sockets. (1 - N).
    type: int
  sshkeys:
    description:
      - 'cloud-init: SSH key to assign to the default user. NOT TESTED with multiple keys but a multi-line value should work.'
    type: str
    version_added: 1.3.0
  startdate:
    description:
      - Sets the initial date of the real time clock.
      - Valid format for date are V('now') or V('2016-09-25T16:01:21') or V('2016-09-25').
    type: str
  startup:
    description:
      - Startup and shutdown behavior. V([[order=]\\d+] [,up=\\d+] [,down=\\d+]).
      - Order is a non-negative number defining the general startup order.
      - Shutdown in done with reverse ordering.
    type: str
  state:
    description:
      - Indicates desired state of the instance.
      - If V(current), the current state of the VM will be fetched. You can access it with C(results.status)
      - V(template) was added in community.general 8.1.0.
    type: str
    choices: ['present', 'started', 'absent', 'stopped', 'restarted', 'current', 'template']
    default: present
  storage:
    description:
      - Target storage for full clone.
    type: str
  tablet:
    description:
      - Enables/disables the USB tablet device.
    type: bool
  tags:
    description:
      - List of tags to apply to the VM instance.
      - Tags must start with V([a-z0-9_]) followed by zero or more of the following characters V([a-z0-9_-+.]).
      - Tags are only available in Proxmox 6+.
    type: list
    elements: str
    version_added: 2.3.0
  target:
    description:
      - Target node. Only allowed if the original VM is on shared storage.
      - Used only with clone
    type: str
  tdf:
    description:
      - Enables/disables time drift fix.
    type: bool
  template:
    description:
      - Enables/disables the template.
    type: bool
  timeout:
    description:
      - Timeout for operations.
      - When used with O(state=stopped) the option sets a graceful timeout for VM stop after which a VM will be forcefully stopped.
    type: int
    default: 30
  tpmstate0:
    description:
      - A hash/dictionary of options for the Trusted Platform Module disk.
      - A TPM state disk is required for Windows 11 installations.
    suboptions:
      storage:
        description:
          - O(tpmstate0.storage) is the storage identifier where to create the disk.
        type: str
        required: true
      version:
        description:
          - The TPM version to use.
        type: str
        choices: ['1.2', '2.0']
        default: '2.0'
    type: dict
    version_added: 7.1.0
  usb:
    description:
      - A hash/dictionary of USB devices for the VM. O(usb='{"key":"value", "key":"value"}').
      - Keys allowed are - C(usb[n]) where 0 ≤ n ≤ N.
      - Values allowed are - C(host="value|spice",mapping="value",usb3="1|0").
      - host is either C(spice) or the USB id/port.
      - Option C(mapping) is the mapped USB device name.
      - Option C(usb3) enables USB 3 support.
    type: dict
    version_added: 9.0.0
  update:
    description:
      - If V(true), the VM will be updated with new value.
      - Because of the operations of the API and security reasons, I have disabled the update of the following parameters
        O(net), O(virtio), O(ide), O(sata), O(scsi). Per example updating O(net) update the MAC address and C(virtio) create always new disk...
        This security feature can be disabled by setting the O(update_unsafe) to V(true).
      - Update of O(pool) is disabled. It needs an additional API endpoint not covered by this module.
    type: bool
    default: false
  update_unsafe:
    description:
      - If V(true), do not enforce limitations on parameters O(net), O(virtio), O(ide), O(sata), O(scsi), O(efidisk0), and O(tpmstate0).
        Use this option with caution because an improper configuration might result in a permanent loss of data (e.g. disk recreated).
    type: bool
    default: false
    version_added: 8.4.0
  vcpus:
    description:
      - Sets number of hotplugged vcpus.
    type: int
  vga:
    description:
      - Select VGA type. If you want to use high resolution modes (>= 1280x1024x16) then you should use option 'std' or 'vmware'.
    type: str
    choices: ['std', 'cirrus', 'vmware', 'qxl', 'serial0', 'serial1', 'serial2', 'serial3', 'qxl2', 'qxl3', 'qxl4']
  virtio:
    description:
      - A hash/dictionary of volume used as VIRTIO hard disk. O(virtio='{"key":"value", "key":"value"}').
      - Keys allowed are - C(virtio[n]) where 0 ≤ n ≤ 15.
      - Values allowed are -  C("storage:size,format=value").
      - C(storage) is the storage identifier where to create the disk.
      - C(size) is the size of the disk in GB.
      - C(format) is the drive's backing file's data format. C(qcow2|raw|subvol). Please refer to the Proxmox VE
        Administrator Guide, section Proxmox VE Storage (see U(https://pve.proxmox.com/pve-docs/chapter-pvesm.html)
        for the latest version, tables 3 to 14) to find out format supported by the provided storage backend.
    type: dict
  watchdog:
    description:
      - Creates a virtual hardware watchdog device.
    type: str
seealso:
  - module: community.general.proxmox_vm_info
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.proxmox.selection
  - community.general.attributes
'''

EXAMPLES = '''
- name: Create new VM with minimal options
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf

- name: Create a VM from archive (backup)
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    archive: backup-storage:backup/vm/140/2023-03-08T06:41:23Z
    name: spynal

- name: Create new VM with minimal options and given vmid
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    vmid: 100

- name: Create new VM with two network interface options
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    net:
      net0: 'virtio,bridge=vmbr1,rate=200'
      net1: 'e1000,bridge=vmbr2'

- name: Create new VM with one network interface, three virto hard disk, 4 cores, and 2 vcpus
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    net:
      net0: 'virtio,bridge=vmbr1,rate=200'
    virtio:
      virtio0: 'VMs_LVM:10'
      virtio1: 'VMs:2,format=qcow2'
      virtio2: 'VMs:5,format=raw'
    cores: 4
    vcpus: 2

- name: Create VM with 1 10GB SATA disk and an EFI disk, with Secure Boot disabled by default
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    sata:
      sata0: 'VMs_LVM:10,format=raw'
    bios: ovmf
    efidisk0:
      storage: VMs_LVM_thin
      format: raw
      efitype: 4m
      pre_enrolled_keys: false

- name: Create VM with 1 10GB SATA disk and an EFI disk, with Secure Boot enabled by default
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    sata:
      sata0: 'VMs_LVM:10,format=raw'
    bios: ovmf
    efidisk0:
      storage: VMs_LVM
      format: raw
      efitype: 4m
      pre_enrolled_keys: 1

- name: >
    Clone VM with only source VM name.
    The VM source is spynal.
    The target VM name is zavala
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    clone: spynal
    name: zavala
    node: sabrewulf
    storage: VMs
    format: qcow2
    timeout: 500

- name: >
    Create linked clone VM with only source VM name.
    The VM source is spynal.
    The target VM name is zavala
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    clone: spynal
    name: zavala
    node: sabrewulf
    storage: VMs
    full: false
    format: unspecified
    timeout: 500

- name: Clone VM with source vmid and target newid and raw format
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    clone: arbitrary_name
    vmid: 108
    newid: 152
    name: zavala
    node: sabrewulf
    storage: LVM_STO
    format: raw
    timeout: 300

- name: Create new VM and lock it for snapshot
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    lock: snapshot

- name: Create new VM and set protection to disable the remove VM and remove disk operations
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    protection: true

- name: Create new VM using cloud-init with a username and password
  community.general.proxmox_kvm:
    node: sabrewulf
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    ide:
      ide2: 'local:cloudinit,format=qcow2'
    ciuser: mylinuxuser
    cipassword: supersecret
    searchdomains: 'mydomain.internal'
    nameservers: 1.1.1.1
    net:
      net0: 'virtio,bridge=vmbr1,tag=77'
    ipconfig:
      ipconfig0: 'ip=192.168.1.1/24,gw=192.168.1.1'

- name: Create new VM using Cloud-Init with an ssh key
  community.general.proxmox_kvm:
    node: sabrewulf
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    ide:
      ide2: 'local:cloudinit,format=qcow2'
    sshkeys: 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILJkVm98B71lD5XHfihwcYHE9TVpsJmK1vR1JcaU82L+'
    searchdomains: 'mydomain.internal'
    nameservers:
      - '1.1.1.1'
      - '8.8.8.8'
    net:
      net0: 'virtio,bridge=vmbr1,tag=77'
    ipconfig:
      ipconfig0: 'ip=192.168.1.1/24'

- name: Start VM
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: started

- name: Stop VM
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: stopped

- name: Stop VM with force
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: stopped
    force: true

- name: Restart VM
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: restarted

- name: Convert VM to template
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: template

- name: Convert VM to template (stop VM if running)
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: template
    force: true

- name: Remove VM
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: absent

- name: Get VM current state
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    state: current

- name: Update VM configuration
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    cores: 8
    memory: 16384
    update: true

- name: Update VM configuration (incl. unsafe options)
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    cores: 8
    memory: 16384
    net:
        net0: virtio,bridge=vmbr1
    update: true
    update_unsafe: true

- name: Delete QEMU parameters
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    delete: 'args,template,cpulimit'

- name: Revert a pending change
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf
    revert: 'template,cpulimit'

- name: Migrate VM on second node
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    name: spynal
    node: sabrewulf-2
    migrate: true

- name: Add hookscript to existing VM
  community.general.proxmox_kvm:
    api_user: root@pam
    api_password: secret
    api_host: helldorado
    vmid: 999
    node: sabrewulf
    hookscript: local:snippets/hookscript.pl
    update: true

'''

RETURN = '''
vmid:
  description: The VM vmid.
  returned: success
  type: int
  sample: 115
status:
  description: The current virtual machine status.
  returned: success, not clone, not absent, not update
  type: str
  sample: running
msg:
  description: A short message
  returned: always
  type: str
  sample: "VM kropta with vmid = 110 is running"
'''

import re
import time
from ansible.module_utils.six.moves.urllib.parse import quote

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import boolean


def parse_mac(netstr):
    return re.search('=(.*?),', netstr).group(1)


def parse_dev(devstr):
    return re.search('(.*?)(,|$)', devstr).group(1)


class ProxmoxKvmAnsible(ProxmoxAnsible):
    def get_vminfo(self, node, vmid, **kwargs):
        global results
        results = {}
        mac = {}
        devices = {}
        try:
            vm = self.proxmox_api.nodes(node).qemu(vmid).config.get()
        except Exception as e:
            self.module.fail_json(msg='Getting information for VM with vmid = %s failed with exception: %s' % (vmid, e))

        # Sanitize kwargs. Remove not defined args and ensure True and False converted to int.
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Convert all dict in kwargs to elements.
        # For hostpci[n], ide[n], net[n], numa[n], parallel[n], sata[n], scsi[n], serial[n], virtio[n]
        for k in list(kwargs.keys()):
            if isinstance(kwargs[k], dict):
                kwargs.update(kwargs[k])
                del kwargs[k]

        # Split information by type
        re_net = re.compile(r'net[0-9]')
        re_dev = re.compile(r'(virtio|ide|scsi|sata|efidisk)[0-9]')
        for k in kwargs.keys():
            if re_net.match(k):
                mac[k] = parse_mac(vm[k])
            elif re_dev.match(k):
                devices[k] = parse_dev(vm[k])

        results['mac'] = mac
        results['devices'] = devices
        results['vmid'] = int(vmid)

    def settings(self, vmid, node, **kwargs):
        proxmox_node = self.proxmox_api.nodes(node)

        # Sanitize kwargs. Remove not defined args and ensure True and False converted to int.
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        return proxmox_node.qemu(vmid).config.set(**kwargs) is None

    def wait_for_task(self, node, taskid):
        timeout = self.module.params['timeout']
        if self.module.params['state'] == 'stopped':
            # Increase task timeout in case of stopped state to be sure it waits longer than VM stop operation itself
            timeout += 10

        while timeout:
            if self.api_task_ok(node, taskid):
                # Wait an extra second as the API can be a ahead of the hypervisor
                time.sleep(1)
                return True
            timeout = timeout - 1
            if timeout == 0:
                break
            time.sleep(1)
        return False

    def create_vm(self, vmid, newid, node, name, memory, cpu, cores, sockets, update, update_unsafe, **kwargs):
        # Available only in PVE 4
        only_v4 = ['force', 'protection', 'skiplock']
        only_v6 = ['ciuser', 'cipassword', 'sshkeys', 'ipconfig', 'tags']

        # valid clone parameters
        valid_clone_params = ['format', 'full', 'pool', 'snapname', 'storage', 'target']
        clone_params = {}
        # Default args for vm. Note: -args option is for experts only. It allows you to pass arbitrary arguments to kvm.
        vm_args = "-serial unix:/var/run/qemu-server/{0}.serial,server,nowait".format(vmid)

        proxmox_node = self.proxmox_api.nodes(node)

        # Sanitize kwargs. Remove not defined args and ensure True and False converted to int.
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        kwargs.update({k: int(v) for k, v in kwargs.items() if isinstance(v, bool)})

        version = self.version()
        pve_major_version = 3 if version < LooseVersion('4.0') else version.version[0]

        # The features work only on PVE 4+
        if pve_major_version < 4:
            for p in only_v4:
                if p in kwargs:
                    del kwargs[p]

        # The features work only on PVE 6
        if pve_major_version < 6:
            for p in only_v6:
                if p in kwargs:
                    del kwargs[p]

        # 'sshkeys' param expects an urlencoded string
        if 'sshkeys' in kwargs:
            urlencoded_ssh_keys = quote(kwargs['sshkeys'], safe='')
            kwargs['sshkeys'] = str(urlencoded_ssh_keys)

        # If update, don't update disk (virtio, efidisk0, tpmstate0, ide, sata, scsi) and network interface, unless update_unsafe=True
        # pool parameter not supported by qemu/<vmid>/config endpoint on "update" (PVE 6.2) - only with "create"
        if update:
            if update_unsafe is False:
                if 'virtio' in kwargs:
                    del kwargs['virtio']
                if 'sata' in kwargs:
                    del kwargs['sata']
                if 'scsi' in kwargs:
                    del kwargs['scsi']
                if 'ide' in kwargs:
                    del kwargs['ide']
                if 'efidisk0' in kwargs:
                    del kwargs['efidisk0']
                if 'tpmstate0' in kwargs:
                    del kwargs['tpmstate0']
                if 'net' in kwargs:
                    del kwargs['net']
            if 'force' in kwargs:
                del kwargs['force']
            if 'pool' in kwargs:
                del kwargs['pool']

        # Check that the bios option is set to ovmf if the efidisk0 option is present
        if 'efidisk0' in kwargs:
            if ('bios' not in kwargs) or ('ovmf' != kwargs['bios']):
                self.module.fail_json(msg='efidisk0 cannot be used if bios is not set to ovmf. ')

        # Flatten efidisk0 option to a string so that it's a string which is what Proxmoxer and the API expect
        if 'efidisk0' in kwargs:
            efidisk0_str = ''
            # Regexp to catch underscores in keys name, to replace them after by hyphens
            hyphen_re = re.compile(r'_')
            # If present, the storage definition should be the first argument
            if 'storage' in kwargs['efidisk0']:
                efidisk0_str += kwargs['efidisk0'].get('storage') + ':1,'
                kwargs['efidisk0'].pop('storage')
            # Join other elements from the dict as key=value using commas as separator, replacing any underscore in key
            # by hyphens (needed for pre_enrolled_keys to pre-enrolled-keys)
            efidisk0_str += ','.join([hyphen_re.sub('-', k) + "=" + str(v) for k, v in kwargs['efidisk0'].items()
                                      if 'storage' != k])
            kwargs['efidisk0'] = efidisk0_str

        # Flatten tpmstate0 option to a string so that it's a string which is what Proxmoxer and the API expect
        if 'tpmstate0' in kwargs:
            kwargs['tpmstate0'] = '{storage}:1,version=v{version}'.format(
                storage=kwargs['tpmstate0'].get('storage'),
                version=kwargs['tpmstate0'].get('version')
            )

        # Convert all dict in kwargs to elements.
        # For hostpci[n], ide[n], net[n], numa[n], parallel[n], sata[n], scsi[n], serial[n], virtio[n], ipconfig[n], usb[n]
        for k in list(kwargs.keys()):
            if isinstance(kwargs[k], dict):
                kwargs.update(kwargs[k])
                del kwargs[k]

        if 'agent' in kwargs:
            try:
                # The API also allows booleans instead of e.g. `enabled=1` for backward-compatibility.
                kwargs['agent'] = int(boolean(kwargs['agent'], strict=True))
            except TypeError:
                # Not something that Ansible would parse as a boolean.
                pass

        # Rename numa_enabled to numa, according the API documentation
        if 'numa_enabled' in kwargs:
            kwargs['numa'] = kwargs['numa_enabled']
            del kwargs['numa_enabled']

        # PVE api expects strings for the following params
        if 'nameservers' in self.module.params:
            nameservers = self.module.params.pop('nameservers')
            if nameservers:
                kwargs['nameserver'] = ' '.join(nameservers)
        if 'searchdomains' in self.module.params:
            searchdomains = self.module.params.pop('searchdomains')
            if searchdomains:
                kwargs['searchdomain'] = ' '.join(searchdomains)

        # VM tags are expected to be valid and presented as a comma/semi-colon delimited string
        if 'tags' in kwargs:
            re_tag = re.compile(r'^[a-z0-9_][a-z0-9_\-\+\.]*$')
            for tag in kwargs['tags']:
                if not re_tag.match(tag):
                    self.module.fail_json(msg='%s is not a valid tag' % tag)
            kwargs['tags'] = ",".join(kwargs['tags'])

        # -args and skiplock require root@pam user - but can not use api tokens
        if self.module.params['api_user'] == "root@pam" and self.module.params['args'] is not None:
            kwargs['args'] = self.module.params['args']
        elif self.module.params['api_user'] != "root@pam" and self.module.params['args'] is not None:
            self.module.fail_json(msg='args parameter require root@pam user. ')

        if self.module.params['api_user'] != "root@pam" and self.module.params['skiplock'] is not None:
            self.module.fail_json(msg='skiplock parameter require root@pam user. ')

        if update:
            if proxmox_node.qemu(vmid).config.set(name=name, memory=memory, cpu=cpu, cores=cores, sockets=sockets, **kwargs) is None:
                return True
            else:
                return False
        elif self.module.params['clone'] is not None:
            for param in valid_clone_params:
                if self.module.params[param] is not None:
                    clone_params[param] = self.module.params[param]
            clone_params.update({k: int(v) for k, v in clone_params.items() if isinstance(v, bool)})
            taskid = proxmox_node.qemu(vmid).clone.post(newid=newid, name=name, **clone_params)
        else:
            taskid = proxmox_node.qemu.create(vmid=vmid, name=name, memory=memory, cpu=cpu, cores=cores, sockets=sockets, **kwargs)

        if not self.wait_for_task(node, taskid):
            self.module.fail_json(msg='Reached timeout while waiting for creating VM. Last line in task before timeout: %s' %
                                  proxmox_node.tasks(taskid).log.get()[:1])
            return False
        return True

    def start_vm(self, vm):
        vmid = vm['vmid']
        proxmox_node = self.proxmox_api.nodes(vm['node'])
        taskid = proxmox_node.qemu(vmid).status.start.post()
        if not self.wait_for_task(vm['node'], taskid):
            self.module.fail_json(msg='Reached timeout while waiting for starting VM. Last line in task before timeout: %s' %
                                  proxmox_node.tasks(taskid).log.get()[:1])
            return False
        return True

    def stop_vm(self, vm, force, timeout):
        vmid = vm['vmid']
        proxmox_node = self.proxmox_api.nodes(vm['node'])
        taskid = proxmox_node.qemu(vmid).status.shutdown.post(forceStop=(1 if force else 0), timeout=timeout)
        if not self.wait_for_task(vm['node'], taskid):
            self.module.fail_json(msg='Reached timeout while waiting for stopping VM. Last line in task before timeout: %s' %
                                  proxmox_node.tasks(taskid).log.get()[:1])
            return False
        return True

    def restart_vm(self, vm, force, **status):
        vmid = vm['vmid']
        try:
            proxmox_node = self.proxmox_api.nodes(vm['node'])
            taskid = proxmox_node.qemu(vmid).status.reset.post() if force else proxmox_node.qemu(vmid).status.reboot.post()
            if not self.wait_for_task(vm['node'], taskid):
                self.module.fail_json(msg='Reached timeout while waiting for rebooting VM. Last line in task before timeout: %s' %
                                          proxmox_node.tasks(taskid).log.get()[:1])
                return False
            return True
        except Exception as e:
            self.module.fail_json(vmid=vmid, msg="restarting of VM %s failed with exception: %s" % (vmid, e))
            return False

    def convert_to_template(self, vm, timeout, force):
        vmid = vm['vmid']
        try:
            proxmox_node = self.proxmox_api.nodes(vm['node'])
            if proxmox_node.qemu(vmid).status.current.get()['status'] == 'running' and force:
                self.stop_instance(vm, vmid, timeout, force)
            # not sure why, but templating a container doesn't return a taskid
            proxmox_node.qemu(vmid).template.post()
            return True
        except Exception as e:
            self.module.fail_json(vmid=vmid, msg="conversion of VM %s to template failed with exception: %s" % (vmid, e))
            return False

    def migrate_vm(self, vm, target_node):
        vmid = vm['vmid']
        proxmox_node = self.proxmox_api.nodes(vm['node'])
        taskid = proxmox_node.qemu(vmid).migrate.post(vmid=vmid, node=vm['node'], target=target_node, online=1)
        if not self.wait_for_task(vm['node'], taskid):
            self.module.fail_json(msg='Reached timeout while waiting for migrating VM. Last line in task before timeout: %s' %
                                  proxmox_node.tasks(taskid).log.get()[:1])
            return False
        return True


def main():
    module_args = proxmox_auth_argument_spec()
    kvm_args = dict(
        archive=dict(type='str'),
        acpi=dict(type='bool'),
        agent=dict(type='str'),
        args=dict(type='str'),
        autostart=dict(type='bool'),
        balloon=dict(type='int'),
        bios=dict(choices=['seabios', 'ovmf']),
        boot=dict(type='str'),
        bootdisk=dict(type='str'),
        cicustom=dict(type='str'),
        cipassword=dict(type='str', no_log=True),
        citype=dict(type='str', choices=['nocloud', 'configdrive2']),
        ciuser=dict(type='str'),
        clone=dict(type='str'),
        cores=dict(type='int'),
        cpu=dict(type='str'),
        cpulimit=dict(type='int'),
        cpuunits=dict(type='int'),
        delete=dict(type='str'),
        description=dict(type='str'),
        digest=dict(type='str'),
        efidisk0=dict(type='dict',
                      options=dict(
                          storage=dict(type='str'),
                          format=dict(type='str'),
                          efitype=dict(type='str', choices=['2m', '4m']),
                          pre_enrolled_keys=dict(type='bool'),
                      )),
        force=dict(type='bool'),
        format=dict(type='str', choices=['cloop', 'cow', 'qcow', 'qcow2', 'qed', 'raw', 'vmdk', 'unspecified']),
        freeze=dict(type='bool'),
        full=dict(type='bool', default=True),
        hookscript=dict(type='str'),
        hostpci=dict(type='dict'),
        hotplug=dict(type='str'),
        hugepages=dict(choices=['any', '2', '1024']),
        ide=dict(type='dict'),
        ipconfig=dict(type='dict'),
        keyboard=dict(type='str'),
        kvm=dict(type='bool'),
        localtime=dict(type='bool'),
        lock=dict(choices=['migrate', 'backup', 'snapshot', 'rollback']),
        machine=dict(type='str'),
        memory=dict(type='int'),
        migrate=dict(type='bool', default=False),
        migrate_downtime=dict(type='int'),
        migrate_speed=dict(type='int'),
        name=dict(type='str'),
        nameservers=dict(type='list', elements='str'),
        net=dict(type='dict'),
        newid=dict(type='int'),
        node=dict(),
        numa=dict(type='dict'),
        numa_enabled=dict(type='bool'),
        onboot=dict(type='bool'),
        ostype=dict(choices=['other', 'wxp', 'w2k', 'w2k3', 'w2k8', 'wvista', 'win7', 'win8', 'win10', 'win11', 'l24', 'l26', 'solaris']),
        parallel=dict(type='dict'),
        pool=dict(type='str'),
        protection=dict(type='bool'),
        reboot=dict(type='bool'),
        revert=dict(type='str'),
        sata=dict(type='dict'),
        scsi=dict(type='dict'),
        scsihw=dict(choices=['lsi', 'lsi53c810', 'virtio-scsi-pci', 'virtio-scsi-single', 'megasas', 'pvscsi']),
        serial=dict(type='dict'),
        searchdomains=dict(type='list', elements='str'),
        shares=dict(type='int'),
        skiplock=dict(type='bool'),
        smbios=dict(type='str'),
        snapname=dict(type='str'),
        sockets=dict(type='int'),
        sshkeys=dict(type='str', no_log=False),
        startdate=dict(type='str'),
        startup=dict(),
        state=dict(default='present', choices=['present', 'absent', 'stopped', 'started', 'restarted', 'current', 'template']),
        storage=dict(type='str'),
        tablet=dict(type='bool'),
        tags=dict(type='list', elements='str'),
        target=dict(type='str'),
        tdf=dict(type='bool'),
        template=dict(type='bool'),
        timeout=dict(type='int', default=30),
        tpmstate0=dict(type='dict',
                       options=dict(
                           storage=dict(type='str', required=True),
                           version=dict(type='str', choices=['2.0', '1.2'], default='2.0')
                       )),
        usb=dict(type='dict'),
        update=dict(type='bool', default=False),
        update_unsafe=dict(type='bool', default=False),
        vcpus=dict(type='int'),
        vga=dict(choices=['std', 'cirrus', 'vmware', 'qxl', 'serial0', 'serial1', 'serial2', 'serial3', 'qxl2', 'qxl3', 'qxl4']),
        virtio=dict(type='dict'),
        vmid=dict(type='int'),
        watchdog=dict(),
    )
    module_args.update(kvm_args)

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[('delete', 'revert'), ('delete', 'update'), ('revert', 'update'), ('clone', 'update'), ('clone', 'delete'), ('clone', 'revert')],
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('name', 'vmid'), ('api_password', 'api_token_id')],
        required_if=[('state', 'present', ['node'])],
    )

    clone = module.params['clone']
    cpu = module.params['cpu']
    cores = module.params['cores']
    delete = module.params['delete']
    migrate = module.params['migrate']
    memory = module.params['memory']
    name = module.params['name']
    newid = module.params['newid']
    node = module.params['node']
    revert = module.params['revert']
    sockets = module.params['sockets']
    state = module.params['state']
    update = bool(module.params['update'])
    update_unsafe = bool(module.params['update_unsafe'])
    vmid = module.params['vmid']
    validate_certs = module.params['validate_certs']

    if module.params['format'] == 'unspecified':
        module.params['format'] = None

    proxmox = ProxmoxKvmAnsible(module)

    # If vmid is not defined then retrieve its value from the vm name,
    # the cloned vm name or retrieve the next free VM id from ProxmoxAPI.
    if not vmid:
        if state == 'present' and not update and not clone and not delete and not revert and not migrate:
            existing_vmid = proxmox.get_vmid(name, ignore_missing=True)
            if existing_vmid:
                vmid = existing_vmid
            else:
                try:
                    vmid = proxmox.get_nextvmid()
                except Exception:
                    module.fail_json(msg="Can't get the next vmid for VM {0} automatically. Ensure your cluster state is good".format(name))
        else:
            clone_target = clone or name
            vmid = proxmox.get_vmid(clone_target, ignore_missing=True)

    if clone is not None:
        # If newid is not defined then retrieve the next free id from ProxmoxAPI
        if not newid:
            try:
                newid = proxmox.get_nextvmid()
            except Exception:
                module.fail_json(msg="Can't get the next vmid for VM {0} automatically. Ensure your cluster state is good".format(name))

        # Ensure source VM name exists when cloning
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % clone)

        # Ensure source VM id exists when cloning
        proxmox.get_vm(vmid)

        # Ensure the chosen VM name doesn't already exist when cloning
        existing_vmid = proxmox.get_vmid(name, ignore_missing=True)
        if existing_vmid:
            module.exit_json(changed=False, vmid=existing_vmid, msg="VM with name <%s> already exists" % name)

        # Ensure the chosen VM id doesn't already exist when cloning
        if proxmox.get_vm(newid, ignore_missing=True):
            module.exit_json(changed=False, vmid=vmid, msg="vmid %s with VM name %s already exists" % (newid, name))

    if delete is not None:
        try:
            proxmox.settings(vmid, node, delete=delete)
            module.exit_json(changed=True, vmid=vmid, msg="Settings has deleted on VM {0} with vmid {1}".format(name, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to delete settings on VM {0} with vmid {1}: '.format(name, vmid) + str(e))

    if revert is not None:
        try:
            proxmox.settings(vmid, node, revert=revert)
            module.exit_json(changed=True, vmid=vmid, msg="Settings has reverted on VM {0} with vmid {1}".format(name, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to revert settings on VM {0} with vmid {1}: Maybe is not a pending task...   '.format(name, vmid) + str(e))

    if migrate:
        try:
            vm = proxmox.get_vm(vmid)
            vm_node = vm['node']
            if node != vm_node:
                proxmox.migrate_vm(vm, node)
                module.exit_json(changed=True, vmid=vmid, msg="VM {0} has been migrated from {1} to {2}".format(vmid, vm_node, node))
            else:
                module.exit_json(changed=False, vmid=vmid, msg="VM {0} is already on {1}".format(vmid, node))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to migrate VM {0} from {1} to {2}: {3}'.format(vmid, vm_node, node, e))

    if state == 'present':
        if not (update or clone) and proxmox.get_vm(vmid, ignore_missing=True):
            module.exit_json(changed=False, vmid=vmid, msg="VM with vmid <%s> already exists" % vmid)
        elif not (update or clone or vmid) and proxmox.get_vmid(name, ignore_missing=True):
            module.exit_json(changed=False, vmid=proxmox.get_vmid(name), msg="VM with name <%s> already exists" % name)
        elif not node:
            module.fail_json(msg='node is mandatory for creating/updating VM')
        elif update and not any([vmid, name]):
            module.fail_json(msg='vmid or name is mandatory for updating VM')
        elif not proxmox.get_node(node):
            module.fail_json(msg="node '%s' does not exist in cluster" % node)

        try:
            proxmox.create_vm(vmid, newid, node, name, memory, cpu, cores, sockets, update, update_unsafe,
                              archive=module.params['archive'],
                              acpi=module.params['acpi'],
                              agent=module.params['agent'],
                              autostart=module.params['autostart'],
                              balloon=module.params['balloon'],
                              bios=module.params['bios'],
                              boot=module.params['boot'],
                              bootdisk=module.params['bootdisk'],
                              cicustom=module.params['cicustom'],
                              cipassword=module.params['cipassword'],
                              citype=module.params['citype'],
                              ciuser=module.params['ciuser'],
                              cpulimit=module.params['cpulimit'],
                              cpuunits=module.params['cpuunits'],
                              description=module.params['description'],
                              digest=module.params['digest'],
                              efidisk0=module.params['efidisk0'],
                              force=module.params['force'],
                              freeze=module.params['freeze'],
                              hookscript=module.params['hookscript'],
                              hostpci=module.params['hostpci'],
                              hotplug=module.params['hotplug'],
                              hugepages=module.params['hugepages'],
                              ide=module.params['ide'],
                              ipconfig=module.params['ipconfig'],
                              keyboard=module.params['keyboard'],
                              kvm=module.params['kvm'],
                              localtime=module.params['localtime'],
                              lock=module.params['lock'],
                              machine=module.params['machine'],
                              migrate_downtime=module.params['migrate_downtime'],
                              migrate_speed=module.params['migrate_speed'],
                              net=module.params['net'],
                              numa=module.params['numa'],
                              numa_enabled=module.params['numa_enabled'],
                              onboot=module.params['onboot'],
                              ostype=module.params['ostype'],
                              parallel=module.params['parallel'],
                              pool=module.params['pool'],
                              protection=module.params['protection'],
                              reboot=module.params['reboot'],
                              sata=module.params['sata'],
                              scsi=module.params['scsi'],
                              scsihw=module.params['scsihw'],
                              serial=module.params['serial'],
                              shares=module.params['shares'],
                              skiplock=module.params['skiplock'],
                              smbios1=module.params['smbios'],
                              snapname=module.params['snapname'],
                              sshkeys=module.params['sshkeys'],
                              startdate=module.params['startdate'],
                              startup=module.params['startup'],
                              tablet=module.params['tablet'],
                              tags=module.params['tags'],
                              target=module.params['target'],
                              tdf=module.params['tdf'],
                              template=module.params['template'],
                              tpmstate0=module.params['tpmstate0'],
                              usb=module.params['usb'],
                              vcpus=module.params['vcpus'],
                              vga=module.params['vga'],
                              virtio=module.params['virtio'],
                              watchdog=module.params['watchdog'])

            if not clone:
                proxmox.get_vminfo(node, vmid,
                                   ide=module.params['ide'],
                                   net=module.params['net'],
                                   sata=module.params['sata'],
                                   scsi=module.params['scsi'],
                                   virtio=module.params['virtio'])
        except Exception as e:
            if update:
                module.fail_json(vmid=vmid, msg="Unable to update vm {0} with vmid {1}=".format(name, vmid) + str(e))
            elif clone is not None:
                module.fail_json(vmid=vmid, msg="Unable to clone vm {0} from vmid {1}=".format(name, vmid) + str(e))
            else:
                module.fail_json(vmid=vmid, msg="creation of qemu VM %s with vmid %s failed with exception=%s" % (name, vmid, e))

        if update:
            module.exit_json(changed=True, vmid=vmid, msg="VM %s with vmid %s updated" % (name, vmid))
        elif clone is not None:
            module.exit_json(changed=True, vmid=newid, msg="VM %s with newid %s cloned from vm with vmid %s" % (name, newid, vmid))
        else:
            module.exit_json(changed=True, msg="VM %s with vmid %s deployed" % (name, vmid), **results)

    elif state == 'started':
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % name)

        status = {}
        try:
            vm = proxmox.get_vm(vmid)
            current = proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).status.current.get()['status']
            status['status'] = current
            if current == 'running':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is already running" % vmid, **status)

            if proxmox.start_vm(vm):
                module.exit_json(changed=True, vmid=vmid, msg="VM %s started" % vmid, **status)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="starting of VM %s failed with exception: %s" % (vmid, e), **status)

    elif state == 'stopped':
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % name)

        status = {}
        try:
            vm = proxmox.get_vm(vmid)
            current = proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).status.current.get()['status']
            status['status'] = current
            if current == 'stopped':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is already stopped" % vmid, **status)

            proxmox.stop_vm(vm, force=module.params['force'], timeout=module.params['timeout'])
            module.exit_json(changed=True, vmid=vmid, msg="VM %s is shutting down" % vmid, **status)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="stopping of VM %s failed with exception: %s" % (vmid, e), **status)

    elif state == 'template':
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % name)

        status = {}
        try:
            vm = proxmox.get_vm(vmid)

            if vm['template'] == 1:
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is already a template" % vmid, **status)

            if proxmox.convert_to_template(vm, force=module.params['force'], timeout=module.params['timeout']):
                module.exit_json(changed=True, vmid=vmid, msg="VM %s is converting to template" % vmid, **status)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="conversion of VM %s to template failed with exception: %s" % (vmid, e), **status)

    elif state == 'restarted':
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % name)

        status = {}
        vm = proxmox.get_vm(vmid)
        current = proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).status.current.get()['status']
        status['status'] = current
        if current == 'stopped':
            module.exit_json(changed=False, vmid=vmid, msg="VM %s is not running" % vmid, **status)

        if proxmox.restart_vm(vm, force=module.params['force']):
            module.exit_json(changed=True, vmid=vmid, msg="VM %s is restarted" % vmid, **status)

    elif state == 'absent':
        status = {}
        if not vmid:
            module.exit_json(changed=False, msg='VM with name = %s is already absent' % name)

        try:
            vm = proxmox.get_vm(vmid, ignore_missing=True)
            if not vm:
                module.exit_json(changed=False, vmid=vmid)

            proxmox_node = proxmox.proxmox_api.nodes(vm['node'])
            current = proxmox_node.qemu(vmid).status.current.get()['status']
            status['status'] = current
            if current == 'running':
                if module.params['force']:
                    proxmox.stop_vm(vm, True, timeout=module.params['timeout'])
                else:
                    module.exit_json(changed=False, vmid=vmid, msg="VM %s is running. Stop it before deletion or use force=true." % vmid)
            taskid = proxmox_node.qemu.delete(vmid)
            if not proxmox.wait_for_task(vm['node'], taskid):
                module.fail_json(msg='Reached timeout while waiting for removing VM. Last line in task before timeout: %s' %
                                 proxmox_node.tasks(taskid).log.get()[:1])
            else:
                module.exit_json(changed=True, vmid=vmid, msg="VM %s removed" % vmid)
        except Exception as e:
            module.fail_json(msg="deletion of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'current':
        status = {}
        if not vmid:
            module.fail_json(msg='VM with name = %s does not exist in cluster' % name)
        vm = proxmox.get_vm(vmid)
        if not name:
            name = vm.get('name', '(unnamed)')
        current = proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).status.current.get()['status']
        status['status'] = current
        if status:
            module.exit_json(changed=False, vmid=vmid, msg="VM %s with vmid = %s is %s" % (name, vmid, current), **status)


if __name__ == '__main__':
    main()
