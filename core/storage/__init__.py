from urlparse import urlparse
from django.conf import settings
import local

def _get_backend_method(method):
    try:
        module = globals()[settings.STORAGE_BACKEND]
        return getattr(module, method)
    except AttributeError:
        raise NotImplementedError

def upload(file_obj, sha1):
    f = _get_backend_method('upload')
    return f(file_obj, sha1)

def download(sha1):
    f = _get_backend_method('download')
    return f(sha1)

def delete(sha1):
    f = _get_backend_method('delete')
    return f(sha1)
