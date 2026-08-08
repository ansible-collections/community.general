#!/usr/bin/python
# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: appimage
short_description: Manage AppImage packages
description:
  - Install, update, and remove applications distributed as AppImage files.
  - The module installs AppImage files into a user-controlled directory and can optionally create a desktop launcher.
  - Sources can be direct AppImage URLs, GitHub release pages containing AppImage assets, or appimage.github.io catalog entries.
author:
  - Ansible Community (@ansible-collections)
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the managed AppImage.
      - This is used as the installed executable filename and as the desktop file basename.
      - When O(url) is omitted, this is also used to look up the AppImage in the appimage.github.io catalog.
    type: str
    required: true
  url:
    description:
      - URL used to install the AppImage.
      - This can point directly to an AppImage file, or to a GitHub releases page such as
        V(https://github.com/OWNER/REPO/releases) or V(https://github.com/OWNER/REPO/releases/tag/TAG).
      - When omitted with O(state=present) or O(state=latest), the module looks up O(name) in the appimage.github.io catalog.
    type: str
  state:
    description:
      - Desired state of the AppImage.
      - When O(state=present), the AppImage is installed if missing.
      - When O(state=latest), GitHub releases pages are resolved to the latest release unless O(version) is set.
        Direct AppImage URLs are installed when missing or when the recorded source URL differs.
    type: str
    choices: [absent, present, latest]
    default: present
  install_dir:
    description:
      - Directory where the AppImage executable is installed.
    type: path
    default: "~/.local/bin"
  desktop_integration:
    description:
      - Whether to create a desktop launcher for the installed AppImage.
      - The launcher is written to C($HOME/.local/share/applications/).
    type: bool
    default: false
  version:
    description:
      - GitHub release tag to install when O(url) points to a GitHub releases page.
      - By default, GitHub release pages use the latest release.
    type: str
  asset_name:
    description:
      - Glob pattern used to select the AppImage asset from a GitHub release.
      - If the pattern matches multiple assets, the module fails and asks for a more specific pattern.
    type: str
    default: "*.AppImage"
  github_token:
    description:
      - GitHub token used when querying GitHub releases.
      - This can be useful for private repositories or higher API rate limits.
    type: str
  catalog_url:
    description:
      - URL of the appimage.github.io-compatible JSON feed used when O(url) is omitted.
    type: str
    default: https://appimage.github.io/feed.json
  validate_certs:
    description:
      - If V(false), SSL certificates are not validated.
    type: bool
    default: true
  timeout:
    description:
      - Timeout in seconds for HTTP requests.
    type: int
    default: 30
"""

EXAMPLES = r"""
- name: Install an AppImage from a direct URL
  community.general.appimage:
    name: example
    url: https://example.com/downloads/example-x86_64.AppImage

- name: Install an AppImage from the appimage.github.io catalog
  community.general.appimage:
    name: appimagetool

- name: Install the latest x86_64 AppImage from GitHub releases
  community.general.appimage:
    name: example
    url: https://github.com/example/example/releases
    state: latest
    asset_name: "*x86_64.AppImage"

- name: Install a specific GitHub release tag
  community.general.appimage:
    name: example
    url: https://github.com/example/example/releases
    version: v1.2.3

- name: Install an AppImage and create a desktop launcher
  community.general.appimage:
    name: example
    url: https://example.com/downloads/example.AppImage
    desktop_integration: true

- name: Remove an AppImage
  community.general.appimage:
    name: example
    state: absent
"""

RETURN = r"""
path:
  description: Path to the managed AppImage executable.
  returned: always
  type: str
  sample: /home/user/.local/bin/example
source_url:
  description: Resolved AppImage download URL.
  returned: when O(state) is V(present) or V(latest)
  type: str
  sample: https://github.com/example/example/releases/download/v1.2.3/example-x86_64.AppImage
desktop_file:
  description: Path to the managed desktop launcher.
  returned: when O(desktop_integration=true) or O(state=absent)
  type: str
  sample: /home/user/.local/share/applications/example.desktop
version:
  description: GitHub release tag that was installed.
  returned: when installing from a GitHub release
  type: str
  sample: v1.2.3
catalog_name:
  description: AppImage catalog entry name used to resolve the source.
  returned: when installing from the appimage.github.io catalog
  type: str
  sample: appimagetool
catalog_url:
  description: AppImage catalog page used to resolve the source.
  returned: when installing from the appimage.github.io catalog
  type: str
  sample: https://appimage.github.io/appimagetool/
"""

import fnmatch
import json
import os
import tempfile
from urllib.parse import urlparse

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def normalized_catalog_name(name):
    return "".join(c for c in name.lower() if c.isalnum())


def is_github_releases_url(url):
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    return parsed.netloc.lower() == "github.com" and len(path_parts) >= 3 and path_parts[2] == "releases"


def parse_github_releases_url(url):
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if not is_github_releases_url(url):
        raise ValueError("URL is not a GitHub releases page")
    owner = path_parts[0]
    repo = path_parts[1]
    tag = None
    if len(path_parts) >= 5 and path_parts[3] == "tag":
        tag = path_parts[4]
    return owner, repo, tag


def github_api_url(owner, repo, tag):
    if tag:
        return f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    return f"https://api.github.com/repos/{owner}/{repo}/releases/latest"


def appimage_catalog_name_url(catalog_name):
    return f"https://appimage.github.io/{catalog_name}/"


def response_body(response):
    if response is None:
        return b""
    return response.read()


def fetch_json(module, url, headers):
    response, info = fetch_url(
        module,
        url,
        headers=headers,
        method="GET",
        timeout=module.params["timeout"],
    )
    status = info.get("status", 0)
    if status != 200:
        module.fail_json(msg=f"Failed to fetch {url}", status=status, details=info.get("msg"))
    try:
        return json.loads(response_body(response).decode("utf-8"))
    except (TypeError, ValueError) as e:
        module.fail_json(msg=f"Failed to parse JSON from {url}: {e}")


def select_release_asset(module, release, asset_name):
    matches = []
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        download_url = asset.get("browser_download_url")
        if download_url and fnmatch.fnmatchcase(name, asset_name):
            matches.append(asset)

    if not matches:
        module.fail_json(
            msg=f"No AppImage asset matching {asset_name!r} was found in GitHub release {release.get('tag_name')}"
        )
    if len(matches) > 1:
        names = [asset["name"] for asset in matches]
        module.fail_json(
            msg=f"Multiple AppImage assets match {asset_name!r}; make asset_name more specific", assets=names
        )

    return matches[0]


def select_catalog_item(module, feed, name):
    items = feed.get("items") or []
    exact_matches = [item for item in items if item.get("name") == name]
    if exact_matches:
        return exact_matches[0]

    normalized_name = normalized_catalog_name(name)
    normalized_matches = [item for item in items if normalized_catalog_name(item.get("name", "")) == normalized_name]
    if not normalized_matches:
        module.fail_json(msg=f"No AppImage named {name!r} was found in the appimage.github.io catalog")
    if len(normalized_matches) > 1:
        names = [item["name"] for item in normalized_matches]
        module.fail_json(
            msg=f"Multiple AppImage catalog entries match {name!r}; use the exact catalog name", catalog_names=names
        )

    return normalized_matches[0]


def select_catalog_download_url(module, item):
    links = item.get("links") or []
    download_links = [link for link in links if link.get("type") == "Download" and link.get("url")]
    github_links = [link for link in links if link.get("type") == "GitHub" and link.get("url")]

    if download_links:
        return download_links[0]["url"]
    if github_links:
        github_url = github_links[0]["url"]
        if github_url.startswith("http://") or github_url.startswith("https://"):
            return github_url.rstrip("/") + "/releases"
        return f"https://github.com/{github_url.strip('/')}/releases"

    module.fail_json(msg=f"AppImage catalog entry {item.get('name')!r} does not contain a supported download link")


def resolve_url_source(module, url, catalog_name=None):
    if is_github_releases_url(url):
        owner, repo, tag_from_url = parse_github_releases_url(url)
        tag = module.params["version"] or tag_from_url
        headers = {}
        if module.params["github_token"]:
            headers["Authorization"] = f"Bearer {module.params['github_token']}"
        release = fetch_json(module, github_api_url(owner, repo, tag), headers)
        asset = select_release_asset(module, release, module.params["asset_name"])
        source = {
            "source_url": asset["browser_download_url"],
            "asset_name": asset.get("name"),
            "version": release.get("tag_name"),
        }
        if catalog_name:
            source["catalog_name"] = catalog_name
        return source

    if not urlparse(url).path.lower().endswith(".appimage"):
        module.fail_json(
            msg=(
                f"Resolved URL {url!r} is not a direct AppImage URL or GitHub releases page. "
                "Use url to provide a supported AppImage source explicitly."
            )
        )

    source = {
        "source_url": url,
        "asset_name": os.path.basename(urlparse(url).path),
        "version": None,
    }
    if catalog_name:
        source["catalog_name"] = catalog_name
    return source


def resolve_catalog_source(module):
    feed = fetch_json(module, module.params["catalog_url"], {})
    item = select_catalog_item(module, feed, module.params["name"])
    download_url = select_catalog_download_url(module, item)
    source = resolve_url_source(module, download_url, catalog_name=item.get("name"))
    source["catalog_url"] = appimage_catalog_name_url(item.get("name"))
    return source


def resolve_source(module):
    url = module.params["url"]
    if url:
        return resolve_url_source(module, url)
    return resolve_catalog_source(module)


def metadata_path(path):
    return f"{path}.appimage.json"


def load_metadata(path):
    meta_path = metadata_path(path)
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_metadata(path, metadata):
    with open(metadata_path(path), "w", encoding="utf-8") as f:
        json.dump(metadata, f, sort_keys=True, indent=2)
        f.write("\n")


def needs_install(path, state, source):
    if not os.path.exists(path):
        return True
    if state != "latest":
        return False
    metadata = load_metadata(path)
    return metadata.get("source_url") != source.get("source_url") or metadata.get("version") != source.get("version")


def download_appimage(module, source_url, dest):
    response, info = fetch_url(
        module,
        source_url,
        method="GET",
        timeout=module.params["timeout"],
    )
    status = info.get("status", 0)
    if status != 200:
        module.fail_json(msg=f"Failed to download AppImage from {source_url}", status=status, details=info.get("msg"))

    install_dir = os.path.dirname(dest)
    fd, tmp_path = tempfile.mkstemp(prefix=".ansible-appimage-", dir=install_dir)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            tmp_file.write(response_body(response))
        os.chmod(tmp_path, 0o755)
        module.atomic_move(tmp_path, dest)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def desktop_file_path(name):
    base_dir = os.path.expanduser("~/.local/share/applications")
    return os.path.join(base_dir, f"{name}.desktop")


def desired_desktop_file(name, executable):
    return f"[Desktop Entry]\nType=Application\nName={name}\nExec={executable}\nTerminal=false\nCategories=Utility;\n"


def ensure_desktop_file(path, content, check_mode):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return False
    if not check_mode:
        os.makedirs(os.path.dirname(path), mode=0o755, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return True


def remove_file(path, check_mode):
    if not os.path.exists(path):
        return False
    if not check_mode:
        os.unlink(path)
    return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            url=dict(type="str"),
            state=dict(type="str", default="present", choices=["absent", "present", "latest"]),
            install_dir=dict(type="path", default="~/.local/bin"),
            desktop_integration=dict(type="bool", default=False),
            version=dict(type="str"),
            asset_name=dict(type="str", default="*.AppImage"),
            github_token=dict(type="str", no_log=True),
            catalog_url=dict(type="str", default="https://appimage.github.io/feed.json"),
            validate_certs=dict(type="bool", default=True),
            timeout=dict(type="int", default=30),
        ),
        supports_check_mode=True,
    )

    state = module.params["state"]
    name = module.params["name"]
    install_dir = os.path.expanduser(module.params["install_dir"])
    path = os.path.join(install_dir, name)
    desktop_path = desktop_file_path(name)
    result = {"changed": False, "path": path}

    if state == "absent":
        result["changed"] = remove_file(path, module.check_mode)
        result["changed"] = remove_file(metadata_path(path), module.check_mode) or result["changed"]
        result["changed"] = remove_file(desktop_path, module.check_mode) or result["changed"]
        result["desktop_file"] = desktop_path
        module.exit_json(**result)

    source = resolve_source(module)
    result.update(source)

    if needs_install(path, state, source):
        result["changed"] = True
        if not module.check_mode:
            os.makedirs(install_dir, mode=0o755, exist_ok=True)
            download_appimage(module, source["source_url"], path)
            write_metadata(path, source)

    if module.params["desktop_integration"]:
        result["desktop_file"] = desktop_path
        content = desired_desktop_file(name, path)
        result["changed"] = ensure_desktop_file(desktop_path, content, module.check_mode) or result["changed"]

    module.exit_json(**result)


if __name__ == "__main__":
    main()
