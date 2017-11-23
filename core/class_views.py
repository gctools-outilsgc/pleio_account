from django.contrib.auth.forms import AuthenticationForm
from .forms import PleioAuthenticationTokenForm
from .models import User
from two_factor.forms import TOTPDeviceForm, BackupTokenForm
from two_factor.views.core import LoginView, SetupView

class PleioLoginView(LoginView):
    template_name = 'login.html'

    form_list = (
        ('auth', AuthenticationForm),
        ('token', PleioAuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def done(self, form_list, **kwargs):
        self.request.session.set_expiry(30 * 24 * 60 * 60)

        user = self.get_user()
        user.check_users_previous_logins(self.request)

        return LoginView.done(self, form_list, **kwargs)
