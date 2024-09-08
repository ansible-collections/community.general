#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2023, Vlad Glagolev <scm@vaygr.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: sorcery
short_description: Package manager for Source Mage GNU/Linux
description:
    - Manages "spells" on Source Mage GNU/Linux using I(sorcery) toolchain
author: "Vlad Glagolev (@vaygr)"
notes:
    - When all three components are selected, the update goes by the sequence --
      Sorcery -> Grimoire(s) -> Spell(s); you cannot override it.
    - Grimoire handling is supported since community.general 7.3.0.
requirements:
    - bash
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
            - Name of the spell or grimoire.
            - Multiple names can be given, separated by commas.
            - Special value V(*) in conjunction with states V(latest) or
              V(rebuild) will update or rebuild the whole system respectively
            - The alias O(grimoire) was added in community.general 7.3.0.
        aliases: ["spell", "grimoire"]
        type: list
        elements: str

    repository:
        description:
            - Repository location.
            - If specified, O(name) represents grimoire(s) instead of spell(s).
            - Special value V(*) will pull grimoire from the official location.
            - Only single item in O(name) in conjunction with V(*) can be used.
            - O(state=absent) must be used with a special value V(*).
        type: str
        version_added: 7.3.0

    state:
        description:
            - Whether to cast, dispel or rebuild a package.
            - State V(cast) is an equivalent of V(present), not V(latest).
            - State V(rebuild) implies cast of all specified spells, not only
              those existed before.
        choices: ["present", "latest", "absent", "cast", "dispelled", "rebuild"]
        default: "present"
        type: str

    depends:
        description:
            - Comma-separated list of _optional_ dependencies to build a spell
              (or make sure it is built) with; use V(+)/V(-) in front of dependency
              to turn it on/off (V(+) is optional though).
            - This option is ignored if O(name) parameter is equal to V(*) or
              contains more than one spell.
            - Providers must be supplied in the form recognized by Sorcery,
              for example 'V(openssl(SSL\))'.
        type: str

    update:
        description:
            - Whether or not to update sorcery scripts at the very first stage.
        type: bool
        default: false

    update_cache:
        description:
            - Whether or not to update grimoire collection before casting spells.
        type: bool
        default: false
        aliases: ["update_codex"]

    cache_valid_time:
        description:
            - Time in seconds to invalidate grimoire collection on update.
            - Especially useful for SCM and rsync grimoires.
            - Makes sense only in pair with O(update_cache).
        type: int
        default: 0
'''


EXAMPLES = '''
- name: Make sure spell foo is installed
  community.general.sorcery:
    spell: foo
    state: present

- name: Make sure spells foo, bar and baz are removed
  community.general.sorcery:
    spell: foo,bar,baz
    state: absent

- name: Make sure spell foo with dependencies bar and baz is installed
  community.general.sorcery:
    spell: foo
    depends: bar,baz
    state: present

- name: Make sure spell foo with bar and without baz dependencies is installed
  community.general.sorcery:
    spell: foo
    depends: +bar,-baz
    state: present

- name: Make sure spell foo with libressl (providing SSL) dependency is installed
  community.general.sorcery:
    spell: foo
    depends: libressl(SSL)
    state: present

- name: Make sure spells with/without required dependencies (if any) are installed
  community.general.sorcery:
    name: "{{ item.spell }}"
    depends: "{{ item.depends | default(None) }}"
    state: present
  loop:
    - { spell: 'vifm', depends: '+file,-gtk+2' }
    - { spell: 'fwknop', depends: 'gpgme' }
    - { spell: 'pv,tnftp,tor' }

- name: Install the latest version of spell foo using regular glossary
  community.general.sorcery:
    name: foo
    state: latest

- name: Rebuild spell foo
  community.general.sorcery:
    spell: foo
    state: rebuild

- name: Rebuild the whole system, but update Sorcery and Codex first
  community.general.sorcery:
    spell: '*'
    state: rebuild
    update: true
    update_cache: true

- name: Refresh the grimoire collection if it is 1 day old using native sorcerous alias
  community.general.sorcery:
    update_codex: true
    cache_valid_time: 86400

- name: Make sure stable grimoire is present
  community.general.sorcery:
    name: stable
    repository: '*'
    state: present

- name: Make sure binary and stable-rc grimoires are removed
  community.general.sorcery:
    grimoire: binary,stable-rc
    repository: '*'
    state: absent

- name: Make sure games grimoire is pulled from rsync
  community.general.sorcery:
    grimoire: games
    repository: "rsync://download.sourcemage.org::codex/games"
    state: present

- name: Make sure a specific branch of stable grimoire is pulled from git
  community.general.sorcery:
    grimoire: stable.git
    repository: "git://download.sourcemage.org/smgl/grimoire.git:stable.git:stable-0.62"
    state: present

- name: Update only Sorcery itself
  community.general.sorcery:
    update: true
'''


RETURN = '''
'''


import datetime
import fileinput
import os
import re
import shutil
import sys

from ansible.module_utils.basic import AnsibleModule


# auto-filled at module init
SORCERY = {
    'sorcery': None,
    'scribe': None,
    'cast': None,
    'dispel': None,
    'gaze': None
}

SORCERY_LOG_DIR = "/var/log/sorcery"
SORCERY_STATE_DIR = "/var/state/sorcery"

NA = "N/A"


def get_sorcery_ver(module):
    """ Get Sorcery version. """

    cmd_sorcery = "%s --version" % SORCERY['sorcery']

    rc, stdout, stderr = module.run_command(cmd_sorcery)

    if rc != 0 or not stdout:
        module.fail_json(msg="unable to get Sorcery version")

    return stdout.strip()


def codex_fresh(codex, module):
    """ Check if grimoire collection is fresh enough. """

    if not module.params['cache_valid_time']:
        return False

    timedelta = datetime.timedelta(seconds=module.params['cache_valid_time'])

    for grimoire in codex:
        lastupdate_path = os.path.join(SORCERY_STATE_DIR,
                                       grimoire + ".lastupdate")

        try:
            mtime = os.stat(lastupdate_path).st_mtime
        except Exception:
            return False

        lastupdate_ts = datetime.datetime.fromtimestamp(mtime)

        # if any grimoire is not fresh, we invalidate the Codex
        if lastupdate_ts + timedelta < datetime.datetime.now():
            return False

    return True


def codex_list(module, skip_new=False):
    """ List valid grimoire collection. """

    params = module.params

    codex = {}

    cmd_scribe = "%s index" % SORCERY['scribe']

    rc, stdout, stderr = module.run_command(cmd_scribe)

    if rc != 0:
        module.fail_json(msg="unable to list grimoire collection, fix your Codex")

    rex = re.compile(r"^\s*\[\d+\] : (?P<grim>[\w\-+.]+) : [\w\-+./]+(?: : (?P<ver>[\w\-+.]+))?\s*$")

    # drop 4-line header and empty trailing line
    for line in stdout.splitlines()[4:-1]:
        match = rex.match(line)

        if match:
            codex[match.group('grim')] = match.group('ver')

    # return only specified grimoires unless requested to skip new
    if params['repository'] and not skip_new:
        codex = {x: codex.get(x, NA) for x in params['name']}

    if not codex:
        module.fail_json(msg="no grimoires to operate on; add at least one")

    return codex


def update_sorcery(module):
    """ Update sorcery scripts.

    This runs 'sorcery update' ('sorcery -u'). Check mode always returns a
    positive change value.

    """

    changed = False

    if module.check_mode:
        return (True, "would have updated Sorcery")
    else:
        sorcery_ver = get_sorcery_ver(module)

        cmd_sorcery = "%s update" % SORCERY['sorcery']

        rc, stdout, stderr = module.run_command(cmd_sorcery)

        if rc != 0:
            module.fail_json(msg="unable to update Sorcery: " + stdout)

        if sorcery_ver != get_sorcery_ver(module):
            changed = True

        return (changed, "successfully updated Sorcery")


def update_codex(module):
    """ Update grimoire collections.

    This runs 'scribe update'. Check mode always returns a positive change
    value when 'cache_valid_time' is used.

    """

    params = module.params

    changed = False

    codex = codex_list(module)
    fresh = codex_fresh(codex, module)

    if module.check_mode:
        if not fresh:
            changed = True

        return (changed, "would have updated Codex")
    else:
        if not fresh:
            # SILENT is required as a workaround for query() in libgpg
            module.run_command_environ_update.update(dict(SILENT='1'))

            cmd_scribe = "%s update" % SORCERY['scribe']

            if params['repository']:
                cmd_scribe += ' %s' % ' '.join(codex.keys())

            rc, stdout, stderr = module.run_command(cmd_scribe)

            if rc != 0:
                module.fail_json(msg="unable to update Codex: " + stdout)

            if codex != codex_list(module):
                changed = True

        return (changed, "successfully updated Codex")


def match_depends(module):
    """ Check for matching dependencies.

    This inspects spell's dependencies with the desired states and returns
    'False' if a recast is needed to match them. It also adds required lines
    to the system-wide depends file for proper recast procedure.

    """

    params = module.params
    spells = params['name']

    depends = {}

    depends_ok = True

    if len(spells) > 1 or not params['depends']:
        return depends_ok

    spell = spells[0]

    if module.check_mode:
        sorcery_depends_orig = os.path.join(SORCERY_STATE_DIR, "depends")
        sorcery_depends = os.path.join(SORCERY_STATE_DIR, "depends.check")

        try:
            shutil.copy2(sorcery_depends_orig, sorcery_depends)
        except IOError:
            module.fail_json(msg="failed to copy depends.check file")
    else:
        sorcery_depends = os.path.join(SORCERY_STATE_DIR, "depends")

    rex = re.compile(r"^(?P<status>\+?|\-){1}(?P<depend>[a-z0-9]+[a-z0-9_\-\+\.]*(\([A-Z0-9_\-\+\.]+\))*)$")

    for d in params['depends'].split(','):
        match = rex.match(d)

        if not match:
            module.fail_json(msg="wrong depends line for spell '%s'" % spell)

        # normalize status
        if not match.group('status') or match.group('status') == '+':
            status = 'on'
        else:
            status = 'off'

        depends[match.group('depend')] = status

    # drop providers spec
    depends_list = [s.split('(')[0] for s in depends]

    cmd_gaze = "%s -q version %s" % (SORCERY['gaze'], ' '.join(depends_list))

    rc, stdout, stderr = module.run_command(cmd_gaze)

    if rc != 0:
        module.fail_json(msg="wrong dependencies for spell '%s'" % spell)

    fi = fileinput.input(sorcery_depends, inplace=True)

    try:
        try:
            for line in fi:
                if line.startswith(spell + ':'):
                    match = None

                    for d in depends:
                        # when local status is 'off' and dependency is provider,
                        # use only provider value
                        d_offset = d.find('(')

                        if d_offset == -1:
                            d_p = ''
                        else:
                            d_p = re.escape(d[d_offset:])

                        # .escape() is needed mostly for the spells like 'libsigc++'
                        rex = re.compile("%s:(?:%s|%s):(?P<lstatus>on|off):optional:" %
                                         (re.escape(spell), re.escape(d), d_p))

                        match = rex.match(line)

                        # we matched the line "spell:dependency:on|off:optional:"
                        if match:
                            # if we also matched the local status, mark dependency
                            # as empty and put it back into depends file
                            if match.group('lstatus') == depends[d]:
                                depends[d] = None

                                sys.stdout.write(line)

                            # status is not that we need, so keep this dependency
                            # in the list for further reverse switching;
                            # stop and process the next line in both cases
                            break

                    if not match:
                        sys.stdout.write(line)
                else:
                    sys.stdout.write(line)
        except IOError:
            module.fail_json(msg="I/O error on the depends file")
    finally:
        fi.close()

    depends_new = [v for v in depends if depends[v]]

    if depends_new:
        try:
            try:
                fl = open(sorcery_depends, 'a')

                for k in depends_new:
                    fl.write("%s:%s:%s:optional::\n" % (spell, k, depends[k]))
            except IOError:
                module.fail_json(msg="I/O error on the depends file")
        finally:
            fl.close()

        depends_ok = False

    if module.check_mode:
        try:
            os.remove(sorcery_depends)
        except IOError:
            module.fail_json(msg="failed to clean up depends.backup file")

    return depends_ok


def manage_grimoires(module):
    """ Add or remove grimoires. """

    params = module.params
    grimoires = params['name']
    url = params['repository']

    codex = codex_list(module, True)

    if url == '*':
        if params['state'] in ('present', 'latest', 'absent'):
            if params['state'] == 'absent':
                action = "remove"
                todo = set(grimoires) & set(codex)
            else:
                action = "add"
                todo = set(grimoires) - set(codex)

            if not todo:
                return (False, "all grimoire(s) are already %sed" % action[:5])

            if module.check_mode:
                return (True, "would have %sed grimoire(s)" % action[:5])

            cmd_scribe = "%s %s %s" % (SORCERY['scribe'], action, ' '.join(todo))

            rc, stdout, stderr = module.run_command(cmd_scribe)

            if rc != 0:
                module.fail_json(msg="failed to %s one or more grimoire(s): %s" % (action, stdout))

            return (True, "successfully %sed one or more grimoire(s)" % action[:5])
        else:
            module.fail_json(msg="unsupported operation on '*' repository value")
    else:
        if params['state'] in ('present', 'latest'):
            if len(grimoires) > 1:
                module.fail_json(msg="using multiple items with repository is invalid")

            grimoire = grimoires[0]

            if grimoire in codex:
                return (False, "grimoire %s already exists" % grimoire)

            if module.check_mode:
                return (True, "would have added grimoire %s from %s" % (grimoire, url))

            cmd_scribe = "%s add %s from %s" % (SORCERY['scribe'], grimoire, url)

            rc, stdout, stderr = module.run_command(cmd_scribe)

            if rc != 0:
                module.fail_json(msg="failed to add grimoire %s from %s: %s" % (grimoire, url, stdout))

            return (True, "successfully added grimoire %s from %s" % (grimoire, url))
        else:
            module.fail_json(msg="unsupported operation on repository value")


def manage_spells(module):
    """ Cast or dispel spells.

    This manages the whole system ('*'), list or a single spell. Command 'cast'
    is used to install or rebuild spells, while 'dispel' takes care of theirs
    removal from the system.

    """

    params = module.params
    spells = params['name']

    sorcery_queue = os.path.join(SORCERY_LOG_DIR, "queue/install")

    if spells == '*':
        if params['state'] == 'latest':
            # back up original queue
            try:
                os.rename(sorcery_queue, sorcery_queue + ".backup")
            except IOError:
                module.fail_json(msg="failed to backup the update queue")

            # see update_codex()
            module.run_command_environ_update.update(dict(SILENT='1'))

            cmd_sorcery = "%s queue" % SORCERY['sorcery']

            rc, stdout, stderr = module.run_command(cmd_sorcery)

            if rc != 0:
                module.fail_json(msg="failed to generate the update queue")

            try:
                queue_size = os.stat(sorcery_queue).st_size
            except Exception:
                module.fail_json(msg="failed to read the update queue")

            if queue_size != 0:
                if module.check_mode:
                    try:
                        os.rename(sorcery_queue + ".backup", sorcery_queue)
                    except IOError:
                        module.fail_json(msg="failed to restore the update queue")

                    return (True, "would have updated the system")

                cmd_cast = "%s --queue" % SORCERY['cast']

                rc, stdout, stderr = module.run_command(cmd_cast)

                if rc != 0:
                    module.fail_json(msg="failed to update the system")

                return (True, "successfully updated the system")
            else:
                return (False, "the system is already up to date")
        elif params['state'] == 'rebuild':
            if module.check_mode:
                return (True, "would have rebuilt the system")

            cmd_sorcery = "%s rebuild" % SORCERY['sorcery']

            rc, stdout, stderr = module.run_command(cmd_sorcery)

            if rc != 0:
                module.fail_json(msg="failed to rebuild the system: " + stdout)

            return (True, "successfully rebuilt the system")
        else:
            module.fail_json(msg="unsupported operation on '*' name value")
    else:
        if params['state'] in ('present', 'latest', 'rebuild', 'absent'):
            # extract versions from the 'gaze' command
            cmd_gaze = "%s -q version %s" % (SORCERY['gaze'], ' '.join(spells))

            rc, stdout, stderr = module.run_command(cmd_gaze)

            # fail if any of spells cannot be found
            if rc != 0:
                module.fail_json(msg="failed to locate spell(s) in the list (%s)" %
                                 ', '.join(spells))

            cast_queue = []
            dispel_queue = []

            rex = re.compile(r"[^|]+\|[^|]+\|(?P<spell>[^|]+)\|(?P<grim_ver>[^|]+)\|(?P<inst_ver>[^$]+)")

            # drop 2-line header and empty trailing line
            for line in stdout.splitlines()[2:-1]:
                match = rex.match(line)

                cast = False

                if params['state'] == 'present':
                    # spell is not installed..
                    if match.group('inst_ver') == '-':
                        # ..so set up depends reqs for it
                        match_depends(module)

                        cast = True
                    # spell is installed..
                    else:
                        # ..but does not conform depends reqs
                        if not match_depends(module):
                            cast = True
                elif params['state'] == 'latest':
                    # grimoire and installed versions do not match..
                    if match.group('grim_ver') != match.group('inst_ver'):
                        # ..so check for depends reqs first and set them up
                        match_depends(module)

                        cast = True
                    # grimoire and installed versions match..
                    else:
                        # ..but the spell does not conform depends reqs
                        if not match_depends(module):
                            cast = True
                elif params['state'] == 'rebuild':
                    cast = True
                # 'absent'
                else:
                    if match.group('inst_ver') != '-':
                        dispel_queue.append(match.group('spell'))

                if cast:
                    cast_queue.append(match.group('spell'))

            if cast_queue:
                if module.check_mode:
                    return (True, "would have cast spell(s)")

                cmd_cast = "%s -c %s" % (SORCERY['cast'], ' '.join(cast_queue))

                rc, stdout, stderr = module.run_command(cmd_cast)

                if rc != 0:
                    module.fail_json(msg="failed to cast spell(s): " + stdout)

                return (True, "successfully cast spell(s)")
            elif params['state'] != 'absent':
                return (False, "spell(s) are already cast")

            if dispel_queue:
                if module.check_mode:
                    return (True, "would have dispelled spell(s)")

                cmd_dispel = "%s %s" % (SORCERY['dispel'], ' '.join(dispel_queue))

                rc, stdout, stderr = module.run_command(cmd_dispel)

                if rc != 0:
                    module.fail_json(msg="failed to dispel spell(s): " + stdout)

                return (True, "successfully dispelled spell(s)")
            else:
                return (False, "spell(s) are already dispelled")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(default=None, aliases=['spell', 'grimoire'], type='list', elements='str'),
            repository=dict(default=None, type='str'),
            state=dict(default='present', choices=['present', 'latest',
                                                   'absent', 'cast', 'dispelled', 'rebuild']),
            depends=dict(default=None),
            update=dict(default=False, type='bool'),
            update_cache=dict(default=False, aliases=['update_codex'], type='bool'),
            cache_valid_time=dict(default=0, type='int')
        ),
        required_one_of=[['name', 'update', 'update_cache']],
        supports_check_mode=True
    )

    if os.geteuid() != 0:
        module.fail_json(msg="root privileges are required for this operation")

    for c in SORCERY:
        SORCERY[c] = module.get_bin_path(c, True)

    # prepare environment: run sorcery commands without asking questions
    module.run_command_environ_update = dict(PROMPT_DELAY='0', VOYEUR='0')

    params = module.params

    # normalize 'state' parameter
    if params['state'] in ('present', 'cast'):
        params['state'] = 'present'
    elif params['state'] in ('absent', 'dispelled'):
        params['state'] = 'absent'

    changed = {
        'sorcery': (False, NA),
        'grimoires': (False, NA),
        'codex': (False, NA),
        'spells': (False, NA)
    }

    if params['update']:
        changed['sorcery'] = update_sorcery(module)

    if params['name'] and params['repository']:
        changed['grimoires'] = manage_grimoires(module)

    if params['update_cache']:
        changed['codex'] = update_codex(module)

    if params['name'] and not params['repository']:
        changed['spells'] = manage_spells(module)

    if any(x[0] for x in changed.values()):
        state_msg = "state changed"
        state_changed = True
    else:
        state_msg = "no change in state"
        state_changed = False

    module.exit_json(changed=state_changed, msg=state_msg + ": " + '; '.join(x[1] for x in changed.values()))


if __name__ == '__main__':
    main()
