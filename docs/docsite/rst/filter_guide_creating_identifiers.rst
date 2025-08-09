..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Creating identifiers
--------------------

The following filters allow to create identifiers.

Hashids
^^^^^^^

`Hashids <https://hashids.org/>`_ allow to convert sequences of integers to short unique string identifiers. The :ansplugin:`community.general.hashids_encode#filter` and :ansplugin:`community.general.hashids_decode#filter` filters need the `hashids Python library <https://pypi.org/project/hashids/>`_ installed on the controller.

.. code-block:: yaml+jinja

    - name: "Create hashid"
      debug:
        msg: "{{ [1234, 5, 6] | community.general.hashids_encode }}"

    - name: "Decode hashid"
      debug:
        msg: "{{ 'jm2Cytn' | community.general.hashids_decode }}"

This produces:

.. ansible-output-data::

    variables:
      task:
        previous_code_block: yaml+jinja
    playbook: |-
      - hosts: localhost
        gather_facts: false
        tasks:
          @{{ task | indent(4) }}@

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

You can use the :ansplugin:`community.general.random_mac filter <community.general.random_mac#filter>` to complete a partial `MAC address <https://en.wikipedia.org/wiki/MAC_address>`_ to a random 6-byte MAC address.

.. code-block:: yaml+jinja

    - name: "Create a random MAC starting with ff:"
      debug:
        msg: "{{ 'FF' | community.general.random_mac }}"

    - name: "Create a random MAC starting with 00:11:22:"
      debug:
        msg: "{{ '00:11:22' | community.general.random_mac }}"

This produces:

.. ansible-output-data::

    playbook: |-
      - hosts: localhost
        gather_facts: false
        tasks:
          - name: "Create a random MAC starting with ff:"
            debug:
              # We're using a seed here to avoid randomness in the output
              msg: "{{ 'FF' | community.general.random_mac(seed='') }}"

          - name: "Create a random MAC starting with 00:11:22:"
            debug:
              # We're using a seed here to avoid randomness in the output
              msg: "{{ '00:11:22' | community.general.random_mac(seed='') }}"

.. code-block:: ansible-output

    TASK [Create a random MAC starting with ff:] **********************************************
    ok: [localhost] => {
        "msg": "ff:84:f5:d1:59:20"
    }

    TASK [Create a random MAC starting with 00:11:22:] ****************************************
    ok: [localhost] => {
        "msg": "00:11:22:84:f5:d1"
    }

You can also initialize the random number generator from a seed to create random-but-idempotent MAC addresses:

.. code-block:: yaml+jinja

    "{{ '52:54:00' | community.general.random_mac(seed=inventory_hostname) }}"
