Example list_merge=replace (default):

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', replace lists (default)
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true) }}"
    vars:
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
  - debug:
      var: list3

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

Example list_merge=keep

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', keep lists
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true,
                                                 list_merge='keep') }}"
    vars:
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
  - debug:
      var: list3

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

Example list_merge=append

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', append lists
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true,
                                                 list_merge='append') }}"
    vars:
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
  - debug:
      var: list3

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

Example list_merge=prepend

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', prepend lists
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true,
                                                 list_merge='prepend') }}"
    vars:
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
  - debug:
      var: list3

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

Example list_merge=append_rp

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', append lists 'remove present'
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true,
                                                 list_merge='append_rp') }}"
    vars:
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
  - debug:
      var: list3

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

Example list_merge=prepend_rp

.. code-block:: yaml+jinja

  ---
  - name: Merge recursive by 'name', prepend lists 'remove present'
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name',
                                                 recursive=true,
                                                 list_merge='prepend_rp') }}"
    vars:
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
  - debug:
      var: list3

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

