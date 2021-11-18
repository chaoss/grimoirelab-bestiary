# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2021 Bitergia
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
#

import os

import click


@click.option('--config', envvar='BESTIARY_CONFIG',
              help="Configuration module in Python path syntax, e.g. bestiary.settings.")
@click.option('--dev', 'devel', is_flag=True, default=False,
              help="Run the service in developer mode.")
@click.command()
def bestiaryd(config, devel):
    """Starts the Bestiary server.

    Bestiary allows to visually manage software development ecosystems
    grouping them by projects and data sources. The server provides an API
    and a web interface to perform all the operations.

    To run the server, you will need to pass a configuration file module
    using Python path syntax (e.g. bestiary.settings). Take into account
    the module should be accessible by your PYTHON_PATH.

    By default, the server runs a WSGI app because in production it should
    be run with a reverse proxy. If you activate the '--dev' flag, a HTTP
    server will be run instead.
    """
    env = os.environ

    if config:
        env['UWSGI_ENV'] = f"DJANGO_SETTINGS_MODULE={config}"
    else:
        raise click.ClickException(
            "Configuration file not given. "
            "Set it with '--config' option "
            "or 'BESTIARY_CONFIG' env variable."
        )

    if devel:
        from django.conf import settings

        env['DJANGO_SETTINGS_MODULE'] = config
        env['UWSGI_HTTP'] = "127.0.0.1:8000"
        env['UWSGI_STATIC_MAP'] = settings.STATIC_URL + "=" + settings.STATIC_ROOT

    env['UWSGI_MODULE'] = "bestiary.app.wsgi:application"
    env['UWSGI_SOCKET'] = "0.0.0.0:9314"

    # These options shouldn't be modified
    env['UWSGI_MASTER'] = "true"
    env['UWSGI_ENABLE_THREADS'] = "true"
    env['UWSGI_LAZY_APPS'] = "true"
    env['UWSGI_SINGLE_INTERPRETER'] = "true"

    os.execvp("uwsgi", ("uwsgi",))


if __name__ == "__main__":
    bestiaryd()
