# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2019 Bitergia
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
#     Jose Javier Merchante <jjmerchante@cauldron.io>
#

import os
import unittest

import httpretty
import requests

from bestiary.core.retrieval.github import github_owner_repositories

GITHUB_API_URL = "https://api.github.com"
GITHUB_REPOS_URL = GITHUB_API_URL + "/users/chaoss_example/repos"


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestGitHubOwnerRepos(unittest.TestCase):
    """Unit tests for github_owner_repositories"""

    @httpretty.activate
    def test_fetch_repos(self):
        """Test whether a list of repositories is returned from an owner"""

        body = read_file('../data/github_repos_2.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=body,
                               status=200)

        repositories = github_owner_repositories('chaoss_example')

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/grimoirelab')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/grimoirelab-bestiary')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_more_repos(self):
        """Test whether a list of repositories from different pages is returned from an owner"""

        repos_1 = read_file('../data/github_repos_1.json')
        repos_2 = read_file('../data/github_repos_2.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos_1,
                               status=200,
                               forcing_headers={
                                   'Link': '<{}/?&page=2>; rel="next", '
                                           '<{}/?&page=2>; rel="last"'.format(GITHUB_REPOS_URL,
                                                                              GITHUB_REPOS_URL)
                               })

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL + '/?&page=2',
                               body=repos_2,
                               status=200)

        repositories = github_owner_repositories('chaoss_example')

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/community-handbook')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/community-reports')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[2]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/grimoirelab')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[3]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/grimoirelab-bestiary')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_fork_repos(self):
        """Test whether a list of repositories contains fork repos"""

        repos = read_file('../data/github_repos_forks.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)

        repositories = github_owner_repositories('chaoss_example')

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/bitergia-training')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/bootstrap')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_no_issues_repos(self):
        """Test whether a list of repositories contains repos without issues"""

        repos = read_file('../data/github_repos_issues.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)

        repositories = github_owner_repositories('chaoss_example')

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/eagle')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], False)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://github.com/chaoss_example/echarts')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_repos_with_token(self):
        """Test whether it includes an api token when provided"""

        repos = read_file('../data/github_repos_issues.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos)

        _ = github_owner_repositories('chaoss_example', 'aaaa')

        self.assertEqual(httpretty.last_request().headers["Authorization"], "token aaaa")

    @httpretty.activate
    def test_wrong_server_status(self):
        """Test whether a it fails when it gets a server error"""

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=[],
                               status=500)

        with self.assertRaises(requests.exceptions.HTTPError):
            _ = github_owner_repositories('chaoss_example')

    @httpretty.activate
    def test_not_found(self):
        """Test whether a it fails when it gets a server error"""

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=[],
                               status=404)

        with self.assertRaises(requests.exceptions.HTTPError):
            _ = github_owner_repositories('chaoss_example')
