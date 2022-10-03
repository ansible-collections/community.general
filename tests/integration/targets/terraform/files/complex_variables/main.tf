# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

resource "null_resource" "mynullresource" {
  triggers = {
    # plain dictionaries
    dict_name = var.dictionaries.name
    dict_age  = var.dictionaries.age

    # list of dicrs
    join_dic_name = join(",", var.list_of_objects.*.name)

    # list-of-strings
    join_list = join(",", var.list_of_strings.*)

    # testing boolean
    name = var.boolean ? var.dictionaries.name : var.list_of_objects[0].name

    # top level string
    sample_string_1 = var.string_type

    # nested lists
    num_from_matrix = var.list_of_lists[1][2]
  }

}

output "string_type" {
  value = var.string_type
}

output "multiline_string" {
  value = var.multiline_string
}
