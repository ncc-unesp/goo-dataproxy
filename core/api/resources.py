# vim: tabstop=4 shiftwidth=4 softtabstop=4
from django import forms
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.conf.urls import url
from tastypie.resources import Resource
from tastypie.exceptions import NotFound, BadRequest
from tastypie.utils import trailing_slash
from tastypie import fields
from datetime import datetime
import os
from core.storage.utils import Storage

class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    file = forms.FileField(required=True)


class ObjectResource(Resource):
    """This resource handler auth requests.

    Allowed Methods:
    ----------------

        POST   /dataproxy/objects/       # Upload a new object
        GET    /dataproxy/objects/{id}/  # Download an object
        DELETE /dataproxy/objects/{id}/  # Delete an object
    """
    class Meta:
        resource_name = 'dataproxy/objects'
        list_allowed_methods = ['post']
        detail_allowd_methods = ['get', 'delete']

        # return object on POST request
        always_return_data = True

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)%s$" % (self._meta.resource_name,
                                                                  trailing_slash()),
                self.wrap_view('download'),
                name="api_download"),
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name,
                                                trailing_slash()),
                self.wrap_view('upload'),
                name="api_upload"),
            ]

    def handle_uploaded_file(self, f):
        with open('/tmp/bla.zip', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def download(self, request=None, **kwargs):
        """Send a file through TastyPie without loading the whole file into
        memory at once. The FileWrapper will turn the file object into an
        iterator for chunks of 8KB.

        No need to build a bundle here only to return a file.
        """
        try:
            token = request.REQUEST['token']
            object_id = kwargs['pk']
        except Exception as e:
            return HttpResponse(status=401)

        filename = '/tmp/teste.zip'
        wrapper = FileWrapper(file(filename))
        response = HttpResponse(wrapper, content_type='aplication/octet-stream')
        response['Content-Disposition'] = 'filename="somefilename.pdf"'
        response['Content-Length'] = os.path.getsize(filename)
        return response

    def upload(self, request=None, **kwargs):
        try:
            token = request.REQUEST['token']
        except Exception as e:
            return HttpResponse(status=401)

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']
            name = file.name
            Storage.upload(file, name)
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


    def delete(self, request=None, **kwargs):
        pass
