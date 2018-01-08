from django import forms
from django.forms import Form
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm

from account.models import User


class SignUpForm(Form):
    """Formulario de creación de usuarios
    """
    first_name = forms.CharField(
        label='first name',
        required=True,
        max_length=50,
        error_messages={
            'required': 'This field is required.',
        },
    )

    last_name = forms.CharField(
        label='last name',
        required=True,
        max_length=50,
        error_messages={
            'required': 'This field is required.',
        },
    )

    email = forms.EmailField(
        label=u'email',
        required=True,
        max_length=50,
        error_messages={
            'required': 'This field is required.',
        },
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label=u"password",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginForm(Form):
    email = forms.EmailField(
        label=u'email',
        required=True,
        max_length=50,
        error_messages={
            'required': 'This field is required.',
        },
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label=u'password',
        required=True,
        max_length=50,
        error_messages={
            'required': 'This field is required.',
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs['placeholder'] = 'email'
        self.fields['password'].widget.attrs['placeholder'] = 'password'


class ProfileForm(ModelForm):
    country_search = forms.CharField(
        required=True,
        label='country',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Type the contry name and select one from the list.',
            },
        ),
    )

    country_code = forms.CharField(
        required=True,
        label='country code',
    )

    city_search = forms.CharField(
        label='city',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Type the city name.',
            },
        ),
    )

    city_id = forms.CharField(
        label='city id',
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'country_search',
            'country_code',
            'city_search',
            'city_id',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance', None)

        country = user.country
        city = user.city

        if country:
            self.fields['country_search'].initial = user.country.name
            self.fields['country_code'].initial = user.country.country.code

        if city:
            self.fields['city_search'].initial = user.city.name
            self.fields['city_id'].initial = user.city.id


class ProfileDescriptionForm(Form):
    description_en = forms.CharField(
        required=False,
        min_length=40,
        label='description',
        widget=forms.Textarea,
    )

    description_es = forms.CharField(
        required=False,
        min_length=40,
        label='description',
        widget=forms.Textarea,
    )


class UserPasswordResetForm(PasswordResetForm):
    required_css_class = 'required'

    def get_users(self, email):
        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True
        )
        return (u for u in active_users)


class ProfileAutocompleteForm(Form):
    userprofile = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search by name, email or username',
            },
        ),
        label='',
    )
