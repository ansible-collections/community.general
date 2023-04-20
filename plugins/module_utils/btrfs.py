# Copyright (c) 2022, Gregory Furlong <gnfzdz@fzdz.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.common.text.converters import to_bytes
import re
import os


def normalize_subvolume_path(path):
    """
    Normalizes btrfs subvolume paths to ensure exactly one leading slash, no trailing slashes and no consecutive slashes.
    In addition, if the path is prefixed with a leading <FS_TREE>, this value is removed.
    """
    fstree_stripped = re.sub(r'^<FS_TREE>', '', path)
    result = re.sub(r'/+$', '', re.sub(r'/+', '/', '/' + fstree_stripped))
    return result if len(result) > 0 else '/'


class BtrfsModuleException(Exception):
    pass


class BtrfsCommands(object):

    """
    Provides access to a subset of the Btrfs command line
    """

    def __init__(self, module):
        self.__module = module
        self.__btrfs = self.__module.get_bin_path("btrfs", required=True)

    def filesystem_show(self):
        command = "%s filesystem show -d" % (self.__btrfs)
        result = self.__module.run_command(command, check_rc=True)
        stdout = [x.strip() for x in result[1].splitlines()]
        filesystems = []
        current = None
        for line in stdout:
            if line.startswith('Label'):
                current = self.__parse_filesystem(line)
                filesystems.append(current)
            elif line.startswith('devid'):
                current['devices'].append(self.__parse_filesystem_device(line))
        return filesystems

    def __parse_filesystem(self, line):
        label = re.sub(r'\s*uuid:.*$', '', re.sub(r'^Label:\s*', '', line))
        id = re.sub(r'^.*uuid:\s*', '', line)

        filesystem = {}
        filesystem['label'] = label.strip("'") if label != 'none' else None
        filesystem['uuid'] = id
        filesystem['devices'] = []
        filesystem['mountpoints'] = []
        filesystem['subvolumes'] = []
        filesystem['default_subvolid'] = None
        return filesystem

    def __parse_filesystem_device(self, line):
        return re.sub(r'^.*path\s', '', line)

    def subvolumes_list(self, filesystem_path):
        command = "%s subvolume list -tap %s" % (self.__btrfs, filesystem_path)
        result = self.__module.run_command(command, check_rc=True)
        stdout = [x.split('\t') for x in result[1].splitlines()]
        subvolumes = [{'id': 5, 'parent': None, 'path': '/'}]
        if len(stdout) > 2:
            subvolumes.extend([self.__parse_subvolume_list_record(x) for x in stdout[2:]])
        return subvolumes

    def __parse_subvolume_list_record(self, item):
        return {
            'id': int(item[0]),
            'parent': int(item[2]),
            'path': normalize_subvolume_path(item[5]),
        }

    def subvolume_get_default(self, filesystem_path):
        command = [self.__btrfs, "subvolume", "get-default", to_bytes(filesystem_path)]
        result = self.__module.run_command(command, check_rc=True)
        # ID [n] ...
        return int(result[1].strip().split()[1])

    def subvolume_set_default(self, filesystem_path, subvolume_id):
        command = [self.__btrfs, "subvolume", "set-default", str(subvolume_id), to_bytes(filesystem_path)]
        result = self.__module.run_command(command, check_rc=True)

    def subvolume_create(self, subvolume_path):
        command = [self.__btrfs, "subvolume", "create", to_bytes(subvolume_path)]
        result = self.__module.run_command(command, check_rc=True)

    def subvolume_snapshot(self, snapshot_source, snapshot_destination):
        command = [self.__btrfs, "subvolume", "snapshot", to_bytes(snapshot_source), to_bytes(snapshot_destination)]
        result = self.__module.run_command(command, check_rc=True)

    def subvolume_delete(self, subvolume_path):
        command = [self.__btrfs, "subvolume", "delete", to_bytes(subvolume_path)]
        result = self.__module.run_command(command, check_rc=True)


class BtrfsInfoProvider(object):

    """
    Utility providing details of the currently available btrfs filesystems
    """

    def __init__(self, module):
        self.__module = module
        self.__btrfs_api = BtrfsCommands(module)
        self.__findmnt_path = self.__module.get_bin_path("findmnt", required=True)

    def get_filesystems(self):
        filesystems = self.__btrfs_api.filesystem_show()
        mountpoints = self.__find_mountpoints()
        for filesystem in filesystems:
            device_mountpoints = self.__filter_mountpoints_for_devices(mountpoints, filesystem['devices'])
            filesystem['mountpoints'] = device_mountpoints

            if len(device_mountpoints) > 0:

                # any path within the filesystem can be used to query metadata
                mountpoint = device_mountpoints[0]['mountpoint']
                filesystem['subvolumes'] = self.get_subvolumes(mountpoint)
                filesystem['default_subvolid'] = self.get_default_subvolume_id(mountpoint)

        return filesystems

    def get_mountpoints(self, filesystem_devices):
        mountpoints = self.__find_mountpoints()
        return self.__filter_mountpoints_for_devices(mountpoints, filesystem_devices)

    def get_subvolumes(self, filesystem_path):
        return self.__btrfs_api.subvolumes_list(filesystem_path)

    def get_default_subvolume_id(self, filesystem_path):
        return self.__btrfs_api.subvolume_get_default(filesystem_path)

    def __filter_mountpoints_for_devices(self, mountpoints, devices):
        return [m for m in mountpoints if (m['device'] in devices)]

    def __find_mountpoints(self):
        command = "%s -t btrfs -nvP" % self.__findmnt_path
        result = self.__module.run_command(command)
        mountpoints = []
        if result[0] == 0:
            lines = result[1].splitlines()
            for line in lines:
                mountpoint = self.__parse_mountpoint_pairs(line)
                mountpoints.append(mountpoint)
        return mountpoints

    def __parse_mountpoint_pairs(self, line):
        pattern = re.compile(r'^TARGET="(?P<target>.*)"\s+SOURCE="(?P<source>.*)"\s+FSTYPE="(?P<fstype>.*)"\s+OPTIONS="(?P<options>.*)"\s*$')
        match = pattern.search(line)
        if match is not None:
            groups = match.groupdict()

            return {
                'mountpoint': groups['target'],
                'device': groups['source'],
                'subvolid': self.__extract_mount_subvolid(groups['options']),
            }
        else:
            raise BtrfsModuleException("Failed to parse findmnt result for line: '%s'" % line)

    def __extract_mount_subvolid(self, mount_options):
        for option in mount_options.split(','):
            if option.startswith('subvolid='):
                return int(option[len('subvolid='):])
        raise BtrfsModuleException("Failed to find subvolid for mountpoint in options '%s'" % mount_options)


class BtrfsSubvolume(object):

    """
    Wrapper class providing convenience methods for inspection of a btrfs subvolume
    """

    def __init__(self, filesystem, subvolume_id):
        self.__filesystem = filesystem
        self.__subvolume_id = subvolume_id

    def get_filesystem(self):
        return self.__filesystem

    def is_mounted(self):
        mountpoints = self.get_mountpoints()
        return mountpoints is not None and len(mountpoints) > 0

    def is_filesystem_root(self):
        return 5 == self.__subvolume_id

    def is_filesystem_default(self):
        return self.__filesystem.default_subvolid == self.__subvolume_id

    def get_mounted_path(self):
        mountpoints = self.get_mountpoints()
        if mountpoints is not None and len(mountpoints) > 0:
            return mountpoints[0]
        elif self.parent is not None:
            parent = self.__filesystem.get_subvolume_by_id(self.parent)
            parent_path = parent.get_mounted_path()
            if parent_path is not None:
                return parent_path + os.path.sep + self.name
        else:
            return None

    def get_mountpoints(self):
        return self.__filesystem.get_mountpoints_by_subvolume_id(self.__subvolume_id)

    def get_child_relative_path(self, absolute_child_path):
        """
        Get the relative path from this subvolume to the named child subvolume.
        The provided parameter is expected to be normalized as by normalize_subvolume_path.
        """
        path = self.path
        if absolute_child_path.startswith(path):
            relative = absolute_child_path[len(path):]
            return re.sub(r'^/*', '', relative)
        else:
            raise BtrfsModuleException("Path '%s' doesn't start with '%s'" % (absolute_child_path, path))

    def get_parent_subvolume(self):
        parent_id = self.parent
        return self.__filesystem.get_subvolume_by_id(parent_id) if parent_id is not None else None

    def get_child_subvolumes(self):
        return self.__filesystem.get_subvolume_children(self.__subvolume_id)

    @property
    def __info(self):
        return self.__filesystem.get_subvolume_info_for_id(self.__subvolume_id)

    @property
    def id(self):
        return self.__subvolume_id

    @property
    def name(self):
        return self.path.split('/').pop()

    @property
    def path(self):
        return self.__info['path']

    @property
    def parent(self):
        return self.__info['parent']


class BtrfsFilesystem(object):

    """
    Wrapper class providing convenience methods for inspection of a btrfs filesystem
    """

    def __init__(self, info, provider, module):
        self.__provider = provider

        # constant for module execution
        self.__uuid = info['uuid']
        self.__label = info['label']
        self.__devices = info['devices']

        # refreshable
        self.__default_subvolid = info['default_subvolid'] if 'default_subvolid' in info else None
        self.__update_mountpoints(info['mountpoints'] if 'mountpoints' in info else [])
        self.__update_subvolumes(info['subvolumes'] if 'subvolumes' in info else [])

    @property
    def uuid(self):
        return self.__uuid

    @property
    def label(self):
        return self.__label

    @property
    def default_subvolid(self):
        return self.__default_subvolid

    @property
    def devices(self):
        return list(self.__devices)

    def refresh(self):
        self.refresh_mountpoints()
        self.refresh_subvolumes()
        self.refresh_default_subvolume()

    def refresh_mountpoints(self):
        mountpoints = self.__provider.get_mountpoints(list(self.__devices))
        self.__update_mountpoints(mountpoints)

    def __update_mountpoints(self, mountpoints):
        self.__mountpoints = dict()
        for i in mountpoints:
            subvolid = i['subvolid']
            mountpoint = i['mountpoint']
            if subvolid not in self.__mountpoints:
                self.__mountpoints[subvolid] = []
            self.__mountpoints[subvolid].append(mountpoint)

    def refresh_subvolumes(self):
        filesystem_path = self.get_any_mountpoint()
        if filesystem_path is not None:
            subvolumes = self.__provider.get_subvolumes(filesystem_path)
            self.__update_subvolumes(subvolumes)

    def __update_subvolumes(self, subvolumes):
        # TODO strategy for retaining information on deleted subvolumes?
        self.__subvolumes = dict()
        for subvolume in subvolumes:
            self.__subvolumes[subvolume['id']] = subvolume

    def refresh_default_subvolume(self):
        filesystem_path = self.get_any_mountpoint()
        if filesystem_path is not None:
            self.__default_subvolid = self.__provider.get_default_subvolume_id(filesystem_path)

    def contains_device(self, device):
        return device in self.__devices

    def contains_subvolume(self, subvolume):
        return self.get_subvolume_by_name(subvolume) is not None

    def get_subvolume_by_id(self, subvolume_id):
        return BtrfsSubvolume(self, subvolume_id) if subvolume_id in self.__subvolumes else None

    def get_subvolume_info_for_id(self, subvolume_id):
        return self.__subvolumes[subvolume_id] if subvolume_id in self.__subvolumes else None

    def get_subvolume_by_name(self, subvolume):
        for subvolume_info in self.__subvolumes.values():
            if subvolume_info['path'] == subvolume:
                return BtrfsSubvolume(self, subvolume_info['id'])
        return None

    def get_any_mountpoint(self):
        for subvol_mountpoints in self.__mountpoints.values():
            if len(subvol_mountpoints) > 0:
                return subvol_mountpoints[0]
        # maybe error?
        return None

    def get_any_mounted_subvolume(self):
        for subvolid, subvol_mountpoints in self.__mountpoints.items():
            if len(subvol_mountpoints) > 0:
                return self.get_subvolume_by_id(subvolid)
        return None

    def get_mountpoints_by_subvolume_id(self, subvolume_id):
        return self.__mountpoints[subvolume_id] if subvolume_id in self.__mountpoints else []

    def get_nearest_subvolume(self, subvolume):
        """Return the identified subvolume if existing, else the closest matching parent"""
        subvolumes_by_path = self.__get_subvolumes_by_path()
        while len(subvolume) > 1:
            if subvolume in subvolumes_by_path:
                return BtrfsSubvolume(self, subvolumes_by_path[subvolume]['id'])
            else:
                subvolume = re.sub(r'/[^/]+$', '', subvolume)

        return BtrfsSubvolume(self, 5)

    def get_mountpath_as_child(self, subvolume_name):
        """Find a path to the target subvolume through a mounted ancestor"""
        nearest = self.get_nearest_subvolume(subvolume_name)
        if nearest.path == subvolume_name:
            nearest = nearest.get_parent_subvolume()
        if nearest is None or nearest.get_mounted_path() is None:
            raise BtrfsModuleException("Failed to find a path '%s' through a mounted parent subvolume" % subvolume_name)
        else:
            return nearest.get_mounted_path() + os.path.sep + nearest.get_child_relative_path(subvolume_name)

    def get_subvolume_children(self, subvolume_id):
        return [BtrfsSubvolume(self, x['id']) for x in self.__subvolumes.values() if x['parent'] == subvolume_id]

    def __get_subvolumes_by_path(self):
        result = {}
        for s in self.__subvolumes.values():
            path = s['path']
            result[path] = s
        return result

    def is_mounted(self):
        return self.__mountpoints is not None and len(self.__mountpoints) > 0

    def get_summary(self):
        subvolumes = []
        sources = self.__subvolumes.values() if self.__subvolumes is not None else []
        for subvolume in sources:
            id = subvolume['id']
            subvolumes.append({
                'id': id,
                'path': subvolume['path'],
                'parent': subvolume['parent'],
                'mountpoints': self.get_mountpoints_by_subvolume_id(id),
            })

        return {
            'default_subvolume': self.__default_subvolid,
            'devices': self.__devices,
            'label': self.__label,
            'uuid': self.__uuid,
            'subvolumes': subvolumes,
        }


class BtrfsFilesystemsProvider(object):

    """
    Provides methods to query available btrfs filesystems
    """

    def __init__(self, module):
        self.__module = module
        self.__provider = BtrfsInfoProvider(module)
        self.__filesystems = None

    def get_matching_filesystem(self, criteria):
        if criteria['device'] is not None:
            criteria['device'] = os.path.realpath(criteria['device'])

        self.__check_init()
        matching = [f for f in self.__filesystems.values() if self.__filesystem_matches_criteria(f, criteria)]
        if len(matching) == 1:
            return matching[0]
        else:
            raise BtrfsModuleException("Found %d filesystems matching criteria uuid=%s label=%s device=%s" % (
                len(matching),
                criteria['uuid'],
                criteria['label'],
                criteria['device']
            ))

    def __filesystem_matches_criteria(self, filesystem, criteria):
        return ((criteria['uuid'] is None or filesystem.uuid == criteria['uuid']) and
                (criteria['label'] is None or filesystem.label == criteria['label']) and
                (criteria['device'] is None or filesystem.contains_device(criteria['device'])))

    def get_filesystem_for_device(self, device):
        real_device = os.path.realpath(device)
        self.__check_init()
        for fs in self.__filesystems.values():
            if fs.contains_device(real_device):
                return fs
        return None

    def get_filesystems(self):
        self.__check_init()
        return list(self.__filesystems.values())

    def __check_init(self):
        if self.__filesystems is None:
            self.__filesystems = dict()
            for f in self.__provider.get_filesystems():
                uuid = f['uuid']
                self.__filesystems[uuid] = BtrfsFilesystem(f, self.__provider, self.__module)
