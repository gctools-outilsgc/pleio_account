from django.apps import AppConfig


class SamlConfig(AppConfig):
    name = 'saml'

    def ready(self):
        import saml.signals