..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_uthelper:

UTHelper Guide
==============

Introduction
^^^^^^^^^^^^

``UTHelper`` was written to reduce the boilerplate code used in unit tests for modules.
It was originally written to handle tests of modules that run external commands using ``AnsibleModule.run_command()``.
At the time of writing (Feb 2025) that remains the only type of tests you can use
``UTHelper`` for, but it aims to provide support for other types of interactions.

Until now, there are many different ways to implement unit tests that validate a module based on the execution of external commands. See some examples:

* `test_apk.py <https://github.com/ansible-collections/community.general/blob/10.3.0/tests/unit/plugins/modules/test_apk.py>`_ - A very simple one
* `test_bootc_manage.py <https://github.com/ansible-collections/community.general/blob/10.3.0/tests/unit/plugins/modules/test_bootc_manage.py>`_ -
  This one has more test cases, but do notice how the code is repeated amongst them.
* `test_modprobe.py <https://github.com/ansible-collections/community.general/blob/10.3.0/tests/unit/plugins/modules/test_modprobe.py>`_ -
  This one has 15 tests in it, but to achieve that it declares 8 classes repeating quite a lot of code.

As you can notice, there is no consistency in the way these tests are executed -
they all do the same thing eventually, but each one is written in a very distinct way.

``UTHelper`` aims to:

* provide a consistent idiom to define unit tests
* reduce the code to a bare minimal, and
* define tests as data instead
* allow the test cases definition to be expressed not only as a Python data structure but also as YAML content

Quickstart
""""""""""

To use UTHelper, your test module will need only a bare minimal of code:

.. code-block:: python

    # tests/unit/plugin/modules/test_ansible_module.py
    from ansible_collections.community.general.plugins.modules import ansible_module
    from .uthelper import UTHelper, RunCommandMock


    UTHelper.from_module(ansible_module, __name__, mocks=[RunCommandMock])

Then, in the test specification file, you have:

.. code-block:: yaml

    # tests/unit/plugin/modules/test_ansible_module.yaml
    test_cases:
      - id: test_ansible_module
        flags:
          diff: true
        input:
          state: present
          name: Roger the Shrubber
        output:
          shrubbery:
            looks: nice
            price: not too expensive
          changed: true
          diff:
            before:
              shrubbery: null
            after:
              shrubbery:
                looks: nice
                price: not too expensive
        mocks:
          run_command:
            - command: [/testbin/shrubber, --version]
              rc: 0
              out: "2.80.0\n"
              err: ''
            - command: [/testbin/shrubber, --make-shrubbery]
              rc: 0
              out: 'Shrubbery created'
              err: ''

.. note::

    If you prefer to pick a different YAML file for the test cases, or if you prefer to define them in plain Python,
    you can use the convenience methods ``UTHelper.from_file()`` and ``UTHelper.from_spec()``, respectively.
    See more details below.


Using ``UTHelper``
^^^^^^^^^^^^^^^^^^

Test Module
"""""""""""

``UTHelper`` is **strictly for unit tests**. To use it, you import the ``.uthelper.UTHelper`` class.
As mentioned in different parts of this guide, there are three different mechanisms to load the test cases.

.. seealso::

    See the UTHelper class reference below for API details on the three different mechanisms.


The easies and most recommended way of using ``UTHelper`` is literally the example shown.
See a real world example at
`test_gconftool2.py <https://github.com/ansible-collections/community.general/blob/10.3.0/tests/unit/plugins/modules/test_gconftool2.py>`_.

The ``from_module()`` method will pick the filename of the test module up (in the example above, ``tests/unit/plugins/modules/test_gconftool2.py``)
and it will search for ``tests/unit/plugins/modules/test_gconftool2.yaml`` (or ``.yml`` if that is not found).
In that file it will expect to find the test specification expressed in YAML format, conforming to the structure described below LINK LINK LINK.

If you prefer to read the test specifications a different file path, use ``from_file()`` passing the file handle for the YAML file.

And, if for any reason you prefer or need to pass the data structure rather than dealing with YAML files, use the ``from_spec()`` method.
A real world example for that can be found at
`test_snap.py <https://github.com/ansible-collections/community.general/blob/main/tests/unit/plugins/modules/test_snap.py>`_.


Test Specification
""""""""""""""""""

The structure of the test specification data is described below.

Top level
---------

At the top level there are two accepted keys:

- ``anchors: dict``
    Optional. Placeholder for you to define YAML anchors that can be repeated in the test cases.
    Its contents are never accessed directly by test Helper.
- ``test_cases: list``
    Mandatory. List of test cases, see below for definition.

Test cases
----------

You write the test cases with five elements:

- ``id: str``
    Mandatory. Used to identify the test case.

- ``flags: dict``
    Optional. Flags controling the behavior of the test case. All flags are optional. Accepted flags:

    * ``check: bool``: set to ``true`` if the module is to be executed in **check mode**.
    * ``diff: bool``: set to ``true`` if the module is to be executed in **diff mode**.
    * ``skip: str``: set the test case to be skipped, providing the message for ``pytest.skip()``.
    * ``xfail: str``: set the test case to expect failure, providing the message for ``pytest.xfail()``.

- ``input: dict``
    Optional. Parameters for the Ansible module, it can be empty.

- ``output: dict``
    Optional. Expected return values from the Ansible module.
    All RV names are used here are expected to be found in the module output, but not all RVs in the output must be here.
    It can include special RVs such as ``changed`` and ``diff``.
    It can be empty.

- ``mocks: dict``
    Optional. Mocked interactions, ``run_command`` being the only one supported for now.
    Each key in this dictionary refers to one subclass of ``TestCaseMock`` and its
    structure is dictated by the ``TestCaseMock`` subclass implementation.
    All keys are expected to be named using snake case, as in ``run_command``.
    The ``TestCaseMock`` subclass is responsible for defining the name used in the test specification.
    The structure for that specification is dependent on the implementing class.
    See more details below for the implementation of ``RunCommandMock``

Example using YAML
------------------

We recommend you use ``UTHelper`` reading the test specifications from a YAML file.
See an example below of how one actually looks like (excerpt from ``test_opkg.yaml``):

..  code-block:: yaml

  ---
  anchors:
    environ: &env-def {environ_update: {LANGUAGE: C, LC_ALL: C}, check_rc: false}
  test_cases:
    - id: install_zlibdev
      input:
        name: zlib-dev
        state: present
      output:
        msg: installed 1 package(s)
      mocks:
        run_command:
          - command: [/testbin/opkg, --version]
            environ: *env-def
            rc: 0
            out: ''
            err: ''
          - command: [/testbin/opkg, list-installed, zlib-dev]
            environ: *env-def
            rc: 0
            out: ''
            err: ''
          - command: [/testbin/opkg, install, zlib-dev]
            environ: *env-def
            rc: 0
            out: |
              Installing zlib-dev (1.2.11-6) to root...
              Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib-dev_1.2.11-6_mips_24kc.ipk
              Installing zlib (1.2.11-6) to root...
              Downloading https://downloads.openwrt.org/releases/22.03.0/packages/mips_24kc/base/zlib_1.2.11-6_mips_24kc.ipk
              Configuring zlib.
              Configuring zlib-dev.
            err: ''
          - command: [/testbin/opkg, list-installed, zlib-dev]
            environ: *env-def
            rc: 0
            out: |
              zlib-dev - 1.2.11-6
            err: ''
    - id: install_zlibdev_present
      input:
        name: zlib-dev
        state: present
      output:
        msg: package(s) already present
      mocks:
        run_command:
          - command: [/testbin/opkg, --version]
            environ: *env-def
            rc: 0
            out: ''
            err: ''
          - command: [/testbin/opkg, list-installed, zlib-dev]
            environ: *env-def
            rc: 0
            out: |
              zlib-dev - 1.2.11-6
            err: ''

TestCaseMocks Specifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``TestCaseMock`` subclass is free to define the expected data structure.

RunCommandMock Specification
""""""""""""""""""""""""""""

``RunCommandMock`` mocks can be specified with the key ``run_command`` and it expects a ``list`` in which elements follow the structure:

- ``command: Union[list, str]``
    Mandatory. The command that is expected to be executed by the module. It corresponds to the parameter ``args`` of the ``AnsibleModule.run_command()`` call.
    It can be either a list or a string, though the list form is generally recommended.
- ``environ: dict``
    Mandatory. All other parameters passed to the ``AnsibleModule.run_command()`` call.
    Most commonly used are ``environ_update`` and ``check_rc``.
    Must include all parameters the Ansible module uses in the ``AnsibleModule.run_command()`` call, otherwise the test will fail.
- ``rc: int``
    Mandatory. The return code for the command execution.
    As per usual in bash scripting, a value of ``0`` means success, whereas any other number is an error code.
- ``out: str``
    Mandatory. The *stdout* result of the command execution, as one single string containing zero or more lines.
- ``err: str``
    Mandatory. The *stderr* result of the command execution, as one single string containing zero or more lines.


``UTHelper`` Reference
^^^^^^^^^^^^^^^^^^^^^^

.. py:module:: .uthelper

  .. py:class:: UTHelper

    A class to encapsulate unit tests.

    .. py:staticmethod:: from_spec(ansible_module, test_module, test_spec, mocks=None)

      Creates an ``UTHelper`` instance from a given test specification.

      :param ansible_module: The Ansible module to be tested.
      :type ansible_module: :py:class:`types.ModuleType`
      :param test_module: The test module.
      :type test_module: :py:class:`types.ModuleType`
      :param test_spec: The test specification.
      :type test_spec: dict
      :param mocks: List of ``TestCaseMocks`` to be used during testing. Currently only ``RunCommandMock`` exists.
      :type mocks: list or None
      :return: An ``UTHelper`` instance.
      :rtype: UTHelper

      Example usage of ``from_spec()``:

      .. code-block:: python

          import sys

          from ansible_collections.community.general.plugins.modules import ansible_module
          from .uthelper import UTHelper, RunCommandMock

          TEST_SPEC = dict(
              test_cases=[
                  ...
              ]
          )

          helper = UTHelper.from_spec(ansible_module, sys.modules[__name__], TEST_SPEC, mocks=[RunCommandMock])

    .. py:staticmethod:: from_file(ansible_module, test_module, test_spec_filehandle, mocks=None)

      Creates an ``UTHelper`` instance from a test specification file.

      :param ansible_module: The Ansible module to be tested.
      :type ansible_module: :py:class:`types.ModuleType`
      :param test_module: The test module.
      :type test_module: :py:class:`types.ModuleType`
      :param test_spec_filehandle: A file handle to an file stream handle providing the test specification in YAML format.
      :type test_spec_filehandle: ``file-like object``
      :param mocks: List of ``TestCaseMocks`` to be used during testing. Currently only ``RunCommandMock`` exists.
      :type mocks: list or None
      :return: An ``UTHelper`` instance.
      :rtype: UTHelper

      Example usage of ``from_file()``:

      .. code-block:: python

          import sys

          from ansible_collections.community.general.plugins.modules import ansible_module
          from .uthelper import UTHelper, RunCommandMock

          with open("test_spec.yaml", "r") as test_spec_filehandle:
              helper = UTHelper.from_file(ansible_module, sys.modules[__name__], test_spec_filehandle, mocks=[RunCommandMock])

    .. py:staticmethod:: from_module(ansible_module, test_module_name, mocks=None)

      Creates an ``UTHelper`` instance from a given Ansible module and test module.

      :param ansible_module: The Ansible module to be tested.
      :type ansible_module: :py:class:`types.ModuleType`
      :param test_module_name: The name of the test module. It works if passed ``__name__``.
      :type test_module_name: str
      :param mocks: List of ``TestCaseMocks`` to be used during testing. Currently only ``RunCommandMock`` exists.
      :type mocks: list or None
      :return: An ``UTHelper`` instance.
      :rtype: UTHelper

      Example usage of ``from_module()``:

      .. code-block:: python

          from ansible_collections.community.general.plugins.modules import ansible_module
          from .uthelper import UTHelper, RunCommandMock

          # Example usage
          helper = UTHelper.from_module(ansible_module, __name__, mocks=[RunCommandMock])


Creating TestCaseMocks
^^^^^^^^^^^^^^^^^^^^^^

To create a new ``TestCaseMock`` you must extend that class and implement the relevant parts:

.. code-block:: python

    class ShrubberyMock(TestCaseMock):
        # this name is mandatory, it is the name used in the test specification
        name = "shrubbery"

        def setup(self, mocker):
            # perform setup, commonly using mocker to patch some other piece of code
            ...

        def check(self, test_case, results):
            # verify the tst execution met the expectations of the test case
            # for example the function was called as many times as it should
            ...

        def fixtures(self):
            # returns a dict mapping names to pytest fixtures that should be used for the test case
            # for example, in RunCommandMock it creates a fixture that patches AnsibleModule.get_bin_path
            ...

Caveats
^^^^^^^

Known issues/opportunities for improvement:

* Only one ``UTHelper`` per test module: UTHelper injects a test function with a fixed name into the module's namespace,
  so placing a second ``UTHelper`` instance is going to overwrite the function created by the first one.
* Order of elements in module's namespace is not consistent across executions in Python 3.5, so if adding more tests to the test module
  might make Test Helper add its function before or after the other test functions.
  In the community.general collection the CI processes uses ``pytest-xdist`` to paralellize and distribute the tests,
  and it requires the order of the tests to be consistent.

.. versionadded:: 7.5.0
