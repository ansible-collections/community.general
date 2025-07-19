# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Felix Fontein <felix@fontein.de>

# /// script
# dependencies = ["nox>=2025.02.09", "antsibull-nox"]
# ///

import os
import sys

import nox

# Whether the noxfile is running in CI:
IN_CI = os.environ.get("CI") == "true"


try:
    import antsibull_nox
except ImportError:
    print("You need to install antsibull-nox in the same Python environment as nox.")
    sys.exit(1)


antsibull_nox.load_antsibull_nox_toml()


@nox.session(name="aliases", python=False, default=True)
def aliases(session: nox.Session) -> None:
    session.run("python", "tests/sanity/extra/aliases.py")


@nox.session(name="botmeta", default=True)
def botmeta(session: nox.Session) -> None:
    session.install("PyYAML", "voluptuous")
    session.run("python", "tests/sanity/extra/botmeta.py")


@nox.session(name="ansible-output", default=False)
def ansible_output(session: nox.Session) -> None:
    session.install(
        "ansible-core",
        "antsibull-docs",
        # Needed libs for some code blocks:
        "jc",
        "hashids",
        # Tools for post-processing
        "ruamel.yaml",  # used by docs/docsite/reformat-yaml.py
    )
    args = []
    if IN_CI:
        args.append("--check")
    session.run("antsibull-docs", "ansible-output", *args, *session.posargs)


# Allow to run the noxfile with `python noxfile.py`, `pipx run noxfile.py`, or similar.
# Requires nox >= 2025.02.09
if __name__ == "__main__":
    nox.main()
