from urlparse import urlparse
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
import os

def upload(file_obj, sha1):
    if not os.path.exists(settings.STORAGE_BACKEND_LOCAL_DIR):
        os.makedirs(settings.STORAGE_BACKEND_LOCAL_DIR) # pragma: no cover

    input_file = open(file_obj, 'r')
    output = os.path.join(settings.STORAGE_BACKEND_LOCAL_DIR,sha1)

    with open(output, 'wb+') as destination:
        while True:
            chunk = input_file.read(1024)
            if not chunk:
                break
            destination.write(chunk)

def download(sha1):
    filename = os.path.join(settings.STORAGE_BACKEND_LOCAL_DIR,sha1)
    return file(filename)

def delete(sha1):
    filename = os.path.join(settings.STORAGE_BACKEND_LOCAL_DIR,sha1)
    os.unlink(filename)
