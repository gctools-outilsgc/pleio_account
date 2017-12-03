import uuid
import os

def unique_filepath(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars/', filename)

def str2dict(astring):
    astring = astring.replace("', '", "',,'")
    astring = astring.replace(">, '", "'>,,'")
    astring = astring.replace("'", "")
    astring = astring.replace("{", "")
    astring = astring.replace("}", "")
    items = astring.split(',,')
    adict = {}
    for item in items:
        key,value = item.split(": ")
        adict[key] = value
 
    return(adict)

