..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

keep_keys
"""""""""

Use the filter ``keep_keys`` if you have a list of dictionaries and want to keep certain keys only.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ref:`the documentation for the community.general.yaml callback plugin <ansible_collections.community.general.yaml_callback>`.

Let us use the below list in the following examples:

.. code-block:: yaml

  list1:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

* The results of the below examples 1-5 are all the same:

.. code-block:: yaml

  r:
    - {k0_x0: A0, k1_x1: B0}
    - {k0_x0: A1, k1_x1: B1}

1) By default match keys that equal any of the items in the target.

.. code-block:: yaml+jinja

  t: [k0_x0, k1_x1]
  r: "{{ list1 | community.general.keep_keys(target=t) }}"


.. versionadded:: 9.1.0

2) Match keys that start with any of the items in the target.

.. code-block:: yaml+jinja

  t: [k0, k1]
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='starts_with') }}"

3) Match keys that end with any of the items in target.

.. code-block:: yaml+jinja

  t: [x0, x1]
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='ends_with') }}"

4) Match keys by the regex.

.. code-block:: yaml+jinja

  t: ['^.*[01]_x.*$']
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='regex') }}"

5) Match keys by the regex.

.. code-block:: yaml+jinja

  t: '^.*[01]_x.*$'
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='regex') }}"


* The results of the below examples 6-9 are all the same:

.. code-block:: yaml

  r:
    - {k0_x0: A0}
    - {k0_x0: A1}

6) By default match keys that equal the target.

.. code-block:: yaml+jinja

  t: k0_x0
  r: "{{ list1 | community.general.keep_keys(target=t) }}"

7) Match keys that start with the target.

.. code-block:: yaml+jinja

  t: k0
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='starts_with') }}"

8) Match keys that end with the target.

.. code-block:: yaml+jinja

  t: x0
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='ends_with') }}"

9) Match keys by the regex.

.. code-block:: yaml+jinja

  t: '^.*0_x.*$'
  r: "{{ list1 | community.general.keep_keys(target=t, matching_parameter='regex') }}"

