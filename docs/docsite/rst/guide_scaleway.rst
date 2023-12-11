..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_scaleway:

**************
Scaleway Guide
**************

Introduction
============

`Scaleway <https://scaleway.com>`_ is a cloud provider supported by the community.general collection through a set of plugins and modules.
Those modules are:

- :ansplugin:`community.general.scaleway_compute#module`: manages servers on Scaleway. You can use this module to create, restart and delete servers.
- :ansplugin:`community.general.scaleway_compute_private_network#module`
- :ansplugin:`community.general.scaleway_container#module`
- :ansplugin:`community.general.scaleway_container_info#module`
- :ansplugin:`community.general.scaleway_container_namespace_info#module`
- :ansplugin:`community.general.scaleway_container_namespace#module`
- :ansplugin:`community.general.scaleway_container_registry_info#module`
- :ansplugin:`community.general.scaleway_container_registry#module`
- :ansplugin:`community.general.scaleway_database_backup#module`
- :ansplugin:`community.general.scaleway_function#module`
- :ansplugin:`community.general.scaleway_function_info#module`
- :ansplugin:`community.general.scaleway_function_namespace_info#module`
- :ansplugin:`community.general.scaleway_function_namespace#module`
- :ansplugin:`community.general.scaleway_image_info#module`
- :ansplugin:`community.general.scaleway_ip#module`
- :ansplugin:`community.general.scaleway_ip_info#module`
- :ansplugin:`community.general.scaleway_lb#module`
- :ansplugin:`community.general.scaleway_organization_info#module`
- :ansplugin:`community.general.scaleway_private_network#module`
- :ansplugin:`community.general.scaleway_security_group#module`
- :ansplugin:`community.general.scaleway_security_group_info#module`
- :ansplugin:`community.general.scaleway_security_group_rule#module`
- :ansplugin:`community.general.scaleway_server_info#module`
- :ansplugin:`community.general.scaleway_snapshot_info#module`
- :ansplugin:`community.general.scaleway_sshkey#module`: adds a public SSH key from a file or value to the Packet infrastructure. Every subsequently-created device will have this public key installed in .ssh/authorized_keys.
- :ansplugin:`community.general.scaleway_user_data#module`
- :ansplugin:`community.general.scaleway_volume#module`: manages volumes on Scaleway.
- :ansplugin:`community.general.scaleway_volume_info#module`

The plugins are:

- :ansplugin:`community.general.scaleway#inventory`: inventory plugin


.. note::
   This guide assumes you are familiar with Ansible and how it works.
   If you are not, have a look at :ref:`ansible_documentation` before getting started.

Requirements
============

The Scaleway modules and inventory script connect to the Scaleway API using `Scaleway REST API <https://developer.scaleway.com>`_.
To use the modules and inventory script you will need a Scaleway API token.
You can generate an API token through the `Scaleway console's credential page <https://cloud.scaleway.com/#/credentials>`__.
The simplest way to authenticate yourself is to set the Scaleway API token in an environment variable:

.. code-block:: console

    $ export SCW_TOKEN=00000000-1111-2222-3333-444444444444

If you are not comfortable exporting your API token, you can pass it as a parameter to the modules using the ``api_token`` argument.

If you want to use a new SSH key pair in this tutorial, you can generate it to ``./id_rsa`` and ``./id_rsa.pub`` as:

.. code-block:: console

    $ ssh-keygen -t rsa -f ./id_rsa

If you want to use an existing key pair, just copy the private and public key over to the playbook directory.

How to add an SSH key?
======================

Connection to Scaleway Compute nodes use Secure Shell.
SSH keys are stored at the account level, which means that you can reuse the same SSH key in multiple nodes.
The first step to configure Scaleway compute resources is to have at least one SSH key configured.

:ansplugin:`community.general.scaleway_sshkey#module` is a module that manages SSH keys on your Scaleway account.
You can add an SSH key to your account by including the following task in a playbook:

.. code-block:: yaml+jinja

    - name: "Add SSH key"
      community.general.scaleway_sshkey:
        ssh_pub_key: "ssh-rsa AAAA..."
        state: "present"

The ``ssh_pub_key`` parameter contains your ssh public key as a string. Here is an example inside a playbook:


.. code-block:: yaml+jinja

    - name: Test SSH key lifecycle on a Scaleway account
      hosts: localhost
      gather_facts: false
      environment:
        SCW_API_KEY: ""

      tasks:

        - community.general.scaleway_sshkey:
            ssh_pub_key: "ssh-rsa AAAAB...424242 developer@example.com"
            state: present
          register: result

        - ansible.builtin.assert:
            that:
              - result is success and result is changed

How to create a compute instance?
=================================

Now that we have an SSH key configured, the next step is to spin up a server!
:ansplugin:`community.general.scaleway_compute#module` is a module that can create, update and delete Scaleway compute instances:

.. code-block:: yaml+jinja

    - name: Create a server
      community.general.scaleway_compute:
        name: foobar
        state: present
        image: 00000000-1111-2222-3333-444444444444
        organization: 00000000-1111-2222-3333-444444444444
        region: ams1
        commercial_type: START1-S

Here are the parameter details for the example shown above:

- ``name`` is the name of the instance (the one that will show up in your web console).
- ``image`` is the UUID of the system image you would like to use.
  A list of all images is available for each availability zone.
- ``organization`` represents the organization that your account is attached to.
- ``region`` represents the Availability Zone which your instance is in (for this example, ``par1`` and ``ams1``).
- ``commercial_type`` represents the name of the commercial offers.
  You can check out the Scaleway pricing page to find which instance is right for you.

Take a look at this short playbook to see a working example using ``scaleway_compute``:

.. code-block:: yaml+jinja

    - name: Test compute instance lifecycle on a Scaleway account
      hosts: localhost
      gather_facts: false
      environment:
        SCW_API_KEY: ""

      tasks:

        - name: Create a server
          register: server_creation_task
          community.general.scaleway_compute:
            name: foobar
            state: present
            image: 00000000-1111-2222-3333-444444444444
            organization: 00000000-1111-2222-3333-444444444444
            region: ams1
            commercial_type: START1-S
            wait: true

        - ansible.builtin.debug:
            var: server_creation_task

        - ansible.builtin.assert:
            that:
              - server_creation_task is success
              - server_creation_task is changed

        - name: Run it
          community.general.scaleway_compute:
            name: foobar
            state: running
            image: 00000000-1111-2222-3333-444444444444
            organization: 00000000-1111-2222-3333-444444444444
            region: ams1
            commercial_type: START1-S
            wait: true
            tags:
              - web_server
          register: server_run_task

        - ansible.builtin.debug:
            var: server_run_task

        - ansible.builtin.assert:
            that:
              - server_run_task is success
              - server_run_task is changed

Dynamic Inventory Plugin
========================

Ansible ships with :ansplugin:`community.general.scaleway#inventory`.
You can now get a complete inventory of your Scaleway resources through this plugin and filter it on
different parameters (``regions`` and ``tags`` are currently supported).

Let us create an example!
Suppose that we want to get all hosts that got the tag web_server.
Create a file named ``scaleway_inventory.yml`` with the following content:

.. code-block:: yaml+jinja

    plugin: community.general.scaleway
    regions:
      - ams1
      - par1
    tags:
      - web_server

This inventory means that we want all hosts that got the tag ``web_server`` on the zones ``ams1`` and ``par1``.
Once you have configured this file, you can get the information using the following command:

.. code-block:: console

    $ ansible-inventory --list -i scaleway_inventory.yml

The output will be:

.. code-block:: json

    {
        "_meta": {
            "hostvars": {
                "dd8e3ae9-0c7c-459e-bc7b-aba8bfa1bb8d": {
                    "ansible_verbosity": 6,
                    "arch": "x86_64",
                    "commercial_type": "START1-S",
                    "hostname": "foobar",
                    "ipv4": "192.0.2.1",
                    "organization": "00000000-1111-2222-3333-444444444444",
                    "state": "running",
                    "tags": [
                        "web_server"
                    ]
                }
            }
        },
        "all": {
            "children": [
                "ams1",
                "par1",
                "ungrouped",
                "web_server"
            ]
        },
        "ams1": {},
        "par1": {
            "hosts": [
                "dd8e3ae9-0c7c-459e-bc7b-aba8bfa1bb8d"
            ]
        },
        "ungrouped": {},
        "web_server": {
            "hosts": [
                "dd8e3ae9-0c7c-459e-bc7b-aba8bfa1bb8d"
            ]
        }
    }

As you can see, we get different groups of hosts.
``par1`` and ``ams1`` are groups based on location.
``web_server`` is a group based on a tag.

In case a filter parameter is not defined, the plugin supposes all values possible are wanted.
This means that for each tag that exists on your Scaleway compute nodes, a group based on each tag will be created.

Scaleway S3 object storage
==========================

`Object Storage <https://www.scaleway.com/object-storage>`_ allows you to store any kind of objects (documents, images, videos, and so on).
As the Scaleway API is S3 compatible, Ansible supports it natively through the amazon.aws modules: :ansplugin:`amazon.aws.s3_bucket#module`, :ansplugin:`amazon.aws.s3_object#module`.

You can find many examples in the `scaleway_s3 integration tests <https://github.com/ansible/ansible-legacy-tests/tree/devel/test/legacy/roles/scaleway_s3>`_.

.. code-block:: yaml+jinja

    - hosts: myserver
      vars:
        scaleway_region: nl-ams
        s3_url: https://s3.nl-ams.scw.cloud
      environment:
        # AWS_ACCESS_KEY matches your scaleway organization id available at https://cloud.scaleway.com/#/account
        AWS_ACCESS_KEY: 00000000-1111-2222-3333-444444444444
        # AWS_SECRET_KEY matches a secret token that you can retrieve at https://cloud.scaleway.com/#/credentials
        AWS_SECRET_KEY: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
      module_defaults:
        group/amazon.aws.aws:
          s3_url: '{{ s3_url }}'
          region: '{{ scaleway_region }}'
      tasks:
       # use a fact instead of a variable, otherwise template is evaluate each time variable is used
        - ansible.builtin.set_fact:
            bucket_name: "{{ 99999999 | random | to_uuid }}"

        # "requester_pays:" is mandatory because Scaleway does not implement related API
        # another way is to use amazon.aws.s3_object and "mode: create" !
        - amazon.aws.s3_bucket:
            name: '{{ bucket_name }}'
            requester_pays:

        - name: Another way to create the bucket
          amazon.aws.s3_object:
            bucket: '{{ bucket_name }}'
            mode: create
            encrypt: false
          register: bucket_creation_check

        - name: add something in the bucket
          amazon.aws.s3_object:
            mode: put
            bucket: '{{ bucket_name }}'
            src: /tmp/test.txt  #  needs to be created before
            object: test.txt
            encrypt: false  # server side encryption must be disabled
