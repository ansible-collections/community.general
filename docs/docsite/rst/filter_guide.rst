.. _ansible_collections.community.general.docsite.filter_guide:

Community.General Filter Guide
==============================

The :ref:`community.general collection <plugins_in_community.general>` offers several useful filter plugins.

Paths
-----

The ``path_join`` filter has been added in ansible-base 2.10. If you want to use this filter, but also need to support Ansible 2.9, you can use ``community.general``'s ``path_join`` shim, ``community.general.path_join``. This filter redirects to ``path_join`` for ansible-base 2.10 and ansible-core 2.11 or newer, and re-implements the filter for Ansible 2.9.

.. code-block:: yaml+jinja

    # ansible-base 2.10 or newer:
    path: {{ ('/etc', path, 'subdir', file) | path_join }}

    # Also works with Ansible 2.9:
    path: {{ ('/etc', path, 'subdir', file) | community.general.path_join }}

.. versionadded:: 3.0.0

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

If you have two lists of dictionaries and want to combine them into a list of merged dictionaries, where two dictionaries are merged if they coincide in one attribute, you can use the ``lists_mergeby`` filter.

.. code-block:: yaml+jinja

    - name: Merge two lists by common attribute 'name'
      debug:
        var: list1 | community.general.lists_mergeby(list2, 'name')
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
            path: /bazzz

This produces:

.. code-block:: ansible-output

    TASK [Merge two lists by common attribute 'name']  ****************************************
    ok: [localhost] => {
        "list1 | community.general.lists_mergeby(list2, 'name')": [
            {
                "extra": false,
                "name": "bar"
            },
            {
                "name": "baz",
                "path": "/bazzz"
            },
            {
                "extra": true,
                "name": "foo",
                "path": "/foo"
            },
            {
                "extra": true,
                "name": "meh"
            }
        ]
    }

.. versionadded: 2.0.0
