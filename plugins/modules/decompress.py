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
    @abc.abstractmethod
    def decompress(self, src, dest):
        pass


class GzDecompress(Decompress):
    def decompress(self, src, dest):
        with gzip.open(src, "rb") as src_file:
            with open(dest, "wb") as dest_file:
                shutil.copyfileobj(src_file, dest_file)


class Bz2Decompress(Decompress):

    def decompress(self, src, dest):
        with bz2.open(src, "rb") as src_file:
            with open(dest, "wb") as dest_file:
                shutil.copyfileobj(src_file, dest_file)


class LZMADecompress(Decompress):

    def decompress(self, src, dest):
        with lzma.open(src, "rb") as src_file:
            with open(dest, "wb") as dest_file:
                shutil.copyfileobj(src_file, dest_file)


def main():
    result = dict(changed=False, diff=dict(before=dict(), after=dict()))

    compressors = {"gz": GzDecompress, "bz2": Bz2Decompress, "xz": LZMADecompress}

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='str', required=True),
            dest=dict(type='str', required=True),
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
