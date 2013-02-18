from unittest import TestCase

# TODO: Rename gooclient to gooclientlib
from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError

import json

class ObjectResourceTest(TestCase):
    def setUp(self):
        super(ObjectResourceTest, self).setUp()

        self.endpoint = 'http://localhost:8001/api/v1/dataproxy/'
        self.format = 'json'

        self.filename = '/bin/true'
        self.object_name = 'true'

        self.server = API(self.endpoint, debug=False)

        # Create one token
        self.token = '782dd0a8-02f6-4169-baf7-b30c58dd7b25'
        self.bad_token = 'not-a-valid-token'

    def test_token_missing(self):
        try:
            ret = self.server.objects(9999).get()
        except HttpClientError as e:
            if e.code != 401:
                self.fail('Return code != 401')
        except Exception as e:
            self.fail("Another exception %s" % e)

    def test_bad_token(self):
        try:
            ret = self.server.objects(9999).get(token=self.bad_token)
        except HttpClientError as e:
            if e.code != 401:
                self.fail('Return code != 401')
        except Exception as e:
            self.fail("Another exception %s" % e)

    # TODO: return object id after upload
    def test_upload(self):
        try:
            f = open(self.filename, 'r')
            object_data = {'name': "%s" % self.object_name,
                           'file': f}

            result = self.server.objects.post(data=object_data, token=self.token)
            f.close()
        except HttpClientError as e:
            self.fail('Return code == %d' % e.code)
        except Exception as e:
            self.fail("Another exception %s" % e)

    # TODO: do a sha1 or md5 check
    def test_download(self):
        self.test_upload()

        try:
            result = self.server.objects(1).get(token=self.token)
        except HttpClientError as e:
            self.fail('Return code == %d' % e.code)
        except Exception as e:
            self.fail("Another exception %s" % e)





#    def test_download(self):
#
#    def test_delete(self):
#        self.job.status='P'
#        self.job.save()
#
#        data = {"time_left": 60}
#        token = self.pilot.token
#        url = "%s?token=%s" % (self.endpoint, token)
#        request = self.client.post(url, self.format, data=data)
#        self.assertHttpCreated(request)
#
#    def test_pilot_get_job(self):
#        self.job.status='R'
#        self.job.pilot = self.pilot
#        self.job.save()
#
#        token = self.pilot.token
#        url = "%s%d/?token=%s" % (self.endpoint, self.job.id, token)
#        request = self.client.get(url, self.format)
#        self.assertValidJSONResponse(request)
#
#    def test_wrong_token(self):
#        url = "%s%d/?token=%s" % (self.endpoint, self.job.id, "not-a-valid-token")
#        request = self.client.get(url, self.format)
#        self.assertHttpUnauthorized(request)
#
#    def test_no_token(self):
#        url = "%s%d/" % (self.endpoint, self.job.id)
#        request = self.client.get(url, self.format)
#        self.assertHttpUnauthorized(request)
#
#    def test_pilot_patch_job(self):
#        self.job.status='R'
#        self.job.pilot = self.pilot
#        self.job.save()
#
#        data = {"progress": 50}
#        token = self.pilot.token
#        url = "%s%d/?token=%s" % (self.endpoint, self.job.id, token)
#        request = self.client.patch(url, self.format, data=data)
#        self.assertHttpAccepted(request)
