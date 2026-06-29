<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Cleaning up `aliases` skips

The skip statements in `tests/integration/targets/*/aliases` files may contain specific OSes and their versions.

For example:

    skip/rhel8.8
    skip/centos6
    skip/macos

Those items being skipped are called `remotes` and they come from the file `test/lib/ansible_test/_data/completion/remote.txt`
in the `ansible-core` repository. Eventually, these remotes are removed from that `ansible_test` config,
but they keep silently cluttering the aliases files here.

The scripts `list-remotes` and `clean-aliases-skips` can help you remove those entries from the `aliases` files.
For that, you will need to have a clone of the `ansible-core` repository in your machine.

In the example below, the path to that repo is `../ansible`:

```shell
./tests/utils/list-remotes ../ansible
```

**Note:** The supported versions of `ansible-core` are hardcoded in `list-remotes`. Those should be updated or automated in the future.

To remove all the skips that are **not** in that list, you should run:

```shell
./tests/utils/list-remotes ../ansible | ./tests/utils/clean-aliases-skips
```

Make sure to thoroughly review the changes before committing!
