Merging lists of dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have two or more lists of dictionaries and want to combine them into a list of merged dictionaries, where the dictionaries are merged by an attribute, you can use the ``lists_mergeby`` filter.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ref:`the documentation for the community.general.yaml callback plugin <ansible_collections.community.general.yaml_callback>`.

Let us use the lists below in the following examples:

.. code-block:: yaml

  list1:
    - name: foo
      extra: true
    - name: bar
      extra: false
    - name: meh
      extra: true

  list2:
    - name: foo
      path: /foo
    - name: baz
      path: /baz

In the example below the lists are merged by the attribute ``name``:

.. code-block:: yaml+jinja

  list3: "{{ list1|
             community.general.lists_mergeby(list2, 'name') }}"

This produces:

.. code-block:: yaml

  list3:
  - extra: false
    name: bar
  - name: baz
    path: /baz
  - extra: true
    name: foo
    path: /foo
  - extra: true
    name: meh


.. versionadded:: 2.0.0

It is possible to use a list of lists as an input of the filter:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name') }}"

This produces the same result as in the previous example:

.. code-block:: yaml

  list3:
  - extra: false
    name: bar
  - name: baz
    path: /baz
  - extra: true
    name: foo
    path: /foo
  - extra: true
    name: meh


The filter also accepts two optional parameters: ``recursive`` and ``list_merge``. These parameters are only supported when used with ansible-base 2.10 or ansible-core, but not with Ansible 2.9. This is available since community.general 4.4.0.

**recursive**
    Is a boolean, default to ``False``. Should the ``community.general.lists_mergeby`` recursively merge nested hashes. Note: It does not depend on the value of the ``hash_behaviour`` setting in ``ansible.cfg``.

**list_merge**
    Is a string, its possible values are ``replace`` (default), ``keep``, ``append``, ``prepend``, ``append_rp`` or ``prepend_rp``. It modifies the behaviour of ``community.general.lists_mergeby`` when the hashes to merge contain arrays/lists.

The examples below set ``recursive=true`` and display the differences among all six options of ``list_merge``. Functionality of the parameters is exactly the same as in the filter ``combine``. See :ref:`Combining hashes/dictionaries <combine_filter>` to learn details about these options.

Let us use the lists below in the following examples

.. code-block:: yaml

  list1:
    - name: myname01
      param01:
        x: default_value
        y: default_value
        list:
          - default_value
    - name: myname02
      param01: [1, 1, 2, 3]

  list2:
    - name: myname01
      param01:
        y: patch_value
        z: patch_value
        list:
          - patch_value
    - name: myname02
      param01: [3, 4, 4, {key: value}]

Example ``list_merge=replace`` (default):

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true) }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - patch_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 3
    - 4
    - 4
    - key: value

Example ``list_merge=keep``:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='keep') }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - default_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 1
    - 1
    - 2
    - 3

Example ``list_merge=append``:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='append') }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - default_value
      - patch_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 1
    - 1
    - 2
    - 3
    - 3
    - 4
    - 4
    - key: value

Example ``list_merge=prepend``:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='prepend') }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - patch_value
      - default_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 3
    - 4
    - 4
    - key: value
    - 1
    - 1
    - 2
    - 3

Example ``list_merge=append_rp``:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='append_rp') }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - default_value
      - patch_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 1
    - 1
    - 2
    - 3
    - 4
    - 4
    - key: value

Example ``list_merge=prepend_rp``:

.. code-block:: yaml+jinja

  list3: "{{ [list1, list2]|
             community.general.lists_mergeby('name',
                                             recursive=true,
                                             list_merge='prepend_rp') }}"

This produces:

.. code-block:: yaml

  list3:
  - name: myname01
    param01:
      list:
      - patch_value
      - default_value
      x: default_value
      y: patch_value
      z: patch_value
  - name: myname02
    param01:
    - 3
    - 4
    - 4
    - key: value
    - 1
    - 1
    - 2

