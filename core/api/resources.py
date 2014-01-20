# vim: tabstop=4 shiftwidth=4 softtabstop=4
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields
from core import storage
from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError
from django.conf import settings
import uuid, zipfile, tempfile, os, hashlib

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

class DataObject(object):
    def __init__(self, token=None):
        goo_server = settings.GOO_SERVER_URI
        self.token = settings.GOO_SERVER_TOKEN
        self.user_token = token
        self.server = API(goo_server)

    def load(self, oid):
        obj = self.server.dataobjects(oid).get(token=self.token,
                                           user_token=self.user_token)

        self.sha1 = obj['sha1']
        self.data_proxy_servers = obj['data_proxy_servers']
        self.name = obj['name']
        self.size = obj['size']
        self.oid = oid

        return self

    def file(self):
        """ Must call load(oid) load before """
        return storage.download(self.sha1)

    def save(self, name, req_file):
        self.name = name

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
                  "sha1": self.sha1}

        response = self.server.dataobjects.post(values,
                                            token=self.token,
                                            user_token=self.user_token)

        self.oid = response["id"]
        self.resource_uri = response["resource_uri"]

    def delete(self):
        """ Must call load(oid) load before """
        # content data deletion
        storage.delete(self.sha1)
        # metadata deletion
        self.server.dataobjects(self.oid).delete(token=self.token,
                                             user_token=self.user_token)

class TokenAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        # check if token exists inside the request
        try:
            token = request.GET['token']
        except KeyError:
            return False

        goo_server = settings.GOO_SERVER_URI
        server = API(goo_server, debug=False)
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

class DataObjectResource(Resource):
    """This resource handler auth requests.

    Allowed Methods:
    ----------------

        POST   /dataproxy/dataobjects/       # Upload a new object
        GET    /dataproxy/dataobjects/{id}/  # Download an object
        DELETE /dataproxy/dataobjects/{id}/  # Delete an object
    """

    name = fields.CharField(attribute='name')
    data = fields.FileField(attribute='file')

    class Meta:
        resource_name = 'dataproxy/dataobjects'
        object_class = DataObject
        
        list_allowed_methods = ['post']
        detail_allowd_methods = ['get', 'delete']

        authentication = TokenAuthentication()
        authorization = Authorization()

        # return object on POST request
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.oid
        else:
            kwargs['pk'] = bundle_or_obj.oid # pragma: no cover

        return kwargs


    def obj_get(self, request=None, **kwargs):
        obj = DataObject(request.token)
        obj.load(kwargs['pk'])
        return obj

    def get_detail(self, request, **kwargs):
        obj = self.obj_get(request=request, **kwargs)
        response = HttpResponse(FileWrapper(obj.file()),
                                content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % obj.name
        response['Content-Length'] = obj.size

        return response

    def obj_create(self, bundle, **kwargs):
        # check to see if is a single file (zip)
        # or multiples (must set compress=1)
        compress = bundle.data.has_key('compress')
        if compress:
            #do compress
            fd, filepath = tempfile.mkstemp('.zip')
            os.close(fd)
            zf = zipfile.ZipFile(filepath, mode='a')

            for f in bundle.data['files'].values():
                #save on disk
                tmp_fd, tmp_fp = tempfile.mkstemp()
                for chunk in f.chunks():
                    os.write(tmp_fd, chunk)
                os.close(tmp_fd)

                #add to zip
                zf.write(tmp_fp, f.name)
                #delete
                os.unlink(tmp_fp)

            zf.close()

        else:
            # Old version: requires file as "file"
            #req_file = bundle.data['files']['file']
            # New version: get a single file
            req_file = bundle.data['files'].values()[0]

            fd, filepath = tempfile.mkstemp()
            os.close(fd)
            with open(filepath, 'wb+') as destination:
                for chunk in req_file.chunks():
                    destination.write(chunk)

        name = bundle.data['name']

        bundle.obj = DataObject(bundle.request.token)
        bundle.obj.save(name, filepath)

        # Force tempfile to be removed
        os.unlink(filepath)
        return bundle

    def obj_delete(self, request=None, **kwargs):
        obj = self.obj_get(request=request, **kwargs)
        obj.delete()

    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE',
                                      'application/json')#pragma: no cover
        if format == 'application/x-www-form-urlencoded':
            return request.POST #pragma: no cover
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.GET.copy())
            data['files'] = request.FILES
            return data
        return super(DataObjectResource,
                     self).deserialize(request,
                                       data,
                                       format) #pragma: no cover

    def dehydrate(self, bundle):
        # only return resource_uri
        bundle.data = {"resource_uri": bundle.obj.resource_uri}
        return bundle
