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

import django.test
import graphene
import graphene.test

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from grimoirelab_toolkit.datetime import datetime_utcnow, str_to_datetime

from bestiary.core.context import BestiaryContext
from bestiary.core.log import TransactionsLog
from bestiary.core.models import (Ecosystem,
                                  Project,
                                  Transaction,
                                  Operation)
from bestiary.core.schema import BestiaryQuery, BestiaryMutation


AUTHENTICATION_ERROR = "You do not have permission to perform this action"
DUPLICATED_ECO_ERROR = "Ecosystem 'Example' already exists in the registry"
DUPLICATED_PROJECT_ERROR = "Project 'Example' already exists in the registry"
NAME_EMPTY_ERROR = "'name' cannot be an empty string"
NAME_NONE_ERROR = "'name' cannot be None"
ECOSYSTEM_ID_NONE_ERROR = "'ecosystem_id' cannot be None"
TITLE_EMPTY_ERROR = "'title' cannot be an empty string"
DESC_EMPTY_ERROR = "'description' cannot be an empty string"
ECOSYSTEM_DOES_NOT_EXIST_ERROR = "Ecosystem ID 11111111 not found in the registry"
PROJECT_DOES_NOT_EXIST_ERROR = "Project ID 11111111 not found in the registry"
PARENT_PROJECT_ERROR = "Project cannot be its own parent"
INVALID_NAME_WHITESPACES = "'name' cannot contain whitespace characters"

# Test queries
BT_TRANSACTIONS_QUERY = """{
  transactions {
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
  }
}"""
BT_TRANSACTIONS_QUERY_FILTER = """{
  transactions(
    filters: {
      tuid: "%s",
      name: "%s",
      fromDate: "%s",
      authoredBy: "%s"
    }
  ){
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
  }
}"""
BT_TRANSACTIONS_QUERY_PAGINATION = """{
  transactions(
    page: %d
    pageSize: %d
  ){
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY = """{
  operations {
    entities {
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
  }
}"""
BT_OPERATIONS_QUERY_FILTER = """{
  operations(
    filters:{
      opType:"%s",
      entityType:"%s",
      fromDate:"%s"
    }
  ){
    entities {
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION = """{
  operations(
    page: %d
    pageSize: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION_NO_PAGE = """{
  operations(
    pageSize: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION_NO_PAGE_SIZE = """{
  operations(
    page: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_ECOSYSTEMS_QUERY = """{
  ecosystems {
    entities {
      id
      name
      title
      description
    }
  }
}"""
BT_ECOSYSTEMS_QUERY_FILTER = """{
  ecosystems (
    filters: {
      id: "%d",
      name: "%s"
    }
  ){
    entities {
      id
      name
      title
      description
    }
  }
}"""
BT_ECOSYSTEMS_QUERY_PAGINATION = """{
  ecosystems (
    page: %d
    pageSize: %d
  ){
    entities {
      id
      name
      title
      description
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_PROJECTS_QUERY = """{
  projects {
    entities {
      id
      name
      title
      parentProject {
        id
        name
      }
      ecosystem {
        id
        name
        title
        description
      }
    }
  }
}"""
BT_PROJECTS_QUERY_FILTER = """{
  projects (
    filters: {
      id: "%d",
      name: "%s"
    }
  ){
    entities {
      id
      name
      title
      parentProject {
        id
        name
      }
      ecosystem {
        id
        name
      }
    }
  }
}"""
BT_PROJECTS_QUERY_FILTER_TERM = """{
  projects (
    filters: {
      term: "%s"
    }
  ){
    entities {
      id
      name
      title
    }
  }
}"""
BT_PROJECTS_QUERY_PAGINATION = """{
  projects (
    page: %d
    pageSize: %d
  ){
    entities {
      id
      name
      title
      parentProject {
        id
        name
      }
      ecosystem {
        id
        name
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""

# API endpoint to obtain a context for executing queries
GRAPHQL_ENDPOINT = '/graphql/'


class TestQuery(BestiaryQuery, graphene.ObjectType):
    pass


class TestQueryPagination(django.test.TestCase):
    pass


class TestMutations(BestiaryMutation):
    pass


schema = graphene.Schema(query=TestQuery,
                         mutation=TestMutations)


class TestQueryTransactions(django.test.TestCase):
    """Unit tests for transaction queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        # Create a transaction controlling input values
        self.timestamp = datetime_utcnow()  # This will be used as a filter
        self.trx = Transaction(name='test_trx',
                               tuid='012345abcdef',
                               created_at=datetime_utcnow(),
                               authored_by=self.user.username)
        self.trx.save()

    def test_transaction(self):
        """Check if it returns the registry of transactions"""

        timestamp = datetime_utcnow()
        client = graphene.test.Client(schema)
        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertEqual(trx['name'], self.trx.name)
        self.assertEqual(str_to_datetime(trx['createdAt']), self.trx.created_at)
        self.assertEqual(trx['tuid'], self.trx.tuid)
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

    def test_filter_registry(self):
        """Check whether it returns the transaction searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_FILTER % ('012345abcdef', 'test_trx',
                                                     self.timestamp.isoformat(),
                                                     'test')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertEqual(trx['name'], self.trx.name)
        self.assertEqual(str_to_datetime(trx['createdAt']), self.trx.created_at)
        self.assertEqual(trx['tuid'], self.trx.tuid)
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing transaction"""

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_FILTER % ('012345abcdefg', 'test_trx',
                                                     self.timestamp.isoformat(),
                                                     'test')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertListEqual(transactions, [])

    def test_pagination(self):
        """Check whether it returns the transactions searched when using pagination"""

        # Creating additional transactions
        trx = Transaction(name='test_trx_2',
                          tuid='567890abcdef',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username,
                          is_closed=True,
                          closed_at=datetime_utcnow())
        trx.save()

        trx = Transaction(name='test_trx_3',
                          tuid='098765fedcba',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username,
                          is_closed=True,
                          closed_at=datetime_utcnow())
        trx.save()

        timestamp = datetime_utcnow()

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 2)

        trx = transactions[0]
        self.assertEqual(trx['name'], 'test_trx')
        self.assertLess(str_to_datetime(trx['createdAt']), timestamp)
        self.assertEqual(trx['tuid'], '012345abcdef')
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

        trx = transactions[1]
        self.assertEqual(trx['name'], 'test_trx_2')
        self.assertLess(str_to_datetime(trx['createdAt']), timestamp)
        self.assertEqual(trx['tuid'], '567890abcdef')
        self.assertLess(str_to_datetime(trx['closedAt']), timestamp)
        self.assertTrue(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

        pag_data = executed['data']['transactions']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Transactions created in `setUp` method
        Transaction.objects.all().delete()
        transactions = Transaction.objects.all()

        self.assertEqual(len(transactions), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=self.context_value)

        q_transactions = executed['data']['transactions']['entities']
        self.assertListEqual(q_transactions, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestQueryOperations(django.test.TestCase):
    """Unit tests for operation queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        # Create an operation controlling input values
        trx = Transaction(name='test_trx',
                          tuid='012345abcdef',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username)
        trx.save()

        self.trxl = TransactionsLog(trx, self.ctx)
        self.timestamp = datetime_utcnow()  # This will be used as a filter
        self.trxl.log_operation(op_type=Operation.OpType.UPDATE,
                                entity_type='test_entity',
                                timestamp=datetime_utcnow(),
                                args={'test_arg': 'test_value'},
                                target='test_target')
        self.trxl.log_operation(op_type=Operation.OpType.ADD,
                                entity_type='test_entity_2',
                                timestamp=datetime_utcnow(),
                                args={'test_arg_2': 'test_value_2'},
                                target='test_target_2')
        self.trxl.log_operation(op_type=Operation.OpType.DELETE,
                                entity_type='test_entity_3',
                                timestamp=datetime_utcnow(),
                                args={'test_arg_3': 'test_value_3'},
                                target='test_target_3')
        self.trxl.close()

    def test_operation(self):
        """Check if it returns the registry of operations"""

        client = graphene.test.Client(schema)
        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 3)

        for op in operations:
            # Check if the query returns the associated transaction
            trx = op['trx']
            self.assertEqual(trx['name'], self.trxl.trx.name)
            self.assertEqual(trx['tuid'], self.trxl.trx.tuid)
            self.assertEqual(str_to_datetime(trx['createdAt']), self.trxl.trx.created_at)

        op = operations[0]
        self.assertEqual(op['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target')
        self.assertEqual(op['args'], {'test_arg': 'test_value'})

        op = operations[1]
        self.assertEqual(op['opType'], Operation.OpType.ADD.value)
        self.assertEqual(op['entityType'], 'test_entity_2')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target_2')
        self.assertEqual(op['args'], {'test_arg_2': 'test_value_2'})

        op = operations[2]
        self.assertEqual(op['opType'], Operation.OpType.DELETE.value)
        self.assertEqual(op['entityType'], 'test_entity_3')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target_3')
        self.assertEqual(op['args'], {'test_arg_3': 'test_value_3'})

    def test_filter_registry(self):
        """Check whether it returns the operation searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_FILTER % ('UPDATE', 'test_entity',
                                                   self.timestamp.isoformat())
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertEqual(op1['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op1['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op1['timestamp']), self.timestamp)
        self.assertEqual(op1['args'], {'test_arg': 'test_value'})

        # Check if the query returns the associated transaction
        trx1 = op1['trx']
        self.assertEqual(trx1['name'], self.trxl.trx.name)
        self.assertEqual(trx1['tuid'], self.trxl.trx.tuid)
        self.assertEqual(str_to_datetime(trx1['createdAt']), self.trxl.trx.created_at)

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing operation"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_FILTER % ('DELETE', 'test_entity',
                                                   self.timestamp.isoformat())
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertListEqual(operations, [])

    def test_pagination(self):
        """Check whether it returns the operations searched when using pagination"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 2)

        op1 = operations[0]
        self.assertEqual(op1['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op1['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op1['timestamp']), self.timestamp)
        self.assertEqual(op1['args'], {'test_arg': 'test_value'})

        op2 = operations[1]
        self.assertEqual(op2['opType'], Operation.OpType.ADD.value)
        self.assertEqual(op2['entityType'], 'test_entity_2')
        self.assertEqual(op2['target'], 'test_target_2')
        self.assertGreater(str_to_datetime(op2['timestamp']), self.timestamp)
        self.assertEqual(op2['args'], {'test_arg_2': 'test_value_2'})

        pag_data = executed['data']['operations']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Operations created in `setUp` method
        Operation.objects.all().delete()
        operations = Operation.objects.all()

        self.assertEqual(len(operations), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=self.context_value)

        q_operations = executed['data']['operations']['entities']
        self.assertListEqual(q_operations, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestQueryEcosystems(django.test.TestCase):
    """Unit tests for ecosystem queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.eco = Ecosystem(name='Example',
                             title='Example title',
                             description='Example desc.')
        self.eco.save()

    def test_ecosystem(self):
        """Check if it returns the list of ecosystems"""

        client = graphene.test.Client(schema)
        executed = client.execute(BT_ECOSYSTEMS_QUERY,
                                  context_value=self.context_value)

        ecosystems = executed['data']['ecosystems']['entities']
        self.assertEqual(len(ecosystems), 1)

        eco = ecosystems[0]
        self.assertEqual(eco['id'], str(self.eco.id))
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], 'Example title')
        self.assertEqual(eco['description'], 'Example desc.')

    def test_filter_registry(self):
        """Check whether it returns the ecosystem searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_ECOSYSTEMS_QUERY_FILTER % (self.eco.id, 'Example')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        ecosystems = executed['data']['ecosystems']['entities']
        self.assertEqual(len(ecosystems), 1)

        eco = ecosystems[0]
        self.assertEqual(eco['id'], str(self.eco.id))
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], 'Example title')
        self.assertEqual(eco['description'], 'Example desc.')

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing ecosystem"""

        client = graphene.test.Client(schema)
        test_query = BT_ECOSYSTEMS_QUERY_FILTER % (11111111, 'Ghost-Eco')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        ecosystems = executed['data']['ecosystems']['entities']
        self.assertListEqual(ecosystems, [])

    def test_pagination(self):
        """Check whether it returns the ecosystems searched when using pagination"""

        # Creating additional ecosystems
        eco1 = Ecosystem(name='Example-1',
                         title='Example title 1',
                         description='Example desc. 1')
        eco1.save()

        eco2 = Ecosystem(name='Example-2',
                         title='Example title 2',
                         description='Example desc. 2')
        eco2.save()

        client = graphene.test.Client(schema)
        test_query = BT_ECOSYSTEMS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        ecosystems = executed['data']['ecosystems']['entities']
        self.assertEqual(len(ecosystems), 2)

        eco = ecosystems[0]
        self.assertEqual(eco['id'], str(self.eco.id))
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], 'Example title')
        self.assertEqual(eco['description'], 'Example desc.')

        eco = ecosystems[1]
        self.assertEqual(eco['id'], str(eco1.id))
        self.assertEqual(eco['name'], 'Example-1')
        self.assertEqual(eco['title'], 'Example title 1')
        self.assertEqual(eco['description'], 'Example desc. 1')

        pag_data = executed['data']['ecosystems']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

        # Testing whether it returns different results in the second page
        test_query = BT_ECOSYSTEMS_QUERY_PAGINATION % (2, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        ecosystems = executed['data']['ecosystems']['entities']
        self.assertEqual(len(ecosystems), 1)

        eco = ecosystems[0]
        self.assertEqual(eco['id'], str(eco2.id))
        self.assertEqual(eco['name'], 'Example-2')
        self.assertEqual(eco['title'], 'Example title 2')
        self.assertEqual(eco['description'], 'Example desc. 2')

        pag_data = executed['data']['ecosystems']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 2)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertFalse(pag_data['hasNext'])
        self.assertTrue(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 3)
        self.assertEqual(pag_data['endIndex'], 3)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Ecosystems created in `setUp` method
        Ecosystem.objects.all().delete()
        ecosystems = Ecosystem.objects.all()

        self.assertEqual(len(ecosystems), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_ECOSYSTEMS_QUERY,
                                  context_value=self.context_value)

        q_ecosystems = executed['data']['ecosystems']['entities']
        self.assertListEqual(q_ecosystems, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_ECOSYSTEMS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestQueryProjects(django.test.TestCase):
    """Unit tests for project queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.proj = Project(name='Example',
                            title='Example title')
        self.proj.save()

    def test_project(self):
        """Check if it returns the list of projects"""

        client = graphene.test.Client(schema)
        executed = client.execute(BT_PROJECTS_QUERY,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertEqual(len(projects), 1)

        proj = projects[0]
        self.assertEqual(proj['id'], str(self.proj.id))
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], 'Example title')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem'], None)

    def test_filter_registry(self):
        """Check whether it returns the project searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_PROJECTS_QUERY_FILTER % (self.proj.id, 'Example')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertEqual(len(projects), 1)

        proj = projects[0]
        self.assertEqual(proj['id'], str(self.proj.id))
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], 'Example title')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem'], None)

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing project"""

        client = graphene.test.Client(schema)
        test_query = BT_PROJECTS_QUERY_FILTER % (11111111, 'Ghost-Project')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertListEqual(projects, [])

    def test_filter_term_registry(self):
        """Check whether it returns the project searched when looking for a term"""

        client = graphene.test.Client(schema)
        test_query = BT_PROJECTS_QUERY_FILTER_TERM % 'ex'
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertEqual(len(projects), 1)

        proj = projects[0]
        self.assertEqual(proj['id'], str(self.proj.id))
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], 'Example title')

    def test_filter_term_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing term"""

        client = graphene.test.Client(schema)
        test_query = BT_PROJECTS_QUERY_FILTER_TERM % 'test'
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertListEqual(projects, [])

    def test_pagination(self):
        """Check whether it returns the projects searched when using pagination"""

        # Creating additional projects
        proj1 = Project(name='Example-1',
                        title='Example title 1')
        proj1.save()

        proj2 = Project(name='Example-2',
                        title='Example title 2')
        proj2.save()

        client = graphene.test.Client(schema)
        test_query = BT_PROJECTS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertEqual(len(projects), 2)

        proj = projects[0]
        self.assertEqual(proj['id'], str(self.proj.id))
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], 'Example title')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem'], None)

        proj = projects[1]
        self.assertEqual(proj['id'], str(proj1.id))
        self.assertEqual(proj['name'], 'Example-1')
        self.assertEqual(proj['title'], 'Example title 1')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem'], None)

        pag_data = executed['data']['projects']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

        # Testing whether it returns different results in the second page
        test_query = BT_PROJECTS_QUERY_PAGINATION % (2, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        projects = executed['data']['projects']['entities']
        self.assertEqual(len(projects), 1)

        proj = projects[0]
        self.assertEqual(proj['id'], str(proj2.id))
        self.assertEqual(proj['name'], 'Example-2')
        self.assertEqual(proj['title'], 'Example title 2')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem'], None)

        pag_data = executed['data']['projects']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 2)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertFalse(pag_data['hasNext'])
        self.assertTrue(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 3)
        self.assertEqual(pag_data['endIndex'], 3)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Projects created in `setUp` method
        Project.objects.all().delete()
        projects = Project.objects.all()

        self.assertEqual(len(projects), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_PROJECTS_QUERY,
                                  context_value=self.context_value)

        q_projects = executed['data']['projects']['entities']
        self.assertListEqual(q_projects, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_PROJECTS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestAddEcosystemMutation(django.test.TestCase):
    """Unit tests for mutation to add ecosystems"""

    BT_ADD_ECO = """
      mutation addEco ($name: String,
                       $title: String,
                       $description: String) {
        addEcosystem(name: $name,
                     title: $title,
                     description: $description)
        {
          ecosystem {
            id
            name
            title
            description
          }
        }
      }
    """

    BT_ADD_ECO_TITLE_NONE = """
      mutation addEco {
        addEcosystem(name: "Example",
                     description: "Example desc.") {
          ecosystem {
            id
            name
            title
            description
          }
        }
      }
    """

    BT_ADD_ECO_DESC_NONE = """
      mutation addEco {
        addEcosystem(name: "Example",
                     title: "Example title") {
          ecosystem {
            id
            name
            title
            description
          }
        }
      }
    """

    def setUp(self):
        """Set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

    def test_add_ecosystem(self):
        """Check if a new ecosystem is added"""

        params = {
            'name': 'Example',
            'title': 'Example title',
            'description': 'Example desc.'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        eco = executed['data']['addEcosystem']['ecosystem']
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], 'Example title')
        self.assertEqual(eco['description'], 'Example desc.')

        # Check database
        eco_db = Ecosystem.objects.get(id=int(eco['id']))
        self.assertEqual(eco_db.id, int(eco['id']))
        self.assertEqual(eco_db.name, 'Example')
        self.assertEqual(eco_db.title, 'Example title')
        self.assertEqual(eco_db.description, 'Example desc.')

    def test_name_empty(self):
        """Check whether ecosystems with empty names cannot be added"""

        params = {
            'name': '',
            'title': 'Example title',
            'description': 'Example desc.'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, NAME_EMPTY_ERROR)

        # Check database
        ecosystems = Ecosystem.objects.all()
        self.assertEqual(len(ecosystems), 0)

    def test_name_invalid(self):
        """Check whether ecosystems with invalid names cannot be added"""

        params = {
            'name': 'Test example',
            'title': 'Example title',
            'description': 'Example desc.'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, INVALID_NAME_WHITESPACES)

        # Check database
        ecosystems = Ecosystem.objects.all()
        self.assertEqual(len(ecosystems), 0)

    def test_title_empty(self):
        """Check whether ecosystems with empty titles cannot be added"""

        params = {
            'name': 'Example',
            'title': '',
            'description': 'Example desc.'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, TITLE_EMPTY_ERROR)

    def test_title_none(self):
        """Check whether ecosystems with null titles can be added"""

        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO_TITLE_NONE,
                                  context_value=self.context_value)

        # Check result
        eco = executed['data']['addEcosystem']['ecosystem']
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], None)
        self.assertEqual(eco['description'], 'Example desc.')

        # Check database
        eco_db = Ecosystem.objects.get(id=int(eco['id']))
        self.assertEqual(eco_db.id, int(eco['id']))
        self.assertEqual(eco_db.name, 'Example')
        self.assertEqual(eco_db.title, None)
        self.assertEqual(eco_db.description, 'Example desc.')

    def test_desc_empty(self):
        """Check whether ecosystems with empty descriptions cannot be added"""

        params = {
            'name': 'Example',
            'title': 'Example title',
            'description': ''
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, DESC_EMPTY_ERROR)

    def test_desc_none(self):
        """Check whether ecosystems with null descriptions can be added"""

        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO_DESC_NONE,
                                  context_value=self.context_value)

        # Check result
        eco = executed['data']['addEcosystem']['ecosystem']
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], 'Example title')
        self.assertEqual(eco['description'], None)

        # Check database
        eco_db = Ecosystem.objects.get(id=int(eco['id']))
        self.assertEqual(eco_db.id, int(eco['id']))
        self.assertEqual(eco_db.name, 'Example')
        self.assertEqual(eco_db.title, 'Example title')
        self.assertEqual(eco_db.description, None)

    def test_integrity_error(self):
        """Check whether ecosystems with the same name cannot be inserted"""

        params = {
            'name': 'Example',
            'title': 'Example title',
            'description': 'Example desc.'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)
        eco = executed['data']['addEcosystem']['ecosystem']
        eco_id = int(eco['id'])

        # Check database
        eco_db = Ecosystem.objects.get(id=eco_id)
        self.assertEqual(eco_db.id, eco_id)
        self.assertEqual(eco_db.name, 'Example')
        self.assertEqual(eco_db.title, 'Example title')
        self.assertEqual(eco_db.description, 'Example desc.')

        # Try to insert it twice
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, DUPLICATED_ECO_ERROR)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_ADD_ECO,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestAddProjectMutation(django.test.TestCase):
    """Unit tests for mutation to add projects"""

    BT_ADD_PROJECT = """
      mutation addProj ($name: String,
                       $title: String,
                       $ecosystemId: ID,
                       $parentId: ID) {
        addProject(name: $name,
                   title: $title,
                   ecosystemId: $ecosystemId,
                   parentId: $parentId)
        {
          project {
            id
            name
            title
            parentProject {
              id
              name
            }
            ecosystem {
              id
              name
            }
          }
        }
      }
    """

    def setUp(self):
        """Set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.eco = Ecosystem.objects.create(name='Eco-example')

        self.parent = Project.objects.create(name='parent-project',
                                             ecosystem=self.eco)

    def test_add_project(self):
        """Check if a new project is added"""

        params = {
            'name': 'Example',
            'title': 'Example title',
            'ecosystemId': self.eco.id,
            'parentId': self.parent.id
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        proj = executed['data']['addProject']['project']
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], 'Example title')

        eco = proj['ecosystem']
        self.assertEqual(eco['id'], str(self.eco.id))
        self.assertEqual(eco['name'], 'Eco-example')

        parent = proj['parentProject']
        self.assertEqual(parent['id'], str(self.parent.id))
        self.assertEqual(parent['name'], 'parent-project')

        # Check database
        proj_db = Project.objects.get(id=int(proj['id']))
        self.assertEqual(proj_db.id, int(proj['id']))
        self.assertEqual(proj_db.name, 'Example')
        self.assertEqual(proj_db.title, 'Example title')
        self.assertEqual(proj_db.parent_project, self.parent)
        self.assertEqual(proj_db.ecosystem, self.eco)

    def test_not_found_ecosystem(self):
        """Check whether projects cannot be added when the ecosystem is not found"""

        params = {
            'name': 'test-example',
            'title': 'Example title',
            'ecosystemId': '11111111'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, ECOSYSTEM_DOES_NOT_EXIST_ERROR)

        # Check database
        projects = Project.objects.filter(name='test-example')
        self.assertEqual(len(projects), 0)

    def test_not_found_parent(self):
        """Check whether projects cannot be added when the parent is not found"""

        params = {
            'name': 'test-example',
            'title': 'Example title',
            'ecosystemId': self.eco.id,
            'parentId': '11111111'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

        # Check database
        projects = Project.objects.filter(name='test-example')
        self.assertEqual(len(projects), 0)

    def test_integrity_error(self):
        """Check whether projects with the same name cannot be inserted"""

        params = {
            'name': 'Example',
            'title': 'Example title',
            'ecosystemId': self.eco.id
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)
        proj = executed['data']['addProject']['project']
        proj_id = int(proj['id'])

        # Check database
        proj_db = Project.objects.get(id=proj_id)
        self.assertEqual(proj_db.id, proj_id)
        self.assertEqual(proj_db.name, 'Example')
        self.assertEqual(proj_db.title, 'Example title')
        self.assertEqual(proj_db.parent_project, None)

        # Try to insert it twice
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, DUPLICATED_PROJECT_ERROR)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_ADD_PROJECT,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestDeleteEcosystemMutation(django.test.TestCase):
    """Unit tests for mutation to delete ecosystems"""

    BT_DELETE_ECO = """
      mutation delEco($id: ID) {
        deleteEcosystem(id: $id) {
          ecosystem{
            id
            name
            title
            description
          }
        }
      }
    """

    def setUp(self):
        """Set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.eco_ex = Ecosystem.objects.create(id=1,
                                               name='Example',
                                               description='Example desc.')

        self.eco_bit = Ecosystem.objects.create(id=2,
                                                name='Bitergia',
                                                description='Bitergia desc.')

    def test_delete_ecosystem(self):
        """Check whether it deletes an ecosystem"""

        # Delete ecosystem
        params = {
            'id': 1
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        eco = executed['data']['deleteEcosystem']['ecosystem']
        self.assertEqual(eco['id'], '1')
        self.assertEqual(eco['name'], 'Example')
        self.assertEqual(eco['title'], None)
        self.assertEqual(eco['description'], 'Example desc.')

        # Tests
        with self.assertRaises(django.core.exceptions.ObjectDoesNotExist):
            Ecosystem.objects.get(id=1)

        ecosystems = Ecosystem.objects.filter(id=2)
        self.assertEqual(len(ecosystems), 1)

    def test_not_found_ecosystem(self):
        """Check if it returns an error when an ecosystem does not exist"""

        params = {
            'id': 11111111
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_ECO,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, ECOSYSTEM_DOES_NOT_EXIST_ERROR)

        ecosystems = Ecosystem.objects.all()
        self.assertEqual(len(ecosystems), 2)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_DELETE_ECO,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestDeleteProjectMutation(django.test.TestCase):
    """Unit tests for mutation to delete projects"""

    BT_DELETE_PROJECT = """
      mutation delProj($id: ID) {
        deleteProject(id: $id) {
          project{
            id
            name
            title
          }
        }
      }
    """

    def setUp(self):
        """Set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.proj_ex = Project.objects.create(id=1,
                                              name='Example')

        self.proj_bit = Project.objects.create(id=2,
                                               name='Bitergia')

    def test_delete_project(self):
        """Check whether it deletes a project"""

        # Delete project
        params = {
            'id': 1
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        proj = executed['data']['deleteProject']['project']
        self.assertEqual(proj['id'], '1')
        self.assertEqual(proj['name'], 'Example')
        self.assertEqual(proj['title'], None)

        # Tests
        with self.assertRaises(django.core.exceptions.ObjectDoesNotExist):
            Project.objects.get(id=1)

        projects = Project.objects.filter(id=2)
        self.assertEqual(len(projects), 1)

    def test_not_found_project(self):
        """Check if it returns an error when a project does not exist"""

        params = {
            'id': 11111111
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

        projects = Project.objects.all()
        self.assertEqual(len(projects), 2)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_DELETE_PROJECT,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestUpdateEcosystemMutation(django.test.TestCase):
    """Unit tests for mutation to update ecosystems"""

    BT_UPDATE_ECOSYSTEM = """
      mutation updateEco($id: ID, $data: EcosystemInputType) {
        updateEcosystem(id: $id, data: $data) {
          ecosystem {
            id
            name
            title
            description
          }
        }
      }
    """

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        self.ecosystem = Ecosystem.objects.create(id=1,
                                                  name='Example',
                                                  title='Example title',
                                                  description='Example desc.')

    def test_update_ecosystem(self):
        """Check if it updates an ecosystem"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example-updated',
                'title': 'Example title updated',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        # Check results, ecosystem was updated
        ecosystem = executed['data']['updateEcosystem']['ecosystem']
        self.assertEqual(ecosystem['id'], '1')
        self.assertEqual(ecosystem['name'], 'Example-updated')
        self.assertEqual(ecosystem['title'], 'Example title updated')
        self.assertEqual(ecosystem['description'], 'Example desc. updated')

        # Check database
        ecosystem_db = Ecosystem.objects.get(id=1)
        self.assertEqual(ecosystem_db.id, 1)
        self.assertEqual(ecosystem_db.name, 'Example-updated')
        self.assertEqual(ecosystem_db.title, 'Example title updated')
        self.assertEqual(ecosystem_db.description, 'Example desc. updated')

    def test_non_existing_ecosystem(self):
        """Check if it fails updating ecosystems that do not exist"""

        client = graphene.test.Client(schema)

        params = {
            'id': 11111111,
            'data': {
                'name': 'Example-updated',
                'title': 'Example title updated',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, ECOSYSTEM_DOES_NOT_EXIST_ERROR)

    def test_title_empty(self):
        """Check if title is set to None when an empty string is given"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example-updated',
                'title': '',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        ecosystem = executed['data']['updateEcosystem']['ecosystem']
        self.assertEqual(ecosystem['id'], '1')
        self.assertEqual(ecosystem['name'], 'Example-updated')
        self.assertEqual(ecosystem['title'], None)
        self.assertEqual(ecosystem['description'], 'Example desc. updated')

    def test_description_empty(self):
        """Check if description is set to None when an empty string is given"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example-updated',
                'title': 'Example title updated',
                'description': ''
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        ecosystem = executed['data']['updateEcosystem']['ecosystem']
        self.assertEqual(ecosystem['id'], '1')
        self.assertEqual(ecosystem['name'], 'Example-updated')
        self.assertEqual(ecosystem['title'], 'Example title updated')
        self.assertEqual(ecosystem['description'], None)

    def test_name_empty(self):
        """Check if it fails when name is set to an empty string"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': '',
                'title': 'Example title updated',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, NAME_EMPTY_ERROR)

    def test_name_invalid(self):
        """Check if it fails updating ecosystems with an invalid name"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example updated',
                'title': 'Example title updated',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, INVALID_NAME_WHITESPACES)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example-updated',
                'title': 'Example title updated',
                'description': 'Example desc. updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_ECOSYSTEM,
                                  context_value=context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestUpdateProjectMutation(django.test.TestCase):
    """Unit tests for mutation to update projects"""

    BT_UPDATE_PROJECT = """
      mutation updateProj($id: ID, $data: ProjectInputType) {
        updateProject(id: $id, data: $data) {
          project {
            id
            name
            title
            parentProject {
              id
              name
            }
            ecosystem {
              id
              name
            }
          }
        }
      }
    """

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        self.ecosystem = Ecosystem.objects.create(id=1,
                                                  name='Example',
                                                  title='Example title',
                                                  description='Example desc.')

        self.project = Project.objects.create(id=1,
                                              name='example',
                                              title='Project title',
                                              ecosystem=self.ecosystem)

    def test_update_project(self):
        """Check if it updates a project"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'example-updated',
                'title': 'Project title updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check results, project was updated
        project = executed['data']['updateProject']['project']
        self.assertEqual(project['id'], '1')
        self.assertEqual(project['name'], 'example-updated')
        self.assertEqual(project['title'], 'Project title updated')
        self.assertEqual(project['parentProject'], None)

        ecosystem = project['ecosystem']
        self.assertEqual(ecosystem['id'], str(self.ecosystem.id))
        self.assertEqual(ecosystem['name'], 'Example')

        # Check database
        project_db = Project.objects.get(id=1)
        self.assertEqual(project_db.id, 1)
        self.assertEqual(project_db.name, 'example-updated')
        self.assertEqual(project_db.title, 'Project title updated')
        self.assertEqual(project_db.parent_project, None)
        self.assertEqual(project_db.ecosystem, self.ecosystem)

    def test_non_existing_project(self):
        """Check if it fails updating projects that do not exist"""

        client = graphene.test.Client(schema)

        params = {
            'id': 11111111,
            'data': {
                'name': 'example-updated',
                'title': 'Project title updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

    def test_title_empty(self):
        """Check if title is set to None when an empty string is given"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'example-updated',
                'title': ''
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        project = executed['data']['updateProject']['project']
        self.assertEqual(project['id'], '1')
        self.assertEqual(project['name'], 'example-updated')
        self.assertEqual(project['title'], None)
        self.assertEqual(project['parentProject'], None)

        ecosystem = project['ecosystem']
        self.assertEqual(ecosystem['id'], str(self.ecosystem.id))
        self.assertEqual(ecosystem['name'], 'Example')

    def test_name_empty(self):
        """Check if it fails when name is set to an empty string"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': '',
                'title': 'Example title updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, NAME_EMPTY_ERROR)

    def test_name_invalid(self):
        """Check if it fails updating projects with an invalid name"""

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'Example updated',
                'title': 'Example title updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, INVALID_NAME_WHITESPACES)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        params = {
            'id': 1,
            'data': {
                'name': 'example-updated',
                'title': 'Project title updated'
            }
        }
        executed = client.execute(self.BT_UPDATE_PROJECT,
                                  context_value=context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestMoveProjectMutation(django.test.TestCase):
    """Unit tests for mutation to move projects"""

    BT_MOVE_PROJECT = """
      mutation moveProj ($fromProjectId: ID,
                        $toProjectId: ID) {
        moveProject(fromProjectId: $fromProjectId,
                    toProjectId: $toProjectId) {
          project {
            id
            name
            title
            parentProject {
              id
              name
            }
            ecosystem {
              id
              name
            }
          }
        }
      }
    """

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        self.ecosystem = Ecosystem.objects.create(id=1,
                                                  name='Example',
                                                  title='Eco title')

        self.project = Project.objects.create(id=1,
                                              name='example',
                                              title='Example title',
                                              ecosystem=self.ecosystem)
        self.parent_project = Project.objects.create(id=2,
                                                     name='example-parent',
                                                     title='Example title',
                                                     ecosystem=self.ecosystem)

    def test_move_project(self):
        """Check if it moves a project to another one and to a given ecosystem"""

        client = graphene.test.Client(schema)

        params = {
            'fromProjectId': 1,
            'toProjectId': 2
        }
        executed = client.execute(self.BT_MOVE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        # Check results, project was updated with the parent project and the ecosystem
        project = executed['data']['moveProject']['project']
        self.assertEqual(project['id'], '1')
        self.assertEqual(project['name'], 'example')
        self.assertEqual(project['title'], 'Example title')

        parent_project = project['parentProject']
        self.assertEqual(parent_project['id'], '2')
        self.assertEqual(parent_project['name'], 'example-parent')

        ecosystem = project['ecosystem']
        self.assertEqual(ecosystem['id'], '1')
        self.assertEqual(ecosystem['name'], 'Example')

        # Check database
        project_db = Project.objects.get(id=1)
        self.assertEqual(project_db.id, 1)
        self.assertEqual(project_db.name, 'example')
        self.assertEqual(project_db.title, 'Example title')

        parent_project_db = project_db.parent_project
        self.assertEqual(parent_project_db.id, 2)
        self.assertEqual(parent_project_db.name, 'example-parent')

        ecosystem_db = project_db.ecosystem
        self.assertEqual(ecosystem_db.id, 1)
        self.assertEqual(ecosystem_db.name, 'Example')

    def test_from_project_not_exists(self):
        """Check if it fails when source project does not exist"""

        client = graphene.test.Client(schema)

        params = {
            'fromProjectId': 11111111,
            'toProjectId': 2
        }
        executed = client.execute(self.BT_MOVE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

    def test_to_project_not_exists(self):
        """Check if it fails when the destination parent project does not exist"""

        client = graphene.test.Client(schema)

        params = {
            'fromProjectId': 1,
            'toProjectId': 11111111
        }
        executed = client.execute(self.BT_MOVE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

    def test_to_project_invalid(self):
        """Check if it fails when the destination project is the same as the source"""

        client = graphene.test.Client(schema)

        params = {
            'fromProjectId': 1,
            'toProjectId': 1
        }
        executed = client.execute(self.BT_MOVE_PROJECT,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PARENT_PROJECT_ERROR)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        params = {
            'fromProjectId': 1,
            'toProjectId': 2
        }
        executed = client.execute(self.BT_MOVE_PROJECT,
                                  context_value=context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)
