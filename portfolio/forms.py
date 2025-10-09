"""
Forms for the portfolio application with enhanced security.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from .models import Contact, Profile, Project, BlogPost, Experience, Education, Skill
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


# Admin forms with enhanced security
class SecureProfileForm(forms.ModelForm):
    """
    Profile form with file upload validation.
    """
    
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


class SecureProjectForm(forms.ModelForm):
    """
    Project form with file upload validation.
    """
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'detailed_description', 'image', 'project_type_obj',
            'technologies', 'primary_language', 'github_owner', 'github_url',
            'demo_url', 'visibility', 'order', 'featured', 'is_private_project',
            'featured_link_type', 'featured_link_post', 'featured_link_pdf'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'detailed_description': forms.Textarea(attrs={'rows': 6}),
            'technologies': forms.CheckboxSelectMultiple(),
        }
    
    def clean_image(self):
        """Validate project image upload."""
        image = self.cleaned_data.get('image')
        if image:
            from .file_handlers import clean_uploaded_file
            return clean_uploaded_file(image)
        return image


class SecureBlogPostForm(forms.ModelForm):
    """
    Blog post form with file upload validation.
    """
    
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


# CV Management Forms
class SecureExperienceForm(forms.ModelForm):
    """
    Experience form with validation.
    """
    
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


class SecureEducationForm(forms.ModelForm):
    """
    Education form with validation.
    """
    
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


class SecureSkillForm(forms.ModelForm):
    """
    Skill form with validation.
    """
    
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