# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Miguel Ángel Fernández <mafesan@bitergia.com>
#
import base64
import os
import re
import string

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, modes, algorithms
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.utils.encoding import force_bytes


def validate_field(name, value, allow_none=False):
    """Validate a given string field following a set of rules.

    The conditions to validate `value` consists on checking if its value is `None`
    and if this is allowed or not; if its value is not an empty string or if it is
    not composed only by whitespaces and/or tabs.

    :param name: name of the field to validate
    :param value: value of the field to validate
    :param allow_none: `True` if `None` values are permitted, `False` otherwise

    :raises ValueError: when a condition to validate the string is not satisfied
    :raises TypeError: when the input value is not a string and not `None`
    """
    if value is None:
        if not allow_none:
            raise ValueError("'{}' cannot be None".format(name))
        else:
            return

    if not isinstance(value, str):
        msg = "field '{}' value must be a string; {} given".format(name, value.__class__.__name__)
        raise TypeError(msg)

    if value == '':
        raise ValueError("'{}' cannot be an empty string".format(name))

    m = re.match(r"^\s+$", value)
    if m:
        raise ValueError("'{}' cannot be composed by whitespaces only".format(name))


def validate_name(name):
    """Validate a string field checking if it follows a set of rules

    The conditions to validate `name` consists on:
     - Checking the conditions from `validate_field`.
     - Checking if the first character is alphanumeric.
     - Checking if the string contains whitespace characters.
     - Checking if the string punctuation characters, different from hyphens.

    :param name: string to validate

    :raises ValueError: when a condition to validate the string is not satisfied
    :raises TypeError: when the input value is not a string and not `None`
    """

    def contains_whitespace(s):
        """Check if a string contains any whitespace characters"""

        for c in s:
            if c in string.whitespace:
                return True
        return False

    def contains_punctuation(s):
        """Check if a string contains any punctuation characters
        distinct from hyphens
        """
        unaccepted_chars = string.punctuation.replace('-', '')
        for c in s:
            if c in unaccepted_chars:
                return True
        return False

    validate_field('name', name)

    if not name[0].isalnum():
        raise ValueError("'name' must start with an alphanumeric character")
    if contains_whitespace(name):
        raise ValueError("'name' cannot contain whitespace characters")
    if contains_punctuation(name):
        raise ValueError("'name' cannot contain punctuation characters except hyphens")


class Crypto:
    """Encrypt and decrypt data using a given key.

    This class derives the key provided to make it suitable
    for use as input to an asymmetric algorithm.
    Given some data as input, returns an encrypted value.
    It also include the reverse method to decrypt.
    """
    def __init__(self, key):
        kdf = HKDF(algorithm=hashes.SHA256(),
                   length=32,
                   salt=None,
                   info=b"hkdf-secret-key")
        self.key = kdf.derive(force_bytes(key))

    def encrypt(self, data):
        """Encrypt the given data.

        :param data: object to encrypt.

        :returns: encrypted binary object
        """
        iv = os.urandom(16)

        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CTR(iv)
        ).encryptor()

        ciphertext = encryptor.update(force_bytes(data)) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext)

    def decrypt(self, data):
        """Decrypt the given data.

        :param data: binary object to decrypt.

        :returns: decrypted binary object.
        """
        enc = base64.b64decode(data)
        iv = enc[:16]
        ciphertext = enc[16:]

        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.CTR(iv)
        ).decryptor()

        return decryptor.update(ciphertext) + decryptor.finalize()
