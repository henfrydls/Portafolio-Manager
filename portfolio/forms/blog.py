from django import forms
from django.conf import settings
from django.utils import translation
from django.utils.html import escape
from django.utils.text import slugify
from parler.forms import TranslatableModelForm

from ..models import BlogPost, Category
from ..utils.files import clean_uploaded_file


class SecureBlogPostForm(TranslatableModelForm):
    """
    Blog post form with file upload validation.
    """

    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', None)
        if language_code:
            self.language_code = language_code
        super().__init__(*args, **kwargs)
        
        # Check if Category is loaded to avoid circular imports randomly
        # Fix for duplicate categories in dropdown due to Parler translation joins
        self.fields['category'].queryset = Category.objects.order_by('order', 'id')

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
