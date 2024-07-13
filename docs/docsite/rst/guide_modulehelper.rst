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
That is where ``ModuleHelper`` comes to assistance: a lot of that boilerplate code is done.


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

        def __run__(self):
            self.vars.original_message = ''
            self.vars.message = ''
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'
            self.changed = bool(self.vars.new)
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")


    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()

From this example notice:

- All the parameters automatically become variables in the ``self.vars`` field, which is of the ``VarDict`` type.
  See :ref:`ansible_collections.community.general.docsite.guide_vardict` for more details on  how to use ``VarDict``.
- Some convenience methods delegate straight into ``AnsibleModule``, like ``self.check_mode``.
- There is no need to call ``module.exit_json()`` (or ``module.fail_json()`` for that matter),
  exceptions are used to cause the module to fail.
  If no exception is raised, the module has succeeded.
  There is a generic method to raise exceptions called ``self.do_raise()``.

These and other features are described in more detail below.


Features
^^^^^^^^

General structure
"""""""""""""""""

``ModuleHelper`` is a wrapper around the standard ``AnsibleModule``, providing some features.
The basic structure of a module using ``ModuleHelper`` is as shown in the `Quickstart`_ section above,
but there are more elements that will take part in it.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper

    class MyTest(ModuleHelper):
        output_params = ()
        change_params = ()
        diff_params = ()
        facts_name = None
        facts_params = ()
        use_old_vardict = True
        mute_vardict_deprecation = False
        module = dict(...)

After importing ``ModuleHelper``, you need to declare a class that extends ``ModuleHelper``.
This part will always be the same, except when using ``StateModuleHelper``, which builds on top
of the features provided by MH. See below for more details.

The easiest way of specifying the module is to create the class variable ``module`` with a dictionary
containing the exact arguments that would be passed as paramters to ``AnsibleModule``.
Keep in mind that ``module`` can be either a dictionary as show above, or it can be a proper ``AnsibleModule`` object.
MH also accepts a parameter ``module`` in its constructor, if that parameter is used used,
then it will override the class variable. The parametercan also be a ``dict`` or ``AnsibleModule``.

Beyond the definition of the module, there are other variables that can be used to control aspects
of MH's behavior. These variables should be set at the very beginning of the class, and their semantics are
explained through this document.

The main logic of the module happens in the ``ModuleHelper.run()`` method, which looks like:

.. code-block:: python

    @module_fails_on_exception
    def run(self):
        self.__init_module__()
        self.__run__()
        self.__quit_module__()
        output = self.output
        if 'failed' not in output:
            output['failed'] = False
        self.module.exit_json(changed=self.has_changed(), **output)

Most modules will be able to perform their tasks simply by implementing the ``ModuleHelper.__run__()``.
However, in some cases, you might want to execute actions before and/or after the main tasks,
for those cases you can use, respectively, ``ModuleHelper.__init_module__()`` and ``ModuleHelper.__quit_module__()``.

Note that the output comes from ``self.output``, which is a ``@property`` method.
By default, that property will collect all the variables that are marked for output and return them in a dictionary with their values.
Moreover, the default ``self.output`` will also handle Ansible ``facts`` and *diff mode*.
See more in `Parameters, variables, and output`_ below.
The property ``self.output`` method can be overriden, but of course you would need to address these issues in your own code.

Also note the changed status comes from self.has_changed(), which is usually calculated from variables that are marked
to track changes in their content. See more in `Handling changes`_ below.

And last but not least on this code above, the method is decorated with ``@module_fails_on_exception``, which will
capture exceptions that are raised and

.. code-block:: python

        def __init_module__(self):
            self.vars.original_message = ''
            self.vars.message = ''

        def __run__(self):
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'
            self.changed = bool(self.vars.new)

        def __quit_module__(self):
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")


    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()


The following methods in MH are executed in the order:

#. ``self.__init_module__()``: commonly used to initialize variables
#. ``self.__run__()``: the actual execution of the module logic
#. ``self.__quit_module__()``: tear-down logic or any code that must be executed after the main part.


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

- :ref:`ansible_collections.community.general.docsite.guide_vardict`
-

.. versionadded:: 3.1.0
