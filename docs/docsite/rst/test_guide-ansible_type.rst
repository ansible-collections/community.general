..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Test ansible_type
-----------------

Use the test :ansplugin:`community.general.ansible_type#test` if you want to test the type of Ansible data.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ansplugin:`the documentation for the community.general.yaml callback plugin <community.general.yaml#callback>`.

.. versionadded:: 9.2.0

**Substitution converts str to AnsibleUnicode**

* String. AnsibleUnicode.

.. code-block:: yaml+jinja

   dtype AnsibleUnicode
   data: "abc"
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

* String. AnsibleUnicode alias str.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   dtype str
   data: "abc"
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

* List. All items are AnsibleUnicode.

.. code-block:: yaml+jinja

   dtype list[AnsibleUnicode]
   data: ["a", "b", "c"]
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

* Dictionary. All keys are AnsibleUnicode. All values are AnsibleUnicode.

.. code-block:: yaml+jinja

   dtype dict[AnsibleUnicode, AnsibleUnicode]
   data: {"a": "foo", "b": "bar", "c": "baz"}
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

**No substitution and no alias. Type of strings is str**

* String

.. code-block:: yaml+jinja

   dtype: str
   result: '{{ "abc" is community.general.ansible_type }}'
   result => true

* Integer

.. code-block:: yaml+jinja

   dtype: int
   result: '{{ 123 is community.general.ansible_type }}'
   result => true

* Float

.. code-block:: yaml+jinja

   dtype: float
   result: '{{ 123.45 is community.general.ansible_type }}'
   result => true

* Boolean

.. code-block:: yaml+jinja

   dtype: bool
   result: '{{ true is community.general.ansible_type }}'
   result => true

* List. All items are strings.

.. code-block:: yaml+jinja

   dtype: list[str]
   result: '{{ ["a", "b", "c"] is community.general.ansible_type }}'
   result => true

* List of dictionaries.

.. code-block:: yaml+jinja

   dtype: list[dict]
   result: '{{ [{"a": 1}, {"b": 2}] is community.general.ansible_type }}'
   result => true

* Dictionary. All keys are strings. All values are integers.

.. code-block:: yaml+jinja

   dtype: dict[str, int]
   result: '{{ {"a": 1} is community.general.ansible_type }}'
   result => true

* Dictionary. All keys are strings. All values are integers.

.. code-block:: yaml+jinja

   dtype: dict[str, int]
   result: '{{ {"a": 1, "b": 2} is community.general.ansible_type }}'
   result => true

**Type of strings is AnsibleUnicode or str**

* Dictionary. The keys are integers or strings. All values are strings.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   dtype: dict[int|str, str]
   data: {1: 'a', 'b': 'b'}
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

* Dictionary. All keys are integers. All values are keys.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   dtype: dict[int, str]
   data: {1: 'a', 2: 'b'}
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

* Dictionary. All keys are strings. Multiple types values.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   dtype: dict[str, bool|dict|float|int|list|str]
   data: {'a': 1, 'b': 1.1, 'c': 'abc', 'd': True, 'e': ['x', 'y', 'z'], 'f': {'x': 1, 'y': 2}}
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

* List. Multiple types items.

.. code-block:: yaml+jinja

   alias: {"AnsibleUnicode": "str"}
   dtype: list[bool|dict|float|int|list|str]
   data: [1, 2, 1.1, 'abc', True, ['x', 'y', 'z'], {'x': 1, 'y': 2}]
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

**Option dtype is list**

* AnsibleUnicode or str

.. code-block:: yaml+jinja

   dtype: ['AnsibleUnicode', 'str']
   data: abc
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

* float or int

.. code-block:: yaml+jinja

   dtype: ['float', 'int']
   data: 123
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

* float or int

.. code-block:: yaml+jinja

   dtype: ['float', 'int']
   data: 123.45
   result: '{{ data is community.general.ansible_type(dtype) }}'
   # result => true

**Multiple alias**

* int alias number

.. code-block:: yaml+jinja

   alias: {"int": "number", "float": "number"}
   dtype: number
   data: 123
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true

* float alias number

.. code-block:: yaml+jinja

   alias: {"int": "number", "float": "number"}
   dtype: number
   data: 123.45
   result: '{{ data is community.general.ansible_type(dtype, alias) }}'
   # result => true
