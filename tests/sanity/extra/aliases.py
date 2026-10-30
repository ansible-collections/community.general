#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check extra collection docs with antsibull-docs."""

from __future__ import annotations

import glob
import os
import sys

import yaml

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def get_heavy_targets():
    """Return the heavy/<backend> targets that have sessions in antsibull-nox.toml, and whether errors were found."""
    with open("antsibull-nox.toml", "rb") as f:
        config = tomllib.load(f)

    targets = set()
    has_errors = False
    for group in config["sessions"]["ansible_test_integration"]["groups"]:
        for session in [group] + group.get("sessions", []):
            tags = set(group.get("tags", [])) | set(session.get("tags", []))
            target = session.get("target", [])
            for value in [target] if isinstance(target, str) else target:
                if not value.startswith("heavy/"):
                    continue
                target_name = value.rstrip("/")
                backend = target_name.split("/", 1)[1]
                if f"heavy-{backend}" not in tags:
                    print(f'antsibull-nox.toml: session for "{target_name}" has no tag "heavy-{backend}"')
                    has_errors = True
                workflow = f".github/workflows/nox-heavy-{backend}.yml"
                if not os.path.exists(workflow):
                    print(f'{workflow}: workflow for "{target_name}" not found')
                    has_errors = True
                targets.add(target_name)
    return targets, has_errors


def main():
    """Main entry point."""
    with open(".azure-pipelines/azure-pipelines.yml", "rb") as f:
        azp = yaml.safe_load(f)

    allowed_targets = {"azp/generic/1"}
    for stage in azp["stages"]:
        if stage["stage"].startswith(("sanity", "unit", "Summary")):
            continue
        for job in stage["jobs"]:
            for param in job["parameters"]["targets"]:
                group = param["test"].rsplit("-", 1)[-1]
                allowed_targets.add(f"azp/posix/{group}")
    heavy_targets, has_errors = get_heavy_targets()
    allowed_targets.update(heavy_targets)

    paths = glob.glob("tests/integration/targets/*/aliases")

    for path in paths:
        targets = []
        skip = False
        with open(path) as f:
            for line in f:
                if "#" in line:
                    line = line[: line.find("#")]
                line = line.strip()
                if line.startswith("needs/"):
                    continue
                if line.startswith("skip/"):
                    continue
                if line.startswith("cloud/"):
                    continue
                if line.startswith("context/"):
                    continue
                if line in ("unsupported", "disabled", "hidden"):
                    skip = True
                if line in ("destructive",):
                    continue
                if "/" not in line and line not in ("heavy",):
                    continue
                targets.append(line)
        if skip:
            continue
        if not targets:
            if "targets/setup_" in path:
                continue
            print(f"{path}: found no targets")
            has_errors = True
        for target in targets:
            if target not in allowed_targets:
                print(f'{path}: found invalid target "{target}"')
                has_errors = True

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
