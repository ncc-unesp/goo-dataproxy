from urlparse import urlparse
from goodataproxy import settings
from django.core.servers.basehttp import FileWrapper
import os

def upload(file_obj, name):
    dst = urlparse(settings.STORAGE_BASE_URI).path
    output = "%s/%s" % (dst, name)

    if not os.path.exists(dst):
        os.makedirs(dst) # pragma: no cover

    with open(output, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    return "%s/%s" % (settings.STORAGE_BASE_URI, name)

def download(url):
    filename = url.replace("local://", "")
    return file(filename)

def delete(url):
    filename = url.replace("local://", "")
    os.unlink(filename)
