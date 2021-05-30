# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2021, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from functools import reduce

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.dict_transformations import dict_merge

from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException as _MHE

YAML_IMP_ERR = None
try:
    import yaml
    HAS_YAML = True
except ImportError:
    YAML_IMP_ERR = traceback.format_exc()
    HAS_YAML = False


class _YamlNotFound(Exception):
    def __init__(self, msg, exception):
        self.msg = msg
        self.exception = exception


class ModuleMixin(object):
    module = None
    ModuleHelperException = _MHE
    auto_args_spec = []

    @staticmethod
    def _parse_options(options):
        param_spec_fields = ('type', 'elements', 'required', 'default', 'choices', 'aliases')
        result = {}
        for opt in options:
            opt_spec = options[opt]
            result.update({opt: dict([(k, opt_spec[k]) for k in opt_spec if k in param_spec_fields])})
            if 'suboptions' in opt_spec:
                result[opt]['options'] = ModuleMixin._parse_options(opt_spec['suboptions'])
        return result

    @staticmethod
    def _args_spec_from_docs(docs):
        if not docs:
            return {}
        d = yaml.load(docs)
        options = d['options']
        return ModuleMixin._parse_options(options)

    def auto_args(self):
        if not HAS_YAML:
            # unable to call module.fail_json() as module is not yet instantiated
            raise _YamlNotFound(msg=missing_required_lib('PyYAML'), exception=YAML_IMP_ERR)

        auto_args = [self.auto_args_spec] if isinstance(self.auto_args_spec, str) else self.auto_args_spec
        opts_docs = [self._args_spec_from_docs(d) for d in auto_args]
        opts_args = [self.module['argument_spec']] or []
        opts_list = opts_docs + opts_args
        options = reduce(dict_merge, opts_list)
        return options

    def __init__(self, module=None):
        super(ModuleMixin, self).__init__()

        if module:
            self.module = module

        if not isinstance(self.module, AnsibleModule):
            if self.auto_args_spec:
                try:
                    options = self.auto_args()
                    self.module['argument_spec'] = options
                except _YamlNotFound as yaml_not_found:
                    # Cannot create the real module if yaml is missing, so raising error with dummy one
                    self.module = AnsibleModule(argument_spec={"dummy": {"type": "str"}})
                    self.module.fail_json(msg=yaml_not_found.msg, exception=yaml_not_found.exception)

            self.module = AnsibleModule(**self.module)

    def exit(self):
        self.module.exit_json(changed=self.has_changed(), **self.output)
