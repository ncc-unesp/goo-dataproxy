from unittest import TestCase

from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError
import hashlib

import json
import sys

class DataObjectResourceTest(TestCase):
    def setUp(self):
        super(DataObjectResourceTest, self).setUp()

        self.endpoint = 'http://localhost:8001/api/v1/dataproxy/'
        self.format = 'json'

        self.filename = '/bin/true'
        self.object_name = 'true'

        debug = sys.stderr if settings.DEBUG else False
        self.server = API(self.endpoint, debug=debug)

        # Create one token
        self.token = '2bae7fa7-5810-4664-8264-725fa3a714b1'
        self.bad_token = 'not-a-valid-token'

    def test_token_missing(self):
        try:
            ret = self.server.dataobjects(9999).get()
        except HttpClientError as e:
            if e.code != 401:
                self.fail('Return code != 401')
        except Exception as e:
            self.fail("Another exception %s" % e)

    def test_bad_token(self):
        try:
            ret = self.server.dataobjects(9999).get(token=self.bad_token)
        except HttpClientError as e:
            if e.code != 401:
                self.fail('Return code != 401')
        except Exception as e:
            self.fail("Another exception %s" % e)

    def test_upload(self):
        try:
            f = open(self.filename, 'r')
            object_data = {'name': "%s" % self.object_name,
                           'file': f}
            result = self.server.dataobjects.post(data=object_data, token=self.token)
            f.close()
            return result['resource_uri']
        except HttpClientError as e:
            self.fail('Return code == %d' % e.code)
        except Exception as e:
            self.fail("Another exception %s" % e)

    def _sha1(self, data):
        sha1 = hashlib.sha1()
        sha1.update(data)
        return sha1.hexdigest()

    # TODO: do a sha1 or md5 check
    def test_download(self):
        resource_uri = self.test_upload()
        oid = int(resource_uri.split('/')[-2:][0])

        f = open(self.filename, "r")
        original_sha1 = self._sha1(f.read())
        f.close()

        try:
            result = self.server.dataobjects(oid).get(token=self.token)
        except HttpClientError as e:
            self.fail('Return code == %d' % e.code)
        except Exception as e:
            self.fail("Another exception %s" % e)

        download_sha1 = self._sha1(result)

        if original_sha1 != download_sha1:
            self.fail("Sha1 different")

    def test_delete(self):
        resource_uri = self.test_upload()
        oid = int(resource_uri.split('/')[-2:][0])

        try:
            result = self.server.dataobjects(oid).delete(token=self.token)
        except HttpClientError as e:
            self.fail('Return code == %d' % e.code)
        except Exception as e:
            self.fail("Another exception %s" % e)
