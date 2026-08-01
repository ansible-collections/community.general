# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from io import StringIO

import pytest
from ansible.playbook.play_context import PlayContext
from ansible.plugins.loader import connection_loader

BUILD_CMD_TEST_CASES: list[dict[str, t.Any]] = [
    dict(
        id="sh simple",
        input=dict(
            cmd="""echo 123""",
            shell="sh",
        ),
        output=["/bin/sh", "-c", "echo 123"],
    ),
    dict(
        id="powershell simple",
        input=dict(
            cmd="""powershell -c My-Command1 -Param 'param' """,
            shell="powershell",
        ),
        output=["powershell", "-c", "My-Command1 -Param 'param'"],
    ),
    dict(
        id=r"D:\my path\powershell.exe simple",
        input=dict(
            cmd=r"""D:\my path\powershell.exe -c My-Command1 -Param 'param' """,
            shell="powershell",
        ),
        output=[r"D:\my path\powershell.exe", "-c", "My-Command1 -Param 'param'"],
    ),
    dict(
        id=r"\\127.0.0.1\share\powershell simple",
        input=dict(
            cmd=r"""\\127.0.0.1\share\powershell -c My-Command1 -Param 'param' """,
            shell="powershell",
        ),
        output=[r"\\127.0.0.1\share\powershell", "-c", "My-Command1 -Param 'param'"],
    ),
    dict(
        id=r"C:\powershell simple",
        input=dict(
            cmd=r"""C:\powershell -c My-Command1 -Param 'param' """,
            shell="powershell",
        ),
        output=[r"C:\powershell", "-c", "My-Command1 -Param 'param'"],
    ),
    dict(
        id=r'"C:\powershell" simple',
        input=dict(
            cmd=r""""C:\powershell" -c My-Command1 -Param 'param' """,
            shell="cmd",  # the plugins does not care the shell type, as long as it is windows
        ),
        output=[r"C:\powershell", "-c", "My-Command1 -Param 'param'"],
    ),
    dict(
        id="powershell multiline",
        input=dict(
            cmd=(
                "powershell -ExecutionPolicy bypass -Command\n"
                "My-Command1 \\\n"
                "  -Param 'param';\n"
                "My-Command2 \\\n"
                "  -Param 'param'"
            ),
            shell="powershell",
        ),
        output=[
            "powershell",
            "-ExecutionPolicy",
            "bypass",
            "-Command",
            "My-Command1 \\\n  -Param 'param';\nMy-Command2 \\\n  -Param 'param'",
        ],
    ),
    dict(
        id="cmd simple",
        input=dict(
            cmd="""CMD.EXE /C some-command /flag1 /flag2""",
            shell="powershell",
        ),
        output=["CMD.EXE", "/C", "some-command /flag1 /flag2"],
    ),
    dict(
        id=r"C:\cmd simple",
        input=dict(
            cmd=r"""C:\CMD.EXE /C some-command /flag1 /flag2""",
            shell="powershell",
        ),
        output=[r"C:\CMD.EXE", "/C", "some-command /flag1 /flag2"],
    ),
    dict(
        id=r'"C:\cmd" simple',
        input=dict(
            cmd=r""""C:\CMD" /c some-command /flag1 /flag2""",
            shell="powershell",
        ),
        output=[r"C:\CMD", "/c", "some-command /flag1 /flag2"],
    ),
    dict(
        id="powershell encoded command strips quotes",
        input=dict(
            cmd="""powershell -NoProfile -NonInteractive -ExecutionPolicy Unrestricted -EncodedCommand 'cABhAHIAYQBtAA=='""",
            shell="powershell",
        ),
        output=[
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Unrestricted",
            "-EncodedCommand",
            "cABhAHIAYQBtAA==",
        ],
    ),
    dict(
        id="powershell encoded command strips double quotes",
        input=dict(
            cmd='''powershell -NoProfile -EncodedCommand "cABhAHIAYQBtAA=="''',
            shell="powershell",
        ),
        output=[
            "powershell",
            "-NoProfile",
            "-EncodedCommand",
            "cABhAHIAYQBtAA==",
        ],
    ),
    dict(
        id="powershell encoded command case-insensitive keyword",
        input=dict(
            cmd="""powershell -NoProfile -eNcOdEdCoMmAnD 'cABhAHIAYQBtAA=='""",
            shell="powershell",
        ),
        output=[
            "powershell",
            "-NoProfile",
            "-eNcOdEdCoMmAnD",
            "cABhAHIAYQBtAA==",
        ],
    ),
    dict(
        id="powershell encoded command keeps surrounding flags",
        input=dict(
            cmd="""powershell -NoProfile -EncodedCommand 'cABhAHIAYQBtAA==' -InputFormat None""",
            shell="powershell",
        ),
        output=[
            "powershell",
            "-NoProfile",
            "-EncodedCommand",
            "cABhAHIAYQBtAA==",
            "-InputFormat",
            "None",
        ],
    ),
    dict(
        id="powershell -enc alias strips quotes",
        input=dict(
            cmd="""powershell -NoProfile -enc 'cABhAHIAYQBtAA=='""",
            shell="powershell",
        ),
        output=[
            "powershell",
            "-NoProfile",
            "-enc",
            "cABhAHIAYQBtAA==",
        ],
    ),
    dict(
        id="powershell -Command with spaces in path",
        input=dict(
            cmd="""powershell.exe -NonInteractive -Command 'Write-Host "hello"; & \\'C:\\My Scripts\\run me.ps1\\''""",
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NonInteractive",
            "-Command",
            """Write-Host "hello"; & \\'C:\\My Scripts\\run me.ps1\\'""",
        ],
    ),
    dict(
        id="powershell -File with spaces in path",
        input=dict(
            cmd='''powershell.exe -NonInteractive -File "C:\\My Scripts\\run me.ps1"''',
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NonInteractive",
            "-File",
            r"C:\My Scripts\run me.ps1",
        ],
    ),
    dict(
        id="powershell -File single quoted path with trailing args",
        input=dict(
            cmd="""powershell.exe -NoProfile -File 'C:\\My Scripts\\run me.ps1' -Arg1 value""",
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NoProfile",
            "-File",
            r"C:\My Scripts\run me.ps1",
            "-Arg1",
            "value",
        ],
    ),
    dict(
        id="powershell -F alias with spaces in path",
        input=dict(
            cmd='''powershell.exe -NoProfile -F "C:\\My Scripts\\run me.ps1"''',
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NoProfile",
            "-F",
            r"C:\My Scripts\run me.ps1",
        ],
    ),
    dict(
        id="powershell -Command outer double quotes",
        input=dict(
            cmd='''powershell.exe -NoProfile -Command "Write-Host 'hello world'"''',
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NoProfile",
            "-Command",
            "Write-Host 'hello world'",
        ],
    ),
    dict(
        id="powershell -Command empty quoted payload",
        input=dict(
            cmd='''powershell.exe -NoProfile -Command ""''',
            shell="powershell",
        ),
        output=[
            "powershell.exe",
            "-NoProfile",
            "-Command",
            "",
        ],
    ),
]


BUILD_CMD_TEST_CASE_IDS: list[str] = [tc["id"] for tc in BUILD_CMD_TEST_CASES]


@pytest.mark.parametrize("testcase", BUILD_CMD_TEST_CASES, ids=BUILD_CMD_TEST_CASE_IDS)
def test_build_command(mocker, testcase):
    mocker.patch("ansible.module_utils.common.process.get_bin_path").return_value = "/test/bin/incus"

    play_context = PlayContext()
    play_context.shell = testcase["input"].get("shell", "sh")
    in_stream = StringIO()
    conn = connection_loader.get("community.general.incus", play_context, in_stream)
    conn.set_option("remote_addr", "server1")
    conn.set_option("remote_user", "root")

    cli_preamble = [
        "/test/bin/incus",
        "--project",
        "default",
        "exec",
        *(["-T"] if play_context.shell in ["cmd", "powershell"] else []),
        "local:server1",
        "--",
    ]

    built = conn._build_command(testcase["input"]["cmd"])
    tc_cmd = cli_preamble + testcase["output"]
    assert built == tc_cmd, f"\n   built = {built}\ntestcase = {tc_cmd}"
