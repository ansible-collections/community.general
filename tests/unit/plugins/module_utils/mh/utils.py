# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import traceback
from functools import wraps

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    ModuleTestCase as TestCase,
)

from ansible_collections.community.general.plugins.module_utils.mh.base import ModuleHelperBase
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException


class ModuleTestCase(TestCase):
    def setUp(self):
        super().setUp()
        ModuleHelperBase.run = module_fails_on_exception(unhandled_exceptions=(AnsibleExitJson, AnsibleFailJson))(
            ModuleHelperBase.run.__wrapped__
        )


def module_fails_on_exception(unhandled_exceptions=()):
    def deco(func):
        conflict_list = ("msg", "exception", "output", "vars", "changed")

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            def fix_key(k):
                return k if k not in conflict_list else f"_{k}"

            def fix_var_conflicts(output):
                result = {fix_key(k): v for k, v in output.items()}
                return result

            try:
                func(self, *args, **kwargs)
            except unhandled_exceptions:
                # re-raise exception without further processing
                raise
            except ModuleHelperException as e:
                if e.update_output:
                    self.update_output(**e.update_output)
                # patchy solution to resolve conflict with output variables
                output = fix_var_conflicts(self.output)
                self.module.fail_json(
                    msg=e.msg, exception=traceback.format_exc(), output=self.output, vars=self.vars.output(), **output
                )
            except Exception as e:
                # patchy solution to resolve conflict with output variables
                output = fix_var_conflicts(self.output)
                msg = f"Module failed with exception: {str(e).strip()}"
                self.module.fail_json(
                    msg=msg, exception=traceback.format_exc(), output=self.output, vars=self.vars.output(), **output
                )

        return wrapper

    return deco
