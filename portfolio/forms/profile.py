from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from parler.forms import TranslatableModelForm

from ..models import Profile, KnowledgeBase, ProjectType, Experience, Education, Skill
from ..utils.files import clean_uploaded_file


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
            raise ValidationError('No puedes tener fecha de fin si está en curso.')
        
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
            raise ValidationError('Los años de experiencia no pueden ser más de 50.')
        if years and years < 0:
            raise ValidationError('Los años de experiencia no pueden ser negativos.')
        return years

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
        return super().save(commit=commit)
