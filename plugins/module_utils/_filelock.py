# Copyright (c) 2018, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

# NOTE:
# This has been vendored from ansible.module_utils.common.file. This code has been removed from there for ansible-core 2.16.

from __future__ import annotations

import os
import stat
import time
import fcntl

from contextlib import contextmanager


class LockTimeout(Exception):
    pass


class FileLock:
    """
    Currently FileLock is implemented via fcntl.flock on a lock file, however this
    behaviour may change in the future. Avoid mixing lock types fcntl.flock,
    fcntl.lockf and module_utils.common.file.FileLock as it will certainly cause
    unwanted and/or unexpected behaviour
    """

    def __init__(self):
        self.lockfd = None

    @contextmanager
    def lock_file(self, path, tmpdir, lock_timeout=None):
        """
        Context for lock acquisition
        """
        try:
            self.set_lock(path, tmpdir, lock_timeout)
            yield
        finally:
            self.unlock()

    def set_lock(self, path, tmpdir, lock_timeout=None):
        """
        Create a lock file based on path with flock to prevent other processes
        using given path.
        Please note that currently file locking only works when it is executed by
        the same user, for example single user scenarios

        :kw path: Path (file) to lock
        :kw tmpdir: Path where to place the temporary .lock file
        :kw lock_timeout:
            Wait n seconds for lock acquisition, fail if timeout is reached.
            0 = Do not wait, fail if lock cannot be acquired immediately,
            Default is None, wait indefinitely until lock is released.
        :returns: True
        """
        lock_path = os.path.join(tmpdir, f"ansible-{os.path.basename(path)}.lock")
        l_wait = 0.1

        self.lockfd = open(lock_path, "w")

        if lock_timeout <= 0:
            fcntl.flock(self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.chmod(lock_path, stat.S_IWRITE | stat.S_IREAD)
            return True

        if lock_timeout:
            e_secs = 0
            while e_secs < lock_timeout:
                try:
                    fcntl.flock(self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    os.chmod(lock_path, stat.S_IWRITE | stat.S_IREAD)
                    return True
                except BlockingIOError:
                    time.sleep(l_wait)
                    e_secs += l_wait
                    continue

            self.lockfd.close()
            raise LockTimeout(f"{lock_timeout} sec")

        fcntl.flock(self.lockfd, fcntl.LOCK_EX)
        os.chmod(lock_path, stat.S_IWRITE | stat.S_IREAD)

        return True

    def unlock(self):
        """
        Make sure lock file is available for everyone and Unlock the file descriptor
        locked by set_lock

        :returns: True
        """
        if not self.lockfd:
            return True

        try:
            fcntl.flock(self.lockfd, fcntl.LOCK_UN)
            self.lockfd.close()
        except ValueError:  # file wasn't opened, let context manager fail gracefully
            pass

        return True
