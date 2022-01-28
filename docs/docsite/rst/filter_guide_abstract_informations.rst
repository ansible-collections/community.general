Abstract transformations
------------------------

Dictionaries
^^^^^^^^^^^^

You can use the ``dict_kv`` filter to create a single-entry dictionary with ``value | community.general.dict_kv(key)``:

.. code-block:: yaml+jinja

    - name: Create a single-entry dictionary
      debug:
        msg: "{{ myvar | community.general.dict_kv('thatsmyvar') }}"
      vars:
        myvar: myvalue

    - name: Create a list of dictionaries where the 'server' field is taken from a list
      debug:
        msg: >-
          {{ myservers | map('community.general.dict_kv', 'server')
                       | map('combine', common_config) }}
      vars:
        common_config:
          type: host
          database: all
        myservers:
        - server1
        - server2

This produces:

.. code-block:: ansible-output

    TASK [Create a single-entry dictionary]  **************************************************
    ok: [localhost] => {
        "msg": {
            "thatsmyvar": "myvalue"
        }
    }

    TASK [Create a list of dictionaries where the 'server' field is taken from a list]  *******
    ok: [localhost] => {
        "msg": [
            {
                "database": "all",
                "server": "server1",
                "type": "host"
            },
            {
                "database": "all",
                "server": "server2",
                "type": "host"
            }
        ]
    }

.. versionadded:: 2.0.0

If you need to convert a list of key-value pairs to a dictionary, you can use the ``dict`` function. Unfortunately, this function cannot be used with ``map``. For this, the ``community.general.dict`` filter can be used:

.. code-block:: yaml+jinja

    - name: Create a dictionary with the dict function
      debug:
        msg: "{{ dict([[1, 2], ['a', 'b']]) }}"

    - name: Create a dictionary with the community.general.dict filter
      debug:
        msg: "{{ [[1, 2], ['a', 'b']] | community.general.dict }}"

    - name: Create a list of dictionaries with map and the community.general.dict filter
      debug:
        msg: >-
          {{ values | map('zip', ['k1', 'k2', 'k3'])
                    | map('map', 'reverse')
                    | map('community.general.dict') }}
      vars:
        values:
          - - foo
            - 23
            - a
          - - bar
            - 42
            - b

This produces:

.. code-block:: ansible-output

    TASK [Create a dictionary with the dict function]  ****************************************
    ok: [localhost] => {
        "msg": {
            "1": 2,
            "a": "b"
        }
    }

    TASK [Create a dictionary with the community.general.dict filter]  ************************
    ok: [localhost] => {
        "msg": {
            "1": 2,
            "a": "b"
        }
    }

    TASK [Create a list of dictionaries with map and the community.general.dict filter]  ******
    ok: [localhost] => {
        "msg": [
            {
                "k1": "foo",
                "k2": 23,
                "k3": "a"
            },
            {
                "k1": "bar",
                "k2": 42,
                "k3": "b"
            }
        ]
    }

.. versionadded:: 3.0.0

Grouping
^^^^^^^^

If you have a list of dictionaries, the Jinja2 ``groupby`` filter allows to group the list by an attribute. This results in a list of ``(grouper, list)`` namedtuples, where ``list`` contains all dictionaries where the selected attribute equals ``grouper``. If you know that for every ``grouper``, there will be a most one entry in that list, you can use the ``community.general.groupby_as_dict`` filter to convert the original list into a dictionary which maps ``grouper`` to the corresponding dictionary.

One example is ``ansible_facts.mounts``, which is a list of dictionaries where each has one ``device`` element to indicate the device which is mounted. Therefore, ``ansible_facts.mounts | community.general.groupby_as_dict('device')`` is a dictionary mapping a device to the mount information:

.. code-block:: yaml+jinja

    - name: Output mount facts grouped by device name
      debug:
        var: ansible_facts.mounts | community.general.groupby_as_dict('device')

    - name: Output mount facts grouped by mount point
      debug:
        var: ansible_facts.mounts | community.general.groupby_as_dict('mount')

This produces:

.. code-block:: ansible-output

    TASK [Output mount facts grouped by device name] ******************************************
    ok: [localhost] => {
        "ansible_facts.mounts | community.general.groupby_as_dict('device')": {
            "/dev/sda1": {
                "block_available": 2000,
                "block_size": 4096,
                "block_total": 2345,
                "block_used": 345,
                "device": "/dev/sda1",
                "fstype": "ext4",
                "inode_available": 500,
                "inode_total": 512,
                "inode_used": 12,
                "mount": "/boot",
                "options": "rw,relatime,data=ordered",
                "size_available": 56821,
                "size_total": 543210,
                "uuid": "ab31cade-d9c1-484d-8482-8a4cbee5241a"
            },
            "/dev/sda2": {
                "block_available": 1234,
                "block_size": 4096,
                "block_total": 12345,
                "block_used": 11111,
                "device": "/dev/sda2",
                "fstype": "ext4",
                "inode_available": 1111,
                "inode_total": 1234,
                "inode_used": 123,
                "mount": "/",
                "options": "rw,relatime",
                "size_available": 42143,
                "size_total": 543210,
                "uuid": "abcdef01-2345-6789-0abc-def012345678"
            }
        }
    }

    TASK [Output mount facts grouped by mount point] ******************************************
    ok: [localhost] => {
        "ansible_facts.mounts | community.general.groupby_as_dict('mount')": {
            "/": {
                "block_available": 1234,
                "block_size": 4096,
                "block_total": 12345,
                "block_used": 11111,
                "device": "/dev/sda2",
                "fstype": "ext4",
                "inode_available": 1111,
                "inode_total": 1234,
                "inode_used": 123,
                "mount": "/",
                "options": "rw,relatime",
                "size_available": 42143,
                "size_total": 543210,
                "uuid": "bdf50b7d-4859-40af-8665-c637ee7a7808"
            },
            "/boot": {
                "block_available": 2000,
                "block_size": 4096,
                "block_total": 2345,
                "block_used": 345,
                "device": "/dev/sda1",
                "fstype": "ext4",
                "inode_available": 500,
                "inode_total": 512,
                "inode_used": 12,
                "mount": "/boot",
                "options": "rw,relatime,data=ordered",
                "size_available": 56821,
                "size_total": 543210,
                "uuid": "ab31cade-d9c1-484d-8482-8a4cbee5241a"
            }
        }
    }

.. versionadded: 3.0.0

Merging lists of dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have two or more lists of dictionaries and want to combine them into a list of merged dictionaries, where the dictionaries are merged by an attribute, you can use the ``lists_mergeby`` filter.

.. note:: The output of the examples in this section use the YAML callback plugin. Quoting: "Ansible output that can be quite a bit easier to read than the default JSON formatting." See :ref:`the documentation for the community.general.yaml callback plugin <ansible_collections.community.general.yaml_callback>`.

In the example below the lists are merged by the attribute ``name``:

.. code-block:: yaml+jinja

  ---
  - name: Merge two lists by common attribute 'name'
    set_fact:
      list3: "{{ list1|
                 community.general.lists_mergeby(list2, 'name') }}"
    vars:
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
  - debug:
      var: list3

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

  ---
  - name: Merge two lists by common attribute 'name'
    set_fact:
      list3: "{{ [list1, list2]|
                 community.general.lists_mergeby('name') }}"
    vars:
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
  - debug:
      var: list3

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

Example ``list_merge=replace`` (default):

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

Example ``list_merge=keep``:

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

Example ``list_merge=append``:

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

Example ``list_merge=prepend``:

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

Example ``list_merge=append_rp``:

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

Example ``list_merge=prepend_rp``:

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


Counting elements in a sequence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``community.general.counter`` filter plugin allows you to count (hashable) elements in a sequence. Elements are returned as dictionary keys and their counts are stored as dictionary values.

.. code-block:: yaml+jinja

    - name: Count character occurrences in a string
      debug:
        msg: "{{ 'abccbaabca' | community.general.counter }}"

    - name: Count items in a list
      debug:
        msg: "{{ ['car', 'car', 'bike', 'plane', 'bike'] | community.general.counter }}"

This produces:

.. code-block:: ansible-output

    TASK [Count character occurrences in a string] ********************************************
    ok: [localhost] => {
        "msg": {
            "a": 4,
            "b": 3,
            "c": 3
        }
    }

    TASK [Count items in a list] **************************************************************
    ok: [localhost] => {
        "msg": {
            "bike": 2,
            "car": 2,
            "plane": 1
        }
    }

This plugin is useful for selecting resources based on current allocation:

.. code-block:: yaml+jinja

    - name: Get ID of SCSI controller(s) with less than 4 disks attached and choose the one with the least disks
      debug:
        msg: >-
          {{
             ( disks | dict2items | map(attribute='value.adapter') | list
               | community.general.counter | dict2items
               | rejectattr('value', '>=', 4) | sort(attribute='value') | first
             ).key
          }}
      vars:
        disks:
          sda:
            adapter: scsi_1
          sdb:
            adapter: scsi_1
          sdc:
            adapter: scsi_1
          sdd:
            adapter: scsi_1
          sde:
            adapter: scsi_2
          sdf:
            adapter: scsi_3
          sdg:
            adapter: scsi_3

This produces:

.. code-block:: ansible-output

    TASK [Get ID of SCSI controller(s) with less than 4 disks attached and choose the one with the least disks]
    ok: [localhost] => {
        "msg": "scsi_2"
    }

.. versionadded:: 4.3.0
