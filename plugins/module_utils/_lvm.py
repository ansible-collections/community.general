# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


# Options shared by the reporting commands: pvs, vgs, lvs (and pvdisplay in column mode).
_REPORT_ARG_FORMATS = dict(
    noheadings=cmd_runner_fmt.as_fixed("--noheadings"),
    nosuffix=cmd_runner_fmt.as_fixed("--nosuffix"),
    readonly=cmd_runner_fmt.as_fixed("--readonly"),
    units=cmd_runner_fmt.as_opt_val("--units"),
    separator=cmd_runner_fmt.as_opt_val("--separator"),
    fields=cmd_runner_fmt.as_opt_val("-o"),
    select=cmd_runner_fmt.as_opt_val("--select"),
)


# ---- PV commands ----


def pvs_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvs). Used by: community.general.lvg, community.general.lvm_pv,
    community.general.lvm_pv_move_data, community.general.lvg_rename,
    community.general.filesystem.

    Suggested arg_formats keys: noheadings nosuffix readonly units separator fields select devices
    """
    return CmdRunner(
        module,
        command="pvs",
        arg_formats=dict(
            **_REPORT_ARG_FORMATS,
            devices=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvcreate_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvcreate). Used by: community.general.lvg, community.general.lvm_pv,
    community.general.filesystem.

    Suggested arg_formats keys: pv_options force yes device

    Note: C(pv_options) accepts a pre-split list (e.g. from C(shlex.split())).
    """
    return CmdRunner(
        module,
        command="pvcreate",
        arg_formats=dict(
            pv_options=cmd_runner_fmt.as_list(),
            force=cmd_runner_fmt.as_bool("-f"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            device=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvchange_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvchange). Used by: community.general.lvg, community.general.filesystem.

    Suggested arg_formats keys: uuid yes device
    """
    return CmdRunner(
        module,
        command="pvchange",
        arg_formats=dict(
            uuid=cmd_runner_fmt.as_bool("-u"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            device=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvresize_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvresize). Used by: community.general.lvg, community.general.lvm_pv,
    community.general.filesystem.

    Suggested arg_formats keys: set_size device
    """
    return CmdRunner(
        module,
        command="pvresize",
        arg_formats=dict(
            set_size=cmd_runner_fmt.as_opt_val("--setphysicalvolumesize"),
            device=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvremove_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvremove). Used by: community.general.lvm_pv.

    Suggested arg_formats keys: force device

    Note: C(-y) is always passed (non-interactive). C(force=True) passes C(-ff),
    which removes PVs even when part of a VG.
    """
    return CmdRunner(
        module,
        command=["pvremove", "-y"],
        arg_formats=dict(
            force=cmd_runner_fmt.as_bool("-ff"),
            device=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvdisplay_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvdisplay). Used by: community.general.lvg.

    Enables machine-readable output via C(--columns). Fields such as C(dev_size),
    C(pe_start), and C(vg_extent_size) are only available through C(pvdisplay),
    not C(pvs).

    Suggested arg_formats keys: columns noheadings nosuffix units separator fields device
    """
    return CmdRunner(
        module,
        command="pvdisplay",
        arg_formats=dict(
            columns=cmd_runner_fmt.as_fixed("--columns"),
            **_REPORT_ARG_FORMATS,
            device=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def pvmove_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(pvmove). Used by: community.general.lvm_pv_move_data.

    Suggested arg_formats keys: auto_answer atomic autobackup verbosity source destination

    Note: C(auto_answer) matches the O(auto_answer) module parameter.
    Pass C(autobackup) as a boolean; it maps to C(--autobackup y/n).
    """
    return CmdRunner(
        module,
        command="pvmove",
        arg_formats=dict(
            auto_answer=cmd_runner_fmt.as_bool("-y"),
            atomic=cmd_runner_fmt.as_bool("--atomic"),
            autobackup=cmd_runner_fmt.as_bool(["--autobackup", "y"], ["--autobackup", "n"], ignore_none=False),
            verbosity=cmd_runner_fmt.as_func(lambda v: [f"-{'v' * v}"] if v > 0 else []),
            source=cmd_runner_fmt.as_list(),
            destination=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


# ---- VG commands ----


def vgs_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgs). Used by: community.general.lvol, community.general.lvg,
    community.general.lvg_rename.

    Suggested arg_formats keys: noheadings nosuffix readonly units separator fields select vg
    """
    return CmdRunner(
        module,
        command="vgs",
        arg_formats=dict(
            **_REPORT_ARG_FORMATS,
            vg=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgcreate_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgcreate). Used by: community.general.lvg.

    Suggested args order: vg_options pesize setautoactivation vg pvs

    Note: C(vg) and C(pvs) are positional — C(vg) must appear before C(pvs)
    in the args_order string. C(pvs) matches the O(pvs) module parameter in
    community.general.lvg. C(vg_options) accepts a pre-split list (e.g. from
    C(shlex.split())). C(setautoactivation) accepts C(True)/C(False)/C(None);
    C(None) omits the flag entirely (C(ignore_none=True)).
    """
    return CmdRunner(
        module,
        command="vgcreate",
        arg_formats=dict(
            vg_options=cmd_runner_fmt.as_list(),
            pesize=cmd_runner_fmt.as_opt_val("-s"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            setautoactivation=cmd_runner_fmt.as_bool(
                ["--setautoactivation", "y"],
                ["--setautoactivation", "n"],
                ignore_none=True,
            ),
            vg=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgchange_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgchange). Used by: community.general.lvg, community.general.lvg_rename.

    Suggested arg_formats keys: activate uuid setautoactivation help vg

    Note: C(activate) and C(setautoactivation) are passed as booleans and map to
    C(--activate y/n) and C(--setautoactivation y/n) respectively.
    """
    return CmdRunner(
        module,
        command="vgchange",
        arg_formats=dict(
            activate=cmd_runner_fmt.as_bool(
                ["--activate", "y"],
                ["--activate", "n"],
                ignore_none=False,
            ),
            uuid=cmd_runner_fmt.as_bool("-u"),
            setautoactivation=cmd_runner_fmt.as_bool(
                ["--setautoactivation", "y"],
                ["--setautoactivation", "n"],
                ignore_none=False,
            ),
            help=cmd_runner_fmt.as_fixed("--help"),
            vg=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgextend_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgextend). Used by: community.general.lvg.

    Suggested args order: vg pvs

    Note: C(vg) must appear before C(pvs) in the args_order string.
    C(pvs) matches the O(pvs) module parameter in community.general.lvg,
    but callers must pass the subset of PVs to add explicitly.
    """
    return CmdRunner(
        module,
        command="vgextend",
        arg_formats=dict(
            vg=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgreduce_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgreduce). Used by: community.general.lvg.

    Suggested args order: force vg pvs

    Note: C(vg) must appear before C(pvs) in the args_order string.
    C(pvs) matches the O(pvs) module parameter in community.general.lvg,
    but callers must pass the subset of PVs to remove explicitly.
    """
    return CmdRunner(
        module,
        command="vgreduce",
        arg_formats=dict(
            force=cmd_runner_fmt.as_bool("--force"),
            vg=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgremove_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgremove). Used by: community.general.lvg.

    Suggested arg_formats keys: force yes vg
    """
    return CmdRunner(
        module,
        command="vgremove",
        arg_formats=dict(
            force=cmd_runner_fmt.as_bool("--force"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            vg=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def vgrename_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(vgrename). Used by: community.general.lvg_rename.

    Suggested args order: vg vg_new

    Note: C(vg) (old name or UUID) must appear before C(vg_new) in the args_order string.
    """
    return CmdRunner(
        module,
        command="vgrename",
        arg_formats=dict(
            vg=cmd_runner_fmt.as_list(),
            vg_new=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


# ---- LV commands ----


def lvs_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvs). Used by: community.general.lvol.

    Suggested arg_formats keys: all noheadings nosuffix units separator fields select vg

    Note: C(all) includes hidden internal LVs such as thin pool metadata.
    """
    return CmdRunner(
        module,
        command="lvs",
        arg_formats=dict(
            all=cmd_runner_fmt.as_fixed("-a"),
            **_REPORT_ARG_FORMATS,
            vg=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def lvcreate_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvcreate). Used by: community.general.lvol, community.general.lxc_container.

    Suggested args order (normal LV): test yes lv size_L vg pvs
    Suggested args order (snapshot):  test yes size_L is_snapshot lv vg
    Suggested args order (thin pool): test yes lv size_L thin vg pvs
    Suggested args order (thin vol):  test yes lv size_V thin vg

    Note: C(vg) must appear after all option args and before C(pvs).
    For snapshots and thin volumes, pass the origin as C(vg="{vg}/{lv}").

    Intentional mismatches with module parameters:
    - C(lv) matches O(lv) in community.general.lvol (the LV name, passed as C(-n lv)).
    - C(is_snapshot) is a boolean flag for C(-s); it differs from the O(snapshot)
      module parameter, which is a string holding the snapshot name.
    - C(thin) is a boolean flag for C(-T); it differs from the O(thinpool)
      module parameter, which is the pool name string.
    - C(size_L), C(size_l), C(size_V) cannot match the O(size) module parameter
      because one module param maps to three distinct CLI size options; callers
      must always pass the appropriate size key explicitly.
    - C(pvs) matches O(pvs) in community.general.lvol; callers must pass the value
      explicitly since it is the list of PV paths, not the full module param value.
    """
    return CmdRunner(
        module,
        command="lvcreate",
        arg_formats=dict(
            test=cmd_runner_fmt.as_bool("--test"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            lv=cmd_runner_fmt.as_opt_val("-n"),
            size_L=cmd_runner_fmt.as_opt_val("-L"),
            size_l=cmd_runner_fmt.as_opt_val("-l"),
            size_V=cmd_runner_fmt.as_opt_val("-V"),
            is_snapshot=cmd_runner_fmt.as_bool("-s"),
            thin=cmd_runner_fmt.as_fixed("-T"),
            vg=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def lvchange_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvchange). Used by: community.general.lvol.

    Suggested arg_formats keys: active lv

    Note: C(active) matches the O(active) module parameter in community.general.lvol.
    It maps to C(-ay) when true and C(-an) when false.
    """
    return CmdRunner(
        module,
        command="lvchange",
        arg_formats=dict(
            active=cmd_runner_fmt.as_bool("-ay", "-an", ignore_none=False),
            lv=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def lvextend_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvextend). Used by: community.general.lvol.

    Suggested args order: test resizefs size_L lv pvs
    (use size_l instead of size_L when sizing by extents or percentage)

    Note: C(lv) must appear before C(pvs) in the args_order string.
    C(pvs) matches the O(pvs) module parameter in community.general.lvol.
    """
    return CmdRunner(
        module,
        command="lvextend",
        arg_formats=dict(
            test=cmd_runner_fmt.as_bool("--test"),
            resizefs=cmd_runner_fmt.as_bool("--resizefs"),
            size_L=cmd_runner_fmt.as_opt_val("-L"),
            size_l=cmd_runner_fmt.as_opt_val("-l"),
            lv=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def lvreduce_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvreduce). Used by: community.general.lvol.

    Suggested args order: test force resizefs size_L lv pvs
    (use size_l instead of size_L when sizing by extents or percentage)

    Note: C(lv) must appear before C(pvs) in the args_order string.
    C(pvs) matches the O(pvs) module parameter in community.general.lvol.
    """
    return CmdRunner(
        module,
        command="lvreduce",
        arg_formats=dict(
            test=cmd_runner_fmt.as_bool("--test"),
            force=cmd_runner_fmt.as_bool("--force"),
            resizefs=cmd_runner_fmt.as_bool("--resizefs"),
            size_L=cmd_runner_fmt.as_opt_val("-L"),
            size_l=cmd_runner_fmt.as_opt_val("-l"),
            lv=cmd_runner_fmt.as_list(),
            pvs=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def lvremove_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    """
    Runner for C(lvremove). Used by: community.general.lvol, community.general.lxc_container.

    Suggested arg_formats keys: test force yes lv
    """
    return CmdRunner(
        module,
        command="lvremove",
        arg_formats=dict(
            test=cmd_runner_fmt.as_bool("--test"),
            force=cmd_runner_fmt.as_bool("--force"),
            yes=cmd_runner_fmt.as_bool("--yes"),
            lv=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )
