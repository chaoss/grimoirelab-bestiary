# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
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
#     Santiago Dueñas <sduenas@bitergia.com>
#     Miguel Ángel Fernández <mafesan@bitergia.com>
#

import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from grimoirelab_toolkit.datetime import datetime_utcnow

from bestiary.core import api
from bestiary.core.context import BestiaryContext
from bestiary.core.errors import (AlreadyExistsError,
                                  InvalidValueError,
                                  NotFoundError)
from bestiary.core.models import (Ecosystem,
                                  Project,
                                  Transaction,
                                  Operation,
                                  DataSourceType,
                                  DataSource,
                                  DataSet,
                                  Credential)

NAME_NONE_OR_EMPTY_ERROR = "'name' cannot be"
ECOSYSTEM_ID_NONE_OR_EMPTY_ERROR = "'ecosystem_id' cannot be"
PROJECT_ID_NONE_OR_EMPTY_ERROR = "'project_id' cannot be"
PROJECT_FROM_ID_NONE_OR_EMPTY_ERROR = "'from_project_id' cannot be"
NAME_VALUE_ERROR = "field 'name' value must be a string;"
ECOSYSTEM_NOT_FOUND_ERROR = "Ecosystem ID {eco_id} not found in the registry"
ECOSYSTEM_ALREADY_EXISTS_ERROR = "Ecosystem '{name}' already exists in the registry"
PROJECT_NOT_FOUND_ERROR = "Project ID {proj_id} not found in the registry"
PROJECT_ALREADY_EXISTS_ERROR = "Project '{name}' already exists in the registry"
PROJECT_INVALID_PARENT_ALREADY_SET = "Parent is already set to the project"
PROJECT_INVALID_PARENT_EQUAL_ERROR = "Project cannot be its own parent"
PROJECT_INVALID_PARENT_DIFFERENT_ROOT = "Parent cannot belong to a different root project"
PROJECT_INVALID_PARENT_DIFFERENT_ECO = "Parent cannot belong to a different ecosystem"
PROJECT_INVALID_PARENT_DESCENDANT_ERROR = "Parent cannot be a descendant"
TITLE_EMPTY_ERROR = "'title' cannot be"
TITLE_VALUE_ERROR = "field 'title' value must be a string;"
DESCRIPTION_EMPTY_ERROR = "'description' cannot be"
DESCRIPTION_VALUE_ERROR = "field 'description' value must be a string;"
FIELD_VALUE_ERROR_INT = "field value must be a string; int given"
ID_INVALID_LITERAL = "invalid literal for int()"
NAME_LENGTH_ERROR = "'name' cannot have more than"
NAME_START_ERROR = "'name' must start with an alphanumeric character"
NAME_CONTAIN_ERROR = "'name' cannot contain"
DATASET_ALREADY_EXISTS_ERROR = "DataSet '.*' already exists in the registry"
DATASOURCE_TYPE_NONE_ERROR = "'datasource_name' cannot be None"
URI_EMPTY_ERROR = "'uri' cannot be"
CATEGORY_EMPTY_ERROR = "'category' cannot be"
FILTERS_NONE_ERROR = "'filters' cannot be None"
DATASET_NOT_FOUND_ERROR = "DataSet ID {dset_id} not found in the registry"
DATASET_ID_NONE_OR_EMPTY_ERROR = "'dataset_id' cannot be"
CREDENTIAL_ALREADY_EXISTS_ERROR = "Credential '1-Test token' already exists in the registry"
USER_EMPTY_ERROR = "'user' cannot be"
DATASOURCE_NAME_EMPTY_ERROR = "'datasource_name' cannot be"
TOKEN_EMPTY_ERROR = "'token' cannot be"
CREDENTIAL_NOT_FOUND_ERROR = "Credential ID {cred_id} not found in the registry"
CREDENTIAL_ID_NONE_OR_EMPTY_ERROR = "'credential_id' cannot be"
CREDENTIAL_USER_NOT_ALLOWED = "User not allowed to remove credential ID .+"


class TestAddEcosystem(TestCase):
    """Unit tests for add_ecosystem"""

    def setUp(self):
        """Load initial values"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

    def test_add_new_ecosystem(self):
        """Check if everything goes OK when adding a new ecosystem"""

        eco = api.add_ecosystem(self.ctx,
                                'Example-name',
                                title='Example title',
                                description='Example desc.')

        # Tests
        self.assertIsInstance(eco, Ecosystem)
        self.assertEqual(eco.name, 'Example-name')
        self.assertEqual(eco.title, 'Example title')
        self.assertEqual(eco.description, 'Example desc.')

        ecosystems_db = Ecosystem.objects.filter(id=eco.id)
        self.assertEqual(len(ecosystems_db), 1)

        eco1 = ecosystems_db[0]
        self.assertEqual(eco, eco1)

    def test_add_duplicate_ecosystem(self):
        """Check if it fails when adding a duplicate ecosystem"""

        eco = api.add_ecosystem(self.ctx,
                                'Example',
                                title='Example title',
                                description='Example desc.')

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(AlreadyExistsError,
                                    ECOSYSTEM_ALREADY_EXISTS_ERROR.format(name='Example')):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description='Example desc. 2')

        ecosystems = Ecosystem.objects.filter(id=eco.id)
        self.assertEqual(len(ecosystems), 1)

        ecosystems = Ecosystem.objects.all()
        self.assertEqual(len(ecosystems), 1)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_none(self):
        """Check if it fails when ecosystem name is `None`"""

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              None,
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_empty(self):
        """Check if it fails when ecosystem name is empty"""

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              '',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_whitespaces(self):
        """Check if it fails when ecosystem name is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              '   ',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              '\t',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              ' \t  ',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_int(self):
        """Check if it fails when ecosystem name is an integer"""

        with self.assertRaisesRegex(TypeError, NAME_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              12345,
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_invalid(self):
        """Check if it fails when ecosystem name is invalid"""

        with self.assertRaisesRegex(InvalidValueError, NAME_START_ERROR):
            api.add_ecosystem(self.ctx,
                              '-Test',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.add_ecosystem(self.ctx,
                              'Test example',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.add_ecosystem(self.ctx,
                              'Test-example(2)',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_none(self):
        """Check if it works when ecosystem title is `None`"""

        eco = api.add_ecosystem(self.ctx,
                                'Example',
                                title=None,
                                description='Example desc.')

        # Tests
        self.assertIsInstance(eco, Ecosystem)
        self.assertEqual(eco.name, 'Example')
        self.assertEqual(eco.title, None)
        self.assertEqual(eco.description, 'Example desc.')

        ecosystems_db = Ecosystem.objects.filter(name='Example')
        self.assertEqual(len(ecosystems_db), 1)

        eco1 = ecosystems_db[0]
        self.assertEqual(eco, eco1)

    def test_ecosystem_title_empty(self):
        """Check if it fails when ecosystem title is empty"""

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_whitespaces(self):
        """Check if it fails when ecosystem title is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='   ',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='\t',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title=' \t  ',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_int(self):
        """Check if it fails when ecosystem title is an integer"""

        with self.assertRaisesRegex(TypeError, TITLE_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title=12345,
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_none(self):
        """Check if it works when ecosystem description is `None`"""

        eco = api.add_ecosystem(self.ctx,
                                'Example',
                                title='Example title',
                                description=None)

        # Tests
        self.assertIsInstance(eco, Ecosystem)
        self.assertEqual(eco.name, 'Example')
        self.assertEqual(eco.title, 'Example title')
        self.assertEqual(eco.description, None)

        ecosystems_db = Ecosystem.objects.filter(name='Example')
        self.assertEqual(len(ecosystems_db), 1)

        eco1 = ecosystems_db[0]
        self.assertEqual(eco, eco1)

    def test_ecosystem_description_empty(self):
        """Check if it fails when ecosystem description is empty"""

        with self.assertRaisesRegex(InvalidValueError, DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description='')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_whitespaces(self):
        """Check if it fails when ecosystem description is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description='   ')

        with self.assertRaisesRegex(InvalidValueError, DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description='\t')

        with self.assertRaisesRegex(InvalidValueError, DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description=' \t  ')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_int(self):
        """Check if it fails when ecosystem description is an integer"""

        with self.assertRaisesRegex(TypeError, DESCRIPTION_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              'Example',
                              title='Example title',
                              description=12345)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when adding an ecosystem"""

        timestamp = datetime_utcnow()

        api.add_ecosystem(self.ctx,
                          'Example',
                          title='Example title',
                          description='Example desc.')

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'add_ecosystem')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when adding an ecosystem"""

        timestamp = datetime_utcnow()

        api.add_ecosystem(self.ctx,
                          'Example',
                          title='Example title',
                          description='Example desc.')

        transactions = Transaction.objects.all()
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.ADD.value)
        self.assertEqual(op1.entity_type, 'ecosystem')
        self.assertEqual(op1.target, 'Example')
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 3)
        self.assertEqual(op1_args['name'], 'Example')
        self.assertEqual(op1_args['title'], 'Example title')
        self.assertEqual(op1_args['description'], 'Example desc.')


class TestAddProject(TestCase):
    """Unit tests for add_project"""

    def setUp(self):
        """Load initial values"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.eco = Ecosystem.objects.create(name='Eco-example')

        self.parent = Project.objects.create(name='parent-project',
                                             ecosystem=self.eco)

    def test_add_new_project(self):
        """Check if everything goes OK when adding a new project"""

        proj = api.add_project(self.ctx,
                               self.eco.id,
                               'example-name',
                               title='Project title',
                               parent_id=self.parent.id)

        # Tests
        self.assertIsInstance(proj, Project)
        self.assertEqual(proj.ecosystem, self.eco)
        self.assertEqual(proj.name, 'example-name')
        self.assertEqual(proj.title, 'Project title')
        self.assertEqual(proj.parent_project, self.parent)

        projects_db = Project.objects.filter(id=proj.id)
        self.assertEqual(len(projects_db), 1)

        proj1 = projects_db[0]
        self.assertEqual(proj, proj1)

    def test_add_duplicate_project(self):
        """Check if it fails when adding a duplicate project"""

        proj = api.add_project(self.ctx,
                               self.eco.id,
                               'example',
                               title='Project title')

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(AlreadyExistsError,
                                    PROJECT_ALREADY_EXISTS_ERROR.format(name='example')):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title='Project title')

        projects = Project.objects.filter(name=proj.name)
        self.assertEqual(len(projects), 1)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_project_eco_none(self):
        """Check if it fails when ecosystem is `None`"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_ID_NONE_OR_EMPTY_ERROR):
            api.add_project(self.ctx,
                            None,
                            'example',
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_eco_not_exists(self):
        """Check if it fails when ecosystem is not found"""

        with self.assertRaisesRegex(NotFoundError, ECOSYSTEM_NOT_FOUND_ERROR.format(eco_id='11111111')):
            api.add_project(self.ctx,
                            11111111,
                            'example',
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_name_empty(self):
        """Check if it fails when project name is empty"""

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            '',
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_name_whitespaces(self):
        """Check if it fails when project name is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            '   ',
                            title='Project title')

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            '\t',
                            title='Project title')

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            ' \t  ',
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_name_int(self):
        """Check if it fails when project name is an integer"""

        with self.assertRaisesRegex(TypeError, NAME_VALUE_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            12345,
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_name_invalid(self):
        """Check if it fails when project name is invalid"""

        with self.assertRaisesRegex(InvalidValueError, NAME_START_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            '-Test',
                            title='Project title')

        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'Test example',
                            title='Project title')

        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'Test-example(2)',
                            title='Project title')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_title_none(self):
        """Check if it works when project title is `None`"""

        proj = api.add_project(self.ctx,
                               self.eco.id,
                               'example',
                               title=None)

        # Tests
        self.assertIsInstance(proj, Project)
        self.assertEqual(proj.ecosystem, self.eco)
        self.assertEqual(proj.name, 'example')
        self.assertEqual(proj.title, None)
        self.assertEqual(proj.parent_project, None)

        projects_db = Project.objects.filter(name='example')
        self.assertEqual(len(projects_db), 1)

        proj1 = projects_db[0]
        self.assertEqual(proj, proj1)

    def test_project_title_empty(self):
        """Check if it fails when project title is empty"""

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title='')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_title_whitespaces(self):
        """Check if it fails when project title is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title='   ')

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title='\t')

        with self.assertRaisesRegex(InvalidValueError, TITLE_EMPTY_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title=' \t  ')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_title_int(self):
        """Check if it fails when project title is an integer"""

        with self.assertRaisesRegex(TypeError, TITLE_VALUE_ERROR):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title=12345)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_parent_none(self):
        """Check if it adds a new project when a parent is not set"""

        proj = api.add_project(self.ctx,
                               self.eco.id,
                               'example-name',
                               title='Project title')

        # Tests
        self.assertIsInstance(proj, Project)
        self.assertEqual(proj.ecosystem, self.eco)
        self.assertEqual(proj.name, 'example-name')
        self.assertEqual(proj.title, 'Project title')
        self.assertEqual(proj.parent_project, None)

        projects_db = Project.objects.filter(id=proj.id)
        self.assertEqual(len(projects_db), 1)

        proj1 = projects_db[0]
        self.assertEqual(proj, proj1)

    def test_parent_not_exists(self):
        """Check if it fails when the parent project to set does not exist"""

        with self.assertRaisesRegex(NotFoundError, PROJECT_NOT_FOUND_ERROR.format(proj_id='11111111')):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example',
                            title='title',
                            parent_id=11111111)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_parent_different_ecosystem(self):
        """Check if it fails when trying set as parent a project from a different ecosystem"""

        eco2 = Ecosystem.objects.create(name='Eco-2')
        parent = Project.objects.create(name='parent-project-2',
                                        ecosystem=eco2)

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(InvalidValueError, PROJECT_INVALID_PARENT_DIFFERENT_ECO):
            api.add_project(self.ctx,
                            self.eco.id,
                            'example-name',
                            parent_id=parent.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when adding a project"""

        timestamp = datetime_utcnow()

        api.add_project(self.ctx,
                        self.eco.id,
                        'example',
                        title='Project title')

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'add_project')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when adding a project"""

        timestamp = datetime_utcnow()

        api.add_project(self.ctx,
                        self.eco.id,
                        'example',
                        title='Project title',
                        parent_id=self.parent.id)

        transactions = Transaction.objects.all()
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.ADD.value)
        self.assertEqual(op1.entity_type, 'project')
        self.assertEqual(op1.target, 'example')
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 4)
        self.assertEqual(op1_args['name'], 'example')
        self.assertEqual(op1_args['title'], 'Project title')
        self.assertEqual(op1_args['ecosystem'], self.eco.id)
        self.assertEqual(op1_args['parent'], self.parent.id)


class TestAddDataset(TestCase):
    """Unit tests for add_dataset"""

    def setUp(self):
        """Load initial values"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.eco = Ecosystem.objects.create(name='Eco-example')
        self.project = Project.objects.create(id=1,
                                              name='example',
                                              title='Project title',
                                              ecosystem=self.eco)
        self.dstype = DataSourceType.objects.create(name='GitHub')
        self.uri = 'https://github.com/chaoss/grimoirelab-bestiary'

    def test_add_new_dataset(self):
        """Check if everything goes OK when adding a new dataset"""

        dataset = api.add_dataset(self.ctx,
                                  self.project.id,
                                  self.dstype.name,
                                  self.uri,
                                  'issues',
                                  {})

        self.assertIsInstance(dataset, DataSet)
        self.assertEqual(dataset.project, self.project)
        self.assertEqual(dataset.datasource.type, self.dstype)
        self.assertEqual(dataset.datasource.uri, self.uri)
        self.assertEqual(dataset.category, 'issues')
        self.assertEqual(dataset.filters, '{}')

        datasets_db = DataSet.objects.filter(id=dataset.id)
        self.assertEqual(len(datasets_db), 1)
        self.assertEqual(dataset, datasets_db[0])

    def test_add_duplicate_dataset(self):
        """Check if it fails when adding a duplicate dataset"""

        dataset_1 = api.add_dataset(self.ctx,
                                    self.project.id,
                                    self.dstype.name,
                                    self.uri,
                                    'issues',
                                    {})

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(AlreadyExistsError,
                                    DATASET_ALREADY_EXISTS_ERROR):
            dataset_2 = api.add_dataset(self.ctx,
                                        self.project.id,
                                        self.dstype.name,
                                        self.uri,
                                        'issues',
                                        {})

        ndatasets = DataSet.objects.count()
        self.assertEqual(ndatasets, 1)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_project_none(self):
        """Check if fails the project is None"""

        with self.assertRaisesRegex(InvalidValueError,
                                    PROJECT_ID_NONE_OR_EMPTY_ERROR):
            api.add_dataset(self.ctx,
                            None,
                            self.dstype.name,
                            self.uri,
                            'issues',
                            {})

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_project_not_exists(self):
        """Check if fails the project does not exist"""

        Project.objects.filter(id=100).delete()

        with self.assertRaisesRegex(NotFoundError,
                                    PROJECT_NOT_FOUND_ERROR.format(proj_id=100)):
            api.add_dataset(self.ctx,
                            100,
                            self.dstype.name,
                            self.uri,
                            'issues',
                            {})

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_datasource_type_empty(self):
        """Check if fails the data source type is None"""

        with self.assertRaisesRegex(InvalidValueError,
                                    DATASOURCE_TYPE_NONE_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            None,
                            self.uri,
                            'issues',
                            {})

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_empty_uri(self):
        """Check if fails the uri is empty"""

        with self.assertRaisesRegex(InvalidValueError,
                                    URI_EMPTY_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            self.dstype.name,
                            '',
                            'issues',
                            {})

        with self.assertRaisesRegex(InvalidValueError,
                                    URI_EMPTY_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            self.dstype.name,
                            None,
                            'issues',
                            {})

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_empty_category(self):
        """Check if fails the category is empty"""

        with self.assertRaisesRegex(InvalidValueError,
                                    CATEGORY_EMPTY_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            self.dstype.name,
                            self.uri,
                            None,
                            {})

        with self.assertRaisesRegex(InvalidValueError,
                                    CATEGORY_EMPTY_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            self.dstype.name,
                            self.uri,
                            '',
                            {})

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_empty_filters(self):
        """Check if fails the filters is None"""

        with self.assertRaisesRegex(InvalidValueError,
                                    FILTERS_NONE_ERROR):
            api.add_dataset(self.ctx,
                            self.project.id,
                            self.dstype.name,
                            self.uri,
                            'issues',
                            None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_unique_datasource_created(self):
        """Check if only a data source is created when many data sets are added"""

        dataset_1 = api.add_dataset(self.ctx,
                                    self.project.id,
                                    self.dstype,
                                    self.uri,
                                    'issues',
                                    {})

        dataset_2 = api.add_dataset(self.ctx,
                                    self.project.id,
                                    self.dstype.name,
                                    self.uri,
                                    'pull-requests',
                                    {})

        self.assertEqual(dataset_1.datasource, dataset_2.datasource)
        ndatasets = DataSet.objects.count()
        self.assertEqual(ndatasets, 2)

    def test_transaction(self):
        """Check if a transaction is created when adding a dataset"""

        timestamp = datetime_utcnow()

        api.add_dataset(self.ctx,
                        self.project.id,
                        self.dstype.name,
                        self.uri,
                        'issues',
                        {})

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'add_dataset')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when adding a dataset"""

        timestamp = datetime_utcnow()

        dataset = api.add_dataset(self.ctx,
                                  self.project.id,
                                  self.dstype.name,
                                  self.uri,
                                  'issues',
                                  {})

        transactions = Transaction.objects.all()
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 2)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.ADD.value)
        self.assertEqual(op1.entity_type, 'datasource')
        self.assertEqual(op1.target, self.uri)
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)
        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 2)
        self.assertEqual(op1_args['type'], 'GitHub')
        self.assertEqual(op1_args['uri'], self.uri)

        op2 = operations[1]
        self.assertIsInstance(op2, Operation)
        self.assertEqual(op2.op_type, Operation.OpType.ADD.value)
        self.assertEqual(op2.entity_type, 'dataset')
        self.assertEqual(op2.target, str(self.project.id))
        self.assertEqual(op2.trx, trx)
        self.assertGreater(op2.timestamp, timestamp)
        op2_args = json.loads(op2.args)
        self.assertEqual(len(op2_args), 4)
        self.assertEqual(op2_args['project'], self.project.id)
        self.assertEqual(op2_args['datasource'], dataset.datasource.id)
        self.assertEqual(op2_args['category'], 'issues')
        self.assertEqual(op2_args['filters'], {})


class TestAddCredential(TestCase):
    """Unit tests for add_credential"""

    def setUp(self):
        """Load initial values"""

        self.user = get_user_model().objects.create(id=1, username='test')
        self.gh_dst = DataSourceType.objects.create(id=1, name='GitHub')
        self.ctx = BestiaryContext(self.user)

    def test_add_new_credential(self):
        """Check if everything goes OK when adding a new credential"""

        cred = api.add_credential(self.ctx,
                                  self.user,
                                  'Test token',
                                  'GitHub',
                                  'abcd12345')

        # Tests
        self.assertIsInstance(cred, Credential)
        self.assertEqual(cred.user, self.user)
        self.assertEqual(cred.name, 'Test token')
        self.assertEqual(cred.datasource.name, 'GitHub')
        self.assertEqual(cred.token, 'abcd12345')

        cred_db = Credential.objects.filter(id=cred.id)
        self.assertEqual(len(cred_db), 1)

        cred1 = cred_db[0]
        self.assertEqual(cred, cred1)

    def test_add_duplicate_credential(self):
        """Check if it fails when adding a duplicate credential"""

        cred = api.add_credential(self.ctx,
                                  self.user,
                                  'Test token',
                                  'GitHub',
                                  'abcd12345')

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(AlreadyExistsError,
                                    CREDENTIAL_ALREADY_EXISTS_ERROR):
            api.add_credential(self.ctx,
                               self.user,
                               'Test token',
                               'GitHub',
                               '12345abcd')

        credentials = Credential.objects.filter(user=self.user)
        self.assertEqual(len(credentials), 1)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_user_none(self):
        """Check if it fails when user is `None`"""

        with self.assertRaisesRegex(InvalidValueError, USER_EMPTY_ERROR):
            api.add_credential(self.ctx,
                               None,
                               'Test token',
                               'GitHub',
                               'abcd12345')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_datasource_empty(self):
        """Check if fails the data source is empty"""

        with self.assertRaisesRegex(InvalidValueError,
                                    DATASOURCE_NAME_EMPTY_ERROR):
            api.add_credential(self.ctx,
                               self.user,
                               'Test token',
                               '',
                               'abcd12345')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_token_empty(self):
        """Check if fails the token is empty"""

        with self.assertRaisesRegex(InvalidValueError,
                                    TOKEN_EMPTY_ERROR):
            api.add_credential(self.ctx,
                               self.user,
                               'Test token',
                               self.gh_dst,
                               '')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_name_empty(self):
        """Check if fails the token is empty or None"""

        with self.assertRaisesRegex(InvalidValueError,
                                    NAME_NONE_OR_EMPTY_ERROR):
            api.add_credential(self.ctx,
                               self.user,
                               '',
                               self.gh_dst,
                               'abcd1234')

        with self.assertRaisesRegex(InvalidValueError,
                                    NAME_NONE_OR_EMPTY_ERROR):
            api.add_credential(self.ctx,
                               self.user,
                               None,
                               self.gh_dst,
                               'abcd1234')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when adding a credential"""

        timestamp = datetime_utcnow()

        api.add_credential(self.ctx,
                           self.user,
                           'Test token',
                           self.gh_dst,
                           'abcde1234')

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'add_credential')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when adding a credential"""

        timestamp = datetime_utcnow()

        api.add_credential(self.ctx,
                           self.user,
                           'Test token',
                           self.gh_dst,
                           'abcde1234')

        transactions = Transaction.objects.all()
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.ADD.value)
        self.assertEqual(op1.entity_type, 'credential')
        self.assertEqual(op1.target, str(self.user.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 4)
        self.assertEqual(op1_args['user'], self.user.id)
        self.assertEqual(op1_args['name'], 'Test token')
        self.assertEqual(op1_args['datasource'], 'GitHub')
        self.assertEqual(op1_args['token'], 'abcde1234')


class TestDeleteEcosystem(TestCase):
    """Unit tests for delete_ecosystem"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.eco_example = api.add_ecosystem(self.ctx, 'Example')
        self.eco_bitergia = api.add_ecosystem(self.ctx, 'Bitergia')
        self.eco_libresoft = api.add_ecosystem(self.ctx, 'Libresoft')

        self.project = api.add_project(self.ctx,
                                       self.eco_example.id,
                                       'example-project')

    def test_delete_ecosystem(self):
        """Check if everything goes OK when deleting an ecosystem"""

        api.delete_ecosystem(self.ctx, ecosystem_id=self.eco_example.id)

        ecosystems = Ecosystem.objects.filter(id=self.eco_example.id)
        self.assertEqual(len(ecosystems), 0)

        ecosystems = Ecosystem.objects.all()
        self.assertEqual(len(ecosystems), 2)

        eco1 = ecosystems[0]
        self.assertEqual(eco1.id, self.eco_bitergia.id)
        self.assertEqual(eco1.name, 'Bitergia')

        eco2 = ecosystems[1]
        self.assertEqual(eco2.id, self.eco_libresoft.id)
        self.assertEqual(eco2.name, 'Libresoft')

        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.get(name='example-project')

    def test_delete_non_existing_ecosystem(self):
        """Check if it fails when deleting a non existing ecosystem"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, ECOSYSTEM_NOT_FOUND_ERROR.format(eco_id='11111111')):
            api.delete_ecosystem(self.ctx, 11111111)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_id_none(self):
        """Check if it fails when ecosystem id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_ID_NONE_OR_EMPTY_ERROR):
            api.delete_ecosystem(self.ctx, ecosystem_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when deleting an ecosystem"""

        timestamp = datetime_utcnow()

        api.delete_ecosystem(self.ctx, ecosystem_id=self.eco_example.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'delete_ecosystem')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when deleting an ecosystem"""

        timestamp = datetime_utcnow()

        api.delete_ecosystem(self.ctx, ecosystem_id=self.eco_example.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.DELETE.value)
        self.assertEqual(op1.entity_type, 'ecosystem')
        self.assertEqual(op1.target, str(self.eco_example.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.eco_example.id)


class TestDeleteProject(TestCase):
    """Unit tests for delete_project"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.eco = Ecosystem.objects.create(name='Eco-example')

        self.proj_example = api.add_project(self.ctx,
                                            self.eco.id,
                                            'example')
        self.proj_bitergia = api.add_project(self.ctx,
                                             self.eco.id,
                                             'bitergia')
        self.proj_libresoft = api.add_project(self.ctx,
                                              self.eco.id,
                                              'libresoft')

    def test_delete_project(self):
        """Check if everything goes OK when deleting a project"""

        api.delete_project(self.ctx, project_id=self.proj_example.id)

        projects = Project.objects.filter(id=self.proj_example.id)
        self.assertEqual(len(projects), 0)

        projects = Project.objects.all()
        self.assertEqual(len(projects), 2)

        proj1 = projects[0]
        self.assertEqual(proj1.id, self.proj_bitergia.id)
        self.assertEqual(proj1.name, 'bitergia')

        proj2 = projects[1]
        self.assertEqual(proj2.id, self.proj_libresoft.id)
        self.assertEqual(proj2.name, 'libresoft')

    def test_delete_non_existing_project(self):
        """Check if it fails when deleting a non existing project"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, PROJECT_NOT_FOUND_ERROR.format(proj_id='11111111')):
            api.delete_project(self.ctx, 11111111)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_delete_parent_project(self):
        """Check if child projects are deleted when removing a parent"""

        Project.objects.create(name='example-project',
                               parent_project=self.proj_bitergia,
                               ecosystem=self.eco)

        api.delete_project(self.ctx, project_id=self.proj_bitergia.id)

        with self.assertRaises(ObjectDoesNotExist):
            Project.objects.get(name='example-project')

    def test_project_id_none(self):
        """Check if it fails when project id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, PROJECT_ID_NONE_OR_EMPTY_ERROR):
            api.delete_project(self.ctx, project_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when deleting a project"""

        timestamp = datetime_utcnow()

        api.delete_project(self.ctx, project_id=self.proj_example.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'delete_project')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when deleting a project"""

        timestamp = datetime_utcnow()

        api.delete_project(self.ctx, project_id=self.proj_example.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.DELETE.value)
        self.assertEqual(op1.entity_type, 'project')
        self.assertEqual(op1.target, str(self.proj_example.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.proj_example.id)


class TestDeleteDataset(TestCase):
    """Unit tests for delete_dataset"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        eco = Ecosystem.objects.create(name='Eco-example')
        project = Project.objects.create(id=1,
                                         name='example',
                                         title='Project title',
                                         ecosystem=eco)
        dstype = DataSourceType.objects.create(name='GitHub')
        dsource = DataSource.objects.create(id=1,
                                            type=dstype,
                                            uri='https://github.com/chaoss/grimoirelab-bestiary')
        dsource_2 = DataSource.objects.create(id=2,
                                              type=dstype,
                                              uri='https://github.com/chaoss/grimoirelab')
        self.dataset_1 = DataSet.objects.create(id=1,
                                                project=project,
                                                datasource=dsource,
                                                category='issues',
                                                filters='{"tag": "test"}')

        self.dataset_2 = DataSet.objects.create(id=2,
                                                project=project,
                                                datasource=dsource,
                                                category='pull-requests',
                                                filters='{"tag": "test"}')

        self.dataset_3 = DataSet.objects.create(id=3,
                                                project=project,
                                                datasource=dsource_2,
                                                category='issues',
                                                filters='{"tag": "test"}')

    def test_delete_dataset(self):
        """Check if everything goes OK when deleting a dataset"""

        api.delete_dataset(self.ctx, dataset_id=self.dataset_1.id)

        datasets = DataSet.objects.filter(id=self.dataset_1.id)
        self.assertEqual(len(datasets), 0)

        datasets = DataSet.objects.all()
        self.assertEqual(len(datasets), 2)

        proj1 = datasets[0]
        self.assertEqual(proj1.id, self.dataset_2.id)

        proj2 = datasets[1]
        self.assertEqual(proj2.id, self.dataset_3.id)

    def test_delete_non_existing_dataset(self):
        """Check if it fails when deleting a non existing dataset"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, DATASET_NOT_FOUND_ERROR.format(dset_id='99999')):
            api.delete_dataset(self.ctx, 99999)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_dataset_id_none(self):
        """Check if it fails when dataset id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, DATASET_ID_NONE_OR_EMPTY_ERROR):
            api.delete_dataset(self.ctx, dataset_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_remove_datasource(self):
        """Check if removing all data sets related with a data source deletes the data source"""

        api.delete_dataset(self.ctx, dataset_id=self.dataset_1.id)
        api.delete_dataset(self.ctx, dataset_id=self.dataset_2.id)

        datasources = DataSource.objects.filter()
        self.assertEqual(len(datasources), 1)
        datasource = datasources[0]
        self.assertEqual(datasource.id, 2)

    def test_transaction(self):
        """Check if a transaction is created when deleting a dataset"""

        timestamp = datetime_utcnow()

        api.delete_dataset(self.ctx, dataset_id=self.dataset_1.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'delete_dataset')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when deleting a dataset"""

        timestamp = datetime_utcnow()

        api.delete_dataset(self.ctx, dataset_id=self.dataset_1.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.DELETE.value)
        self.assertEqual(op1.entity_type, 'dataset')
        self.assertEqual(op1.target, str(self.dataset_1.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.dataset_1.id)


class TestDeleteCredential(TestCase):
    """Unit tests for delete_credential"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(id=1, username='test')
        self.user2 = get_user_model().objects.create(id=2, username='test2')
        self.gh_dst = DataSourceType.objects.create(id=1, name='GitHub')
        self.ctx = BestiaryContext(self.user)

        self.credential_1 = Credential.objects.create(id=1,
                                                      user=self.user,
                                                      name='Test token GH 1',
                                                      datasource=self.gh_dst,
                                                      token='test1token1')
        self.credential_2 = Credential.objects.create(id=2,
                                                      user=self.user,
                                                      name='Test token GH 2',
                                                      datasource=self.gh_dst,
                                                      token='test1token2')
        self.credential_3 = Credential.objects.create(id=3,
                                                      user=self.user2,
                                                      name='Test token GH 3',
                                                      datasource=self.gh_dst,
                                                      token='test2token1')

    def test_delete_credential(self):
        """Check if everything goes OK when deleting a credential"""

        api.delete_credential(self.ctx, user=self.user, credential_id=self.credential_1.id)

        credentials = Credential.objects.filter(id=self.credential_1.id)
        self.assertEqual(len(credentials), 0)

        credentials = Credential.objects.all()
        self.assertEqual(len(credentials), 2)

        cred1 = credentials[0]
        self.assertEqual(cred1.id, self.credential_2.id)

        cred2 = credentials[1]
        self.assertEqual(cred2.id, self.credential_3.id)

    def test_delete_non_existing_credential(self):
        """Check if it fails when deleting a non existing dataset"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, CREDENTIAL_NOT_FOUND_ERROR.format(cred_id='99999')):
            api.delete_credential(self.ctx, self.user, 99999)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_dataset_id_none(self):
        """Check if it fails when credential id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, CREDENTIAL_ID_NONE_OR_EMPTY_ERROR):
            api.delete_credential(self.ctx, self.user, credential_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_delete_not_allowed(self):
        """Check if it fails when a user tries to delete other user credential"""

        trx_date = datetime_utcnow()

        with self.assertRaisesRegex(PermissionError, CREDENTIAL_USER_NOT_ALLOWED):
            api.delete_credential(self.ctx, self.user2, credential_id=1)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when deleting a credential"""

        timestamp = datetime_utcnow()

        api.delete_credential(self.ctx, self.user, credential_id=self.credential_2.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'delete_credential')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when deleting a credential"""

        timestamp = datetime_utcnow()

        api.delete_credential(self.ctx, self.user, credential_id=self.credential_2.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.DELETE.value)
        self.assertEqual(op1.entity_type, 'credential')
        self.assertEqual(op1.target, str(self.credential_2.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.credential_2.id)


class TestUpdateEcosystem(TestCase):
    """Unit tests for update_ecosystem"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.ecosystem = api.add_ecosystem(self.ctx,
                                           'Example',
                                           title='Example title',
                                           description='Example desc.')

    def test_update_ecosystem(self):
        """Check if it updates an ecosystem"""

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Tests
        self.assertIsInstance(ecosystem, Ecosystem)

        self.assertEqual(ecosystem.name, 'Example-updated')
        self.assertEqual(ecosystem.title, 'Example title updated')
        self.assertEqual(ecosystem.description, 'Example desc. updated')

        # Check database object
        ecosystem_db = Ecosystem.objects.get(id=self.ecosystem.id)
        self.assertEqual(ecosystem, ecosystem_db)

    def test_last_modified(self):
        """Check if last modification date is updated"""

        before_dt = datetime_utcnow()
        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)
        after_dt = datetime_utcnow()

        self.assertLessEqual(before_dt, ecosystem.last_modified)
        self.assertGreaterEqual(after_dt, ecosystem.last_modified)

    def test_non_existing_ecosystem(self):
        """Check if it fails updating an ecosystem that does not exist"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }

        with self.assertRaises(NotFoundError):
            api.update_ecosystem(self.ctx, 11111111, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_none_or_empty(self):
        """Check if it fails when name is set to None or to an empty string"""

        timestamp = datetime_utcnow()

        args = {
            'name': '',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = None

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_invalid_type(self):
        """Check if it fails when name parameter is an integer"""

        timestamp = datetime_utcnow()

        args = {
            'name': 12345,
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        with self.assertRaisesRegex(TypeError, NAME_VALUE_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_invalid_string(self):
        """Check if it fails when ecosystem name is invalid"""

        timestamp = datetime_utcnow()

        args = {
            'name': '-Test',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        with self.assertRaisesRegex(InvalidValueError, NAME_START_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = 'Test example'
        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = 'Test-example(2)'
        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_title_empty(self):
        """Check if title is set to None when it is set to an empty string"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': '',
            'description': 'Example desc. updated'
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Tests
        self.assertIsInstance(ecosystem, Ecosystem)

        self.assertEqual(ecosystem.name, 'Example-updated')
        self.assertEqual(ecosystem.title, None)
        self.assertEqual(ecosystem.description, 'Example desc. updated')

        # Check database object
        ecosystem_db = Ecosystem.objects.get(id=self.ecosystem.id)
        self.assertEqual(ecosystem, ecosystem_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_title_none(self):
        """Check if it works when description field is set to None"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': None,
            'description': 'Example desc. updated'
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Tests
        self.assertIsInstance(ecosystem, Ecosystem)

        self.assertEqual(ecosystem.name, 'Example-updated')
        self.assertEqual(ecosystem.title, None)
        self.assertEqual(ecosystem.description, 'Example desc. updated')

        # Check database object
        ecosystem_db = Ecosystem.objects.get(id=self.ecosystem.id)
        self.assertEqual(ecosystem, ecosystem_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_title_invalid_type(self):
        """Check if it fails when title parameter is an integer"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 12345,
            'description': 'Example desc. updated'
        }
        with self.assertRaisesRegex(TypeError, TITLE_VALUE_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_desc_empty(self):
        """Check if description is set to None when it is set to an empty string"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': ''
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Tests
        self.assertIsInstance(ecosystem, Ecosystem)

        self.assertEqual(ecosystem.name, 'Example-updated')
        self.assertEqual(ecosystem.title, 'Example title updated')
        self.assertEqual(ecosystem.description, None)

        # Check database object
        ecosystem_db = Ecosystem.objects.get(id=self.ecosystem.id)
        self.assertEqual(ecosystem, ecosystem_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_desc_none(self):
        """Check if it works when description field is set to None when it is set to `None`"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': None
        }
        ecosystem = api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Tests
        self.assertIsInstance(ecosystem, Ecosystem)

        self.assertEqual(ecosystem.name, 'Example-updated')
        self.assertEqual(ecosystem.title, 'Example title updated')
        self.assertEqual(ecosystem.description, None)

        # Check database object
        ecosystem_db = Ecosystem.objects.get(id=self.ecosystem.id)
        self.assertEqual(ecosystem, ecosystem_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_desc_invalid_type(self):
        """Check if it fails when description parameter is an integer"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 12345
        }
        with self.assertRaisesRegex(TypeError, DESCRIPTION_VALUE_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when updating an ecosystem"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'update_ecosystem')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when updating an ecosystem"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'Example-updated',
            'title': 'Example title updated',
            'description': 'Example desc. updated'
        }
        api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.UPDATE.value)
        self.assertEqual(op1.entity_type, 'ecosystem')
        self.assertEqual(op1.target, str(self.ecosystem.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 4)
        self.assertEqual(op1_args['id'], self.ecosystem.id)
        self.assertEqual(op1_args['name'], 'Example-updated')
        self.assertEqual(op1_args['title'], 'Example title updated')
        self.assertEqual(op1_args['description'], 'Example desc. updated')


class TestUpdateProject(TestCase):
    """Unit tests for update_project"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.ecosystem = api.add_ecosystem(self.ctx,
                                           'Example',
                                           title='Example title',
                                           description='Example desc.')

        self.project = api.add_project(self.ctx,
                                       self.ecosystem.id,
                                       'example',
                                       title='Project title')

    def test_update_project(self):
        """Check if it updates a project"""

        args = {
            'name': 'example-updated',
            'title': 'Project title updated'
        }
        project = api.update_project(self.ctx, self.project.id, **args)

        # Tests
        self.assertIsInstance(project, Project)

        self.assertEqual(project.name, 'example-updated')
        self.assertEqual(project.title, 'Project title updated')
        self.assertEqual(project.parent_project, None)

        # Check database object
        project_db = Project.objects.get(id=self.project.id)
        self.assertEqual(project, project_db)

    def test_last_modified(self):
        """Check if last modification date is updated"""

        before_dt = datetime_utcnow()
        args = {
            'name': 'example-updated',
            'title': 'Project title updated'
        }
        project = api.update_project(self.ctx, self.project.id, **args)
        after_dt = datetime_utcnow()

        self.assertLessEqual(before_dt, project.last_modified)
        self.assertGreaterEqual(after_dt, project.last_modified)

    def test_non_existing_project(self):
        """Check if it fails updating a project that does not exist"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': 'Project title updated'
        }

        with self.assertRaises(NotFoundError):
            api.update_project(self.ctx, 11111111, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_none_or_empty(self):
        """Check if it fails when name is set to None or to an empty string"""

        timestamp = datetime_utcnow()

        args = {
            'name': '',
            'title': 'Project title updated'
        }
        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        args['name'] = None

        with self.assertRaisesRegex(InvalidValueError, NAME_NONE_OR_EMPTY_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_invalid_type(self):
        """Check if it fails when name parameter is an integer"""

        timestamp = datetime_utcnow()

        args = {
            'name': 12345,
            'title': 'Project title updated'
        }
        with self.assertRaisesRegex(TypeError, NAME_VALUE_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_name_invalid_string(self):
        """Check if it fails when project name is invalid"""

        timestamp = datetime_utcnow()

        args = {
            'name': '-Test',
            'title': 'Project title updated'
        }
        with self.assertRaisesRegex(InvalidValueError, NAME_START_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        args['name'] = 'Test example'
        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        args['name'] = 'Test-example(2)'
        with self.assertRaisesRegex(InvalidValueError, NAME_CONTAIN_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_title_empty(self):
        """Check if title is set to None when it is set to an empty string"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': ''
        }
        project = api.update_project(self.ctx, self.project.id, **args)

        # Tests
        self.assertIsInstance(project, Project)

        self.assertEqual(project.name, 'example-updated')
        self.assertEqual(project.title, None)
        self.assertEqual(project.parent_project, None)

        # Check database object
        project_db = Project.objects.get(id=self.project.id)
        self.assertEqual(project, project_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_title_none(self):
        """Check if it works when title field is set to None"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': None
        }
        project = api.update_project(self.ctx, self.project.id, **args)

        # Tests
        self.assertIsInstance(project, Project)

        self.assertEqual(project.name, 'example-updated')
        self.assertEqual(project.title, None)
        self.assertEqual(project.parent_project, None)

        # Check database object
        project_db = Project.objects.get(id=self.project.id)
        self.assertEqual(project, project_db)

        # Check if the transaction is created
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

    def test_title_invalid_type(self):
        """Check if it fails when title parameter is an integer"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': 12345
        }
        with self.assertRaisesRegex(TypeError, TITLE_VALUE_ERROR):
            api.update_project(self.ctx, self.project.id, **args)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when updating a project"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': 'Project title updated'
        }
        api.update_project(self.ctx, self.project.id, **args)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'update_project')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when updating a project"""

        timestamp = datetime_utcnow()

        args = {
            'name': 'example-updated',
            'title': 'Project title updated'
        }
        api.update_project(self.ctx, self.project.id, **args)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.UPDATE.value)
        self.assertEqual(op1.entity_type, 'project')
        self.assertEqual(op1.target, str(self.project.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 3)
        self.assertEqual(op1_args['id'], self.project.id)
        self.assertEqual(op1_args['name'], 'example-updated')
        self.assertEqual(op1_args['title'], 'Project title updated')


class TestMoveProject(TestCase):
    """Unit tests for move_project"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.origin_eco = api.add_ecosystem(self.ctx,
                                            name='Example-origin',
                                            title='Eco title')

        self.project = api.add_project(self.ctx,
                                       ecosystem_id=self.origin_eco.id,
                                       name='example',
                                       title='Project title')
        self.parent_project = api.add_project(self.ctx,
                                              ecosystem_id=self.origin_eco.id,
                                              name='example-parent',
                                              title='Project title')

        self.ecosystem = api.add_ecosystem(self.ctx,
                                           name='Example',
                                           title='Eco title')

    def test_move_project(self):
        """Check if it moves a project to another one and to a given ecosystem"""

        project = api.move_project(self.ctx,
                                   self.project.id,
                                   to_project_id=self.parent_project.id)

        # Tests
        self.assertIsInstance(project, Project)

        self.assertEqual(project.name, 'example')
        self.assertEqual(project.title, 'Project title')
        self.assertEqual(project.parent_project, self.parent_project)
        self.assertEqual(project.ecosystem, self.origin_eco)

        # Check database object
        project_db = Project.objects.get(id=self.project.id)
        self.assertEqual(project, project_db)

    def test_last_modified(self):
        """Check if last modification date is updated"""

        before_dt = datetime_utcnow()
        project = api.move_project(self.ctx,
                                   self.project.id,
                                   to_project_id=self.parent_project.id)
        after_dt = datetime_utcnow()

        self.assertLessEqual(before_dt, project.last_modified)
        self.assertGreaterEqual(after_dt, project.last_modified)

    def test_from_project_none(self):
        """Check if it fails when source project id is `None`"""

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(InvalidValueError, PROJECT_FROM_ID_NONE_OR_EMPTY_ERROR):
            api.move_project(self.ctx,
                             None,
                             to_project_id=self.parent_project.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_from_project_not_exists(self):
        """Check if it fails when source project does not exist"""

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(NotFoundError, PROJECT_NOT_FOUND_ERROR.format(proj_id='11111111')):
            api.move_project(self.ctx,
                             11111111,
                             to_project_id=self.parent_project.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_to_project_not_exists(self):
        """Check if it fails when the destination parent project does not exist"""

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(NotFoundError, PROJECT_NOT_FOUND_ERROR.format(proj_id='11111111')):
            api.move_project(self.ctx,
                             self.project.id,
                             to_project_id=11111111)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_parent_already_set(self):
        """Check if it fails when the project already has that parent"""

        project = api.move_project(self.ctx,
                                   self.project.id,
                                   to_project_id=self.parent_project.id)

        # Tests
        self.assertIsInstance(project, Project)

        self.assertEqual(project.name, 'example')
        self.assertEqual(project.title, 'Project title')
        self.assertEqual(project.parent_project, self.parent_project)
        self.assertEqual(project.ecosystem, self.origin_eco)

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(ValueError, PROJECT_INVALID_PARENT_ALREADY_SET):
            api.move_project(self.ctx,
                             self.project.id,
                             to_project_id=self.parent_project.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_project_parent_equal(self):
        """Check if it fails when trying set as parent the project itself"""

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(ValueError, PROJECT_INVALID_PARENT_EQUAL_ERROR):
            api.move_project(self.ctx,
                             self.project.id,
                             self.project.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_set_descendant_as_parent(self):
        """Check if it fails when trying set as parent a child project"""

        parent = api.add_project(self.ctx,
                                 ecosystem_id=self.origin_eco.id,
                                 name='parent',
                                 title='Project title',
                                 parent_id=self.parent_project.id)
        child = api.add_project(self.ctx,
                                ecosystem_id=self.origin_eco.id,
                                name='child',
                                title='Project title',
                                parent_id=parent.id)
        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(ValueError, PROJECT_INVALID_PARENT_DESCENDANT_ERROR):
            api.move_project(self.ctx,
                             parent.id,
                             child.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_parent_different_ecosystem(self):
        """Check if it fails when trying set as parent a project from a different ecosystem"""

        root1 = api.add_project(self.ctx,
                                ecosystem_id=self.ecosystem.id,
                                name='root-1')

        timestamp = datetime_utcnow()

        with self.assertRaisesRegex(ValueError, PROJECT_INVALID_PARENT_DIFFERENT_ECO):
            api.move_project(self.ctx,
                             root1.id,
                             self.parent_project.id)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 0)

    def test_no_parent(self):
        """Check if removes the parent project when None is given"""

        project = api.move_project(self.ctx,
                                   self.project.id,
                                   to_project_id=self.parent_project.id)

        self.assertEqual(project.parent_project, self.parent_project)

        project = api.move_project(self.ctx,
                                   self.project.id,
                                   to_project_id=None)

        self.assertEqual(project.parent_project, None)

    def test_transaction(self):
        """Check if a transaction is created when moving a project"""

        timestamp = datetime_utcnow()

        api.move_project(self.ctx,
                         self.project.id,
                         to_project_id=self.parent_project.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'move_project')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when moving a project"""

        timestamp = datetime_utcnow()

        api.move_project(self.ctx,
                         self.project.id,
                         to_project_id=self.parent_project.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.LINK.value)
        self.assertEqual(op1.entity_type, 'project')
        self.assertEqual(op1.target, str(self.project.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 2)
        self.assertEqual(op1_args['id'], self.project.id)
        self.assertEqual(op1_args['parent_id'], self.parent_project.id)


class TestArchiveDataset(TestCase):
    """Unit tests for archive_dataset"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        eco = Ecosystem.objects.create(name='Eco-example')
        project = Project.objects.create(id=1,
                                         name='example',
                                         title='Project title',
                                         ecosystem=eco)
        dstype = DataSourceType.objects.create(name='GitHub')
        dsource = DataSource.objects.create(id=1,
                                            type=dstype,
                                            uri='https://github.com/chaoss/grimoirelab-bestiary')
        self.dataset = DataSet.objects.create(id=1,
                                              project=project,
                                              datasource=dsource,
                                              category='issues',
                                              filters='{"tag": "test"}')

    def test_archive_dataset(self):
        """Check if everything goes OK when archiving a dataset"""

        before_dt = datetime_utcnow()
        archived_dataset = api.archive_dataset(self.ctx, dataset_id=self.dataset.id)
        after_dt = datetime_utcnow()

        self.assertIsInstance(archived_dataset, DataSet)
        self.assertEqual(self.dataset, archived_dataset)

        self.assertEqual(archived_dataset.is_archived, True)
        self.assertLessEqual(before_dt, archived_dataset.archived_at)
        self.assertGreaterEqual(after_dt, archived_dataset.archived_at)

    def test_archive_non_existing_dataset(self):
        """Check if it fails when archiving a non existing dataset"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, DATASET_NOT_FOUND_ERROR.format(dset_id='99999')):
            api.archive_dataset(self.ctx, 99999)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_dataset_id_none(self):
        """Check if it fails when dataset id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, DATASET_ID_NONE_OR_EMPTY_ERROR):
            api.archive_dataset(self.ctx, dataset_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when archiving a dataset"""

        timestamp = datetime_utcnow()

        api.archive_dataset(self.ctx, dataset_id=self.dataset.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'archive_dataset')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when archiving a dataset"""

        timestamp = datetime_utcnow()

        api.archive_dataset(self.ctx, dataset_id=self.dataset.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.UPDATE.value)
        self.assertEqual(op1.entity_type, 'dataset')
        self.assertEqual(op1.target, str(self.dataset.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.dataset.id)


class TestUnarchiveDataset(TestCase):
    """Unit tests for unarchive_dataset"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        eco = Ecosystem.objects.create(name='Eco-example')
        project = Project.objects.create(id=1,
                                         name='example',
                                         title='Project title',
                                         ecosystem=eco)
        dstype = DataSourceType.objects.create(name='GitHub')
        dsource = DataSource.objects.create(id=1,
                                            type=dstype,
                                            uri='https://github.com/chaoss/grimoirelab-bestiary')
        self.dataset = DataSet.objects.create(id=1,
                                              project=project,
                                              datasource=dsource,
                                              category='issues',
                                              filters='{"tag": "test"}',
                                              is_archived=True,
                                              archived_at=datetime_utcnow())

    def test_unarchive_dataset(self):
        """Check if everything goes OK when unarchiving a dataset"""

        unarchived_dataset = api.unarchive_dataset(self.ctx, dataset_id=self.dataset.id)

        self.assertIsInstance(unarchived_dataset, DataSet)
        self.assertEqual(self.dataset, unarchived_dataset)

        self.assertEqual(unarchived_dataset.is_archived, False)
        self.assertIsNone(unarchived_dataset.archived_at)

    def test_unarchive_non_existing_dataset(self):
        """Check if it fails when unarchiving a non existing dataset"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(NotFoundError, DATASET_NOT_FOUND_ERROR.format(dset_id='99999')):
            api.unarchive_dataset(self.ctx, 99999)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_dataset_id_none(self):
        """Check if it fails when dataset id is `None`"""

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(InvalidValueError, DATASET_ID_NONE_OR_EMPTY_ERROR):
            api.unarchive_dataset(self.ctx, dataset_id=None)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.filter(created_at__gt=trx_date)
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when unarchiving a dataset"""

        timestamp = datetime_utcnow()

        api.unarchive_dataset(self.ctx, dataset_id=self.dataset.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'unarchive_dataset')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)

    def test_operations(self):
        """Check if the right operations are created when unarchiving a dataset"""

        timestamp = datetime_utcnow()

        api.unarchive_dataset(self.ctx, dataset_id=self.dataset.id)

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        trx = transactions[0]

        operations = Operation.objects.filter(trx=trx)
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertIsInstance(op1, Operation)
        self.assertEqual(op1.op_type, Operation.OpType.UPDATE.value)
        self.assertEqual(op1.entity_type, 'dataset')
        self.assertEqual(op1.target, str(self.dataset.id))
        self.assertEqual(op1.trx, trx)
        self.assertGreater(op1.timestamp, timestamp)

        op1_args = json.loads(op1.args)
        self.assertEqual(len(op1_args), 1)
        self.assertEqual(op1_args['id'], self.dataset.id)
