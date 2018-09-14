from django.db import models


# Create your models here.
class Configuration(models.Model):
    url = models.URLField(default='', null=False, )
    secret_key = models.CharField(max_length=250)


    def __str__(self):
        return self.url
