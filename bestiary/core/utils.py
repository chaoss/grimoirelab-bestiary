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

import re


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
        msg = "field value must be a string; {} given".format(value.__class__.__name__)
        raise TypeError(msg)

    if value == '':
        raise ValueError("'{}' cannot be an empty string".format(name))

    m = re.match(r"^\s+$", value)
    if m:
        raise ValueError("'{}' cannot be composed by whitespaces only".format(name))
