from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.utils.translation import ugettext_lazy as _
from .user_manager import UserManager
from phonenumber_field.modelfields import PhoneNumberField

from core.utils import ik_validator, car_number_validator
import core.proj_conf as conf


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_('Email address'),
        max_length=255,
        unique=True,
    )

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    ik = models.BigIntegerField(_('isikukood'), null=True, blank=True,
                                validators=[MinValueValidator(30000000000),
                                            MaxValueValidator(69999999999),
                                            ik_validator])
    phone = PhoneNumberField(_('Phone'), help_text=_('Contact phone number'))
    car_model = models.CharField(_('car model'), max_length=50)
    car_type = models.IntegerField(_('car type'), choices=conf.CAR_TYPE, default=conf.CAR_TYPE[-1][0])
    car_carrying = models.IntegerField(_('car carrying (kg)'),
                                       validators=[MinValueValidator(100), MaxValueValidator(10000)])
    car_number = models.CharField(_('car number'), max_length=7,
                                  validators=[MinLengthValidator(5), MaxLengthValidator(7), car_number_validator])
    payment = models.IntegerField(_('payment method'), choices=conf.PAYMENT_METHOD, default=conf.PAYMENT_METHOD[0][0])
    movers_num = models.IntegerField(_('number of available movers'),
                                     choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
                                     default=0)
    preferred_language = models.IntegerField(_('Preferred language'),
                                             choices=conf.PREFERRED_LANGUAGE,
                                             default=conf.PREFERRED_LANGUAGE[0][0],
                                             help_text=_('Preferred language to use delivery24'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    email_confirmed = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # required fields will be used when using command createsuperuser
    REQUIRED_FIELDS = ['first_name', 'last_name', 'ik', 'phone', 'car_model', 'car_carrying', 'car_number', 'payment',
                       'movers_num', 'preferred_language']

    class Meta:
        verbose_name = _('user', )
        verbose_name_plural = _('users', )

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

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
