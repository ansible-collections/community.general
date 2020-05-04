# (c) 2020, Jose Angel Munoz <josea.munoz(at)gmail.com>
# (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    lookup: mergelist
    author: Jose Angel Munoz <josea.munoz@gmail.com>
    short_description: Merges lists of dictionaries by a given key
    description:
      - This lookup returns the contents of two or more merged lists of dictionaries using a common key.
    options:
      _terms:
        description: List(s) to merge.
        required: True
      key:
        description: Common key used to merge.
        required: False
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
    vars:
      list1:
        - id: myname01
          param01: myparam01
        - id: myname02
          param01: myparam02
      list2:
        - id: myname01
          param01: myparam03
        - id: myname02
          param02: myparam04
        - id: myname03
          param03: myparam03

  - name: Merges list1, list2 and list3 with 'id' as key
    debug:
      msg: "{{ query('community.general.mergelist', list1, list2, list3, key='id') }}"
    vars:
      list1:
        - id: myname01
          param01: myparam01
        - id: myname02
          param01: myparam02
      list2:
        - id: myname01
          param01: myparam03
        - id: myname02
          param02: myparam04
        - id: myname03
          param03: myparam03
      list3:
        - id: myname01
          param03: myparam05
"""

RETURN = """
  _list:
    description:
      - Medged list of dictionaries.
"""

from collections import defaultdict
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError


class LookupModule(LookupBase):
    def run(self, terms, variables=None, key='name', **kwargs):

        array = defaultdict(dict)

        for term in terms:
            for item in term:
                try:
                    array[item[key]].update(item)
                except KeyError as keyexception:
                    raise AnsibleError("Key not found: %s" % keyexception)
                except TypeError as errorexception:
                    raise AnsibleError("Incorrect formatting: %s" %
                                       errorexception)
        return list(array.values())
