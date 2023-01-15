#!/usr/bin/python

# Copyright (c) 2022, Gregory Furlong <gnfzdz@fzdz.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: btrfs_subvolume
short_description: Manage btrfs subvolumes
version_added: "6.3.0"

description: Creates, updates and deletes btrfs subvolumes and snapshots.

options:
    automount:
        description:
        - Allow the module to temporarily mount the targeted btrfs filesystem in order to validate the current state and make any required changes.
        type: bool
        default: false
    default:
        description:
        - Make the subvolume specified by I(name) the filesystem's default subvolume.
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
        - When true, indicates that parent/child subvolumes should be created/removed.
        - as necessary to complete the operation (for I(state=present) and I(state=absent) respectively).
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
        - C(skip) - Create a snapshot only if a subvolume does not yet exist at the target location, otherwise indicate that no change is required.
          Warning, this option does not yet verify that the target subvolume was generated from a snapshot of the requested source.
        - C(clobber) - If a subvolume already exists at the requested location, delete it first.
          This option is not idempotent and will result in a new snapshot being generated on every execution.
        - C(error) - If a subvolume already exists at the requested location, return an error.
          This option is not idempotent and will result in an error on replay of the module.
        type: str
        choices: [ skip, clobber, error ]
        default: skip
    state:
        description:
            - Indicates the current state of the targeted subvolume.
        type: str
        choices: [ absent, present ]
        default: present

notes:
  - If any or all of the options I(filesystem_device), I(filesystem_label) or I(filesystem_uuid) parameters are provided, there is expected
    to be a matching btrfs filesystem. If none are provided and only a single btrfs filesystem exists or only a single
    btrfs filesystem is mounted, that filesystem will be used; otherwise, the module will take no action and return an error.
  - I(check_mode) is supported, but in some scenarios it may erroneously report intermediate subvolumes being created.
    After mounting, if a directory like file is found where the subvolume would have been created, the operation is skipped.

author:
    - Gregory Furlong (@gnfzdz)
'''

EXAMPLES = r'''

- name: Create a @home subvolume under the root subvolume
  community.general.btrfs_subvolume:
    name: /@home
    device: /dev/vda2

- name: Remove the @home subvolume if it exists
  community.general.btrfs_subvolume:
    name: /@home
    state: absent
    device: /dev/vda2

- name: Create a snapshot of the root subvolume named @
  community.general.btrfs_subvolume:
    name: /@
    snapshot_source: /
    device: /dev/vda2

- name: Create a snapshot of the root subvolume and make it the new default subvolume
  community.general.btrfs_subvolume:
    name: /@
    snapshot_source: /
    default: Yes
    device: /dev/vda2

- name: Create a snapshot of the /@ subvolume and recursively creating intermediate subvolumes as required
  community.general.btrfs_subvolume:
    name: /@snapshots/@2022_06_09
    snapshot_source: /@
    recursive: True
    device: /dev/vda2

- name: Remove the /@ subvolume and recursively delete child subvolumes as required
  community.general.btrfs_subvolume:
    name: /@snapshots/@2022_06_09
    snapshot_source: /@
    recursive: True
    device: /dev/vda2

'''

RETURN = r'''

filesystem:
    description:
    - A summary of the final state of the targeted btrfs filesystem
    type: dict
    returned: success
    contains:
        uuid:
            description: A unique identifier assigned to the filesystem
            returned: success
            type: str
            sample: 96c9c605-1454-49b8-a63a-15e2584c208e
        label:
            description: An optional label assigned to the filesystem
            returned: success
            type: str
            sample: Tank
        devices:
            description: A list of devices assigned to the filesystem
            returned: success
            type: list
            sample:
                - /dev/sda1
                - /dev/sdb1
        default_subvolume:
            description: The id of the filesystem's default subvolume
            returned: success and if filesystem is mounted
            type: int
            sample: 5
        subvolumes:
            description: A list of dicts containing metadata for all of the filesystem's subvolumes
            returned: success and if filesystem is mounted
            type: list
            elements: dict
            contains:
                id:
                    description: An identifier assigned to the subvolume, unique within the containing filesystem
                    type: int
                    sample: 256
                mountpoints:
                    description: Paths where the subvolume is mounted on the targeted host
                    type: list
                    sample: ['/home']
                parent:
                    description: The identifier of this subvolume's parent
                    type: int
                    sample: 5
                path:
                    description: The full path of the subvolume relative to the btrfs fileystem's root
                    type: str
                    sample: /@home

modifications:
    description:
    - A list where each element describes a change made to the target btrfs filesystem
    type: list
    returned: Success
    elements: str

target_subvolume_id:
    description:
    - The id of the subvolume specified with the I(name) parameter, either pre-existing or created as part of module execution
    type: int
    sample: 257
    returned: Success and subvolume exists after module execution
'''

from ansible_collections.community.general.plugins.module_utils.btrfs import BtrfsFilesystemsProvider, BtrfsCommands
from ansible_collections.community.general.plugins.module_utils.btrfs import normalize_subvolume_path, find_common_path_prefix
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
import os
import re
import tempfile


class BtrfsSubvolumeModule(object):

    __BTRFS_ROOT_SUBVOLUME = '/'
    __BTRFS_ROOT_SUBVOLUME_ID = 5
    __BTRFS_SUBVOLUME_INODE_NUMBER = 256

    __CREATE_SUBVOLUME_OPERATION = 'create'
    __CREATE_SNAPSHOT_OPERATION = 'snapshot'
    __DELETE_SUBVOLUME_OPERATION = 'delete'
    __SET_DEFAULT_SUBVOLUME_OPERATION = 'set-default'

    __UNKNOWN_SUBVOLUME_ID = '?'

    def __init__(self, module):
        self.module = module
        self.__btrfs_api = BtrfsCommands(module)
        self.__provider = BtrfsFilesystemsProvider(module)

        #  module parameters
        self.__name = self.module.params['name']
        self.__state = self.module.params['state']

        self.__automount = self.module.params['automount']
        self.__default = self.module.params['default']
        self.__filesystem_device = self.module.params['filesystem_device']
        self.__filesystem_label = self.module.params['filesystem_label']
        self.__filesystem_uuid = self.module.params['filesystem_uuid']
        self.__recursive = self.module.params['recursive']
        self.__snapshot_conflict = self.module.params['snapshot_conflict']
        self.__snapshot_source = self.module.params['snapshot_source']

        # execution state
        self.__filesystem = None
        self.__unit_of_work = []
        self.__completed_work = []
        self.__temporary_mounts = dict()
        self.__messages = []

    def run(self):
        try:
            self.__load_filesystem()
            self.__prepare_unit_of_work()

            if not self.module.check_mode:
                if len(self.__unit_of_work) > 0:
                    self.__execute_unit_of_work()
                    self.__filesystem.refresh()
            else:
                self.__completed_work.extend(self.__unit_of_work)

        finally:
            self.__cleanup_mounts()
            if self.__filesystem is not None:
                self.__filesystem.refresh_mountpoints()

        return self.get_results()

    # Identify the targeted filesystem and obtain the current state
    def __load_filesystem(self):
        if self.__has_filesystem_criteria():
            filesystem = self.__find_matching_filesytem()
        else:
            filesystem = self.__find_default_filesystem()

        # The filesystem must be mounted to obtain the current state (subvolumes, default, etc)
        if not filesystem.is_mounted():
            self.__mount_subvolume_id_to_tempdir(filesystem, self.__BTRFS_ROOT_SUBVOLUME_ID)
            filesystem.refresh()
        self.__filesystem = filesystem

    def __has_filesystem_criteria(self):
        return self.__filesystem_uuid is not None or self.__filesystem_label is not None or self.__filesystem_device is not None

    def __find_matching_filesytem(self):
        criteria = {
            'uuid': self.__filesystem_uuid,
            'label': self.__filesystem_label,
            'device': self.__filesystem_device,
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
            self.module.fail_json(
                msg="Failed to automatically identify targeted filesystem. "
                "No explicit device indicated and found %d available filesystems." % len(filesystems))

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
            if self.__recursive:
                self.__prepare_subvolume_intermediates_present(self.__name)
            self.__stage_create_subvolume(self.__name)

    def __prepare_subvolume_intermediates_present(self, subvolume_name):
        closest_subvolume = self.__filesystem.get_nearest_subvolume(subvolume_name)
        relative_path = closest_subvolume.get_child_relative_path(self.__name)
        missing_subvolumes = [x for x in relative_path.split(os.path.sep) if len(x) > 0]
        if len(missing_subvolumes) > 1:
            current = closest_subvolume.path
            for s in missing_subvolumes[:-1]:
                current = current + os.path.sep + s
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
                self.module.fail_json(msg="Target subvolume=%s already exists and snapshot_conflict='error'" % self.__name)

        if source_subvolume is None:
            self.module.fail_json(msg="Source subvolume %s does not exist" % self.__snapshot_source)
        elif subvolume is not None and source_subvolume.id == subvolume.id:
            self.module.fail_json(msg="Snapshot source and target are the same.")

        if subvolume_exists and self.__snapshot_conflict == "clobber":
            self.__prepare_subvolume_tree_absent(subvolume)
        elif not subvolume_exists and self.__recursive:
            self.__prepare_subvolume_intermediates_present(self.__name)
        self.__stage_create_snapshot(source_subvolume, self.__name)

    def __prepare_subvolume_absent(self):
        subvolume = self.__filesystem.get_subvolume_by_name(self.__name)
        if subvolume is not None:
            self.__prepare_subvolume_tree_absent(subvolume)

    def __prepare_subvolume_tree_absent(self, subvolume):
        if subvolume.is_filesystem_root():
            self.module.fail_json(msg="Can not delete the filesystem's root subvolume")
        if not self.__recursive and len(subvolume.get_child_subvolumes()) > 0:
            self.module.fail_json(msg="Subvolume targeted for deletion %s has children and recursive=False."
                                      "Either explicitly delete the child subvolumes first or pass "
                                      "parameter recursive=True." % subvolume.path)

        queue = self.__prepare_recursive_delete_order(subvolume) if self.__recursive else [subvolume]
        # prepare unit of work
        for s in queue:
            if s.is_mounted():
                # TODO potentially unmount the subvolume if automount=True ?
                self.module.fail_json(msg="Can not delete mounted subvolume=%s" % s.path)
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
    def __stage_create_subvolume(self, subvolume_path, intermediate=False):
        """
        Add required creation of an intermediate subvolume to the unit of work
        If intermediate is true, the action will be skipped if a directory like file is found at target
        after mounting a parent subvolume
        """
        self.__unit_of_work.append({
            'action': self.__CREATE_SUBVOLUME_OPERATION,
            'target': normalize_subvolume_path(subvolume_path),
            'intermediate': intermediate,
        })

    def __stage_create_snapshot(self, source_subvolume, target_subvolume_path):
        """Add creation of a snapshot from source to target to the unit of work"""
        self.__unit_of_work.append({
            'action': self.__CREATE_SNAPSHOT_OPERATION,
            'source': source_subvolume.path,
            'source_id': source_subvolume.id,
            'target': normalize_subvolume_path(target_subvolume_path),
        })

    def __stage_delete_subvolume(self, subvolume):
        """Add deletion of the target subvolume to the unit of work"""
        self.__unit_of_work.append({
            'action': self.__DELETE_SUBVOLUME_OPERATION,
            'target': subvolume.path,
            'target_id': subvolume.id,
        })

    def __stage_set_default_subvolume(self, subvolume_path, subvolume_id=None):
        """Add update of the filesystem's default subvolume to the unit of work"""
        self.__unit_of_work.append({
            'action': self.__SET_DEFAULT_SUBVOLUME_OPERATION,
            'target': normalize_subvolume_path(subvolume_path),
            'target_id': subvolume_id,
        })

    # Execute the unit of work
    def __execute_unit_of_work(self):
        # TODO mount only as close as required for each operation (many mountpoints)?
        # TODO check if anything needs to be mounted during __prepare* so that check_mode will fail when automount=False
        if self.__automount:
            parent = self.__find_common_parent_subvolume(self.__unit_of_work)
            self.__get_btrfs_subvolume_mountpoint(parent)

        for op in self.__unit_of_work:
            if op['action'] == self.__CREATE_SUBVOLUME_OPERATION:
                self.__execute_create_subvolume(op)
            elif op['action'] == self.__CREATE_SNAPSHOT_OPERATION:
                self.__execute_create_snapshot(op)
            elif op['action'] == self.__DELETE_SUBVOLUME_OPERATION:
                self.__execute_delete_subvolume(op)
            elif op['action'] == self.__SET_DEFAULT_SUBVOLUME_OPERATION:
                self.__execute_set_default_subvolume(op)
            else:
                raise ValueError("Unknown operation type '%s'" % op['action'])

    def __find_common_parent_subvolume(self, unit_of_work):
        """
        As most operations require a parent subvolume to be mounted, this finds the
        first currently existing, common ancestor
        """
        paths = []
        for operation in unit_of_work:
            if operation['action'] == self.__SET_DEFAULT_SUBVOLUME_OPERATION:
                # set default (by subvolid) doesn't require any specific subvolume to be available
                continue
            if 'target' in operation:
                parent = os.path.dirname(operation['target'])
                paths.append(parent)
            if 'source' in operation:
                paths.append(operation['source'])

        if len(paths) > 0:
            prefix = find_common_path_prefix(paths)
            common_parent = self.__filesystem.get_subvolume_by_name(prefix)
            if common_parent is not None:
                return common_parent
            else:
                raise Exception("Failed to find common parent subvolume '%s' in filesystem '%s'." % (prefix, self.__filesystem.uuid))
        else:
            # There are no operations requiring specific subvolume(s) to be mounted, but there should be something already available
            # There should be something already available as the filesystem needs to be online to query metadata
            return self.__filesystem.get_any_mounted_subvolume()

    def __execute_create_subvolume(self, operation):
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation['target'])
        if not self.__is_existing_directory_like(target_mounted_path):
            self.__btrfs_api.subvolume_create(target_mounted_path)
            self.__completed_work.append(operation)

    def __execute_create_snapshot(self, operation):
        source_subvolume = self.__filesystem.get_subvolume_by_name(operation['source'])
        source_mounted_path = source_subvolume.get_mounted_path()
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation['target'])

        self.__btrfs_api.subvolume_snapshot(source_mounted_path, target_mounted_path)
        self.__completed_work.append(operation)

    def __execute_delete_subvolume(self, operation):
        target_mounted_path = self.__filesystem.get_mountpath_as_child(operation['target'])
        self.__btrfs_api.subvolume_delete(target_mounted_path)
        self.__completed_work.append(operation)

    def __execute_set_default_subvolume(self, operation):
        target = operation['target']
        target_id = operation['target_id']

        if target_id is None:
            target_subvolume = self.__filesystem.get_subvolume_by_name(target)

            if target_subvolume is None:
                self.__filesystem.refresh()  # the target may have been created earlier in module execution
                target_subvolume = self.__filesystem.get_subvolume_by_name(target)

            if target_subvolume is None:
                raise Exception("Failed to find existing subvolume '%s'" % target)
            else:
                target_id = target_subvolume.id

        self.__btrfs_api.subvolume_set_default(self.__filesystem.get_any_mountpoint(), target_id)
        self.__completed_work.append(operation)

    def __is_existing_directory_like(self, path):
        return os.path.exists(path) and (
            os.path.isdir(path) or
            os.stat(path).st_ino == self.__BTRFS_SUBVOLUME_INODE_NUMBER
        )

    # Get subvolume mountpoints (or mount if none exists)
    def __get_btrfs_subvolume_mountpoint(self, subvolume):
        subvolume = self.__filesystem.get_subvolume_by_name(subvolume) if isinstance(subvolume, str) else subvolume
        mounted_path = subvolume.get_mounted_path()
        if mounted_path is None:
            mounted_path = self.__mount_subvolume_id_to_tempdir(self.__filesystem, subvolume.id)
            self.__filesystem.refresh()
        return mounted_path

    # Create/cleanup temporary mountpoints
    def __mount_subvolume_id_to_tempdir(self, filesystem, subvolid):
        if not self.__automount:
            self.module.fail_json(
                msg="Subvolid=%d needs to be mounted to proceed but automount=%s. "
                    "Mount explicitly before module execution or pass automount=True "
                    "to temporarily mount as part of module execution." % (subvolid, self.__automount))

        # The subvolume was already mounted, so return the current path
        if subvolid in self.__temporary_mounts:
            return self.__temporary_mounts[subvolid]

        device = filesystem.devices[0]
        mountpoint = tempfile.mkdtemp(dir="/tmp")
        self.__temporary_mounts[subvolid] = mountpoint

        mount = self.module.get_bin_path("mount", required=True)
        command = "%s -o noatime,subvolid=%d %s %s " % (mount,
                                                        subvolid,
                                                        device,
                                                        mountpoint)
        result = self.module.run_command(command, check_rc=True)

        self.__messages.append("Created temporary mountpoint for subvolid=%d at path=%s" % (subvolid, mountpoint))
        return mountpoint

    def __cleanup_mounts(self):
        for key in self.__temporary_mounts.keys():
            self.__cleanup_mount(self.__temporary_mounts[key])

    def __cleanup_mount(self, mountpoint):
        umount = self.module.get_bin_path("umount", required=True)
        result = self.module.run_command("%s %s" % (umount, mountpoint))
        if result[0] == 0:
            rmdir = self.module.get_bin_path("rmdir", required=True)
            self.module.run_command("%s %s" % (rmdir, mountpoint))

    # Format and return results
    def get_results(self):
        target = self.__filesystem.get_subvolume_by_name(self.__name)
        return dict(
            changed=len(self.__completed_work) > 0,
            filesystem=self.__filesystem.get_summary(),
            modifications=self.__get_formatted_modifications(),
            target_subvolume_id=(target.id if target is not None else None)
        )

    def __get_formatted_modifications(self):
        return [self.__format_operation_result(op) for op in self.__unit_of_work]

    def __format_operation_result(self, operation):
        action_type = operation['action']
        if action_type == self.__CREATE_SUBVOLUME_OPERATION:
            return self.__format_create_subvolume_result(operation)
        elif action_type == self.__CREATE_SNAPSHOT_OPERATION:
            return self.__format_create_snapshot_result(operation)
        elif action_type == self.__DELETE_SUBVOLUME_OPERATION:
            return self.__format_delete_subvolume_result(operation)
        elif action_type == self.__SET_DEFAULT_SUBVOLUME_OPERATION:
            return self.__format_set_default_subvolume_result(operation)
        else:
            raise ValueError("Unknown operation type '%s'" % operation['action'])

    def __format_create_subvolume_result(self, operation):
        target = operation['target']
        target_subvolume = self.__filesystem.get_subvolume_by_name(target)
        target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return "Created subvolume '%s' (%s)" % (target, target_id)

    def __format_create_snapshot_result(self, operation):
        source = operation['source']
        source_id = operation['source_id']

        target = operation['target']
        target_subvolume = self.__filesystem.get_subvolume_by_name(target)
        target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return "Created snapshot '%s' (%s) from '%s' (%s)" % (target, target_id, source, source_id)

    def __format_delete_subvolume_result(self, operation):
        target = operation['target']
        target_id = operation['target_id']
        return "Deleted subvolume '%s' (%s)" % (target, target_id)

    def __format_set_default_subvolume_result(self, operation):
        target = operation['target']
        if 'target_id' in operation:
            target_id = operation['target_id']
        else:
            target_subvolume = self.__filesystem.get_subvolume_by_name(target)
            target_id = target_subvolume.id if target_subvolume is not None else self.__UNKNOWN_SUBVOLUME_ID
        return "Updated default subvolume to '%s' (%s)" % (target, target_id)


def run_module():
    module_args = dict(
        automount=dict(type='bool', required=False, default=False),
        default=dict(type='bool', required=False, default=False),
        filesystem_device=dict(type='path', required=False),
        filesystem_label=dict(type='str', required=False),
        filesystem_uuid=dict(type='str', required=False),
        name=dict(type='str', required=True),
        recursive=dict(type='bool', default=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
        snapshot_source=dict(type='str', required=False),
        snapshot_conflict=dict(type='str', required=False, default='skip', choices=['skip', 'clobber', 'error'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    subvolume = BtrfsSubvolumeModule(module)
    result = subvolume.run()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
