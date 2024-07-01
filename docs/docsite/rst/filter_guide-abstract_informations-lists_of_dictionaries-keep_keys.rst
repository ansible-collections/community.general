..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

keep_keys
"""""""""

Use the filter :ansplugin:`community.general.keep_keys#filter` if you have a list of dictionaries and want to keep certain keys only.

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


* By default, match keys that equal any of the items in the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1

   target: ['k0_x0', 'k1_x1']
   result: "{{ input | community.general.keep_keys(target=target) }}"


gives

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - {k0_x0: A0, k1_x1: B0}
     - {k0_x0: A1, k1_x1: B1}

 
.. versionadded:: 9.1.0

* The results of the below examples 1-5 are all the same:

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - {k0_x0: A0, k1_x1: B0}
     - {k0_x0: A1, k1_x1: B1}


1. Match keys that equal any of the items in the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: equal
   target: ['k0_x0', 'k1_x1']
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

2. Match keys that start with any of the items in the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: starts_with
   target: ['k0', 'k1']
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

3. Match keys that end with any of the items in target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: ends_with
   target: ['x0', 'x1']
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

4. Match keys by the regex.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: regex
   target: ['^.*[01]_x.*$']
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

5. Match keys by the regex.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: regex
   target: ^.*[01]_x.*$
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"


* The results of the below examples 6-9 are all the same:

.. code-block:: yaml
   :emphasize-lines: 1-

   result:
     - {k0_x0: A0}
     - {k0_x0: A1}


6. Match keys that equal the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: equal
   target: k0_x0
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

7. Match keys that start with the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: starts_with
   target: k0
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

8. Match keys that end with the target.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: ends_with
   target: x0
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

9. Match keys by the regex.

.. code-block:: yaml+jinja
   :emphasize-lines: 1,2

   mp: regex
   target: ^.*0_x.*$
   result: "{{ input | community.general.keep_keys(target=target, matching_parameter=mp) }}"

