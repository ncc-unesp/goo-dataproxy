from core.storage.generic import GenericStorage
from urlparse import urlparse
from goodataproxy import settings

class LocalStorage(GenericStorage):
    def upload(self, file, name):
        dst = urlparse(settings.STORAGE_BASE_URI).path
        output = "%s/%s" % (dst, name)
        with open(output, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def download(self, file):
        pass

    def delete(self, file):
        pass
