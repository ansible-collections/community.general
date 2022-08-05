#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

# Delete traces from last run
rm -rf appdir* dummy-repo.gpg gpg hello.sh repo

# Create GPG key
mkdir -p gpg
chmod 0700 gpg
gpg --homedir gpg --batch --passphrase '' --quick-gen-key test@dummy.com future-default default 10y
KEY_ID=$(gpg --homedir=gpg --list-keys --with-colons test@dummy.com | grep fpr: | head -1 | cut -d ':' -f 10)
gpg --homedir=gpg --export "${KEY_ID}" > dummy-repo.gpg
BASE64_PUBLIC_KEY=$(base64 dummy-repo.gpg | tr -d '\n')

# Install dependencies
flatpak install -y --system flathub org.freedesktop.Platform//1.6 org.freedesktop.Sdk//1.6

# Add individual flatpaks
echo $'#!/bin/sh\necho hello world' > hello.sh

for NUM in 1 2 3; do
    flatpak build-init appdir${NUM} com.dummy.App${NUM} org.freedesktop.Sdk org.freedesktop.Platform 1.6;
    flatpak build appdir${NUM} mkdir /app/bin;
    flatpak build appdir${NUM} install --mode=750 hello.sh /app/bin;
    flatpak build-finish --command=hello.sh appdir${NUM}

    flatpak build-export repo appdir${NUM} stable

    cat > repo/com.dummy.App${NUM}.flatpakref <<EOF
        [Flatpak Ref]
        Title=Dummy App${NUM}
        Name=com.dummy.App${NUM}
        Branch=stable
        Url=file:///tmp/flatpak/repo
        GPGKey=${BASE64_PUBLIC_KEY}
        IsRuntime=false
        RuntimeRepo=https://flathub.org/repo/flathub.flatpakrepo
EOF
done

# Build repository
cat > repo/dummy-repo.flatpakrepo <<EOF
    [Flatpak Repo]
    Title=Dummy Repo
    Url=file:///tmp/flatpak/repo
    Comment=Dummy repo for ansible module integration testing
    Description=Dummy repo for ansible module integration testing
    GPGKey=${BASE64_PUBLIC_KEY}
EOF

flatpak build-sign repo --gpg-sign="${KEY_ID}" --gpg-homedir=gpg
flatpak build-update-repo repo --gpg-sign="${KEY_ID}" --gpg-homedir=gpg

# Compress repository
tar cvfJ repo.tar.xz repo/
mv repo.tar.xz files/

# Cleanup
rm -rf appdir* dummy-repo.gpg gpg hello.sh repo
