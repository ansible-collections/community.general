from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner

_state_map = {
    "present": "--install",
    "absent": "--uninstall"
}


def sdkmanager_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='sdkmanager',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            update=cmd_runner_fmt.as_fixed("--update"),
            installed=cmd_runner_fmt.as_fixed("--list_installed")
        ),
        **kwargs
    )
