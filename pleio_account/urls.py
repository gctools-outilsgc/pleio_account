from django.conf import settings
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.views.decorators.clickjacking import xframe_options_exempt
from django.urls import path, URLPattern, URLResolver
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.views.generic import RedirectView
from oauth2_provider import views as oauth2_views
from two_factor.urls import urlpatterns as tf_urls

from api import views as api_views
from core import views, forms
from core.class_views import (
    PleioLoginView,
    PleioSessionDeleteView,
    PleioSessionDeleteOtherView
)
from axes.decorators import axes_dispatch

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers
router = routers.SimpleRouter()

router.register('users/all', api_views.all_users, 'all_users')

class DecoratedURLPattern(URLPattern):
    def resolve(self, *args, **kwargs):
        result = super(DecoratedURLPattern, self).resolve(*args, **kwargs)
        if result:
            result.func = self._decorate_with(result.func)
        return result


class DecoratedRegexURLResolver(URLResolver):
    def resolve(self, *args, **kwargs):
        result = super(DecoratedRegexURLResolver, self) \
            .resolve(*args, **kwargs)
        if result:
            result.func = self._decorate_with(result.func)
        return result


def decorated_includes(func, includes):
    """
    Include URLconf from module but apply the specified decorator to each.
    """
    urlconf_module, app_name, namespace = includes
    urlconf_urls = urlconf_module.urlpatterns

    for item in urlconf_urls:
        if isinstance(item, URLPattern):
            item.__class__ = DecoratedURLPattern
            item._decorate_with = func
        elif isinstance(item, URLResolver):
            item.__class__ = DecoratedRegexURLResolver
            item._decorate_with = func

    return urlconf_module, app_name, namespace


urlpatterns = [
    path('register-sinscrire/', views.register, name='register'),
    path(
        'register-sinscrire/complete/',
        views.register_complete,
        name='register_complete'
    ),
    path(
        'register-sinscrire/activate/<activation_token>/',
        views.register_activate,
        name='register_activate'
    ),
    path('termsofuse/', views.terms_of_use, name='terms_of_use'),
    path(
        'securitypages-pagesdesecurite/<page_action>/',
        views.security_pages,
        name='security_pages'
    ),
    path('securitypages-pagesdesecurite/', views.security_pages, name='security_pages'),
    path(
        'securityquestions-questionsdesecurite/',
        views.set_security_question,
        name='set-questions'
    ),
    path(
        'login-ouverturedesession/',
        axes_dispatch(PleioLoginView.as_view(redirect_authenticated_user=True)),
        name='login'
    ),
    path('logout/', views.logout, name='logout'),
    path('profile-profil/', views.profile, name='profile'),
    path(
        'accept_previous_logins/<acceptation_token>/',
        views.accept_previous_login,
        name='accept_previous_login'
    ),
    path(
        'account/sessions/other/delete/',
        view=PleioSessionDeleteOtherView.as_view(),
        name='session_delete_other'
    ),
    path(
        'account/sessions/<pk>/delete/',
        view=PleioSessionDeleteView.as_view(),
        name='session_delete'
    ),
    path(
        'oauth/v2/authorize',
        oauth2_views.AuthorizationView.as_view(),
        name='authorize'
    ),
    path('oauth/v2/token', oauth2_views.TokenView.as_view(), name='token'),
    path(
        'oauth/v2/revoke_token',
        oauth2_views.RevokeTokenView.as_view(),
        name='revoke-token'
    ),
    path('api/users/me', api_views.me, name='me'),
    path('api/', include(router.urls)),
     path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('freshdesk/', views.freshdesk_sso, name='freshdesk_sso'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    # Overriding some of the built-in contrib.auth views to use our templates
    # instead.
    path(
        'password_reset/',
        forms.ResetPasswordRequestView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        {
            'template_name': 'registration/password_reset_done.html'
        },
        name='password_reset_done'
    ),
    path(
        'password_reset/questions/',
        views.security_questions,
        name='password_reset_questions'
    ),
    path(
        'password_reset/notactive/',
        views.not_active_profile,
        name='password_reset_not_active'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        {
            'template_name': 'registration/password_reset_confirm.html'
        },
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        {
            'template_name': 'registration/password_reset_complete.html'
        },
        name='password_reset_complete'
    ),
    # django-two-factor
    path('', include(tf_urls)),
    # django-user-sessions
    path('', include('user_sessions.urls', 'user_sessions')),
    # django-oidc-provider
    path('openid/', decorated_includes(
      xframe_options_exempt,
      include('oidc_provider.urls', namespace='oidc_provider')
    )),
    path(
        'security_pages/remove_access',
        views.revoke_app_access,
        name='remove_access'
    )
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
