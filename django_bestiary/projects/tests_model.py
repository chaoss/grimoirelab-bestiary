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

import django

from django.db import transaction
from django.test import TestCase

from .models import Ecosystem, Project, Repository, RepositoryView, DataSource


class EcosystemModelTests(TestCase):

    def test_init(self):
        # The CharField name is filled as en empty string by default, not None
        eco = Ecosystem()
        self.assertIsNot(eco, None)
        eco.save()

        eco = Ecosystem(name=None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                eco.save()

        # Strange that in a CharField you can store dicts!
        eco = Ecosystem(name={'trash': 90})
        eco.save()


class ProjectModelTests(TestCase):

    def test_init(self):
        # All projects are related to a ecosystem
        eco = Ecosystem()
        eco.save()
        project = Project(eco=eco)
        self.assertIsNot(project, None)
        project.save()


class RepositoryModelTest(TestCase):

    def test_init(self):
        repository = Repository()
        self.assertIsNot(rep, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                repository.save()
        ds_type = DataSource(name='git')
        ds_type.save()
        repository = Repository(data_source=ds_type)
        repository.save()


class RepositoryViewModelTests(TestCase):

    def test_init(self):
        repository_view = RepositoryView()
        self.assertIsNot(repository_view, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                repository_view.save()

        ds = DataSource(name='git')
        ds.save()
        repository = Repository(data_source=ds, name='test')
        repository_view = RepositoryView(repository=repository)
        # rep must be saved before using it in data_source above
        # it is saved before data_source but it fails because of that
        repository.save()
        with self.assertRaises(django.db.utils.IntegrityError):
            with transaction.atomic():
                repository_view.save()

        # rep is saved already so we can now use it
        repository_view = RepositoryView(repository=repository)
        repository_view.save()

        return


class DataSourceModelTests(TestCase):

    def test_init(self):
        ds_type = DataSource()
        self.assertIsNot(ds_type, None)
        ds_type.save()
