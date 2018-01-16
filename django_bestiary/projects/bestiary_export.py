#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Feed Bestiary with projects information
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
import os

from time import time


import django
# settings.configure()
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_bestiary.settings'
django.setup()

from projects.models import Ecosystem


def get_params():
    parser = argparse.ArgumentParser(usage="usage: beasts_exporter.py [options]",
                                     description="Export beastiary to a JSON file")
    parser.add_argument("-f", "--file", required=True, help="JSON projects file to be exported")
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-o', '--ecosystem', required=True,
                        help='Ecosystem to be exported. ')

    return parser.parse_args()


def find_project_repo_line(repository_view):
    """ Given a RepositoryView build the complete repository
    string tp be included in the JSON project file to collect the data"""

    repo_line = None

    params = repository_view.params
    repo = repository_view.repository.name
    data_source = str(repository_view.repository.data_source)

    # First complete the repository for filtering
    if data_source in ['askbot', 'functest', 'hyperkitty', 'jenkins', 'mediawiki',
                       'mozillaclub', 'phabricator', 'pipermail',
                       'redmine', 'remo', 'rss']:
        repo = repo
    elif data_source in ['bugzilla', 'bugzillarest']:
        if params:
            repo += '/bugs/buglist.cgi?'
    elif data_source in ['confluence', 'discourse', 'git', 'github', 'jira',
                         'supybot', 'nntp']:
        repo = repo
    elif data_source in ['crates', 'dockerhub', 'google_hits',
                         'meetup', 'puppetforge', 'slack', 'telegram',
                         'twitter']:
        repo = ''  # not needed because it is always the same
    elif data_source in ['gerrit']:
        repo = repo
    elif data_source in ['mbox']:
        repo = repo
    elif data_source in ['stackexchange']:
        repo += "questions"

    repo_line = repo

    return repo_line


def find_project_params_line(repository_view):

    repo_line_params = None
    data_source = str(repository_view.repository.data_source)
    params = repository_view.params

    # And now add the params to the repository url for JSON file
    if data_source in ['askbot', 'crates', 'functest',
                       'hyperkitty', 'jenkins', 'mediawiki', 'mozillaclub',
                       'phabricator', 'pipermail', 'puppetforge', 'redmine',
                       'remo', 'rss']:
        pass
    elif data_source in ['bugzilla', 'bugzillarest']:
        repo_line_params = params
    elif data_source in ['confluence', 'discourse', 'git', 'github', 'jira',
                         'supybot', 'nntp']:
        repo_line_params = " " + params
    elif data_source in ['dockerhub', 'google_hits', 'meetup', 'slack',
                         'telegram', 'twitter']:
        repo_line_params = params
    elif data_source in ['gerrit']:
        repo_line_params = "_" + params
    elif data_source in ['mbox']:
        repo_line_params = " " + params
    elif data_source in ['stackexchange']:
        repo_line_params = "/tagged/" + params

    return repo_line_params


def build_project_repository_view(repository_view):
    """ Given a RepositoryView build the complete repository
    string tp be included in the JSON project file to collect the data"""

    repo_line = None

    params = repository_view.params
    repo_line = find_project_repo_line(repository_view)

    if params:
        repo_line += find_project_params_line(repository_view)

    return repo_line


def fetch_projects(ecosystem):
    try:
        eco_orm = Ecosystem.objects.get(name=ecosystem)
    except Ecosystem.DoesNotExist:
        logging.error("Can not find ecosystem %s", ecosystem)
        raise Ecosystem.DoesNotExist

    projects_orm = eco_orm.projects.all()

    beasts = {}

    for project in projects_orm:
        beasts[project.name] = {}
        if project.meta_title:
            beasts[project.name]["meta"] = {"title": project.meta_title}

        for repository_view_orm in project.repository_views.all():
            data_source = repository_view_orm.repository.data_source.name
            if data_source not in beasts[project.name]:
                beasts[project.name][data_source] = []
            repo_proj_line = build_project_repository_view(repository_view_orm)
            beasts[project.name][data_source].append(repo_proj_line)

    return beasts


def export_projects(projects_file, ecosystem):

    nrepository_views = 0
    projects = fetch_projects(ecosystem)
    nprojects = len(list(projects.keys()))

    for project in projects:
        for ds in projects[project]:
            if ds != 'meta':
                nrepository_views += len(projects[project][ds])

    with open(projects_file, "w") as pfile:
        json.dump(projects, pfile, indent=True, sort_keys=True)

    return (nprojects, nrepository_views)


if __name__ == '__main__':

    task_init = time()

    args = get_params()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging.debug("Debug mode activated")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    (nprojects, nrepos) = export_projects(args.file, args.ecosystem)

    logging.debug("Total exporting time ... %.2f sec", time() - task_init)
    print("Projects exported", nprojects)
    print("Data sources exported", nrepos)
