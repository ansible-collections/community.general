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
* All commits of a pull request branch will be squashed into one commit at last. That does not mean you must have only one commit on your pull request, though!
* Please try not to force-push if it is not needed, so reviewers and other users looking at your pull request later can see the pull request commit history.
* Do not add merge commits to your PR. The bot will complain and you will have to rebase ([instructions for rebasing](https://docs.ansible.com/ansible/latest/dev_guide/developing_rebasing.html)) to remove them before your PR can be merged. To avoid that git automatically does merges during pulls, you can configure it to do rebases instead by running `git config pull.rebase true` inside the respository checkout.

You can also read [our Quick-start development guide](https://github.com/ansible/community-docs/blob/main/create_pr_quick_start_guide.rst).

## Test pull requests

If you want to test a PR locally, refer to [our testing guide](https://github.com/ansible/community-docs/blob/main/test_pr_locally_guide.rst) for instructions on how do it quickly.

If you find any inconsistencies or places in this document which can be improved, feel free to raise an issue or pull request to fix it.
