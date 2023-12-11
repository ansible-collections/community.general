..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_alicloud:

Alibaba Cloud Compute Services Guide
====================================

Introduction
````````````

The community.general collection contains several modules for controlling and managing Alibaba Cloud Compute Services (Alicloud).  This guide
explains how to use the Alicloud Ansible modules together.

All Alicloud modules require ``footmark`` - install it on your control machine with ``pip install footmark``.

Cloud modules, including Alicloud modules, are usually executed on your local machine (the control machine) with ``connection: local``, rather than on remote machines defined in your hosts.

Normally, you'll use the following pattern for plays that provision Alicloud resources:

.. code-block:: yaml

    - hosts: localhost
      connection: local
      vars:
        - ...
      tasks:
        - ...

Authentication
``````````````

You can specify your Alicloud authentication credentials (access key and secret key) by passing them as
environment variables or by storing them in a vars file.

To pass authentication credentials as environment variables:

.. code-block:: console

    export ALICLOUD_ACCESS_KEY='Alicloud123'
    export ALICLOUD_SECRET_KEY='AlicloudSecret123'

To store authentication credentials in a vars file, encrypt them with :ref:`Ansible Vault <vault>` to keep them secure, then list them:

.. code-block:: yaml

    ---
    alicloud_access_key: "--REMOVED--"
    alicloud_secret_key: "--REMOVED--"

Note that if you store your credentials in a vars file, you need to refer to them in each Alicloud module. For example:

.. code-block:: yaml+jinja

    - community.general.ali_instance:
        alicloud_access_key: "{{ alicloud_access_key }}"
        alicloud_secret_key: "{{ alicloud_secret_key }}"
        image_id: "..."

Provisioning
````````````

Alicloud modules create Alicloud ECS instances (:ansplugin:`community.general.ali_instance#module`) and retrieve information on these (:ansplugin:`community.general.ali_instance_info#module`).

You can use the ``count`` parameter to control the number of resources you create or terminate. For example, if you want exactly 5 instances tagged ``NewECS``, set the ``count`` of instances to 5 and the ``count_tag`` to ``NewECS``, as shown in the last task of the example playbook below. If there are no instances with the tag ``NewECS``, the task creates 5 new instances. If there are 2 instances with that tag, the task creates 3 more. If there are 8 instances with that tag, the task terminates 3 of those instances.

If you do not specify a ``count_tag``, the task creates the number of instances you specify in ``count`` with the ``instance_name`` you provide.

.. code-block:: yaml+jinja

    # alicloud_setup.yml

    - hosts: localhost
      connection: local

      tasks:
        - name: Create a set of instances
          community.general.ali_instance:
             instance_type: ecs.n4.small
             image_id: "{{ ami_id }}"
             instance_name: "My-new-instance"
             instance_tags:
                 Name: NewECS
                 Version: 0.0.1
             count: 5
             count_tag:
                 Name: NewECS
             allocate_public_ip: true
             max_bandwidth_out: 50
          register: create_instance

In the example playbook above, data about the instances created by this playbook is saved in the variable defined by the ``register`` keyword in the task.

Each Alicloud module offers a variety of parameter options. Not all options are demonstrated in the above example. See each individual module for further details and examples.
