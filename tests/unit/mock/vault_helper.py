# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.common.text.converters import to_bytes

from ansible.parsing.vault import VaultSecret


class TextVaultSecret(VaultSecret):
    '''A secret piece of text. ie, a password. Tracks text encoding.

    The text encoding of the text may not be the default text encoding so
    we keep track of the encoding so we encode it to the same bytes.'''

    def __init__(self, text, encoding=None, errors=None, _bytes=None):
        super(TextVaultSecret, self).__init__()
        self.text = text
        self.encoding = encoding or 'utf-8'
        self._bytes = _bytes
        self.errors = errors or 'strict'

    @property
    def bytes(self):
        '''The text encoded with encoding, unless we specifically set _bytes.'''
        return self._bytes or to_bytes(self.text, encoding=self.encoding, errors=self.errors)
