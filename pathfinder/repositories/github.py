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


from .repositories import Repos
from fetch.github import GitHubFetcher

logger = logging.getLogger(__name__)


class ReposGitHub(Repos):
    """ Get the list of repositories from a GitHub owner """

    def __init__(self, host, owner, api_token):
        super().__init__(host, user=owner, api_token=api_token)

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

        repos = GitHubFetcher(self.host, api_token=self.api_token).fetch(self.user)

        return repos
