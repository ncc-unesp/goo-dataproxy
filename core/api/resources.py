# vim: tabstop=4 shiftwidth=4 softtabstop=4
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie import fields

from core.auth import TokenAuthentication
from core.models import DataObject

import zipfile, tempfile, os

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

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
