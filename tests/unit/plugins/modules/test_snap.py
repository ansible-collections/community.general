# -*- coding: utf-8 -*-
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys

from ansible_collections.community.general.plugins.modules import snap
from .helper import Helper, RunCommandMock  # pylint: disable=unused-import


issue_6803_status_out = """Name    Version      Rev    Tracking         Publisher    Notes
core20  20220826     1623   latest/stable    canonical**  base
lxd     5.6-794016a  23680  latest/stable/…  canonical**  -
snapd   2.57.4       17336  latest/stable    canonical**  snapd
"""

issue_6803_microk8s_out = (
    "\rEnsure prerequisites for \"microk8s\" are available                              /"
    "\rDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"                     "
    "\rDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"                     \\"
    "\rDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"                     "
    "\rDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"                     /\u001b[?25"
    "\r\u001b[7m\u001b[0mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     0%  880kB/s 3m21"
    "\r\u001b[7m\u001b[0mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     1% 2.82MB/s 1m02"
    "\r\u001b[7mD\u001b[0mownload snap \"microk8s\" (5372) from channel \"1.27/stable\"     2% 4.71MB/s 37.0"
    "\r\u001b[7mDo\u001b[0mwnload snap \"microk8s\" (5372) from channel \"1.27/stable\"     4% 9.09MB/s 18.8"
    "\r\u001b[7mDown\u001b[0mload snap \"microk8s\" (5372) from channel \"1.27/stable\"     6% 12.4MB/s 13.5"
    "\r\u001b[7mDownl\u001b[0moad snap \"microk8s\" (5372) from channel \"1.27/stable\"     7% 14.5MB/s 11.3"
    "\r\u001b[7mDownloa\u001b[0md snap \"microk8s\" (5372) from channel \"1.27/stable\"     9% 15.9MB/s 10.1"
    "\r\u001b[7mDownload \u001b[0msnap \"microk8s\" (5372) from channel \"1.27/stable\"    11% 18.0MB/s 8.75"
    "\r\u001b[7mDownload s\u001b[0mnap \"microk8s\" (5372) from channel \"1.27/stable\"    13% 19.4MB/s 7.91"
    "\r\u001b[7mDownload sn\u001b[0map \"microk8s\" (5372) from channel \"1.27/stable\"    15% 20.1MB/s 7.50"
    "\r\u001b[7mDownload snap\u001b[0m \"microk8s\" (5372) from channel \"1.27/stable\"    17% 20.9MB/s 7.05"
    "\r\u001b[7mDownload snap \"\u001b[0mmicrok8s\" (5372) from channel \"1.27/stable\"    19% 22.1MB/s 6.50"
    "\r\u001b[7mDownload snap \"m\u001b[0microk8s\" (5372) from channel \"1.27/stable\"    21% 22.9MB/s 6.11"
    "\r\u001b[7mDownload snap \"mic\u001b[0mrok8s\" (5372) from channel \"1.27/stable\"    23% 23.2MB/s 5.90"
    "\r\u001b[7mDownload snap \"micr\u001b[0mok8s\" (5372) from channel \"1.27/stable\"    25% 23.9MB/s 5.58"
    "\r\u001b[7mDownload snap \"microk\u001b[0m8s\" (5372) from channel \"1.27/stable\"    27% 24.5MB/s 5.30"
    "\r\u001b[7mDownload snap \"microk8\u001b[0ms\" (5372) from channel \"1.27/stable\"    29% 24.9MB/s 5.09"
    "\r\u001b[7mDownload snap \"microk8s\"\u001b[0m (5372) from channel \"1.27/stable\"    31% 25.4MB/s 4.85"
    "\r\u001b[7mDownload snap \"microk8s\" (\u001b[0m5372) from channel \"1.27/stable\"    33% 25.8MB/s 4.63"
    "\r\u001b[7mDownload snap \"microk8s\" (5\u001b[0m372) from channel \"1.27/stable\"    35% 26.2MB/s 4.42"
    "\r\u001b[7mDownload snap \"microk8s\" (53\u001b[0m72) from channel \"1.27/stable\"    36% 26.3MB/s 4.30"
    "\r\u001b[7mDownload snap \"microk8s\" (5372\u001b[0m) from channel \"1.27/stable\"    38% 26.7MB/s 4.10"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) \u001b[0mfrom channel \"1.27/stable\"    40% 26.9MB/s 3.95"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) f\u001b[0mrom channel \"1.27/stable\"    42% 27.2MB/s 3.77"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) fro\u001b[0mm channel \"1.27/stable\"    44% 27.4MB/s 3.63"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from\u001b[0m channel \"1.27/stable\"    46% 27.8MB/s 3.44"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from c\u001b[0mhannel \"1.27/stable\"    48% 27.9MB/s 3.31"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from cha\u001b[0mnnel \"1.27/stable\"    50% 28.1MB/s 3.15"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from chan\u001b[0mnel \"1.27/stable\"    52% 28.3MB/s 3.02"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channe\u001b[0ml \"1.27/stable\"    54% 28.5MB/s 2.87"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel\u001b[0m \"1.27/stable\"    56% 28.6MB/s 2.75"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \u001b[0m\"1.27/stable\"    57% 28.7MB/s 2.63"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1\u001b[0m.27/stable\"    60% 28.9MB/s 2.47"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.2\u001b[0m7/stable\"    62% 29.0MB/s 2.35"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27\u001b[0m/stable\"    63% 29.1MB/s 2.23"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/s\u001b[0mtable\"    65% 29.2MB/s 2.10"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/st\u001b[0mable\"    67% 29.4MB/s 1.97"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stab\u001b[0mle\"    69% 29.5MB/s 1.85"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stabl\u001b[0me\"    71% 29.5MB/s 1.74"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"\u001b[0m    73% 29.7MB/s 1.59"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"  \u001b[0m  75% 29.8MB/s 1.48"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"   \u001b[0m 77% 29.8MB/s 1.37"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    7\u001b[0m9% 29.9MB/s 1.26"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    81\u001b[0m% 30.0MB/s 1.14"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    83% \u001b[0m30.1MB/s 1.01"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    84% 3\u001b[0m0.1MB/s 919m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    86% 30.\u001b[0m1MB/s 810m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    88% 30.2\u001b[0mMB/s 676m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    91% 30.3MB\u001b[0m/s 555m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    93% 30.4MB/s\u001b[0m 436m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    95% 30.5MB/s \u001b[0m317m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    96% 30.5MB/s 21\u001b[0m1m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"    98% 30.5MB/s 117\u001b[0mm"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"   100% 30.5MB/s  11m\u001b[0m"
    "\r\u001b[7mDownload snap \"microk8s\" (5372) from channel \"1.27/stable\"   100% 30.0MB/s 0.0ns\u001b[0"
    "\rFetch and check assertions for snap \"microk8s\" (5372)                          "
    "\rMount snap \"microk8s\" (5372)                                                   \\"
    "\rMount snap \"microk8s\" (5372)                                                   "
    "\rMount snap \"microk8s\" (5372)                                                   "
    "\rMount snap \"microk8s\" (5372)                                                   "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 \\"
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 \\"
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 \\"
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rSetup snap \"microk8s\" (5372) security profiles                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 \\"
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rRun install hook of \"microk8s\" snap if present                                 "
    "\rStart snap \"microk8s\" (5372) services                                          \\"
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          \\"
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          \\"
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          \\"
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          "
    "\rStart snap \"microk8s\" (5372) services                                          \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun configure hook of \"microk8s\" snap if present                               \\"
    "\rRun configure hook of \"microk8s\" snap if present                               "
    "\rRun service command \"restart\" for services [\"daemon-apiserver-proxy\"] of snap \""
    "\r\u001b[0m\u001b[?25h\u001b[Kmicrok8s (1.27/stable) v1.27.2 from Canonical** installed\n"
)

issue_6803_kubectl_out = (
    "\rEnsure prerequisites for \"kubectl\" are available                              /"
    "\rDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"                     "
    "\rDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"                     \\"
    "\rDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"                     "
    "\rDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"                     /\u001b[?25"
    "\r\u001b[7m\u001b[0mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     0%     0B/s ages"
    "\r\u001b[7m\u001b[0mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     0%  880kB/s 3m21"
    "\r\u001b[7m\u001b[0mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     1% 2.82MB/s 1m02"
    "\r\u001b[7mD\u001b[0mownload snap \"kubectl\" (5372) from channel \"1.27/stable\"     2% 4.71MB/s 37.0"
    "\r\u001b[7mDo\u001b[0mwnload snap \"kubectl\" (5372) from channel \"1.27/stable\"     4% 9.09MB/s 18.8"
    "\r\u001b[7mDown\u001b[0mload snap \"kubectl\" (5372) from channel \"1.27/stable\"     6% 12.4MB/s 13.5"
    "\r\u001b[7mDownl\u001b[0moad snap \"kubectl\" (5372) from channel \"1.27/stable\"     7% 14.5MB/s 11.3"
    "\r\u001b[7mDownloa\u001b[0md snap \"kubectl\" (5372) from channel \"1.27/stable\"     9% 15.9MB/s 10.1"
    "\r\u001b[7mDownload \u001b[0msnap \"kubectl\" (5372) from channel \"1.27/stable\"    11% 18.0MB/s 8.75"
    "\r\u001b[7mDownload s\u001b[0mnap \"kubectl\" (5372) from channel \"1.27/stable\"    13% 19.4MB/s 7.91"
    "\r\u001b[7mDownload sn\u001b[0map \"kubectl\" (5372) from channel \"1.27/stable\"    15% 20.1MB/s 7.50"
    "\r\u001b[7mDownload snap\u001b[0m \"kubectl\" (5372) from channel \"1.27/stable\"    17% 20.9MB/s 7.05"
    "\r\u001b[7mDownload snap \"\u001b[0mkubectl\" (5372) from channel \"1.27/stable\"    19% 22.1MB/s 6.50"
    "\r\u001b[7mDownload snap \"m\u001b[0kubectl\" (5372) from channel \"1.27/stable\"    21% 22.9MB/s 6.11"
    "\r\u001b[7mDownload snap \"mic\u001b[0mrok8s\" (5372) from channel \"1.27/stable\"    23% 23.2MB/s 5.90"
    "\r\u001b[7mDownload snap \"micr\u001b[0mok8s\" (5372) from channel \"1.27/stable\"    25% 23.9MB/s 5.58"
    "\r\u001b[7mDownload snap \"microk\u001b[0m8s\" (5372) from channel \"1.27/stable\"    27% 24.5MB/s 5.30"
    "\r\u001b[7mDownload snap \"microk8\u001b[0ms\" (5372) from channel \"1.27/stable\"    29% 24.9MB/s 5.09"
    "\r\u001b[7mDownload snap \"kubectl\"\u001b[0m (5372) from channel \"1.27/stable\"    31% 25.4MB/s 4.85"
    "\r\u001b[7mDownload snap \"kubectl\" (\u001b[0m5372) from channel \"1.27/stable\"    33% 25.8MB/s 4.63"
    "\r\u001b[7mDownload snap \"kubectl\" (5\u001b[0m372) from channel \"1.27/stable\"    35% 26.2MB/s 4.42"
    "\r\u001b[7mDownload snap \"kubectl\" (53\u001b[0m72) from channel \"1.27/stable\"    36% 26.3MB/s 4.30"
    "\r\u001b[7mDownload snap \"kubectl\" (5372\u001b[0m) from channel \"1.27/stable\"    38% 26.7MB/s 4.10"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) \u001b[0mfrom channel \"1.27/stable\"    40% 26.9MB/s 3.95"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) f\u001b[0mrom channel \"1.27/stable\"    42% 27.2MB/s 3.77"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) fro\u001b[0mm channel \"1.27/stable\"    44% 27.4MB/s 3.63"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from\u001b[0m channel \"1.27/stable\"    46% 27.8MB/s 3.44"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from c\u001b[0mhannel \"1.27/stable\"    48% 27.9MB/s 3.31"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from cha\u001b[0mnnel \"1.27/stable\"    50% 28.1MB/s 3.15"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from chan\u001b[0mnel \"1.27/stable\"    52% 28.3MB/s 3.02"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channe\u001b[0ml \"1.27/stable\"    54% 28.5MB/s 2.87"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel\u001b[0m \"1.27/stable\"    56% 28.6MB/s 2.75"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \u001b[0m\"1.27/stable\"    57% 28.7MB/s 2.63"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1\u001b[0m.27/stable\"    60% 28.9MB/s 2.47"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.2\u001b[0m7/stable\"    62% 29.0MB/s 2.35"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27\u001b[0m/stable\"    63% 29.1MB/s 2.23"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/s\u001b[0mtable\"    65% 29.2MB/s 2.10"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/st\u001b[0mable\"    67% 29.4MB/s 1.97"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stab\u001b[0mle\"    69% 29.5MB/s 1.85"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stabl\u001b[0me\"    71% 29.5MB/s 1.74"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"\u001b[0m    73% 29.7MB/s 1.59"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"  \u001b[0m  75% 29.8MB/s 1.48"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"   \u001b[0m 77% 29.8MB/s 1.37"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    7\u001b[0m9% 29.9MB/s 1.26"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    81\u001b[0m% 30.0MB/s 1.14"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    83% \u001b[0m30.1MB/s 1.01"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    84% 3\u001b[0m0.1MB/s 919m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    86% 30.\u001b[0m1MB/s 810m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    88% 30.2\u001b[0mMB/s 676m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    91% 30.3MB\u001b[0m/s 555m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    93% 30.4MB/s\u001b[0m 436m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    95% 30.5MB/s \u001b[0m317m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    96% 30.5MB/s 21\u001b[0m1m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"    98% 30.5MB/s 117\u001b[0mm"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"   100% 30.5MB/s  11m\u001b[0m"
    "\r\u001b[7mDownload snap \"kubectl\" (5372) from channel \"1.27/stable\"   100% 30.0MB/s 0.0ns\u001b[0"
    "\rFetch and check assertions for snap \"kubectl\" (5372)                          "
    "\rMount snap \"kubectl\" (5372)                                                   \\"
    "\rMount snap \"kubectl\" (5372)                                                   "
    "\rMount snap \"kubectl\" (5372)                                                   "
    "\rMount snap \"kubectl\" (5372)                                                   "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 \\"
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 \\"
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 \\"
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rSetup snap \"kubectl\" (5372) security profiles                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 \\"
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rRun install hook of \"kubectl\" snap if present                                 "
    "\rStart snap \"kubectl\" (5372) services                                          \\"
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          \\"
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          \\"
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          \\"
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          "
    "\rStart snap \"kubectl\" (5372) services                                          \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun configure hook of \"kubectl\" snap if present                               \\"
    "\rRun configure hook of \"kubectl\" snap if present                               "
    "\rRun service command \"restart\" for services [\"daemon-apiserver-proxy\"] of snap \""
    "\r\u001b[0m\u001b[?25h\u001b[Kkubectl (1.27/stable) v1.27.2 from Canonical** installed\n"
)

TEST_CASES = [
    dict(
        id="simple case",
        input={"name": ["hello-world"]},
        output=dict(changed=True, snaps_installed=["hello-world"]),
        flags={},
        mocks=dict(
            run_command=[
                dict(
                    command=['/testbin/snap', 'info', 'hello-world'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out='name: hello-world\n',
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'list'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out="",
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'install', 'hello-world'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out="hello-world (12345/stable) v12345 from Canonical** installed\n",
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'list'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out=(
                        "Name    Version      Rev    Tracking         Publisher    Notes"
                        "core20  20220826     1623   latest/stable    canonical**  base"
                        "lxd     5.6-794016a  23680  latest/stable/…  canonical**  -"
                        "hello-world     5.6-794016a  23680  latest/stable/…  canonical**  -"
                        "snapd   2.57.4       17336  latest/stable    canonical**  snapd"
                        ""),
                    err="",
                ),
            ],
        ),
    ),
    dict(
        id="issue_6803",
        input={"name": ["microk8s", "kubectl"], "classic": True},
        output=dict(changed=True, snaps_installed=["microk8s", "kubectl"]),
        flags={},
        mocks=dict(
            run_command=[
                dict(
                    command=['/testbin/snap', 'info', 'microk8s', 'kubectl'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out='name: microk8s\n---\nname: kubectl\n',
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'list'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out=issue_6803_status_out,
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'install', '--classic', 'microk8s'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out=issue_6803_microk8s_out,
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'install', '--classic', 'kubectl'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out=issue_6803_kubectl_out,
                    err="",
                ),
                dict(
                    command=['/testbin/snap', 'list'],
                    environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                    rc=0,
                    out=(
                        "Name    Version      Rev    Tracking         Publisher    Notes"
                        "core20  20220826     1623   latest/stable    canonical**  base"
                        "lxd     5.6-794016a  23680  latest/stable/…  canonical**  -"
                        "microk8s     5.6-794016a  23680  latest/stable/…  canonical**  -"
                        "kubectl     5.6-794016a  23680  latest/stable/…  canonical**  -"
                        "snapd   2.57.4       17336  latest/stable    canonical**  snapd"
                        ""),
                    err="",
                ),
            ],
        ),
    ),
]

Helper.from_list(sys.modules[__name__], snap, TEST_CASES)
