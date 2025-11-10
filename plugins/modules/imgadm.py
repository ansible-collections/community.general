#!/usr/bin/python

# Copyright (c) 2016, 2017 Jasper Lievisse Adriaanse <j@jasper.la>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: imgadm
short_description: Manage SmartOS images
description:
  - Manage SmartOS virtual machine images through imgadm(8).
author: Jasper Lievisse Adriaanse (@jasperla)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  force:
    type: bool
    description:
      - Force a given operation (where supported by imgadm(8)).
  pool:
    default: zones
    description:
      - The zpool to import to or delete images from.
    type: str
  source:
    description:
      - URI for the image source.
    type: str
  state:
    required: true
    choices: [present, absent, deleted, imported, updated, vacuumed]
    description:
      - State the object operated on should be in. V(imported) is an alias for for V(present) and V(deleted) for V(absent).
        When set to V(vacuumed) and O(uuid=*), it removes all unused images.
    type: str

  type:
    choices: [imgapi, docker, dsapi]
    default: imgapi
    description:
      - Type for image sources.
    type: str

  uuid:
    description:
      - Image UUID. Can either be a full UUID or V(*) for all images.
    type: str
seealso:
  - name: imgadm(8)
    description: Complete manual page for the command C(imgadm).
    link: https://smartos.org/man/8/imgadm
"""

EXAMPLES = r"""
- name: Import an image
  community.general.imgadm:
    uuid: '70e3ae72-96b6-11e6-9056-9737fd4d0764'
    state: imported

- name: Delete an image
  community.general.imgadm:
    uuid: '70e3ae72-96b6-11e6-9056-9737fd4d0764'
    state: deleted

- name: Update all images
  community.general.imgadm:
    uuid: '*'
    state: updated

- name: Update a single image
  community.general.imgadm:
    uuid: '70e3ae72-96b6-11e6-9056-9737fd4d0764'
    state: updated

- name: Add a source
  community.general.imgadm:
    source: 'https://datasets.project-fifo.net'
    state: present

- name: Add a Docker source
  community.general.imgadm:
    source: 'https://docker.io'
    type: docker
    state: present

- name: Remove a source
  community.general.imgadm:
    source: 'https://docker.io'
    state: absent
"""

RETURN = r"""
source:
  description: Source that is managed.
  returned: When not managing an image.
  type: str
  sample: https://datasets.project-fifo.net
uuid:
  description: UUID for an image operated on.
  returned: When not managing an image source.
  type: str
  sample: 70e3ae72-96b6-11e6-9056-9737fd4d0764
state:
  description: State of the target, after execution.
  returned: success
  type: str
  sample: 'present'
"""

import re

from ansible.module_utils.basic import AnsibleModule

# Shortcut for the imgadm(8) command. While imgadm(8) supports a
# -E option to return any errors in JSON, the generated JSON does not play well
# with the JSON parsers of Python. The returned message contains '\n' as part of
# the stacktrace, which breaks the parsers.


class Imgadm:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.cmd = module.get_bin_path("imgadm", required=True)
        self.changed = False
        self.uuid = module.params["uuid"]

        # Since there are a number of (natural) aliases, prevent having to look
        # them up every time we operate on `state`.
        if self.params["state"] in ["present", "imported", "updated"]:
            self.present = True
        else:
            self.present = False

        # Perform basic UUID validation upfront.
        if self.uuid and self.uuid != "*":
            if not re.match("^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$", self.uuid, re.IGNORECASE):
                module.fail_json(msg="Provided value for uuid option is not a valid UUID.")

    # Helper method to massage stderr
    def errmsg(self, stderr):
        match = re.match(r"^imgadm .*?: error \(\w+\): (.*): .*", stderr)
        if match:
            return match.groups()[0]
        else:
            return "Unexpected failure"

    def update_images(self):
        if self.uuid == "*":
            cmd = [self.cmd, "update"]
        else:
            cmd = [self.cmd, "update", self.uuid]

        (rc, stdout, stderr) = self.module.run_command(cmd)

        if rc != 0:
            self.module.fail_json(msg=f"Failed to update images: {self.errmsg(stderr)}")

        # There is no feedback from imgadm(8) to determine if anything
        # was actually changed. So treat this as an 'always-changes' operation.
        # Note that 'imgadm -v' produces unparsable JSON...
        self.changed = True

    def manage_sources(self):
        force = self.params["force"]
        source = self.params["source"]
        imgtype = self.params["type"]

        cmd = [self.cmd, "sources"]

        if force:
            cmd = cmd + ["-f"]

        if self.present:
            cmd = cmd + ["-a", source, "-t", imgtype]
            (rc, stdout, stderr) = self.module.run_command(cmd)

            if rc != 0:
                self.module.fail_json(msg=f"Failed to add source: {self.errmsg(stderr)}")

            # Check the various responses.
            # Note that trying to add a source with the wrong type is handled
            # above as it results in a non-zero status.

            regex = f'Already have "{imgtype}" image source "{source}", no change'
            if re.match(regex, stdout):
                self.changed = False

            regex = f'Added "{imgtype}" image source "{source}"'
            if re.match(regex, stdout):
                self.changed = True
        else:
            # Type is ignored by imgadm(8) here
            cmd += f" -d {source}"
            (rc, stdout, stderr) = self.module.run_command(cmd)

            if rc != 0:
                self.module.fail_json(msg=f"Failed to remove source: {self.errmsg(stderr)}")

            regex = f'Do not have image source "{source}", no change'
            if re.match(regex, stdout):
                self.changed = False

            regex = f'Deleted ".*" image source "{source}"'
            if re.match(regex, stdout):
                self.changed = True

    def manage_images(self):
        pool = self.params["pool"]
        state = self.params["state"]

        if state == "vacuumed":
            # Unconditionally pass '--force', otherwise we're prompted with 'y/N'
            cmd = [self.cmd, "vacuum", "-f"]

            (rc, stdout, stderr) = self.module.run_command(cmd)

            if rc != 0:
                self.module.fail_json(msg=f"Failed to vacuum images: {self.errmsg(stderr)}")
            else:
                if stdout == "":
                    self.changed = False
                else:
                    self.changed = True
        if self.present:
            cmd = [self.cmd, "import", "-P", pool, "-q"] + ([self.uuid] if self.uuid else [])
            (rc, stdout, stderr) = self.module.run_command(cmd)

            if rc != 0:
                self.module.fail_json(msg=f"Failed to import image: {self.errmsg(stderr)}")

            regex = rf"Image {self.uuid} \(.*\) is already installed, skipping"
            if re.match(regex, stdout):
                self.changed = False

            regex = ".*ActiveImageNotFound.*"
            if re.match(regex, stderr):
                self.changed = False

            regex = f"Imported image {self.uuid}.*"
            if re.match(regex, stdout.splitlines()[-1]):
                self.changed = True
        else:
            cmd = [self.cmd, "delete", "-P", pool] + ([self.uuid] if self.uuid else [])
            (rc, stdout, stderr) = self.module.run_command(cmd)

            regex = ".*ImageNotInstalled.*"
            if re.match(regex, stderr):
                # Even if the 'rc' was non-zero (3), we handled the situation
                # in order to determine if there was a change.
                self.changed = False

            regex = f"Deleted image {self.uuid}"
            if re.match(regex, stdout):
                self.changed = True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            force=dict(type="bool"),
            pool=dict(default="zones"),
            source=dict(),
            state=dict(required=True, choices=["present", "absent", "deleted", "imported", "updated", "vacuumed"]),
            type=dict(default="imgapi", choices=["imgapi", "docker", "dsapi"]),
            uuid=dict(),
        ),
        # This module relies largely on imgadm(8) to enforce idempotency, which does not
        # provide a "noop" (or equivalent) mode to do a dry-run.
        supports_check_mode=False,
    )

    imgadm = Imgadm(module)

    uuid = module.params["uuid"]
    source = module.params["source"]
    state = module.params["state"]

    result = {"state": state}

    # Either manage sources or images.
    if source:
        result["source"] = source
        imgadm.manage_sources()
    else:
        result["uuid"] = uuid

        if state == "updated":
            imgadm.update_images()
        else:
            # Make sure operate on a single image for the following actions
            if (uuid == "*") and (state != "vacuumed"):
                module.fail_json(msg='Can only specify uuid as "*" when updating image(s)')
            imgadm.manage_images()

    result["changed"] = imgadm.changed
    module.exit_json(**result)


if __name__ == "__main__":
    main()
