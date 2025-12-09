"""
Custom file upload handlers with enhanced security.
"""
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.conf import settings
from .validators import validate_filename, validate_no_executable


def secure_filename(filename):
    """
    Generate a secure filename to prevent path traversal and other attacks.
    """
    # Validate the original filename
    validate_filename(filename)
    
    # Get file extension
    name, ext = os.path.splitext(filename)
    
    # Generate a unique filename with UUID
    secure_name = f"{uuid.uuid4().hex}{ext.lower()}"
    
    return secure_name


def get_upload_path(instance, filename):
    """
    Generate a secure upload path for files.
    """
    # Get the model name for organization
    model_name = instance.__class__.__name__.lower()
    
    # Generate secure filename
    secure_name = secure_filename(filename)
    
    # Create path: model_name/year/month/secure_filename
    from datetime import datetime
    now = datetime.now()
    path = f"{model_name}/{now.year}/{now.month:02d}/{secure_name}"
    
    return path


class SecureFileUploadHandler(TemporaryFileUploadHandler):
    """
    Custom upload handler that adds security checks during file upload.
    """
    
    def new_file(self, *args, **kwargs):
        """
        Called when a new file upload starts.
        """
        super().new_file(*args, **kwargs)
        
        # Additional security checks can be added here
        if self.file_name:
            # Validate filename
            try:
                validate_filename(self.file_name)
                validate_no_executable(type('MockFile', (), {'name': self.file_name})())
            except Exception as e:
                raise ValueError(f"Invalid file: {e}")
    
    def receive_data_chunk(self, raw_data, start):
        """
        Called for each chunk of data during upload.
        """
        # Check for malicious content patterns in chunks
        if self.is_suspicious_content(raw_data):
            raise ValueError("Suspicious file content detected")
        
        return super().receive_data_chunk(raw_data, start)
    
    def is_suspicious_content(self, data):
        """
        Check for suspicious patterns in file content.
        """
        # Convert bytes to string for pattern matching
        try:
            content = data.decode('utf-8', errors='ignore').lower()
        except:
            content = str(data).lower()
        
        # Suspicious patterns
        suspicious_patterns = [
            '<?php',
            '<script',
            'javascript:',
            'vbscript:',
            'onload=',
            'onerror=',
            'eval(',
            'exec(',
            'system(',
            'shell_exec(',
            'passthru(',
            'base64_decode(',
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content:
                return True
        
        return False


from django.core.exceptions import ValidationError

from io import BytesIO
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps

def compress_image(uploaded_file, max_width=1920, quality=85):
    """
    Compress and optimize user uploaded images for the web.
    Resizes large images, handles orientation, and applies compression.
    """
    try:
        # Open image
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        
        # Handle EXIF orientation (fixes rotation issues)
        img = ImageOps.exif_transpose(img)
        
        # Verify format
        img_format = img.format if img.format else 'JPEG'
        
        # Handle mode (Convert RGBA to RGB for JPEG)
        if img_format.upper() == 'JPEG' and img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize if too large (e.g. > 1920px)
        if img.width > max_width or img.height > max_width:
            img.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)
            
        # Prepare output
        output = BytesIO()
        save_args = {'format': img_format, 'optimize': True, 'quality': quality}
        
        if img_format.upper() == 'JPEG':
            save_args['progressive'] = True
            
        img.save(output, **save_args)
        output.seek(0)
        
        # Create new Django file object
        new_file = InMemoryUploadedFile(
            file=output,
            field_name=getattr(uploaded_file, 'field_name', 'image'),
            name=uploaded_file.name,
            content_type=uploaded_file.content_type,
            size=output.getbuffer().nbytes,
            charset=None
        )
        return new_file
        
    except Exception:
        # If compression fails, return original file
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        return uploaded_file

def clean_uploaded_file(uploaded_file):
    """
    Clean, validate, and optimize an uploaded file.
    """
    # Validate filename
    validate_filename(uploaded_file.name)
    validate_no_executable(uploaded_file)
    
    # Check file size
    # Default to 10MB if not specified in settings
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10485760)  # 10MB
    if uploaded_file.size > max_size:
        raise ValidationError(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
    
    # Additional content validation and compression for images
    content_type = getattr(uploaded_file, 'content_type', None)
    file_name = getattr(uploaded_file, 'name', '')

    is_image = (content_type and content_type.startswith('image/')) or \
               any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])

    if is_image:
        try:
            # Validate integrity
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            img.verify()
            
            # Apply compression/optimization
            uploaded_file = compress_image(uploaded_file)
            
        except Exception:
            # Don't raise error for existing files that might strictly check differently, 
            # but for uploads we want to be strict about validity.
            if hasattr(uploaded_file, 'content_type'):  # New upload
                raise ValidationError("Invalid image file or compression failed")
    
    return uploaded_file


def sanitize_svg(svg_content):
    """
    Sanitize SVG content to remove potentially dangerous elements.
    Note: This is a basic implementation. For production, consider using
    a dedicated library like bleach or defusedxml.
    """
    import re
    
    # Remove script tags and javascript
    svg_content = re.sub(r'<script[^>]*>.*?</script>', '', svg_content, flags=re.IGNORECASE | re.DOTALL)
    svg_content = re.sub(r'javascript:', '', svg_content, flags=re.IGNORECASE)
    svg_content = re.sub(r'vbscript:', '', svg_content, flags=re.IGNORECASE)
    svg_content = re.sub(r'on\w+\s*=', '', svg_content, flags=re.IGNORECASE)
    
    # Remove potentially dangerous elements
    dangerous_elements = ['script', 'object', 'embed', 'iframe', 'frame', 'frameset']
    for element in dangerous_elements:
        pattern = f'<{element}[^>]*>.*?</{element}>'
        svg_content = re.sub(pattern, '', svg_content, flags=re.IGNORECASE | re.DOTALL)
    
    return svg_content