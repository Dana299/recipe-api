from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomUserManager(BaseUserManager):
    """
    Custom manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, user_name, password, **extra_fields):
        if not email:
            raise ValueError(
                _('You must provide an email address')
            )

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, user_name, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                "Supersuer must be assigned to is_staff = True"
            )

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                "Supersuer must be assigned to is_superuser = True"
            )

        if not email:
            raise ValueError(_('The Email must be set'))

        return self.create_user(email, user_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=50, unique=True)
    about = models.TextField(
        _('about'), max_length=1000, blank=True
    )
    # User status
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name',]

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return self.user_name
