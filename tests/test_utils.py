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

from bestiary.core.utils import validate_field


FIELD_NONE_ERROR = "'{name}' cannot be None"
FIELD_EMPTY_ERROR = "'{name}' cannot be an empty string"
FIELD_WHITESPACES_ERROR = "'{name}' cannot be composed by whitespaces only"
FIELD_TYPE_ERROR = "field value must be a string; int given"


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

        with self.assertRaisesRegex(TypeError, FIELD_TYPE_ERROR):
            validate_field('test_field', 42)
