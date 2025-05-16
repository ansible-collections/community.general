#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Paul Durivage <paul.durivage@rackspace.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rax_files
short_description: Manipulate Rackspace Cloud Files Containers
description:
  - Manipulate Rackspace Cloud Files Containers
options:
  clear_meta:
    description:
      - Optionally clear existing metadata when applying metadata to existing containers.
        Selecting this option is only appropriate when setting type=meta
    type: bool
    default: false
  container:
    type: str
    description:
      - The container to use for container or metadata operations.
  meta:
    type: dict
    default: {}
    description:
      - A hash of items to set as metadata values on a container
  private:
    description:
      - Used to set a container as private, removing it from the CDN.  B(Warning!)
        Private containers, if previously made public, can have live objects
        available until the TTL on cached objects expires
    type: bool
    default: false
  public:
    description:
      - Used to set a container as public, available via the Cloud Files CDN
    type: bool
    default: false
  region:
    type: str
    description:
      - Region to create an instance in
  state:
    type: str
    description:
      - Indicate desired state of the resource
    choices: ['present', 'absent', 'list']
    default: present
  ttl:
    type: int
    description:
      - In seconds, set a container-wide TTL for all objects cached on CDN edge nodes.
        Setting a TTL is only appropriate for containers that are public
  type:
    type: str
    description:
      - Type of object to do work on, i.e. metadata object or a container object
    choices:
      - container
      - meta
    default: container
  web_error:
    type: str
    description:
       - Sets an object to be presented as the HTTP error page when accessed by the CDN URL
  web_index:
    type: str
    description:
       - Sets an object to be presented as the HTTP index page when accessed by the CDN URL
author: "Paul Durivage (@angstwad)"
extends_documentation_fragment:
- community.general.rackspace
- community.general.rackspace.openstack

'''

EXAMPLES = '''
- name: "Test Cloud Files Containers"
  hosts: local
  gather_facts: false
  tasks:
    - name: "List all containers"
      community.general.rax_files:
        state: list

    - name: "Create container called 'mycontainer'"
      community.general.rax_files:
        container: mycontainer

    - name: "Create container 'mycontainer2' with metadata"
      community.general.rax_files:
        container: mycontainer2
        meta:
          key: value
          file_for: someuser@example.com

    - name: "Set a container's web index page"
      community.general.rax_files:
        container: mycontainer
        web_index: index.html

    - name: "Set a container's web error page"
      community.general.rax_files:
        container: mycontainer
        web_error: error.html

    - name: "Make container public"
      community.general.rax_files:
        container: mycontainer
        public: true

    - name: "Make container public with a 24 hour TTL"
      community.general.rax_files:
        container: mycontainer
        public: true
        ttl: 86400

    - name: "Make container private"
      community.general.rax_files:
        container: mycontainer
        private: true

- name: "Test Cloud Files Containers Metadata Storage"
  hosts: local
  gather_facts: false
  tasks:
    - name: "Get mycontainer2 metadata"
      community.general.rax_files:
        container: mycontainer2
        type: meta

    - name: "Set mycontainer2 metadata"
      community.general.rax_files:
        container: mycontainer2
        type: meta
        meta:
          uploaded_by: someuser@example.com

    - name: "Remove mycontainer2 metadata"
      community.general.rax_files:
        container: "mycontainer2"
        type: meta
        state: absent
        meta:
          key: ""
          file_for: ""
'''

try:
    import pyrax
    HAS_PYRAX = True
except ImportError as e:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rax import rax_argument_spec, rax_required_together, setup_rax_module


EXIT_DICT = dict(success=True)
META_PREFIX = 'x-container-meta-'


def _get_container(module, cf, container):
    try:
        return cf.get_container(container)
    except pyrax.exc.NoSuchContainer as e:
        module.fail_json(msg=e.message)


def _fetch_meta(module, container):
    EXIT_DICT['meta'] = dict()
    try:
        for k, v in container.get_metadata().items():
            split_key = k.split(META_PREFIX)[-1]
            EXIT_DICT['meta'][split_key] = v
    except Exception as e:
        module.fail_json(msg=e.message)


def meta(cf, module, container_, state, meta_, clear_meta):
    c = _get_container(module, cf, container_)

    if meta_ and state == 'present':
        try:
            meta_set = c.set_metadata(meta_, clear=clear_meta)
        except Exception as e:
            module.fail_json(msg=e.message)
    elif meta_ and state == 'absent':
        remove_results = []
        for k, v in meta_.items():
            c.remove_metadata_key(k)
            remove_results.append(k)
            EXIT_DICT['deleted_meta_keys'] = remove_results
    elif state == 'absent':
        remove_results = []
        for k, v in c.get_metadata().items():
            c.remove_metadata_key(k)
            remove_results.append(k)
            EXIT_DICT['deleted_meta_keys'] = remove_results

    _fetch_meta(module, c)
    _locals = locals().keys()

    EXIT_DICT['container'] = c.name
    if 'meta_set' in _locals or 'remove_results' in _locals:
        EXIT_DICT['changed'] = True

    module.exit_json(**EXIT_DICT)


def container(cf, module, container_, state, meta_, clear_meta, ttl, public,
              private, web_index, web_error):
    if public and private:
        module.fail_json(msg='container cannot be simultaneously '
                             'set to public and private')

    if state == 'absent' and (meta_ or clear_meta or public or private or web_index or web_error):
        module.fail_json(msg='state cannot be omitted when setting/removing '
                             'attributes on a container')

    if state == 'list':
        # We don't care if attributes are specified, let's list containers
        EXIT_DICT['containers'] = cf.list_containers()
        module.exit_json(**EXIT_DICT)

    try:
        c = cf.get_container(container_)
    except pyrax.exc.NoSuchContainer as e:
        # Make the container if state=present, otherwise bomb out
        if state == 'present':
            try:
                c = cf.create_container(container_)
            except Exception as e:
                module.fail_json(msg=e.message)
            else:
                EXIT_DICT['changed'] = True
                EXIT_DICT['created'] = True
        else:
            module.fail_json(msg=e.message)
    else:
        # Successfully grabbed a container object
        # Delete if state is absent
        if state == 'absent':
            try:
                cont_deleted = c.delete()
            except Exception as e:
                module.fail_json(msg=e.message)
            else:
                EXIT_DICT['deleted'] = True

    if meta_:
        try:
            meta_set = c.set_metadata(meta_, clear=clear_meta)
        except Exception as e:
            module.fail_json(msg=e.message)
        finally:
            _fetch_meta(module, c)

    if ttl:
        try:
            c.cdn_ttl = ttl
        except Exception as e:
            module.fail_json(msg=e.message)
        else:
            EXIT_DICT['ttl'] = c.cdn_ttl

    if public:
        try:
            cont_public = c.make_public()
        except Exception as e:
            module.fail_json(msg=e.message)
        else:
            EXIT_DICT['container_urls'] = dict(url=c.cdn_uri,
                                               ssl_url=c.cdn_ssl_uri,
                                               streaming_url=c.cdn_streaming_uri,
                                               ios_uri=c.cdn_ios_uri)

    if private:
        try:
            cont_private = c.make_private()
        except Exception as e:
            module.fail_json(msg=e.message)
        else:
            EXIT_DICT['set_private'] = True

    if web_index:
        try:
            cont_web_index = c.set_web_index_page(web_index)
        except Exception as e:
            module.fail_json(msg=e.message)
        else:
            EXIT_DICT['set_index'] = True
        finally:
            _fetch_meta(module, c)

    if web_error:
        try:
            cont_err_index = c.set_web_error_page(web_error)
        except Exception as e:
            module.fail_json(msg=e.message)
        else:
            EXIT_DICT['set_error'] = True
        finally:
            _fetch_meta(module, c)

    EXIT_DICT['container'] = c.name
    EXIT_DICT['objs_in_container'] = c.object_count
    EXIT_DICT['total_bytes'] = c.total_bytes

    _locals = locals().keys()
    if ('cont_deleted' in _locals
            or 'meta_set' in _locals
            or 'cont_public' in _locals
            or 'cont_private' in _locals
            or 'cont_web_index' in _locals
            or 'cont_err_index' in _locals):
        EXIT_DICT['changed'] = True

    module.exit_json(**EXIT_DICT)


def cloudfiles(module, container_, state, meta_, clear_meta, typ, ttl, public,
               private, web_index, web_error):
    """ Dispatch from here to work with metadata or file objects """
    cf = pyrax.cloudfiles

    if cf is None:
        module.fail_json(msg='Failed to instantiate client. This '
                             'typically indicates an invalid region or an '
                             'incorrectly capitalized region name.')

    if typ == "container":
        container(cf, module, container_, state, meta_, clear_meta, ttl,
                  public, private, web_index, web_error)
    else:
        meta(cf, module, container_, state, meta_, clear_meta)


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            container=dict(),
            state=dict(choices=['present', 'absent', 'list'],
                       default='present'),
            meta=dict(type='dict', default=dict()),
            clear_meta=dict(default=False, type='bool'),
            type=dict(choices=['container', 'meta'], default='container'),
            ttl=dict(type='int'),
            public=dict(default=False, type='bool'),
            private=dict(default=False, type='bool'),
            web_index=dict(),
            web_error=dict()
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together()
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    container_ = module.params.get('container')
    state = module.params.get('state')
    meta_ = module.params.get('meta')
    clear_meta = module.params.get('clear_meta')
    typ = module.params.get('type')
    ttl = module.params.get('ttl')
    public = module.params.get('public')
    private = module.params.get('private')
    web_index = module.params.get('web_index')
    web_error = module.params.get('web_error')

    if state in ['present', 'absent'] and not container_:
        module.fail_json(msg='please specify a container name')
    if clear_meta and not typ == 'meta':
        module.fail_json(msg='clear_meta can only be used when setting '
                             'metadata')

    setup_rax_module(module, pyrax)
    cloudfiles(module, container_, state, meta_, clear_meta, typ, ttl, public,
               private, web_index, web_error)


if __name__ == '__main__':
    main()
