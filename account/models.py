from __future__ import unicode_literals

from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.utils.crypto import get_random_string
from app.validators import FileSizeValidator

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinLengthValidator
from django.utils import timezone

from .data import DEACTIVATED_COMPANY
from .data import DELETED_COMPANY
from .data import NEW_APPLICANTS
from .data import NEW_COMPANY_SCORE
from .data import NEW_ENTREPRENEUR_ADMIN
from .data import NEW_JOB_OFFER
from .data import NEW_MESSAGE_TO_COMPANY
from .data import NOTIFICATION_TYPE_CHOICES
from .data import OLD_JOB_OFFER_CLOSED
from .data import TRANSFERED_COMPANY
from .data import UPDATED_PRIVACY_POLICY
from .data import UPDATED_TERMS
from .data import DELETED_MEMBERSHIP
from entrepreneur.data import ACTIVE_MEMBERSHIP
from entrepreneur.models import AdministratorMembership
from entrepreneur.models import Venture


class UserManager(BaseUserManager):
    """
    Class used to define the users creation. It inherits the
    validations defined in Django to create new users in a correct
    way. The user model defined in this application has an attribute
    called 'professionalprofile'. This attribute is a foreign key to
    a model that has an attribute called 'slug'. This attribute must
    be unique for registered users and companies and is done in this class.
    """
    def create_user(
        self,
        first_name,
        last_name,
        email,
        password=None,
        is_active=True,
    ):
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=UserManager.normalize_email(email),
            is_active=is_active,
        )

        if not first_name:
            first_name = 'Query'
        if not last_name:
            last_name = 'Jane'

        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.accepted_terms_date = timezone.now()
        user.save(using=self._db)

        # Generate new user slug.
        slug = slugify(
            '{0}{1}'.format(
                first_name,
                last_name,
            )
        )

        # If there is an user or a company with the same
        # slug, a new slug is generated with a random string.
        if (
            Venture.objects.filter(slug=slug) or
            ProfessionalProfile.objects.filter(slug=slug)
        ):
            random_string = get_random_string(length=6)
            slug = '{0}-{1}'.format(
                slug,
                random_string.lower(),
            )

        # Create professional profile object. All registered
        # user must have a professional profile.
        ProfessionalProfile.objects.create(
            user=user,
            slug=slug,
        )

        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model. It inherits the basic structure of the Django
    user model. The username field is overwiritten with the
    email value. This model manage basic user iformation and
    legal items status.
    """
    USERNAME_FIELD = 'email'

    avatar = models.ImageField(
        verbose_name=_('profile image'),
        max_length=255,
        blank=True,
        validators=[FileSizeValidator(4000)],
    )

    first_name = models.CharField(
        verbose_name=_('name'),
        max_length=128,
        blank=False,
        validators=[
            MinLengthValidator(3),
        ],
        error_messages={
            'min_length':
                'El campo "Nombre" debe tener al menos %(limit_value)d '
                'caracteres (actualmente tiene %(show_value)d).'
        }
    )

    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=128,
        blank=False,
        validators=[
            MinLengthValidator(3),
        ],
        error_messages={
            'min_length':
                'El campo "Apellidos" debe tener al menos %(limit_value)d '
                'caracteres (actualmente tiene %(show_value)d).'
        }
    )

    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
        blank=False,
    )

    is_staff = models.BooleanField(
        'staff status',
        default=False,
    )

    is_active = models.BooleanField(
        'Activo',
        default=True,
    )

    country = models.ForeignKey(
        'place.Country',
        null=True,
        verbose_name=_('country'),
    )

    state = models.ForeignKey(
        'place.State',
        null=True,
        verbose_name=_('state'),
    )

    city = models.ForeignKey(
        'place.City',
        null=True,
        verbose_name=_('city'),
    )

    address = models.CharField(
        verbose_name=_('address'),
        max_length=80,
        null=True,
        blank=True,
    )

    date_joined = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )

    accepted_terms = models.BooleanField(
        verbose_name=_('accepted user agreement'),
        default=True,
    )

    accepted_terms_date = models.DateField(
        verbose_name=_('accepted user agreement date'),
        null=True,
        blank=True,
    )

    accepted_privacy_policy = models.BooleanField(
        verbose_name=_('accepted privacy policy'),
        default=True,
    )

    accepted_privacy_policy_date = models.DateField(
        verbose_name=_('accepted privacy policy date'),
        null=True,
        blank=True,
    )

    objects = UserManager()

    def get_short_name(self):
        return self.first_name if self.first_name else self.email.split('@')[0]

    @property
    def get_avatar(self):
        avatar = '/static/img/profile_default_avatar.svg'
        if self.avatar:
            avatar = self.avatar.url

        return avatar

    @property
    def get_country(self):
        country = None

        if self.country:
            country = self.country.country

        return country

    @property
    def get_full_name(self):
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def __str__(self):
        return self.get_full_name

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('email',)


class ProfessionalProfile(models.Model):
    """
    This model represents the professional profile of a
    registered user. This model manage the sectors in
    the indsutry that are interesting for the user, the
    basic profile and contact information and the notifications
    configuration.
    """
    user = models.OneToOneField(
        'account.User',
        verbose_name=_('user'),
    )

    description_en = models.TextField(
        blank=True,
        verbose_name=_('English description'),
    )

    description_es = models.TextField(
        blank=True,
        verbose_name=_('Spanish description'),
    )

    phone_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Phone number'),
    )

    industry_categories = models.ManyToManyField(
        'account.IndustryCategory',
        blank=True,
    )

    email_jobs_notifications = models.BooleanField(
        default=True,
        verbose_name=_('receive notifications of job offers'),
    )

    email_messages_notifications = models.BooleanField(
        default=True,
        verbose_name=_('receive notifications of new messages'),
    )

    new_applicants_notifications = models.BooleanField(
        default=True,
        verbose_name=_('receive notifications of new applicants to job offers'),
    )

    new_company_messages_notifications = models.BooleanField(
        default=True,
        verbose_name=_('receive notifications when companies I manage receive messages from users'),
    )

    new_company_scores_notifications = models.BooleanField(
        default=True,
        verbose_name=_('receive notifications when companies I manage receive scores from users'),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    has_new_messages = models.BooleanField(
        default=False,
        verbose_name=_('has new messages'),
    )

    slug = models.SlugField()

    def __str__(self):
        return '{0}'.format(self.user)

    @property
    def get_print(self):
        return self.user.get_full_name

    @property
    def get_managed_venture_ids(self):
        memberships = AdministratorMembership.objects.filter(
            admin=self,
            status=ACTIVE_MEMBERSHIP,
        )

        return list(memberships.values_list('venture__id', flat=True))


class IndustryCategory(models.Model):
    """
    This model represents the sectors in the cannabis industry.
    Users can select them and add to their professional profile.
    In this way, their professional profiles can be easely filtered
    by industry sector.
    """
    name_es = models.CharField(
        max_length=50,
        verbose_name=_('Spanish name'),
    )

    description_es = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Spanish description'),
    )

    name_en = models.CharField(
        max_length=50,
        verbose_name=_('English name'),
    )

    description_en = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('English description'),
    )

    class Meta:
        ordering = ('name_en',)

    def __str__(self):
        return '{0}'.format(self.name_en)


class UserNotification(models.Model):
    """
    This model represents a notification to a user. All
    different type of notifications, to users and companies
    are managed by using this model. The "notification_type"
    attribute is used to classify the notifications. It
    depends of the attributes value to know how notifications
    must be displayed in the application front end.
    """
    notification_type = models.PositiveSmallIntegerField(
        choices=NOTIFICATION_TYPE_CHOICES,
    )

    description = models.TextField(
        verbose_name=_('description'),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    was_seen = models.BooleanField(
        default=False,
    )

    noty_to = models.ForeignKey(
        'account.User',
        verbose_name=_('Notify to'),
    )

    venture_from = models.ForeignKey(
        'entrepreneur.Venture',
        verbose_name=_('from venture'),
        null=True,
    )

    venture_to = models.ForeignKey(
        'entrepreneur.Venture',
        verbose_name=_('venture to'),
        related_name='venture_to',
        null=True,
    )

    membership = models.ForeignKey(
        'entrepreneur.AdministratorMembership',
        verbose_name=_('membership invitation'),
        null=True,
    )

    job_offer = models.ForeignKey(
        'entrepreneur.JobOffer',
        verbose_name=_('related job offer'),
        null=True,
    )

    created_by = models.ForeignKey(
        'account.ProfessionalProfile',
        verbose_name=_('created by'),
        related_name='creator',
        null=True,
        blank=True,
    )

    @property
    def is_new_entrepreneur_admin(self):
        return self.notification_type == NEW_ENTREPRENEUR_ADMIN

    @property
    def is_interest_job_offer(self):
        return self.notification_type == NEW_JOB_OFFER

    @property
    def is_new_job_offer_applicants(self):
        return self.notification_type == NEW_APPLICANTS

    @property
    def is_new_message_to_company(self):
        return self.notification_type == NEW_MESSAGE_TO_COMPANY

    @property
    def is_new_score_to_company(self):
        return self.notification_type == NEW_COMPANY_SCORE

    @property
    def is_updated_user_agreement(self):
        return self.notification_type == UPDATED_TERMS

    @property
    def is_updated_privacy_policy(self):
        return self.notification_type == UPDATED_PRIVACY_POLICY

    @property
    def is_old_job_offer_closed(self):
        return self.notification_type == OLD_JOB_OFFER_CLOSED

    @property
    def is_company_deactivation(self):
        return self.notification_type == DEACTIVATED_COMPANY

    @property
    def is_company_elimination(self):
        return self.notification_type == DELETED_COMPANY

    @property
    def is_company_transfer(self):
        return self.notification_type == TRANSFERED_COMPANY

    @property
    def is_deleted_membership(self):
        return self.notification_type == DELETED_MEMBERSHIP

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.description


class Conversation(models.Model):
    """
    This model represents a conversation. Conversations
    between two users, and between an user and a company
    are managed by using this model.
    """
    participating_users = models.ManyToManyField(
        'account.User',
    )

    participating_company = models.ForeignKey(
        'entrepreneur.Venture',
        null=True,
    )

    updated_at = models.DateTimeField(null=True)

    @property
    def get_last_message(self):
        return self.usermessage_set.latest('created_at')

    @property
    def unread(self):
        return self.usermessage_set.filter(
            user_to__in=self.participating_users.all(),
            unread=True,
        ).exists()

    class Meta:
        ordering = ('-updated_at',)


class UserMessage(models.Model):
    """
    This model represents a private message. Users and
    companies can send private messages to other users.
    All messages must have a value in the 'conversation'
    value.
    """
    user_from = models.ForeignKey(
        'account.User',
        verbose_name=_('from'),
        related_name='user_from',
    )

    user_to = models.ForeignKey(
        'account.User',
        verbose_name=_('to'),
        related_name='user_to',
        null=True,
    )

    company_to = models.ForeignKey(
        'entrepreneur.Venture',
        verbose_name=_('to'),
        related_name='company_to',
        null=True,
    )

    company_from = models.ForeignKey(
        'entrepreneur.Venture',
        verbose_name=_('from'),
        related_name='company_from',
        null=True,
    )

    message = models.TextField(
        verbose_name=_('message'),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    unread = models.BooleanField(
        default=True,
    )

    conversation = models.ForeignKey(
        'account.Conversation'
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return 'message from {0}'.format(
            self.user_from.get_full_name,
        )


class UserContact(models.Model):
    """
    This model represents an user added to the address
    book.
    """
    owner = models.ForeignKey(
        'account.ProfessionalProfile',
        verbose_name=_('owner'),
        related_name='address_book_owner',
    )

    user_contact = models.ForeignKey(
        'account.ProfessionalProfile',
        verbose_name=_('contact'),
    )

    class Meta:
        ordering = ('user_contact',)

    def __str__(self):
        return 'contact: {0}'.format(
            self.user_contact.user.get_full_name,
        )


class CompanyContact(models.Model):
    """
    This model represents a company added to the
    address book.
    """
    owner = models.ForeignKey(
        'account.ProfessionalProfile',
        verbose_name=_('owner'),
    )

    company = models.ForeignKey(
        'entrepreneur.Venture',
    )

    class Meta:
        ordering = ('company',)

    def __str__(self):
        return 'contact: {0}'.format(
            self.company.name,
        )
