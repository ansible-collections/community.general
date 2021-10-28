.. _ansible_collections.community.general.docsite.test_guide:

community.general Test (Plugin) Guide
=====================================

The :ref:`community.general collection <plugins_in_community.general>` offers currently one test plugin.

.. contents:: Topics

Feature Tests
-------------

The ``an_action`` test allows to check whether a given string refers to an existing module or action plugin. This can be useful in roles, which can use this to ensure that required modules are present ahead of time.

.. code-block:: yaml+jinja

    - name: Make sure that community.aws.route53 is available
      assert:
        that:
          - >
            'community.aws.route53' is community.general.an_action

.. versionadded:: 4.0.0
