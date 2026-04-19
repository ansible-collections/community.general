# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

__all__ = ["CryptContext", "has_crypt_context"]

has_crypt_context = True
try:
    from passlib.context import CryptContext

except ImportError:
    try:
        try:
            import crypt as _crypt_mod
        except ImportError:
            import legacycrypt as _crypt_mod

        _SCHEME_TO_METHOD = {
            "sha512_crypt": _crypt_mod.METHOD_SHA512,
            "sha256_crypt": _crypt_mod.METHOD_SHA256,
            "md5_crypt": _crypt_mod.METHOD_MD5,
            "des_crypt": _crypt_mod.METHOD_CRYPT,
        }

        class CryptContext:  # type: ignore[no-redef]
            @staticmethod
            def verify(password, password_hash):
                return _crypt_mod.crypt(password, password_hash) == password_hash

            @staticmethod
            def hash(password, scheme="sha512_crypt", rounds=10000):
                method = _SCHEME_TO_METHOD.get(scheme)
                if method is None:
                    raise ValueError(f"Unsupported scheme: {scheme}")
                salt = _crypt_mod.mksalt(method, rounds=rounds)
                return _crypt_mod.crypt(password, salt)

    except ImportError:

        class CryptContext:  # type: ignore[no-redef]
            pass

        has_crypt_context = False
