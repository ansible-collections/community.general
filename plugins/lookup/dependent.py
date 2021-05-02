# (c) 2015-2021, Felix Fontein <felix@fontein.de>
# (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
lookup: dependent
short_description: Composes a list with nested elements of other lists or dicts which can depend on previous indices
version_added: 2.5.0
description:
  - "Takes the input lists and returns a list with elements that are lists, dictionaries,
     or template expressions which evaluate to lists or dicts, composed of the elements of
     the input evaluated lists and dictionaries."
options:
  _raw:
    description:
      - A list where the elements are strings, lists, or dictionaries.
      - Lists are simply iterated over.
      - Dictionaries are iterated over and returned as if they would be processed by the
        R(ansible.builtin.dict filter,ansible_collections.ansible.builtin.dict_filter).
      - Strings are evaluated as Jinja2 expressions which can access the previously chosen
        elements with C(item.<index>). The result must be a list or a dictionary.
    type: list
    elements: raw
    required: true
"""

EXAMPLES = """
- name: Install/remove public keys for active admin users
  ansible.posix.authorized_key:
    user: "{{ item.0.key }}"
    key: "{{ lookup('file', item.1.public_key) }}"
    state: "{{ 'present' if item.1.active else 'absent' }}"
  when: item.0.value.active
  loop: "{{ lookup('community.general.dependent', admin_user_data, 'admin_ssh_keys[item.0.key]') }}"
  # Alternatively, you could also use the old with_* syntax:
  #   with_community.general.dependent:
  #   - admin_user_data
  #   - "admin_ssh_keys[item.0.key]"
  loop_control:
    # Makes the output readable, so that it doesn't contain the whole subdictionaries and lists
    label: "{{ [item.0.key, 'active' if item.1.active else 'inactive', item.1.public_key] }}"
  vars:
    admin_user_data:
      admin1:
        name: Alice
        active: yes
      admin2:
        name: Bob
        active: yes
    admin_ssh_keys:
      admin1:
      - private_key: keys/private_key_admin1.pem
        public_key: keys/private_key_admin1.pub
        active: yes
      admin2:
      - private_key: keys/private_key_admin2.pem
        public_key: keys/private_key_admin2.pub
        active: yes
      - private_key: keys/private_key_admin2-old.pem
        public_key: keys/private_key_admin2-old.pub
        active: no

- name: Update DNS records
  community.aws.route53:
    zone: "{{ item.0.key }}"
    record: "{{ item.1.key ~ '.' if item.1.key else '' }}{{ item.0.key }}"
    type: "{{ item.2.key }}"
    ttl: "{{ 3600 if item.2.value.ttl is undefined else item.2.value.ttl }}"
    value: "{{ item.2.value.value }}"
    state: "{{ 'absent' if (item.2.value.absent if item.2.value.absent is defined else False) else 'present' }}"
    overwrite: true
  loop_control:
    # Makes the output readable, so that it doesn't contain the whole subdictionaries and lists
    label: "{{ [item.0.key, item.1.key, item.2.key, item.2.value.get('ttl', 3600), item.2.value.get('absent', False), item.2.value.value] }}"
  loop: "{{ lookup('community.general.dependent', dns_setup, 'item.0.value', 'item.1.value') }}"
  # Alternatively, you can also do:
  #   loop: "{{ lookup('community.general.dependent', 'dns_setup', 'item.0.value', 'item.1.value') }}"
  # the dependent lookup will evaluate 'dns_setup'.
  vars:
    dns_setup:
      example.com:
        '':
          A:
            value:
            - 1.2.3.4
          AAAA:
            value:
            - "2a01:1:2:3::1"
        'test._domainkey':
          TXT:
            ttl: 300
            value:
            - '"k=rsa; t=s; p=MIGfMA..."'
      example.org:
        'www':
          A:
            value:
            - 1.2.3.4
            - 5.6.7.8
"""

RETURN = """
  _list:
    description:
      - A list composed of dictionaries whose keys are indices for the input list.
    type: list
    elements: dict
    sample:
      - 0: a
        1: test
      - 0: a
        1: foo
      - 0: b
        1: bar
"""

from ansible.plugins.lookup import LookupBase
from ansible.template import Templar
from ansible.errors import AnsibleError


class LookupModule(LookupBase):
    def __evaluate(self, expression, templar, variables):
        """Evaluate expression with templar.

        ``expression`` is the expression to evaluate.
        ``variables`` are the variables to use.
        """
        templar.available_variables = variables or {}
        return templar.template("{0}{1}{2}".format("{{", expression, "}}"), cache=False)

    def __process(self, result, terms, index, current, templar, variables):
        """Fills ``result`` list with evaluated items.

        ``result`` is a list where the resulting items are placed.
        ``terms`` is the list of terms provided to the plugin.
        ``index`` is the current index to be processed in the list.
        ``current`` is a list, where the first ``index`` items are filled
            with the values of ``item[i]`` for ``i < index``.
        ``variables`` are the variables currently available.
        """
        # Prepare current state (value of 'item')
        data = dict((i, current[i]) for i in range(index))

        # If we are done, add to result list:
        if index == len(terms):
            result.append(data)
            return

        if isinstance(terms[index], (dict, list, tuple)):
            # Use lists, dicts and tuples directly
            items = terms[index]
        else:
            # Evaluate expression in current context
            vars = variables.copy()
            vars['item'] = data
            try:
                items = self.__evaluate(terms[index], templar, variables=vars)
            except Exception as e:
                raise AnsibleError('Caught "{0}" while evaluating "{1}" with item == {2}'.format(e, terms[index], data))

        # Continue
        if isinstance(items, dict):
            for i, v in sorted(items.items()):
                current[index] = dict([('key', i), ('value', v)])
                self.__process(result, terms, index + 1, current, templar, variables)
        else:
            for i in items:
                current[index] = i
                self.__process(result, terms, index + 1, current, templar, variables)

    def run(self, terms, variables=None, **kwargs):
        """Generate list."""
        result = []
        if len(terms) > 0:
            templar = Templar(loader=self._templar._loader)
            self.__process(result, terms, 0, [None] * len(terms), templar, variables)
        return result
