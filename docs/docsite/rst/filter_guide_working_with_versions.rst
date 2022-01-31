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
