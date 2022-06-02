# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.

# Copyright: (c) 2020, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
#
# Simplified BSD License (see simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from stringprep import (
    in_table_a1,
    in_table_b1,
    in_table_c3,
    in_table_c4,
    in_table_c5,
    in_table_c6,
    in_table_c7,
    in_table_c8,
    in_table_c9,
    in_table_c12,
    in_table_c21_c22,
    in_table_d1,
    in_table_d2,
)
from unicodedata import normalize

from ansible.module_utils.six import text_type


def is_unicode_str(string):
    return True if isinstance(string, text_type) else False


def mapping_profile(string):
    """RFC4013 Mapping profile implementation."""
    # Regarding RFC4013,
    # This profile specifies:
    #   -  non-ASCII space characters [StringPrep, C.1.2] that can be
    #      mapped to SPACE (U+0020), and
    #   -  the "commonly mapped to nothing" characters [StringPrep, B.1]
    #      that can be mapped to nothing.

    tmp = []
    for c in string:
        # If not the "commonly mapped to nothing"
        if not in_table_b1(c):
            if in_table_c12(c):
                # map non-ASCII space characters
                # (that can be mapped) to Unicode space
                tmp.append(u' ')
            else:
                tmp.append(c)

    return u"".join(tmp)


def is_ral_string(string):
    """RFC3454 Check bidirectional category of the string"""
    # Regarding RFC3454,
    # Table D.1 lists the characters that belong
    # to Unicode bidirectional categories "R" and "AL".
    # If a string contains any RandALCat character, a RandALCat
    # character MUST be the first character of the string, and a
    # RandALCat character MUST be the last character of the string.
    if in_table_d1(string[0]):
        if not in_table_d1(string[-1]):
            raise ValueError('RFC3454: incorrect bidirectional RandALCat string.')
        return True
    return False


def prohibited_output_profile(string):
    """RFC4013 Prohibited output profile implementation."""
    # Implements:
    # RFC4013, 2.3. Prohibited Output.
    # This profile specifies the following characters as prohibited input:
    #   - Non-ASCII space characters [StringPrep, C.1.2]
    #   - ASCII control characters [StringPrep, C.2.1]
    #   - Non-ASCII control characters [StringPrep, C.2.2]
    #   - Private Use characters [StringPrep, C.3]
    #   - Non-character code points [StringPrep, C.4]
    #   - Surrogate code points [StringPrep, C.5]
    #   - Inappropriate for plain text characters [StringPrep, C.6]
    #   - Inappropriate for canonical representation characters [StringPrep, C.7]
    #   - Change display properties or deprecated characters [StringPrep, C.8]
    #   - Tagging characters [StringPrep, C.9]
    # RFC4013, 2.4. Bidirectional Characters.
    # RFC4013, 2.5. Unassigned Code Points.

    # Determine how to handle bidirectional characters (RFC3454):
    if is_ral_string(string):
        # If a string contains any RandALCat characters,
        # The string MUST NOT contain any LCat character:
        is_prohibited_bidi_ch = in_table_d2
        bidi_table = 'D.2'
    else:
        # Forbid RandALCat characters in LCat string:
        is_prohibited_bidi_ch = in_table_d1
        bidi_table = 'D.1'

    RFC = 'RFC4013'
    for c in string:
        # RFC4013 2.3. Prohibited Output:
        if in_table_c12(c):
            raise ValueError('%s: prohibited non-ASCII space characters '
                             'that cannot be replaced (C.1.2).' % RFC)
        if in_table_c21_c22(c):
            raise ValueError('%s: prohibited control characters (C.2.1).' % RFC)
        if in_table_c3(c):
            raise ValueError('%s: prohibited private Use characters (C.3).' % RFC)
        if in_table_c4(c):
            raise ValueError('%s: prohibited non-character code points (C.4).' % RFC)
        if in_table_c5(c):
            raise ValueError('%s: prohibited surrogate code points (C.5).' % RFC)
        if in_table_c6(c):
            raise ValueError('%s: prohibited inappropriate for plain text '
                             'characters (C.6).' % RFC)
        if in_table_c7(c):
            raise ValueError('%s: prohibited inappropriate for canonical '
                             'representation characters (C.7).' % RFC)
        if in_table_c8(c):
            raise ValueError('%s: prohibited change display properties / '
                             'deprecated characters (C.8).' % RFC)
        if in_table_c9(c):
            raise ValueError('%s: prohibited tagging characters (C.9).' % RFC)

        # RFC4013, 2.4. Bidirectional Characters:
        if is_prohibited_bidi_ch(c):
            raise ValueError('%s: prohibited bidi characters (%s).' % (RFC, bidi_table))

        # RFC4013, 2.5. Unassigned Code Points:
        if in_table_a1(c):
            raise ValueError('%s: prohibited unassigned code points (A.1).' % RFC)


def saslprep(string):
    """RFC4013 implementation.
    Implements "SASLprep" profile (RFC4013) of the "stringprep" algorithm (RFC3454)
    to prepare Unicode strings representing user names and passwords for comparison.
    Regarding the RFC4013, the "SASLprep" profile is intended to be used by
    Simple Authentication and Security Layer (SASL) mechanisms
    (such as PLAIN, CRAM-MD5, and DIGEST-MD5), as well as other protocols
    exchanging simple user names and/or passwords.

    Args:
        string (unicode string): Unicode string to validate and prepare.

    Returns:
        Prepared unicode string.
    """
    # RFC4013: "The algorithm assumes all strings are
    # comprised of characters from the Unicode [Unicode] character set."
    # Validate the string is a Unicode string
    # (text_type is the string type if PY3 and unicode otherwise):
    if not is_unicode_str(string):
        raise TypeError('input must be of type %s, not %s' % (text_type, type(string)))

    # RFC4013: 2.1. Mapping.
    string = mapping_profile(string)

    # RFC4013: 2.2. Normalization.
    # "This profile specifies using Unicode normalization form KC."
    string = normalize('NFKC', string)
    if not string:
        return u''

    # RFC4013: 2.3. Prohibited Output.
    # RFC4013: 2.4. Bidirectional Characters.
    # RFC4013: 2.5. Unassigned Code Points.
    prohibited_output_profile(string)

    return string
