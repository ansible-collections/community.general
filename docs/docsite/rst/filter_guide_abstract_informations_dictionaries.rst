..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

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
