# vim: tabstop=4 shiftwidth=4 softtabstop=4
from django import forms
from django.http import HttpResponse
from django.conf.urls import url
from tastypie.resources import Resource
from tastypie.utils import trailing_slash
from tastypie import fields
from datetime import datetime
from core.storage.utils import Storage
from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError, HttpServerError
from goodataproxy import settings
from tastypie.exceptions import ImmediateHttpResponse
import os
import uuid


def translate_gooapi_to_tastypie_exception(f):
    def _f(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HttpClientError as e:
            raise ImmediateHttpResponse(HttpResponse(status=e.code))
        except HttpServerError as e:
            raise ImmediateHttpResponse(HttpResponse(status=500))
    return _f

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
                self.wrap_view('detail'),
                name="api_detail"),
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name,
                                                trailing_slash()),
                self.wrap_view('upload'),
                name="api_upload"),
            ]

    def detail(self, request=None, **kwargs):
        """
        Called when accessing GET,DELETE /dataproxy/objects/{id}/
        """

        method = request.method

        try:
            token = request.REQUEST['token']
            object_id = kwargs['pk']
        except KeyError as e:
            return HttpResponse(status=401)

        # Check if token is valid
        if self._is_token_valid(token):
            if method == 'GET':
                return self._download(object_id, token)
            elif method == 'DELETE':
                return self._delete(object_id, token)
            else:
                return HttpResponse(status=501)
        else:
            return HttpResponse(status=401)

    def upload(self, request=None, **kwargs):
        """
        Called when accessing POST /dataproxy/objects/
        """
        try:
            token = request.REQUEST['token']
        except KeyError as e:
            return HttpResponse(status=401)

        # Check if token is valid
        if not self._is_token_valid(token):
            return HttpResponse(status=401)

        # If form is valid save file on Storage Backend
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            name = request.POST['name']
            filename = "%s.zip" % uuid.uuid4()
            size = file.size / 1024 / 1024 # MB
            url = "%s/%s" % (Storage.get_base_uri(), filename)
            token = request.REQUEST['token']
            Storage.upload(file, filename)
        else:
            return HttpResponse(status=400)

        # If object is stored create object metadata on goo-server
        if not self._create_object(name, size, url, token):
            return HttpResponse(status=400)

        return HttpResponse(status=201)

    @translate_gooapi_to_tastypie_exception
    def _create_object(self, name, size, url, token):
        goo_server = settings.GOO_SERVER_URI
        server = API(goo_server, debug=True)
        values = {}
        values['name'] = name
        values['size'] = size
        values['url'] = url
        response = server.objects.post(values, token=token)

        return True

    @translate_gooapi_to_tastypie_exception
    def _get_object_url(self, id, token):
        goo_server = settings.GOO_SERVER_URI
        server = API(goo_server, debug=True)
        obj = server.objects(id).get(token=token)

        return obj['url']

    @translate_gooapi_to_tastypie_exception
    def _is_token_valid(self, token):
        goo_server = settings.GOO_SERVER_URI
        server = API(goo_server, debug=False)
        response = server.token.get(token=token)
        if response['expire_time']:
            return True
        else:
            return False


    @translate_gooapi_to_tastypie_exception
    def _download(self, object_id, token):
        object_url = self._get_object_url(object_id, token)
        response = Storage.download(url=object_url)
        return response

    @translate_gooapi_to_tastypie_exception
    def _delete_object(self, id, token):
        """
        Delete a meta data object from database.
        """
        goo_server = settings.GOO_SERVER_URI
        server = API(goo_server, debug=True)
        server.objects(id).delete(token=token)

    @translate_gooapi_to_tastypie_exception
    def _delete(self, object_id, token):
        """
        Get a object url and delete object metadata from database and
        delete object from Storage.
        """
        object_url = self._get_object_url(object_id, token)
        Storage.delete(url=object_url)
        self._delete_object(object_id, token)
        return HttpResponse(status=204)
