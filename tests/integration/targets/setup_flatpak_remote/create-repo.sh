#!/usr/bin/env bash
set -eux

flatpak install -y --system flathub org.freedesktop.Platform//1.6 org.freedesktop.Sdk//1.6

echo $'#!/bin/sh\necho hello world' > hello.sh

export NUM=1
flatpak build-init appdir$NUM com.dummy.App$NUM org.freedesktop.Sdk org.freedesktop.Platform 1.6;
flatpak build appdir$NUM mkdir /app/bin;
flatpak build appdir$NUM install --mode=750 hello.sh /app/bin;
flatpak build-finish --command=hello.sh appdir$NUM

flatpak build-export repo appdir$NUM stable

mkdir -p gpg
chmod 0700 gpg
gpg --homedir gpg --batch --passphrase '' --quick-gen-key test@dummy.com future-default default 10y

KEY_ID=$(gpg --homedir=gpg --list-keys --with-colons test@dummy.com | grep fpr: | head -1 | cut -d ':' -f 10)

gpg --homedir=gpg --export "${KEY_ID}" > dummy-repo.gpg

BASE64_PUBLIC_KEY=$(base64 dummy-repo.gpg | tr -d '\n')

cat > repo/com.dummy.App1.flatpakref <<EOF
[Flatpak Ref]
Title=Dummy App$NUM
Name=com.dummy.App$NUM
Branch=stable
Url=file:///tmp/flatpak/repo
GPGKey=${BASE64_PUBLIC_KEY}
IsRuntime=false
RuntimeRepo=https://flathub.org/repo/flathub.flatpakrepo
EOF

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
tar cvfJ repo.tar.xz repo/
mv repo.tar.xz files/

rm -rf appdir* dummy-repo.gpg gpg hello.sh repo
