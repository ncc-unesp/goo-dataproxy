# This file is part of goo-dataproxy.
#
# Copyright (c) 2103-2014 by Núcleo de Computação Científica, UNESP
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#    Gabriel von. Winckler <winckler AT ncc DOT unesp DOT br>
#
# goo-dataproxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# goo-dataproxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4
from tastypie.authentication import Authentication

from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError

from django.conf import settings
import sys

class TokenAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        # check if token exists inside the request
        try:
            token = request.GET['token']
        except KeyError:
            return False

        goo_server = settings.GOO_SERVER_URI
        debug = sys.stderr if settings.DEBUG else False
        server = API(goo_server, debug=debug)
        try:
            response = server.token.get(token=token)
            if response['expire_time']:
                request.token = token
                return True
            else:
                return False # pragma: no cover
        except HttpClientError as e:
            if e.code == 401:
                # maybe a pilot token
                try:
                    response = server.pilot.token.get(token=token)
                    if response['valid']:
                        request.token = token
                        return True
                    else:
                        return False
                except HttpClientError as e:
                    if e.code == 401:
                        return False
                    else:
                        raise e # pragma: no cover
            else:
                raise e # pragma: no cover

        return False # pragma: no cover
