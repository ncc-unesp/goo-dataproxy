# Django settings for goodataproxy project.
from defaults import *

DEBUG = True

# Local or GridFTP
STORAGE_BASE_URI = "local:///tmp/data"
#STORAGE_BASE_URI = "gridftp://se:80/gridftp/"

GOO_SERVER_URI = "http://localhost:8000/api/v1/"
