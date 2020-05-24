from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from .user_manager import UserManager
from phone_field import PhoneField


USER_TYPE = [
    ('DR', 'Driver'),
    ('CU', 'Customer'),
]


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(choices=USER_TYPE, max_length=2, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type',]

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


class Driver(models.Model):
    PAYMENT_METHOD = [
        (1, 'Cash'),
        (2, 'Bank'),
        (3, 'Both'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    ik = models.IntegerField(_('isikukood'), null=True, blank=True)
    phone = PhoneField(help_text='Contact phone number', null=True)
    car_model = models.CharField(_('car model'), max_length=50)
    car_carrying = models.IntegerField(_('car carrying'))
    car_number = models.CharField(_('car number'), max_length=7)
    payment = models.IntegerField(_('payment method'), choices=PAYMENT_METHOD)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Driver.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.driver.save()