..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Conversions
-----------

Parsing CSV files
^^^^^^^^^^^^^^^^^

Ansible offers the :ansplugin:`community.general.read_csv module <community.general.read_csv#module>` to read CSV files. Sometimes you need to convert strings to CSV files instead. For this, the :ansplugin:`community.general.from_csv filter <community.general.from_csv#filter>` exists.

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

The :ansplugin:`community.general.from_csv filter <community.general.from_csv#filter>` has several keyword arguments to control its behavior:

:dialect: Dialect of the CSV file. Default is ``excel``. Other possible choices are ``excel-tab`` and ``unix``. If one of ``delimiter``, ``skipinitialspace`` or ``strict`` is specified, ``dialect`` is ignored.
:fieldnames: A set of column names to use. If not provided, the first line of the CSV is assumed to contain the column names.
:delimiter: Sets the delimiter to use. Default depends on the dialect used.
:skipinitialspace: Set to ``true`` to ignore space directly after the delimiter. Default depends on the dialect used (usually ``false``).
:strict: Set to ``true`` to error out on invalid CSV input.

.. versionadded: 3.0.0

Converting to JSON
^^^^^^^^^^^^^^^^^^

`JC <https://pypi.org/project/jc/>`_ is a CLI tool and Python library which allows to interpret output of various CLI programs as JSON. It is also available as a filter in community.general, called :ansplugin:`community.general.jc#filter`. This filter needs the `jc Python library <https://pypi.org/project/jc/>`_ installed on the controller.

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
