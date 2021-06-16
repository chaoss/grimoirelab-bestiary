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

import django.db.transaction

from .db import (find_ecosystem,
                 find_project,
                 add_ecosystem as add_ecosystem_db,
                 add_project as add_project_db,
                 update_ecosystem as update_ecosystem_db,
                 update_project as update_project_db,
                 delete_ecosystem as delete_ecosystem_db,
                 delete_project as delete_project_db,
                 link_parent_project as link_parent_project_db)
from .errors import AlreadyExistsError, InvalidValueError, NotFoundError
from .log import TransactionsLog


@django.db.transaction.atomic
def add_ecosystem(ctx, name, title=None, description=None):
    """Add an ecosystem to the registry.

    This function adds an ecosystem to the registry.
    It checks first whether the ecosystem is already on the registry.
    When it is not found, the new ecosystem is added. Otherwise,
    it raises a 'AlreadyExistsError' exception to notify that the ecosystem
    already exists.

    :param ctx: context from where this method is called
    :param name: name of the ecosystem
    :param title: title of the ecosystem
    :param description: description of the ecosystem

    :raises InvalidValueError: raised when name is None or an empty string
    :raises TypeError: raised when name is not a string or a NoneType
    :raises AlreadyExistsError: raised when the ecosystem already exists
        in the registry
    """
    if name is None:
        raise InvalidValueError(msg="'name' cannot be None")
    if name == '':
        raise InvalidValueError(msg="'name' cannot be an empty string")
    if title == '':
        raise InvalidValueError(msg="'title' cannot be an empty string")
    if description == '':
        raise InvalidValueError(msg="'description' cannot be an empty string")

    trxl = TransactionsLog.open('add_ecosystem', ctx)

    try:
        ecosystem = add_ecosystem_db(trxl,
                                     name=name,
                                     title=title,
                                     description=description)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return ecosystem


@django.db.transaction.atomic
def add_project(ctx, ecosystem_id, name, title=None, parent_id=None):
    """Add a project to the registry.

    This function adds a project to the registry.
    It checks first whether the project is already on the registry.
    When it is not found, the new project is added. Otherwise,
    it raises a 'AlreadyExistsError' exception to notify that the project
    already exists.

    :param ctx: context from where this method is called
    :param ecosystem_id: ID of the ecosystem where this project belongs to
    :param name: name of the project
    :param title: title of the project
    :param parent_id: ID of the parent project to be set to the new project

    :raises InvalidValueError: raised when name is None or an empty string
        or when the parent project to be set is invalid
    :raises TypeError: raised when name is not a string or a NoneType
    :raises AlreadyExistsError: raised when the project already exists
        in the registry
    """
    if name is None:
        raise InvalidValueError(msg="'name' cannot be None")
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")
    if name == '':
        raise InvalidValueError(msg="'name' cannot be an empty string")
    if title == '':
        raise InvalidValueError(msg="'title' cannot be an empty string")

    trxl = TransactionsLog.open('add_project', ctx)

    try:
        ecosystem = find_ecosystem(ecosystem_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        parent = find_project(parent_id) if parent_id else None
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        project = add_project_db(trxl,
                                 ecosystem,
                                 name,
                                 title=title,
                                 parent=parent)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return project


@django.db.transaction.atomic
def update_ecosystem(ctx, ecosystem_id, **kwargs):
    """Update an ecosystem.

    This function allows to edit or update the ecosystem information
    of the `Ecosystem` object identified by `id`.

    The values to update are given as keyword arguments. The allowed
    keys are listed below (other keywords will be ignored):

       - `name`: unique name of the ecosystem
       - `title`: title of the ecosystem
       - `description`: description of the ecosystem

    The result of calling this function will be the updated
    `Ecosystem` object.

    :param ctx: context from where this method is called
    :param ecosystem_id: identifier of the ecosystem to be updated
    :param kwargs: keyword arguments with data to update the ecosystem

    :returns: an updated ecosystem

    :raises NotFoundError: raised when either ecosystem do not exist in
        the registry.
    :raises InvalidValueError: raised when any of the keyword arguments
        has an invalid value.
    """
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")

    trxl = TransactionsLog.open('update_ecosystem', ctx)

    ecosystem = find_ecosystem(ecosystem_id)

    try:
        ecosystem = update_ecosystem_db(trxl, ecosystem, **kwargs)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))

    trxl.close()

    return ecosystem


@django.db.transaction.atomic
def update_project(ctx, project_id, **kwargs):
    """Update the information of a given project.

    This function allows to edit or update the project information
    of the `Project` object identified by `id`.

    The values to update are given as keyword arguments. The allowed
    keys are listed below (other keywords will be ignored):

       - `name`: unique name of the project
       - `title`: title of the project

    The result of calling this function will be the updated
    `Project` object.

    :param ctx: context from where this method is called
    :param project_id: identifier of the project to be updated
    :param kwargs: keyword arguments with data to update the project

    :returns: an updated project

    :raises NotFoundError: raised when either project do not exist in
        the registry.
    :raises InvalidValueError: raised when any of the keyword arguments
        has an invalid value.
    """
    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")

    trxl = TransactionsLog.open('update_project', ctx)

    project = find_project(project_id)

    try:
        project = update_project_db(trxl, project, **kwargs)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))

    trxl.close()

    return project


@django.db.transaction.atomic
def delete_ecosystem(ctx, ecosystem_id):
    """Remove an ecosystem from the registry.

    This function removes the given ecosystem from the registry.
    It checks first whether the ecosystem is already on the registry.
    When it is found, the ecosystem is removed. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param ecosystem_id: id of the ecosystem to remove

    :raises InvalidValueError: raised when ecosystem is None or an empty string
    :raises NotFoundError: raised when the ecosystem does not exist
        in the registry
    """
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")

    trxl = TransactionsLog.open('delete_ecosystem', ctx)

    try:
        ecosystem = find_ecosystem(ecosystem_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    delete_ecosystem_db(trxl, ecosystem=ecosystem)

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    ecosystem.id = ecosystem_id

    return ecosystem


@django.db.transaction.atomic
def delete_project(ctx, project_id):
    """Remove a project from the registry.

    This function removes the given project from the registry.
    It checks first whether the project is already on the registry.
    When it is found, the project is removed. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param project_id: id of the project to remove

    :raises InvalidValueError: raised when project is None or an empty string
    :raises NotFoundError: raised when the project does not exist
        in the registry
    """
    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")

    trxl = TransactionsLog.open('delete_project', ctx)

    try:
        project = find_project(project_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    delete_project_db(trxl, project=project)

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    project.id = project_id

    return project


@django.db.transaction.atomic
def move_project(ctx, from_project_id, to_project_id):
    """Move a project to a parent project.

    Link a project with another one with a child-parent relation. If a project
    is not linked to any project, it is a root project.
    If the source project was already linked to a parent project, it will be
    overwritten.

    :param ctx: context from where this method is called
    :param from_project_id: Project to be linked to another project or to an ecosystem
    :param to_project_id: Destination project which will be linked as a parent project

    :returns: the updated project object

    :raises InvalidValueError: raised when from_project_id is None or any of the
        other IDs are invalid, or when the parent project to be set is invalid
    :raises NotFoundError: raised when the any of the projects or the ecosystem
        do not exist in the registry
    """
    if from_project_id is None:
        raise InvalidValueError(msg="'from_project_id' cannot be None")

    trxl = TransactionsLog.open('move_project', ctx)

    try:
        from_project = find_project(from_project_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        to_project = find_project(to_project_id) if to_project_id else None
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    from_project = link_parent_project_db(trxl, from_project, to_project)

    return from_project
