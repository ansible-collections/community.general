#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check BOTMETA file."""

from __future__ import annotations

import os
import re
import sys

import yaml

from voluptuous import Any, MultipleInvalid, PREVENT_EXTRA, Schema
from voluptuous.humanize import humanize_error


IGNORE_NO_MAINTAINERS = [
    'docs/docsite/rst/filter_guide.rst',
    'docs/docsite/rst/filter_guide_abstract_informations.rst',
    'docs/docsite/rst/filter_guide_paths.rst',
    'docs/docsite/rst/filter_guide_selecting_json_data.rst',
    'plugins/cache/memcached.py',
    'plugins/cache/redis.py',
    'plugins/callback/cgroup_memory_recap.py',
    'plugins/callback/context_demo.py',
    'plugins/callback/counter_enabled.py',
    'plugins/callback/jabber.py',
    'plugins/callback/log_plays.py',
    'plugins/callback/logdna.py',
    'plugins/callback/logentries.py',
    'plugins/callback/null.py',
    'plugins/callback/selective.py',
    'plugins/callback/slack.py',
    'plugins/callback/splunk.py',
    'plugins/callback/yaml.py',
    'plugins/inventory/nmap.py',
    'plugins/inventory/virtualbox.py',
    'plugins/connection/chroot.py',
    'plugins/connection/iocage.py',
    'plugins/connection/lxc.py',
    'plugins/lookup/cartesian.py',
    'plugins/lookup/chef_databag.py',
    'plugins/lookup/consul_kv.py',
    'plugins/lookup/credstash.py',
    'plugins/lookup/cyberarkpassword.py',
    'plugins/lookup/flattened.py',
    'plugins/lookup/keyring.py',
    'plugins/lookup/lastpass.py',
    'plugins/lookup/passwordstore.py',
    'plugins/lookup/shelvefile.py',
    'plugins/filter/json_query.py',
    'plugins/filter/random_mac.py',
]

FILENAME = '.github/BOTMETA.yml'

LIST_ENTRIES = frozenset(('supershipit', 'maintainers', 'labels', 'keywords', 'notify', 'ignore'))

AUTHOR_REGEX = re.compile(r'^\w.*\(@([\w-]+)\)(?![\w.])')


def read_authors(filename):
    data = {}
    try:
        documentation = []
        in_docs = False
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('DOCUMENTATION ='):
                    in_docs = True
                elif line.startswith(("'''", '"""')) and in_docs:
                    in_docs = False
                elif in_docs:
                    documentation.append(line)
        if in_docs:
            print(f'{filename}: cannot find DOCUMENTATION end')
            return []
        if not documentation:
            print(f'{filename}: cannot find DOCUMENTATION')
            return []

        data = yaml.safe_load('\n'.join(documentation))

    except Exception as e:
        print(f'{filename}:0:0: Cannot load DOCUMENTATION: {e}')
        return []

    author = data.get('author') or []
    if isinstance(author, str):
        author = [author]
    return author


def extract_author_name(author):
    m = AUTHOR_REGEX.match(author)
    if m:
        return m.group(1)
    if author == 'Ansible Core Team':
        return '$team_ansible_core'
    return None


def validate(filename, filedata):
    if not filename.startswith('plugins/'):
        return
    if filename.startswith(('plugins/doc_fragments/', 'plugins/module_utils/')):
        return
    # Compile list of all active and inactive maintainers
    all_maintainers = filedata['maintainers'] + filedata['ignore']
    if not filename.startswith(('plugins/action/', 'plugins/doc_fragments/', 'plugins/filter/', 'plugins/module_utils/', 'plugins/plugin_utils/')):
        maintainers = read_authors(filename)
        for maintainer in maintainers:
            maintainer = extract_author_name(maintainer)
            if maintainer is not None and maintainer not in all_maintainers:
                others = ', '.join(all_maintainers)
                msg = f'Author {maintainer} not mentioned as active or inactive maintainer for {filename} (mentioned are: {others})'
                print(f'{FILENAME}:0:0: {msg}')
    should_have_no_maintainer = filename in IGNORE_NO_MAINTAINERS
    if not all_maintainers and not should_have_no_maintainer:
        print(f'{FILENAME}:0:0: No (active or inactive) maintainer mentioned for {filename}')
    if all_maintainers and should_have_no_maintainer:
        print(f'{FILENAME}:0:0: Please remove {filename} from the ignore list of {sys.argv[0]}')


def main():
    """Main entry point."""
    try:
        with open(FILENAME, 'rb') as f:
            botmeta = yaml.safe_load(f)
    except yaml.error.MarkedYAMLError as ex:
        msg = re.sub(r'\s+', ' ', str(ex))
        print('f{FILENAME}:{ex.context_mark.line + 1}:{ex.context_mark.column + 1}: YAML load failed: {msg}')
        return
    except Exception as ex:  # pylint: disable=broad-except
        msg = re.sub(r'\s+', ' ', str(ex))
        print(f'{FILENAME}:0:0: YAML load failed: {msg}')
        return

    # Validate schema

    MacroSchema = Schema({
        (str): Any(str, None),
    }, extra=PREVENT_EXTRA)

    FilesSchema = Schema({
        (str): {
            ('supershipit'): str,
            ('support'): Any('community'),
            ('maintainers'): str,
            ('labels'): str,
            ('keywords'): str,
            ('notify'): str,
            ('ignore'): str,
        },
    }, extra=PREVENT_EXTRA)

    schema = Schema({
        ('notifications'): bool,
        ('automerge'): bool,
        ('macros'): MacroSchema,
        ('files'): FilesSchema,
    }, extra=PREVENT_EXTRA)

    try:
        schema(botmeta)
    except MultipleInvalid as ex:
        for error in ex.errors:
            # No way to get line/column numbers
            print(f'{FILENAME}:0:0: {humanize_error(botmeta, error)}')
        return

    # Preprocess (substitute macros, convert to lists)
    macros = botmeta.get('macros') or {}
    macro_re = re.compile(r'\$([a-zA-Z_]+)')

    def convert_macros(text, macros):
        def f(m):
            macro = m.group(1)
            replacement = (macros[macro] or '')
            if macro == 'team_ansible_core':
                return f'$team_ansible_core {replacement}'
            return replacement

        return macro_re.sub(f, text)

    files = {}
    try:
        for file, filedata in (botmeta.get('files') or {}).items():
            file = convert_macros(file, macros)
            filedata = {k: convert_macros(v, macros) for k, v in filedata.items()}
            files[file] = filedata
            for k, v in filedata.items():
                if k in LIST_ENTRIES:
                    filedata[k] = v.split()
    except KeyError as e:
        print(f'{FILENAME}:0:0: Found unknown macro {e}')
        return

    # Scan all files
    unmatched = set(files)
    for dirs in ('docs/docsite/rst', 'plugins', 'tests', 'changelogs'):
        for dirpath, _dirnames, filenames in os.walk(dirs):
            for file in sorted(filenames):
                if file.endswith('.pyc'):
                    continue
                filename = os.path.join(dirpath, file)
                if os.path.islink(filename):
                    continue
                if os.path.isfile(filename):
                    matching_files = []
                    for file, filedata in files.items():
                        if filename.startswith(file):
                            matching_files.append((file, filedata))
                            if file in unmatched:
                                unmatched.remove(file)
                    if not matching_files:
                        print(f'{FILENAME}:0:0: Did not find any entry for {filename}')

                    matching_files.sort(key=lambda kv: kv[0])
                    filedata = {}
                    for k in LIST_ENTRIES:
                        filedata[k] = []
                    for dummy, data in matching_files:
                        for k, v in data.items():
                            if k in LIST_ENTRIES:
                                v = filedata[k] + v
                            filedata[k] = v
                    validate(filename, filedata)

    for file in unmatched:
        print(f'{FILENAME}:0:0: Entry {file} was not used')


if __name__ == '__main__':
    main()
