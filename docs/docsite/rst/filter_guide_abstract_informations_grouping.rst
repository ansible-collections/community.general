..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Grouping
^^^^^^^^

If you have a list of dictionaries, the Jinja2 ``groupby`` filter allows to group the list by an attribute. This results in a list of ``(grouper, list)`` namedtuples, where ``list`` contains all dictionaries where the selected attribute equals ``grouper``. If you know that for every ``grouper``, there will be a most one entry in that list, you can use the :ansplugin:`community.general.groupby_as_dict filter <community.general.groupby_as_dict#filter>` to convert the original list into a dictionary which maps ``grouper`` to the corresponding dictionary.

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
