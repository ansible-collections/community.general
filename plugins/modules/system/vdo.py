#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Red Hat, Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
author:
    - Bryan Gurney (@bgurney-rh)

module: vdo

short_description: Module to control VDO


description:
    - This module controls the VDO dedupe and compression device.
    - VDO, or Virtual Data Optimizer, is a device-mapper target that
      provides inline block-level deduplication, compression, and
      thin provisioning capabilities to primary storage.

options:
    name:
        description:
            - The name of the VDO volume.
        type: str
        required: true
    state:
        description:
            - Whether this VDO volume should be "present" or "absent".
              If a "present" VDO volume does not exist, it will be
              created.  If a "present" VDO volume already exists, it
              will be modified, by updating the configuration, which
              will take effect when the VDO volume is restarted.
              Not all parameters of an existing VDO volume can be
              modified; the "statusparamkeys" list contains the
              parameters that can be modified after creation. If an
              "absent" VDO volume does not exist, it will not be
              removed.
        type: str
        choices: [ absent, present ]
        default: present
    activated:
        description:
            - The "activate" status for a VDO volume.  If this is set
              to C(false), the VDO volume cannot be started, and it will
              not start on system startup.  However, on initial
              creation, a VDO volume with "activated" set to "off"
              will be running, until stopped.  This is the default
              behavior of the "vdo create" command; it provides the
              user an opportunity to write a base amount of metadata
              (filesystem, LVM headers, etc.) to the VDO volume prior
              to stopping the volume, and leaving it deactivated
              until ready to use.
        type: bool
    running:
        description:
            - Whether this VDO volume is running.
            - A VDO volume must be activated in order to be started.
        type: bool
    device:
        description:
            - The full path of the device to use for VDO storage.
            - This is required if "state" is "present".
        type: str
    logicalsize:
        description:
            - The logical size of the VDO volume (in megabytes, or
              LVM suffix format).  If not specified for a new volume,
              this defaults to the same size as the underlying storage
              device, which is specified in the 'device' parameter.
              Existing volumes will maintain their size if the
              logicalsize parameter is not specified, or is smaller
              than or identical to the current size.  If the specified
              size is larger than the current size, a growlogical
              operation will be performed.
        type: str
    deduplication:
        description:
            - Configures whether deduplication is enabled.  The
              default for a created volume is 'enabled'.  Existing
              volumes will maintain their previously configured
              setting unless a different value is specified in the
              playbook.
        type: str
        choices: [ disabled, enabled ]
    compression:
        description:
            - Configures whether compression is enabled.  The default
              for a created volume is 'enabled'.  Existing volumes
              will maintain their previously configured setting unless
              a different value is specified in the playbook.
        type: str
        choices: [ disabled, enabled ]
    blockmapcachesize:
        description:
            - The amount of memory allocated for caching block map
              pages, in megabytes (or may be issued with an LVM-style
              suffix of K, M, G, or T).  The default (and minimum)
              value is 128M.  The value specifies the size of the
              cache; there is a 15% memory usage overhead. Each 1.25G
              of block map covers 1T of logical blocks, therefore a
              small amount of block map cache memory can cache a
              significantly large amount of block map data.  Existing
              volumes will maintain their previously configured
              setting unless a different value is specified in the
              playbook.
        type: str
    readcache:
        description:
            - Enables or disables the read cache.  The default is
              'disabled'.  Choosing 'enabled' enables a read cache
              which may improve performance for workloads of high
              deduplication, read workloads with a high level of
              compression, or on hard disk storage.  Existing
              volumes will maintain their previously configured
              setting unless a different value is specified in the
              playbook.
            - The read cache feature is available in VDO 6.1 and older.
        type: str
        choices: [ disabled, enabled ]
    readcachesize:
        description:
            - Specifies the extra VDO device read cache size in
              megabytes.  This is in addition to a system-defined
              minimum.  Using a value with a suffix of K, M, G, or T
              is optional.  The default value is 0.  1.125 MB of
              memory per bio thread will be used per 1 MB of read
              cache specified (for example, a VDO volume configured
              with 4 bio threads will have a read cache memory usage
              overhead of 4.5 MB per 1 MB of read cache specified).
              Existing volumes will maintain their previously
              configured setting unless a different value is specified
              in the playbook.
            - The read cache feature is available in VDO 6.1 and older.
        type: str
    emulate512:
        description:
            - Enables 512-byte emulation mode, allowing drivers or
              filesystems to access the VDO volume at 512-byte
              granularity, instead of the default 4096-byte granularity.
              Default is 'disabled'; only recommended when a driver
              or filesystem requires 512-byte sector level access to
              a device.  This option is only available when creating
              a new volume, and cannot be changed for an existing
              volume.
        type: bool
        default: false
    growphysical:
        description:
            - Specifies whether to attempt to execute a growphysical
              operation, if there is enough unused space on the
              device.  A growphysical operation will be executed if
              there is at least 64 GB of free space, relative to the
              previous physical size of the affected VDO volume.
        type: bool
        default: false
    slabsize:
        description:
            - The size of the increment by which the physical size of
              a VDO volume is grown, in megabytes (or may be issued
              with an LVM-style suffix of K, M, G, or T).  Must be a
              power of two between 128M and 32G.  The default is 2G,
              which supports volumes having a physical size up to 16T.
              The maximum, 32G, supports a physical size of up to 256T.
              This option is only available when creating a new
              volume, and cannot be changed for an existing volume.
        type: str
    writepolicy:
        description:
            - Specifies the write policy of the VDO volume.  The
              'sync' mode acknowledges writes only after data is on
              stable storage.  The 'async' mode acknowledges writes
              when data has been cached for writing to stable
              storage.  The default (and highly recommended) 'auto'
              mode checks the storage device to determine whether it
              supports flushes.  Devices that support flushes will
              result in a VDO volume in 'async' mode, while devices
              that do not support flushes will run in sync mode.
              Existing volumes will maintain their previously
              configured setting unless a different value is
              specified in the playbook.
        type: str
        choices: [ async, auto, sync ]
    indexmem:
        description:
            - Specifies the amount of index memory in gigabytes.  The
              default is 0.25.  The special decimal values 0.25, 0.5,
              and 0.75 can be used, as can any positive integer.
              This option is only available when creating a new
              volume, and cannot be changed for an existing volume.
        type: str
    indexmode:
        description:
            - Specifies the index mode of the Albireo index.  The
              default is 'dense', which has a deduplication window of
              1 GB of index memory per 1 TB of incoming data,
              requiring 10 GB of index data on persistent storage.
              The 'sparse' mode has a deduplication window of 1 GB of
              index memory per 10 TB of incoming data, but requires
              100 GB of index data on persistent storage.  This option
              is only available when creating a new volume, and cannot
              be changed for an existing volume.
        type: str
        choices: [ dense, sparse ]
    ackthreads:
        description:
            - Specifies the number of threads to use for
              acknowledging completion of requested VDO I/O operations.
              Valid values are integer values from 1 to 100 (lower
              numbers are preferable due to overhead).  The default is
              1.  Existing volumes will maintain their previously
              configured setting unless a different value is specified
              in the playbook.
        type: str
    biothreads:
        description:
            - Specifies the number of threads to use for submitting I/O
              operations to the storage device.  Valid values are
              integer values from 1 to 100 (lower numbers are
              preferable due to overhead).  The default is 4.
              Existing volumes will maintain their previously
              configured setting unless a different value is specified
              in the playbook.
        type: str
    cputhreads:
        description:
            - Specifies the number of threads to use for CPU-intensive
              work such as hashing or compression.  Valid values are
              integer values from 1 to 100 (lower numbers are
              preferable due to overhead).  The default is 2.
              Existing volumes will maintain their previously
              configured setting unless a different value is specified
              in the playbook.
        type: str
    logicalthreads:
        description:
            - Specifies the number of threads across which to
              subdivide parts of the VDO processing based on logical
              block addresses.  Valid values are integer values from
              1 to 100 (lower numbers are preferable due to overhead).
              The default is 1.  Existing volumes will maintain their
              previously configured setting unless a different value
              is specified in the playbook.
        type: str
    physicalthreads:
        description:
            - Specifies the number of threads across which to
              subdivide parts of the VDO processing based on physical
              block addresses.  Valid values are integer values from
              1 to 16 (lower numbers are preferable due to overhead).
              The physical space used by the VDO volume must be
              larger than (slabsize * physicalthreads).  The default
              is 1.  Existing volumes will maintain their previously
              configured setting unless a different value is specified
              in the playbook.
        type: str
    force:
        description:
            - When creating a volume, ignores any existing file system
              or VDO signature already present in the storage device.
              When stopping or removing a VDO volume, first unmounts
              the file system stored on the device if mounted.
            - "B(Warning:) Since this parameter removes all safety
              checks it is important to make sure that all parameters
              provided are accurate and intentional."
        type: bool
        default: false
        version_added: 2.4.0
notes:
  - In general, the default thread configuration should be used.
requirements:
  - PyYAML
  - kmod-kvdo
  - vdo
'''

EXAMPLES = r'''
- name: Create 2 TB VDO volume vdo1 on device /dev/md0
  community.general.vdo:
    name: vdo1
    state: present
    device: /dev/md0
    logicalsize: 2T

- name: Remove VDO volume vdo1
  community.general.vdo:
    name: vdo1
    state: absent
'''

RETURN = r'''#  '''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import re
import traceback

YAML_IMP_ERR = None
try:
    import yaml
    HAS_YAML = True
except ImportError:
    YAML_IMP_ERR = traceback.format_exc()
    HAS_YAML = False


# Generate a list of VDO volumes, whether they are running or stopped.
#
# @param module  The AnsibleModule object.
# @param vdocmd  The path of the 'vdo' command.
#
# @return vdolist  A list of currently created VDO volumes.
def inventory_vdos(module, vdocmd):
    rc, vdostatusout, err = module.run_command([vdocmd, "status"])

    # if rc != 0:
    #   module.fail_json(msg="Inventorying VDOs failed: %s"
    #                        % vdostatusout, rc=rc, err=err)

    vdolist = []

    if rc == 2 and re.findall(r"vdoconf\.yml does not exist", err, re.MULTILINE):
        # If there is no /etc/vdoconf.yml file, assume there are no
        # VDO volumes. Return an empty list of VDO volumes.
        return vdolist

    if rc != 0:
        module.fail_json(msg="Inventorying VDOs failed: %s" % vdostatusout, rc=rc, err=err)

    vdostatusyaml = yaml.safe_load(vdostatusout)
    if vdostatusyaml is None:
        return vdolist

    vdoyamls = vdostatusyaml['VDOs']

    if vdoyamls is not None:
        vdolist = list(vdoyamls.keys())

    return vdolist


def list_running_vdos(module, vdocmd):
    rc, vdolistout, err = module.run_command([vdocmd, "list"])
    runningvdolist = filter(None, vdolistout.split('\n'))
    return runningvdolist


# Generate a string containing options to pass to the 'VDO' command.
# Note that a 'create' operation will pass more options than a
# 'modify' operation.
#
# @param params  A dictionary of parameters, and their values
#                (values of 'None' and/or nonexistent values are ignored).
#
# @return vdocmdoptions  A string to be used in a 'vdo <action>' command.
def start_vdo(module, vdoname, vdocmd):
    rc, out, err = module.run_command([vdocmd, "start", "--name=%s" % vdoname])
    if rc == 0:
        module.log("started VDO volume %s" % vdoname)
    return rc


def stop_vdo(module, vdoname, vdocmd):
    rc, out, err = module.run_command([vdocmd, "stop", "--name=%s" % vdoname])
    if rc == 0:
        module.log("stopped VDO volume %s" % vdoname)
    return rc


def activate_vdo(module, vdoname, vdocmd):
    rc, out, err = module.run_command([vdocmd, "activate", "--name=%s" % vdoname])
    if rc == 0:
        module.log("activated VDO volume %s" % vdoname)
    return rc


def deactivate_vdo(module, vdoname, vdocmd):
    rc, out, err = module.run_command([vdocmd, "deactivate", "--name=%s" % vdoname])
    if rc == 0:
        module.log("deactivated VDO volume %s" % vdoname)
    return rc


def add_vdooptions(params):
    options = []

    if params.get('logicalsize') is not None:
        options.append("--vdoLogicalSize=" + params['logicalsize'])

    if params.get('blockmapcachesize') is not None:
        options.append("--blockMapCacheSize=" + params['blockmapcachesize'])

    if params.get('readcache') == 'enabled':
        options.append("--readCache=enabled")

    if params.get('readcachesize') is not None:
        options.append("--readCacheSize=" + params['readcachesize'])

    if params.get('slabsize') is not None:
        options.append("--vdoSlabSize=" + params['slabsize'])

    if params.get('emulate512'):
        options.append("--emulate512=enabled")

    if params.get('indexmem') is not None:
        options.append("--indexMem=" + params['indexmem'])

    if params.get('indexmode') == 'sparse':
        options.append("--sparseIndex=enabled")

    if params.get('force'):
        options.append("--force")

    # Entering an invalid thread config results in a cryptic
    # 'Could not set up device mapper for %s' error from the 'vdo'
    # command execution.  The dmsetup module on the system will
    # output a more helpful message, but one would have to log
    # onto that system to read the error.  For now, heed the thread
    # limit warnings in the DOCUMENTATION section above.
    if params.get('ackthreads') is not None:
        options.append("--vdoAckThreads=" + params['ackthreads'])

    if params.get('biothreads') is not None:
        options.append("--vdoBioThreads=" + params['biothreads'])

    if params.get('cputhreads') is not None:
        options.append("--vdoCpuThreads=" + params['cputhreads'])

    if params.get('logicalthreads') is not None:
        options.append("--vdoLogicalThreads=" + params['logicalthreads'])

    if params.get('physicalthreads') is not None:
        options.append("--vdoPhysicalThreads=" + params['physicalthreads'])

    return options


def run_module():

    # Define the available arguments/parameters that a user can pass to
    # the module.
    # Defaults for VDO parameters are None, in order to facilitate
    # the detection of parameters passed from the playbook.
    # Creation param defaults are determined by the creation section.

    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        activated=dict(type='bool'),
        running=dict(type='bool'),
        growphysical=dict(type='bool', default=False),
        device=dict(type='str'),
        logicalsize=dict(type='str'),
        deduplication=dict(type='str', choices=['disabled', 'enabled']),
        compression=dict(type='str', choices=['disabled', 'enabled']),
        blockmapcachesize=dict(type='str'),
        readcache=dict(type='str', choices=['disabled', 'enabled']),
        readcachesize=dict(type='str'),
        emulate512=dict(type='bool', default=False),
        slabsize=dict(type='str'),
        writepolicy=dict(type='str', choices=['async', 'auto', 'sync']),
        indexmem=dict(type='str'),
        indexmode=dict(type='str', choices=['dense', 'sparse']),
        ackthreads=dict(type='str'),
        biothreads=dict(type='str'),
        cputhreads=dict(type='str'),
        logicalthreads=dict(type='str'),
        physicalthreads=dict(type='str'),
        force=dict(type='bool', default=False),
    )

    # Seed the result dictionary in the object.  There will be an
    # 'invocation' dictionary added with 'module_args' (arguments
    # given).
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )

    if not HAS_YAML:
        module.fail_json(msg=missing_required_lib('PyYAML'), exception=YAML_IMP_ERR)

    vdocmd = module.get_bin_path("vdo", required=True)
    if not vdocmd:
        module.fail_json(msg='VDO is not installed.', **result)

    # Print a pre-run list of VDO volumes in the result object.
    vdolist = inventory_vdos(module, vdocmd)

    runningvdolist = list_running_vdos(module, vdocmd)

    # Collect the name of the desired VDO volume, and its state.  These will
    # determine what to do.
    desiredvdo = module.params['name']
    state = module.params['state']

    # Create a desired VDO volume that doesn't exist yet.
    if (desiredvdo not in vdolist) and (state == 'present'):
        device = module.params['device']
        if device is None:
            module.fail_json(msg="Creating a VDO volume requires specifying "
                                 "a 'device' in the playbook.")

        # Create a dictionary of the options from the AnsibleModule
        # parameters, compile the vdo command options, and run "vdo create"
        # with those options.
        # Since this is a creation of a new VDO volume, it will contain all
        # all of the parameters given by the playbook; the rest will
        # assume default values.
        vdocmdoptions = add_vdooptions(module.params)
        rc, out, err = module.run_command(
            [vdocmd, "create", "--name=%s" % desiredvdo, "--device=%s" % device] + vdocmdoptions)
        if rc == 0:
            result['changed'] = True
        else:
            module.fail_json(msg="Creating VDO %s failed." % desiredvdo, rc=rc, err=err)

        if module.params['compression'] == 'disabled':
            rc, out, err = module.run_command([vdocmd, "disableCompression", "--name=%s" % desiredvdo])

        if module.params['deduplication'] == 'disabled':
            rc, out, err = module.run_command([vdocmd, "disableDeduplication", "--name=%s" % desiredvdo])

        if module.params['activated'] is False:
            deactivate_vdo(module, desiredvdo, vdocmd)

        if module.params['running'] is False:
            stop_vdo(module, desiredvdo, vdocmd)

        # Print a post-run list of VDO volumes in the result object.
        vdolist = inventory_vdos(module, vdocmd)
        module.log("created VDO volume %s" % desiredvdo)
        module.exit_json(**result)

    # Modify the current parameters of a VDO that exists.
    if desiredvdo in vdolist and state == 'present':
        rc, vdostatusoutput, err = module.run_command([vdocmd, "status"])
        vdostatusyaml = yaml.safe_load(vdostatusoutput)

        # An empty dictionary to contain dictionaries of VDO statistics
        processedvdos = {}

        vdoyamls = vdostatusyaml['VDOs']
        if vdoyamls is not None:
            processedvdos = vdoyamls

        # The 'vdo status' keys that are currently modifiable.
        statusparamkeys = ['Acknowledgement threads',
                           'Bio submission threads',
                           'Block map cache size',
                           'CPU-work threads',
                           'Logical threads',
                           'Physical threads',
                           'Read cache',
                           'Read cache size',
                           'Configured write policy',
                           'Compression',
                           'Deduplication']

        # A key translation table from 'vdo status' output to Ansible
        # module parameters.  This covers all of the 'vdo status'
        # parameter keys that could be modified with the 'vdo'
        # command.
        vdokeytrans = {
            'Logical size': 'logicalsize',
            'Compression': 'compression',
            'Deduplication': 'deduplication',
            'Block map cache size': 'blockmapcachesize',
            'Read cache': 'readcache',
            'Read cache size': 'readcachesize',
            'Configured write policy': 'writepolicy',
            'Acknowledgement threads': 'ackthreads',
            'Bio submission threads': 'biothreads',
            'CPU-work threads': 'cputhreads',
            'Logical threads': 'logicalthreads',
            'Physical threads': 'physicalthreads'
        }

        # Build a dictionary of the current VDO status parameters, with
        # the keys used by VDO.  (These keys will be converted later.)
        currentvdoparams = {}

        # Build a "lookup table" dictionary containing a translation table
        # of the parameters that can be modified
        modtrans = {}

        for statfield in statusparamkeys:
            if statfield in processedvdos[desiredvdo]:
                currentvdoparams[statfield] = processedvdos[desiredvdo][statfield]

            modtrans[statfield] = vdokeytrans[statfield]

        # Build a dictionary of current parameters formatted with the
        # same keys as the AnsibleModule parameters.
        currentparams = {}
        for paramkey in modtrans.keys():
            currentparams[modtrans[paramkey]] = modtrans[paramkey]

        diffparams = {}

        # Check for differences between the playbook parameters and the
        # current parameters. This will need a comparison function;
        # since AnsibleModule params are all strings, compare them as
        # strings (but if it's None; skip).
        for key in currentparams.keys():
            if module.params[key] is not None:
                if str(currentparams[key]) != module.params[key]:
                    diffparams[key] = module.params[key]

        if diffparams:
            vdocmdoptions = add_vdooptions(diffparams)
            if vdocmdoptions:
                rc, out, err = module.run_command([vdocmd, "modify", "--name=%s" % desiredvdo] + vdocmdoptions)
                if rc == 0:
                    result['changed'] = True
                else:
                    module.fail_json(msg="Modifying VDO %s failed."
                                     % desiredvdo, rc=rc, err=err)

            if 'deduplication' in diffparams.keys():
                dedupemod = diffparams['deduplication']
                dedupeparam = "disableDeduplication" if dedupemod == 'disabled' else "enableDeduplication"
                rc, out, err = module.run_command([vdocmd, dedupeparam, "--name=%s" % desiredvdo])

                if rc == 0:
                    result['changed'] = True
                else:
                    module.fail_json(msg="Changing deduplication on VDO volume %s failed." % desiredvdo, rc=rc, err=err)

            if 'compression' in diffparams.keys():
                compressmod = diffparams['compression']
                compressparam = "disableCompression" if compressmod == 'disabled' else "enableCompression"
                rc, out, err = module.run_command([vdocmd, compressparam, "--name=%s" % desiredvdo])
                if rc == 0:
                    result['changed'] = True
                else:
                    module.fail_json(msg="Changing compression on VDO volume %s failed." % desiredvdo, rc=rc, err=err)

            if 'writepolicy' in diffparams.keys():
                writepolmod = diffparams['writepolicy']
                rc, out, err = module.run_command([
                    vdocmd,
                    "changeWritePolicy",
                    "--name=%s" % desiredvdo,
                    "--writePolicy=%s" % writepolmod,
                ])

                if rc == 0:
                    result['changed'] = True
                else:
                    module.fail_json(msg="Changing write policy on VDO volume %s failed." % desiredvdo, rc=rc, err=err)

        # Process the size parameters, to determine of a growPhysical or
        # growLogical operation needs to occur.
        sizeparamkeys = ['Logical size', ]

        currentsizeparams = {}
        sizetrans = {}
        for statfield in sizeparamkeys:
            currentsizeparams[statfield] = processedvdos[desiredvdo][statfield]
            sizetrans[statfield] = vdokeytrans[statfield]

        sizeparams = {}
        for paramkey in currentsizeparams.keys():
            sizeparams[sizetrans[paramkey]] = currentsizeparams[paramkey]

        diffsizeparams = {}
        for key in sizeparams.keys():
            if module.params[key] is not None and str(sizeparams[key]) != module.params[key]:
                diffsizeparams[key] = module.params[key]

        if module.params['growphysical']:
            physdevice = module.params['device']
            rc, devsectors, err = module.run_command([module.get_bin_path("blockdev"), "--getsz", physdevice])
            devblocks = (int(devsectors) / 8)
            dmvdoname = ('/dev/mapper/' + desiredvdo)
            currentvdostats = processedvdos[desiredvdo]['VDO statistics'][dmvdoname]
            currentphysblocks = currentvdostats['physical blocks']

            # Set a growPhysical threshold to grow only when there is
            # guaranteed to be more than 2 slabs worth of unallocated
            # space on the device to use.  For now, set to device
            # size + 64 GB, since 32 GB is the largest possible
            # slab size.
            growthresh = devblocks + 16777216

            if currentphysblocks > growthresh:
                result['changed'] = True
                rc, out, err = module.run_command([vdocmd, "growPhysical", "--name=%s" % desiredvdo])

        if 'logicalsize' in diffsizeparams.keys():
            result['changed'] = True
            rc, out, err = module.run_command([vdocmd, "growLogical", "--name=%s" % desiredvdo, "--vdoLogicalSize=%s" % diffsizeparams['logicalsize']])

        vdoactivatestatus = processedvdos[desiredvdo]['Activate']

        if module.params['activated'] is False and vdoactivatestatus == 'enabled':
            deactivate_vdo(module, desiredvdo, vdocmd)
            if not result['changed']:
                result['changed'] = True

        if module.params['activated'] and vdoactivatestatus == 'disabled':
            activate_vdo(module, desiredvdo, vdocmd)
            if not result['changed']:
                result['changed'] = True

        if module.params['running'] is False and desiredvdo in runningvdolist:
            stop_vdo(module, desiredvdo, vdocmd)
            if not result['changed']:
                result['changed'] = True

        # Note that a disabled VDO volume cannot be started by the
        # 'vdo start' command, by design.  To accurately track changed
        # status, don't try to start a disabled VDO volume.
        # If the playbook contains 'activated: true', assume that
        # the activate_vdo() operation succeeded, as 'vdoactivatestatus'
        # will have the activated status prior to the activate_vdo()
        # call.
        if (vdoactivatestatus == 'enabled' or module.params['activated']) and module.params['running'] and desiredvdo not in runningvdolist:
            start_vdo(module, desiredvdo, vdocmd)
            if not result['changed']:
                result['changed'] = True

        # Print a post-run list of VDO volumes in the result object.
        vdolist = inventory_vdos(module, vdocmd)
        if diffparams:
            module.log("modified parameters of VDO volume %s" % desiredvdo)

        module.exit_json(**result)

    # Remove a desired VDO that currently exists.
    if desiredvdo in vdolist and state == 'absent':
        rc, out, err = module.run_command([vdocmd, "remove", "--name=%s" % desiredvdo])
        if rc == 0:
            result['changed'] = True
        else:
            module.fail_json(msg="Removing VDO %s failed." % desiredvdo, rc=rc, err=err)

        # Print a post-run list of VDO volumes in the result object.
        vdolist = inventory_vdos(module, vdocmd)
        module.log("removed VDO volume %s" % desiredvdo)
        module.exit_json(**result)

    # fall through
    # The state for the desired VDO volume was absent, and it does
    # not exist. Print a post-run list of VDO volumes in the result
    # object.
    vdolist = inventory_vdos(module, vdocmd)
    module.log("received request to remove non-existent VDO volume %s" % desiredvdo)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
