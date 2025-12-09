from django import forms
from ..utils.files import clean_uploaded_file
from ..utils.validators import validate_no_executable, validate_filename

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
