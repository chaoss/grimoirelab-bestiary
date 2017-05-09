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

logger = logging.getLogger(__name__)


class Repos():
    def __init__(self):
        """ Empty constructor """
        pass

    def get_repos(self):
        """ Return a generator of repositories """
        raise NotImplementedError

    def get_ids(self):
        """ Return a generator of repositories ids """
        raise NotImplementedError

    def get_id(self, repository):
        """ Return the id for a repository """
        raise NotImplementedError

    def is_fork(self, repository):
        """ Return if a repository is a fork """
        return False
