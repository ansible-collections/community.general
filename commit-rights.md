<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

Committers Guidelines for community.general
===========================================

This document is based on the [Ansible committer guidelines](https://github.com/ansible/ansible/blob/b57444af14062ec96e0af75fdfc2098c74fe2d9a/docs/docsite/rst/community/committer_guidelines.rst) ([latest version](https://docs.ansible.com/ansible/devel/community/committer_guidelines.html)).

These are the guidelines for people with commit privileges on the Ansible Community General Collection GitHub repository. Please read the guidelines before you commit.

These guidelines apply to everyone. At the same time, this is NOT a process document. So just use good judgment. You have been given commit access because we trust your judgment.

That said, use the trust wisely.

If you abuse the trust and break components and builds, and so on, the trust level falls and you may be asked not to commit or you may lose your commit privileges.

Our workflow on GitHub
----------------------

As a committer, you may already know this, but our workflow forms a lot of our team policies. Please ensure you are aware of the following workflow steps:

* Fork the repository upon which you want to do some work to your own personal repository
* Work on the specific branch upon which you need to commit
* Create a Pull Request back to the collection repository and await reviews
* Adjust code as necessary based on the Comments provided
* Ask someone from the other committers to do a final review and merge

Sometimes, committers merge their own pull requests. This section is a set of guidelines. If you are changing a comma in a doc or making a very minor change, you can use your best judgement. This is another trust thing. The process is critical for any major change, but for little things or getting something done quickly, use your best judgement and make sure people on the team are aware of your work.

Roles
-----
* Release managers: Merge pull requests to `stable-X` branches, create tags to do releases.
* Committers: Fine to do PRs for most things, but we should have a timebox. Hanging PRs may merge on the judgement of these devs.
* Module maintainers: Module maintainers own specific modules and have indirect commit access through the current module PR mechanisms. This is primary [ansibullbot](https://github.com/ansibullbot)'s `shipit` mechanism.

General rules
-------------
Individuals with direct commit access to this collection repository are entrusted with powers that allow them to do a broad variety of things--probably more than we can write down. Rather than rules, treat these as general *guidelines*, individuals with this power are expected to use their best judgement.

* Do NOTs:

  - Do not commit directly.
  - Do not merge your own PRs. Someone else should have a chance to review and approve the PR merge. You have a small amount of leeway here for very minor changes.
  - Do not forget about non-standard / alternate environments. Consider the alternatives. Yes, people have bad/unusual/strange environments (like binaries from multiple init systems installed), but they are the ones who need us the most.
  - Do not drag your community team members down. Discuss the technical merits of any pull requests you review. Avoid negativity and personal comments. For more guidance on being a good community member, read the [Ansible Community Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).
  - Do not forget about the maintenance burden. High-maintenance features may not be worth adding.
  - Do not break playbooks. Always keep backwards compatibility in mind.
  - Do not forget to keep it simple. Complexity breeds all kinds of problems.
  - Do not merge to branches other than `main`, especially not to `stable-X`, if you do not have explicit permission to do so.
  - Do not create tags. Tags are used in the release process, and should only be created by the people responsible for managing the stable branches.

* Do:

  - Squash, avoid merges whenever possible, use GitHub's squash commits or cherry pick if needed (bisect thanks you).
  - Be active. Committers who have no activity on the project (through merges, triage, commits, and so on) will have their permissions suspended.
  - Consider backwards compatibility (goes back to "do not break existing playbooks").
  - Write tests. PRs with tests are looked at with more priority than PRs without tests that should have them included. While not all changes require tests, be sure to add them for bug fixes or functionality changes.
  - Discuss with other committers, specially when you are unsure of something.
  - Document! If your PR is a new feature or a change to behavior, make sure you've updated all associated documentation or have notified the right people to do so.
  - Consider scope, sometimes a fix can be generalized.
  - Keep it simple, then things are maintainable, debuggable and intelligible.

Committers are expected to continue to follow the same community and contribution guidelines followed by the rest of the Ansible community.


People
------

Individuals who have been asked to become a part of this group have generally been contributing in significant ways to the community.general collection for some time. Should they agree, they are requested to add their names and GitHub IDs to this file, in the section below, through a pull request. Doing so indicates that these individuals agree to act in the ways that their fellow committers trust that they will act.

| Name                | GitHub ID            | IRC Nick           | Other                |
| ------------------- | -------------------- | ------------------ | -------------------- |
| Alexei Znamensky    | russoz               | russoz             |                      |
| Andrew Klychkov     | andersson007         | andersson007_      |                      |
| Andrew Pantuso      | Ajpantuso            | ajpantuso          |                      |
| Felix Fontein       | felixfontein         | felixfontein       |                      |
| John R Barker       | gundalow             | gundalow           |                      |
