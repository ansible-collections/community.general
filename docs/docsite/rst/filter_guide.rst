.. _ansible_collections.community.general.docsite.filter_guide:

community.general Filter Guide
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

You can also initialize the random number generator from a seed to create random-but-idempotent MAC addresses:

.. code-block:: yaml+jinja

    "{{ '52:54:00' | community.general.random_mac(seed=inventory_hostname) }}"

Conversions
-----------

Parsing CSV files
^^^^^^^^^^^^^^^^^

Ansible offers the :ref:`community.general.read_csv module <ansible_collections.community.general.read_csv_module>` to read CSV files. Sometimes you need to convert strings to CSV files instead. For this, the ``from_csv`` filter exists.

.. code-block:: yaml+jinja

    - name: "Parse CSV from string"
      debug:
        msg: "{{ csv_string | community.general.from_csv }}"
      vars:
        csv_string: |
          foo,bar,baz
          1,2,3
          you,this,then

This produces:

.. code-block:: ansible-output

    TASK [Parse CSV from string] **************************************************************
    ok: [localhost] => {
        "msg": [
            {
                "bar": "2",
                "baz": "3",
                "foo": "1"
            },
            {
                "bar": "this",
                "baz": "then",
                "foo": "you"
            }
        ]
    }

The ``from_csv`` filter has several keyword arguments to control its behavior:

:dialect: Dialect of the CSV file. Default is ``excel``. Other possible choices are ``excel-tab`` and ``unix``. If one of ``delimiter``, ``skipinitialspace`` or ``strict`` is specified, ``dialect`` is ignored.
:fieldnames: A set of column names to use. If not provided, the first line of the CSV is assumed to contain the column names.
:delimiter: Sets the delimiter to use. Default depends on the dialect used.
:skipinitialspace: Set to ``true`` to ignore space directly after the delimiter. Default depends on the dialect used (usually ``false``).
:strict: Set to ``true`` to error out on invalid CSV input.

.. versionadded: 3.0.0

Converting to JSON
^^^^^^^^^^^^^^^^^^

`JC <https://pypi.org/project/jc/>`_ is a CLI tool and Python library which allows to interpret output of various CLI programs as JSON. It is also available as a filter in community.general. This filter needs the `jc Python library <https://pypi.org/project/jc/>`_ installed on the controller.

.. code-block:: yaml+jinja

    - name: Run 'ls' to list files in /
      command: ls /
      register: result

    - name: Parse the ls output
      debug:
        msg: "{{ result.stdout | community.general.jc('ls') }}"

This produces:

.. code-block:: ansible-output

    TASK [Run 'ls' to list files in /] ********************************************************
    changed: [localhost]

    TASK [Parse the ls output] ****************************************************************
    ok: [localhost] => {
        "msg": [
            {
                "filename": "bin"
            },
            {
                "filename": "boot"
            },
            {
                "filename": "dev"
            },
            {
                "filename": "etc"
            },
            {
                "filename": "home"
            },
            {
                "filename": "lib"
            },
            {
                "filename": "proc"
            },
            {
                "filename": "root"
            },
            {
                "filename": "run"
            },
            {
                "filename": "tmp"
            }
        ]
    }

.. versionadded: 2.0.0

.. _ansible_collections.community.general.docsite.json_query_filter:

Selecting JSON data: JSON queries
---------------------------------

To select a single element or a data subset from a complex data structure in JSON format (for example, Ansible facts), use the ``json_query`` filter.  The ``json_query`` filter lets you query a complex JSON structure and iterate over it using a loop structure.

.. note:: You must manually install the **jmespath** dependency on the Ansible controller before using this filter. This filter is built upon **jmespath**, and you can use the same syntax. For examples, see `jmespath examples <http://jmespath.org/examples.html>`_.

Consider this data structure:

.. code-block:: yaml+jinja

    {
        "domain_definition": {
            "domain": {
                "cluster": [
                    {
                        "name": "cluster1"
                    },
                    {
                        "name": "cluster2"
                    }
                ],
                "server": [
                    {
                        "name": "server11",
                        "cluster": "cluster1",
                        "port": "8080"
                    },
                    {
                        "name": "server12",
                        "cluster": "cluster1",
                        "port": "8090"
                    },
                    {
                        "name": "server21",
                        "cluster": "cluster2",
                        "port": "9080"
                    },
                    {
                        "name": "server22",
                        "cluster": "cluster2",
                        "port": "9090"
                    }
                ],
                "library": [
                    {
                        "name": "lib1",
                        "target": "cluster1"
                    },
                    {
                        "name": "lib2",
                        "target": "cluster2"
                    }
                ]
            }
        }
    }

To extract all clusters from this structure, you can use the following query:

.. code-block:: yaml+jinja

    - name: Display all cluster names
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.cluster[*].name') }}"

To extract all server names:

.. code-block:: yaml+jinja

    - name: Display all server names
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.server[*].name') }}"

To extract ports from cluster1:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
      vars:
        server_name_cluster1_query: "domain.server[?cluster=='cluster1'].port"

.. note:: You can use a variable to make the query more readable.

To print out the ports from cluster1 in a comma separated string:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1 as a string
      ansible.builtin.debug:
        msg: "{{ domain_definition | community.general.json_query('domain.server[?cluster==`cluster1`].port') | join(', ') }}"

.. note:: In the example above, quoting literals using backticks avoids escaping quotes and maintains readability.

You can use YAML `single quote escaping <https://yaml.org/spec/current.html#id2534365>`_:

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query('domain.server[?cluster==''cluster1''].port') }}"

.. note:: Escaping single quotes within single quotes in YAML is done by doubling the single quote.

To get a hash map with all ports and names of a cluster:

.. code-block:: yaml+jinja

    - name: Display all server ports and names from cluster1
      ansible.builtin.debug:
        var: item
      loop: "{{ domain_definition | community.general.json_query(server_name_cluster1_query) }}"
      vars:
        server_name_cluster1_query: "domain.server[?cluster=='cluster2'].{name: name, port: port}"

To extract ports from all clusters with name starting with 'server1':

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
      vars:
        server_name_query: "domain.server[?starts_with(name,'server1')].port"

To extract ports from all clusters with name containing 'server1':

.. code-block:: yaml+jinja

    - name: Display all ports from cluster1
      ansible.builtin.debug:
        msg: "{{ domain_definition | to_json | from_json | community.general.json_query(server_name_query) }}"
      vars:
        server_name_query: "domain.server[?contains(name,'server1')].port"

.. note:: while using ``starts_with`` and ``contains``, you have to use `` to_json | from_json `` filter for correct parsing of data structure.

Working with Unicode
---------------------

`Unicode <https://unicode.org/main.html>`_ makes it possible to produce two strings which may be visually equivalent, but are comprised of distinctly different characters/character sequences. To address this ``Unicode`` defines `normalization forms <https://unicode.org/reports/tr15/>`_ which avoid these distinctions by choosing a unique character sequence for a given visual representation.

You can use the ``community.general.unicode_normalize`` filter to normalize ``Unicode`` strings within your playbooks.

.. code-block:: yaml+jinja

    - name: Compare Unicode representations
      debug:
        msg: "{{ with_combining_character | community.general.unicode_normalize == without_combining_character }}"
      vars:
        with_combining_character: "{{ 'Mayagu\u0308ez' }}"
        without_combining_character: Mayagüez

This produces:

.. code-block:: ansible-output

    TASK [Compare Unicode representations] ********************************************************
    ok: [localhost] => {
        "msg": true
    }

The ``community.general.unicode_normalize`` filter accepts a keyword argument to select the ``Unicode`` form used to normalize the input string.

:form: One of ``'NFC'`` (default), ``'NFD'``, ``'NFKC'``, or ``'NFKD'``. See the `Unicode reference <https://unicode.org/reports/tr15/>`_ for more information.

.. versionadded:: 3.7.0
