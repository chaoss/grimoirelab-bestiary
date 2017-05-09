#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2017 Bitergia
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

import logging

from datetime import datetime
from time import sleep

import requests

from .repositories import Repos

logger = logging.getLogger(__name__)

class ReposGitHub(Repos):
    """ Get the list of repositories from a GitHub owner """

    GITHUB_URL = "https://github.com/"
    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, owners, token):
        self.owners = owners
        self.token = token

    @classmethod
    def __get_payload(cls):
        # 100 max in repos
        payload = {'per_page': 100,
                   # 'fork': False,
                   'sort': 'updated', # does not work in repos listing
                   'direction': 'desc'}
        return payload

    def __get_headers(self):
        headers = {'Authorization': 'token ' + self.token}
        return headers

    def __call(self, url):
        """ Call to GitHub API """

        github_res = None

        while True:
            try:
                github_res = requests.get(url,
                                          params=self.__get_payload(),
                                          headers=self.__get_headers())
                github_res.raise_for_status()
                break
            except requests.exceptions.HTTPError as ex:
                if github_res.status_code == 403:
                    rate_limit_reset_ts = int(github_res.headers['X-RateLimit-Reset'])
                    rate_limit_reset_date = datetime.fromtimestamp(rate_limit_reset_ts)
                    seconds_to_reset = (rate_limit_reset_date - datetime.utcnow()).seconds+1
                    logger.info("GitHub rate limit exhausted. Waiting %i secs" + \
                                "for rate limit reset.", seconds_to_reset)
                    sleep(seconds_to_reset)
                else:
                    raise ex

        return github_res


    def __get_owner_repos_url(self, owner):
        """ The owner could be a org or a user.
            It waits if need to have rate limit.
        """
        url_org = self.GITHUB_API_URL+"/orgs/"+owner+"/repos"
        url_user = self.GITHUB_API_URL+"/users/"+owner+"/repos"

        url_owner = url_org  # Use org by default

        try:
            res = self.__call(url_owner)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            # owner is not an org, try with a user
            res = self.__call(url_user)
            res.raise_for_status()
            url_owner = url_user
        return url_owner

    def get_ids(self):
        repo_list = self.get_repos()
        repo_ids_list = [self.get_id(repo) for repo in repo_list]

        return repo_ids_list

    def get_id(self, repo):
        return repo['html_url']

    def get_is_fork(self, repo):
        return repo['fork']

    def get_repos(self):
        """ Get the repository list for all the owners """
        for owner in self.owners:
            owner_url = self.__get_owner_repos_url(owner)
            logger.debug("Getting repos from: %s", owner_url)

            while True:
                try:
                    repos_res = self.__call(owner_url)
                    for repo in repos_res.json():
                        yield repo

                    logger.debug("Rate limit: %s", repos_res.headers['X-RateLimit-Remaining'])

                    if 'next' not in repos_res.links:
                        break

                    owner_url = repos_res.links['next']['url']  # Loving requests :)
                except requests.exceptions.ConnectionError:
                    logger.error("Can not connect to GitHub")
                    break
