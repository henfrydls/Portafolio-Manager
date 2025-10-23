"""
Forms for the portfolio application with enhanced security.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.text import slugify
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from parler.forms import TranslatableModelForm
from .models import (
    Contact,
    Profile,
    Project,
    KnowledgeBase,
    ProjectType,
    Category,
    BlogPost,
    Experience,
    Education,
    Skill,
    SiteConfiguration,
)
from .validators import validate_no_executable, validate_filename


class SecureContactForm(forms.ModelForm):
    """
    Contact form with enhanced security and validation.
    """
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo',
                'maxlength': 100,
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asunto del mensaje',
                'maxlength': 200,
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu mensaje aqu├¡...',
                'rows': 6,
                'maxlength': 2000,
                'required': True
            }),
        }
    
    def clean_name(self):
        """Clean and validate name field."""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('El nombre es requerido.')
        
        if len(name) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        
        # Remove potentially dangerous characters
        name = escape(name)
        
        # Check for suspicious patterns
        suspicious_patterns = ['<script', 'javascript:', 'vbscript:', 'onload=']
        name_lower = name.lower()
        for pattern in suspicious_patterns:
            if pattern in name_lower:
                raise ValidationError('El nombre contiene caracteres no v├ílidos.')
        
        return name
    
    def clean_email(self):
        """Clean and validate email field."""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise ValidationError('El email es requerido.')
        
        # Basic email validation (Django's EmailField handles most of this)
        if '@' not in email or '.' not in email:
            raise ValidationError('Ingresa un email v├ílido.')
        
        return email
    
    def clean_subject(self):
        """Clean and validate subject field."""
        subject = self.cleaned_data.get('subject', '').strip()
        
        if not subject:
            raise ValidationError('El asunto es requerido.')
        
        if len(subject) < 3:
            raise ValidationError('El asunto debe tener al menos 3 caracteres.')
        
        # Remove potentially dangerous characters
        subject = escape(subject)
        
        return subject
    
    def clean_message(self):
        """Clean and validate message field."""
        message = self.cleaned_data.get('message', '').strip()
        
        if not message:
            raise ValidationError('El mensaje es requerido.')
        
        if len(message) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres.')
        
        # Remove potentially dangerous characters
        message = escape(message)
        
        # Check for spam patterns
        spam_patterns = [
            'viagra', 'casino', 'lottery', 'winner', 'congratulations',
            'click here', 'free money', 'make money fast'
        ]
        message_lower = message.lower()
        for pattern in spam_patterns:
            if pattern in message_lower:
                raise ValidationError('El mensaje contiene contenido no permitido.')
        
        return message


class SecureFileUploadForm(forms.Form):
    """
    Base form for secure file uploads.
    """
    file = forms.FileField(
        validators=[validate_no_executable],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.webp,.pdf,.doc,.docx'
        })
    )
    
    def clean_file(self):
        """Clean and validate uploaded file."""
        uploaded_file = self.cleaned_data.get('file')
        
        if not uploaded_file:
            return uploaded_file
        
        # Validate filename
        validate_filename(uploaded_file.name)
        
        # Additional security checks
        from .file_handlers import clean_uploaded_file
        return clean_uploaded_file(uploaded_file)


class HoneypotMixin:
    """
    Mixin to add honeypot field for bot detection.
    """
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none !important;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )


class SiteConfigurationForm(forms.ModelForm):
    """
    Formulario para gestionar la configuraci├│n global del sitio.
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
            raise ValidationError('Idioma seleccionado no es v├ílido.')
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


class SecureContactFormWithHoneypot(HoneypotMixin, SecureContactForm):
    """
    Contact form with honeypot protection against bots.
    """
    pass


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


# Admin forms with enhanced security
class SecureProfileForm(TranslatableModelForm):
    """
    Profile form with file upload validation.
    """

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)
        tech_language = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        if 'knowledge_bases' in self.fields:
            self.fields['knowledge_bases'].queryset = KnowledgeBase.objects.language(tech_language).order_by('translations__name')
        if 'project_type_obj' in self.fields:
            self.fields['project_type_obj'].queryset = ProjectType.objects.language(tech_language).order_by('order', 'translations__name')

        placeholders = {
            'name': _('Your name'),
            'title': _('Your professional title (e.g., Full Stack Developer).'),
            'bio': _('Update your biography to introduce yourself.'),
            'email': _('contact@example.com'),
            'phone': _('Phone number (optional)'),
            'location': _('City, Country'),
            'linkedin_url': _('https://www.linkedin.com/in/username'),
            'github_url': _('https://github.com/username'),
            'medium_url': _('https://medium.com/@username'),
        }
        for field, placeholder in placeholders.items():
            if field in self.fields:
                self.fields[field].widget.attrs.setdefault('placeholder', placeholder)

        label_overrides = {
            'name': _('Name'),
            'title': _('Professional title'),
            'bio': _('Biography'),
            'email': _('Email'),
            'phone': _('Phone'),
            'location': _('Location'),
            'linkedin_url': _('LinkedIn URL'),
            'github_url': _('GitHub URL'),
            'medium_url': _('Medium URL'),
            'resume_pdf': _('PDF resume (English)'),
            'resume_pdf_es': _('PDF resume (Spanish)'),
            'show_web_resume': _('Display web resume on the site'),
        }
        for field, label in label_overrides.items():
            if field in self.fields:
                self.fields[field].label = label
    
    class Meta:
        model = Profile
        fields = [
            'name', 'title', 'bio', 'profile_image', 'email', 'phone', 'location',
            'linkedin_url', 'github_url', 'medium_url', 
            'resume_pdf', 'resume_pdf_es', 'show_web_resume'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'profile_image': forms.FileInput(),
            'resume_pdf': forms.FileInput(),
            'resume_pdf_es': forms.FileInput(),
        }
    
    def clean_profile_image(self):
        """Validate profile image upload."""
        image = self.cleaned_data.get('profile_image')

        # If no new image uploaded but instance has existing image, keep existing
        if not image and self.instance and self.instance.pk and self.instance.profile_image:
            return self.instance.profile_image

        # Only validate if a new image is being uploaded
        if image:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(image)

        return image
    
    def clean_resume_pdf(self):
        """Validate resume PDF upload (English)."""
        pdf = self.cleaned_data.get('resume_pdf')

        # If no new PDF uploaded but instance has existing PDF, keep existing
        if not pdf and self.instance and self.instance.pk and self.instance.resume_pdf:
            return self.instance.resume_pdf

        # Only validate if a new PDF is being uploaded
        if pdf:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(pdf)

        return pdf
    
    def clean_resume_pdf_es(self):
        """Validate resume PDF upload (Spanish)."""
        pdf = self.cleaned_data.get('resume_pdf_es')

        # If no new PDF uploaded but instance has existing PDF, keep existing
        if not pdf and self.instance and self.instance.pk and self.instance.resume_pdf_es:
            return self.instance.resume_pdf_es

        # Only validate if a new PDF is being uploaded
        if pdf:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(pdf)

        return pdf

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        instance = super().save(commit=commit)
        if commit and instance.pk:
            default_name = self.cleaned_data.get('name')
            if default_name and hasattr(instance, 'translations'):
                translation_model = instance.translations.model
                translation_model.objects.filter(master_id=instance.pk).update(name=default_name)
        return instance


def build_primary_language_choices(language_code, current_value=""):
    """
    Build select options for the primary knowledge base field.

    Returns (choices, initial_value).
    """
    queryset = (
        KnowledgeBase.objects.language(language_code)
        .order_by('translations__name')
        .distinct()
    )
    choices = [('', _("Select primary knowledge base"))]
    seen_identifiers = set()
    value_map = {}

    for kb in queryset:
        identifier = (kb.identifier or str(kb.pk)).strip()
        if not identifier or identifier in seen_identifiers:
            continue
        label = kb.safe_translation_getter('name', any_language=True) or identifier
        choices.append((identifier, label))
        seen_identifiers.add(identifier)
        value_map[identifier.lower()] = identifier
        if label:
            value_map[label.lower()] = identifier

    initial_value = ""
    if current_value:
        stored = current_value.strip()
        match = value_map.get(stored.lower())
        if match:
            initial_value = match
        else:
            choices.append((stored, stored))
            initial_value = stored

    return choices, initial_value


class SecureProjectForm(TranslatableModelForm):
    """
    Project form with file upload validation.
    """

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)
        active_language = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        current_value = ''
        if self.instance and getattr(self.instance, 'pk', None):
            current_value = self.instance.primary_language or ''
        original_field = self.fields.get('primary_language')
        if original_field:
            help_text = original_field.help_text
            label = original_field.label or _("Primary knowledge base")
            choices, initial_value = build_primary_language_choices(active_language, current_value)
            self.fields['primary_language'] = forms.ChoiceField(
                choices=choices,
                required=False,
                label=label,
                help_text=help_text,
            )
            self.fields['primary_language'].initial = initial_value
            self.fields['primary_language'].widget.attrs.setdefault('class', 'form-select')

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'detailed_description', 'image', 'project_type_obj',
            'knowledge_bases', 'primary_language', 'github_owner', 'github_url',
            'demo_url', 'visibility', 'order', 'featured', 'is_private_project',
            'featured_link_type', 'featured_link_post', 'featured_link_pdf'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'detailed_description': forms.Textarea(attrs={'rows': 6}),
            'knowledge_bases': forms.CheckboxSelectMultiple(),
        }
    
    def clean_image(self):
        """Validate project image upload."""
        image = self.cleaned_data.get('image')
        if image:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(image)
        return image

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)


class SecureBlogPostForm(TranslatableModelForm):
    """
    Blog post form with file upload validation.
    """

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = BlogPost
        fields = [
            'title', 'excerpt', 'content', 'featured_image', 'category',
            'reading_time', 'tags', 'status', 'publish_date', 'featured',
            'github_url', 'medium_url', 'linkedin_url'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tags': forms.TextInput(attrs={'placeholder': 'django, python, web'}),
        }
    
    def clean_featured_image(self):
        """Validate blog post image upload."""
        image = self.cleaned_data.get('featured_image')
        if image:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(image)
        return image
    
    def clean_content(self):
        """Clean and validate blog post content."""
        content = self.cleaned_data.get('content', '').strip()
        
        # Basic XSS protection (escape HTML)
        content = escape(content)
        
        return content

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)


# Catalog Management Forms
class SecureCategoryForm(TranslatableModelForm):
    """Category form with translation awareness."""

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ['name', 'description', 'slug', 'is_active', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={'placeholder': 'innovacion-digital'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name)
        return slug

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        if not self.instance.slug:
            self.instance.slug = slugify(self.instance.safe_translation_getter('name') or self.cleaned_data.get('name', ''))
        return super().save(commit=commit)


class SecureProjectTypeForm(TranslatableModelForm):
    """ProjectType form aligned with admin style."""

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProjectType
        fields = ['name', 'description', 'slug', 'is_active', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={'placeholder': 'innovation'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name)
        return slug

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        if not self.instance.slug:
            self.instance.slug = slugify(self.instance.safe_translation_getter('name') or self.cleaned_data.get('name', ''))
        return super().save(commit=commit)


class SecureKnowledgeBaseForm(TranslatableModelForm):
    """KnowledgeBase form with helpful defaults."""

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)
        self.fields['identifier'].help_text = self.fields['identifier'].help_text or 'Stable identifier used internally.'

    class Meta:
        model = KnowledgeBase
        fields = ['name', 'identifier', 'icon', 'color']
        widgets = {
            'identifier': forms.TextInput(attrs={'placeholder': 'python', 'maxlength': 60}),
            'icon': forms.TextInput(attrs={'placeholder': 'fab fa-python'}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()
        return slugify(identifier)

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        instance = super().save(commit=commit)
        if not instance.icon:
            instance.icon = instance.get_suggested_icon()
        if not instance.color:
            instance.color = instance.get_suggested_color()
        if commit:
            instance.save(update_fields=['icon', 'color'])
        return instance


# CV Management Forms
class SecureExperienceForm(TranslatableModelForm):
    """
    Experience form with validation.
    """
    
    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = Experience
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get('current')
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        
        if current and end_date:
            raise ValidationError('No puedes tener fecha de fin si es trabajo actual.')
        
        if not current and not end_date:
            raise ValidationError('Debes especificar fecha de fin o marcar como trabajo actual.')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)


class SecureEducationForm(TranslatableModelForm):
    """
    Education form with validation.
    """
    
    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = Education
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get('current')
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        
        if current and end_date:
            raise ValidationError('No puedes tener fecha de fin si est├í en curso.')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)


class SecureSkillForm(TranslatableModelForm):
    """
    Skill form with validation.
    """
    
    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)

    class Meta:
        model = Skill
        fields = '__all__'
        widgets = {
            'proficiency': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_years_experience(self):
        years = self.cleaned_data.get('years_experience')
        if years and years > 50:
            raise ValidationError('Los a├▒os de experiencia no pueden ser m├ís de 50.')
        if years and years < 0:
            raise ValidationError('Los a├▒os de experiencia no pueden ser negativos.')
        return years

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)
