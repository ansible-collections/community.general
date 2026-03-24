..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_ee:

Execution Environment Guide
===========================

`Ansible Execution Environments <https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html>`_
(EEs) are container images that bundle ansible-core, collections, and their Python and system dependencies.
They are the standard runtime for Red Hat Ansible Automation Platform and AWX, replacing the older virtualenv model.

What runs in the EE
^^^^^^^^^^^^^^^^^^^

Only **controller-side plugins** run inside the EE. Their Python and system dependencies must be installed there.
This includes: lookup plugins, inventory plugins, callback plugins, connection plugins, become plugins, and filter plugins.

Modules run on the managed nodes and are transferred there at runtime — their dependencies must be present on the
target, not in the EE.

.. note::

    Modules delegated to ``localhost`` (for example, those that interact with a remote API) are an exception:
    they run on the controller and their dependencies must therefore be available in the EE.

Why community.general does not ship an EE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``community.general`` ships dozens of controller-side plugins covering a very broad range of technologies.
Bundling the dependencies for all of them into a single EE image would almost certainly create irreconcilable
conflicts — both within the collection and with other collections or tools (such as ``ansible-lint``) that
share the same image.

For that reason, ``community.general`` does **not** provide a ``requirements.txt`` or ``bindep.txt`` at the
collection root. Users are expected to build purpose-built, minimal EEs containing only the dependencies
required by the specific plugins they actually use.

Finding the dependencies you need
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every plugin that has external dependencies documents them in its ``requirements`` field.
You can inspect those with ``ansible-doc``:

.. code-block:: shell

    $ ansible-doc -t lookup community.general.some_lookup | grep -A 10 "REQUIREMENTS"

Or browse the plugin's documentation page on `docs.ansible.com <https://docs.ansible.com/ansible/latest/collections/community/general/>`_.

For example, a lookup plugin that wraps an external service might list:

.. code-block:: yaml

    requirements:
      - some-python-library >= 1.2

An inventory plugin backed by a REST API might list:

.. code-block:: yaml

    requirements:
      - requests
      - some-sdk

These are the packages you need to add to your EE.

For a more complete picture, you can also read the plugin's source code directly and look at its
top-level `import` statements. The ``requirements`` field documents the intended public dependencies, but inspecting
the imports reveals the exact Python packages that are actually used.

Building a minimal EE with ansible-builder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`ansible-builder <https://ansible-builder.readthedocs.io/>`_ is the standard tool for creating EEs.

Install it with:

.. code-block:: shell

    $ pip install ansible-builder

Create an ``execution-environment.yml`` **in your own project** — not inside ``community.general`` —
that includes only the dependencies needed for the plugins you use:

.. code-block:: yaml

    version: 3

    dependencies:
      galaxy:
        collections:
          - name: community.general
      python:
        - some-python-library>=1.2
        - requests
      system:
        - libxml2-devel [platform:rpm]
        - libxml2-dev [platform:deb]

    images:
      base_image:
        name: ghcr.io/ansible/community-ee-base:latest

Then build the image:

.. code-block:: shell

    $ ansible-builder build -t my-custom-ee:latest

.. seealso::

    - `ansible-builder documentation <https://ansible-builder.readthedocs.io/>`_
    - `Ansible Execution Environments overview <https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html>`_
    - `Building EEs with ansible-builder <https://ansible-builder.readthedocs.io/en/latest/definition/>`_
    - `Issue #2968 — original request for EE requirements support <https://github.com/ansible-collections/community.general/issues/2968>`_
    - `Issue #4512 — design discussion for EE support in community.general <https://github.com/ansible-collections/community.general/issues/4512>`_
