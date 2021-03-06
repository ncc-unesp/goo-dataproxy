# This file is part of goo-dataproxy.
#
# Copyright (c) 2103-2014 by Nucleo de Computacao Cientifica, UNESP
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#    Gabriel von. Winckler <winckler AT ncc DOT unesp DOT br>
#
# goo-dataproxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# goo-dataproxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Deprecated

#from urlparse import urlparse
#from django.conf import settings
#from django.core.servers.basehttp import FileWrapper
#import os, tempfile
#from subprocess import Popen, PIPE, call

#GRIDFTP_COPY = "/usr/bin/globus-url-copy"
#GRIDFTP_DELETE = "/usr/bin/edg-gridftp-rm"

#class ObjectDownloadError(Exception):
#    pass

#class ObjectDeleteError(Exception):
#    pass

#def _is_local(url):
#    return url.startswith(settings.STORAGE_BASE_URI)

#def upload(file_obj, name):
#    dst = urlparse(settings.STORAGE_BASE_URI).path
#    input_file = open(file_obj, 'r')
#    output = "%s/%s" % (dst, name)

#    if not os.path.exists(dst):
#        os.makedirs(dst) # pragma: no cover

#    with open(output, 'wb+') as destination:
#        while True:
#            chunk = input_file.read(1024)
#            if not chunk:
#                break
#            destination.write(chunk)

#    return "%s/%s" % (settings.STORAGE_BASE_URI, name)

#def download(url):
#    if not _is_local(url):
#        # try to get a cache version
#        basename = url.split("/")[-1]
#        server_dir = urlparse(settings.STORAGE_BASE_URI).path
#        cache_dir = os.path.join(server_dir, 'cache')
#        filename = os.path.join(cache_dir, basename)

#        if not os.path.exists(filename):
#            # get file remote file
#            (tmp_fd, tmp_file) = tempfile.mkstemp(dir=cache_dir)
#            os.close(tmp_fd)

#            local_url = 'file://%s' % os.path.abspath(tmp_file)
#            ret_code = call([GRIDFTP_COPY, url, local_url], close_fds=True)

#            if (ret_code != 0):
#                raise ObjectDownloadError

#            os.rename(tmp_file, filename)

#    else:
#        filename = urlparse(url).path

#    return open(filename, 'r')

#def delete(url):
#    if not _is_local(url):
#        ret_code = call([GRIDFTP_DELETE, url], close_fds=True)
#        if (ret_code != 0):
#            raise ObjectDeleteError
#    else:
#        filename = urlparse(url).path
#        os.unlink(filename)
