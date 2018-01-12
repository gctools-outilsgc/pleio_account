import uuid
import os
from urllib.parse import urlencode
from urllib.request import urlopen
from django.conf import settings

def unique_filepath(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars/', filename)

