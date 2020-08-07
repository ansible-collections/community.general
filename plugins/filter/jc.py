# (c) 2015, Filipe Niero Felisbino <filipenf@gmail.com>
#
# This file is part of Ansible
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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
import importlib

try:
    import jc
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def jc(data, parser):
    '''Convert returned command output to JSON using the JC library'''

    if not HAS_LIB:
        raise AnsibleError('You need to install "jc" prior to running '
                           'jc filter')

    try:
        jc_parser = importlib.import_module('jc.parsers.' + parser)
        return jc_parser.parse(data, quiet=True)

    except Exception as e:
        raise AnsibleFilterError('Error in jc filter plugin:\n%s' % e)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'jc': jc
        }
