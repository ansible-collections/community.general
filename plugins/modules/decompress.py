import bz2
import filecmp
import gzip
import lzma
import os
import shutil
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def lzma_decompress(src):
    return lzma.open(src, "rb")


def bz2_decompress(src):
    return bz2.open(src, "rb")


def gzip_decompress(src):
    return gzip.open(src, "rb")


def decompress(src, dest, handler):
    with handler(src) as src_file:
        with open(dest, "wb") as dest_file:
            shutil.copyfileobj(src_file, dest_file)


def is_dest_changed(src, dest):
    return not filecmp.cmp(src, dest, shallow=False)


def main():
    result = dict(changed=False, diff=dict(before=dict(), after=dict()))

    compressors = {"gz": gzip_decompress, "bz2": bz2_decompress, "xz": lzma_decompress}

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path', required=True),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz']),
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )

    src = module.params['src']
    dest = module.params['dest']
    if not os.path.exists(src):
        module.fail_json(msg="Path does not exist: '%s'" % src)
    if os.path.isdir(src):
        module.fail_json(msg="Cannot decompress directory '%s'" % src)
    if os.path.exists(dest) and os.path.isdir(dest):
        module.fail_json(msg="Destination is a directory, cannot decompress: '%s'" % dest)
    format = module.params['format']
    if format not in compressors:
        module.fail_json(msg=f"Couldn't decompress '%s' format." % format)
    dest = os.path.abspath(dest)

    file_args = module.load_file_common_arguments(module.params, path=dest)
    handler = compressors[format]
    try:
        tempd, temppath = tempfile.mkstemp(dir=module.tmpdir)
        decompress(src, tempd, handler)
    except OSError as e:
        module.fail_json(msg="Unable to create temporary file '%s'" % to_native(e))

    if os.path.exists(dest):
        changed = is_dest_changed(temppath, dest)
    else:
        changed = True
    if changed and not module.check_mode:
        try:
            module.atomic_move(temppath, dest)
        except OSError:
            module.fail_json(msg="Unable to move temporary file '%s' to '%s'" % (temppath, dest))

    if os.path.exists(temppath):
        os.unlink(temppath)
    result['msg'] = 'success'
    result['changed'] = module.set_fs_attributes_if_different(file_args, changed)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
