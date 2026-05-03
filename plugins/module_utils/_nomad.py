# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils import _deps as deps

nomad: t.Any = None
with deps.declare("python-nomad"):
    import nomad  # type: ignore[no-redef]

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

argument_spec = dict(
    host=dict(required=True, type="str"),
    port=dict(type="int", default=4646),
    use_ssl=dict(type="bool", default=True),
    timeout=dict(type="int", default=5),
    validate_certs=dict(type="bool", default=True),
    client_cert=dict(type="path"),
    client_key=dict(type="path"),
    namespace=dict(type="str"),
    token=dict(type="str", no_log=True),
)


def setup_nomad_client(module: AnsibleModule) -> nomad.Nomad:
    deps.validate(module)

    certificate_ssl = (module.params["client_cert"], module.params["client_key"])

    return nomad.Nomad(
        host=module.params["host"],
        port=module.params["port"],
        secure=module.params["use_ssl"],
        timeout=module.params["timeout"],
        verify=module.params["validate_certs"],
        cert=certificate_ssl,
        namespace=module.params["namespace"],
        token=module.params["token"],
    )
