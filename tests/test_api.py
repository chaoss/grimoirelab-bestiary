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
from django.test import TestCase

from grimoirelab_toolkit.datetime import datetime_utcnow

from bestiary.core import api
from bestiary.core.context import BestiaryContext
from bestiary.core.errors import (AlreadyExistsError,
                                  InvalidValueError,
                                  NotFoundError)
from bestiary.core.models import (Ecosystem,
                                  Transaction,
                                  Operation)

ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR = "'name' cannot be"
ECOSYSTEM_ID_NONE_OR_EMPTY_ERROR = "'ecosystem_id' cannot be"
ECOSYSTEM_NAME_VALUE_ERROR = "field 'name' value must be a string;"
ECOSYSTEM_NOT_FOUND_ERROR = "Ecosystem ID {eco_id} not found in the registry"
ECOSYSTEM_ALREADY_EXISTS_ERROR = "Ecosystem '{name}' already exists in the registry"
ECOSYSTEM_TITLE_EMPTY_ERROR = "'title' cannot be"
ECOSYSTEM_TITLE_VALUE_ERROR = "field 'title' value must be a string;"
ECOSYSTEM_DESCRIPTION_EMPTY_ERROR = "'description' cannot be"
ECOSYSTEM_DESCRIPTION_VALUE_ERROR = "field 'description' value must be a string;"
ECOSYSTEM_TITLE_VALUE_ERROR = "field 'title' value must be a string;"
ECOSYSTEM_VALUE_ERROR = "field value must be a string; int given"
ECOSYSTEM_ID_INVALID_LITERAL = "invalid literal for int()"
ECOSYSTEM_NAME_LENGTH_ERROR = "'name' cannot have more than"
ECOSYSTEM_NAME_START_ERROR = "'name' must start with an alphanumeric character"
ECOSYSTEM_NAME_CONTAIN_ERROR = "'name' cannot contain"


class TestAddEcosystem(TestCase):
    """Unit tests for add_ecosystem"""

    def setUp(self):
        """Load initial values"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

    def test_add_new_ecosystem(self):
        """Check if everything goes OK when adding a new ecosystem"""

        eco = api.add_ecosystem(self.ctx,
                                name='Example-name',
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
                                name='Example',
                                title='Example title',
                                description='Example desc.')

        trx_date = datetime_utcnow()  # After this datetime no transactions should be created

        with self.assertRaisesRegex(AlreadyExistsError,
                                    ECOSYSTEM_ALREADY_EXISTS_ERROR.format(name='Example')):
            api.add_ecosystem(self.ctx,
                              name='Example',
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

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name=None,
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_empty(self):
        """Check if it fails when ecosystem name is empty"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_whitespaces(self):
        """Check if it fails when ecosystem name is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='   ',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='\t',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name=' \t  ',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_int(self):
        """Check if it fails when ecosystem name is an integer"""

        with self.assertRaisesRegex(TypeError, ECOSYSTEM_NAME_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              name=12345,
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_name_invalid(self):
        """Check if it fails when ecosystem name is invalid"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_START_ERROR):
            api.add_ecosystem(self.ctx,
                              name='-Test',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_CONTAIN_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Test example',
                              title='Example title',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_CONTAIN_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Test-example(2)',
                              title='Example title',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_none(self):
        """Check if it works when ecosystem title is `None`"""

        eco = api.add_ecosystem(self.ctx,
                                name='Example',
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

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_whitespaces(self):
        """Check if it fails when ecosystem title is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='   ',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='\t',
                              description='Example desc.')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_TITLE_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title=' \t  ',
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_title_int(self):
        """Check if it fails when ecosystem title is an integer"""

        with self.assertRaisesRegex(TypeError, ECOSYSTEM_TITLE_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title=12345,
                              description='Example desc.')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_none(self):
        """Check if it works when ecosystem description is `None`"""

        eco = api.add_ecosystem(self.ctx,
                                name='Example',
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

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='Example title',
                              description='')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_whitespaces(self):
        """Check if it fails when ecosystem description is composed by whitespaces only"""

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='Example title',
                              description='   ')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='Example title',
                              description='\t')

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_DESCRIPTION_EMPTY_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='Example title',
                              description=' \t  ')

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_ecosystem_description_int(self):
        """Check if it fails when ecosystem description is an integer"""

        with self.assertRaisesRegex(TypeError, ECOSYSTEM_DESCRIPTION_VALUE_ERROR):
            api.add_ecosystem(self.ctx,
                              name='Example',
                              title='Example title',
                              description=12345)

        # Check if there are no transactions created when there is an error
        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 0)

    def test_transaction(self):
        """Check if a transaction is created when adding an ecosystem"""

        timestamp = datetime_utcnow()

        api.add_ecosystem(self.ctx,
                          name='Example',
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
                          name='Example',
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


class TestDeleteEcosystem(TestCase):
    """Unit tests for delete_ecosystem"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.eco_example = api.add_ecosystem(self.ctx, name='Example')
        self.eco_bitergia = api.add_ecosystem(self.ctx, name='Bitergia')
        self.eco_libresoft = api.add_ecosystem(self.ctx, name='Libresoft')

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


class TestUpdateEcosystem(TestCase):
    """Unit tests for update_ecosystem"""

    def setUp(self):
        """Load initial dataset"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(self.user)

        self.ecosystem = api.add_ecosystem(self.ctx,
                                           name='Example',
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
        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = None

        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_NONE_OR_EMPTY_ERROR):
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
        with self.assertRaisesRegex(TypeError, ECOSYSTEM_NAME_VALUE_ERROR):
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
        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_START_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = 'Test example'
        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_CONTAIN_ERROR):
            api.update_ecosystem(self.ctx, self.ecosystem.id, **args)

        args['name'] = 'Test-example(2)'
        with self.assertRaisesRegex(InvalidValueError, ECOSYSTEM_NAME_CONTAIN_ERROR):
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
        """Check if it works when description field is set to None when it is set to `None`"""

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
        with self.assertRaisesRegex(TypeError, ECOSYSTEM_TITLE_VALUE_ERROR):
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
        with self.assertRaisesRegex(TypeError, ECOSYSTEM_DESCRIPTION_VALUE_ERROR):
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
