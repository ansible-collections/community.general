..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Merging lists of dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have two or more lists of dictionaries and want to combine them into a list of merged dictionaries, where the dictionaries are merged by an attribute, you can use the :ansplugin:`community.general.lists_mergeby <community.general.lists_mergeby#filter>` filter.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See the documentation for the :ansplugin:`community.general.yaml callback plugin <community.general.yaml#callback>`.

Let us use the lists below in the following examples:

.. code-block:: yaml

  list1:
    - {name: foo, extra: true}
    - {name: bar, extra: false}
    - {name: meh, extra: true}

  list2:
    - {name: foo, path: /foo}
    - {name: baz, path: /baz}

Two lists
"""""""""
In the example below the lists are merged by the attribute ``name``:

.. code-block:: yaml+jinja

  list3: "{{ list1 |
             community.general.lists_mergeby(list2, 'name') }}"

This produces:

.. code-block:: yaml

  list3:
    - {name: bar, extra: false}
    - {name: baz, path: /baz}
    - {name: foo, extra: true, path: /foo}
    - {name: meh, extra: true}


.. versionadded:: 2.0.0

List of two lists
"""""""""""""""""
It is possible to use a list of lists as an input of the filter:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name') }}"

This produces the same result as in the previous example:

.. code-block:: yaml

  list3:
    - {name: bar, extra: false}
    - {name: baz, path: /baz}
    - {name: foo, extra: true, path: /foo}
    - {name: meh, extra: true}

Single list
"""""""""""
It is possible to merge single list:

.. code-block:: yaml+jinja

  list3: "{{ [list1 + list2, []] |
             community.general.lists_mergeby('name') }}"

This produces the same result as in the previous example:

.. code-block:: yaml

  list3:
    - {name: bar, extra: false}
    - {name: baz, path: /baz}
    - {name: foo, extra: true, path: /foo}
    - {name: meh, extra: true}


The filter also accepts two optional parameters: :ansopt:`community.general.lists_mergeby#filter:recursive` and :ansopt:`community.general.lists_mergeby#filter:list_merge`. This is available since community.general 4.4.0.

**recursive**
    Is a boolean, default to ``false``. Should the :ansplugin:`community.general.lists_mergeby#filter` filter recursively merge nested hashes. Note: It does not depend on the value of the ``hash_behaviour`` setting in ``ansible.cfg``.

**list_merge**
    Is a string, its possible values are :ansval:`replace` (default), :ansval:`keep`, :ansval:`append`, :ansval:`prepend`, :ansval:`append_rp` or :ansval:`prepend_rp`. It modifies the behaviour of :ansplugin:`community.general.lists_mergeby#filter` when the hashes to merge contain arrays/lists.

The examples below set :ansopt:`community.general.lists_mergeby#filter:recursive=true` and display the differences among all six options of :ansopt:`community.general.lists_mergeby#filter:list_merge`. Functionality of the parameters is exactly the same as in the filter :ansplugin:`ansible.builtin.combine#filter`. See :ref:`Combining hashes/dictionaries <combine_filter>` to learn details about these options.

Let us use the lists below in the following examples

.. code-block:: yaml

  list1:
    - name: myname01
      param01:
        x: default_value
        y: default_value
        list: [default_value]
    - name: myname02
      param01: [1, 1, 2, 3]

  list2:
    - name: myname01
      param01:
        y: patch_value
        z: patch_value
        list: [patch_value]
    - name: myname02
      param01: [3, 4, 4]

list_merge=replace (default)
""""""""""""""""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=replace` (default):

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true) }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [patch_value]
        z: patch_value
    - name: myname02
      param01: [3, 4, 4]

list_merge=keep
"""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=keep`:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='keep') }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [default_value]
        z: patch_value
    - name: myname02
      param01: [1, 1, 2, 3]

list_merge=append
"""""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=append`:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='append') }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [default_value, patch_value]
        z: patch_value
    - name: myname02
      param01: [1, 1, 2, 3, 3, 4, 4]

list_merge=prepend
""""""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=prepend`:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='prepend') }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [patch_value, default_value]
        z: patch_value
    - name: myname02
      param01: [3, 4, 4, 1, 1, 2, 3]

list_merge=append_rp
""""""""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=append_rp`:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='append_rp') }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [default_value, patch_value]
        z: patch_value
    - name: myname02
      param01: [1, 1, 2, 3, 4, 4]

list_merge=prepend_rp
"""""""""""""""""""""
Example :ansopt:`community.general.lists_mergeby#filter:list_merge=prepend_rp`:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2] |
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='prepend_rp') }}"

This produces:

.. code-block:: yaml

  list3:
    - name: myname01
      param01:
        x: default_value
        y: patch_value
        list: [patch_value, default_value]
        z: patch_value
    - name: myname02
      param01: [3, 4, 4, 1, 1, 2]

