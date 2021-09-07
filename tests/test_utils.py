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

from django.test import TestCase

from bestiary.core.utils import (validate_field,
                                 validate_name,
                                 Crypto)


FIELD_NONE_ERROR = "'{name}' cannot be None"
FIELD_EMPTY_ERROR = "'{name}' cannot be an empty string"
FIELD_WHITESPACES_ERROR = "'{name}' cannot be composed by whitespaces only"
FIELD_TYPE_ERROR = "field '{name}' value must be a string; int given"
FIELD_START_ALPHANUM_ERROR = "'{name}' must start with an alphanumeric character"
FIELD_MAX_LENGTH_ERROR = "'{name}' length is exceeded"
FIELD_CONTAINS_WHITESPACES_ERROR = "'{name}' cannot contain whitespace characters"
FIELD_CONTAINS_PUNCTUATION_ERROR = "'{name}' cannot contain punctuation characters except hyphens"


class TestValidateField(TestCase):
    """Unit tests for validate_field"""

    def test_validate_string(self):
        """Check valid fields"""

        # If the field is valid, the method does not raise any exception
        validate_field('test_field', 'Test')

    def test_invalid_string(self):
        """Check invalid string fields"""

        expected = FIELD_EMPTY_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', '')

        expected = FIELD_WHITESPACES_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', '\t')

        expected = FIELD_WHITESPACES_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', '  \t ')

    def test_allow_none(self):
        """Check valid and invalid fields allowing `None` values"""

        validate_field('test_field', None, allow_none=True)

        expected = FIELD_NONE_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', None, allow_none=False)

        expected = FIELD_EMPTY_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', '', allow_none=True)

        expected = FIELD_WHITESPACES_ERROR.format(name='test_field')
        with self.assertRaisesRegex(ValueError, expected):
            validate_field('test_field', ' \t ', allow_none=True)

    def test_no_string(self):
        """Check if an exception is raised when the value type is not a string"""

        with self.assertRaisesRegex(TypeError, FIELD_TYPE_ERROR.format(name='test_field')):
            validate_field('test_field', 42)


class TestValidateName(TestCase):
    """Unit tests for validate_name"""

    def test_validate_name(self):
        """Check valid value"""

        # If the field is valid, the method does not raise any exception
        validate_name('Test-Value')

    def test_name_empty(self):
        """Check if it fails when name is an empty string"""

        expected = FIELD_EMPTY_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name('')

    def test_name_none(self):
        """Check if it fails when name is `None`"""

        expected = FIELD_NONE_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name(None)

    def test_name_int(self):
        """Check if an exception is raised when the value type is not a string"""

        with self.assertRaisesRegex(TypeError, FIELD_TYPE_ERROR.format(name='name')):
            validate_name(42)

    def test_name_not_alphanum(self):
        """Check if it fails when name does not start with an alphanumeric character"""

        expected = FIELD_START_ALPHANUM_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name('-Test')

    def test_name_contains_whitespace(self):
        """Check if it fails when name contains any whitespace characters"""

        expected = FIELD_CONTAINS_WHITESPACES_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name('Test example')

        expected = FIELD_WHITESPACES_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name(' ')

        expected = FIELD_WHITESPACES_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name('\t')

    def test_name_contains_punctuation(self):
        """Check if it fails when name contains any punctuation characters distinct from hyphens"""

        expected = FIELD_CONTAINS_PUNCTUATION_ERROR.format(name='name')
        with self.assertRaisesRegex(ValueError, expected):
            validate_name('Test-example(2)')


class TestCrypto(TestCase):
    """Unit tests for Crypto to encrypt and decrypt"""

    def test_initialization(self):
        """Check if Crypto is initialized correctly"""

        crypto = Crypto('1234')
        self.assertIsInstance(crypto, Crypto)

    def test_encrypt_decrypt(self):
        """Check if it can encrypt and decrypt using same key"""

        crypto = Crypto('1234')
        encrypted = crypto.encrypt('testing')
        self.assertIsInstance(encrypted, bytes)

        decrypted = crypto.decrypt(encrypted)
        self.assertIsInstance(decrypted, bytes)
        self.assertEqual(decrypted, b'testing')

    def test_decrypt_new_instance(self):
        """Check if it can decrypt using a different object with same key"""

        crypto_1 = Crypto('1234')
        encrypted = crypto_1.encrypt('testing')
        self.assertIsInstance(encrypted, bytes)

        crypto_2 = Crypto('1234')
        decrypted = crypto_2.decrypt(encrypted)
        self.assertIsInstance(decrypted, bytes)
        self.assertEqual(decrypted, b'testing')

    def test_wrong_key(self):
        """Try to decrypt using the wrong key"""

        crypto = Crypto('1234')
        encrypted = crypto.encrypt('testing')

        crypto_2 = Crypto('4321')
        decrypted = crypto_2.decrypt(encrypted)
        self.assertNotEqual(decrypted, b'testing')
