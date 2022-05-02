# (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: a_module
  short_description: Test whether a given string refers to an existing module or action plugin
  version_added: 4.0.0
  author: Felix Fontein (@felixfontein)
  description:
    - Test whether a given string refers to an existing module or action plugin.
    - This can be useful in roles, which can use this to ensure that required modules are present ahead of time.
  options:
    _input:
      description: A string denoting a fully qualified collection name (FQCN) of a module or action plugin.
      type: string
      required: true
'''

EXAMPLES = '''
- name: Make sure that community.aws.route53 is available
  ansible.builtin.assert:
    that:
      - >
        'community.aws.route53' is community.general.a_module

- name: Make sure that community.general.does_not_exist is not a module or action plugin
  ansible.builtin.assert:
    that:
      - "'community.general.does_not_exist' is not community.general.a_module"
'''

RETURN = '''
  _value:
    description: Whether the module or action plugin denoted by the input exists.
    type: boolean
'''

from ansible.plugins.loader import action_loader, module_loader

try:
    from ansible.errors import AnsiblePluginRemovedError
except ImportError:
    AnsiblePluginRemovedError = Exception


def a_module(term):
    """
    Example:
      - 'community.general.ufw' is community.general.a_module
      - 'community.general.does_not_exist' is not community.general.a_module
    """
    try:
        for loader in (action_loader, module_loader):
            data = loader.find_plugin(term)
            # Ansible 2.9 returns a tuple
            if isinstance(data, tuple):
                data = data[0]
            if data is not None:
                return True
        return False
    except AnsiblePluginRemovedError:
        return False


class TestModule(object):
    ''' Ansible jinja2 tests '''

    def tests(self):
        return {
            'a_module': a_module,
        }
