#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Fabrizio Colonna <colofabrix@tin.it>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
author:
 - Fabrizio Colonna (@ColOfAbRiX)
module: parted
short_description: Configure block device partitions
description:
  - This module allows configuring block device partition using the C(parted)
    command line tool. For a full description of the fields and the options
    check the GNU parted manual.
requirements:
  - This module requires parted version 1.8.3 and above
  - align option (except 'undefined') requires parted 2.1 and above
  - If the version of parted is below 3.1, it requires a Linux version running
    the sysfs file system C(/sys/).
options:
  device:
    description: The block device (disk) where to operate.
    type: str
    required: True
  align:
    description: Set alignment for newly created partitions. Use 'undefined' for parted default aligment.
    type: str
    choices: [ cylinder, minimal, none, optimal, undefined ]
    default: optimal
  number:
    description:
    - The number of the partition to work with or the number of the partition
      that will be created.
    - Required when performing any action on the disk, except fetching information.
    type: int
  unit:
    description:
    - Selects the current default unit that Parted will use to display
      locations and capacities on the disk and to interpret those given by the
      user if they are not suffixed by an unit.
    - When fetching information about a disk, it is always recommended to specify a unit.
    type: str
    choices: [ s, B, KB, KiB, MB, MiB, GB, GiB, TB, TiB, '%', cyl, chs, compact ]
    default: KiB
  label:
    description:
     - Disk label type to use.
     - If C(device) already contains different label, it will be changed to C(label) and any previous partitions will be lost.
    type: str
    choices: [ aix, amiga, bsd, dvh, gpt, loop, mac, msdos, pc98, sun ]
    default: msdos
  part_type:
    description:
    - May be specified only with 'msdos' or 'dvh' partition tables.
    - A C(name) must be specified for a 'gpt' partition table.
    - Neither C(part_type) nor C(name) may be used with a 'sun' partition table.
    type: str
    choices: [ extended, logical, primary ]
    default: primary
  part_start:
    description:
    - Where the partition will start as offset from the beginning of the disk,
      that is, the "distance" from the start of the disk. Negative numbers
      specify distance from the end of the disk.
    - The distance can be specified with all the units supported by parted
      (except compat) and it is case sensitive, e.g. C(10GiB), C(15%).
    - Using negative values may require setting of C(fs_type) (see notes).
    type: str
    default: 0%
  part_end:
    description:
    - Where the partition will end as offset from the beginning of the disk,
      that is, the "distance" from the start of the disk. Negative numbers
      specify distance from the end of the disk.
    - The distance can be specified with all the units supported by parted
      (except compat) and it is case sensitive, e.g. C(10GiB), C(15%).
    type: str
    default: 100%
  name:
    description:
    - Sets the name for the partition number (GPT, Mac, MIPS and PC98 only).
    type: str
  flags:
    description: A list of the flags that has to be set on the partition.
    type: list
    elements: str
  state:
    description:
    - Whether to create or delete a partition.
    - If set to C(info) the module will only return the device information.
    type: str
    choices: [ absent, present, info ]
    default: info
  fs_type:
    description:
     - If specified and the partition does not exist, will set filesystem type to given partition.
     - Parameter optional, but see notes below about negative C(part_start) values.
    type: str
    version_added: '0.2.0'
  resize:
    description:
      - Call C(resizepart) on existing partitions to match the size specified by I(part_end).
    type: bool
    default: false
    version_added: '1.3.0'

notes:
  - When fetching information about a new disk and when the version of parted
    installed on the system is before version 3.1, the module queries the kernel
    through C(/sys/) to obtain disk information. In this case the units CHS and
    CYL are not supported.
  - Negative C(part_start) start values were rejected if C(fs_type) was not given.
    This bug was fixed in parted 3.2.153. If you want to use negative C(part_start),
    specify C(fs_type) as well or make sure your system contains newer parted.
'''

RETURN = r'''
partition_info:
  description: Current partition information
  returned: success
  type: complex
  contains:
    disk:
      description: Generic device information.
      type: dict
    partitions:
      description: List of device partitions.
      type: list
    script:
      description: parted script executed by module
      type: str
  sample: {
      "disk": {
        "dev": "/dev/sdb",
        "logical_block": 512,
        "model": "VMware Virtual disk",
        "physical_block": 512,
        "size": 5.0,
        "table": "msdos",
        "unit": "gib"
      },
      "partitions": [{
        "begin": 0.0,
        "end": 1.0,
        "flags": ["boot", "lvm"],
        "fstype": "",
        "name": "",
        "num": 1,
        "size": 1.0
      }, {
        "begin": 1.0,
        "end": 5.0,
        "flags": [],
        "fstype": "",
        "name": "",
        "num": 2,
        "size": 4.0
      }],
      "script": "unit KiB print "
    }
'''

EXAMPLES = r'''
- name: Create a new ext4 primary partition
  community.general.parted:
    device: /dev/sdb
    number: 1
    state: present
    fs_type: ext4

- name: Remove partition number 1
  community.general.parted:
    device: /dev/sdb
    number: 1
    state: absent

- name: Create a new primary partition with a size of 1GiB
  community.general.parted:
    device: /dev/sdb
    number: 1
    state: present
    part_end: 1GiB

- name: Create a new primary partition for LVM
  community.general.parted:
    device: /dev/sdb
    number: 2
    flags: [ lvm ]
    state: present
    part_start: 1GiB

- name: Create a new primary partition with a size of 1GiB at disk's end
  community.general.parted:
    device: /dev/sdb
    number: 3
    state: present
    fs_type: ext3
    part_start: -1GiB

# Example on how to read info and reuse it in subsequent task
- name: Read device information (always use unit when probing)
  community.general.parted: device=/dev/sdb unit=MiB
  register: sdb_info

- name: Remove all partitions from disk
  community.general.parted:
    device: /dev/sdb
    number: '{{ item.num }}'
    state: absent
  loop: '{{ sdb_info.partitions }}'

- name: Extend an existing partition to fill all available space
  community.general.parted:
    device: /dev/sdb
    number: "{{ sdb_info.partitions | length }}"
    part_end: "100%"
    resize: true
    state: present
'''


from ansible.module_utils.basic import AnsibleModule
import math
import re
import os


# Reference prefixes (International System of Units and IEC)
units_si = ['B', 'KB', 'MB', 'GB', 'TB']
units_iec = ['KiB', 'MiB', 'GiB', 'TiB']
parted_units = units_si + units_iec + ['s', '%', 'cyl', 'chs', 'compact']


def parse_unit(size_str, unit=''):
    """
    Parses a string containing a size or boundary information
    """
    matches = re.search(r'^(-?[\d.]+) *([\w%]+)?$', size_str)
    if matches is None:
        # "<cylinder>,<head>,<sector>" format
        matches = re.search(r'^(\d+),(\d+),(\d+)$', size_str)
        if matches is None:
            module.fail_json(
                msg="Error interpreting parted size output: '%s'" % size_str
            )

        size = {
            'cylinder': int(matches.group(1)),
            'head': int(matches.group(2)),
            'sector': int(matches.group(3))
        }
        unit = 'chs'

    else:
        # Normal format: "<number>[<unit>]"
        if matches.group(2) is not None:
            unit = matches.group(2)

        size = float(matches.group(1))

    return size, unit


def parse_partition_info(parted_output, unit):
    """
    Parses the output of parted and transforms the data into
    a dictionary.

    Parted Machine Parseable Output:
    See: https://lists.alioth.debian.org/pipermail/parted-devel/2006-December/00
    0573.html
     - All lines end with a semicolon (;)
     - The first line indicates the units in which the output is expressed.
       CHS, CYL and BYT stands for CHS, Cylinder and Bytes respectively.
     - The second line is made of disk information in the following format:
       "path":"size":"transport-type":"logical-sector-size":"physical-sector-siz
       e":"partition-table-type":"model-name";
     - If the first line was either CYL or CHS, the next line will contain
       information on no. of cylinders, heads, sectors and cylinder size.
     - Partition information begins from the next line. This is of the format:
       (for BYT)
       "number":"begin":"end":"size":"filesystem-type":"partition-name":"flags-s
       et";
       (for CHS/CYL)
       "number":"begin":"end":"filesystem-type":"partition-name":"flags-set";
    """
    lines = [x for x in parted_output.split('\n') if x.strip() != '']

    # Generic device info
    generic_params = lines[1].rstrip(';').split(':')

    # The unit is read once, because parted always returns the same unit
    size, unit = parse_unit(generic_params[1], unit)

    generic = {
        'dev': generic_params[0],
        'size': size,
        'unit': unit.lower(),
        'table': generic_params[5],
        'model': generic_params[6],
        'logical_block': int(generic_params[3]),
        'physical_block': int(generic_params[4])
    }

    # CYL and CHS have an additional line in the output
    if unit in ['cyl', 'chs']:
        chs_info = lines[2].rstrip(';').split(':')
        cyl_size, cyl_unit = parse_unit(chs_info[3])
        generic['chs_info'] = {
            'cylinders': int(chs_info[0]),
            'heads': int(chs_info[1]),
            'sectors': int(chs_info[2]),
            'cyl_size': cyl_size,
            'cyl_size_unit': cyl_unit.lower()
        }
        lines = lines[1:]

    parts = []
    for line in lines[2:]:
        part_params = line.rstrip(';').split(':')

        # CHS use a different format than BYT, but contrary to what stated by
        # the author, CYL is the same as BYT. I've tested this undocumented
        # behaviour down to parted version 1.8.3, which is the first version
        # that supports the machine parseable output.
        if unit != 'chs':
            size = parse_unit(part_params[3])[0]
            fstype = part_params[4]
            name = part_params[5]
            flags = part_params[6]

        else:
            size = ""
            fstype = part_params[3]
            name = part_params[4]
            flags = part_params[5]

        parts.append({
            'num': int(part_params[0]),
            'begin': parse_unit(part_params[1])[0],
            'end': parse_unit(part_params[2])[0],
            'size': size,
            'fstype': fstype,
            'name': name,
            'flags': [f.strip() for f in flags.split(', ') if f != ''],
            'unit': unit.lower(),
        })

    return {'generic': generic, 'partitions': parts}


def format_disk_size(size_bytes, unit):
    """
    Formats a size in bytes into a different unit, like parted does. It doesn't
    manage CYL and CHS formats, though.
    This function has been adapted from https://github.com/Distrotech/parted/blo
    b/279d9d869ff472c52b9ec2e180d568f0c99e30b0/libparted/unit.c
    """
    global units_si, units_iec

    unit = unit.lower()

    # Shortcut
    if size_bytes == 0:
        return 0.0, 'b'

    # Cases where we default to 'compact'
    if unit in ['', 'compact', 'cyl', 'chs']:
        index = max(0, int(
            (math.log10(size_bytes) - 1.0) / 3.0
        ))
        unit = 'b'
        if index < len(units_si):
            unit = units_si[index]

    # Find the appropriate multiplier
    multiplier = 1.0
    if unit in units_si:
        multiplier = 1000.0 ** units_si.index(unit)
    elif unit in units_iec:
        multiplier = 1024.0 ** units_iec.index(unit)

    output = size_bytes // multiplier * (1 + 1E-16)

    # Corrections to round up as per IEEE754 standard
    if output < 10:
        w = output + 0.005
    elif output < 100:
        w = output + 0.05
    else:
        w = output + 0.5

    if w < 10:
        precision = 2
    elif w < 100:
        precision = 1
    else:
        precision = 0

    # Round and return
    return round(output, precision), unit


def convert_to_bytes(size_str, unit):
    size = float(size_str)
    multiplier = 1.0
    if unit in units_si:
        multiplier = 1000.0 ** units_si.index(unit)
    elif unit in units_iec:
        multiplier = 1024.0 ** (units_iec.index(unit) + 1)
    elif unit in ['', 'compact', 'cyl', 'chs']:
        # As per format_disk_size, default to compact, which defaults to megabytes
        multiplier = 1000.0 ** units_si.index("MB")

    output = size * multiplier
    return int(output)


def get_unlabeled_device_info(device, unit):
    """
    Fetches device information directly from the kernel and it is used when
    parted cannot work because of a missing label. It always returns a 'unknown'
    label.
    """
    device_name = os.path.basename(device)
    base = "/sys/block/%s" % device_name

    vendor = read_record(base + "/device/vendor", "Unknown")
    model = read_record(base + "/device/model", "model")
    logic_block = int(read_record(base + "/queue/logical_block_size", 0))
    phys_block = int(read_record(base + "/queue/physical_block_size", 0))
    size_bytes = int(read_record(base + "/size", 0)) * logic_block

    size, unit = format_disk_size(size_bytes, unit)

    return {
        'generic': {
            'dev': device,
            'table': "unknown",
            'size': size,
            'unit': unit,
            'logical_block': logic_block,
            'physical_block': phys_block,
            'model': "%s %s" % (vendor, model),
        },
        'partitions': []
    }


def get_device_info(device, unit):
    """
    Fetches information about a disk and its partitions and it returns a
    dictionary.
    """
    global module, parted_exec

    # If parted complains about missing labels, it means there are no partitions.
    # In this case only, use a custom function to fetch information and emulate
    # parted formats for the unit.
    label_needed = check_parted_label(device)
    if label_needed:
        return get_unlabeled_device_info(device, unit)

    command = "%s -s -m %s -- unit '%s' print" % (parted_exec, device, unit)
    rc, out, err = module.run_command(command)
    if rc != 0 and 'unrecognised disk label' not in err:
        module.fail_json(msg=(
            "Error while getting device information with parted "
            "script: '%s'" % command),
            rc=rc, out=out, err=err
        )

    return parse_partition_info(out, unit)


def check_parted_label(device):
    """
    Determines if parted needs a label to complete its duties. Versions prior
    to 3.1 don't return data when there is no label. For more information see:
    http://upstream.rosalinux.ru/changelogs/libparted/3.1/changelog.html
    """
    global parted_exec

    # Check the version
    parted_major, parted_minor, dummy = parted_version()
    if (parted_major == 3 and parted_minor >= 1) or parted_major > 3:
        return False

    # Older parted versions return a message in the stdout and RC > 0.
    rc, out, err = module.run_command("%s -s -m %s print" % (parted_exec, device))
    if rc != 0 and 'unrecognised disk label' in out.lower():
        return True

    return False


def parse_parted_version(out):
    """
    Returns version tuple from the output of "parted --version" command
    """
    lines = [x for x in out.split('\n') if x.strip() != '']
    if len(lines) == 0:
        return None, None, None

    # Sample parted versions (see as well test unit):
    # parted (GNU parted) 3.3
    # parted (GNU parted) 3.4.5
    # parted (GNU parted) 3.3.14-dfc61
    matches = re.search(r'^parted.+\s(\d+)\.(\d+)(?:\.(\d+))?', lines[0].strip())

    if matches is None:
        return None, None, None

    # Convert version to numbers
    major = int(matches.group(1))
    minor = int(matches.group(2))
    rev = 0
    if matches.group(3) is not None:
        rev = int(matches.group(3))

    return major, minor, rev


def parted_version():
    """
    Returns the major and minor version of parted installed on the system.
    """
    global module, parted_exec

    rc, out, err = module.run_command("%s --version" % parted_exec)
    if rc != 0:
        module.fail_json(
            msg="Failed to get parted version.", rc=rc, out=out, err=err
        )

    (major, minor, rev) = parse_parted_version(out)
    if major is None:
        module.fail_json(msg="Failed to get parted version.", rc=0, out=out)

    return major, minor, rev


def parted(script, device, align):
    """
    Runs a parted script.
    """
    global module, parted_exec

    align_option = '-a %s' % align
    if align == 'undefined':
        align_option = ''

    if script and not module.check_mode:
        command = "%s -s -m %s %s -- %s" % (parted_exec, align_option, device, script)
        rc, out, err = module.run_command(command)

        if rc != 0:
            module.fail_json(
                msg="Error while running parted script: %s" % command.strip(),
                rc=rc, out=out, err=err
            )


def read_record(file_path, default=None):
    """
    Reads the first line of a file and returns it.
    """
    try:
        f = open(file_path, 'r')
        try:
            return f.readline().strip()
        finally:
            f.close()
    except IOError:
        return default


def part_exists(partitions, attribute, number):
    """
    Looks if a partition that has a specific value for a specific attribute
    actually exists.
    """
    return any(
        part[attribute] and
        part[attribute] == number for part in partitions
    )


def check_size_format(size_str):
    """
    Checks if the input string is an allowed size
    """
    size, unit = parse_unit(size_str)
    return unit in parted_units


def main():
    global module, units_si, units_iec, parted_exec

    changed = False
    output_script = ""
    script = ""
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type='str', required=True),
            align=dict(type='str', default='optimal', choices=['cylinder', 'minimal', 'none', 'optimal', 'undefined']),
            number=dict(type='int'),

            # unit <unit> command
            unit=dict(type='str', default='KiB', choices=parted_units),

            # mklabel <label-type> command
            label=dict(type='str', default='msdos', choices=['aix', 'amiga', 'bsd', 'dvh', 'gpt', 'loop', 'mac', 'msdos', 'pc98', 'sun']),

            # mkpart <part-type> [<fs-type>] <start> <end> command
            part_type=dict(type='str', default='primary', choices=['extended', 'logical', 'primary']),
            part_start=dict(type='str', default='0%'),
            part_end=dict(type='str', default='100%'),
            fs_type=dict(type='str'),

            # name <partition> <name> command
            name=dict(type='str'),

            # set <partition> <flag> <state> command
            flags=dict(type='list', elements='str'),

            # rm/mkpart command
            state=dict(type='str', default='info', choices=['absent', 'info', 'present']),

            # resize part
            resize=dict(type='bool', default=False),
        ),
        required_if=[
            ['state', 'present', ['number']],
            ['state', 'absent', ['number']],
        ],
        supports_check_mode=True,
    )
    module.run_command_environ_update = {'LANG': 'C', 'LC_ALL': 'C', 'LC_MESSAGES': 'C', 'LC_CTYPE': 'C'}

    # Data extraction
    device = module.params['device']
    align = module.params['align']
    number = module.params['number']
    unit = module.params['unit']
    label = module.params['label']
    part_type = module.params['part_type']
    part_start = module.params['part_start']
    part_end = module.params['part_end']
    name = module.params['name']
    state = module.params['state']
    flags = module.params['flags']
    fs_type = module.params['fs_type']
    resize = module.params['resize']

    # Parted executable
    parted_exec = module.get_bin_path('parted', True)

    # Conditioning
    if number is not None and number < 1:
        module.fail_json(msg="The partition number must be greater then 0.")
    if not check_size_format(part_start):
        module.fail_json(
            msg="The argument 'part_start' doesn't respect required format."
                "The size unit is case sensitive.",
            err=parse_unit(part_start)
        )
    if not check_size_format(part_end):
        module.fail_json(
            msg="The argument 'part_end' doesn't respect required format."
                "The size unit is case sensitive.",
            err=parse_unit(part_end)
        )

    # Read the current disk information
    current_device = get_device_info(device, unit)
    current_parts = current_device['partitions']

    if state == 'present':

        # Assign label if required
        mklabel_needed = current_device['generic'].get('table', None) != label
        if mklabel_needed:
            script += "mklabel %s " % label

        # Create partition if required
        if part_type and (mklabel_needed or not part_exists(current_parts, 'num', number)):
            script += "mkpart %s %s%s %s " % (
                part_type,
                '%s ' % fs_type if fs_type is not None else '',
                part_start,
                part_end
            )

        # Set the unit of the run
        if unit and script:
            script = "unit %s %s" % (unit, script)

        # If partition exists, try to resize
        if resize and part_exists(current_parts, 'num', number):
            # Ensure new end is different to current
            partition = [p for p in current_parts if p['num'] == number][0]
            current_part_end = convert_to_bytes(partition['end'], unit)

            size, parsed_unit = parse_unit(part_end, unit)
            if parsed_unit == "%":
                size = int((int(current_device['generic']['size']) * size) / 100)
                parsed_unit = unit

            desired_part_end = convert_to_bytes(size, parsed_unit)

            if current_part_end != desired_part_end:
                script += "resizepart %s %s " % (
                    number,
                    part_end
                )

        # Execute the script and update the data structure.
        # This will create the partition for the next steps
        if script:
            output_script += script
            parted(script, device, align)
            changed = True
            script = ""

            if not module.check_mode:
                current_parts = get_device_info(device, unit)['partitions']

        if part_exists(current_parts, 'num', number) or module.check_mode:
            if changed and module.check_mode:
                partition = {'flags': []}   # Empty structure for the check-mode
            else:
                partition = [p for p in current_parts if p['num'] == number][0]

            # Assign name to the partition
            if name is not None and partition.get('name', None) != name:
                # Wrap double quotes in single quotes so the shell doesn't strip
                # the double quotes as those need to be included in the arg
                # passed to parted
                script += 'name %s \'"%s"\' ' % (number, name)

            # Manage flags
            if flags:
                # Parted infers boot with esp, if you assign esp, boot is set
                # and if boot is unset, esp is also unset.
                if 'esp' in flags and 'boot' not in flags:
                    flags.append('boot')

                # Compute only the changes in flags status
                flags_off = list(set(partition['flags']) - set(flags))
                flags_on = list(set(flags) - set(partition['flags']))

                for f in flags_on:
                    script += "set %s %s on " % (number, f)

                for f in flags_off:
                    script += "set %s %s off " % (number, f)

        # Set the unit of the run
        if unit and script:
            script = "unit %s %s" % (unit, script)

        # Execute the script
        if script:
            output_script += script
            changed = True
            parted(script, device, align)

    elif state == 'absent':
        # Remove the partition
        if part_exists(current_parts, 'num', number) or module.check_mode:
            script = "rm %s " % number
            output_script += script
            changed = True
            parted(script, device, align)

    elif state == 'info':
        output_script = "unit '%s' print " % unit

    # Final status of the device
    final_device_status = get_device_info(device, unit)
    module.exit_json(
        changed=changed,
        disk=final_device_status['generic'],
        partitions=final_device_status['partitions'],
        script=output_script.strip()
    )


if __name__ == '__main__':
    main()
