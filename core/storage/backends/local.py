from core.storage.generic import GenericStorage
from urlparse import urlparse
from goodataproxy import settings
import os

class LocalStorage(GenericStorage):
    def upload(self, file, name):
        dst = urlparse(settings.STORAGE_BASE_URI).path
        output = "%s/%s" % (dst, name)
        with open(output, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def download(self, file):
        pass

    def delete(self, url):
        filename = url.replace("local://", "")
        try:
            os.unlink(filename)
        except:
            pass
