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

import argparse
import json
import logging
import sys

from repositories.github import ReposGitHub

logger = logging.getLogger(__name__)

def config_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging.debug("Debug mode activated")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def get_params():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--data-source', dest='data_source',
                        help='Data source to get repositories from',
                        default='github')
    parser.add_argument('-g', '--debug', dest='debug', action='store_true')
    parser.add_argument('-t', '--token', dest='token', help="Auth token")
    parser.add_argument('-o', '--owners', dest='owners', nargs='*',
                        help='GitHub owners to get repos from')

    args = parser.parse_args()

    if not args.data_source:
        parser.error("data source must be provided.")
        sys.exit(1)

    if args.data_source == 'github' and (not args.token or not args.owners):
        parser.error("github data source needs token and owners.")
        sys.exit(1)

    return args


if __name__ == '__main__':

    args = get_params()

    config_logging(args.debug)

    # Just github in this first iteration
    data_source = "github"

    # Retrieve all the repositories
    if args.data_source == 'github':
        repos = ReposGitHub(args.owners, args.token)
        for repo in repos.get_list():
            print(repo)
    else:
        logger.error("Data source %s not supported", data_source)
