from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from ..models import Contact
from .base import HoneypotMixin

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
                'placeholder': 'Escribe tu mensaje aquí...',
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
                raise ValidationError('El nombre contiene caracteres no válidos.')
        
        return name
    
    def clean_email(self):
        """Clean and validate email field."""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise ValidationError('El email es requerido.')
        
        # Basic email validation (Django's EmailField handles most of this)
        if '@' not in email or '.' not in email:
            raise ValidationError('Ingresa un email válido.')
        
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


class SecureContactFormWithHoneypot(SecureContactForm):
    """
    Contact form with honeypot protection against bots.
    """
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none !important;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )
