from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ..models import SiteConfiguration

class SiteConfigurationForm(forms.ModelForm):
    """
    Formulario para gestionar la configuración global del sitio.
    """

    translation_api_url = forms.CharField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tu-servidor-translate'}))
    class Meta:

        model = SiteConfiguration
        fields = [
            'default_language',
            'auto_translate_enabled',
            'translation_provider',
            'translation_api_url',
            'translation_api_key',
            'translation_timeout',
        ]
        widgets = {
            'default_language': forms.Select(attrs={'class': 'form-select'}),
            'auto_translate_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'translation_provider': forms.Select(attrs={'class': 'form-select'}),
            'translation_api_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tu-servidor-translate'}),
            'translation_api_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'translation_timeout': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'step': 1}),
        }

    def clean_default_language(self):
        lang = self.cleaned_data.get('default_language') or settings.LANGUAGE_CODE
        language_codes = [code for code, _ in settings.LANGUAGES]
        if lang not in language_codes:
            raise ValidationError('Idioma seleccionado no es válido.')
        return lang

    def clean(self):
        cleaned = super().clean()
        use_auto = cleaned.get('auto_translate_enabled')
        provider = cleaned.get('translation_provider')
        api_url = cleaned.get('translation_api_url')
        timeout = cleaned.get('translation_timeout')

        provider_default_url = getattr(settings, 'TRANSLATION_API_URL', 'http://libretranslate:5000')
        effective_url = api_url or provider_default_url

        if use_auto:
            if not api_url:
                cleaned['translation_api_url'] = effective_url
                self.instance.translation_api_url = effective_url

        if timeout is not None and timeout <= 0:
            self.add_error('translation_timeout', 'El tiempo de espera debe ser mayor que cero.')

        return cleaned
    
    def clean_honeypot(self):
        """Check honeypot field - should be empty."""
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise ValidationError('Bot detected.')
        return honeypot


class InitialSetupForm(forms.Form):
    """
    Formulario para el asistente de primer arranque y creación del superusuario.
    """

    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    language = forms.ChoiceField(
        label=_("Dashboard language"),
        choices=[],
        initial=settings.LANGUAGE_CODE,
    )

    def __init__(self, *args, **kwargs):
        available_languages = kwargs.pop('available_languages', settings.LANGUAGES)
        super().__init__(*args, **kwargs)
        self.fields['language'].choices = list(available_languages)
        placeholders = {
            'username': _('Choose a username'),
            'email': _('Admin email address'),
            'password1': _('Enter a strong password'),
            'password2': _('Repeat the password'),
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control-custom')
            if name in placeholders:
                field.widget.attrs.setdefault('placeholder', placeholders[name])

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if not username:
            raise ValidationError(_('Username is required.'))
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            raise ValidationError(_('This username is already taken.'))
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise ValidationError(_('Email address is required.'))
        user_model = get_user_model()
        if user_model.objects.filter(email=email).exists():
            raise ValidationError(_('This email address is already in use.'))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1 or not password2:
            raise ValidationError(_('Both password fields are required.'))
        if password1 != password2:
            raise ValidationError(_('Passwords do not match.'))
        user_model = get_user_model()
        temp_user = user_model(
            username=self.cleaned_data.get('username') or '',
            email=self.cleaned_data.get('email') or '',
        )
        password_validation.validate_password(password2, user=temp_user)
        return password2

    def save(self):
        cleaned = self.cleaned_data
        user_model = get_user_model()
        with transaction.atomic():
            user = user_model.objects.create_superuser(
                username=cleaned['username'],
                email=cleaned['email'],
                password=cleaned['password1'],
            )
            config = SiteConfiguration.get_solo()
            language = cleaned.get('language') or settings.LANGUAGE_CODE
            update_fields = []
            if config.default_language != language:
                config.default_language = language
                update_fields.append('default_language')
            if not config.auto_translate_enabled:
                config.auto_translate_enabled = True
                update_fields.append('auto_translate_enabled')
            if update_fields:
                update_fields.append('updated_at')
                config.save(update_fields=update_fields)
        return user
