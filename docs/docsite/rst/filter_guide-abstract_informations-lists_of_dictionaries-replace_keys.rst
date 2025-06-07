..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

replace_keys
""""""""""""

Use the filter :ansplugin:`community.general.replace_keys#filter` if you have a list of dictionaries and want to replace certain keys.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ansplugin:`the documentation for the community.general.yaml callback plugin <community.general.yaml#callback>`.


Let us use the below list in the following examples:

.. code-block:: yaml

   input:
     - k0_x0: A0
       k1_x1: B0
       k2_x2: [C0]
       k3_x3: foo
     - k0_x0: A1
       k1_x1: B1
       k2_x2: [C1]
       k3_x3: bar


* By default, match keys that equal any of the attributes before.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-3

   target:
     - {after: a0, before: k0_x0}
     - {after: a1, before: k1_x1}

   result: "{{ input | community.general.replace_keys(target=target) }}"


gives

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - a0: A0
       a1: B0
       k2_x2: [C0]
       k3_x3: foo
     - a0: A1
       a1: B1
       k2_x2: [C1]
       k3_x3: bar


.. versionadded:: 9.1.0

* The results of the below examples 1-3 are all the same:

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - a0: A0
       a1: B0
       k2_x2: [C0]
       k3_x3: foo
     - a0: A1
       a1: B1
       k2_x2: [C1]
       k3_x3: bar


1. Replace keys that starts with any of the attributes before.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-4

   mp: starts_with
   target:
     - {after: a0, before: k0}
     - {after: a1, before: k1}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"

2. Replace keys that ends with any of the attributes before.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-4

   mp: ends_with
   target:
     - {after: a0, before: x0}
     - {after: a1, before: x1}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"

3. Replace keys that match any regex of the attributes before.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-4

   mp: regex
   target:
     - {after: a0, before: ^.*0_x.*$}
     - {after: a1, before: ^.*1_x.*$}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"


* The results of the below examples 4-5 are the same:

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - {X: foo}
     - {X: bar}


4. If more keys match the same attribute before the last one will be used.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-3

   mp: regex
   target:
     - {after: X, before: ^.*_x.*$}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"

5. If there are items with equal attribute before the first one will be used.

.. code-block:: yaml+jinja
   :emphasize-lines: 1-3

   mp: regex
   target:
     - {after: X, before: ^.*_x.*$}
     - {after: Y, before: ^.*_x.*$}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"


6. If there are more matches for a key the first one will be used.

.. code-block:: yaml
   :emphasize-lines: 1-

   input:
     - {aaa1: A, bbb1: B, ccc1: C}
     - {aaa2: D, bbb2: E, ccc2: F}


.. code-block:: yaml+jinja
   :emphasize-lines: 1-4

   mp: starts_with
   target:
     - {after: X, before: a}
     - {after: Y, before: aa}

   result: "{{ input | community.general.replace_keys(target=target, matching_parameter=mp) }}"

gives

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - {X: A, bbb1: B, ccc1: C}
     - {X: D, bbb2: E, ccc2: F}


