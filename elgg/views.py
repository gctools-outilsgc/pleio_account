from django.shortcuts import render
from django.conf import settings
import os
from time import strftime
import urllib.request
from sqlalchemy import Table, Column, Integer, BigInteger, String, Text, LargeBinary, MetaData
from sqlalchemy import create_engine, select, and_, or_
from .elgg_models import entities, users_entity
from core.models import User, ResizedAvatars
from core.helpers import unique_avatar_filepath, unique_avatar_large_filename, unique_avatar_medium_filename
from core.helpers import unique_avatar_small_filename, unique_avatar_tiny_filename, unique_avatar_topbar_filename

import datetime
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

def migrate(verbosity=1):
    engine = create_engine(settings.ELGG_DB_URL, pool_recycle=3600)
    connection = engine.connect()

    join = users_entity.join(entities, users_entity.c.guid == entities.c.guid)
    #query = select([join])
    query = select(
        [users_entity.c.guid
        ,users_entity.c.password_hash
        ,users_entity.c.last_login
        ,users_entity.c.username
        ,users_entity.c.name
        ,users_entity.c.email
        ,users_entity.c.admin
        ,users_entity.c.banned
        ,entities.c.time_created
        ]).select_from(join)


    migrated = 0
    not_migrated = 0

    for row in connection.execute(query):
        row = dict(row)
        timedelta = datetime.timedelta()
        timezone = datetime.timezone(timedelta)

        id = row.get('guid')
        username = row.get('username')
        name = row.get('name')
        email = row.get('email')
        password = 'bcrypt$' + row.get('password_hash')
        is_active = True
        accepted_terms = True
        is_admin = (row.get('admin') == 'yes')
        is_banned = (row.get('banned') == 'yes')
        last_login = datetime.datetime.fromtimestamp(row.get('last_login'), timezone)
        time_created = datetime.datetime.fromtimestamp(row.get('time_created'), timezone)
        
        avatar_master_url = settings.LEGACY_AVATAR_URL + '?joindate=' + str(row.get('time_created')) + '&guid=' + str(id) + '&size=master'
        avatar_rel_path = os.path.join('avatars/', strftime('%Y/%m/%d'), str(id))
        avatar_master  = os.path.join(avatar_rel_path, 'master.jpg')
        avatar_dest = os.path.join(settings.MEDIA_ROOT, avatar_master)

        try:
            # does the user have an avatar?
            tmpfile, headers = urllib.request.urlretrieve(avatar_master_url)
            content_type = headers.get('Content-Type')
            content_length = headers.get('Content-Length')
            if content_length == '43' and content_type == 'image/gif':
                # user has a dummy avatar, no further action regarding avatars requiered
                avatar_master = None                
        except Exception as e:
            if verbosity >= 1:
                logger.error = ('Error: %s' % e)
            avatar_master = None                

        try:
            user = User.objects.create(
                id = id,
                username = username,
                name = name,
                email = email,
                password = password,
                is_active = is_active,
                accepted_terms = accepted_terms,
                is_admin = is_admin,
                is_banned = is_banned,
                last_login = last_login,
                time_created = time_created,
            )

            if avatar_master:                
                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, avatar_rel_path)):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, avatar_rel_path))
                try:
                    urllib.request.urlretrieve(avatar_master_url, avatar_dest)
                    user.avatar = avatar_master
                    user.save()
                except Exception as e:
                    if verbosity >= 1:
                        logger.error = ('Error: %s' % e)
                try:
                    resized_avatars = ResizedAvatars.objects.get(user=user)
                except ResizedAvatars.DoesNotExist:
                    resized_avatars = ResizedAvatars.objects.create(user=user)

                resized_avatars.large = copy_avatars(id, row.get('time_created'), 'large', verbosity)
                resized_avatars.medium = copy_avatars(id, row.get('time_created'), 'medium', verbosity)
                resized_avatars.small = copy_avatars(id, row.get('time_created'), 'small', verbosity)
                resized_avatars.tiny = copy_avatars(id, row.get('time_created'), 'tiny', verbosity)
                resized_avatars.topbar = copy_avatars(id, row.get('time_created'), 'topbar', verbosity)

                resized_avatars.save()
                 
            migrated = migrated + 1
    
        except Exception as e:
            not_migrated = not_migrated + 1
            field = str(e).split('core_user.')[-1]
            if field == 'id':
                if verbosity >= 2:
                    errormsg = 'Error: %s' % e, 'id: %s' % id
                else:
                    errormsg = None
            elif field == 'email':
                if verbosity >= 1:
                    errormsg = 'Error: %s' % e, 'email: %s' % email
                else:
                    errormsg = None
            elif field == 'username':
                if verbosity >= 1:
                    errormsg = 'Error: %s' % e, 'username: %s' % username
                else:
                    errormsg = None
            else:
                if verbosity >= 1:
                    errormsg = 'Error: %s' % e
                else:
                    errormsg = None
        
            if errormsg:
                logger.error(errormsg[0] + ', ' + errormsg[1]) 

    logger.warning('Number of migrated accounts: %d, errors: %d, total: %d' % (migrated, not_migrated, migrated + not_migrated))

def copy_avatars(id, time_created, size, verbosity):
        avatar_url = settings.LEGACY_AVATAR_URL + '?joindate=' + str(time_created) + '&guid=' + str(id) + '&size=' + size
        avatar_rel_path = os.path.join('avatars/', strftime('%Y/%m/%d'), str(id))
        avatar  = os.path.join(avatar_rel_path, str(size + '.jpg'))
        avatar_dest = os.path.join(settings.MEDIA_ROOT, avatar)
        try:
            urllib.request.urlretrieve(avatar_url, avatar_dest)
            return avatar
        except Exception as e:
            if verbosity >= 1:
                logger.error = ('Error: %s' % e)

            return None
    