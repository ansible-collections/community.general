#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Check BOTMETA file."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ast
import os
import re
import sys

import yaml

from voluptuous import All, Any, MultipleInvalid, PREVENT_EXTRA
from voluptuous import Required, Schema, Invalid
from voluptuous.humanize import humanize_error


REPORT_MISSING_MAINTAINERS = False

FILENAME = '.github/BOTMETA.yml'

LIST_ENTRIES = frozenset(('supershipit', 'maintainers', 'labels', 'keywords', 'notify', 'ignore'))

AUTHOR_REGEX = re.compile(r'^\w.*\(@([\w-]+)\)(?![\w.])$')


def read_authors(filename):
    data = {}
    try:
        with open(filename, 'rb') as b_module_data:
            M = ast.parse(b_module_data.read())

        for child in M.body:
            if isinstance(child, ast.Assign):
                for t in child.targets:
                    try:
                        theid = t.id
                    except AttributeError:
                        # skip errors can happen when trying to use the normal code
                        continue

                    if theid == 'DOCUMENTATION':
                        if isinstance(child.value, ast.Dict):
                            data = ast.literal_eval(child.value)
                        else:
                            data = yaml.safe_load(child.value.s)

    except Exception as e:
        print('%s:%d:%d: Cannot load DOCUMENTATION: %s' % (filename, 0, 0, e))
        return []

    author = data.get('author') or []
    if isinstance(author, str):
        author = [author]
    return author


def validate(filename, filedata):
    if filename.startswith('plugins/doc_fragments/'):
        return
    # Compile lis tof all active and inactive maintainers
    all_maintainers = filedata['maintainers'] + filedata['ignore']
    if not all_maintainers:
        if REPORT_MISSING_MAINTAINERS:
            print('%s:%d:%d: %s' % (FILENAME, 0, 0, 'No (active or inactive) maintainer mentioned for %s' % filename))
        return
    if filename.startswith('plugins/filter/'):
        return
    maintainers = read_authors(filename)
    for maintainer in maintainers:
        m = AUTHOR_REGEX.match(maintainer)
        if m:
            maintainer = m.group(1)
            if maintainer not in all_maintainers:
                msg = 'Author %s not mentioned as active or inactive maintainer for %s (mentioned are: %s)' % (
                    maintainer, filename, ', '.join(all_maintainers))
                if REPORT_MISSING_MAINTAINERS:
                    print('%s:%d:%d: %s' % (FILENAME, 0, 0, msg))


def main():
    """Main entry point."""
    paths = sys.argv[1:] or sys.stdin.read().splitlines()
    paths = [path for path in paths if path.endswith('/aliases')]

    try:
        with open(FILENAME, 'rb') as f:
            botmeta = yaml.safe_load(f)
    except yaml.error.MarkedYAMLError as ex:
        print('%s:%d:%d: YAML load failed: %s' % (FILENAME, ex.context_mark.line +
                                                  1, ex.context_mark.column + 1, re.sub(r'\s+', ' ', str(ex))))
        return
    except Exception as ex:  # pylint: disable=broad-except
        print('%s:%d:%d: YAML load failed: %s' %
              (FILENAME, 0, 0, re.sub(r'\s+', ' ', str(ex))))
        return

    # Validate schema

    MacroSchema = Schema({
        (str): str,
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
        ('automerge'): bool,
        ('macros'): MacroSchema,
        ('files'): FilesSchema,
    }, extra=PREVENT_EXTRA)

    try:
        schema(botmeta)
    except MultipleInvalid as ex:
        for error in ex.errors:
            # No way to get line/column numbers
            print('%s:%d:%d: %s' % (FILENAME, 0, 0, humanize_error(botmeta, error)))
        return

    # Preprocess (substitute macros, convert to lists)
    macros = botmeta.get('macros') or {}
    macro_re = re.compile(r'\$([a-zA-Z_]+)')

    def convert_macros(text, macros):
        def f(m):
            return macros[m.group(1)]

        return macro_re.sub(f, text)

    files = {}
    try:
        for file, filedata in (botmeta.get('files') or {}).items():
            file = convert_macros(file, macros)
            filedata = dict((k, convert_macros(v, macros)) for k, v in filedata.items())
            files[file] = filedata
            for k, v in filedata.items():
                if k in LIST_ENTRIES:
                    filedata[k] = v.split()
    except KeyError as e:
        print('%s:%d:%d: %s' % (FILENAME, 0, 0, 'Found unknown macro %s' % e))
        return

    # Scan all files
    for dirpath, dirnames, filenames in os.walk('plugins/'):
        for file in filenames:
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
                if not matching_files:
                    print('%s:%d:%d: %s' % (FILENAME, 0, 0, 'Did not find any entry for %s' % filename))

                matching_files.sort(key=lambda kv: kv[0])
                filedata = dict()
                for k in LIST_ENTRIES:
                    filedata[k] = []
                for dummy, data in matching_files:
                    for k, v in data.items():
                        if k in LIST_ENTRIES:
                            v = filedata[k] + v
                        filedata[k] = v
                validate(filename, filedata)


if __name__ == '__main__':
    main()
