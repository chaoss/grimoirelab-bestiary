# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Bitergia
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
#     Alvaro del Castillo <acs@bitergia.com>
#

import logging
import requests
import time

logger = logging.getLogger(__name__)


class Fetcher:
    """Fetch raw data"""

    MAX_RETRIES = 3  # max number of retries when a request fails
    RETRY_WAIT = 10  # number of seconds when retrying HTTP request

    def __init__(self, host, user=None, password=None, api_token=None):
        self.host = host
        self.user = user
        self.password = password
        self.api_token = api_token

    def fetch(self, owner=None):
        """ Fetch raw repository data """

        raise NotImplementedError

    def _call(self, url, headers=None, params=None):
        """ Get data from a remote URL with retry  """

        retries = 0

        while retries < self.MAX_RETRIES:
            try:
                response = requests.get(url, headers=headers, params=params)
                break
            except requests.exceptions.ConnectionError as ex:
                logger.error("github url %s failed: %s", url, ex)
                time.sleep(self.RETRY_WAIT * retries)
                retries += 1

        response.raise_for_status()

        return response
