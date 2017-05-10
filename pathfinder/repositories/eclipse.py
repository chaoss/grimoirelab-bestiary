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

import json
import logging

import requests

from VizGrimoireUtils.eclipse.eclipse_projects_lib import (
    get_repos_list,
    get_project_repos)

from .repositories import Repos
from fetch.eclipse import EclipseFetcher

logger = logging.getLogger(__name__)

class ReposEclipse(Repos):
    """ Get the list of repositories from Eclipse projects remote JSON file """

    ECLIPSE_PROJECTS_URL = "http://projects.eclipse.org/json/projects/all"
    ECLIPSE_DATA_SOURCES = ['its', 'mls', 'scm', 'scr']


    def __init__(self, data_source='git'):
        self.data_source = data_source
        if data_source == 'git':
            self.data_source = 'scm'
        super().__init__(None, data_source=self.data_source)

        if self.data_source not in self.ECLIPSE_DATA_SOURCES:
            raise RuntimeError("Data source %s does not exists in Eclipse", data_source)

        self.eclipse_projects = EclipseFetcher().fetch()

    def get_ids(self):
        repo_list = self.get_repos()
        repo_ids_list = [self.get_id(repo) for repo in repo_list]

        return repo_ids_list

    def get_id(self, repo):
        return repo

    def get_repos(self):
        """ Get the repository list for a data sources for all projects """
        return get_repos_list(self.eclipse_projects, self.data_source)

    def get_projects(self):
        return list(self.eclipse_projects.keys())

    def get_project_repos_id(self, project):
        return get_project_repos(project, self.eclipse_projects, self.data_source)
