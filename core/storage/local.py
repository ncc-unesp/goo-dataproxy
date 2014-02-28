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
