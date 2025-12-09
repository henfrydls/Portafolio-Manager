from django import forms
from django.conf import settings
from django.utils import translation
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.forms import TranslatableModelForm

from ..models import Project, ProjectType, KnowledgeBase
from ..utils.files import clean_uploaded_file


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

        # Fix for duplicate project types/knowledge bases in dropdown due to Parler joins
        # Override ordering to avoid joining with translations table which multiplies rows
        self.fields['project_type_obj'].queryset = ProjectType.objects.order_by('order', 'id')
        
        self.fields['knowledge_bases'].queryset = KnowledgeBase.objects.order_by('identifier')

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
            return clean_uploaded_file(image)
        return image

    def save(self, commit=True):
        language_code = getattr(self, 'language_code', None) or translation.get_language() or settings.LANGUAGE_CODE
        self.instance.set_current_language(language_code)
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
