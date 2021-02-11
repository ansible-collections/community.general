# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.monitoring import statsd
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestStatsDModule(ModuleTestCase):

    def setUp(self):
        super(TestStatsDModule, self).setUp()
        self.module = statsd
