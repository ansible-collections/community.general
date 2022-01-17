# (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


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
