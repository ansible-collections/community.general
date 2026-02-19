# Copyright (c) 2023, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ansible.plugins.loader as plugin_loader

from ansible import __version__ as ansible_version
from ansible.errors import AnsiblePluginNotFound
from ansible.module_utils.six import raise_from
from ansible.plugins.loader import fragment_loader
from ansible.template import Templar
from ansible.utils.plugin_docs import get_plugin_docs

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


# Whether Templar has a cache, which can be controlled by Templar.template()'s cache option.
# The cache was removed for ansible-core 2.14 (https://github.com/ansible/ansible/pull/78419)
_TEMPLAR_HAS_TEMPLATE_CACHE = LooseVersion(ansible_version) < LooseVersion('2.14.0')


class LoadingError(Exception):
    pass


class UnknownPlugin(LoadingError):
    pass


class UnknownPluginType(UnknownPlugin):
    pass


class Requirements(object):
    def __init__(self, system=None, python=None):
        self.system = set(system if system else [])
        self.python = set(python if python else [])

    def merge(self, other):
        self.system.update(other.system)
        self.python.update(other.python)

    def __repr__(self):
        return 'Requirements(system={system!r}, python={python!r})'.format(
            system=sorted(self.system),
            python=sorted(self.python),
        )


def _check(value, name, acceptable_types, accept_none=False):
    if accept_none and value is None:
        return value

    if isinstance(value, acceptable_types):
        return value

    if not isinstance(acceptable_types, tuple):
        acceptable_types = (acceptable_types, )

    raise LoadingError(
        '{name} {value!r} is not one of types {acceptable_types}{or_none}'.format(
            value=value,
            name=name,
            acceptable_types=', '.join(str(t) for t in acceptable_types),
            or_none=', or none' if accept_none else ''
        )
    )


def _check_list(value, name, element_types, accept_none=False, none_result=None):
    if accept_none and value is None:
        return none_result

    if isinstance(value, element_types):
        value = [value]

    if not isinstance(value, list):
        raise LoadingError('{name} {value!r} is not a list'.format(value=value, name=name))

    for i, v in enumerate(value):
        _check(v, '{0}[{1}]'.format(name, i + 1), element_types)

    return value


class InstallableBlock(object):
    def __init__(self, when, system, python):
        self.when = when
        self.system = system
        self.python = python

    def __repr__(self):
        return 'InstallableBlock(when={when!r}, system={system!r}, python={python!r})'.format(
            when=self.when,
            system=self.system,
            python=self.python,
        )

    @classmethod
    def parse(cls, block):
        _check(block, 'block', dict)
        when = _check(block.get('when'), 'when', (str, bool), accept_none=True)
        system = _check_list(block.get('system'), 'system', str, accept_none=True, none_result=[])
        python = _check_list(block.get('python'), 'python', str, accept_none=True, none_result=[])
        return cls(when, system, python)


class InstallableRequirement(object):
    def __init__(self, name, blocks):
        self.name = name
        self.blocks = blocks

    @classmethod
    def parse(cls, requirement):
        _check(requirement, 'requirement', dict)
        name = _check(requirement.get('name'), 'name', str)
        blocks = _check_list(requirement.get('blocks'), 'blocks', dict)
        return cls(name, [InstallableBlock.parse(block) for block in blocks])


class InstallableRequirements(object):
    def __init__(self, plugin_name, plugin_type, requirements):
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.requirements = requirements

    @classmethod
    def parse(cls, plugin_name, plugin_type, reqs):
        return cls(
            _check(plugin_name, 'plugin_name', str),
            _check(plugin_type, 'plugin_type', str),
            [InstallableRequirement.parse(req) for req in _check(reqs, 'requirements', list)]
        )


def retrieve_plugin_dependencies(plugin_name, plugin_type):
    loader = getattr(plugin_loader, '%s_loader' % plugin_type, None)
    if loader is None:
        raise UnknownPluginType(plugin_type)

    try:
        doc, dummy1, dummy2, dummy3 = get_plugin_docs(plugin_name, plugin_type, loader, fragment_loader, verbose=False)
    except AnsiblePluginNotFound as e:
        raise_from(UnknownPlugin(plugin_name), e)
    except Exception as e:
        raise_from(LoadingError('Error while loading documentation of {0} {1}: {2}'.format(plugin_type, plugin_name, e)), e)

    if not doc:
        raise LoadingError('Found no documentation of {0} {1}'.format(plugin_type, plugin_name))

    reqs = doc.get('installable_requirements')
    if not isinstance(reqs, list):
        raise LoadingError('Found no installable requirements information for {0} {1}'.format(plugin_type, plugin_name))

    try:
        return InstallableRequirements.parse(plugin_name, plugin_type, reqs)
    except LoadingError as e:
        raise_from(LoadingError('Error while parsing installable requirements for {0} {1}: {2}'.format(plugin_type, plugin_name, e)), e)


_REQUIRED_FACTS = (
    'architecture',
    'distribution',
    'distribution_major_version',
    'distribution_release',
    'distribution_version',
    'os_family',
    'pkg_mgr',
    'python',
    'python_version',
    'selinux',
    'selinux_python_present',
    'service_mgr',
    'system',
)


_ACCEPTABLE_FACTS = tuple(sorted(_REQUIRED_FACTS + (
    'distribution_minor_version',
)))


def get_needed_facts():
    return _REQUIRED_FACTS


def get_used_facts():
    return _ACCEPTABLE_FACTS


class RequirementFinder(object):
    @staticmethod
    def _massage_facts(ansible_facts):
        result = {}
        for fact in _ACCEPTABLE_FACTS:
            if fact in ansible_facts:
                result[fact] = ansible_facts[fact]
        return result

    def __init__(self, templar, controller_ansible_facts, remote_ansible_facts):
        self.templar = Templar(loader=templar._loader)
        self.controller_ansible_facts = self._massage_facts(controller_ansible_facts)
        self.remote_ansible_facts = self._massage_facts(remote_ansible_facts)

    def _match_block(self, block, ansible_facts):
        if block.when is None:
            return True

        if isinstance(block.when, bool):
            return block.when

        self.templar.available_variables = {'ansible_facts': ansible_facts}
        expression = "{0}{1}{2}".format("{{", block.when, "}}")
        kwargs = {
            'fail_on_undefined': True,
            'disable_lookups': True,
        }
        if _TEMPLAR_HAS_TEMPLATE_CACHE:
            kwargs['cache'] = False
        value = self.templar.template(expression, **kwargs)

        if isinstance(value, bool):
            return value

        raise LoadingError('Expression evaluated to {value!r}, expected boolean'.format(value=value))

    def _find(self, req, ansible_facts, plugin_name, plugin_type):
        for block in req.blocks:
            try:
                if self._match_block(block, ansible_facts):
                    return Requirements(system=block.system, python=block.python)
            except LoadingError:
                raise
            except Exception as e:
                raise_from(LoadingError('Error while matching block {block!r} for {req!r} of {type} {plugin}: {exc}'.format(
                    block=block,
                    req=req.name,
                    type=plugin_type,
                    plugin=plugin_name,
                    exc=e,
                )), e)
        raise LoadingError('Cannot find matching block for "{req}" of {type} {plugin}'.format(
            req=req.name,
            type=plugin_type,
            plugin=plugin_name,
        ))

    def find(self, installable_requirements, modules_for_remote=True):
        ansible_facts = (
            self.remote_ansible_facts
            if installable_requirements.plugin_type == 'module' and modules_for_remote
            else self.controller_ansible_facts
        )
        result = Requirements()
        for req in installable_requirements.requirements:
            result.merge(self._find(
                req,
                ansible_facts,
                installable_requirements.plugin_name,
                installable_requirements.plugin_type,
            ))
        return result
