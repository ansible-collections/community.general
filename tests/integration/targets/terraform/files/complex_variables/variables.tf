# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

variable "dictionaries" {
  type = object({
    name = string
    age  = number
  })
  description = "Same as ansible Dict"
  default = {
    age = 1
    name = "value"
  }
}

variable "list_of_strings" {
  type        = list(string)
  description = "list of strings"
}

variable "list_of_objects" {
  type = list(object({
    name = string
    age  = number
  }))

}

variable "boolean" {
  type        = bool
  description = "boolean"

}

variable "string_type" {
  type = string
  validation {
    condition     = (var.string_type == "randomstring2\"&$%@")
    error_message = "Strings do not match."
  }
  default = "randomstring2\"&$%@"
}

variable "list_of_lists" {
  type = list(list(any))
  default = [ [ 1 ], [1, 2, 3], [3] ]
}
