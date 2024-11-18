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


class Decompress(object):
    def __init__(self, module):
        self.src = module.params['src']
        self.dest = module.params['dest']
        self.fmt = module.params['format']
        self.check_mode = module.check_mode
        self.module = module
        self.changed = False
        self.msg = ""
        self.handlers = {"gz": gzip_decompress, "bz2": bz2_decompress, "xz": lzma_decompress}

    def configure(self):
        if not os.path.exists(self.src):
            self.module.fail_json(msg="Path does not exist: '%s'" % self.src)
        if os.path.isdir(self.src):
            self.module.fail_json(msg="Cannot decompress directory '%s'" % self.src)
        if os.path.exists(self.dest) and os.path.isdir(self.dest):
            self.module.fail_json(msg="Destination is a directory, cannot decompress: '%s'" % self.dest)
        self.fmt = self.module.params['format']
        if self.fmt not in self.handlers:
            self.module.fail_json(msg="Couldn't decompress '%s' format" % self.fmt)

    def run(self):
        self.configure()
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.dest)
        handler = self.handlers[self.fmt]
        try:
            tempfd, temppath = tempfile.mkstemp(dir=self.module.tmpdir)
            decompress(self.src, tempfd, handler)
        except OSError as e:
            self.module.fail_json(msg="Unable to create temporary file '%s'" % to_native(e))

        if os.path.exists(self.dest):
            self.changed = not filecmp.cmp(temppath, self.dest, shallow=False)
        else:
            self.changed = True

        if self.changed and not self.module.check_mode:
            try:
                self.module.atomic_move(temppath, self.dest)
            except OSError:
                self.module.fail_json(msg="Unable to move temporary file '%s' to '%s'" % (temppath, self.dest))

        if os.path.exists(temppath):
            os.unlink(temppath)

        self.msg = "success"
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path', required=True),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz']),
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )
    d = Decompress(module)
    d.run()

    module.exit_json(changed=d.changed, msg=d.msg)


if __name__ == '__main__':
    main()
