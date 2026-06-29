#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


def fake_xenapi_ref(xenapi_class):
    return f"OpaqueRef:fake-xenapi-{xenapi_class}-ref"


testcase_bad_xenapi_refs = {
    "params": [
        None,
        "",
        "OpaqueRef:NULL",
    ],
    "ids": [
        "none",
        "empty",
        "ref-null",
    ],
}
