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
  - The module installs AppImage files into a user-controlled directory.
  - Sources can be local AppImage files, direct AppImage URLs, GitHub release pages containing AppImage assets,
    or U(https://appimage.github.io) catalog entries.
author:
  - Travis Beale (@travisbeale)
extends_documentation_fragment:
  - community.general._attributes
  - ansible.builtin.files
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the managed AppImage.
      - This is used as the installed executable filename.
      - When O(url) is omitted, this is also used to look up the AppImage in the U(https://appimage.github.io) catalog.
    type: str
    required: true
  url:
    description:
      - Source used to install the AppImage.
      - This can point directly to an AppImage URL, a local AppImage file path, a V(file://) AppImage URL,
        or to a GitHub releases page such as V(https://github.com/OWNER/REPO/releases)
        or V(https://github.com/OWNER/REPO/releases/tag/TAG).
      - When omitted with O(state=present) or O(state=latest), the module looks up O(name) in the U(https://appimage.github.io) catalog.
    type: str
  state:
    description:
      - Desired state of the AppImage.
      - When O(state=present), the AppImage is installed if missing.
      - When O(state=latest), sources that support multiple versions, such as GitHub releases pages,
        are resolved to the latest release and updated when the recorded version differs.
      - O(state=latest) cannot be combined with O(version), and is not supported for fixed sources such
        as direct AppImage URLs or local files.
    type: str
    choices: [absent, present, latest]
    default: present
  install_dir:
    description:
      - Directory where the AppImage executable is installed.
    type: path
    default: "~/.local/bin"
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
      - URL of the U(https://appimage.github.io)-compatible JSON feed used when O(url) is omitted.
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

- name: Install an AppImage from a local file
  community.general.appimage:
    name: example
    url: /tmp/example-x86_64.AppImage

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
source_path:
  description: Local AppImage source path.
  returned: when installing from a local path or V(file://) source
  type: str
  sample: /tmp/example-x86_64.AppImage
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
import shutil
import tempfile
from urllib.parse import unquote, urlparse

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def normalized_catalog_name(name):
    return "".join(c for c in name.lower() if c.isalnum())


def is_github_releases_url(url, parsed=None):
    if parsed is None:
        parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    return parsed.netloc.lower() == "github.com" and len(path_parts) >= 3 and path_parts[2] == "releases"


def parse_github_releases_url(url, parsed=None):
    if parsed is None:
        parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if not is_github_releases_url(url, parsed):
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


def github_api_url_from_releases_url(url, state, version, parsed=None):
    owner, repo, tag_from_url = parse_github_releases_url(url, parsed)
    tag = None if state == "latest" else version or tag_from_url
    return github_api_url(owner, repo, tag)


def appimage_catalog_name_url(catalog_name):
    return f"https://appimage.github.io/{catalog_name}/"


def response_text(response):
    if response is None:
        return ""
    return response.read().decode("utf-8")


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
        return json.loads(response_text(response))
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


def local_appimage_path(source, parsed=None):
    if parsed is None:
        parsed = urlparse(source)
    if parsed.scheme == "file":
        if parsed.netloc not in ("", "localhost"):
            return None
        return unquote(parsed.path)
    if parsed.scheme == "":
        return source
    return None


def resolve_local_source(module, source, parsed=None, catalog_name=None):
    path = local_appimage_path(source, parsed)
    if path is None:
        return None
    if module.params["state"] == "latest":
        module.fail_json(
            msg="state=latest is only supported for sources that provide release versions, such as GitHub releases pages"
        )
    if not path.lower().endswith(".appimage"):
        module.fail_json(
            msg=(
                f"Local source {source!r} is not an AppImage file. "
                "Use `url` to provide a supported AppImage source explicitly."
            )
        )
    if not os.path.isfile(path):
        module.fail_json(msg=f"Local AppImage source {path!r} does not exist or is not a file")
    resolved_path = os.path.abspath(path)
    result = {
        "source_path": resolved_path,
        "asset_name": os.path.basename(resolved_path),
        "version": None,
    }
    if catalog_name:
        result["catalog_name"] = catalog_name
    return result


def resolve_url_source(module, url, catalog_name=None):
    parsed = urlparse(url)
    local_source = resolve_local_source(module, url, parsed=parsed, catalog_name=catalog_name)
    if local_source is not None:
        return local_source

    if is_github_releases_url(url, parsed):
        if module.params["state"] == "latest" and module.params["version"]:
            module.fail_json(msg="state=latest cannot be combined with version")
        headers = {}
        if module.params["github_token"]:
            headers["Authorization"] = f"Bearer {module.params['github_token']}"
        release = fetch_json(
            module,
            github_api_url_from_releases_url(url, module.params["state"], module.params["version"], parsed),
            headers,
        )
        asset = select_release_asset(module, release, module.params["asset_name"])
        source = {
            "source_url": asset["browser_download_url"],
            "asset_name": asset.get("name"),
            "version": release.get("tag_name"),
        }
        if catalog_name:
            source["catalog_name"] = catalog_name
        return source

    if not parsed.path.lower().endswith(".appimage"):
        module.fail_json(
            msg=(
                f"Resolved URL {url!r} is not a direct AppImage URL or GitHub releases page. "
                "Use `url` to provide a supported AppImage source explicitly."
            )
        )
    if module.params["state"] == "latest":
        module.fail_json(
            msg="state=latest is only supported for sources that provide release versions, such as GitHub releases pages"
        )

    source = {
        "source_url": url,
        "asset_name": os.path.basename(parsed.path),
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
        with open(meta_path, "r") as f:
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
    return (
        metadata.get("source_url") != source.get("source_url")
        or metadata.get("source_path") != source.get("source_path")
        or metadata.get("version") != source.get("version")
    )


def atomic_install(module, source_file, dest):
    fd, tmp_path = tempfile.mkstemp(prefix=".ansible-appimage-", dir=module.tmpdir)
    with os.fdopen(fd, "wb") as tmp_file:
        shutil.copyfileobj(source_file, tmp_file)
    module.atomic_move(tmp_path, dest, unsafe_writes=module.params["unsafe_writes"])


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

    atomic_install(module, response, dest)


def copy_appimage(module, source_path, dest):
    with open(source_path, "rb") as source_file:
        atomic_install(module, source_file, dest)


def install_appimage(module, source, dest):
    if source.get("source_path"):
        copy_appimage(module, source["source_path"], dest)
    else:
        download_appimage(module, source["source_url"], dest)


def apply_file_attributes(module, path, changed):
    file_params = module.params.copy()
    if file_params.get("mode") is None:
        file_params["mode"] = "0755"
    file_args = module.load_file_common_arguments(file_params, path=path)
    return module.set_fs_attributes_if_different(file_args, changed)


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
            version=dict(type="str"),
            asset_name=dict(type="str", default="*.AppImage"),
            github_token=dict(type="str", no_log=True),
            catalog_url=dict(type="str", default="https://appimage.github.io/feed.json"),
            validate_certs=dict(type="bool", default=True),
            timeout=dict(type="int", default=30),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )

    state = module.params["state"]
    name = module.params["name"]
    install_dir = module.params["install_dir"]
    path = os.path.join(install_dir, name)
    result = {"changed": False, "path": path}

    if state == "absent":
        removed_appimage = remove_file(path, module.check_mode)
        removed_metadata = remove_file(metadata_path(path), module.check_mode)
        result["changed"] = removed_appimage or removed_metadata
        module.exit_json(**result)

    source = resolve_source(module)
    result.update(source)

    if needs_install(path, state, source):
        result["changed"] = True
        if not module.check_mode:
            os.makedirs(install_dir, exist_ok=True)
            install_appimage(module, source, path)
            write_metadata(path, source)

    if os.path.exists(path):
        result["changed"] = apply_file_attributes(module, path, result["changed"])

    module.exit_json(**result)


if __name__ == "__main__":
    main()
