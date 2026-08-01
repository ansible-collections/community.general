# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from ansible.module_utils import basic

from ansible_collections.community.general.plugins.modules import maven_artifact

pytestmark = pytest.mark.usefixtures("patch_ansible_module")

maven_metadata_example = b"""<?xml version="1.0" encoding="UTF-8"?>
<metadata>
   <groupId>junit</groupId>
   <artifactId>junit</artifactId>
   <versioning>
      <latest>4.13-beta-2</latest>
      <release>4.13-beta-2</release>
      <versions>
         <version>3.7</version>
         <version>3.8</version>
         <version>3.8.1</version>
         <version>3.8.2</version>
         <version>4.0</version>
         <version>4.1</version>
         <version>4.2</version>
         <version>4.3</version>
         <version>4.3.1</version>
         <version>4.4</version>
         <version>4.5</version>
         <version>4.6</version>
         <version>4.7</version>
         <version>4.8</version>
         <version>4.8.1</version>
         <version>4.8.2</version>
         <version>4.9</version>
         <version>4.10</version>
         <version>4.11-beta-1</version>
         <version>4.11</version>
         <version>4.12-beta-1</version>
         <version>4.12-beta-2</version>
         <version>4.12-beta-3</version>
         <version>4.12</version>
         <version>4.13-beta-1</version>
         <version>4.13-beta-2</version>
      </versions>
      <lastUpdated>20190202141051</lastUpdated>
   </versioning>
</metadata>
"""


@pytest.mark.parametrize(
    "patch_ansible_module, version_by_spec, version_choosed",
    [
        (None, "(,3.9]", "3.8.2"),
        (None, "3.0", "3.8.2"),
        (None, "[3.7]", "3.7"),
        (None, "[4.10, 4.12]", "4.12"),
        (None, "[4.10, 4.12)", "4.11"),
        (None, "[2.0,)", "4.13-beta-2"),
    ],
)
def test_find_version_by_spec(mocker, version_by_spec, version_choosed):
    _getContent = mocker.patch(
        "ansible_collections.community.general.plugins.modules.maven_artifact.MavenDownloader._getContent"
    )
    _getContent.return_value = maven_metadata_example

    artifact = maven_artifact.Artifact("junit", "junit", None, version_by_spec, "jar")
    mvn_downloader = maven_artifact.MavenDownloader(basic.AnsibleModule, "https://repo1.maven.org/maven2")

    assert mvn_downloader.find_version_by_spec(artifact) == version_choosed


# Metadata with multiple snapshotVersion entries per extension (as produced by GitHub Packages).
# The entries are deliberately NOT in chronological order to verify that
# resolution uses the <updated> timestamp rather than relying on list position.
snapshot_metadata_multiple_entries = b"""<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>com.example</groupId>
  <artifactId>my-lib</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <versioning>
    <snapshot>
      <timestamp>20260210.152345</timestamp>
      <buildNumber>3</buildNumber>
    </snapshot>
    <lastUpdated>20260210153158</lastUpdated>
    <snapshotVersions>
      <snapshotVersion>
        <extension>jar</extension>
        <value>1.0.0-20260205.091032-2</value>
        <updated>20260205091858</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>jar</extension>
        <value>1.0.0-20260210.152345-3</value>
        <updated>20260210153154</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>pom</extension>
        <value>1.0.0-20260210.152345-3</value>
        <updated>20260210153153</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>jar</extension>
        <value>1.0.0-20260203.123107-1</value>
        <updated>20260203123944</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>pom</extension>
        <value>1.0.0-20260203.123107-1</value>
        <updated>20260203123943</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>pom</extension>
        <value>1.0.0-20260205.091032-2</value>
        <updated>20260205091857</updated>
      </snapshotVersion>
    </snapshotVersions>
  </versioning>
</metadata>
"""

# Metadata without a <snapshot> block but with <snapshotVersions> only.
snapshot_metadata_no_snapshot_block = b"""<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>com.example</groupId>
  <artifactId>my-lib</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <versioning>
    <lastUpdated>20260210153158</lastUpdated>
    <snapshotVersions>
      <snapshotVersion>
        <extension>jar</extension>
        <value>1.0.0-20260203.123107-1</value>
        <updated>20260203123944</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>pom</extension>
        <value>1.0.0-20260203.123107-1</value>
        <updated>20260203123943</updated>
      </snapshotVersion>
    </snapshotVersions>
  </versioning>
</metadata>
"""


@pytest.mark.parametrize("patch_ansible_module", [None])
def test_find_uri_for_snapshot_resolves_to_latest(mocker):
    """When metadata has multiple snapshotVersion entries per extension,
    the entry with the newest updated timestamp should be resolved."""
    _getContent = mocker.patch(
        "ansible_collections.community.general.plugins.modules.maven_artifact.MavenDownloader._getContent"
    )
    _getContent.return_value = snapshot_metadata_multiple_entries

    artifact = maven_artifact.Artifact("com.example", "my-lib", "1.0.0-SNAPSHOT", None, "", "jar")
    mvn_downloader = maven_artifact.MavenDownloader(basic.AnsibleModule, "https://repo.example.com")

    uri = mvn_downloader.find_uri_for_artifact(artifact)
    assert "1.0.0-20260210.152345-3.jar" in uri


@pytest.mark.parametrize("patch_ansible_module", [None])
def test_find_uri_for_snapshot_without_snapshot_block_uses_snapshot_versions(mocker):
    """When metadata lacks a <snapshot> block, fall back to scanning
    <snapshotVersions> entries."""
    _getContent = mocker.patch(
        "ansible_collections.community.general.plugins.modules.maven_artifact.MavenDownloader._getContent"
    )
    _getContent.return_value = snapshot_metadata_no_snapshot_block

    artifact = maven_artifact.Artifact("com.example", "my-lib", "1.0.0-SNAPSHOT", None, "", "jar")
    mvn_downloader = maven_artifact.MavenDownloader(basic.AnsibleModule, "https://repo.example.com")

    uri = mvn_downloader.find_uri_for_artifact(artifact)
    assert "1.0.0-20260203.123107-1.jar" in uri


# Metadata with a <snapshot> block that has <timestamp> but no <buildNumber>.
# This is schema-valid but non-standard (e.g. produced by non-Maven tools).
# The module should fall back to <snapshotVersions> scanning.
snapshot_metadata_incomplete_snapshot_block = b"""<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>com.example</groupId>
  <artifactId>my-lib</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <versioning>
    <snapshot>
      <timestamp>20260210.152345</timestamp>
    </snapshot>
    <lastUpdated>20260210153158</lastUpdated>
    <snapshotVersions>
      <snapshotVersion>
        <extension>jar</extension>
        <value>1.0.0-20260210.152345-3</value>
        <updated>20260210153154</updated>
      </snapshotVersion>
      <snapshotVersion>
        <extension>pom</extension>
        <value>1.0.0-20260210.152345-3</value>
        <updated>20260210153153</updated>
      </snapshotVersion>
    </snapshotVersions>
  </versioning>
</metadata>
"""


@pytest.mark.parametrize("patch_ansible_module", [None])
def test_find_uri_for_snapshot_incomplete_snapshot_block_uses_snapshot_versions(mocker):
    """When the <snapshot> block is incomplete (e.g. missing <buildNumber>),
    fall back to <snapshotVersions> instead of raising an error."""
    _getContent = mocker.patch(
        "ansible_collections.community.general.plugins.modules.maven_artifact.MavenDownloader._getContent"
    )
    _getContent.return_value = snapshot_metadata_incomplete_snapshot_block

    artifact = maven_artifact.Artifact("com.example", "my-lib", "1.0.0-SNAPSHOT", None, "", "jar")
    mvn_downloader = maven_artifact.MavenDownloader(basic.AnsibleModule, "https://repo.example.com")

    uri = mvn_downloader.find_uri_for_artifact(artifact)
    assert "1.0.0-20260210.152345-3.jar" in uri


@pytest.mark.parametrize("patch_ansible_module", [None])
def test_find_uri_for_release_version_unaffected(mocker):
    """Non-SNAPSHOT versions must not be affected by snapshot resolution logic."""
    artifact = maven_artifact.Artifact("com.example", "my-lib", "2.1.0", None, "", "jar")
    mvn_downloader = maven_artifact.MavenDownloader(basic.AnsibleModule, "https://repo.example.com")

    uri = mvn_downloader.find_uri_for_artifact(artifact)
    assert uri == "https://repo.example.com/com/example/my-lib/2.1.0/my-lib-2.1.0.jar"
