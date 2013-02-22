from core.storage.generic import GenericStorage
from django.http import HttpResponse
from urlparse import urlparse
from goodataproxy import settings
from django.core.servers.basehttp import FileWrapper
import os
from subprocess import Popen, PIPE, call

GRIDFTP_COPY = "/usr/bin/globus-url-copy"
GRIDFTP_DELETE = "/usr/bin/edg-gridftp-rm"

class ObjectDownloadError(Exception):
    pass

class LocalStorage(GenericStorage):
    def upload(self, file, name):
        dst = urlparse(settings.STORAGE_BASE_URI).path
        output = "%s/%s" % (dst, name)

        if not os.path.exists(dst):
            os.makedirs(dst) # pragma: no cover

        with open(output, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    def _is_local(self, url):
        return url.startswith(settings.STORAGE_BASE_URI)

    def download(self, url):
        if not _is_local(url):
            # get file remote file
            local_url = settings.STORAGE_BASE_URI.replace('gsiftp','file')
            ret_code = call([GRIDFTP_COPY, url, local_url], close_fds=True)

            if (ret_code != 0):
                raise ObjectDownloadError

            basename = url.split("/")[-1]
            url = "%s/%s" % (settings.STORAGE_BASE_URI, basename)

        filename = urlparse(url).path
        return file(filename)

    def delete(self, url):
        if not _is_local(url):
            ret_code = call([GRIDFTP_DELETE, url], close_fds=True)
        else:
            filename = urlparse(url).path
            os.unlink(filename)
