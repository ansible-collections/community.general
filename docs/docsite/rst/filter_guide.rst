.. _ansible_collections.community.general.docsite.filter_guide:

Community.General Filter Guide
==============================

The :ref:`community.general collection <plugins_in_community.general>` offers several useful filter plugins.

.. contents:: Topics

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

Working with times
------------------

The ``to_time_unit`` filter allows to convert times from a human-readable string to a unit. For example, ``'4h 30min 12second' | community.general.to_time_unit('hour')`` gives the number of hours that correspond to 4 hours, 30 minutes and 12 seconds.

There are shorthands to directly convert to various units, like ``to_hours``, ``to_minutes``, ``to_seconds``, and so on. The following table lists all units that can be used:

.. list-table:: Units
   :widths: 25 25 25 25
   :header-rows: 1

   * - Unit name
     - Unit value in seconds
     - Unit strings for filter
     - Shorthand filter
   * - Millisecond
     - 1/1000 second
     - ``ms``, ``millisecond``, ``milliseconds``, ``msec``, ``msecs``, ``msecond``, ``mseconds``
     - ``to_milliseconds``
   * - Second
     - 1 second
     - ``s``, ``sec``, ``secs``, ``second``, ``seconds``
     - ``to_seconds``
   * - Minute
     - 60 seconds
     - ``m``, ``min``, ``mins``, ``minute``, ``minutes``
     - ``to_minutes``
   * - Hour
     - 60*60 seconds
     - ``h``, ``hour``, ``hours``
     - ``to_hours``
   * - Day
     - 24*60*60 seconds
     - ``d``, ``day``, ``days``
     - ``to_days``
   * - Week
     - 7*24*60*60 seconds
     - ``w``, ``week``, ``weeks``
     - ``to_weeks``
   * - Month
     - 30*24*60*60 seconds
     - ``mo``, ``month``, ``months``
     - ``to_months``
   * - Year
     - 365*24*60*60 seconds
     - ``y``, ``year``, ``years``
     - ``to_years``

Note that months and years are using a simplified representation: a month is 30 days, and a year is 365 days. If you need different definitions of months or years, you can pass them as keyword arguments. For example, if you want a year to be 365.25 days, and a month to be 30.5 days, you can write ``'11months 4' | community.general.to_years(year=365.25, month=30.5)``. These keyword arguments can be specified to ``to_time_unit`` and to all shorthand filters.

.. code-block:: yaml+jinja

    - name: Convert string to seconds
      debug:
        msg: "{{ '30h 20m 10s 123ms' | community.general.to_time_unit('seconds') }}"

    - name: Convert string to hours
      debug:
        msg: "{{ '30h 20m 10s 123ms' | community.general.to_hours }}"

    - name: Convert string to years (using 365.25 days == 1 year)
      debug:
        msg: "{{ '400d 15h' | community.general.to_years(year=365.25) }}"

This produces:

.. code-block:: ansible-output

    TASK [Convert string to seconds] **********************************************************
    ok: [localhost] => {
        "msg": "109210.123"
    }

    TASK [Convert string to hours] ************************************************************
    ok: [localhost] => {
        "msg": "30.336145277778"
    }

    TASK [Convert string to years (using 365.25 days == 1 year)] ******************************
    ok: [localhost] => {
        "msg": "1.096851471595"
    }

.. versionadded: 0.2.0

Working with versions
---------------------

If you need to sort a list of version numbers, the Jinja ``sort`` filter is problematic. Since it sorts lexicographically, ``2.10`` will come before ``2.9``. To treat version numbers correctly, you can use the ``version_sort`` filter:

.. code-block:: yaml+jinja

    - name: Sort list by version number
      debug:
        var: ansible_versions | community.general.version_sort
      vars:
        ansible_versions:
          - '2.8.0'
          - '2.11.0'
          - '2.7.0'
          - '2.10.0'
          - '2.9.0'

This produces:

.. code-block:: ansible-output

    TASK [Sort list by version number] ********************************************************
    ok: [localhost] => {
        "ansible_versions | community.general.version_sort": [
            "2.7.0",
            "2.8.0",
            "2.9.0",
            "2.10.0",
            "2.11.0"
        ]
    }

.. versionadded: 2.2.0

Creating identifiers
--------------------

The following filters allow to create identifiers.

Hashids
^^^^^^^

`Hashids <https://hashids.org/>`_ allow to convert sequences of integers to short unique string identifiers. This filter needs the `hashids Python library <https://pypi.org/project/hashids/>`_ installed on the controller.

.. code-block:: yaml+jinja

    - name: "Create hashid"
      debug:
        msg: "{{ [1234, 5, 6] | community.general.hashids_encode }}"

    - name: "Decode hashid"
      debug:
        msg: "{{ 'jm2Cytn' | community.general.hashids_decode }}"

This produces:

.. code-block:: ansible-output

    TASK [Create hashid] **********************************************************************
    ok: [localhost] => {
        "msg": "jm2Cytn"
    }

    TASK [Decode hashid] **********************************************************************
    ok: [localhost] => {
        "msg": [
            1234,
            5,
            6
        ]
    }

The hashids filters accept keyword arguments to allow fine-tuning the hashids generated:

:salt: String to use as salt when hashing.
:alphabet: String of 16 or more unique characters to produce a hash.
:min_length: Minimum length of hash produced.

.. versionadded: 3.0.0

Random MACs
^^^^^^^^^^^

You can use the ``random_mac`` filter to complete a partial `MAC address <https://en.wikipedia.org/wiki/MAC_address>`_ to a random 6-byte MAC address.

.. code-block:: yaml+jinja

    - name: "Create a random MAC starting with ff:"
      debug:
        msg: "{{ 'FF' | community.general.random_mac }}"

    - name: "Create a random MAC starting with 00:11:22:"
      debug:
        msg: "{{ '00:11:22' | community.general.random_mac }}"
  
This produces:

.. code-block:: ansible-output

    TASK [Create a random MAC starting with ff:] **********************************************
    ok: [localhost] => {
        "msg": "ff:69:d3:78:7f:b4"
    }

    TASK [Create a random MAC starting with 00:11:22:] ****************************************
    ok: [localhost] => {
        "msg": "00:11:22:71:5d:3b"
    }
