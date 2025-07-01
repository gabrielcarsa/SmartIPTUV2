from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        User = get_user_model()

        # Try autenticate 
        if username is None:
            return None
        try:
            # Search user by email
            user = User.objects.get(email=username)
            
            # Check the user password 
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
