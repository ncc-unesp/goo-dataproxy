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
