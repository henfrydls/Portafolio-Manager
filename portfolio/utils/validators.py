"""
Custom validators for file uploads and form validation.
"""
import os
import magic
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.deconstruct import deconstructible
from PIL import Image


@deconstructible
class FileValidator:
    """
    Validator for file uploads with size and type restrictions.
    """
    def __init__(self, max_size=None, allowed_extensions=None, allowed_mimetypes=None):
        self.max_size = max_size or 5 * 1024 * 1024  # 5MB default
        self.allowed_extensions = allowed_extensions or []
        self.allowed_mimetypes = allowed_mimetypes or []
    
    def __call__(self, file):
        # Skip validation if file is None or empty
        if not file:
            return

        # Check if this is an existing file that doesn't need validation
        if hasattr(file, 'url') and not hasattr(file, 'content_type'):
            return

        # Check file size
        if hasattr(file, 'size') and file.size > self.max_size:
            raise ValidationError(
                f'El archivo es demasiado grande. Tamaño máximo permitido: {self.max_size // (1024*1024)}MB'
            )

        # Check file extension
        if self.allowed_extensions and hasattr(file, 'name'):
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(self.allowed_extensions)}'
                )

        # Check MIME type using python-magic for security (only for new uploads)
        if self.allowed_mimetypes and hasattr(file, 'seek') and hasattr(file, 'read'):
            try:
                # Read first 1024 bytes to determine MIME type
                file.seek(0)
                file_header = file.read(1024)
                file.seek(0)

                mime_type = magic.from_buffer(file_header, mime=True)

                if mime_type not in self.allowed_mimetypes:
                    raise ValidationError(
                        f'Tipo de archivo no válido. Tipos permitidos: {", ".join(self.allowed_mimetypes)}'
                    )
            except Exception:
                # If magic fails, fall back to extension check
                if not self.allowed_extensions:
                    raise ValidationError('No se pudo verificar el tipo de archivo')


@deconstructible
class ImageValidator(FileValidator):
    """
    Specialized validator for image files.
    """
    def __init__(self, max_size=None, max_width=None, max_height=None, min_width=None, min_height=None):
        # Default image settings
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        allowed_mimetypes = [
            'image/jpeg', 
            'image/png', 
            'image/gif', 
            'image/webp'
        ]
        
        super().__init__(
            max_size=max_size or 2 * 1024 * 1024,  # 2MB for images
            allowed_extensions=allowed_extensions,
            allowed_mimetypes=allowed_mimetypes
        )
        
        self.max_width = max_width
        self.max_height = max_height
        self.min_width = min_width
        self.min_height = min_height
    
    def __call__(self, file):
        # Skip validation if file is None or empty (for editing existing objects)
        if not file:
            return

        # Check if this is an existing file that doesn't need validation
        # (e.g., during form editing without file change)
        if hasattr(file, 'url') and not hasattr(file, 'content_type'):
            # This is likely an existing file, skip validation
            return

        # Run base validation first
        super().__call__(file)

        # Additional image validation
        try:
            # Only seek if the file supports it (new uploads)
            if hasattr(file, 'seek'):
                file.seek(0)

            with Image.open(file) as img:
                width, height = img.size

                # Check dimensions
                if self.max_width and width > self.max_width:
                    raise ValidationError(f'Ancho máximo permitido: {self.max_width}px')

                if self.max_height and height > self.max_height:
                    raise ValidationError(f'Alto máximo permitido: {self.max_height}px')

                if self.min_width and width < self.min_width:
                    raise ValidationError(f'Ancho mínimo requerido: {self.min_width}px')

                if self.min_height and height < self.min_height:
                    raise ValidationError(f'Alto mínimo requerido: {self.min_height}px')

            # Only seek back if the file supports it
            if hasattr(file, 'seek'):
                file.seek(0)

        except Exception as e:
            # Only raise validation error for new uploads
            if hasattr(file, 'content_type') or hasattr(file, 'seek'):
                raise ValidationError('El archivo no es una imagen válida')


@deconstructible
class DocumentValidator(FileValidator):
    """
    Specialized validator for document files (PDF, DOC, etc.).
    """
    def __init__(self, max_size=None):
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        allowed_mimetypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        
        super().__init__(
            max_size=max_size or 10 * 1024 * 1024,  # 10MB for documents
            allowed_extensions=allowed_extensions,
            allowed_mimetypes=allowed_mimetypes
        )


def validate_no_executable(file):
    """
    Validator to prevent executable file uploads.
    """
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
        '.sh', '.py', '.php', '.asp', '.aspx', '.jsp', '.pl', '.cgi'
    ]
    
    ext = os.path.splitext(file.name)[1].lower()
    if ext in dangerous_extensions:
        raise ValidationError('No se permiten archivos ejecutables por seguridad')


def validate_filename(filename):
    """
    Validate filename for security (no path traversal, etc.).
    """
    # Get just the filename without path (Django should handle this but let's be safe)
    filename = os.path.basename(filename)

    # Check for path traversal attempts
    if '..' in filename:
        raise ValidationError('Nombre de archivo no válido')

    # Check for null bytes
    if '\x00' in filename:
        raise ValidationError('Nombre de archivo contiene caracteres no válidos')

    # Check length
    if len(filename) > 255:
        raise ValidationError('Nombre de archivo demasiado largo')

    # Check for empty filename
    if not filename or filename == '.':
        raise ValidationError('Nombre de archivo no válido')

    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        raise ValidationError('Nombre de archivo reservado del sistema')


@deconstructible
class ProfileImageValidator(ImageValidator):
    """
    Specialized validator for profile images that enforces square aspect ratio.
    """
    def __init__(self):
        super().__init__(
            max_size=3 * 1024 * 1024,  # 3MB
            max_width=2000,
            max_height=2000,
            min_width=200,
            min_height=200
        )
    
    def __call__(self, file):
        # Skip validation if file is None or empty
        if not file:
            return

        # Check if this is an existing file that doesn't need validation
        if hasattr(file, 'url') and not hasattr(file, 'content_type'):
            return

        # Run base validation first
        super().__call__(file)

        # Additional profile image validation - check for square aspect ratio
        try:
            if hasattr(file, 'seek'):
                file.seek(0)

            with Image.open(file) as img:
                width, height = img.size
                
                # Calculate aspect ratio tolerance (allow 5% difference)
                aspect_ratio = width / height
                tolerance = 0.05
                
                if not (1 - tolerance <= aspect_ratio <= 1 + tolerance):
                    raise ValidationError(
                        'La imagen de perfil debe ser cuadrada (misma anchura y altura). '
                        f'Dimensiones actuales: {width}x{height}px. '
                        'Recomendación: Use una imagen de 250x250px o mayor con proporción 1:1.'
                    )

            if hasattr(file, 'seek'):
                file.seek(0)

        except ValidationError:
            raise
        except Exception as e:
            if hasattr(file, 'content_type') or hasattr(file, 'seek'):
                raise ValidationError('El archivo no es una imagen válida')


# Pre-configured validators for common use cases
profile_image_validator = ProfileImageValidator()

project_image_validator = ImageValidator(
    max_size=3 * 1024 * 1024,  # 3MB
    max_width=1920,
    max_height=1080,
    min_width=200,
    min_height=150
)

blog_image_validator = ImageValidator(
    max_size=2 * 1024 * 1024,  # 2MB
    max_width=1200,
    max_height=800,
    min_width=300,
    min_height=200
)

resume_pdf_validator = DocumentValidator(
    max_size=5 * 1024 * 1024  # 5MB
)