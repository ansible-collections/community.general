<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Contributing

We follow [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our contributions and interactions within this repository.

If you are a committer, also refer to the [collection's committer guidelines](https://github.com/ansible-collections/community.general/blob/main/commit-rights.md).

## Issue tracker

Whether you are looking for an opportunity to contribute or you found a bug and already know how to solve it, please go to the [issue tracker](https://github.com/ansible-collections/community.general/issues).
There you can find feature ideas to implement, reports about bugs to solve, or submit an issue to discuss your idea before implementing it which can help choose a right direction at the beginning of your work and potentially save a lot of time and effort.
Also somebody may already have started discussing or working on implementing the same or a similar idea,
so you can cooperate to create a better solution together.

* If you are interested in starting with an easy issue, look for [issues with an `easyfix` label](https://github.com/ansible-collections/community.general/labels/easyfix).
* Often issues that are waiting for contributors to pick up have [the `waiting_on_contributor` label](https://github.com/ansible-collections/community.general/labels/waiting_on_contributor).

## Open pull requests

Look through currently [open pull requests](https://github.com/ansible-collections/community.general/pulls).
You can help by reviewing them. Reviews help move pull requests to merge state. Some good pull requests cannot be merged only due to a lack of reviews. And it is always worth saying that good reviews are often more valuable than pull requests themselves.
Note that reviewing does not only mean code review, but also offering comments on new interfaces added to existing plugins/modules, interfaces of new plugins/modules, improving language (not everyone is a native english speaker), or testing bugfixes and new features!

Also, consider taking up a valuable, reviewed, but abandoned pull request which you could politely ask the original authors to complete yourself.

* Try committing your changes with an informative but short commit message.
* Do not squash your commits and force-push to your branch if not needed. Reviews of your pull request are much easier with individual commits to comprehend the pull request history. All commits of your pull request branch will be squashed into one commit by GitHub upon merge.
* Do not add merge commits to your PR. The bot will complain and you will have to rebase ([instructions for rebasing](https://docs.ansible.com/ansible/latest/dev_guide/developing_rebasing.html)) to remove them before your PR can be merged. To avoid that git automatically does merges during pulls, you can configure it to do rebases instead by running `git config pull.rebase true` inside the repository checkout.
* Make sure your PR includes a [changelog fragment](https://docs.ansible.com/ansible/devel/community/collection_development_process.html#creating-a-changelog-fragment).
  * You must not include a fragment for new modules or new plugins. Also you shouldn't include one for docs-only changes. (If you're not sure, simply don't include one, we'll tell you whether one is needed or not :) )
  * Please always include a link to the pull request itself, and if the PR is about an issue, also a link to the issue. Also make sure the fragment ends with a period, and begins with a lower-case letter after `-`. (Again, if you don't do this, we'll add suggestions to fix it, so don't worry too much :) )
* Avoid reformatting unrelated parts of the codebase in your PR. These types of changes will likely be requested for reversion, create additional work for reviewers, and may cause approval to be delayed.

You can also read [our Quick-start development guide](https://github.com/ansible/community-docs/blob/main/create_pr_quick_start_guide.rst).

## Test pull requests

If you want to test a PR locally, refer to [our testing guide](https://github.com/ansible/community-docs/blob/main/test_pr_locally_guide.rst) for instructions on how do it quickly.

If you find any inconsistencies or places in this document which can be improved, feel free to raise an issue or pull request to fix it.

## Run sanity, unit or integration tests locally

You have to check out the repository into a specific path structure to be able to run `ansible-test`. The path to the git checkout must end with `.../ansible_collections/community/general`. Please see [our testing guide](https://github.com/ansible/community-docs/blob/main/test_pr_locally_guide.rst) for instructions on how to check out the repository into a correct path structure. The short version of these instructions is:

```.bash
mkdir -p ~/dev/ansible_collections/community
git clone https://github.com/ansible-collections/community.general.git ~/dev/ansible_collections/community/general
cd ~/dev/ansible_collections/community/general
```

Then you can run `ansible-test` (which is a part of [ansible-core](https://pypi.org/project/ansible-core/)) inside the checkout. The following example commands expect that you have installed Docker or Podman. Note that Podman has only been supported by more recent ansible-core releases. If you are using Docker, the following will work with Ansible 2.9+.

The following commands show how to run sanity tests:

```.bash
# Run sanity tests for all files in the collection:
ansible-test sanity --docker -v

# Run sanity tests for the given files and directories:
ansible-test sanity --docker -v plugins/modules/system/pids.py tests/integration/targets/pids/
```

The following commands show how to run unit tests:

```.bash
# Run all unit tests:
ansible-test units --docker -v

# Run all unit tests for one Python version (a lot faster):
ansible-test units --docker -v --python 3.8

# Run a specific unit test (for the nmcli module) for one Python version:
ansible-test units --docker -v --python 3.8 tests/unit/plugins/modules/net_tools/test_nmcli.py
```

The following commands show how to run integration tests:

```.bash
# Run integration tests for the interfaces_files module in a Docker container using the
# fedora35 operating system image (the supported images depend on your ansible-core version):
ansible-test integration --docker fedora35 -v interfaces_file

# Run integration tests for the flattened lookup **without any isolation**:
ansible-test integration -v lookup_flattened
```

If you are unsure about the integration test target name for a module or plugin, you can take a look in `tests/integration/targets/`. Tests for plugins have the plugin type prepended.

## Creating new modules or plugins

Creating new modules and plugins requires a bit more work than other Pull Requests.

1. Please make sure that your new module or plugin is of interest to a larger audience. Very specialized modules or plugins that
   can only be used by very few people should better be added to more specialized collections.

2. Please do not add more than one plugin/module in one PR, especially if it is the first plugin/module you are contributing.
   That makes it easier for reviewers, and increases the chance that your PR will get merged. If you plan to contribute a group
   of plugins/modules (say, more than a module and a corresponding ``_info`` module), please mention that in the first PR. In
   such cases, you also have to think whether it is better to publish the group of plugins/modules in a new collection.

3. When creating a new module or plugin, please make sure that you follow various guidelines:

   - Follow [development conventions](https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_best_practices.html);
   - Follow [documentation standards](https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html) and
     the [Ansible style guide](https://docs.ansible.com/ansible/devel/dev_guide/style_guide/index.html#style-guide);
   - Make sure your modules and plugins are [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0-standalone.html) licensed
     (new module_utils can also be [BSD-2-clause](https://opensource.org/licenses/BSD-2-Clause) licensed);
   - Make sure that new plugins and modules have tests (unit tests, integration tests, or both); it is preferable to have some tests
     which run in CI.

4. Action plugins need to be accompanied by a module, even if the module file only contains documentation
   (`DOCUMENTATION`, `EXAMPLES` and `RETURN`). The module must have the same name and directory path in `plugins/modules/`
   than the action plugin has in `plugins/action/`.

5. Make sure to add a BOTMETA entry for your new module/plugin in `.github/BOTMETA.yml`. Search for other plugins/modules in the
   same directory to see how entries could look. You should list all authors either as `maintainers` or under `ignore`. People
   listed as `maintainers` will be pinged for new issues and PRs that modify the module/plugin or its tests.

   When you add a new plugin/module, we expect that you perform maintainer duty for at least some time after contributing it.
