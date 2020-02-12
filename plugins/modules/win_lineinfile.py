#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_lineinfile
short_description: Ensure a particular line is in a file, or replace an existing line using a back-referenced regular expression
description:
  - This module will search a file for a line, and ensure that it is present or absent.
  - This is primarily useful when you want to change a single line in a file only.
options:
  path:
    description:
      - The path of the file to modify.
      - Note that the Windows path delimiter C(\) must be escaped as C(\\) when the line is double quoted.
      - Before Ansible 2.3 this option was only usable as I(dest), I(destfile) and I(name).
    type: path
    required: yes
    aliases: [ dest, destfile, name ]
  backup:
    description:
      - Determine whether a backup should be created.
      - When set to C(yes), create a backup file including the timestamp information
        so you can get the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: no
  regex:
    description:
      - The regular expression to look for in every line of the file. For C(state=present), the pattern to replace if found; only the last line found
        will be replaced. For C(state=absent), the pattern of the line to remove. Uses .NET compatible regular expressions;
        see U(https://msdn.microsoft.com/en-us/library/hs600312%28v=vs.110%29.aspx).
    aliases: [ "regexp" ]
  state:
    description:
      - Whether the line should be there or not.
    type: str
    choices: [ absent, present ]
    default: present
  line:
    description:
      - Required for C(state=present). The line to insert/replace into the file. If C(backrefs) is set, may contain backreferences that will get
        expanded with the C(regexp) capture groups if the regexp matches.
      - Be aware that the line is processed first on the controller and thus is dependent on yaml quoting rules. Any double quoted line
        will have control characters, such as '\r\n', expanded. To print such characters literally, use single or no quotes.
    type: str
  backrefs:
    description:
      - Used with C(state=present). If set, line can contain backreferences (both positional and named) that will get populated if the C(regexp)
        matches. This flag changes the operation of the module slightly; C(insertbefore) and C(insertafter) will be ignored, and if the C(regexp)
        doesn't match anywhere in the file, the file will be left unchanged.
      - If the C(regexp) does match, the last matching line will be replaced by the expanded line parameter.
    type: bool
    default: no
  insertafter:
    description:
      - Used with C(state=present). If specified, the line will be inserted after the last match of specified regular expression. A special value is
        available; C(EOF) for inserting the line at the end of the file.
      - If specified regular expression has no matches, EOF will be used instead. May not be used with C(backrefs).
    type: str
    choices: [ EOF, '*regex*' ]
    default: EOF
  insertbefore:
    description:
      - Used with C(state=present). If specified, the line will be inserted before the last match of specified regular expression. A value is available;
        C(BOF) for inserting the line at the beginning of the file.
      - If specified regular expression has no matches, the line will be inserted at the end of the file. May not be used with C(backrefs).
    type: str
    choices: [ BOF, '*regex*' ]
  create:
    description:
      - Used with C(state=present). If specified, the file will be created if it does not already exist. By default it will fail if the file is missing.
    type: bool
    default: no
  validate:
    description:
      - Validation to run before copying into place. Use %s in the command to indicate the current file to validate.
      - The command is passed securely so shell features like expansion and pipes won't work.
    type: str
  encoding:
    description:
      - Specifies the encoding of the source text file to operate on (and thus what the output encoding will be). The default of C(auto) will cause
        the module to auto-detect the encoding of the source file and ensure that the modified file is written with the same encoding.
      - An explicit encoding can be passed as a string that is a valid value to pass to the .NET framework System.Text.Encoding.GetEncoding() method -
        see U(https://msdn.microsoft.com/en-us/library/system.text.encoding%28v=vs.110%29.aspx).
      - This is mostly useful with C(create=yes) if you want to create a new file with a specific encoding. If C(create=yes) is specified without a
        specific encoding, the default encoding (UTF-8, no BOM) will be used.
    type: str
    default: auto
  newline:
    description:
      - Specifies the line separator style to use for the modified file. This defaults to the windows line separator (C(\r\n)). Note that the indicated
        line separator will be used for file output regardless of the original line separator that appears in the input file.
    type: str
    choices: [ unix, windows ]
    default: windows
notes:
  - As of Ansible 2.3, the I(dest) option has been changed to I(path) as default, but I(dest) still works as well.
seealso:
- module: assemble
- module: lineinfile
author:
- Brian Lloyd (@brianlloyd)
'''

EXAMPLES = r'''
# Before Ansible 2.3, option 'dest', 'destfile' or 'name' was used instead of 'path'
- name: Insert path without converting \r\n
  win_lineinfile:
    path: c:\file.txt
    line: c:\return\new

- win_lineinfile:
    path: C:\Temp\example.conf
    regex: '^name='
    line: 'name=JohnDoe'

- win_lineinfile:
    path: C:\Temp\example.conf
    regex: '^name='
    state: absent

- win_lineinfile:
    path: C:\Temp\example.conf
    regex: '^127\.0\.0\.1'
    line: '127.0.0.1 localhost'

- win_lineinfile:
    path: C:\Temp\httpd.conf
    regex: '^Listen '
    insertafter: '^#Listen '
    line: Listen 8080

- win_lineinfile:
    path: C:\Temp\services
    regex: '^# port for http'
    insertbefore: '^www.*80/tcp'
    line: '# port for http by default'

- name: Create file if it doesn't exist with a specific encoding
  win_lineinfile:
    path: C:\Temp\utf16.txt
    create: yes
    encoding: utf-16
    line: This is a utf-16 encoded file

- name: Add a line to a file and ensure the resulting file uses unix line separators
  win_lineinfile:
    path: C:\Temp\testfile.txt
    line: Line added to file
    newline: unix

- name: Update a line using backrefs
  win_lineinfile:
    path: C:\Temp\example.conf
    backrefs: yes
    regex: '(^name=)'
    line: '$1JohnDoe'
'''

RETURN = r'''
backup:
  description:
  - Name of the backup file that was created.
  - This is now deprecated, use C(backup_file) instead.
  returned: if backup=yes
  type: str
  sample: C:\Path\To\File.txt.11540.20150212-220915.bak
backup_file:
  description: Name of the backup file that was created.
  returned: if backup=yes
  type: str
  sample: C:\Path\To\File.txt.11540.20150212-220915.bak
'''
