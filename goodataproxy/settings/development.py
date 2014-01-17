# Django settings for goodataproxy project.
from defaults import *

DEBUG = True

STORAGE_BACKEND = "local"
STORAGE_BACKEND_LOCAL_DIR = "/tmp/data"

GOO_SERVER_TOKEN = ""
GOO_SERVER_URI = "http://localhost:8000/api/v1/"
