import abc
import bz2
import gzip
import lzma
import os
import shutil

from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule


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


def main():
    result = dict(changed=False, diff=dict(before=dict(), after=dict()))

    compressors = {"gz": GzDecompress, "bz2": Bz2Decompress, "xz": LZMADecompress}

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path', required=True),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz'])
        )
    )

    src = module.params['src']
    dest = module.params['dest']
    format = module.params['format']

    src = os.path.abspath(src)
    dest = os.path.abspath(dest)

    compressor = compressors[format]

    if compressor is not None:
        obj = compressor()
        obj.decompress(src, dest)
        result['msg'] = 'success'
        module.exit_json(**result)
    else:
        module.fail_json(msg="Compressor not found.")


if __name__ == '__main__':
    main()
