# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2021 Bitergia
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

import logging
import requests


GITHUB_API_URL = "https://api.github.com"


logger = logging.getLogger(__name__)


def github_owner_repositories(owner, api_token=None):
    """Fetch GitHub repositories from an owner.

    This function fetch all the repositories from a GitHub owner.
    It return a list of repositories indicating whether the repository
    is a fork, has issues enabled, or has pull requests enabled.

    :param owner: name of the GitHub user or organization
    :param api_token: GitHub auth token to access the API

    :returns: a list of repositories including url, has_issues and fork.
    """
    logger.debug(
        f"Fetching GitHub owner repositories; "
        f"owner={owner}; ..."
    )

    headers = {}
    if api_token:
        headers = {'Authorization': 'token {}'.format(api_token)}

    url = GITHUB_API_URL + "/users/" + owner + "/repos"

    while True:
        res = _fetch(url, headers)
        for repo in res.json():
            repo_data = {
                'url': repo['html_url'],
                'fork': repo['fork'],
                'has_issues': repo['has_issues']
            }
            yield repo_data
        if 'next' in res.links.keys():
            url = res.links['next']['url']
        else:
            break

    logger.info(f"GitHub owner repositories fetched; owner='{owner}'")


def _fetch(url, headers=None):
    """Fetch the data from a given URL.

    :param url: link to the resource
    :param headers: headers of the request
    """
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r
