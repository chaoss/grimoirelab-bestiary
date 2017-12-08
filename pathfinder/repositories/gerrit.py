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
from fetch.gerrit import GerritFetcher

logger = logging.getLogger(__name__)


class ReposGerrit(Repos):
    """ Get the list of repositories from Gerrit """

    def __init__(self, host, user):
        super().__init__(host, user=user)

    def get_ids(self):
        repo_list = self.get_repos()
        repo_ids_list = [self.get_id(repo) for repo in repo_list]

        return repo_ids_list

    def get_id(self, repo):
        return repo

    def get_repos(self):
        """ Get the repository list for a data sources for all projects """
        projects_raw = GerritFetcher(self.host, self.user).fetch()
        projects = projects_raw.split("\n")
        repos = ['https://' + self.host + '/r/' + project for project in projects]
        return repos
