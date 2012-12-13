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
from core.storage.utils import Storage
from goodataproxy import settings
import os
import uuid
import slumber

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

    def _create_object(self, name, size, url, token):
        try:
            goo_server = settings.GOO_SERVER_URI
            api = slumber.API(goo_server)
            values = {}
            values['name'] = name
            values['size'] = size
            values['url'] = url
            response = api.objects.post(values, token=token)
        except Exception as e:
            return False

        return True

    def _is_token_valid(self, request):
        try:
            token = request.REQUEST['token']
        except:
            return False
        try:
            goo_server = settings.GOO_SERVER_URI
            api = slumber.API(goo_server)
            response = api.check_token.get(token=token)
        except Exception as e:
            return False

        return True

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

        filename = uuid.uuid4()
        wrapper = FileWrapper(file(filename))
        response = HttpResponse(wrapper, content_type='aplication/octet-stream')
        response['Content-Disposition'] = 'filename="somefilename.pdf"'
        response['Content-Length'] = os.path.getsize(filename)
        return response

    def upload(self, request=None, **kwargs):
        # Check if token is valid
        if not self._is_token_valid(request):
            return HttpResponse(status=401)

        # If form is valid save file on Storage Backend
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            name = request.POST['name']
            filename = "%s.zip" % uuid.uuid4()
            size = file.size
            url = "%s/%s" % (Storage.get_base_uri(), filename)
            token = request.REQUEST['token']
            Storage.upload(file, filename)
        else:
            return HttpResponse(status=400)

        # If object is stored create object metadata on goo-server
        if not self._create_object(name, size, url, token):
            return HttpResponse(status=400)

        return HttpResponse(status=201)

    def delete(self, request=None, **kwargs):
        pass
