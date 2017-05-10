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

from repositories.eclipse import ReposEclipse
from repositories.gerrit import ReposGerrit
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

    parser.add_argument('-b', '--backend', dest='backend',
                        help='Repositories backend to use',
                        default='github')
    parser.add_argument('-d', '--data-source', dest='data_source',
                        help='Data source to get repositories from',
                        default='github')
    parser.add_argument('-g', '--debug', dest='debug', action='store_true')
    parser.add_argument('-t', '--token', dest='token', help="Auth token")
    parser.add_argument('-o', '--owner', dest='owner',
                        help='GitHub owner to get repos from')
    parser.add_argument('--host', dest='host', help="repositories server host")
    parser.add_argument('-u', '--user', dest='user', help="User for accessing the repositories host")

    args = parser.parse_args()

    if not args.backend:
        parser.error("backend must be provided.")
        sys.exit(1)

    if args.backend == 'github' and (not args.token or not args.owner):
        parser.error("github backend needs token and owner.")
        sys.exit(1)

    if args.backend == 'gerrit' and (not args.host or not args.user):
        parser.error("gerrit backend needs host and user.")
        sys.exit(1)


    return args


if __name__ == '__main__':

    args = get_params()

    config_logging(args.debug)

    # Retrieve all the repositories
    if args.backend == 'github':
        repos = ReposGitHub("github.com", args.owner, args.token)
        for repo in repos.get_ids():
            print(repo)
    elif args.backend == 'eclipse':
        repos = ReposEclipse(args.data_source)
        for repo in repos.get_ids():
            print(repo)
    elif args.backend == 'gerrit':
        repos = ReposGerrit(args.host, args.user)
        for repo in repos.get_ids():
            print(repo)
    else:
        logger.error("Backend %s not supported", args.backend)
