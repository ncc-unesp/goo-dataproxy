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

        if not os.path.exists(dst):
            os.makedirs(dst) # pragma: no cover

        with open(output, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def download(self, url):
        filename = url.replace("local://", "")
        return file(filename)

    def delete(self, url):
        filename = url.replace("local://", "")
        os.unlink(filename)
