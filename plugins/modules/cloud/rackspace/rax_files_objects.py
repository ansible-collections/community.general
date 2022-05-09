#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Paul Durivage <paul.durivage@rackspace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rax_files_objects
short_description: Upload, download, and delete objects in Rackspace Cloud Files
description:
  - Upload, download, and delete objects in Rackspace Cloud Files.
options:
  clear_meta:
    description:
      - Optionally clear existing metadata when applying metadata to existing objects.
        Selecting this option is only appropriate when setting I(type=meta).
    type: bool
    default: false
  container:
    type: str
    description:
      - The container to use for file object operations.
    required: true
  dest:
    type: str
    description:
      - The destination of a C(get) operation; i.e. a local directory, C(/home/user/myfolder).
        Used to specify the destination of an operation on a remote object; i.e. a file name,
        C(file1), or a comma-separated list of remote objects, C(file1,file2,file17).
  expires:
    type: int
    description:
      - Used to set an expiration in seconds on an uploaded file or folder.
  meta:
    type: dict
    description:
      - Items to set as metadata values on an uploaded file or folder.
  method:
    type: str
    description:
      - >
        The method of operation to be performed: C(put) to upload files, C(get) to download files or
        C(delete) to remove remote objects in Cloud Files.
    choices:
      - get
      - put
      - delete
    default: get
  src:
    type: str
    description:
      - Source from which to upload files.  Used to specify a remote object as a source for
        an operation, i.e. a file name, C(file1), or a comma-separated list of remote objects,
        C(file1,file2,file17). Parameters I(src) and I(dest) are mutually exclusive on remote-only object operations
  structure:
    description:
      - Used to specify whether to maintain nested directory structure when downloading objects
        from Cloud Files.  Setting to false downloads the contents of a container to a single,
        flat directory
    type: bool
    default: 'yes'
  type:
    type: str
    description:
      - Type of object to do work on
      - Metadata object or a file object
    choices:
      - file
      - meta
    default: file
author: "Paul Durivage (@angstwad)"
extends_documentation_fragment:
- community.general.rackspace
- community.general.rackspace.openstack

'''

EXAMPLES = '''
- name: "Test Cloud Files Objects"
  hosts: local
  gather_facts: False
  tasks:
    - name: "Get objects from test container"
      community.general.rax_files_objects:
        container: testcont
        dest: ~/Downloads/testcont

    - name: "Get single object from test container"
      community.general.rax_files_objects:
        container: testcont
        src: file1
        dest: ~/Downloads/testcont

    - name: "Get several objects from test container"
      community.general.rax_files_objects:
        container: testcont
        src: file1,file2,file3
        dest: ~/Downloads/testcont

    - name: "Delete one object in test container"
      community.general.rax_files_objects:
        container: testcont
        method: delete
        dest: file1

    - name: "Delete several objects in test container"
      community.general.rax_files_objects:
        container: testcont
        method: delete
        dest: file2,file3,file4

    - name: "Delete all objects in test container"
      community.general.rax_files_objects:
        container: testcont
        method: delete

    - name: "Upload all files to test container"
      community.general.rax_files_objects:
        container: testcont
        method: put
        src: ~/Downloads/onehundred

    - name: "Upload one file to test container"
      community.general.rax_files_objects:
        container: testcont
        method: put
        src: ~/Downloads/testcont/file1

    - name: "Upload one file to test container with metadata"
      community.general.rax_files_objects:
        container: testcont
        src: ~/Downloads/testcont/file2
        method: put
        meta:
          testkey: testdata
          who_uploaded_this: someuser@example.com

    - name: "Upload one file to test container with TTL of 60 seconds"
      community.general.rax_files_objects:
        container: testcont
        method: put
        src: ~/Downloads/testcont/file3
        expires: 60

    - name: "Attempt to get remote object that does not exist"
      community.general.rax_files_objects:
        container: testcont
        method: get
        src: FileThatDoesNotExist.jpg
        dest: ~/Downloads/testcont
      ignore_errors: yes

    - name: "Attempt to delete remote object that does not exist"
      community.general.rax_files_objects:
        container: testcont
        method: delete
        dest: FileThatDoesNotExist.jpg
      ignore_errors: yes

- name: "Test Cloud Files Objects Metadata"
  hosts: local
  gather_facts: false
  tasks:
    - name: "Get metadata on one object"
      community.general.rax_files_objects:
        container: testcont
        type: meta
        dest: file2

    - name: "Get metadata on several objects"
      community.general.rax_files_objects:
        container: testcont
        type: meta
        src: file2,file1

    - name: "Set metadata on an object"
      community.general.rax_files_objects:
        container: testcont
        type: meta
        dest: file17
        method: put
        meta:
          key1: value1
          key2: value2
        clear_meta: true

    - name: "Verify metadata is set"
      community.general.rax_files_objects:
        container: testcont
        type: meta
        src: file17

    - name: "Delete metadata"
      community.general.rax_files_objects:
        container: testcont
        type: meta
        dest: file17
        method: delete
        meta:
          key1: ''
          key2: ''

    - name: "Get metadata on all objects"
      community.general.rax_files_objects:
        container: testcont
        type: meta
'''

import os

try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rax import rax_argument_spec, rax_required_together, setup_rax_module


EXIT_DICT = dict(success=False)
META_PREFIX = 'x-object-meta-'


def _get_container(module, cf, container):
    try:
        return cf.get_container(container)
    except pyrax.exc.NoSuchContainer as e:
        module.fail_json(msg=e.message)


def _upload_folder(cf, folder, container, ttl=None, headers=None):
    """ Uploads a folder to Cloud Files.
    """
    total_bytes = 0
    for root, dummy, files in os.walk(folder):
        for fname in files:
            full_path = os.path.join(root, fname)
            obj_name = os.path.relpath(full_path, folder)
            obj_size = os.path.getsize(full_path)
            cf.upload_file(container, full_path, obj_name=obj_name, return_none=True, ttl=ttl, headers=headers)
            total_bytes += obj_size
    return total_bytes


def upload(module, cf, container, src, dest, meta, expires):
    """ Uploads a single object or a folder to Cloud Files Optionally sets an
    metadata, TTL value (expires), or Content-Disposition and Content-Encoding
    headers.
    """
    if not src:
        module.fail_json(msg='src must be specified when uploading')

    c = _get_container(module, cf, container)
    src = os.path.abspath(os.path.expanduser(src))
    is_dir = os.path.isdir(src)

    if not is_dir and not os.path.isfile(src) or not os.path.exists(src):
        module.fail_json(msg='src must be a file or a directory')
    if dest and is_dir:
        module.fail_json(msg='dest cannot be set when whole '
                             'directories are uploaded')

    cont_obj = None
    total_bytes = 0
    try:
        if dest and not is_dir:
            cont_obj = c.upload_file(src, obj_name=dest, ttl=expires, headers=meta)
        elif is_dir:
            total_bytes = _upload_folder(cf, src, c, ttl=expires, headers=meta)
        else:
            cont_obj = c.upload_file(src, ttl=expires, headers=meta)
    except Exception as e:
        module.fail_json(msg=e.message)

    EXIT_DICT['success'] = True
    EXIT_DICT['container'] = c.name
    EXIT_DICT['msg'] = "Uploaded %s to container: %s" % (src, c.name)
    if cont_obj or total_bytes > 0:
        EXIT_DICT['changed'] = True
    if meta:
        EXIT_DICT['meta'] = dict(updated=True)

    if cont_obj:
        EXIT_DICT['bytes'] = cont_obj.total_bytes
        EXIT_DICT['etag'] = cont_obj.etag
    else:
        EXIT_DICT['bytes'] = total_bytes

    module.exit_json(**EXIT_DICT)


def download(module, cf, container, src, dest, structure):
    """ Download objects from Cloud Files to a local path specified by "dest".
    Optionally disable maintaining a directory structure by by passing a
    false value to "structure".
    """
    # Looking for an explicit destination
    if not dest:
        module.fail_json(msg='dest is a required argument when '
                             'downloading from Cloud Files')

    # Attempt to fetch the container by name
    c = _get_container(module, cf, container)

    # Accept a single object name or a comma-separated list of objs
    # If not specified, get the entire container
    if src:
        objs = map(str.strip, src.split(','))
    else:
        objs = c.get_object_names()

    dest = os.path.abspath(os.path.expanduser(dest))
    is_dir = os.path.isdir(dest)

    if not is_dir:
        module.fail_json(msg='dest must be a directory')

    try:
        results = [c.download_object(obj, dest, structure=structure) for obj in objs]
    except Exception as e:
        module.fail_json(msg=e.message)

    len_results = len(results)
    len_objs = len(objs)

    EXIT_DICT['container'] = c.name
    EXIT_DICT['requested_downloaded'] = results
    if results:
        EXIT_DICT['changed'] = True
    if len_results == len_objs:
        EXIT_DICT['success'] = True
        EXIT_DICT['msg'] = "%s objects downloaded to %s" % (len_results, dest)
    else:
        EXIT_DICT['msg'] = "Error: only %s of %s objects were " \
                           "downloaded" % (len_results, len_objs)
    module.exit_json(**EXIT_DICT)


def delete(module, cf, container, src, dest):
    """ Delete specific objects by proving a single file name or a
    comma-separated list to src OR dest (but not both).  Omitting file name(s)
    assumes the entire container is to be deleted.
    """
    if src and dest:
        module.fail_json(msg="Error: ambiguous instructions; files to be deleted "
                             "have been specified on both src and dest args")

    c = _get_container(module, cf, container)

    objs = dest or src
    if objs:
        objs = map(str.strip, objs.split(','))
    else:
        objs = c.get_object_names()

    num_objs = len(objs)

    try:
        results = [c.delete_object(obj) for obj in objs]
    except Exception as e:
        module.fail_json(msg=e.message)

    num_deleted = results.count(True)

    EXIT_DICT['container'] = c.name
    EXIT_DICT['deleted'] = num_deleted
    EXIT_DICT['requested_deleted'] = objs

    if num_deleted:
        EXIT_DICT['changed'] = True

    if num_objs == num_deleted:
        EXIT_DICT['success'] = True
        EXIT_DICT['msg'] = "%s objects deleted" % num_deleted
    else:
        EXIT_DICT['msg'] = ("Error: only %s of %s objects "
                            "deleted" % (num_deleted, num_objs))
    module.exit_json(**EXIT_DICT)


def get_meta(module, cf, container, src, dest):
    """ Get metadata for a single file, comma-separated list, or entire
    container
    """
    if src and dest:
        module.fail_json(msg="Error: ambiguous instructions; files to be deleted "
                             "have been specified on both src and dest args")

    c = _get_container(module, cf, container)

    objs = dest or src
    if objs:
        objs = map(str.strip, objs.split(','))
    else:
        objs = c.get_object_names()

    try:
        results = dict()
        for obj in objs:
            meta = c.get_object(obj).get_metadata()
            results[obj] = dict((k.split(META_PREFIX)[-1], v) for k, v in meta.items())
    except Exception as e:
        module.fail_json(msg=e.message)

    EXIT_DICT['container'] = c.name
    if results:
        EXIT_DICT['meta_results'] = results
        EXIT_DICT['success'] = True
    module.exit_json(**EXIT_DICT)


def put_meta(module, cf, container, src, dest, meta, clear_meta):
    """ Set metadata on a container, single file, or comma-separated list.
    Passing a true value to clear_meta clears the metadata stored in Cloud
    Files before setting the new metadata to the value of "meta".
    """
    if src and dest:
        module.fail_json(msg="Error: ambiguous instructions; files to set meta"
                             " have been specified on both src and dest args")
    objs = dest or src
    objs = map(str.strip, objs.split(','))

    c = _get_container(module, cf, container)

    try:
        results = [c.get_object(obj).set_metadata(meta, clear=clear_meta) for obj in objs]
    except Exception as e:
        module.fail_json(msg=e.message)

    EXIT_DICT['container'] = c.name
    EXIT_DICT['success'] = True
    if results:
        EXIT_DICT['changed'] = True
        EXIT_DICT['num_changed'] = True
    module.exit_json(**EXIT_DICT)


def delete_meta(module, cf, container, src, dest, meta):
    """ Removes metadata keys and values specified in meta, if any.  Deletes on
    all objects specified by src or dest (but not both), if any; otherwise it
    deletes keys on all objects in the container
    """
    if src and dest:
        module.fail_json(msg="Error: ambiguous instructions; meta keys to be "
                             "deleted have been specified on both src and dest"
                             " args")
    objs = dest or src
    objs = map(str.strip, objs.split(','))

    c = _get_container(module, cf, container)

    try:
        for obj in objs:
            o = c.get_object(obj)
            results = [
                o.remove_metadata_key(k)
                for k in (meta or o.get_metadata())
            ]
    except Exception as e:
        module.fail_json(msg=e.message)

    EXIT_DICT['container'] = c.name
    EXIT_DICT['success'] = True
    if results:
        EXIT_DICT['changed'] = True
        EXIT_DICT['num_deleted'] = len(results)
    module.exit_json(**EXIT_DICT)


def cloudfiles(module, container, src, dest, method, typ, meta, clear_meta,
               structure, expires):
    """ Dispatch from here to work with metadata or file objects """
    cf = pyrax.cloudfiles

    if cf is None:
        module.fail_json(msg='Failed to instantiate client. This '
                             'typically indicates an invalid region or an '
                             'incorrectly capitalized region name.')

    if typ == "file":
        if method == 'get':
            download(module, cf, container, src, dest, structure)

        if method == 'put':
            upload(module, cf, container, src, dest, meta, expires)

        if method == 'delete':
            delete(module, cf, container, src, dest)

    else:
        if method == 'get':
            get_meta(module, cf, container, src, dest)

        if method == 'put':
            put_meta(module, cf, container, src, dest, meta, clear_meta)

        if method == 'delete':
            delete_meta(module, cf, container, src, dest, meta)


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            container=dict(required=True),
            src=dict(),
            dest=dict(),
            method=dict(default='get', choices=['put', 'get', 'delete']),
            type=dict(default='file', choices=['file', 'meta']),
            meta=dict(type='dict', default=dict()),
            clear_meta=dict(default=False, type='bool'),
            structure=dict(default=True, type='bool'),
            expires=dict(type='int'),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together(),
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    container = module.params.get('container')
    src = module.params.get('src')
    dest = module.params.get('dest')
    method = module.params.get('method')
    typ = module.params.get('type')
    meta = module.params.get('meta')
    clear_meta = module.params.get('clear_meta')
    structure = module.params.get('structure')
    expires = module.params.get('expires')

    if clear_meta and not typ == 'meta':
        module.fail_json(msg='clear_meta can only be used when setting metadata')

    setup_rax_module(module, pyrax)
    cloudfiles(module, container, src, dest, method, typ, meta, clear_meta, structure, expires)


if __name__ == '__main__':
    main()
