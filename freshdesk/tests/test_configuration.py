from django.conf import settings
from django.test import TransactionTestCase
from freshdesk.models import Configuration

class test_freshdesk_config(TransactionTestCase):
    def setUp(self):
        self.config = Configuration(url="url1")
        self.config.secret_key = "123"
        self.config.save()
    def test_save(self):
        savedconfig = Configuration.objects.get(url="url1")
        print(savedconfig.url)
        #self.fail()