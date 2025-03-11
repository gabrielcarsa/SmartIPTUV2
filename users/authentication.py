from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

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
