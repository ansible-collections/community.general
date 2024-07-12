..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_modulehelper:


Module Helper guide
===================


Introduction
^^^^^^^^^^^^

Writing a module for Ansible is largely described in existing documentation.
However, a good part of that is boilerplate code that needs to be repeated every single time.
That is where ``ModuleHelper`` comes to assistance. A lot of the boilerplate code is already
in place.


Quickstart
""""""""""

The example from Ansible documentation written with ``ModuleHelper`` is below.
Bear in mind that it does **not** showcase all of MH's features:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


    class MyTest(ModuleHelper):
        module = dict(
            argument_spec=dict(
                name=dict(type='str', required=True),
                new=dict(type='bool', required=False, default=False),
            ),
            supports_check_mode=True,
        )

        def __init_module__(self):
            self.vars.original_message = ''
            self.vars.message = ''

        def __run__(self):
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'

        def __changed__(self):
            return bool(self.vars.new)

        def __quit_module__(self):
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")


    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()


From that example please notice:

- All the parameters automatically become variables in the ``self.vars`` field, which
  is of the ``VarDict`` type. See :ref:`VarDict Guide` for more details
  on  how to use ``VarDict``.
- Some convenience methods delegate straight into ``AnsibleModule``, like ``self.check_mode``, ``self.diff_mode``, ``self.verbosity``.
- The following methods in MH are executed in the order:

  #. ``self.__init_module__()``: commonly used to initialize variables
  #. ``self.__run__()``: the actual execution of the module logic
  #. ``self.__quit_module__()``: tear-down logic or any code that must be executed after the main part.

- There is no need to call ``module.exit_json()`` (or ``module.fail_json()`` for that matter),
  exceptions are used to cause the module to fail. If no ``Exception`` is raised, it is
  understood that the module succeeded.
- Speaking of exceptions, there is a convenience method to raise a generic ``ModuleHelperException``
  called ``self.do_raise()``.

These and other features are described in more detail below.


Features
^^^^^^^^

General structure
"""""""""""""""""

- class

  - ``__init_module__()``
  - ``__run__()``
  - ``__quit_module__()``

- main > class.execute()


Handling changes
""""""""""""""""

- ``self.__changed__()``
- self.vars
- override ``self.has_changed()``


Parameters, variables, and output
"""""""""""""""""""""""""""""""""

- VarDict

  - ``use_old_vardict = True``
  - ``mute_vardict_deprecation = False``

- output
- track changes

  - present diff in output

- facts

  - facts vars
  - facts parameters
  - facts name


Exceptions
""""""""""

StateModuleHelper
^^^^^^^^^^^^^^^^^



References
^^^^^^^^^^

- `Developer Guide <https://docs.ansible.com/ansible/latest/dev_guide/index.html>`_
    - `Creating a module <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-a-module>`_
- :ref:`VarDict Guide`
-

.. versionadded:: 3.1.0
