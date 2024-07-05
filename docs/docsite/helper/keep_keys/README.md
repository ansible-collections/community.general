<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Docs helper. Create RST file.

The playbook `playbook.yml` writes a RST file that can be used in
docs/docsite/rst. The usage of this helper is recommended but not
mandatory. You can stop reading here and update the RST file manually
if you don't want to use this helper.

## Run the playbook

If you want to generate the RST file by this helper fit the variables
in the playbook and the template to your needs. Then, run the play

```sh
shell> ansible-playbook playbook.yml
```

## Copy RST to docs/docsite/rst

Copy the RST file to `docs/docsite/rst` and remove it from this
directory.

## Update the checksums

Substitute the variables and run the below commands

```sh
shell> sha1sum {{ target_vars }} > {{ target_sha1 }}
shell> sha1sum {{ file_rst }} > {{ file_sha1 }}
```

## Playbook explained

The playbook includes the variable *tests* from the integration tests
and creates the RST file from the template. The playbook will
terminate if:

* The file with the variable *tests* was changed
* The RST file was changed

This means that this helper is probably not up to date.

### The file with the variable *tests* was changed

This means that somebody updated the integration tests. Review the
changes and update the template if needed. Update the checksum to pass
the integrity test. The playbook message provides you with the
command.

### The RST file was changed

This means that somebody updated the RST file manually. Review the
changes and update the template. Update the checksum to pass the
integrity test. The playbook message provides you with the
command. Make sure that the updated template will create identical RST
file. Only then apply your changes.
