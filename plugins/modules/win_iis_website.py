#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2015, Henrik Wallström <henrik@wallstroms.nu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_iis_website
short_description: Configures a IIS Web site
description:
     - Creates, Removes and configures a IIS Web site.
options:
  name:
    description:
      - Names of web site.
    type: str
    required: yes
  site_id:
    description:
      - Explicitly set the IIS numeric ID for a site.
      - Note that this value cannot be changed after the website has been created.
    type: str
  state:
    description:
      - State of the web site
    type: str
    choices: [ absent, started, stopped, restarted ]
  physical_path:
    description:
      - The physical path on the remote host to use for the new site.
      - The specified folder must already exist.
    type: str
  application_pool:
    description:
      - The application pool in which the new site executes.
    type: str
  port:
    description:
      - The port to bind to / use for the new site.
    type: int
  ip:
    description:
      - The IP address to bind to / use for the new site.
    type: str
  hostname:
    description:
      - The host header to bind to / use for the new site.
    type: str
  ssl:
    description:
      - Enables HTTPS binding on the site..
    type: str
  parameters:
    description:
      - Custom site Parameters from string where properties are separated by a pipe and property name/values by colon Ex. "foo:1|bar:2"
    type: str
seealso:
- module: win_iis_virtualdirectory
- module: win_iis_webapplication
- module: win_iis_webapppool
- module: win_iis_webbinding
author:
- Henrik Wallström (@henrikwallstrom)
'''

EXAMPLES = r'''

# Start a website

- name: Acme IIS site
  win_iis_website:
    name: Acme
    state: started
    port: 80
    ip: 127.0.0.1
    hostname: acme.local
    application_pool: acme
    physical_path: C:\sites\acme
    parameters: logfile.directory:C:\sites\logs
  register: website

# Remove Default Web Site and the standard port 80 binding
- name: Remove Default Web Site
  win_iis_website:
    name: "Default Web Site"
    state: absent

# Some commandline examples:

# This return information about an existing host
# $ ansible -i vagrant-inventory -m win_iis_website -a "name='Default Web Site'" window
# host | success >> {
#     "changed": false,
#     "site": {
#         "ApplicationPool": "DefaultAppPool",
#         "Bindings": [
#             "*:80:"
#         ],
#         "ID": 1,
#         "Name": "Default Web Site",
#         "PhysicalPath": "%SystemDrive%\\inetpub\\wwwroot",
#         "State": "Stopped"
#     }
# }

# This stops an existing site.
# $ ansible -i hosts -m win_iis_website -a "name='Default Web Site' state=stopped" host

# This creates a new site.
# $ ansible -i hosts -m win_iis_website -a "name=acme physical_path=C:\\sites\\acme" host

# Change logfile.
# $ ansible -i hosts -m win_iis_website -a "name=acme physical_path=C:\\sites\\acme" host
'''
