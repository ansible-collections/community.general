<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Docs helper. Create RST file.

The playbook `playbook.yml` writes a RST file that can be used in
docs/docsite/rst.

## Configure COLLECTIONS_PATHS

Configure COLLECTIONS_PATHS to point to your development copy. For example, in
the configuration file

```ini
shell> grep collections_path ansible.cfg 
collections_path = /scratch/collections/
```
See:
* [Prepare your environment](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_test_pr_locally.html#prepare-your-environment)
* [Test the Pull Request](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_test_pr_locally.html#test-the-pull-request) point 1.

## Run the playbook

See the playbook. Fit the variables and the template to your
needs. Then, run the play

```yaml
ansible-playbook playbook.yml
```

## Copy RST to docs/docsite/rst

Copy the RST file to `docs/docsite/rst`

## Create collection docsite

Create the collection docsite and proofread your chapter. See
[Creating a collection docsite](https://ansible.readthedocs.io/projects/antsibull-docs/collection-docs/)

## .gitignore

Recommended .gitignore in this directory

```bash
shell> cat .gitignore 
*~
\#*
.gitignore
*.rst
```
