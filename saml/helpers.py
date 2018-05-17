import uuid
import os

def unique_idp_metadata_filepath(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    result = os.path.join('idp_metadata/', filename)
    return result