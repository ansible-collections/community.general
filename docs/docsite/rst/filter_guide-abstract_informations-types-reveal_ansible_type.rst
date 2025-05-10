..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Filter reveal_ansible_type
""""""""""""""""""""""""""

Use the filter :ansplugin:`community.general.reveal_ansible_type#filter` if you want to get the type of Ansible data.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ansplugin:`the documentation for the community.general.yaml callback plugin <community.general.yaml#callback>`.

.. versionadded:: 9.2.0

**Substitution converts str to AnsibleUnicode**

* String. AnsibleUnicode.

.. code-block:: yaml+jinja

   data: "abc"
   result: '{{ data | community.general.reveal_ansible_type }}'
   # result => AnsibleUnicode

* String. AnsibleUnicode alias str.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   data: "abc"
   result: '{{ data | community.general.reveal_ansible_type(alias) }}'
   # result => str

* List. All items are AnsibleUnicode.

.. code-block:: yaml+jinja

   data: ["a", "b", "c"]
   result: '{{ data | community.general.reveal_ansible_type }}'
   # result => list[AnsibleUnicode]

* Dictionary. All keys are AnsibleUnicode. All values are AnsibleUnicode.

.. code-block:: yaml+jinja

   data: {"a": "foo", "b": "bar", "c": "baz"}
   result: '{{ data | community.general.reveal_ansible_type }}'
   # result => dict[AnsibleUnicode, AnsibleUnicode]

**No substitution and no alias. Type of strings is str**

* String

.. code-block:: yaml+jinja

   result: '{{ "abc" | community.general.reveal_ansible_type }}'
   # result => str

* Integer

.. code-block:: yaml+jinja

   result: '{{ 123 | community.general.reveal_ansible_type }}'
   # result => int

* Float

.. code-block:: yaml+jinja

   result: '{{ 123.45 | community.general.reveal_ansible_type }}'
   # result => float

* Boolean

.. code-block:: yaml+jinja

   result: '{{ true | community.general.reveal_ansible_type }}'
   # result => bool

* List. All items are strings.

.. code-block:: yaml+jinja

   result: '{{ ["a", "b", "c"] | community.general.reveal_ansible_type }}'
   # result => list[str]

* List of dictionaries.

.. code-block:: yaml+jinja

   result: '{{ [{"a": 1}, {"b": 2}] | community.general.reveal_ansible_type }}'
   # result => list[dict]

* Dictionary. All keys are strings. All values are integers.

.. code-block:: yaml+jinja

   result: '{{ {"a": 1} | community.general.reveal_ansible_type }}'
   # result => dict[str, int]

* Dictionary. All keys are strings. All values are integers.

.. code-block:: yaml+jinja

   result: '{{ {"a": 1, "b": 2} | community.general.reveal_ansible_type }}'
   # result => dict[str, int]

**Type of strings is AnsibleUnicode or str**

* Dictionary. The keys are integers or strings. All values are strings.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   data: {1: 'a', 'b': 'b'}
   result: '{{ data | community.general.reveal_ansible_type(alias) }}'
   # result => dict[int|str, str]

* Dictionary. All keys are integers. All values are keys.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   data: {1: 'a', 2: 'b'}
   result: '{{ data | community.general.reveal_ansible_type(alias) }}'
   # result => dict[int, str]

* Dictionary. All keys are strings. Multiple types values.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   data: {'a': 1, 'b': 1.1, 'c': 'abc', 'd': True, 'e': ['x', 'y', 'z'], 'f': {'x': 1, 'y': 2}}
   result: '{{ data | community.general.reveal_ansible_type(alias) }}'
   # result => dict[str, bool|dict|float|int|list|str]

* List. Multiple types items.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   data: [1, 2, 1.1, 'abc', True, ['x', 'y', 'z'], {'x': 1, 'y': 2}]
   result: '{{ data | community.general.reveal_ansible_type(alias) }}'
   # result => list[bool|dict|float|int|list|str]
