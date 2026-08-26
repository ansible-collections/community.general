# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import io
import os

import pytest

from ansible_collections.community.general.plugins.modules import appimage


class FakeModule:
    def __init__(self, params=None):
        self.fail = None
        self.params = params or {
            "state": "present",
            "version": None,
            "github_token": None,
            "asset_name": "*.AppImage",
        }

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

    with pytest.raises(RuntimeError, match="not a direct AppImage URL or GitHub releases page"):
        appimage.resolve_url_source(module, "https://example.com/download")


def test_local_appimage_path_rejects_non_local_sources():
    with pytest.raises(appimage.NoLocalImagePath):
        appimage.local_appimage_path("https://example.com/tool.AppImage")


def test_resolve_url_source_continues_after_non_local_source(monkeypatch):
    fetched_urls = []

    def fake_fetch_json(module, url, headers):
        fetched_urls.append(url)
        return {
            "tag_name": "v1.2.3",
            "assets": [{"name": "tool.AppImage", "browser_download_url": "https://example.com/tool.AppImage"}],
        }

    monkeypatch.setattr(appimage, "fetch_json", fake_fetch_json)

    source = appimage.resolve_url_source(FakeModule(), "https://github.com/example/project/releases")

    assert fetched_urls == ["https://api.github.com/repos/example/project/releases/latest"]
    assert source["source_url"] == "https://example.com/tool.AppImage"


def test_resolve_url_source_accepts_local_path(tmp_path):
    path = tmp_path / "tool.AppImage"
    path.write_bytes(b"appimage")

    source = appimage.resolve_url_source(FakeModule(), str(path))

    assert source["source_path"] == str(path)
    assert source["asset_name"] == "tool.AppImage"


def test_resolve_url_source_accepts_file_url(tmp_path):
    path = tmp_path / "tool.AppImage"
    path.write_bytes(b"appimage")

    source = appimage.resolve_url_source(FakeModule(), path.as_uri())

    assert source["source_path"] == str(path)
    assert source["asset_name"] == "tool.AppImage"


def test_resolve_url_source_rejects_latest_for_local_path(tmp_path):
    path = tmp_path / "tool.AppImage"
    path.write_bytes(b"appimage")

    with pytest.raises(RuntimeError, match=r"`state=latest` is only supported"):
        appimage.resolve_url_source(FakeModule({"state": "latest"}), str(path))


def test_resolve_url_source_rejects_latest_for_direct_url():
    module = FakeModule({"state": "latest"})

    with pytest.raises(RuntimeError, match=r"`state=latest` is only supported"):
        appimage.resolve_url_source(module, "https://example.com/tool.AppImage")


def test_resolve_url_source_rejects_latest_with_version():
    module = FakeModule(
        {
            "state": "latest",
            "version": "v1.2.3",
            "github_token": None,
            "asset_name": "*.AppImage",
        }
    )

    with pytest.raises(RuntimeError, match="state=latest cannot be combined with version"):
        appimage.resolve_url_source(module, "https://github.com/example/project/releases")


def test_resolve_url_source_uses_latest_github_release_for_state_latest(monkeypatch):
    fetched_urls = []

    def fake_fetch_json(module, url, headers):
        fetched_urls.append(url)
        return {
            "tag_name": "v2.0.0",
            "assets": [{"name": "tool.AppImage", "browser_download_url": "https://example.com/tool.AppImage"}],
        }

    monkeypatch.setattr(appimage, "fetch_json", fake_fetch_json)

    source = appimage.resolve_url_source(
        FakeModule({"state": "latest", "version": None, "github_token": None, "asset_name": "*.AppImage"}),
        "https://github.com/example/project/releases/tag/v1.0.0",
    )

    assert fetched_urls == ["https://api.github.com/repos/example/project/releases/latest"]
    assert source["version"] == "v2.0.0"


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


def test_needs_install_uses_source_path_metadata_for_latest(tmp_path):
    path = tmp_path / "tool"
    path.write_text("appimage", encoding="utf-8")
    appimage.write_metadata(str(path), {"source_path": "/tmp/tool-v1.AppImage", "version": None})

    assert not appimage.needs_install(str(path), "latest", {"source_path": "/tmp/tool-v1.AppImage", "version": None})
    assert appimage.needs_install(str(path), "latest", {"source_path": "/tmp/tool-v2.AppImage", "version": None})


def test_response_text_decodes_body():
    class Response:
        def read(self):
            return b'{"ok": true}'

    assert appimage.response_text(Response()) == '{"ok": true}'


def test_atomic_install_copies_source_file(tmp_path):
    class InstallModule(FakeModule):
        def __init__(self):
            super().__init__({"unsafe_writes": False})
            self.tmpdir = str(tmp_path)
            self.atomic_move_args = None

        def atomic_move(self, tmp_path, dest, unsafe_writes=False):
            self.atomic_move_args = (tmp_path, dest, unsafe_writes)
            os.replace(tmp_path, dest)

    module = InstallModule()
    dest = tmp_path / "tool"

    appimage.atomic_install(module, io.BytesIO(b"appimage"), str(dest))

    assert dest.read_bytes() == b"appimage"
    assert module.atomic_move_args[1:] == (str(dest), False)


def test_copy_appimage_installs_local_file(tmp_path):
    class InstallModule(FakeModule):
        def __init__(self):
            super().__init__({"unsafe_writes": False})
            self.tmpdir = str(tmp_path)

        def atomic_move(self, tmp_path, dest, unsafe_writes=False):
            os.replace(tmp_path, dest)

    source = tmp_path / "source.AppImage"
    dest = tmp_path / "tool"
    source.write_bytes(b"local appimage")

    appimage.copy_appimage(InstallModule(), str(source), str(dest))

    assert dest.read_bytes() == b"local appimage"


def test_download_appimage_installs_response_body(monkeypatch, tmp_path):
    class InstallModule(FakeModule):
        def __init__(self):
            super().__init__({"timeout": 30, "unsafe_writes": False})
            self.tmpdir = str(tmp_path)

        def atomic_move(self, tmp_path, dest, unsafe_writes=False):
            os.replace(tmp_path, dest)

    def fake_fetch_url(module, source_url, method=None, timeout=None):
        return io.BytesIO(b"downloaded appimage"), {"status": 200}

    monkeypatch.setattr(appimage, "fetch_url", fake_fetch_url)
    dest = tmp_path / "tool"

    appimage.download_appimage(InstallModule(), "https://example.com/tool.AppImage", str(dest))

    assert dest.read_bytes() == b"downloaded appimage"


def test_apply_file_attributes_defaults_to_executable_mode(tmp_path):
    class AttrModule(FakeModule):
        def __init__(self):
            super().__init__({"mode": None})
            self.loaded = None

        def load_file_common_arguments(self, params, path=None):
            self.loaded = (params, path)
            return {"mode": params["mode"], "path": path}

        def set_fs_attributes_if_different(self, file_args, changed):
            return changed

    path = tmp_path / "tool"
    path.write_text("appimage", encoding="utf-8")
    module = AttrModule()

    appimage.apply_file_attributes(module, str(path), False)

    assert module.loaded[0]["mode"] == "0755"
    assert module.loaded[1] == str(path)
