import abc
import bz2
import filecmp
import gzip
import lzma
import os
import shutil
import tempfile

from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


@six.add_metaclass(abc.ABCMeta)
class Decompress(abc.ABC):
    def decompress(self, src, dest):
        with self._compression_file(src) as src_file:
            with open(dest, "wb") as dest_file:
                shutil.copyfileobj(src_file, dest_file)

    @abc.abstractmethod
    def _compression_file(self, src):
        pass


class GzDecompress(Decompress):
    def _compression_file(self, src):
        return gzip.open(src, "rb")


class Bz2Decompress(Decompress):

    def _compression_file(self, src):
        return bz2.open(src, "rb")


class LZMADecompress(Decompress):
    def _compression_file(self, src):
        return lzma.open(src, "rb")


def is_dest_changed(src, dest):
    return not filecmp.cmp(src, dest, shallow=False)


def main():
    result = dict(changed=False, diff=dict(before=dict(), after=dict()))

    compressors = {"gz": GzDecompress, "bz2": Bz2Decompress, "xz": LZMADecompress}

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path', required=True),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz']),
        ),
        add_file_common_args=True
    )

    src = module.params['src']
    if not os.path.exists(src):
        module.fail_json(msg="Path does not exist: %s" % src)
    dest = module.params['dest']
    format = module.params['format']
    dest = os.path.abspath(dest)

    file_args = module.load_file_common_arguments(module.params, path=dest)
    compressor = compressors[format]
    if compressor is None:
        module.fail_json(msg=f"Couldn't decompress '{format}' format.")

    obj = compressor()
    try:
        tempd, temppath = tempfile.mkstemp(dir=module.tmpdir)
        obj.decompress(src, tempd)
    except OSError as e:
        module.fail_json(msg="Unable to create temporary file %s" % to_native(e))

    if os.path.exists(dest):
        changed = is_dest_changed(temppath, dest)
    else:
        changed = True
    if changed:
        try:
            module.atomic_move(temppath, dest)
        except OSError:
            module.fail_json(msg="Unable to move temporary file %s to %s" % (temppath, dest))

    if os.path.exists(temppath):
        os.unlink(temppath)
    result['msg'] = 'success'
    result['changed'] = module.set_fs_attributes_if_different(file_args, changed)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
