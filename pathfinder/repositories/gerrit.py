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
import subprocess

import requests

from .repositories import Repos

logger = logging.getLogger(__name__)

class ReposGerrit(Repos):
    """ Get the list of repositories from Gerrit """

    def __init__(self, gerrit_url, gerrit_user, data_source='git'):
        self.url = gerrit_url
        self.user = gerrit_user
        self.data_source = data_source

    def __run(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = proc.communicate()
        errs_str = errs.decode("utf8")
        outs_str = outs.decode("utf8")

        return (errs_str, outs_str)


    def get_ids(self):
        repo_list = self.get_repos()
        repo_ids_list = [self.get_id(repo) for repo in repo_list]

        return repo_ids_list

    def get_id(self, repo):
        return repo

    def get_repos(self):
        """ Get the repository list for a data sources for all projects """
        cmd = ['ssh', '-p', '29418', self.user+"@"+self.url, "gerrit"]
        cmd += ['ls-projects']
        (errs_str, outs_str) = self.__run(cmd)
        projects = outs_str.split("\n")
        repos = ['https://' + self.url + '/r/' + project for project in projects]
        return repos
