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
import unittest.mock

import django.test
import django_rq
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
                                  DataSet,
                                  DataSourceType,
                                  DataSource,
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
DATASOURCE_NAME_DOES_NOT_EXIST_ERROR = "DataSourceType name .+ not found in the registry"
DUPLICATED_DATASET_ERROR = "DataSet '.+' already exists in the registry"
DATASET_DOES_NOT_EXIST_ERROR = "DataSet ID .+ not found in the registry"

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
BT_DATASETS_QUERY = """{
  datasets {
    entities {
      id
      datasource {
        type {
          name
        }
        uri
      }
      category
      project {
        id
        name
      }
      filters
    }
  }
}"""
BT_DATASETS_QUERY_FILTER_CATEGORY = """{
  datasets (
    filters: {
      projectId: %d
      category: "%s"
    }
  ) {
    entities {
      id
      datasource {
        type {
          name
        }
        uri
      }
      category
      project {
        id
        name
      }
      filters
    }
  }
}"""
BT_DATASETS_QUERY_FILTER_URI = """{
  datasets (
    filters: {
      projectId: %d
      uri: "%s"
    }
  ) {
    entities {
      id
      datasource {
        type {
          name
        }
        uri
      }
      category
      project {
        id
        name
      }
      filters
    }
  }
}"""
BT_DATASETS_QUERY_PAGINATION = """{
  datasets (
    page: %d
    pageSize: %d
  ){
    entities {
      id
      datasource {
        type {
          name
        }
        uri
      }
      category
      project {
        id
        name
      }
      filters
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
BT_JOB_QUERY = """{
  job(
    jobId:"%s"
  ){
    jobId
    jobType
    status
    errors
    result {
      __typename
    }
  }
}
"""
BT_JOBS_QUERY = """{
  jobs(page: 1) {
    entities {
      jobId
      jobType
      status
      errors
      result {
        __typename
      }
    }
  }
}
"""
BT_JOBS_QUERY_PAGINATION = """{
  jobs(page: %d, pageSize: %d) {
    entities {
      jobId
      jobType
      status
      errors
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
}
"""
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

        self.eco = Ecosystem.objects.create(name='Eco-example')
        self.proj = Project(name='Example',
                            title='Example title',
                            ecosystem=self.eco)
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
        self.assertEqual(proj['ecosystem']['id'], str(self.eco.id))

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
        self.assertEqual(proj['ecosystem']['id'], str(self.eco.id))

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
                        title='Example title 1',
                        ecosystem=self.eco)
        proj1.save()

        proj2 = Project(name='Example-2',
                        title='Example title 2',
                        ecosystem=self.eco)
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
        self.assertEqual(proj['ecosystem']['id'], str(self.eco.id))

        proj = projects[1]
        self.assertEqual(proj['id'], str(proj1.id))
        self.assertEqual(proj['name'], 'Example-1')
        self.assertEqual(proj['title'], 'Example title 1')
        self.assertEqual(proj['parentProject'], None)
        self.assertEqual(proj['ecosystem']['id'], str(self.eco.id))

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
        self.assertEqual(proj['ecosystem']['id'], str(self.eco.id))

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


class TestQueryDatasets(django.test.TestCase):
    """Unit tests for dataset queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.eco = Ecosystem.objects.create(name='Eco-example')
        self.project = Project.objects.create(id=1,
                                              name='example',
                                              title='Project title',
                                              ecosystem=self.eco)
        self.dstype = DataSourceType.objects.create(name='GitHub')
        self.dsource = DataSource.objects.create(id=1,
                                                 type=self.dstype,
                                                 uri='https://github.com/chaoss/grimoirelab-bestiary')
        self.filters = {'tag': 'test'}
        self.dataset = DataSet.objects.create(id=1,
                                              project=self.project,
                                              datasource=self.dsource,
                                              category='issues',
                                              filters=json.dumps(self.filters))

    def test_dataset(self):
        """Check if it returns the list of datasets"""

        client = graphene.test.Client(schema)
        executed = client.execute(BT_DATASETS_QUERY,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']

        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['id'], str(self.dataset.id))
        self.assertEqual(dataset['project']['id'], str(self.project.id))
        self.assertEqual(dataset['project']['name'], self.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], self.dsource.type.name)
        self.assertEqual(dataset['datasource']['uri'], self.dsource.uri)
        self.assertEqual(dataset['category'], 'issues')
        self.assertEqual(dataset['filters'], self.filters)

    def test_filter_category(self):
        """Check whether it returns the project searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_DATASETS_QUERY_FILTER_CATEGORY % (self.project.id, 'issues')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['id'], str(self.dataset.id))
        self.assertEqual(dataset['project']['id'], str(self.project.id))
        self.assertEqual(dataset['project']['name'], self.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], self.dsource.type.name)
        self.assertEqual(dataset['datasource']['uri'], self.dsource.uri)
        self.assertEqual(dataset['category'], 'issues')
        self.assertEqual(dataset['filters'], self.filters)

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing dataset"""

        client = graphene.test.Client(schema)
        test_query = BT_DATASETS_QUERY_FILTER_CATEGORY % (11111111, 'unknown')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertListEqual(datasets, [])

        test_query = BT_DATASETS_QUERY_FILTER_URI % (self.project.id, 'unknown')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertListEqual(datasets, [])

    def test_filter_uri(self):
        """Check whether it returns the project searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_DATASETS_QUERY_FILTER_URI % (self.project.id,
                                                     'https://github.com/chaoss/grimoirelab-bestiary')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['id'], str(self.dataset.id))
        self.assertEqual(dataset['project']['id'], str(self.project.id))
        self.assertEqual(dataset['project']['name'], self.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], self.dsource.type.name)
        self.assertEqual(dataset['datasource']['uri'], self.dsource.uri)
        self.assertEqual(dataset['category'], 'issues')
        self.assertEqual(dataset['filters'], self.filters)

    def test_pagination(self):
        """Check whether it returns the projects searched when using pagination"""

        # Creating additional datasets
        dataset2 = DataSet.objects.create(id=2,
                                          project=self.project,
                                          datasource=self.dsource,
                                          category='pull-requests',
                                          filters=json.dumps({'tag': 'test'}))

        dataset3 = DataSet.objects.create(id=3,
                                          project=self.project,
                                          datasource=self.dsource,
                                          category='issues',
                                          filters=json.dumps({'tag': 'test2'}))

        client = graphene.test.Client(schema)
        test_query = BT_DATASETS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertEqual(len(datasets), 2)

        dataset = datasets[0]
        self.assertEqual(dataset['id'], str(self.dataset.id))
        self.assertEqual(dataset['project']['id'], str(self.project.id))
        self.assertEqual(dataset['project']['name'], self.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], self.dsource.type.name)
        self.assertEqual(dataset['datasource']['uri'], self.dsource.uri)
        self.assertEqual(dataset['category'], 'issues')
        self.assertEqual(dataset['filters'], self.filters)

        dataset = datasets[1]
        self.assertEqual(dataset['id'], str(dataset2.id))
        self.assertEqual(dataset['project']['id'], str(dataset2.project.id))
        self.assertEqual(dataset['project']['name'], dataset2.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], dataset2.datasource.type.name)
        self.assertEqual(dataset['datasource']['uri'], dataset2.datasource.uri)
        self.assertEqual(dataset['category'], dataset2.category)
        self.assertEqual(dataset['filters'], {'tag': 'test'})

        pag_data = executed['data']['datasets']['pageInfo']
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
        test_query = BT_DATASETS_QUERY_PAGINATION % (2, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertEqual(len(datasets), 1)

        dataset = datasets[0]
        self.assertEqual(dataset['id'], str(dataset3.id))
        self.assertEqual(dataset['project']['id'], str(dataset3.project.id))
        self.assertEqual(dataset['project']['name'], dataset3.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], dataset3.datasource.type.name)
        self.assertEqual(dataset['datasource']['uri'], dataset3.datasource.uri)
        self.assertEqual(dataset['category'], dataset3.category)
        self.assertEqual(dataset['filters'], {'tag': 'test2'})

        pag_data = executed['data']['datasets']['pageInfo']
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
        DataSet.objects.all().delete()
        datasets = DataSet.objects.all()

        self.assertEqual(len(datasets), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_DATASETS_QUERY,
                                  context_value=self.context_value)

        datasets = executed['data']['datasets']['entities']
        self.assertListEqual(datasets, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_DATASETS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class MockJob:
    """Class mock job queries."""

    def __init__(self, job_id, func_name, status, result, error=None):
        self.id = job_id
        self.func_name = func_name
        self.status = status
        self.result = result
        self.exc_info = error
        self.enqueued_at = datetime_utcnow()

    def get_status(self):
        return self.status

    def get_id(self):
        return self.id


class TestQueryJob(django.test.TestCase):
    """Unit tests for job queries"""

    def setUp(self):
        """Set queries context"""

        conn = django_rq.queues.get_redis_connection(None, True)
        conn.flushall()

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

    @unittest.mock.patch('bestiary.core.schema.find_job')
    def test_job(self, mock_job):
        """Check if it returns an affiliated result type"""

        result = {
            'results': None,
            'errors': None
        }

        job = MockJob('1234-5678-90AB-CDEF', 'sample', 'finished', result)
        mock_job.return_value = job

        # Tests
        client = graphene.test.Client(schema)

        query = BT_JOB_QUERY % '1234-5678-90AB-CDEF'

        executed = client.execute(query,
                                  context_value=self.context_value)

        job_data = executed['data']['job']
        self.assertEqual(job_data['jobId'], '1234-5678-90AB-CDEF')
        self.assertEqual(job_data['jobType'], 'sample')
        self.assertEqual(job_data['status'], 'finished')
        self.assertEqual(job_data['errors'], None)
        self.assertEqual(job_data['result'], None)

    def test_job_not_found(self):
        """Check if it returns an error when the job is not found"""

        # Tests
        client = graphene.test.Client(schema)

        query = BT_JOB_QUERY % '1234-5678-90AB-CDEF'

        executed = client.execute(query,
                                  context_value=self.context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, "1234-5678-90AB-CDEF not found in the registry")

    @unittest.mock.patch('bestiary.core.schema.find_job')
    def test_failed_job(self, mock_job):
        """Check if it returns an error when the job has failed"""

        job = MockJob('90AB-CD12-3456-78EF', 'sample', 'failed', None, 'Error')
        mock_job.return_value = job

        # Tests
        client = graphene.test.Client(schema)

        query = BT_JOB_QUERY % '90AB-CD12-3456-78EF'

        executed = client.execute(query,
                                  context_value=self.context_value)

        job_data = executed['data']['job']
        self.assertEqual(job_data['status'], 'failed')
        self.assertEqual(job_data['errors'], ['Error'])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_JOB_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)

    @unittest.mock.patch('bestiary.core.schema.get_jobs')
    def test_jobs(self, mock_jobs):
        """Check if it returns a list of jobs"""

        job = MockJob('1234-5678-90AB-CDEF', 'sample', 'queued', None)
        mock_jobs.return_value = [job]

        # Tests
        client = graphene.test.Client(schema)

        executed = client.execute(BT_JOBS_QUERY,
                                  context_value=self.context_value)

        jobs_entities = executed['data']['jobs']['entities']
        self.assertEqual(len(jobs_entities), 1)
        self.assertEqual(jobs_entities[0]['jobId'], '1234-5678-90AB-CDEF')
        self.assertEqual(jobs_entities[0]['jobType'], 'sample')
        self.assertEqual(jobs_entities[0]['status'], 'queued')
        self.assertEqual(jobs_entities[0]['errors'], [])
        self.assertEqual(jobs_entities[0]['result'], [])

    def test_jobs_no_results(self):
        """Check if it returns an empty list when no jobs are found"""

        client = graphene.test.Client(schema)

        executed = client.execute(BT_JOBS_QUERY,
                                  context_value=self.context_value)

        jobs_entities = executed['data']['jobs']['entities']
        self.assertEqual(len(jobs_entities), 0)

    @unittest.mock.patch('bestiary.core.schema.get_jobs')
    def test_jobs_pagination(self, mock_jobs):
        """Check if it returns a paginated list of jobs"""

        job1 = MockJob('1234-5678-90AB-CDEF', 'sample_1', 'queued', None)
        job2 = MockJob('5678-5678-90EF-GHIJ', 'sample_2', 'queued', None)
        job3 = MockJob('9123-5678-90IJ-KLMN', 'sample_3', 'queued', None)
        mock_jobs.return_value = [job1, job2, job3]

        # Tests
        client = graphene.test.Client(schema)
        test_query = BT_JOBS_QUERY_PAGINATION % (2, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        jobs_entities = executed['data']['jobs']['entities']
        self.assertEqual(len(jobs_entities), 1)
        self.assertEqual(jobs_entities[0]['jobId'], '9123-5678-90IJ-KLMN')
        self.assertEqual(jobs_entities[0]['jobType'], 'sample_3')
        self.assertEqual(jobs_entities[0]['status'], 'queued')
        self.assertEqual(jobs_entities[0]['errors'], [])

        jobs_pagination = executed['data']['jobs']['pageInfo']
        self.assertEqual(jobs_pagination['page'], 2)
        self.assertEqual(jobs_pagination['pageSize'], 2)
        self.assertEqual(jobs_pagination['numPages'], 2)
        self.assertFalse(jobs_pagination['hasNext'])
        self.assertTrue(jobs_pagination['hasPrev'])
        self.assertEqual(jobs_pagination['startIndex'], 3)
        self.assertEqual(jobs_pagination['endIndex'], 3)
        self.assertEqual(jobs_pagination['totalResults'], 3)


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


class TestAddDatasetMutation(django.test.TestCase):
    """Unit tests for mutation to add datasets"""

    BT_ADD_DATASET = """
      mutation addDatasetTest ($projectId: ID,
                           $datasourceName:String,
                           $uri: String,
                           $category: String,
                           $filters: JSONString) {
        addDataset(projectId: $projectId,
                   datasourceName: $datasourceName,
                   uri: $uri,
                   category: $category,
                   filters: $filters)
        {
          dataset {
            id
            datasource {
              type {
                name
              }
              uri
            }
            category
            project {
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
        self.project = Project.objects.create(id=1,
                                              name='example',
                                              title='Project title',
                                              ecosystem=self.eco)
        self.dstype = DataSourceType.objects.create(id=1, name='GitHub')

    def test_add_dataset(self):
        """Check if a new dataset is added"""

        params = {
            'projectId': 1,
            'datasourceName': 'GitHub',
            'uri': 'https://github.com/chaoss/grimoirelab-bestiary',
            'category': 'issues',
            'filters': '{"a": 1}'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        dataset = executed['data']['addDataset']['dataset']

        self.assertEqual(dataset['project']['id'], str(self.project.id))
        self.assertEqual(dataset['project']['name'], self.project.name)
        self.assertEqual(dataset['datasource']['type']['name'], 'GitHub')
        self.assertEqual(dataset['datasource']['uri'],
                         'https://github.com/chaoss/grimoirelab-bestiary')
        self.assertEqual(dataset['category'], 'issues')

        # Check database
        dset_db = DataSet.objects.get(id=int(dataset['id']))
        self.assertEqual(dset_db.id, int(dataset['id']))
        self.assertEqual(dset_db.project.id, self.project.id)
        self.assertEqual(dset_db.project.name, self.project.name)
        self.assertEqual(dset_db.datasource.type.name, 'GitHub')
        self.assertEqual(dset_db.datasource.uri,
                         'https://github.com/chaoss/grimoirelab-bestiary')
        self.assertEqual(dset_db.category, 'issues')

    def test_not_found_project(self):
        """Check whether datasets cannot be added when the project is not found"""

        Project.objects.filter(id=11111111).delete()
        params = {
            'projectId': 11111111,
            'datasourceName': 'GitHub',
            'uri': 'https://github.com/chaoss/grimoirelab',
            'category': 'issues',
            'filters': '{"a": 1}'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertEqual(msg, PROJECT_DOES_NOT_EXIST_ERROR)

        # Check database
        datasets = DataSet.objects.filter(
            datasource__uri='https://github.com/chaoss/grimoirelab')
        self.assertEqual(len(datasets), 0)

    def test_not_found_parent(self):
        """Check whether datasets cannot be added when the data source type is not found"""

        params = {
            'projectId': 1,
            'datasourceName': 'GitLab',
            'uri': 'https://github.com/chaoss/grimoirelab',
            'category': 'issues',
            'filters': '{"a": 1}'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertRegex(msg, DATASOURCE_NAME_DOES_NOT_EXIST_ERROR)

        # Check database
        datasets = DataSet.objects.filter(
            datasource__uri='https://github.com/chaoss/grimoirelab')
        self.assertEqual(len(datasets), 0)

    def test_integrity_error(self):
        """Check whether there shouldn't be identical data sets"""

        params = {
            'projectId': 1,
            'datasourceName': 'GitHub',
            'uri': 'https://github.com/chaoss/grimoirelab-bestiary',
            'category': 'issues',
            'filters': '{}'
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_DATASET,
                                  context_value=self.context_value,
                                  variables=params)
        dataset = executed['data']['addDataset']['dataset']
        dataset_id = int(dataset['id'])

        # Check database
        dataset_db = DataSet.objects.get(id=dataset_id)
        self.assertEqual(dataset_db.id, dataset_id)
        self.assertEqual(dataset_db.project.id, self.project.id)
        self.assertEqual(dataset_db.project.name, self.project.name)
        self.assertEqual(dataset_db.datasource.type.name, 'GitHub')
        self.assertEqual(dataset_db.datasource.uri,
                         'https://github.com/chaoss/grimoirelab-bestiary')
        self.assertEqual(dataset_db.category, 'issues')
        self.assertEqual(dataset_db.filters, '{}')

        # Try to insert it twice
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_ADD_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        msg = executed['errors'][0]['message']
        self.assertRegex(msg, DUPLICATED_DATASET_ERROR)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_ADD_DATASET,
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

        eco = Ecosystem.objects.create(name='Eco-example')
        self.proj_ex = Project.objects.create(id=1,
                                              name='Example',
                                              ecosystem=eco)

        self.proj_bit = Project.objects.create(id=2,
                                               name='Bitergia',
                                               ecosystem=eco)

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


class TestDeleteDatasetMutation(django.test.TestCase):
    """Unit tests for mutation to delete datasets"""

    BT_DELETE_DATASET = """
      mutation delDatasetTest($id: ID) {
        deleteDataset(id: $id) {
          dataset {
            id
            datasource {
              type {
                name
              }
              uri
            }
            category
          }
        }
      }
    """

    def setUp(self):
        """Set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        eco = Ecosystem.objects.create(name='Eco-example')
        project = Project.objects.create(id=1,
                                         name='example',
                                         title='Project title',
                                         ecosystem=eco)
        dstype = DataSourceType.objects.create(id=1, name='GitHub')

        dsource = DataSource.objects.create(id=1,
                                            type=dstype,
                                            uri='https://github.com/chaoss/grimoirelab-bestiary')
        self.dataset_1 = DataSet.objects.create(id=1,
                                                project=project,
                                                datasource=dsource,
                                                category='issues',
                                                filters=json.dumps({'tag': 'test'}))

        self.dataset_2 = DataSet.objects.create(id=2,
                                                project=project,
                                                datasource=dsource,
                                                category='pull-requests',
                                                filters=json.dumps({'tag': 'test'}))

    def test_delete_dataset(self):
        """Check whether it deletes a dataset"""

        # Delete project
        params = {
            'id': 1
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        # Check result
        dataset = executed['data']['deleteDataset']['dataset']
        self.assertEqual(dataset['id'], '1')
        self.assertEqual(dataset['datasource']['type']['name'], 'GitHub')
        self.assertEqual(dataset['datasource']['uri'],
                         'https://github.com/chaoss/grimoirelab-bestiary')
        self.assertEqual(dataset['category'], 'issues')

        # Tests
        with self.assertRaises(django.core.exceptions.ObjectDoesNotExist):
            DataSet.objects.get(id=1)

        ndatasets = DataSet.objects.count()
        self.assertEqual(ndatasets, 1)

    def test_not_found_dataset(self):
        """Check if it returns an error when a dataset does not exist"""

        params = {
            'id': 11111111
        }
        client = graphene.test.Client(schema)
        executed = client.execute(self.BT_DELETE_DATASET,
                                  context_value=self.context_value,
                                  variables=params)

        # Check error
        msg = executed['errors'][0]['message']
        self.assertRegex(msg, DATASET_DOES_NOT_EXIST_ERROR)

        datasets = DataSet.objects.all()
        self.assertEqual(len(datasets), 2)

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(self.BT_DELETE_DATASET,
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
