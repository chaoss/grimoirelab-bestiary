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

from .fetcher import Fetcher


logger = logging.getLogger(__name__)


class GitHubFetcher(Fetcher):
    """Fetch github repositories"""

    GITHUB_API_URL = "https://api.github.com"
    MAX_RETRIES = 3  # max number of retries when a request fails
    RETRY_WAIT = 10  # number of seconds when retrying HTTP request

    def __init__(self, host, api_token):
        super().__init__(host, api_token=api_token)

    def fetch(self, owner):
        return [data for data in self.__fetch(owner)]

    def __fetch(self, owner):
        headers = {'Authorization': 'token ' + self.api_token}
        params = {
            'per_page': 100 # Maximum limit by the API
        }

        url = self.__get_owner_repos_url(owner, headers, params)

        while True:
            response = self._call(url, headers, params)
            for repository in response.json():
                yield repository

            if response.links and 'next' in response.links:
                url = response.links['next']['url']
            else:
                break


    def __get_owner_repos_url(self, owner, headers, params):
        """ The owner could be a org or a user.
            It waits if need to have rate limit.
        """
        url_org = self.GITHUB_API_URL+"/orgs/"+owner+"/repos"
        url_user = self.GITHUB_API_URL+"/users/"+owner+"/repos"

        url_owner = url_org  # Use org by default

        try:
            res = self._call(url_owner, headers, params)
        except requests.exceptions.HTTPError:
            # owner is not an org, try with a user
            res = self._call(url_user, headers, params)
            res.raise_for_status()
            url_owner = url_user

        return url_owner
