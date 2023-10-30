..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Counting elements in a sequence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :ansplugin:`community.general.counter filter plugin <community.general.counter#filter>` allows you to count (hashable) elements in a sequence. Elements are returned as dictionary keys and their counts are stored as dictionary values.

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
