from sqlalchemy import Table, Column, Integer, BigInteger, String, Text, LargeBinary, MetaData

entities = Table('elgg_entities', MetaData(),
    Column('guid', BigInteger, primary_key=True),
    Column('type', String),
    Column('subtype', Integer),
    Column('owner_guid', BigInteger),
    Column('site_guid', BigInteger),
    Column('container_guid', BigInteger),
    Column('access_id', BigInteger),
    Column('time_created', BigInteger),
    Column('time_updated', BigInteger),
    Column('last_action', BigInteger),
    Column('enabled', String)
)

users_entity = Table('elgg_users_entity', MetaData(),
    Column('guid', BigInteger, primary_key=True),
    Column('name', String),
    Column('username', String),
    Column('password', String),
    Column('salt', String),
    Column('password_hash', String),
    Column('email', String),
    Column('language', String),
    Column('code', String),
    Column('banned', String),
    Column('admin', String),
    Column('last_action', BigInteger),
    Column('prev_last_action', BigInteger),
    Column('last_login', BigInteger),
    Column('prev_last_login', BigInteger)
)