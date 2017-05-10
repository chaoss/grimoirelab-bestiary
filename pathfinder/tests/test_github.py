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

from repositories.github import ReposGitHub


OWNER_ORG = 'grimoirelab'
OWNER_USER = 'acs'
GITHUB_API_URL = "https://api.github.com"
GITHUB_ORG_URL = GITHUB_API_URL+"/orgs/"+OWNER_ORG+"/repos"
GITHUB_BAD_ORG_URL = GITHUB_API_URL+"/orgs/"+OWNER_USER+"/repos"
GITHUB_USER_URL = GITHUB_API_URL+"/users/"+OWNER_USER+"/repos"

def read_file(filename, mode='r'):
    with open(filename, mode) as f:
        content = f.read()
    return content

def setup_http_server():
    org_repos = read_file('data/org_repos.json')
    user_repos = read_file('data/user_repos.json')

    http_requests = []

    def not_found_callback(method, uri, headers):
        headers["X-RateLimit-Remaining"] = 500
        headers["X-RateLimit-Reset"] = 3600
        return (404, headers, '')


    def request_callback(method, uri, headers):
        last_request = httpretty.last_request()

        if uri.startswith(GITHUB_ORG_URL):
            body = org_repos
        elif uri.startswith(GITHUB_USER_URL):
            body = user_repos
        else:
            body = ''

        http_requests.append(last_request)
        headers["X-RateLimit-Remaining"] = 500
        headers["X-RateLimit-Reset"] = 3600

        return (200, headers, body)

    httpretty.register_uri(httpretty.GET,
                           GITHUB_ORG_URL,
                           responses=[
                               httpretty.Response(body=request_callback)
                           ])
    httpretty.register_uri(httpretty.GET,
                           GITHUB_USER_URL,
                           responses=[
                               httpretty.Response(body=request_callback)
                           ])
    httpretty.register_uri(httpretty.GET,
                           GITHUB_BAD_ORG_URL,
                           responses=[
                               httpretty.Response(body=not_found_callback)
                           ])


    return http_requests

class ReposGitHubTest(unittest.TestCase):
    """ReposGitHub tests"""

    def setUp(self):
        self.host = 'github.com'
        self.owner = 'grimoirelab'
        self.api_token = 'github_token'

    def tearDown(self):
        pass

    def test_initialization(self):
        """Test whether attributes are initializated"""

        repos = ReposGitHub(self.host, owner=self.owner, api_token=self.api_token)

        self.assertEqual(repos.user, self.owner)
        self.assertEqual(repos.api_token, self.api_token)

    @httpretty.activate
    def test_get_repos(self):
        http_requests = setup_http_server()
        total_repos = 12

        repos = ReposGitHub(self.host, owner=self.owner, api_token=self.api_token)
        repos_list = repos.get_repos()
        self.assertEqual(len(repos_list), total_repos)

if __name__ == "__main__":
    unittest.main(warnings='ignore')
