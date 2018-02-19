import requests
import json
from .models import User
from django.conf import settings

class ElggBackend:

    def authenticate(self, request, username=None, password=None):
        if settings.ELGG_URL is None
            return None
            
        elgg_url = settings.ELGG_URL

        # Verify user exists in Elgg database
        valid_user_request = requests.post(elgg_url + "/services/api/rest/json/", data={'method': 'pleio.userexists', 'user': username})
        valid_user_json = json.loads(valid_user_request.text)
        valid_user = valid_user_json["result"] if 'result' in valid_user_json else False

        # Verify username/password combination
        valid_pass_request = requests.post(elgg_url + "/services/api/rest/json/", data={'method': 'pleio.verifyuser', 'user': username, 'password': password})
        valid_pass_json = json.loads(valid_pass_request.text)
        valid_pass_result = valid_pass_json["result"] if 'result' in valid_pass_json else False
        valid_pass = valid_pass_result["valid"] if 'valid' in valid_pass_result else False
        name = valid_pass_result["name"] if 'name' in valid_pass_result else username
        admin = valid_pass_result["admin"] if 'admin' in valid_pass_result else False

        # If valid, create new user with Elgg attributes
        if valid_user is True and valid_pass is True:
            user = User.objects.create_user(
                name=name,
                email=username,
                password=password,
                accepted_terms=True,
                receives_newsletter=False
            )
            user.is_active = True
            user.is_admin = admin
            user.save()
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
