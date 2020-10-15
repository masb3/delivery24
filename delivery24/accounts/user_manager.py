from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        Creates and saves a User with the given email, password and other fields

        """
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)

        user.first_name = kwargs['first_name']
        user.last_name = kwargs['last_name']
        user.ik = kwargs['ik']
        user.phone = kwargs['phone']
        user.car_model = kwargs['car_model']
        user.car_carrying = kwargs['car_carrying']
        user.car_number = kwargs['car_number']
        user.payment = kwargs['payment']
        user.movers_num = kwargs['movers_num']
        user.preferred_language = kwargs['preferred_language']

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email, password and other fields
        """
        user = self.create_user(email, password=password, **kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user

