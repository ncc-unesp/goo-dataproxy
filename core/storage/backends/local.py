from core.storage.generic import GenericStorage
from django.http import HttpResponse
from urlparse import urlparse
from goodataproxy import settings
from django.core.servers.basehttp import FileWrapper
import os

class LocalStorage(GenericStorage):
    def upload(self, file, name):
        dst = urlparse(settings.STORAGE_BASE_URI).path
        output = "%s/%s" % (dst, name)
        with open(output, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def download(self, url):
        filename = url.replace("local://", "")
        wrapper = FileWrapper(file(filename))
        response = HttpResponse(wrapper, content_type='aplication/octet-stream')
        response['Content-Disposition'] = 'filename="somefilename.pdf"'
        response['Content-Length'] = os.path.getsize(filename)
        return response

    def delete(self, url):
        filename = url.replace("local://", "")
        try:
            os.unlink(filename)
        except:
            pass
