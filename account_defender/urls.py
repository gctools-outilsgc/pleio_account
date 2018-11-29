"""accountlockout URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import block_view, unblock_ip_view, unblock_username_view

urlpatterns = [
    url(r'^blocks/$', block_view,
        name="defender_blocks_view"),
    url(r'^blocks/ip/(?P<ip_address>[A-Za-z0-9-._]+)/unblock$', unblock_ip_view,
        name="defender_unblock_ip_view"),
    url(r'^blocks/username/(?P<username>[\w]+[^\/]*)/unblock$',
        unblock_username_view,
        name="defender_unblock_username_view"),
]