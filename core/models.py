# vim: tabstop=4 shiftwidth=4 softtabstop=4

from core import storage

from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError

from django.conf import settings

import os, hashlib, sys

class DataObject(object):
    def __init__(self, token=None):
        goo_server = settings.GOO_SERVER_URI
        self.proxy_token = settings.GOO_SERVER_TOKEN
        self.user_token = token
        debug = sys.stderr if settings.DEBUG else False
        self.server = API(goo_server, debug=debug)

    def load(self, oid):
        obj = self.server.dataobjects(oid).get(token=self.user_token,
                                               proxy_token=self.proxy_token)

        self.sha1 = obj['sha1']
        self.data_proxy_servers = obj['data_proxy_servers']
        self.name = obj['name']
        self.size = obj['size']
        self.oid = oid

        return self

    def file(self):
        """ Must call load(oid) load before """
        return storage.download(self.sha1)

    def save(self, name, req_file, public=False):
        self.name = name
        self.public = public

        # calculate SHA256
        digest = hashlib.sha1()
        with open(req_file,'rb') as f:
            for chunk in iter(lambda: f.read(128*digest.block_size), b''):
                digest.update(chunk)

        self.sha1 = digest.hexdigest()
        self.size = os.path.getsize(req_file)
        storage.upload(req_file, self.sha1)

        values = {"name": self.name,
                  "size": self.size,
                  "sha1": self.sha1,
                  "public": self.public}

        response = self.server.dataobjects.post(values, token=self.user_token,
                                                proxy_token=self.proxy_token)

        self.oid = response["id"]
        self.resource_uri = response["resource_uri"]

    def delete(self):
        """ Must call load(oid) load before """
        # content data deletion
        storage.delete(self.sha1)
        # metadata deletion
        self.server.dataobjects(self.oid).delete(token=self.user_token,
                                                 proxy_token=self.proxy_token)
