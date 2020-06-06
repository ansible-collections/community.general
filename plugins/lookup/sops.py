# -*- coding: utf-8 -*-
#
#  Copyright 2018 Edoardo Tenani <e.tenani@arduino.cc> [@endorama]
#
# This file is part of Ansible.
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_native
from ansible_collections.community.general.plugins.module_utils.sops import Sops, SopsError

from ansible.utils.display import Display
display = Display()


DOCUMENTATION = """
    lookup: sops
    author: Edoardo Tenani (@endorama) <e.tenani@arduino.cc>
    short_description: Read sops encrypted file contents
    description:
        - This lookup returns the contents from a file on the Ansible controller's file system.
        - This lookup requires the C(sops) executable to be available in the controller PATH.
    options:
        _terms:
            description: path(s) of files to read
            required: True
    notes:
        - This lookup does not understand 'globbing' - use the fileglob lookup instead.
"""

EXAMPLES = """
tasks:
  - name: Output secrets to screen (BAD IDEA!)
    debug:
        msg: "Content: {{ lookup('sops', item) }}"
    loop:
        - sops-encrypted-file.enc.yaml

  - name: Add SSH private key
    copy:
        content: "{{ lookup('sops', user + '-id_rsa') }}"
        dest: /home/{{ user }}/.ssh/id_rsa
        owner: "{{ user }}"
        group: "{{ user }}"
        mode: 0600
    no_log: true  # avoid content to be written to log
"""

RETURN = """
    _raw:
        description: decrypted file content
"""


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []

        for term in terms:
            display.debug("Sops lookup term: %s" % term)
            lookupfile = self.find_file_in_search_path(variables, 'files', term)
            display.vvvv(u"Sops lookup using %s as file" % lookupfile)

            if not lookupfile:
                raise AnsibleLookupError("could not locate file in lookup: %s" % to_native(term))

            try:
                output = Sops.decrypt(lookupfile, display=display)
            except SopsError as e:
                raise AnsibleLookupError(to_native(e))

            ret.append(output.rstrip())

        return ret
