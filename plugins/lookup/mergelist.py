# (c) 2020, Jose Angel Munoz <josea.munoz(at)gmail.com>
# (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    lookup: mergelist
    author: Jose Angel Munoz <josea.munoz@gmail.com>
    short_description: merges lists from a given array key
    description:
      - This lookup returns the contents of two or more merged lists using a common key.
    options:
      _terms:
        description: list(s) to merge
        required: True
    notes:
      - if key is not defined, "name" will be the default
      - use query if you want to return a list when a single value is given.
'''

EXAMPLES = """
  - name: Merges list1 and list2 with 'name' as key
    debug:
      msg: "{{ query('community.general.mergelist', list1, list2) }}"
    vars:
      list1:
        - name: myname01
          param01: myparam01
        - name: myname02
          param01: myparam02
      list2:
        - name: myname01
          param01: myparam03
        - name: myname02
          param02: myparam04
        - name: myname03
          param03: myparam03

  - name: Merges list1 and list2 with 'id' as key
    debug:
      msg: "{{ query('community.general.mergelist', list1, list2, key='id') }}"
"""

RETURN = """
  _list:
    description:
      - medged list with key and value
"""

from collections import defaultdict
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        array = defaultdict(dict)
        arraykey = "name"

        for items in terms:

            if isinstance(items, str):
                arraykey = items

            elif isinstance(items, list):
                for item in items:
                    try:
                        array[item[arraykey]].update(item)
                    except KeyError as exception:
                        raise AnsibleError("Key not found: %s" % exception)
            ret = list(array.values())

        return ret
