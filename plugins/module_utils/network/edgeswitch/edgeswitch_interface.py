# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2018 Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import re


class InterfaceConfiguration:
    def __init__(self):
        self.commands = []
        self.merged = False

    def has_same_commands(self, interface):
        len1 = len(self.commands)
        len2 = len(interface.commands)
        return len1 == len2 and len1 == len(frozenset(self.commands).intersection(interface.commands))


def merge_interfaces(interfaces):
    """ to reduce commands generated by an edgeswitch module
        we take interfaces one by one and we try to merge them with neighbors if everyone has same commands to run
    """
    merged = {}

    for i, interface in interfaces.items():
        if interface.merged:
            continue
        interface.merged = True

        match = re.match(r'(\d+)\/(\d+)', i)
        group = int(match.group(1))
        start = int(match.group(2))
        end = start

        while True:
            try:
                start = start - 1
                key = '{0}/{1}'.format(group, start)
                neighbor = interfaces[key]
                if not neighbor.merged and interface.has_same_commands(neighbor):
                    neighbor.merged = True
                else:
                    break
            except KeyError:
                break
        start = start + 1

        while True:
            try:
                end = end + 1
                key = '{0}/{1}'.format(group, end)
                neighbor = interfaces[key]
                if not neighbor.merged and interface.has_same_commands(neighbor):
                    neighbor.merged = True
                else:
                    break
            except KeyError:
                break
        end = end - 1

        if end == start:
            key = '{0}/{1}'.format(group, start)
        else:
            key = '{0}/{1}-{2}/{3}'.format(group, start, group, end)

        merged[key] = interface
    return merged
