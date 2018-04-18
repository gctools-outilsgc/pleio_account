from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^one', views.requestmembership_step_one, name='request_one'),
    url(r'^two', views.requestmembership_step_two, name='request_two'),
    url(r'^complete', views.requestmembership_complete, name='request_complete'),
    url(r'^ajax/validate_email', views.validate_email, name="validate_email")
]
