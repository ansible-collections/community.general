#!/usr/bin/python

# Copyright (c) 2022, Gregory Furlong <gnfzdz@fzdz.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: btrfs_subvolume
short_description: Manage btrfs subvolumes
version_added: "6.6.0"

description: Creates, updates and deletes btrfs subvolumes and snapshots.

options:
  automount:
    description:
      - Allow the module to temporarily mount the targeted btrfs filesystem in order to validate the current state and make
        any required changes.
    type: bool
    default: false
  default:
    description:
      - Make the subvolume specified by O(name) the filesystem's default subvolume.
    type: bool
    default: false
  filesystem_device:
    description:
      - A block device contained within the btrfs filesystem to be targeted.
      - Useful when multiple btrfs filesystems are present to specify which filesystem should be targeted.
    type: path
  filesystem_label:
    description:
      - A descriptive label assigned to the btrfs filesystem to be targeted.
      - Useful when multiple btrfs filesystems are present to specify which filesystem should be targeted.
    type: str
  filesystem_uuid:
    description:
      - A unique identifier assigned to the btrfs filesystem to be targeted.
      - Useful when multiple btrfs filesystems are present to specify which filesystem should be targeted.
    type: str
  name:
    description:
      - Name of the subvolume/snapshot to be targeted.
    required: true
    type: str
  recursive:
    description:
      - When true, indicates that parent/child subvolumes should be created/removedas necessary to complete the operation
        (for O(state=present) and O(state=absent) respectively).
    type: bool
    default: false
  snapshot_source:
    description:
      - Identifies the source subvolume for the created snapshot.
      - Infers that the created subvolume is a snapshot.
    type: str
  snapshot_conflict:
    description:
      - Policy defining behavior when a subvolume already exists at the path of the requested snapshot.
      - V(skip) - Create a snapshot only if a subvolume does not yet exist at the target location, otherwise indicate that
        no change is required. Warning, this option does not yet verify that the target subvolume was generated from a snapshot
        of the requested source.
      - V(clobber) - If a subvolume already exists at the requested location, delete it first. This option is not idempotent
        and results in a new snapshot being generated on every execution.
      - V(error) - If a subvolume already exists at the requested location, return an error. This option is not idempotent
        and results in an error on replay of the module.
    type: str
    choices: [skip, clobber, error]
    default: skip
  state:
    description:
      - Indicates the current state of the targeted subvolume.
    type: str
    choices: [absent, present]
    default: present

notes:
  - If any or all of the options O(filesystem_device), O(filesystem_label) or O(filesystem_uuid) parameters are provided,
    there is expected to be a matching btrfs filesystem. If none are provided and only a single btrfs filesystem exists or
    only a single btrfs filesystem is mounted, that filesystem is used; otherwise, the module takes no action and returns an
    error.
extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: partial
    details:
      - In some scenarios it may erroneously report intermediate subvolumes being created. After mounting, if a directory
        like file is found where the subvolume would have been created, the operation is skipped.
  diff_mode:
    support: none

author:
  - Gregory Furlong (@gnfzdz)
"""

EXAMPLES = r"""
- name: Create a @home subvolume under the root subvolume
  community.general.btrfs_subvolume:
    name: /@home
    filesystem_device: /dev/vda2

- name: Remove the @home subvolume if it exists
  community.general.btrfs_subvolume:
    name: /@home
    state: absent
    filesystem_device: /dev/vda2

- name: Create a snapshot of the root subvolume named @
  community.general.btrfs_subvolume:
    name: /@
    snapshot_source: /
    filesystem_device: /dev/vda2

- name: Create a snapshot of the root subvolume and make it the new default subvolume
  community.general.btrfs_subvolume:
    name: /@
    snapshot_source: /
    default: true
    filesystem_device: /dev/vda2

- name: Create a snapshot of the /@ subvolume and recursively creating intermediate subvolumes as required
  community.general.btrfs_subvolume:
    name: /@snapshots/@2022_06_09
    snapshot_source: /@
    recursive: true
    filesystem_device: /dev/vda2

- name: Remove the /@ subvolume and recursively delete child subvolumes as required
  community.general.btrfs_subvolume:
    name: /@snapshots/@2022_06_09
    snapshot_source: /@
    recursive: true
    filesystem_device: /dev/vda2
"""

RETURN = r"""
filesystem:
  description:
    - A summary of the final state of the targeted btrfs filesystem.
  type: dict
  returned: success
  contains:
    uuid:
      description: A unique identifier assigned to the filesystem.
      returned: success
      type: str
      sample: 96c9c605-1454-49b8-a63a-15e2584c208e
    label:
      description: An optional label assigned to the filesystem.
      returned: success
      type: str
      sample: Tank
    devices:
      description: A list of devices assigned to the filesystem.
      returned: success
      type: list
      sample:
        - /dev/sda1
        - /dev/sdb1
    default_subvolume:
      description: The ID of the filesystem's default subvolume.
      returned: success and if filesystem is mounted
      type: int
      sample: 5
    subvolumes:
      description: A list of dicts containing metadata for all of the filesystem's subvolumes.
      returned: success and if filesystem is mounted
      type: list
      elements: dict
      contains:
        id:
          description: An identifier assigned to the subvolume, unique within the containing filesystem.
          type: int
          sample: 256
        mountpoints:
          description: Paths where the subvolume is mounted on the targeted host.
          type: list
          sample: ["/home"]
        parent:
          description: The identifier of this subvolume's parent.
          type: int
          sample: 5
        path:
          description: The full path of the subvolume relative to the btrfs fileystem's root.
          type: str
          sample: /@home

modifications:
  description:
    - A list where each element describes a change made to the target btrfs filesystem.
  type: list
  returned: Success
  elements: str

target_subvolume_id:
  description:
    - The ID of the subvolume specified with the O(name) parameter, either pre-existing or created as part of module execution.
  type: int
  sample: 257
  returned: Success and subvolume exists after module execution
"""

from ansible_collections.community.general.plugins.module_utils.btrfs import (
    BtrfsFilesystemsProvider,
    BtrfsCommands,
    BtrfsModuleException,
)
from ansible_collections.community.general.plugins.module_utils.btrfs import normalize_subvolume_path
from ansible.module_utils.basic import AnsibleModule
import os
import tempfile


class BtrfsSubvolumeModule:
    __BTRFS_ROOT_SUBVOLUME = "/"
    __BTRFS_ROOT_SUBVOLUME_ID = 5
    __BTRFS_SUBVOLUME_INODE_NUMBER = 256

    __CREATE_SUBVOLUME_OPERATION = "create"
    __CREATE_SNAPSHOT_OPERATION = "snapshot"
    __DELETE_SUBVOLUME_OPERATION = "delete"
    __SET_DEFAULT_SUBVOLUME_OPERATION = "set-default"

    __UNKNOWN_SUBVOLUME_ID = "?"

    def __init__(self, module):
        self.module = module
        self.__btrfs_api = BtrfsCommands(module)
        self.__provider = BtrfsFilesystemsProvider(module)

        #  module parameters
        name = self.module.params["name"]
        self.__name = normalize_subvolume_path(name) if name is not None else None
        self.__state = self.module.params["state"]

        self.__automount = self.module.params["automount"]
        self.__default = self.module.params["default"]
        self.__filesystem_device = self.module.params["filesystem_device"]
        self.__filesystem_label = self.module.params["filesystem_label"]
        self.__filesystem_uuid = self.module.params["filesystem_uuid"]
        self.__recursive = self.module.params["recursive"]
        self.__snapshot_conflict = self.module.params["snapshot_conflict"]
        snapshot_source = self.module.params["snapshot_source"]
        self.__snapshot_source = normalize_subvolume_path(snapshot_source) if snapshot_source is not None else None

        # execution state
        self.__filesystem = None
        self.__required_mounts = []
        self.__unit_of_work = []
        self.__completed_work = []
        self.__temporary_mounts = dict()

    def run(self):
        error = None
        try:
            self.__load_filesystem()
            self.__prepare_unit_of_work()

            if not self.module.check_mode:
                # check required mounts & mount
                if len(self.__unit_of_work) > 0:
                    self.__execute_unit_of_work()
                    self.__filesystem.refresh()
            else:
                # check required mounts
                self.__completed_work.extend(self.__unit_of_work)
        except Exception as e:
            error = e
        finally:
            self.__cleanup_mounts()
            if self.__filesystem is not None:
                self.__filesystem.refresh_mountpoints()

        return (error, self.get_results())

    # Identify the targeted filesystem and obtain the current state
    def __load_filesystem(self):
        if self.__has_filesystem_criteria():
            filesystem = self.__find_matching_filesytem()
        else:
            filesystem = self.__find_default_filesystem()

        # The filesystem must be mounted to obtain the current state (subvolumes, default, etc)
        if not filesystem.is_mounted():
            if not self.__automount:
                raise BtrfsModuleException(
                    f"Target filesystem uuid={filesystem.uuid} is not currently mounted and automount=False."
                    "Mount explicitly before module execution or pass automount=True"
                )
            elif self.module.check_mode:
                # TODO is failing the module an appropriate outcome in this scenario?
                raise BtrfsModuleException(
                    f"Target filesystem uuid={filesystem.uuid} is not currently mounted. Unable to validate the current"
                    "state while running with check_mode=True"
                )
            else:
                self.__mount_subvolume_id_to_tempdir(filesystem, self.__BTRFS_ROOT_SUBVOLUME_ID)
                filesystem.refresh()
        self.__filesystem = filesystem

    def __has_filesystem_criteria(self):
        return (
            self.__filesystem_uuid is not None
            or self.__filesystem_label is not None
            or self.__filesystem_device is not None
        )

    def __find_matching_filesytem(self):
        criteria = {
            "uuid": self.__filesystem_uuid,
            "label": self.__filesystem_label,
            "device": self.__filesystem_device,
        }
        return self.__provider.get_matching_filesystem(criteria)

    def __find_default_filesystem(self):
        filesystems = self.__provider.get_filesystems()
        filesystem = None

        if len(filesystems) == 1:
            filesystem = filesystems[0]
        else:
            mounted_filesystems = [x for x in filesystems if x.is_mounted()]
            if len(mounted_filesystems) == 1:
                filesystem = mounted_filesystems[0]

        if filesystem is not None:
            return filesystem
        else:
            raise BtrfsModuleException(
                f"Failed to automatically identify targeted filesystem. No explicit device indicated and found {len(filesystems)} available filesystems."
            )

    # Prepare unit of work
    def __prepare_unit_of_work(self):
        if self.__state == "present":
            if self.__snapshot_source is None:
                self.__prepare_subvolume_present()
            else:
                self.__prepare_snapshot_present()

            if self.__default:
                self.__prepare_set_default()
        elif self.__state == "absent":
            self.__prepare_subvolume_absent()

    def __prepare_subvolume_present(self):
        subvolume = self.__filesystem.get_subvolume_by_name(self.__name)
        if subvolume is None:
            self.__prepare_before_create_subvolume(self.__name)
            self.__stage_create_subvolume(self.__name)

    def __prepare_before_create_subvolume(self, subvolume_name):
        closest_parent = self.__filesystem.get_nearest_subvolume(subvolume_name)
        self.__stage_required_mount(closest_parent)
        if self.__recursive:
            self.__prepare_create_intermediates(closest_parent, subvolume_name)

    def __prepare_create_intermediates(self, closest_subvolume, subvolume_name):
        relative_path = closest_subvolume.get_child_relative_path(self.__name)
        missing_subvolumes = [x for x in relative_path.split(os.path.sep) if len(x) > 0]
        if len(missing_subvolumes) > 1:
            current = closest_subvolume.path
            for s in missing_subvolumes[:-1]:
                separator = os.path.sep if current[-1] != os.path.sep else ""
                current = current + separator + s
                self.__stage_create_subvolume(current, True)

    def __prepare_snapshot_present(self):
        source_subvolume = self.__filesystem.get_subvolume_by_name(self.__snapshot_source)
        subvolume = self.__filesystem.get_subvolume_by_name(self.__name)
        subvolume_exists = subvolume is not None

        if subvolume_exists:
            if self.__snapshot_conflict == "skip":
                # No change required
                return
            elif self.__snapshot_conflict == "error":
                raise BtrfsModuleException(
                    f"Target subvolume={self.__name} already exists and snapshot_conflict='error'"
                )

        if source_subvolume is None:
            raise BtrfsModuleException(f"Source subvolume {self.__snapshot_source} does not exist")
        elif subvolume is not None and source_subvolume.id == subvolume.id:
            raise BtrfsModuleException("Snapshot source and target are the same.")
        else:
            self.__stage_required_mount(source_subvolume)

        if subvolume_exists and self.__snapshot_conflict == "clobber":
            self.__prepare_delete_subvolume_tree(subvolume)
        elif not subvolume_exists:
            self.__prepare_before_create_subvolume(self.__name)

        self.__stage_create_snapshot(source_subvolume, self.__name)

    def __prepare_subvolume_absent(self):
        subvolume = self.__filesystem.get_subvolume_by_name(self.__name)
        if subvolume is not None:
            self.__prepare_delete_subvolume_tree(subvolume)

    def __prepare_delete_subvolume_tree(self, subvolume):
        if subvolume.is_filesystem_root():
            raise BtrfsModuleException("Can not delete the filesystem's root subvolume")
        if not self.__recursive and len(subvolume.get_child_subvolumes()) > 0:
            raise BtrfsModuleException(
                f"Subvolume targeted for deletion {subvolume.path} has children and recursive=False."
                "Either explicitly delete the child subvolumes first or pass "
                "parameter recursive=True."
            )

        self.__stage_required_mount(subvolume.get_parent_subvolume())
        queue = self.__prepare_recursive_delete_order(subvolume) if self.__recursive else [subvolume]
        # prepare unit of work
        for s in queue:
            if s.is_mounted():
                # TODO potentially unmount the subvolume if automount=True ?
                raise BtrfsModuleException(f"Can not delete mounted subvolume={s.path}")
            if s.is_filesystem_default():
                self.__stage_set_default_subvolume(self.__BTRFS_ROOT_SUBVOLUME, self.__BTRFS_ROOT_SUBVOLUME_ID)
            self.__stage_delete_subvolume(s)

    def __prepare_recursive_delete_order(self, subvolume):
        """Return the subvolume and all descendents as a list, ordered so that descendents always occur before their ancestors"""
        pending = [subvolume]
        ordered = []
        while len(pending) > 0:
            next = pending.pop()
            ordered.append(next)
            pending.extend(next.get_child_subvolumes())
        ordered.reverse()  # reverse to ensure children are deleted before their parent
        return ordered

    def __prepare_set_default(self):
        subvolume = self.__filesystem.get_subvolume_by_name(self.__name)
        subvolume_id = subvolume.id if subvolume is not None else None

        if self.__filesystem.default_subvolid != subvolume_id:
            self.__stage_set_default_subvolume(self.__name, subvolume_id)

    # Stage operations to the unit of work
    def __stage_required_mount(self, subvolume):
        if subvolume.get_mounted_path() is None:
            if self.__automount:
                self.__required_mounts.append(subvolume)
            else:
                raise BtrfsModuleException(
                    f"The requested changes will require the subvolume '{subvolume.path}' to be mounted, but automount=False"
                )

    def __stage_create_subvolume(self, subvolume_path, intermediate=False):
        """
        Add required creation of an intermediate subvolume to the unit of work
        If intermediate is true, the action will be skipped if a directory like file is found at target
        after mounting a parent subvolume
        """
        self.__unit_of_work.append(
            {
                "action": self.__CREATE_SUBVOLUME_OPERATION,
                "target": subvolume_path,
                "intermediate": intermediate,
            }
        )

    def __stage_create_snapshot(self, source_subvolume, target_subvolume_path):
        """Add creation of a snapshot from source to target to the unit of work"""
        self.__unit_of_work.append(
            {
                "action": self.__CREATE_SNAPSHOT_OPERATION,
                "source": source_subvolume.path,
                "source_id": source_subvolume.id,
                "target": target_subvolume_path,
            }
        )

    def __stage_delete_subvolume(self, subvolume):
        """Add deletion of the target subvolume to the unit of work"""
        self.__unit_of_work.append(
            {
                "action": self.__DELETE_SUBVOLUME_OPERATION,
                "target": subvolume.path,
                "target_id": subvolume.id,
            }
        )

    def __stage_set_default_subvolume(self, subvolume_path, subvolume_id=None):
        """Add update of the filesystem's default subvolume to the unit of work"""
        self.__unit_of_work.append(
            {
                "action": self.__SET_DEFAULT_SUBVOLUME_OPERATION,
                "target": subvolume_path,
                "target_id": subvolume_id,
            }
        )

    # Execute the unit of work
    def __execute_unit_of_work(self):
        self.__check_required_mounts()
        for op in self.__unit_of_work:
            if op["action"] == self.__CREATE_SUBVOLUME_OPERATION:
                self.__execute_create_subvolume(op)
            elif op["action"] == self.__CREATE_SNAPSHOT_OPERATION:
                self.__execute_create_snapshot(op)
            elif op["action"] == self.__DELETE_SUBVOLUME_OPERATION:
                self.__execute_delete_subvolume(op)
            elif op["action"] == self.__SET_DEFAULT_SUBVOLUME_OPERATION:
                self.__execute_set_default_subvolume(op)
            else:
                raise ValueError(f"Unknown operation type '{op['action']}'")

    def __execute_create_subvolume(self, operation):
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation["target"])
        if not self.__is_existing_directory_like(target_mounted_path):
            self.__btrfs_api.subvolume_create(target_mounted_path)
            self.__completed_work.append(operation)

    def __execute_create_snapshot(self, operation):
        source_subvolume = self.__filesystem.get_subvolume_by_name(operation["source"])
        source_mounted_path = source_subvolume.get_mounted_path()
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation["target"])

        self.__btrfs_api.subvolume_snapshot(source_mounted_path, target_mounted_path)
        self.__completed_work.append(operation)

    def __execute_delete_subvolume(self, operation):
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation["target"])
        self.__btrfs_api.subvolume_delete(target_mounted_path)
        self.__completed_work.append(operation)

    def __execute_set_default_subvolume(self, operation):
        target = operation["target"]
        target_id = operation["target_id"]

        if target_id is None:
            target_subvolume = self.__filesystem.get_subvolume_by_name(target)

            if target_subvolume is None:
                self.__filesystem.refresh()  # the target may have been created earlier in module execution
                target_subvolume = self.__filesystem.get_subvolume_by_name(target)

            if target_subvolume is None:
                raise BtrfsModuleException(f"Failed to find existing subvolume '{target}'")
            else:
                target_id = target_subvolume.id

        self.__btrfs_api.subvolume_set_default(self.__filesystem.get_any_mountpoint(), target_id)
        self.__completed_work.append(operation)

    def __is_existing_directory_like(self, path):
        return os.path.exists(path) and (
            os.path.isdir(path) or os.stat(path).st_ino == self.__BTRFS_SUBVOLUME_INODE_NUMBER
        )

    def __check_required_mounts(self):
        filtered = self.__filter_child_subvolumes(self.__required_mounts)
        if len(filtered) > 0:
            for subvolume in filtered:
                self.__mount_subvolume_id_to_tempdir(self.__filesystem, subvolume.id)
            self.__filesystem.refresh_mountpoints()

    def __filter_child_subvolumes(self, subvolumes):
        """Filter the provided list of subvolumes to remove any that are a child of another item in the list"""
        filtered = []
        last = None
        ordered = sorted(subvolumes, key=lambda x: x.path)
        for next in ordered:
            if last is None or next.path[0 : len(last)] != last:
                filtered.append(next)
                last = next.path
        return filtered

    # Create/cleanup temporary mountpoints
    def __mount_subvolume_id_to_tempdir(self, filesystem, subvolid):
        # this check should be redundant
        if self.module.check_mode or not self.__automount:
            raise BtrfsModuleException(
                "Unable to temporarily mount required subvolumes"
                f" with automount={self.__automount} and check_mode={self.module.check_mode}"
            )

        cache_key = f"{filesystem.uuid}:{int(subvolid)}"
        # The subvolume was already mounted, so return the current path
        if cache_key in self.__temporary_mounts:
            return self.__temporary_mounts[cache_key]

        device = filesystem.devices[0]
        mountpoint = tempfile.mkdtemp(dir="/tmp")
        self.__temporary_mounts[cache_key] = mountpoint

        mount = self.module.get_bin_path("mount", required=True)
        command = [mount, "-o", f"noatime,subvolid={int(subvolid)}", device, mountpoint]
        self.module.run_command(command, check_rc=True)

        return mountpoint

    def __cleanup_mounts(self):
        for key in self.__temporary_mounts.keys():
            self.__cleanup_mount(self.__temporary_mounts[key])

    def __cleanup_mount(self, mountpoint):
        umount = self.module.get_bin_path("umount", required=True)
        result = self.module.run_command([umount, mountpoint])
        if result[0] == 0:
            rmdir = self.module.get_bin_path("rmdir", required=True)
            self.module.run_command([rmdir, mountpoint])

    # Format and return results
    def get_results(self):
        target = self.__filesystem.get_subvolume_by_name(self.__name)
        return dict(
            changed=len(self.__completed_work) > 0,
            filesystem=self.__filesystem.get_summary(),
            modifications=self.__get_formatted_modifications(),
            target_subvolume_id=(target.id if target is not None else None),
        )

    def __get_formatted_modifications(self):
        return [self.__format_operation_result(op) for op in self.__completed_work]

    def __format_operation_result(self, operation):
        action_type = operation["action"]
        if action_type == self.__CREATE_SUBVOLUME_OPERATION:
            return self.__format_create_subvolume_result(operation)
        elif action_type == self.__CREATE_SNAPSHOT_OPERATION:
            return self.__format_create_snapshot_result(operation)
        elif action_type == self.__DELETE_SUBVOLUME_OPERATION:
            return self.__format_delete_subvolume_result(operation)
        elif action_type == self.__SET_DEFAULT_SUBVOLUME_OPERATION:
            return self.__format_set_default_subvolume_result(operation)
        else:
            raise ValueError(f"Unknown operation type '{operation['action']}'")

    def __format_create_subvolume_result(self, operation):
        target = operation["target"]
        target_subvolume = self.__filesystem.get_subvolume_by_name(target)
        target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return f"Created subvolume '{target}' ({target_id})"

    def __format_create_snapshot_result(self, operation):
        source = operation["source"]
        source_id = operation["source_id"]

        target = operation["target"]
        target_subvolume = self.__filesystem.get_subvolume_by_name(target)
        target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return f"Created snapshot '{target}' ({target_id}) from '{source}' ({source_id})"

    def __format_delete_subvolume_result(self, operation):
        target = operation["target"]
        target_id = operation["target_id"]
        return f"Deleted subvolume '{target}' ({target_id})"

    def __format_set_default_subvolume_result(self, operation):
        target = operation["target"]
        if "target_id" in operation:
            target_id = operation["target_id"]
        else:
            target_subvolume = self.__filesystem.get_subvolume_by_name(target)
            target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return f"Updated default subvolume to '{target}' ({target_id})"


def run_module():
    module_args = dict(
        automount=dict(type="bool", default=False),
        default=dict(type="bool", default=False),
        filesystem_device=dict(type="path"),
        filesystem_label=dict(type="str"),
        filesystem_uuid=dict(type="str"),
        name=dict(type="str", required=True),
        recursive=dict(type="bool", default=False),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        snapshot_source=dict(type="str"),
        snapshot_conflict=dict(type="str", default="skip", choices=["skip", "clobber", "error"]),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    subvolume = BtrfsSubvolumeModule(module)
    error, result = subvolume.run()
    if error is not None:
        module.fail_json(str(error), **result)
    else:
        module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
