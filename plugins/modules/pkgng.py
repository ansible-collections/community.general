#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, bleader
# Written by bleader <bleader@ratonland.org>
# Based on pkgin module written by Shaun Zinck <shaun.zinck at gmail.com>
# that was based on pacman module written by Afterburn <https://github.com/afterburn>
#  that was based on apt module written by Matthew Williams <matthew@flowroute.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pkgng
short_description: Package manager for FreeBSD >= 9.0
description:
    - Manage binary packages for FreeBSD using 'pkgng' which is available in versions after 9.0.
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
        description:
            - Name or list of names of packages to install/remove.
            - "With O(name=*), O(state=latest) will operate, but O(state=present) and O(state=absent) will be noops."
        required: true
        aliases: [pkg]
        type: list
        elements: str
    state:
        description:
            - State of the package.
        choices: [ 'present', 'latest', 'absent' ]
        required: false
        default: present
        type: str
    cached:
        description:
            - Use local package base instead of fetching an updated one.
        type: bool
        required: false
        default: false
    annotation:
        description:
            - A list of keyvalue-pairs of the form
              C(<+/-/:><key>[=<value>]). A V(+) denotes adding an annotation, a
              V(-) denotes removing an annotation, and V(:) denotes modifying an
              annotation.
              If setting or modifying annotations, a value must be provided.
        required: false
        type: list
        elements: str
    pkgsite:
        description:
            - For pkgng versions before 1.1.4, specify packagesite to use
              for downloading packages. If not specified, use settings from
              C(/usr/local/etc/pkg.conf).
            - For newer pkgng versions, specify a the name of a repository
              configured in C(/usr/local/etc/pkg/repos).
        required: false
        type: str
    rootdir:
        description:
            - For pkgng versions 1.5 and later, pkg will install all packages
              within the specified root directory.
            - Can not be used together with O(chroot) or O(jail) options.
        required: false
        type: path
    chroot:
        description:
            - Pkg will chroot in the specified environment.
            - Can not be used together with O(rootdir) or O(jail) options.
        required: false
        type: path
    jail:
        description:
            - Pkg will execute in the given jail name or id.
            - Can not be used together with O(chroot) or O(rootdir) options.
        type: str
    autoremove:
        description:
            - Remove automatically installed packages which are no longer needed.
        required: false
        type: bool
        default: false
    ignore_osver:
        description:
            - Ignore FreeBSD OS version check, useful on -STABLE and -CURRENT branches.
            - Defines the E(IGNORE_OSVERSION) environment variable.
        required: false
        type: bool
        default: false
        version_added: 1.3.0
    use_globs:
        description:
            - Treat the package names as shell glob patterns.
        required: false
        type: bool
        default: true
        version_added: 9.3.0
author: "bleader (@bleader)"
notes:
  - When using pkgsite, be careful that already in cache packages won't be downloaded again.
  - When used with a C(loop:) each package will be processed individually,
    it is much more efficient to pass the list directly to the O(name) option.
'''

EXAMPLES = '''
- name: Install package foo
  community.general.pkgng:
    name: foo
    state: present

- name: Annotate package foo and bar
  community.general.pkgng:
    name:
      - foo
      - bar
    annotation: '+test1=baz,-test2,:test3=foobar'

- name: Remove packages foo and bar
  community.general.pkgng:
    name:
      - foo
      - bar
    state: absent

- name: Upgrade package baz
  community.general.pkgng:
    name: baz
    state: latest

- name: Upgrade all installed packages (see warning for the name option first!)
  community.general.pkgng:
    name: "*"
    state: latest

- name: Upgrade foo/bar
  community.general.pkgng:
    name: foo/bar
    state: latest
    use_globs: false
'''


from collections import defaultdict
import re
from ansible.module_utils.basic import AnsibleModule


def query_package(module, run_pkgng, name):

    rc, out, err = run_pkgng('info', '-e', name)

    return rc == 0


def query_update(module, run_pkgng, name):

    # Check to see if a package upgrade is available.
    # rc = 0, no updates available or package not installed
    # rc = 1, updates available
    rc, out, err = run_pkgng('upgrade', '-n', name)

    return rc == 1


def pkgng_older_than(module, pkgng_path, compare_version):

    rc, out, err = module.run_command([pkgng_path, '-v'])
    version = [int(x) for x in re.split(r'[\._]', out)]

    i = 0
    new_pkgng = True
    while compare_version[i] == version[i]:
        i += 1
        if i == min(len(compare_version), len(version)):
            break
    else:
        if compare_version[i] > version[i]:
            new_pkgng = False
    return not new_pkgng


def upgrade_packages(module, run_pkgng):
    # Run a 'pkg upgrade', updating all packages.
    upgraded_c = 0

    pkgng_args = ['upgrade']
    pkgng_args.append('-n' if module.check_mode else '-y')
    rc, out, err = run_pkgng(*pkgng_args, check_rc=(not module.check_mode))

    matches = re.findall('^Number of packages to be (?:upgraded|reinstalled): ([0-9]+)', out, re.MULTILINE)
    for match in matches:
        upgraded_c += int(match)

    if upgraded_c > 0:
        return (True, "updated %s package(s)" % upgraded_c, out, err)
    return (False, "no packages need upgrades", out, err)


def remove_packages(module, run_pkgng, packages):
    remove_c = 0
    stdout = ""
    stderr = ""
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, run_pkgng, package):
            continue

        if not module.check_mode:
            rc, out, err = run_pkgng('delete', '-y', package)
            stdout += out
            stderr += err

        if not module.check_mode and query_package(module, run_pkgng, package):
            module.fail_json(msg="failed to remove %s: %s" % (package, out), stdout=stdout, stderr=stderr)

        remove_c += 1

    if remove_c > 0:
        return (True, "removed %s package(s)" % remove_c, stdout, stderr)

    return (False, "package(s) already absent", stdout, stderr)


def install_packages(module, run_pkgng, packages, cached, state):
    action_queue = defaultdict(list)
    action_count = defaultdict(int)
    stdout = ""
    stderr = ""

    if not module.check_mode and not cached:
        rc, out, err = run_pkgng('update')
        stdout += out
        stderr += err
        if rc != 0:
            module.fail_json(msg="Could not update catalogue [%d]: %s %s" % (rc, out, err), stdout=stdout, stderr=stderr)

    for package in packages:
        already_installed = query_package(module, run_pkgng, package)
        if already_installed and state == "present":
            continue

        if (
            already_installed and state == "latest"
            and not query_update(module, run_pkgng, package)
        ):
            continue

        if already_installed:
            action_queue["upgrade"].append(package)
        else:
            action_queue["install"].append(package)

    # install/upgrade all named packages with one pkg command
    for (action, package_list) in action_queue.items():
        if module.check_mode:
            # Do nothing, but count up how many actions
            # would be performed so that the changed/msg
            # is correct.
            action_count[action] += len(package_list)
            continue

        pkgng_args = [action, '-U', '-y'] + package_list
        rc, out, err = run_pkgng(*pkgng_args)
        stdout += out
        stderr += err

        # individually verify packages are in requested state
        for package in package_list:
            verified = False
            if action == 'install':
                verified = query_package(module, run_pkgng, package)
            elif action == 'upgrade':
                verified = not query_update(module, run_pkgng, package)

            if verified:
                action_count[action] += 1
            else:
                module.fail_json(msg="failed to %s %s" % (action, package), stdout=stdout, stderr=stderr)

    if sum(action_count.values()) > 0:
        past_tense = {'install': 'installed', 'upgrade': 'upgraded'}
        messages = []
        for (action, count) in action_count.items():
            messages.append("%s %s package%s" % (past_tense.get(action, action), count, "s" if count != 1 else ""))

        return (True, '; '.join(messages), stdout, stderr)

    return (False, "package(s) already %s" % (state), stdout, stderr)


def annotation_query(module, run_pkgng, package, tag):
    rc, out, err = run_pkgng('info', '-A', package)
    match = re.search(r'^\s*(?P<tag>%s)\s*:\s*(?P<value>\w+)' % tag, out, flags=re.MULTILINE)
    if match:
        return match.group('value')
    return False


def annotation_add(module, run_pkgng, package, tag, value):
    _value = annotation_query(module, run_pkgng, package, tag)
    if not _value:
        # Annotation does not exist, add it.
        if not module.check_mode:
            rc, out, err = run_pkgng('annotate', '-y', '-A', package, tag, data=value, binary_data=True)
            if rc != 0:
                module.fail_json(msg="could not annotate %s: %s"
                                 % (package, out), stderr=err)
        return True
    elif _value != value:
        # Annotation exists, but value differs
        module.fail_json(
            msg="failed to annotate %s, because %s is already set to %s, but should be set to %s"
            % (package, tag, _value, value))
        return False
    else:
        # Annotation exists, nothing to do
        return False


def annotation_delete(module, run_pkgng, package, tag, value):
    _value = annotation_query(module, run_pkgng, package, tag)
    if _value:
        if not module.check_mode:
            rc, out, err = run_pkgng('annotate', '-y', '-D', package, tag)
            if rc != 0:
                module.fail_json(msg="could not delete annotation to %s: %s"
                                 % (package, out), stderr=err)
        return True
    return False


def annotation_modify(module, run_pkgng, package, tag, value):
    _value = annotation_query(module, run_pkgng, package, tag)
    if not _value:
        # No such tag
        module.fail_json(msg="could not change annotation to %s: tag %s does not exist"
                         % (package, tag))
    elif _value == value:
        # No change in value
        return False
    else:
        if not module.check_mode:
            rc, out, err = run_pkgng('annotate', '-y', '-M', package, tag, data=value, binary_data=True)

            # pkg sometimes exits with rc == 1, even though the modification succeeded
            # Check the output for a success message
            if (
                rc != 0
                and re.search(r'^%s-[^:]+: Modified annotation tagged: %s' % (package, tag), out, flags=re.MULTILINE) is None
            ):
                module.fail_json(msg="failed to annotate %s, could not change annotation %s to %s: %s"
                                 % (package, tag, value, out), stderr=err)
        return True


def annotate_packages(module, run_pkgng, packages, annotations):
    annotate_c = 0
    if len(annotations) == 1:
        # Split on commas with optional trailing whitespace,
        # to support the old style of multiple annotations
        # on a single line, rather than YAML list syntax
        annotations = re.split(r'\s*,\s*', annotations[0])

    operation = {
        '+': annotation_add,
        '-': annotation_delete,
        ':': annotation_modify
    }

    for package in packages:
        for annotation_string in annotations:
            # Note to future maintainers: A dash (-) in a regex character class ([-+:] below)
            # must appear as the first character in the class, or it will be interpreted
            # as a range of characters.
            annotation = \
                re.match(r'(?P<operation>[-+:])(?P<tag>[^=]+)(=(?P<value>.+))?', annotation_string)

            if annotation is None:
                module.fail_json(
                    msg="failed to annotate %s, invalid annotate string: %s"
                    % (package, annotation_string)
                )

            annotation = annotation.groupdict()
            if operation[annotation['operation']](module, run_pkgng, package, annotation['tag'], annotation['value']):
                annotate_c += 1

    if annotate_c > 0:
        return (True, "added %s annotations." % annotate_c)
    return (False, "changed no annotations")


def autoremove_packages(module, run_pkgng):
    stdout = ""
    stderr = ""
    rc, out, err = run_pkgng('autoremove', '-n')

    autoremove_c = 0

    match = re.search('^Deinstallation has been requested for the following ([0-9]+) packages', out, re.MULTILINE)
    if match:
        autoremove_c = int(match.group(1))

    if autoremove_c == 0:
        return (False, "no package(s) to autoremove", stdout, stderr)

    if not module.check_mode:
        rc, out, err = run_pkgng('autoremove', '-y')
        stdout += out
        stderr += err

    return (True, "autoremoved %d package(s)" % (autoremove_c), stdout, stderr)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "latest", "absent"], required=False),
            name=dict(aliases=["pkg"], required=True, type='list', elements='str'),
            cached=dict(default=False, type='bool'),
            ignore_osver=dict(default=False, required=False, type='bool'),
            annotation=dict(required=False, type='list', elements='str'),
            pkgsite=dict(required=False),
            rootdir=dict(required=False, type='path'),
            chroot=dict(required=False, type='path'),
            jail=dict(required=False, type='str'),
            autoremove=dict(default=False, type='bool'),
            use_globs=dict(default=True, required=False, type='bool'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["rootdir", "chroot", "jail"]])

    pkgng_path = module.get_bin_path('pkg', True)

    p = module.params

    pkgs = p["name"]

    changed = False
    msgs = []
    stdout = ""
    stderr = ""
    dir_arg = None

    if p["rootdir"] is not None:
        rootdir_not_supported = pkgng_older_than(module, pkgng_path, [1, 5, 0])
        if rootdir_not_supported:
            module.fail_json(msg="To use option 'rootdir' pkg version must be 1.5 or greater")
        else:
            dir_arg = "--rootdir=%s" % (p["rootdir"])

    if p["ignore_osver"]:
        ignore_osver_not_supported = pkgng_older_than(module, pkgng_path, [1, 11, 0])
        if ignore_osver_not_supported:
            module.fail_json(msg="To use option 'ignore_osver' pkg version must be 1.11 or greater")

    if p["chroot"] is not None:
        dir_arg = '--chroot=%s' % (p["chroot"])

    if p["jail"] is not None:
        dir_arg = '--jail=%s' % (p["jail"])

    # as of pkg-1.1.4, PACKAGESITE is deprecated in favor of repository definitions
    # in /usr/local/etc/pkg/repos
    repo_flag_not_supported = pkgng_older_than(module, pkgng_path, [1, 1, 4])

    def run_pkgng(action, *args, **kwargs):
        cmd = [pkgng_path, dir_arg, action]

        if p["use_globs"] and action in ('info', 'install', 'upgrade',):
            args = ('-g',) + args

        pkgng_env = {'BATCH': 'yes'}

        if p["ignore_osver"]:
            pkgng_env['IGNORE_OSVERSION'] = 'yes'

        if p['pkgsite'] is not None and action in ('update', 'install', 'upgrade',):
            if repo_flag_not_supported:
                pkgng_env['PACKAGESITE'] = p['pkgsite']
            else:
                cmd.append('--repository=%s' % (p['pkgsite'],))

        # If environ_update is specified to be "passed through"
        # to module.run_command, then merge its values into pkgng_env
        pkgng_env.update(kwargs.pop('environ_update', dict()))

        return module.run_command(cmd + list(args), environ_update=pkgng_env, **kwargs)

    if pkgs == ['*'] and p["state"] == 'latest':
        # Operate on all installed packages. Only state: latest makes sense here.
        _changed, _msg, _stdout, _stderr = upgrade_packages(module, run_pkgng)
        changed = changed or _changed
        stdout += _stdout
        stderr += _stderr
        msgs.append(_msg)

    # Operate on named packages
    if len(pkgs) == 1:
        # The documentation used to show multiple packages specified in one line
        # with comma or space delimiters. That doesn't result in a YAML list, and
        # wrong actions (install vs upgrade) can be reported if those
        # comma- or space-delimited strings make it to the pkg command line.
        pkgs = re.split(r'[,\s]', pkgs[0])
    named_packages = [pkg for pkg in pkgs if pkg != '*']
    if p["state"] in ("present", "latest") and named_packages:
        _changed, _msg, _out, _err = install_packages(module, run_pkgng, named_packages,
                                                      p["cached"], p["state"])
        stdout += _out
        stderr += _err
        changed = changed or _changed
        msgs.append(_msg)

    elif p["state"] == "absent" and named_packages:
        _changed, _msg, _out, _err = remove_packages(module, run_pkgng, named_packages)
        stdout += _out
        stderr += _err
        changed = changed or _changed
        msgs.append(_msg)

    if p["autoremove"]:
        _changed, _msg, _stdout, _stderr = autoremove_packages(module, run_pkgng)
        changed = changed or _changed
        stdout += _stdout
        stderr += _stderr
        msgs.append(_msg)

    if p["annotation"] is not None:
        _changed, _msg = annotate_packages(module, run_pkgng, pkgs, p["annotation"])
        changed = changed or _changed
        msgs.append(_msg)

    module.exit_json(changed=changed, msg=", ".join(msgs), stdout=stdout, stderr=stderr)


if __name__ == '__main__':
    main()
