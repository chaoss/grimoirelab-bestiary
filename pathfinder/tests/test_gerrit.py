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
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Alvaro del Castillo <acs@bitergia.com>
#

import sys
import unittest

# Hack to make sure that tests import the right packages
# due to setuptools behaviour
sys.path.insert(0, '..')

from repositories.gerrit import ReposGerrit

GERRIT_USER = 'adelcastillo'
GERRIT_HOST = 'git.eclipse.org'

TOTAL_REPOS = 1053


class ReposEclipseTest(unittest.TestCase):

    def test_initialization(self):
        """Test whether attributes are initializated"""

        repos = ReposGerrit(GERRIT_HOST, GERRIT_USER)
        self.assertEqual(repos.user, GERRIT_USER)
        self.assertEqual(repos.host, GERRIT_HOST)

        # with self.assertRaises(RuntimeError):
        #     repos = ReposEclipse("irc")

    def test_get_repos(self):
        repos = ReposGerrit(GERRIT_HOST, GERRIT_USER)
        repos_list = repos.get_repos()
        print(repos_list)
        # This number changes. We must read from a cache
        self.assertEqual(len(repos_list), TOTAL_REPOS)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
