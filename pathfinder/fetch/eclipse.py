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

from .fetcher import Fetcher


logger = logging.getLogger(__name__)


class EclipseFetcher(Fetcher):
    """Fetch github repositories"""

    ECLIPSE_PROJECTS_URL = "http://projects.eclipse.org/json/projects/all"

    def __init__(self):
        super().__init__(None)

    def fetch(self):
        logger.info("Getting Eclipse projects (1 min) from  %s ", self.ECLIPSE_PROJECTS_URL)

        eclipse_projects_resp = self._call(self.ECLIPSE_PROJECTS_URL)
        eclipse_projects = eclipse_projects_resp.json()['projects']

        return eclipse_projects
