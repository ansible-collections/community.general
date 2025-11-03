..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Union, intersection and difference of lists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with Ansible Core 2.16, the builtin filters :ansplugin:`ansible.builtin.union#filter`, :ansplugin:`ansible.builtin.intersect#filter`, :ansplugin:`ansible.builtin.difference#filter` and :ansplugin:`ansible.builtin.symmetric_difference#filter` began to behave differently and do no longer preserve the item order. Items in the resulting lists are returned in arbitrary order and the order can vary between subsequent runs.

The Ansible community.general collection provides the following additional list filters:

- :ansplugin:`community.general.lists_union#filter`
- :ansplugin:`community.general.lists_intersect#filter`
- :ansplugin:`community.general.lists_difference#filter`
- :ansplugin:`community.general.lists_symmetric_difference#filter`

These filters preserve the item order, eliminate duplicates and are an extended version of the builtin ones, because they can operate on more than two lists.

.. note:: Stick to the builtin filters, when item order is not important or when you do not need the n-ary operating mode. The builtin filters are faster, because they rely mostly on sets as their underlying datastructure.

Let us use the lists below in the following examples:

.. ansible-output-meta::

  actions:
    - name: reset-previous-blocks
    - name: set-template
      template:
        env:
          ANSIBLE_CALLBACK_RESULT_FORMAT: yaml
        variables:
          data:
            previous_code_block: yaml
            previous_code_block_index: 0
          computation:
            previous_code_block: yaml+jinja
        postprocessors:
          - name: reformat-yaml
        language: yaml
        skip_first_lines: 2
        playbook: |-
          - hosts: localhost
            gather_facts: false
            tasks:
              - vars:
                  @{{ data | indent(8) }}@
                  @{{ computation | indent(8) }}@
                ansible.builtin.debug:
                  var: result

.. code-block:: yaml

  A: [9, 5, 7, 1, 9, 4, 10, 5, 9, 7]
  B: [4, 1, 2, 8, 3, 1, 7]
  C: [10, 2, 1, 9, 1]

The union of ``A`` and ``B`` can be written as:

.. code-block:: yaml+jinja

  result: "{{ A | community.general.lists_union(B) }}"

This statement produces:

.. ansible-output-data::

    playbook: ~

.. code-block:: yaml

  result:
    - 9
    - 5
    - 7
    - 1
    - 4
    - 10
    - 2
    - 8
    - 3

If you want to calculate the intersection of ``A``, ``B`` and ``C``, you can use the following statement:

.. code-block:: yaml+jinja

  result: "{{ A | community.general.lists_intersect(B, C) }}"

Alternatively, you can use a list of lists as an input of the filter

.. code-block:: yaml+jinja

  result: "{{ [A, B] | community.general.lists_intersect(C) }}"

or

.. code-block:: yaml+jinja

  result: "{{ [A, B, C] | community.general.lists_intersect(flatten=true) }}"

All three statements are equivalent and give:

.. ansible-output-data::

    playbook: ~

.. code-block:: yaml

  result:
    - 1

.. note:: Be aware that in most cases, filter calls without any argument require ``flatten=true``, otherwise the input is returned as result. The reason for this is, that the input is considered as a variable argument and is wrapped by an additional outer list. ``flatten=true`` ensures that this list is removed before the input is processed by the filter logic.

The filters :ansplugin:`community.general.lists_difference#filter` or :ansplugin:`community.general.lists_symmetric_difference#filter` can be used in the same way as the filters in the examples above. They calculate the difference or the symmetric difference between two or more lists and preserve the item order.

For example, the symmetric difference of ``A``, ``B`` and ``C`` may be written as:

.. code-block:: yaml+jinja

  result: "{{ A | community.general.lists_symmetric_difference(B, C) }}"

This gives:

.. ansible-output-data::

    playbook: ~

.. code-block:: yaml

  result:
    - 5
    - 8
    - 3
    - 1
