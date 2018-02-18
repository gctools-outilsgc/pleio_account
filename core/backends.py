import requests
import json
from .models import User

class ElggBackend:

    def authenticate(self, request, username=None, password=None):
        valid_user_request = requests.post("https://dev.gccollab.ca/services/api/rest/json/", data={'method': 'pleio.userexists', 'user': username})
        valid_user_json = json.loads(valid_user_request.text)
        valid_user = valid_user_json["result"]

        valid_pass_request = requests.post("https://dev.gccollab.ca/services/api/rest/json/", data={'method': 'pleio.verifyuser', 'user': username, 'password': password})
        valid_pass_json = json.loads(valid_pass_request.text)
        valid_pass = valid_pass_json["result"]["valid"]
        name = valid_pass_json["result"]["name"]

        if valid_user is True and valid_pass is True:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    name=name,
                    email=username,
                    password=password,
                    accepted_terms=True,
                    receives_newsletter=False
                )
                user.is_active = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
