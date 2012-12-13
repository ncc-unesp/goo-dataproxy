from urlparse import urlparse
from goodataproxy import settings
from core.storage.backends import local
import inspect

class Storage():
    @staticmethod
    def get_base_uri():
        return "local:///tmp/data"

    @staticmethod
    def get_scheme():
        backend_url = settings.STORAGE_BASE_URI
        return urlparse(backend_url).scheme

    @staticmethod
    def upload(file, filename):
        for name, obj in inspect.getmembers(eval(Storage.get_scheme())):
            if inspect.isclass(obj):
                StorageClass = obj

        StorageClass().upload(file, filename)

    @staticmethod
    def download(id):
        pass

    @staticmethod
    def delete(id):
        pass
