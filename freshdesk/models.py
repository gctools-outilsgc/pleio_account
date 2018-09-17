from django.db import models
from django.db.models import Q


# Create your models here.
class Configuration(models.Model):
    url = models.URLField(default='', null=False)
    secret_key = models.CharField(max_length=250, blank=True, default='')
    default = models.BooleanField(default=False)


    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        if(self.default == True):
            self.__class__.objects.filter(~Q(id=self.id)).update(default=False)
        super(Configuration, self).save(*args, **kwargs)