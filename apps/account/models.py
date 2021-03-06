from django.db import models
from django.core import validators
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.models import User
from datetime import timedelta
import requests
from ..rate.models import Rate
from ..transaction.models import Transaction


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):

        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.USER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    @property
    def new_password(self):
        return None

    @new_password.setter
    def new_password(self, value):
        pass

    USER = "user"
    ADMIN = "admin"
    SUBSCRIPTION = "subscription"

    ROLE = [
        (USER, "user"),
        (ADMIN, "admin"),
        (SUBSCRIPTION, "subscription"),
    ]

    email = models.EmailField(
        db_index=True,
        validators=[validators.validate_email],
        unique=True,
        blank=False,
    )
    avatar = models.ImageField(
        upload_to='photos/%y/%m/%d/',
        max_length=500,
        null=True, blank=True
    )
    first_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="??????"
    )
    last_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="??????????????"
    )
    patronymic = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="????????????????"
    )

    role = models.CharField(
        choices=ROLE,
        default="user",
        max_length=20,
        blank=False,
        null=False,
        verbose_name="????????",
    )

    date_create = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="???????? ??????????????????????")
    is_staff = models.BooleanField(default=False, verbose_name="????????????????")
    is_active = models.BooleanField(default=True, verbose_name='???????????????? ????????????????????????')
    is_superuser = models.BooleanField(default=False, verbose_name="??????????????????????????")
    post_agreement = models.BooleanField(default=True, verbose_name="???????????????? ???? ???????????????? ??????????")
    card = models.CharField(max_length=16, null=True, blank=True, verbose_name="??????????")
    card_year = models.CharField(max_length=5, null=True, blank=True, verbose_name="???????? ???????????????? ??????????")
    card_ovner = models.CharField(max_length=250, null=True, blank=True, verbose_name="???????????? ?????????????????? ??????????")

    marketplace_data = models.ManyToManyField("marketplace.Marketplace", related_name="user_marketplace", blank=True, null=True)

    name_org = models.CharField(max_length=256, null=True, blank=True, verbose_name="???????????????? ??????????????????????")
    inn = models.CharField(max_length=12, null=True, blank=True, verbose_name="??????")
    orgn = models.CharField(max_length=12, null=True, blank=True, verbose_name="????????")
    kpp = models.CharField(max_length=9, null=True, blank=True, verbose_name="??????")
    bank_account = models.CharField(max_length=20, null=True, blank=True, verbose_name="?????????? ??????????")
    bank = models.CharField(max_length=1000, null=True, blank=True, verbose_name="???????????????? ??????????")
    correspondent_bank_account = models.CharField(max_length=20, null=True, blank=True,
                                                  verbose_name="???????????????????????????????? ????????")
    bik = models.CharField(max_length=8, null=True, blank=True, verbose_name="??????")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]
    objects = UserManager()

    def transaction_data(self):
        user_transaction_query = Transaction.objects.filter(id_user=self.id)
        return_transaction = ''

        for user_transaction in user_transaction_query:
            return_transaction = return_transaction + f'?????????? ????????????????????:  {user_transaction.transaction_number}, ' \
                                                      f'\n ???????? ????????????????????:  {user_transaction.date_issued}, \n ' \
                                                      f'?????? ????????????:  {user_transaction.type}, \n ??????????: ' \
                                                      f'{user_transaction.rate}, \n ??????????:  {user_transaction.summ}' \
                                                      f'\n \n \n'

        return return_transaction

    def user_tarif_data(self):

        rate_data = []
        try:
            rate_query = Rate.objects.get(slag=self.role)
            rate = rate_query.rate_name
            tarif_action = rate_query.validity

            try:
                transaction_query = Transaction.objects.get(id_user=self.pk, rate=rate_query.pk)

                if transaction_query.date_issued is not None:
                    date_issued = transaction_query.date_issued
                    next_date_issued = date_issued + timedelta(rate_query.validity)
            except Transaction.DoesNotExist:
                next_date_issued = None

        except Rate.DoesNotExist:
            rate = None
            next_date_issued = None
            tarif_action = None

        rate_data.append(rate)
        rate_data.append(next_date_issued)
        rate_data.append(tarif_action)

        return rate_data

    def return_status(self):
        api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list', headers={'Client-Id': str(self.ozon_id),
                                                                                             'Api-Key': str(self.api_key),
                                                                                             'Content-Type': 'application/json',
                                                                                             'Host': 'api-seller.ozon.ru'})
        if api_key_isset.status_code == 200:
            status = 'valid'
        else:
            status = 'novalid'

        return status

    class Meta:
        verbose_name = "????????????????????????"
        verbose_name_plural = "????????????????????????"
        ordering = ("id",)

    def __str__(self):
        return self.email


class UserResetPasswordCode(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    verify_code = models.CharField(max_length=100)