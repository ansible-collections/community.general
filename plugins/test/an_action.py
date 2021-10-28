# (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible.plugins.loader import action_loader, module_loader


def an_action(term):
    """
    Example:
      - 'community.general.ufw' is community.general.an_action
      - 'community.general.does_not_exist' is not community.general.an_action
    """
    for loader in (action_loader, module_loader):
        data = loader.find_plugin(term)
        # Ansible 2.9 returns a tuple
        if isinstance(data, tuple):
            data = data[0]
        if data is not None:
            return True
    return False


class TestModule(object):
    ''' Ansible jinja2 tests '''

    def tests(self):
        return {
            'an_action': an_action,
        }
