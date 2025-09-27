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


def clean_uploaded_file(uploaded_file):
    """
    Clean and validate an uploaded file.
    """
    # Validate filename
    validate_filename(uploaded_file.name)
    validate_no_executable(uploaded_file)
    
    # Check file size
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 5242880)  # 5MB
    if uploaded_file.size > max_size:
        raise ValueError(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
    
    # Additional content validation for images
    # Check if it's an uploaded file with content_type or if it's an existing file that looks like an image
    content_type = getattr(uploaded_file, 'content_type', None)
    file_name = getattr(uploaded_file, 'name', '')

    is_image = (content_type and content_type.startswith('image/')) or \
               any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])

    if is_image:
        try:
            from PIL import Image
            # Only seek if the file has the seek method (uploaded files)
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
            with Image.open(uploaded_file) as img:
                # Verify it's actually an image
                img.verify()
            # Only seek if the file has the seek method
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
        except Exception:
            # Don't raise error for existing files, they've already been validated
            if hasattr(uploaded_file, 'content_type'):  # This means it's a new upload
                raise ValueError("Invalid image file")
    
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