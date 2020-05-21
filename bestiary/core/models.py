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


from django.db.models import (CASCADE,
                              Model,
                              BooleanField,
                              CharField,
                              DateTimeField,
                              ForeignKey)

from django_mysql.models import JSONField

from enum import Enum

from grimoirelab_toolkit.datetime import datetime_utcnow


# Innodb and utf8mb4 can only index 191 characters
# For more information regarding this topic see:
# https://dev.mysql.com/doc/refman/5.5/en/charset-unicode-conversion.html
MAX_SIZE_CHAR_INDEX = 191
MAX_SIZE_CHAR_FIELD = 128
MAX_SIZE_NAME_FIELD = 32
MAX_SIZE_TITLE_FIELD = 80


class CreationDateTimeField(DateTimeField):
    """Field automatically set to the current date when an object is created."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', datetime_utcnow)
        super().__init__(*args, **kwargs)


class LastModificationDateTimeField(DateTimeField):
    """Field automatically set to the current date on each save() call."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', datetime_utcnow)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = datetime_utcnow()
        setattr(model_instance, self.attname, value)
        return value


class EntityBase(Model):
    created_at = CreationDateTimeField()
    last_modified = LastModificationDateTimeField()

    class Meta:
        abstract = True


class Transaction(Model):
    """Model class for Transaction objects.

    This class is meant to represent objects which are
    created inside a context (e.g., a method from the API)
    where the database is going to be modified in some way.

    Every transaction object must have a unique identifier
    (`tuid`) and the name of the method creating the
    transaction (`name`).

    :param tuid: unique identifier for the transaction.
    :param name: name of the method creating the transaction.
    :param created_at: datetime when the transaction is created.
    :param closed_at: datetime when the transaction is closed.
    :param is_closed: boolean value, `True` if the transaction is closed.
    :param authored_by: username from who created the transaction.
    """
    tuid = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                     primary_key=True,
                     help_text='Transaction unique identifier')
    name = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                     help_text='Name of the method creating the transaction')
    created_at = DateTimeField(help_text='Datetime when the transaction was created')
    closed_at = DateTimeField(null=True,
                              help_text='Datetime when the transaction was closed')
    is_closed = BooleanField(default=False,
                             help_text='Boolean value, `True` if the transaction is closed')
    authored_by = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                            null=True,
                            help_text='Username from who created the transaction')

    class Meta:
        db_table = 'transactions'
        ordering = ('created_at', 'tuid')

    def __str__(self):
        return '%s - %s' % (self.tuid, self.name)


class Operation(Model):
    """Model class for Transaction objects.

    This class is meant to represent atomic interactions
    with the database (either add, delete or update something)
    and the entities which are involved in this interaction.
    An `Operation` object is including the original arguments
    from the method creating the operation.

    Every operation object must have a unique identifier
    (`ouid`), its operation type (`ADD`, `DELETE` or `UPDATE`),
    the type of the entity affected by this operation, the targeted
    object and the parent transaction where this operation is
    performed.

    :param ouid: unique identifier for the operation.
    :param op_type: type of the operation (`ADD`, `DELETE` or `UPDATE`).
    :param entity_type: type of the entity affected by this operation.
    :param target: identifier for the main object affected by the
        operation.
    :param trx: parent Transaction object.
    :param timestamp: datetime when this operation is performed.
    :param args: main input arguments from the method performing the
        operation. They are serialized in JSON format.
    """
    class OpType(Enum):
        ADD = 'ADD'
        DELETE = 'DELETE'
        UPDATE = 'UPDATE'

        @classmethod
        def choices(cls):
            return ((item.name, item.value) for item in cls)

        def __str__(self):
            return self.value

    ouid = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                     primary_key=True,
                     help_text='Operation unique identifier')
    op_type = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                        choices=OpType.choices(),
                        help_text='Operation type (`ADD`, `DELETE` or `UPDATE`)')
    entity_type = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                            help_text='Type of the main entity involved in the operation')
    target = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                       help_text='Identifier of the targeted entity in the operation')
    trx = ForeignKey(Transaction,
                     related_name='operations',
                     on_delete=CASCADE,
                     db_column='tuid',
                     help_text='Transaction (context) where this operation is performed')
    timestamp = DateTimeField(help_text='Datetime when the operation is performed')
    args = JSONField(help_text='Main input arguments when performing the operation')

    class Meta:
        db_table = 'operations'
        ordering = ('timestamp', 'ouid', 'trx')

    def __str__(self):
        return '%s - %s - %s - %s - %s' % (self.ouid, self.trx, self.op_type, self.entity_type, self.target)


class Project(EntityBase):
    """Model class for Project objects.

    This class is meant to represent a set of data locations which
    have to be grouped under the same entity. Moreover, this grouping
    may have a hierarchy by defining n sub-projects.

    Every project object must have a name (`name`) and must belong
    to one single Ecosystem (`ecosystem`).
    Optionally, it may have a title (`title`), and a relation with
    a parent project (`parent_project`).

    :param name: Name of the project
    :param title: Title of the project
    :param parent_project: Parent project object
    :param ecosystem: Ecosystem which the project belongs to
    """
    name = CharField(unique=True,
                     max_length=MAX_SIZE_NAME_FIELD,
                     help_text='Project name')
    title = CharField(max_length=MAX_SIZE_TITLE_FIELD,
                      null=True,
                      help_text='Project title')
    parent_project = ForeignKey("Project",
                                parent_link=True,
                                null=True,
                                on_delete=CASCADE,
                                related_name='subprojects',
                                help_text='Parent project')
    ecosystem = ForeignKey("Ecosystem",
                           null=True,
                           on_delete=CASCADE,
                           help_text='Ecosystem')

    class Meta:
        db_table = 'projects'
        unique_together = ('name',)
        ordering = ('name',)

    def __str__(self):
        return '%s' % self.name


class Ecosystem(EntityBase):
    """Model class for Ecosystem objects.

    This class is meant to represent an abstract set of projects
    which may share a common context.

    Every ecosystem object must have a unique name (`name`).
    Optionally, it may have a title (`title`) and a `description`
    field containing a brief text describing what
    the ecosystem is about.

    :param name: Name of the ecosystem
    :param title: Title of the ecosystem
    :param description: Description of the ecosystem
    """
    name = CharField(unique=True,
                     max_length=MAX_SIZE_NAME_FIELD,
                     help_text='Ecosystem name')
    title = CharField(max_length=MAX_SIZE_TITLE_FIELD,
                      null=True,
                      help_text='Ecosystem title')
    description = CharField(max_length=MAX_SIZE_CHAR_FIELD,
                            null=True,
                            help_text='Brief text describing the ecosystem')

    class Meta:
        db_table = 'ecosystems'
        unique_together = ('name', )
        ordering = ('name', )

    def __str__(self):
        return '%s' % self.name
