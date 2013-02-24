from urlparse import urlparse
from goodataproxy import settings
import local, gsiftp

def _get_backend_method(method):
    scheme = urlparse(settings.STORAGE_BASE_URI).scheme
    try:
        module = globals()[scheme]
        return getattr(module, method)
    except AttributeError:
        raise NotImplementedError

def upload(file_obj, filename):
    f = _get_backend_method('upload')
    return f(file_obj, filename)

def download(url):
    f = _get_backend_method('download')
    return f(url)

def delete(url):
    f = _get_backend_method('delete')
    return f(url)
