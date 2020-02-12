#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The exos lldp_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.community.general.plugins.module_utils.network.exos.argspec.lldp_interfaces.lldp_interfaces import Lldp_interfacesArgs
from ansible_collections.community.general.plugins.module_utils.network.exos.exos import send_requests


class Lldp_interfacesFacts(object):
    """ The exos lldp_interfaces fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Lldp_interfacesArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lldp_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            request = [{
                "path": "/rest/restconf/data/openconfig-lldp:lldp/interfaces?depth=4",
                "method": "GET"
            }]
            data = send_requests(self._module, requests=request)

        objs = []
        if data:
            for d in data[0]["openconfig-lldp:interfaces"]["interface"]:
                obj = self.render_config(self.generated_spec, d["config"])
                if obj:
                    objs.append(obj)

        ansible_facts['ansible_network_resources'].pop('lldp_interfaces', None)
        facts = {}
        if objs:
            params = utils.validate_config(self.argument_spec, {'config': objs})
            facts['lldp_interfaces'] = params['config']

        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)

        config["name"] = conf["name"]
        config["enabled"] = bool(conf["enabled"])

        return utils.remove_empties(config)
