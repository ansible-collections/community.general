# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


import os

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


_PUPPET_PATH_PREFIX = ["/opt/puppetlabs/bin"]


def get_facter_dir():
    if os.getuid() == 0:
        return "/etc/facter/facts.d"
    else:
        return os.path.expanduser("~/.facter/facts.d")


def _puppet_cmd(module):
    return module.get_bin_path("puppet", False, _PUPPET_PATH_PREFIX)


# If the `timeout` CLI command feature is removed,
# Then we could add this as a fixed param to `puppet_runner`
def ensure_agent_enabled(module):
    runner = CmdRunner(
        module,
        command="puppet",
        path_prefix=_PUPPET_PATH_PREFIX,
        arg_formats=dict(
            _agent_disabled=cmd_runner_fmt.as_fixed(["config", "print", "agent_disabled_lockfile"]),
        ),
        check_rc=False,
    )

    rc, stdout, stderr = runner("_agent_disabled").run()
    if os.path.exists(stdout.strip()):
        module.fail_json(msg="Puppet agent is administratively disabled.", disabled=True)
    elif rc != 0:
        module.fail_json(msg="Puppet agent state could not be determined.")


def puppet_runner(module):
    # Keeping backward compatibility, allow for running with the `timeout` CLI command.
    # If this can be replaced with ansible `timeout` parameter in playbook,
    # then this function could be removed.
    def _prepare_base_cmd():
        _tout_cmd = module.get_bin_path("timeout", False)
        if _tout_cmd:
            cmd = ["timeout", "-s", "9", module.params["timeout"], _puppet_cmd(module)]
        else:
            cmd = ["puppet"]
        return cmd

    def noop_func(v):
        return ["--noop"] if module.check_mode or v else ["--no-noop"]

    _logdest_map = {
        "syslog": ["--logdest", "syslog"],
        "all": ["--logdest", "syslog", "--logdest", "console"],
    }

    @cmd_runner_fmt.unpack_args
    def execute_func(execute, manifest):
        if execute:
            return ["--execute", execute]
        else:
            return [manifest]

    runner = CmdRunner(
        module,
        command=_prepare_base_cmd(),
        path_prefix=_PUPPET_PATH_PREFIX,
        arg_formats=dict(
            _agent_fixed=cmd_runner_fmt.as_fixed(
                [
                    "agent",
                    "--onetime",
                    "--no-daemonize",
                    "--no-usecacheonfailure",
                    "--no-splay",
                    "--detailed-exitcodes",
                    "--verbose",
                    "--color",
                    "0",
                ]
            ),
            _apply_fixed=cmd_runner_fmt.as_fixed(["apply", "--detailed-exitcodes"]),
            puppetmaster=cmd_runner_fmt.as_opt_val("--server"),
            show_diff=cmd_runner_fmt.as_bool("--show-diff"),
            confdir=cmd_runner_fmt.as_opt_val("--confdir"),
            environment=cmd_runner_fmt.as_opt_val("--environment"),
            tags=cmd_runner_fmt.as_func(lambda v: ["--tags", ",".join(v)]),
            skip_tags=cmd_runner_fmt.as_func(lambda v: ["--skip_tags", ",".join(v)]),
            certname=cmd_runner_fmt.as_opt_eq_val("--certname"),
            noop=cmd_runner_fmt.as_func(noop_func),
            use_srv_records=cmd_runner_fmt.as_bool("--usr_srv_records", "--no-usr_srv_records", ignore_none=True),
            logdest=cmd_runner_fmt.as_map(_logdest_map, default=[]),
            modulepath=cmd_runner_fmt.as_opt_eq_val("--modulepath"),
            _execute=cmd_runner_fmt.as_func(execute_func),
            summarize=cmd_runner_fmt.as_bool("--summarize"),
            waitforlock=cmd_runner_fmt.as_opt_val("--waitforlock"),
            debug=cmd_runner_fmt.as_bool("--debug"),
            verbose=cmd_runner_fmt.as_bool("--verbose"),
        ),
        check_rc=False,
        force_lang=module.params["environment_lang"],
    )
    return runner
