import os
import logging
from urllib.request import urlopen
from lxml import etree
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib import admin
from django.conf import settings
from django.core import signing
from core.models import User
from .helpers import unique_idp_metadata_filepath

# Get an instance of a logger
logger = logging.getLogger(__name__)

class IdentityProvider(models.Model):
    shortname = models.SlugField(unique=True)
    displayname = models.CharField(max_length=100, null=False)
    metadata_url = models.URLField(max_length=256, blank=True)
    metadata_filename = models.FileField(upload_to=unique_idp_metadata_filepath, blank=True)
    entityId = models.URLField(max_length=256, null=False)
    perform_slo = models.BooleanField(default=True)
    ssoId = models.URLField(max_length=256, blank=True)
    sloId = models.URLField(max_length=256, blank=True)
    signing_x509cert1 = models.TextField(blank=True)
    signing_x509cert2 = models.TextField(blank=True)
    encryption_x509cert1 = models.TextField(blank=True)
    encryption_x509cert2 = models.TextField(blank=True)
    last_modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.shortname

    def save(self, *args, **kwargs):
        self.shortname = slugify(self.shortname)

        super(IdentityProvider, self).save(*args, **kwargs)

    def get_saml_configuration(self):
        return {
            "entityId": self.entityId,
            "singleSignOnService": {
                "url": self.ssoId,
                "binding": settings.SAML_IDP_BINDING
            },
            "singleLogoutService": {
                "url": self.sloId,
                "binding": settings.SAML_IDP_BINDING
            },
            "x509certMulti": {
	            "signing": [self.signing_x509cert1, self.signing_x509cert2], 
	            "encryption": [self.encryption_x509cert1, self.encryption_x509cert2], 
            }     
        }

    def get_idp_metadata(self):
        #print(settings.MEDIA_ROOT + self.metadata_filename.__str__())
        try:
            idp_metadata = etree.fromstring(urlopen(self.metadata_url).read())
        except:
            try:
                f = open(os.path.join(settings.MEDIA_ROOT, self.metadata_filename.__str__()))
                xml = f.read()
                f.close()
                idp_metadata = etree.fromstring(xml)
            except:
                logger.info("saml.models.get_idp_metadata,  no metadata provided")
                return False

        namespace = settings.SAML_IDP_NAMESPACE

        entity = idp_metadata.findall(".")
        self.entityId = entity[0].attrib.get('entityID', None)

        sso = idp_metadata.findall("./md:IDPSSODescriptor/md:SingleSignOnService[@Binding='"+settings.SAML_IDP_BINDING+"']", namespace)
        try:
            self.ssoId = sso[0].attrib.get('Location', "")
        except IndexError:
            logger.warning("saml.models.get_idp_metadata,  no SingleSignOnService in metadata found")
            self.ssoId = ""

        slo = idp_metadata.findall("./md:IDPSSODescriptor/md:SingleLogoutService[@Binding='"+settings.SAML_IDP_BINDING+"']", namespace)
        try:
            self.sloId = slo[0].attrib.get('Location', "")
        except IndexError:
            logger.warning("saml.models.get_idp_metadata,  no SingleLogoutService in metadata found")
            self.sloId = ""

        x509certs = []
        signing_x509certs = idp_metadata.findall("./md:IDPSSODescriptor/md:KeyDescriptor[@use='signing']/ds:KeyInfo/ds:X509Data", namespace)
            
        for x509cert in signing_x509certs:
            x509certs.append(x509cert.findtext("ds:X509Certificate", namespaces=namespace))
        
        try:
            self.signing_x509cert1 = x509certs[0]
            try:
                self.signing_x509cert2 = x509cert[1]
            except IndexError: 
                pass
        except IndexError:
            logger.warning("saml.models.get_idp_metadata,  no signing X509Certificate in metadata found")

        x509certs = []
        encryption_x509certs = idp_metadata.findall("./md:IDPSSODescriptor/md:KeyDescriptor[@use='encryption']/ds:KeyInfo/ds:X509Data", namespace)
            
        for x509cert in encryption_x509certs:
            x509certs.append(x509cert.findtext("ds:X509Certificate", namespaces=namespace))
        
        try:
            self.encryption_x509cert1 = x509certs[0]
            try:
                self.encryption_x509cert2 = x509cert[1]
            except IndexError: 
                pass
        except IndexError:
            pass    
    
        self.last_modified = timezone.now()

        #update_fields are provided to prevent this function being called again by the post_save signal
        self.save(update_fields=[
                'entityId',
                'ssoId',
                'sloId',
                'signing_x509cert1',
                'signing_x509cert2',
                'encryption_x509cert1',
                'encryption_x509cert2',
                'last_modified'
                ])
                
        return True

class IdpEmailDomain(models.Model):
    email_domain = models.CharField(max_length=100, db_index=True, unique=True)
    identityprovider = models.ForeignKey('IdentityProvider', db_column="IdentityProvider.shortname", on_delete=models.CASCADE, db_index=True)
     
    def __str__(self):
        return self.email_domain
           

class ExternalId(models.Model):
    identityproviderid = models.ForeignKey('IdentityProvider', on_delete=models.CASCADE, db_index=True)
    externalid = models.CharField(max_length=100, db_index=True, unique=True)
    userid = models.ForeignKey('core.User', on_delete=models.CASCADE, db_index=True)
