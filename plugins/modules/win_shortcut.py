#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_shortcut
short_description: Manage shortcuts on Windows
description:
- Create, manage and delete Windows shortcuts
options:
  src:
    description:
    - Executable or URL the shortcut points to.
    - The executable needs to be in your PATH, or has to be an absolute
      path to the executable.
    type: str
  description:
    description:
    - Description for the shortcut.
    - This is usually shown when hoovering the icon.
    type: str
  dest:
    description:
    - Destination file for the shortcuting file.
    - File name should have a C(.lnk) or C(.url) extension.
    type: path
    required: yes
  arguments:
    description:
    - Additional arguments for the executable defined in C(src).
    - Was originally just C(args) but renamed in Ansible 2.8.
    type: str
    aliases: [ args ]
  directory:
    description:
    - Working directory for executable defined in C(src).
    type: path
  icon:
    description:
    - Icon used for the shortcut.
    - File name should have a C(.ico) extension.
    - The file name is followed by a comma and the number in the library file (.dll) or use 0 for an image file.
    type: path
  hotkey:
    description:
    - Key combination for the shortcut.
    - This is a combination of one or more modifiers and a key.
    - Possible modifiers are Alt, Ctrl, Shift, Ext.
    - Possible keys are [A-Z] and [0-9].
    type: str
  windowstyle:
    description:
    - Influences how the application is displayed when it is launched.
    type: str
    choices: [ maximized, minimized, normal ]
  state:
    description:
    - When C(absent), removes the shortcut if it exists.
    - When C(present), creates or updates the shortcut.
    type: str
    choices: [ absent, present ]
    default: present
  run_as_admin:
    description:
    - When C(src) is an executable, this can control whether the shortcut will be opened as an administrator or not.
    type: bool
    default: no
notes:
- 'The following options can include Windows environment variables: C(dest), C(args), C(description), C(dest), C(directory), C(icon) C(src)'
- 'Windows has two types of shortcuts: Application and URL shortcuts. URL shortcuts only consists of C(dest) and C(src)'
seealso:
- module: win_file
author:
- Dag Wieers (@dagwieers)
'''

EXAMPLES = r'''
- name: Create an application shortcut on the desktop
  win_shortcut:
    src: C:\Program Files\Mozilla Firefox\Firefox.exe
    dest: C:\Users\Public\Desktop\Mozilla Firefox.lnk
    icon: C:\Program Files\Mozilla Firefox\Firefox.exe,0

- name: Create the same shortcut using environment variables
  win_shortcut:
    description: The Mozilla Firefox web browser
    src: '%ProgramFiles%\Mozilla Firefox\Firefox.exe'
    dest: '%Public%\Desktop\Mozilla Firefox.lnk'
    icon: '%ProgramFiles\Mozilla Firefox\Firefox.exe,0'
    directory: '%ProgramFiles%\Mozilla Firefox'
    hotkey: Ctrl+Alt+F

- name: Create an application shortcut for an executable in PATH to your desktop
  win_shortcut:
    src: cmd.exe
    dest: Desktop\Command prompt.lnk

- name: Create an application shortcut for the Ansible website
  win_shortcut:
    src: '%ProgramFiles%\Google\Chrome\Application\chrome.exe'
    dest: '%UserProfile%\Desktop\Ansible website.lnk'
    arguments: --new-window https://ansible.com/
    directory: '%ProgramFiles%\Google\Chrome\Application'
    icon: '%ProgramFiles%\Google\Chrome\Application\chrome.exe,0'
    hotkey: Ctrl+Alt+A

- name: Create a URL shortcut for the Ansible website
  win_shortcut:
    src: https://ansible.com/
    dest: '%Public%\Desktop\Ansible website.url'
'''

RETURN = r'''
'''
