#!/usr/bin/python

# Copyright 2012 Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: hpilo_boot
author: Dag Wieers (@dagwieers)
short_description: Boot system using specific media through HP iLO interface
description:
  - 'This module boots a system through its HP iLO interface. The boot media can be one of: V(cdrom), V(floppy), V(hdd), V(network),
    or V(usb).'
  - This module requires the hpilo python module.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  host:
    description:
      - The HP iLO hostname/address that is linked to the physical system.
    type: str
    required: true
  login:
    description:
      - The login name to authenticate to the HP iLO interface.
    default: Administrator
    type: str
  password:
    description:
      - The password to authenticate to the HP iLO interface.
    default: admin
    type: str
  media:
    description:
      - The boot media to boot the system from.
    choices: ["cdrom", "floppy", "rbsu", "hdd", "network", "normal", "usb"]
    type: str
  image:
    description:
      - The URL of a cdrom, floppy or usb boot media image in the form V(protocol://username:password@hostname:port/filename).
      - V(protocol) is either V(http) or V(https).
      - V(username:password) is optional.
      - V(port) is optional.
    type: str
  state:
    description:
      - The state of the boot media.
      - 'V(no_boot): Do not boot from the device.'
      - 'V(boot_once): Boot from the device once and then notthereafter.'
      - 'V(boot_always): Boot from the device each time the server is rebooted.'
      - 'V(connect): Connect the virtual media device and set to boot_always.'
      - 'V(disconnect): Disconnects the virtual media device and set to no_boot.'
      - 'V(poweroff): Power off the server.'
    default: boot_once
    type: str
    choices: ["boot_always", "boot_once", "connect", "disconnect", "no_boot", "poweroff"]
  force:
    description:
      - Whether to force a reboot (even when the system is already booted).
      - As a safeguard, without force, M(community.general.hpilo_boot) refuses to reboot a server that is already running.
    default: false
    type: bool
  ssl_version:
    description:
      - Change the ssl_version used.
    default: TLSv1
    type: str
    choices: ["SSLv3", "SSLv23", "TLSv1", "TLSv1_1", "TLSv1_2"]
  idempotent_boot_once:
    description:
      - This option makes O(state=boot_once) succeed instead of failing when the server is already powered on.
    type: bool
    default: false
    version_added: 10.6.0
requirements:
  - python-hpilo
notes:
  - To use a USB key image you need to specify floppy as boot media.
  - This module ought to be run from a system that can access the HP iLO interface directly, either by using C(local_action)
    or using C(delegate_to).
"""

EXAMPLES = r"""
- name: Task to boot a system using an ISO from an HP iLO interface only if the system is an HP server
  community.general.hpilo_boot:
    host: YOUR_ILO_ADDRESS
    login: YOUR_ILO_LOGIN
    password: YOUR_ILO_PASSWORD
    media: cdrom
    image: http://some-web-server/iso/boot.iso
  when: cmdb_hwmodel.startswith('HP ')
  delegate_to: localhost

- name: Power off a server
  community.general.hpilo_boot:
    host: YOUR_ILO_HOST
    login: YOUR_ILO_LOGIN
    password: YOUR_ILO_PASSWORD
    state: poweroff
  delegate_to: localhost
"""

RETURN = r"""
# Default return values
"""

import time
import traceback
import warnings

HPILO_IMP_ERR = None
try:
    import hpilo

    HAS_HPILO = True
except ImportError:
    HPILO_IMP_ERR = traceback.format_exc()
    HAS_HPILO = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


# Suppress warnings from hpilo
warnings.simplefilter("ignore")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type="str", required=True),
            login=dict(type="str", default="Administrator"),
            password=dict(type="str", default="admin", no_log=True),
            media=dict(type="str", choices=["cdrom", "floppy", "rbsu", "hdd", "network", "normal", "usb"]),
            image=dict(type="str"),
            state=dict(
                type="str",
                default="boot_once",
                choices=["boot_always", "boot_once", "connect", "disconnect", "no_boot", "poweroff"],
            ),
            force=dict(type="bool", default=False),
            idempotent_boot_once=dict(type="bool", default=False),
            ssl_version=dict(type="str", default="TLSv1", choices=["SSLv3", "SSLv23", "TLSv1", "TLSv1_1", "TLSv1_2"]),
        )
    )

    if not HAS_HPILO:
        module.fail_json(msg=missing_required_lib("python-hpilo"), exception=HPILO_IMP_ERR)

    host = module.params["host"]
    login = module.params["login"]
    password = module.params["password"]
    media = module.params["media"]
    image = module.params["image"]
    state = module.params["state"]
    force = module.params["force"]
    idempotent_boot_once = module.params["idempotent_boot_once"]
    ssl_version = getattr(hpilo.ssl, f"PROTOCOL_{module.params.get('ssl_version').upper().replace('V', 'v')}")

    ilo = hpilo.Ilo(host, login=login, password=password, ssl_version=ssl_version)
    changed = False
    status = {}
    power_status = "UNKNOWN"

    if media and state in ("boot_always", "boot_once", "connect", "disconnect", "no_boot"):
        # Workaround for: Error communicating with iLO: Problem manipulating EV
        try:
            ilo.set_one_time_boot(media)
        except hpilo.IloError:
            time.sleep(60)
            ilo.set_one_time_boot(media)

        # TODO: Verify if image URL exists/works
        if image:
            ilo.insert_virtual_media(media, image)
            changed = True

        if media == "cdrom":
            ilo.set_vm_status("cdrom", state, True)
            status = ilo.get_vm_status()
            changed = True
        elif media in ("floppy", "usb"):
            ilo.set_vf_status(state, True)
            status = ilo.get_vf_status()
            changed = True

    # Only perform a boot when state is boot_once or boot_always, or in case we want to force a reboot
    if state in ("boot_once", "boot_always") or force:
        power_status = ilo.get_host_power_status()

        if power_status == "ON":
            if not force and not idempotent_boot_once:
                # module.deprecate(
                #     'The failure of the module when the server is already powered on is being deprecated.'
                #     ' Please set the parameter "idempotent_boot_once=true" to start using the new behavior.',
                #     version='11.0.0',
                #     collection_name='community.general'
                # )
                module.fail_json(msg=f"HP iLO ({host}) reports that the server is already powered on !")
            elif not force and idempotent_boot_once:
                pass
            elif force:
                ilo.warm_boot_server()
                #            ilo.cold_boot_server()
                changed = True
        else:
            ilo.press_pwr_btn()
            #            ilo.reset_server()
            #            ilo.set_host_power(host_power=True)
            changed = True

    elif state in ("poweroff"):
        power_status = ilo.get_host_power_status()

        if power_status != "OFF":
            ilo.hold_pwr_btn()
            #            ilo.set_host_power(host_power=False)
            changed = True

    module.exit_json(changed=changed, power=power_status, **status)


if __name__ == "__main__":
    main()
