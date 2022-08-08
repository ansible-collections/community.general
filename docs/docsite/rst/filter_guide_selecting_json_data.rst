..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

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
