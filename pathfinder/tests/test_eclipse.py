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

import httpretty
import requests

# Hack to make sure that tests import the right packages
# due to setuptools behaviour
sys.path.insert(0, '..')

from repositories.eclipse import ReposEclipse


ECLIPSE_PROJECTS_URL = 'http://projects.eclipse.org/json/projects/all'
ECLIPSE_PROJECTS_FILE = 'data/eclipse-projects.json'


def read_file(filename, mode='r'):
    with open(filename, mode) as f:
        content = f.read()
    return content

def setup_http_server():
    eclipse_projects = read_file(ECLIPSE_PROJECTS_FILE)

    http_requests = []

    def request_callback(method, uri, headers):
        last_request = httpretty.last_request()

        if uri.startswith(ECLIPSE_PROJECTS_URL):
            body = eclipse_projects
        http_requests.append(last_request)

        return (200, headers, body)

    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_PROJECTS_URL,
                           responses=[
                               httpretty.Response(body=request_callback)
                           ])

    return http_requests


class ReposEclipseTest(unittest.TestCase):
    """ReposEclipse tests"""

    repos_ds = {
        "scm": 851,
        "its": 239,
        "scr": 649,
        "mls": 351
    }


    @httpretty.activate
    def test_initialization(self):
        """Test whether attributes are initializated"""

        http_requests = setup_http_server()
        repos = ReposEclipse("scm")
        self.assertEqual(repos.data_source, "scm")

        repos = ReposEclipse("git")
        self.assertEqual(repos.data_source, "scm")

        with self.assertRaises(RuntimeError):
            repos = ReposEclipse("irc")

    @httpretty.activate
    def test_get_repos(self):
        http_requests = setup_http_server()

        for ds in self.repos_ds:
            repos = ReposEclipse(ds)
            repos_list = repos.get_repos()
            self.assertEqual(len(repos_list), self.repos_ds[ds])

    @httpretty.activate
    def test_get_ids(self):
        http_requests = setup_http_server()

        for ds in self.repos_ds:
            repos = ReposEclipse(ds)
            repos_ids_list = repos.get_ids()
            self.assertEqual(len(repos_ids_list), self.repos_ds[ds])



if __name__ == "__main__":
    unittest.main(warnings='ignore')
