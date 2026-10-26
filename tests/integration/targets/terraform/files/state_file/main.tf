# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

variable "second" {
  type    = bool
  default = false
}

resource "null_resource" "first" {}

resource "null_resource" "second" {
  count = var.second ? 1 : 0
}
