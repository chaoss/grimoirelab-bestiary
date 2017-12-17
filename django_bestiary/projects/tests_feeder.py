#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Bestiary Tests
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


import json
import tempfile

from django.test import TestCase

from .models import Ecosystem, Project, Repository, DataSource, DataSourceType

from .bestiary_import import load_projects, list_not_ds_fields, find_repo_name
from .bestiary_export import export_projects


class BeastFeederTests(TestCase):

    def test_all_loaded(self):

        projects = {}
        no_ds = list_not_ds_fields()

        projects_file = 'projects/projects-release.json'

        with open(projects_file) as pfile:
            projects = json.load(pfile)

        read_projects = len(projects.keys())
        read_data_sources_types = 0
        read_orgs = 1
        read_repos = 0
        dup_repos = 2  # repos duplicated in projects-release.json
        repos_already = []
        read_data_sources = 0

        for project in projects.keys():
            for data_source_type in projects[project]:
                if data_source_type in no_ds:
                    continue
                read_data_sources_types += 1
                for data_source_str in projects[project][data_source_type]:
                    repo = find_repo_name(data_source_str, data_source_type)
                    if repo is None:
                        continue
                    read_data_sources += 1
                    if repo != '' and repo in repos_already:
                        # stackexchange has three repos view for the same repo
                        continue
                    repos_already.append(repo)
                    read_repos += 1

        load_projects(projects_file, "Test Org")

        total_orgs = Ecosystem.objects.all().count()
        total_projects = Project.objects.all().count()
        total_data_sources_types = DataSourceType.objects.all().count()
        total_repos = Repository.objects.all().count()
        total_data_sources = DataSource.objects.all().count()

        self.assertEqual(total_orgs, read_orgs)
        self.assertEqual(total_projects, read_projects)
        self.assertEqual(total_data_sources_types, read_data_sources_types)
        self.assertEqual(total_repos, read_repos)
        self.assertEqual(total_data_sources, read_data_sources)

    def test_import_export(self):
        pfile = 'projects/projects-release.json'
        pfile_export = '/tmp/projects-release.json'

        print('Loading projects')
        load_projects(pfile, "Test Org")

        with tempfile.NamedTemporaryFile() as temp:
            pfile_export = temp.name
            print('Exporting projects')
            export_projects(pfile_export, "Test Org")
            with open(pfile_export) as exported:
                exported_json = json.load(exported)

        with open(pfile) as orig:
            orig_json = json.load(orig)

            self.maxDiff = 1000000
            print("Comparing projects contents between imported and exported")
            self.assertDictEqual(orig_json, exported_json)
