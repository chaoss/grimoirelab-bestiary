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
import shutil

logger = logging.getLogger(__name__)


class Projects():
    def __init__(self, projects_file):
        self.projects_file = projects_file
        with open(self.projects_file, "r") as fprojects:
            self.projects = json.load(fprojects)

    def __check_project(self, project):
        if project not in self.projects:
            msg_error = "Can't find %s in %s" % (project, self.projects.keys())
            raise RuntimeError(msg_error)

    def update_project_repos(self, project, data_source, repos):
        self.__check_project(project)

        self.projects[project][data_source] = repos
        self.projects[project][data_source] = list(set(self.projects[project][data_source]))

    def set_project_repos(self, project, data_source, repos):
        self.__check_project(project)

        self.projects[project][data_source] = repos

    def get_project_repos(self, project, data_source):
        self.__check_project(project)

        return self.projects[project][data_source]

    def get_projects(self):
        return self.projects.keys()

    def get_project_data_sources(self, project):
        self.__check_project(project)

        return self.projects[project].keys()

    def dump(self):
        # Backup the projects file
        shutil.copy(self.projects_file, self.projects_file + ".bak")
        with open(self.projects_file, "w") as fprojects:
            json.dump(self.projects, fprojects, sort_keys=True, indent=4)

        logging.info("Projects file updated %s", self.projects_file)
