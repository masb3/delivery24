from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from .user_manager import UserManager
from phone_field import PhoneField


class User(AbstractBaseUser, PermissionsMixin):
    PAYMENT_METHOD = [
        (1, 'Cash'),
        (2, 'Bank'),
        (3, 'Both'),
    ]

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    ik = models.IntegerField(_('isikukood'), null=True, blank=True)
    phone = PhoneField(help_text='Contact phone number', null=True)
    car_model = models.CharField(_('car model'), max_length=50)
    car_carrying = models.IntegerField(_('car carrying'), blank=True, null=True)
    car_number = models.CharField(_('car number'), max_length=7)
    payment = models.IntegerField(_('payment method'), choices=PAYMENT_METHOD, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user',)
        verbose_name_plural = _('users',)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
