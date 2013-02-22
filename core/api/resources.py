# vim: tabstop=4 shiftwidth=4 softtabstop=4
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields
from core.storage.utils import Storage
from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError
from goodataproxy import settings
import uuid

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

class DataObject(object):
    def __init__(self, token=None):
        goo_server = settings.GOO_SERVER_URI
        self.token = token
        self.server = API(goo_server)

    def load(self, oid):
        obj = self.server.objects(oid).get(token=self.token)

        self.url = obj['url']
        self.name = obj['name']
        self.size = obj['size']
        self.oid = oid

        return self

    def file(self):
        """ Must call load(oid) load before """
        return Storage.download(url=self.url)

    def save(self, name, req_file):
        self.name = name

        # internal storage name
        filename = "%s" % uuid.uuid4()
        self.size = req_file.size
        self.url = "%s/%s" % (Storage.get_base_uri(), filename)
        Storage.upload(req_file, filename)

        values = {"name": self.name,
                  "size": self.size,
                  "url": self.url}
        response = self.server.objects.post(values, token=self.token)

        self.oid = response["id"]
        self.resource_uri = response["resource_uri"]

    def delete(self):
        """ Must call load(oid) load before """
        # content data deletion
        Storage.delete(url=self.url)
        # metadata deletion
        self.server.objects(self.oid).delete(token=self.token)

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
        except HttpClientError as e:
            if e.code == 401:
                return False
            else:
                raise e # pragma: no cover

        if response['expire_time']:
            request.token = token
            return True
        else:
            return False # pragma: no cover

        return False # pragma: no cover

class ObjectResource(Resource):
    """This resource handler auth requests.

    Allowed Methods:
    ----------------

        POST   /dataproxy/objects/       # Upload a new object
        GET    /dataproxy/objects/{id}/  # Download an object
        DELETE /dataproxy/objects/{id}/  # Delete an object
    """

    name = fields.CharField(attribute='name')
    data = fields.FileField(attribute='file')

    class Meta:
        resource_name = 'dataproxy/objects'
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
        req_file = bundle.data['file']
        name = bundle.data['name']

        bundle.obj = DataObject(bundle.request.token)
        bundle.obj.save(name, req_file)

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
            data.update(request.FILES)
            return data
        return super(ObjectResource,
                     self).deserialize(request,
                                       data,
                                       format) #pragma: no cover

    def dehydrate(self, bundle):
        # only return resource_uri
        bundle.data = {"resource_uri": bundle.obj.resource_uri}
        return bundle
