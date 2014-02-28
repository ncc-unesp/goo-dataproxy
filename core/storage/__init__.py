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
