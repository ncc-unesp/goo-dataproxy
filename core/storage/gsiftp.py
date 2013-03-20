from urlparse import urlparse
from goodataproxy import settings
from django.core.servers.basehttp import FileWrapper
import os
from subprocess import Popen, PIPE, call

GRIDFTP_COPY = "/usr/bin/globus-url-copy"
GRIDFTP_DELETE = "/usr/bin/edg-gridftp-rm"

class ObjectDownloadError(Exception):
    pass

class ObjectDeleteError(Exception):
    pass

def _is_local(url):
    return url.startswith(settings.STORAGE_BASE_URI)

def upload(file_obj, name):
    dst = urlparse(settings.STORAGE_BASE_URI).path
    input_file = open(file_obj, 'r')
    output = "%s/%s" % (dst, name)

    if not os.path.exists(dst):
        os.makedirs(dst) # pragma: no cover

    with open(output, 'wb+') as destination:
        while True:
            chunk = input_file.read(1024)
            if not chunk:
                break
            destination.write(chunk)

    return "%s/%s" % (settings.STORAGE_BASE_URI, name)

def download(url):
    if not _is_local(url):
        # get file remote file
        local_url = 'file://%s/' % urlparse(settings.STORAGE_BASE_URI).path
        ret_code = call([GRIDFTP_COPY, url, local_url], close_fds=True)

        if (ret_code != 0):
            raise ObjectDownloadError

        basename = url.split("/")[-1]
        url = "%s/%s" % (settings.STORAGE_BASE_URI, basename)

    filename = urlparse(url).path
    return open(filename, 'r')

def delete(url):
    if not _is_local(url):
        ret_code = call([GRIDFTP_DELETE, url], close_fds=True)
        if (ret_code != 0):
            raise ObjectDeleteError
    else:
        filename = urlparse(url).path
        os.unlink(filename)
