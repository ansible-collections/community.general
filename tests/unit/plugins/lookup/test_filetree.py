# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from ansible.errors import AnsibleLookupError
from ansible.plugins.loader import lookup_loader
from ansible.template import Templar
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader


class TestFiletreeLookup(unittest.TestCase):
    def setUp(self):
        self.loader = DictDataLoader({})
        self.templar = Templar(loader=self.loader, variables={})
        self.lookup = lookup_loader.get(
            "community.general.filetree",
            loader=self.loader,
            templar=self.templar,
        )
        self.tmpdir = tempfile.mkdtemp(prefix="ansible_test_filetree_")
        self.tree_root = os.path.join(self.tmpdir, "data")
        os.makedirs(os.path.join(self.tree_root, ".git"))
        os.makedirs(os.path.join(self.tree_root, "subdir"))
        with open(os.path.join(self.tree_root, "app.conf"), "w", encoding="utf-8") as handle:
            handle.write("content\n")
        with open(os.path.join(self.tree_root, "subdir", "nested.conf"), "w", encoding="utf-8") as handle:
            handle.write("nested\n")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _run_lookup(self, **kwargs):
        with (
            patch.object(self.lookup, "get_basedir", return_value=self.tmpdir),
            patch.object(self.loader, "path_dwim_relative", return_value=self.tmpdir),
        ):
            return self.lookup.run(["data"], {}, **kwargs)

    def test_invalid_exclude_regex_raises_lookup_error(self):
        with self.assertRaises(AnsibleLookupError) as ctx:
            self._run_lookup(exclude="temp[1")

        self.assertIn("Invalid exclude regular expression", str(ctx.exception))
        self.assertIn("temp[1", str(ctx.exception))

    def test_valid_exclude_skips_matching_basenames(self):
        result = self._run_lookup(exclude=r"^\.git$")

        paths = {entry["path"] for entry in result}
        self.assertIn("app.conf", paths)
        self.assertIn(os.path.join("subdir", "nested.conf"), paths)
        self.assertNotIn(".git", paths)

    def test_lookup_without_exclude_lists_entries(self):
        result = self._run_lookup()

        paths = {entry["path"] for entry in result}
        self.assertIn("app.conf", paths)
        self.assertIn(".git", paths)
        self.assertIn("subdir", paths)
        self.assertIn(os.path.join("subdir", "nested.conf"), paths)

    def test_file_entry_includes_expected_properties(self):
        result = self._run_lookup()
        app_conf = next(entry for entry in result if entry["path"] == "app.conf")

        self.assertEqual(app_conf["state"], "file")
        self.assertEqual(app_conf["root"], self.tree_root)
        self.assertEqual(app_conf["src"], os.path.join(self.tree_root, "app.conf"))
        self.assertIn("mode", app_conf)
        self.assertIn("owner", app_conf)
        self.assertIn("group", app_conf)
