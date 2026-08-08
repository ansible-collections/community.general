# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules import appimage


class FakeModule:
    def __init__(self):
        self.fail = None

    def fail_json(self, **kwargs):
        self.fail = kwargs
        raise RuntimeError(kwargs["msg"])


def test_parse_github_releases_url_latest():
    owner, repo, tag = appimage.parse_github_releases_url("https://github.com/example/project/releases")

    assert owner == "example"
    assert repo == "project"
    assert tag is None


def test_parse_github_releases_url_tag():
    owner, repo, tag = appimage.parse_github_releases_url("https://github.com/example/project/releases/tag/v1.2.3")

    assert owner == "example"
    assert repo == "project"
    assert tag == "v1.2.3"


def test_select_release_asset_single_match():
    release = {
        "tag_name": "v1.2.3",
        "assets": [
            {"name": "tool.tar.gz", "browser_download_url": "https://example.com/tool.tar.gz"},
            {"name": "tool-x86_64.AppImage", "browser_download_url": "https://example.com/tool.AppImage"},
        ],
    }

    asset = appimage.select_release_asset(FakeModule(), release, "*.AppImage")

    assert asset["name"] == "tool-x86_64.AppImage"


def test_select_release_asset_fails_on_multiple_matches():
    release = {
        "tag_name": "v1.2.3",
        "assets": [
            {"name": "tool-x86_64.AppImage", "browser_download_url": "https://example.com/tool-x86_64.AppImage"},
            {"name": "tool-aarch64.AppImage", "browser_download_url": "https://example.com/tool-aarch64.AppImage"},
        ],
    }
    module = FakeModule()

    with pytest.raises(RuntimeError, match="Multiple AppImage assets"):
        appimage.select_release_asset(module, release, "*.AppImage")

    assert module.fail["assets"] == ["tool-x86_64.AppImage", "tool-aarch64.AppImage"]


def test_select_catalog_item_prefers_exact_match():
    feed = {
        "items": [
            {"name": "Tool_App"},
            {"name": "tool-app"},
        ],
    }

    item = appimage.select_catalog_item(FakeModule(), feed, "Tool_App")

    assert item["name"] == "Tool_App"


def test_select_catalog_item_normalizes_name():
    feed = {"items": [{"name": "AppImageUpdate"}]}

    item = appimage.select_catalog_item(FakeModule(), feed, "appimage-update")

    assert item["name"] == "AppImageUpdate"


def test_select_catalog_download_url_prefers_download_link():
    item = {
        "name": "tool",
        "links": [
            {"type": "GitHub", "url": "example/tool"},
            {"type": "Download", "url": "https://github.com/example/tool/releases"},
        ],
    }

    assert appimage.select_catalog_download_url(FakeModule(), item) == "https://github.com/example/tool/releases"


def test_select_catalog_download_url_uses_github_fallback():
    item = {"name": "tool", "links": [{"type": "GitHub", "url": "example/tool"}]}

    assert appimage.select_catalog_download_url(FakeModule(), item) == "https://github.com/example/tool/releases"


def test_resolve_url_source_rejects_unsupported_catalog_url():
    module = FakeModule()
    module.params = {"version": None, "github_token": None, "asset_name": "*.AppImage"}

    with pytest.raises(RuntimeError, match="not a direct AppImage URL or GitHub releases page"):
        appimage.resolve_url_source(module, "https://example.com/download")


def test_needs_install_uses_metadata_for_latest(tmp_path):
    path = tmp_path / "tool"
    path.write_text("appimage", encoding="utf-8")
    appimage.write_metadata(
        str(path),
        {"source_url": "https://example.com/tool-v1.AppImage", "version": "v1"},
    )

    assert not appimage.needs_install(
        str(path),
        "latest",
        {"source_url": "https://example.com/tool-v1.AppImage", "version": "v1"},
    )
    assert appimage.needs_install(
        str(path),
        "latest",
        {"source_url": "https://example.com/tool-v2.AppImage", "version": "v2"},
    )


def test_desktop_file_content():
    content = appimage.desired_desktop_file("tool", "/home/user/.local/bin/tool")

    assert "Name=tool\n" in content
    assert "Exec=/home/user/.local/bin/tool\n" in content
