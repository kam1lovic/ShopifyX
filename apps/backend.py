from django.contrib.auth.backends import ModelBackend

from apps.models import User


class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:

            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
