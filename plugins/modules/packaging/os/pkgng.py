#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, bleader
# Written by bleader <bleader@ratonland.org>
# Based on pkgin module written by Shaun Zinck <shaun.zinck at gmail.com>
# that was based on pacman module written by Afterburn <https://github.com/afterburn>
#  that was based on apt module written by Matthew Williams <matthew@flowroute.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pkgng
short_description: Package manager for FreeBSD >= 9.0
description:
    - Manage binary packages for FreeBSD using 'pkgng' which is available in versions after 9.0.
options:
    name:
        description:
            - Name or list of names of packages to install/remove.
            - "With I(name=*), I(state: latest) will operate, but I(state: present) and I(state: absent) will be noops."
            - >
                Warning: In Ansible 2.9 and earlier this module had a misfeature
                where I(name=*) with I(state: latest) or I(state: present) would
                install every package from every package repository, filling up
                the machines disk. Avoid using them unless you are certain that
                your role will only be used with newer versions.
        required: true
        aliases: [pkg]
        type: list
        elements: str
    state:
        description:
            - State of the package.
            - 'Note: "latest" added in 2.7'
        choices: [ 'present', 'latest', 'absent' ]
        required: false
        default: present
        type: str
    cached:
        description:
            - Use local package base instead of fetching an updated one.
        type: bool
        required: false
        default: no
    annotation:
        description:
            - A comma-separated list of keyvalue-pairs of the form
              C(<+/-/:><key>[=<value>]). A C(+) denotes adding an annotation, a
              C(-) denotes removing an annotation, and C(:) denotes modifying an
              annotation.
              If setting or modifying annotations, a value must be provided.
        required: false
        type: str
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
            - Can not be used together with I(chroot) or I(jail) options.
        required: false
        type: path
    chroot:
        description:
            - Pkg will chroot in the specified environment.
            - Can not be used together with I(rootdir) or I(jail) options.
        required: false
        type: path
    jail:
        description:
            - Pkg will execute in the given jail name or id.
            - Can not be used together with I(chroot) or I(rootdir) options.
        type: str
    autoremove:
        description:
            - Remove automatically installed packages which are no longer needed.
        required: false
        type: bool
        default: no
    ignore_osver:
        description:
            - Ignore FreeBSD OS version check, useful on -STABLE and -CURRENT branches.
            - Defines the C(IGNORE_OSVERSION) environment variable.
        required: false
        type: bool
        default: no
        version_added: 1.3.0
author: "bleader (@bleader)"
notes:
  - When using pkgsite, be careful that already in cache packages won't be downloaded again.
  - When used with a `loop:` each package will be processed individually,
    it is much more efficient to pass the list directly to the `name` option.
'''

EXAMPLES = '''
- name: Install package foo
  community.general.pkgng:
    name: foo
    state: present

- name: Annotate package foo and bar
  community.general.pkgng:
    name: foo,bar
    annotation: '+test1=baz,-test2,:test3=foobar'

- name: Remove packages foo and bar
  community.general.pkgng:
    name: foo,bar
    state: absent

# "latest" support added in 2.7
- name: Upgrade package baz
  community.general.pkgng:
    name: baz
    state: latest

- name: Upgrade all installed packages (see warning for the name option first!)
  community.general.pkgng:
    name: "*"
    state: latest
'''


from collections import defaultdict
import re
from ansible.module_utils.basic import AnsibleModule


def query_package(module, pkgng_path, name, dir_arg):

    rc, out, err = module.run_command("%s %s info -g -e %s" % (pkgng_path, dir_arg, name))

    if rc == 0:
        return True

    return False


def query_update(module, pkgng_path, name, dir_arg, old_pkgng, pkgsite):

    # Check to see if a package upgrade is available.
    # rc = 0, no updates available or package not installed
    # rc = 1, updates available
    if old_pkgng:
        rc, out, err = module.run_command("%s %s upgrade -g -n %s" % (pkgsite, pkgng_path, name))
    else:
        rc, out, err = module.run_command("%s %s upgrade %s -g -n %s" % (pkgng_path, dir_arg, pkgsite, name))

    if rc == 1:
        return True

    return False


def pkgng_older_than(module, pkgng_path, compare_version):

    rc, out, err = module.run_command("%s -v" % pkgng_path)
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


def upgrade_packages(module, pkgng_path, dir_arg):
    # Run a 'pkg upgrade', updating all packages.
    upgraded_c = 0

    cmd = "%s %s upgrade -y" % (pkgng_path, dir_arg)
    if module.check_mode:
        cmd += " -n"
    rc, out, err = module.run_command(cmd)

    match = re.search('^Number of packages to be upgraded: ([0-9]+)', out, re.MULTILINE)
    if match:
        upgraded_c = int(match.group(1))

    if upgraded_c > 0:
        return (True, "updated %s package(s)" % upgraded_c, out, err)
    return (False, "no packages need upgrades", out, err)


def remove_packages(module, pkgng_path, packages, dir_arg):
    remove_c = 0
    stdout = ""
    stderr = ""
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, pkgng_path, package, dir_arg):
            continue

        if not module.check_mode:
            rc, out, err = module.run_command("%s %s delete -y %s" % (pkgng_path, dir_arg, package))
            stdout += out
            stderr += err

        if not module.check_mode and query_package(module, pkgng_path, package, dir_arg):
            module.fail_json(msg="failed to remove %s: %s" % (package, out), stdout=stdout, stderr=stderr)

        remove_c += 1

    if remove_c > 0:
        return (True, "removed %s package(s)" % remove_c, stdout, stderr)

    return (False, "package(s) already absent", stdout, stderr)


def install_packages(module, pkgng_path, packages, cached, pkgsite, dir_arg, state, ignoreosver):
    action_queue = defaultdict(list)
    action_count = defaultdict(int)
    stdout = ""
    stderr = ""

    # as of pkg-1.1.4, PACKAGESITE is deprecated in favor of repository definitions
    # in /usr/local/etc/pkg/repos
    old_pkgng = pkgng_older_than(module, pkgng_path, [1, 1, 4])
    if pkgsite != "":
        if old_pkgng:
            pkgsite = "PACKAGESITE=%s" % (pkgsite)
        else:
            pkgsite = "-r %s" % (pkgsite)

    # This environment variable skips mid-install prompts,
    # setting them to their default values.
    batch_var = 'env BATCH=yes'

    if ignoreosver:
        # Ignore FreeBSD OS version check,
        #   useful on -STABLE and -CURRENT branches.
        batch_var = batch_var + ' IGNORE_OSVERSION=yes'

    if not module.check_mode and not cached:
        if old_pkgng:
            rc, out, err = module.run_command("%s %s update" % (pkgsite, pkgng_path))
        else:
            rc, out, err = module.run_command("%s %s %s update" % (batch_var, pkgng_path, dir_arg))
        stdout += out
        stderr += err
        if rc != 0:
            module.fail_json(msg="Could not update catalogue [%d]: %s %s" % (rc, out, err), stdout=stdout, stderr=stderr)

    for package in packages:
        already_installed = query_package(module, pkgng_path, package, dir_arg)
        if already_installed and state == "present":
            continue

        if (
            already_installed and state == "latest"
            and not query_update(module, pkgng_path, package, dir_arg, old_pkgng, pkgsite)
        ):
            continue

        if already_installed:
            action_queue["upgrade"].append(package)
        else:
            action_queue["install"].append(package)

    if not module.check_mode:
        # install/upgrade all named packages with one pkg command
        for (action, package_list) in action_queue.items():
            packages = ' '.join(package_list)
            if old_pkgng:
                rc, out, err = module.run_command("%s %s %s %s -g -U -y %s" % (batch_var, pkgsite, pkgng_path, action, packages))
            else:
                rc, out, err = module.run_command("%s %s %s %s %s -g -U -y %s" % (batch_var, pkgng_path, dir_arg, action, pkgsite, packages))
            stdout += out
            stderr += err

            # individually verify packages are in requested state
            for package in package_list:
                verified = False
                if action == 'install':
                    verified = query_package(module, pkgng_path, package, dir_arg)
                elif action == 'upgrade':
                    verified = not query_update(module, pkgng_path, package, dir_arg, old_pkgng, pkgsite)

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


def annotation_query(module, pkgng_path, package, tag, dir_arg):
    rc, out, err = module.run_command("%s %s info -g -A %s" % (pkgng_path, dir_arg, package))
    match = re.search(r'^\s*(?P<tag>%s)\s*:\s*(?P<value>\w+)' % tag, out, flags=re.MULTILINE)
    if match:
        return match.group('value')
    return False


def annotation_add(module, pkgng_path, package, tag, value, dir_arg):
    _value = annotation_query(module, pkgng_path, package, tag, dir_arg)
    if not _value:
        # Annotation does not exist, add it.
        rc, out, err = module.run_command('%s %s annotate -y -A %s %s "%s"'
                                          % (pkgng_path, dir_arg, package, tag, value))
        if rc != 0:
            module.fail_json(msg="could not annotate %s: %s"
                             % (package, out), stderr=err)
        return True
    elif _value != value:
        # Annotation exists, but value differs
        module.fail_json(
            mgs="failed to annotate %s, because %s is already set to %s, but should be set to %s"
            % (package, tag, _value, value))
        return False
    else:
        # Annotation exists, nothing to do
        return False


def annotation_delete(module, pkgng_path, package, tag, value, dir_arg):
    _value = annotation_query(module, pkgng_path, package, tag, dir_arg)
    if _value:
        rc, out, err = module.run_command('%s %s annotate -y -D %s %s'
                                          % (pkgng_path, dir_arg, package, tag))
        if rc != 0:
            module.fail_json(msg="could not delete annotation to %s: %s"
                             % (package, out), stderr=err)
        return True
    return False


def annotation_modify(module, pkgng_path, package, tag, value, dir_arg):
    _value = annotation_query(module, pkgng_path, package, tag, dir_arg)
    if not value:
        # No such tag
        module.fail_json(msg="could not change annotation to %s: tag %s does not exist"
                         % (package, tag))
    elif _value == value:
        # No change in value
        return False
    else:
        rc, out, err = module.run_command('%s %s annotate -y -M %s %s "%s"'
                                          % (pkgng_path, dir_arg, package, tag, value))
        if rc != 0:
            module.fail_json(msg="could not change annotation annotation to %s: %s"
                             % (package, out), stderr=err)
        return True


def annotate_packages(module, pkgng_path, packages, annotation, dir_arg):
    annotate_c = 0
    annotations = map(lambda _annotation:
                      re.match(r'(?P<operation>[\+-:])(?P<tag>\w+)(=(?P<value>\w+))?',
                               _annotation).groupdict(),
                      re.split(r',', annotation))

    operation = {
        '+': annotation_add,
        '-': annotation_delete,
        ':': annotation_modify
    }

    for package in packages:
        for _annotation in annotations:
            if operation[_annotation['operation']](module, pkgng_path, package, _annotation['tag'], _annotation['value']):
                annotate_c += 1

    if annotate_c > 0:
        return (True, "added %s annotations." % annotate_c)
    return (False, "changed no annotations")


def autoremove_packages(module, pkgng_path, dir_arg):
    stdout = ""
    stderr = ""
    rc, out, err = module.run_command("%s %s autoremove -n" % (pkgng_path, dir_arg))

    autoremove_c = 0

    match = re.search('^Deinstallation has been requested for the following ([0-9]+) packages', out, re.MULTILINE)
    if match:
        autoremove_c = int(match.group(1))

    if autoremove_c == 0:
        return (False, "no package(s) to autoremove", stdout, stderr)

    if not module.check_mode:
        rc, out, err = module.run_command("%s %s autoremove -y" % (pkgng_path, dir_arg))
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
            annotation=dict(default="", required=False),
            pkgsite=dict(default="", required=False),
            rootdir=dict(default="", required=False, type='path'),
            chroot=dict(default="", required=False, type='path'),
            jail=dict(default="", required=False, type='str'),
            autoremove=dict(default=False, type='bool')),
        supports_check_mode=True,
        mutually_exclusive=[["rootdir", "chroot", "jail"]])

    pkgng_path = module.get_bin_path('pkg', True)

    p = module.params

    pkgs = p["name"]

    changed = False
    msgs = []
    stdout = ""
    stderr = ""
    dir_arg = ""

    if p["rootdir"] != "":
        old_pkgng = pkgng_older_than(module, pkgng_path, [1, 5, 0])
        if old_pkgng:
            module.fail_json(msg="To use option 'rootdir' pkg version must be 1.5 or greater")
        else:
            dir_arg = "--rootdir %s" % (p["rootdir"])

    if p["ignore_osver"]:
        old_pkgng = pkgng_older_than(module, pkgng_path, [1, 11, 0])
        if old_pkgng:
            module.fail_json(msg="To use option 'ignore_osver' pkg version must be 1.11 or greater")

    if p["chroot"] != "":
        dir_arg = '--chroot %s' % (p["chroot"])

    if p["jail"] != "":
        dir_arg = '--jail %s' % (p["jail"])

    if pkgs == ['*'] and p["state"] == 'latest':
        # Operate on all installed packages. Only state: latest makes sense here.
        _changed, _msg, _stdout, _stderr = upgrade_packages(module, pkgng_path, dir_arg)
        changed = changed or _changed
        stdout += _stdout
        stderr += _stderr
        msgs.append(_msg)

    # Operate on named packages
    named_packages = [pkg for pkg in pkgs if pkg != '*']
    if p["state"] in ("present", "latest") and named_packages:
        _changed, _msg, _out, _err = install_packages(module, pkgng_path, named_packages,
                                                      p["cached"], p["pkgsite"], dir_arg,
                                                      p["state"], p["ignore_osver"])
        stdout += _out
        stderr += _err
        changed = changed or _changed
        msgs.append(_msg)

    elif p["state"] == "absent" and named_packages:
        _changed, _msg, _out, _err = remove_packages(module, pkgng_path, named_packages, dir_arg)
        stdout += _out
        stderr += _err
        changed = changed or _changed
        msgs.append(_msg)

    if p["autoremove"]:
        _changed, _msg, _stdout, _stderr = autoremove_packages(module, pkgng_path, dir_arg)
        changed = changed or _changed
        stdout += _stdout
        stderr += _stderr
        msgs.append(_msg)

    if p["annotation"]:
        _changed, _msg = annotate_packages(module, pkgng_path, pkgs, p["annotation"], dir_arg)
        changed = changed or _changed
        msgs.append(_msg)

    module.exit_json(changed=changed, msg=", ".join(msgs), stdout=stdout, stderr=stderr)


if __name__ == '__main__':
    main()
