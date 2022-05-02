# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
  name: unicode_normalize
  short_description: Normalizes unicode strings to facilitate comparison of characters with normalized forms
  version_added: 3.7.0
  author: Andrew Pantuso (@Ajpantuso)
  description:
    - Normalizes unicode strings to facilitate comparison of characters with normalized forms.
  positional: form
  options:
    _input:
      description: A unicode string.
      type: string
      required: true
    form:
      description:
        - The normal form to use.
        - See U(https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize) for details.
      type: string
      default: NFC
      choices:
        - NFC
        - NFD
        - NFKC
        - NFKD
'''

EXAMPLES = '''
- name: Normalize unicode string
  ansible.builtin.set_fact:
    dictionary: "{{ 'ä' | community.general.unicode_normalize('NFKD') }}"
    # The resulting string has length 2: one letter is 'a', the other
    # the diacritic combiner.
'''

RETURN = '''
  _value:
    description: The normalized unicode string of the specified normal form.
    type: string
'''

from unicodedata import normalize

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible.module_utils.six import text_type


def unicode_normalize(data, form='NFC'):
    """Applies normalization to 'unicode' strings.

    Args:
        data: A unicode string piped into the Jinja filter
        form: One of ('NFC', 'NFD', 'NFKC', 'NFKD').
              See https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize for more information.

    Returns:
        A normalized unicode string of the specified 'form'.
    """

    if not isinstance(data, text_type):
        raise AnsibleFilterTypeError("%s is not a valid input type" % type(data))

    if form not in ('NFC', 'NFD', 'NFKC', 'NFKD'):
        raise AnsibleFilterError("%s is not a valid form" % form)

    return normalize(form, data)


class FilterModule(object):
    def filters(self):
        return {
            'unicode_normalize': unicode_normalize,
        }
