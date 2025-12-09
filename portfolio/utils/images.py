"""
Image optimization utilities for portfolio application.
Provides image compression, resizing, and format optimization.
"""

import os
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
import logging

logger = logging.getLogger('portfolio')

class ImageOptimizer:
    """
    Utility class for optimizing images uploaded to the portfolio.
    Handles compression, resizing, and format conversion.
    """
    
    # Image quality settings
    QUALITY_SETTINGS = {
        'high': 100,  # Maximum quality for profile images
        'medium': 75,
        'low': 65,
        'thumbnail': 60
    }
    
    # Maximum dimensions for different image types
    MAX_DIMENSIONS = {
        'profile': (500, 500),  # Exact size for profile images (increased for better quality)
        'project': (1200, 800),
        'blog': (1200, 800),
        'thumbnail': (300, 300)
    }
    
    # Supported formats
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP']
    
    @classmethod
    def optimize_profile_image(cls, image_file, target_size=500, quality='high'):
        """
        Optimize a profile image to exact square dimensions.

        Args:
            image_file: Django UploadedFile or file-like object
            target_size: Target width and height (default 500px)
            quality: Quality level for optimization

        Returns:
            ContentFile: Optimized square image file
        """
        try:
            with Image.open(image_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Auto-orient image based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Get original dimensions
                original_width, original_height = img.size
                
                # Make image square by cropping to center
                min_dimension = min(original_width, original_height)
                
                # Calculate crop box to center the square
                left = (original_width - min_dimension) // 2
                top = (original_height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                
                # Crop to square
                img = img.crop((left, top, right, bottom))
                
                # Resize to target size
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                # Get quality setting
                quality_value = cls.QUALITY_SETTINGS.get(quality, cls.QUALITY_SETTINGS['high'])
                
                # Save optimized image
                output = BytesIO()
                img.save(output, format='JPEG', quality=quality_value, optimize=True)
                output.seek(0)
                
                # Calculate compression ratio
                original_size = image_file.size if hasattr(image_file, 'size') else len(image_file.read())
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
                optimized_size = len(output.getvalue())
                compression_ratio = (1 - optimized_size / original_size) * 100
                
                logger.info(f'Profile image optimized: {original_width}x{original_height} -> {target_size}x{target_size}, '
                           f'{original_size} -> {optimized_size} bytes ({compression_ratio:.1f}% reduction)')
                
                # Create ContentFile
                optimized_file = ContentFile(output.getvalue())
                original_name = getattr(image_file, 'name', 'profile')
                name_without_ext = os.path.splitext(original_name)[0]
                optimized_file.name = f"{name_without_ext}_profile_{target_size}x{target_size}.jpg"
                
                return optimized_file
                
        except Exception as e:
            logger.error(f'Error optimizing profile image: {e}')
            return image_file

    @classmethod
    def optimize_image(cls, image_file, image_type='project', quality='medium', 
                      max_width=None, max_height=None, convert_to_webp=False):
        """
        Optimize an image file by compressing and resizing.
        
        Args:
            image_file: Django UploadedFile or file-like object
            image_type: Type of image ('profile', 'project', 'blog', 'thumbnail')
            quality: Quality level ('high', 'medium', 'low', 'thumbnail')
            max_width: Override maximum width
            max_height: Override maximum height
            convert_to_webp: Convert image to WebP format
            
        Returns:
            ContentFile: Optimized image file
        """
        try:
            # Open the image
            with Image.open(image_file) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Auto-orient image based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Get dimensions
                original_width, original_height = img.size
                
                # Determine target dimensions
                if max_width and max_height:
                    target_width, target_height = max_width, max_height
                else:
                    target_width, target_height = cls.MAX_DIMENSIONS.get(
                        image_type, cls.MAX_DIMENSIONS['project']
                    )
                
                # Calculate new dimensions maintaining aspect ratio
                if original_width > target_width or original_height > target_height:
                    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    logger.info(f'Resized image from {original_width}x{original_height} to {img.size}')
                
                # Determine output format
                output_format = 'WEBP' if convert_to_webp else 'JPEG'
                
                # Get quality setting
                quality_value = cls.QUALITY_SETTINGS.get(quality, cls.QUALITY_SETTINGS['medium'])
                
                # Save optimized image to BytesIO
                output = BytesIO()
                
                if output_format == 'WEBP':
                    img.save(output, format='WEBP', quality=quality_value, optimize=True)
                    file_extension = '.webp'
                else:
                    img.save(output, format='JPEG', quality=quality_value, optimize=True)
                    file_extension = '.jpg'
                
                output.seek(0)
                
                # Calculate compression ratio
                original_size = image_file.size if hasattr(image_file, 'size') else len(image_file.read())
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
                optimized_size = len(output.getvalue())
                compression_ratio = (1 - optimized_size / original_size) * 100
                
                logger.info(f'Image optimized: {original_size} -> {optimized_size} bytes '
                           f'({compression_ratio:.1f}% reduction)')
                
                # Create ContentFile with optimized image
                optimized_file = ContentFile(output.getvalue())
                
                # Generate filename
                original_name = getattr(image_file, 'name', 'image')
                name_without_ext = os.path.splitext(original_name)[0]
                optimized_file.name = f"{name_without_ext}_optimized{file_extension}"
                
                return optimized_file
                
        except Exception as e:
            logger.error(f'Error optimizing image: {e}')
            # Return original file if optimization fails
            return image_file
    
    @classmethod
    def create_thumbnail(cls, image_file, size=(300, 300), quality='thumbnail'):
        """
        Create a thumbnail version of an image.
        
        Args:
            image_file: Django UploadedFile or file-like object
            size: Tuple of (width, height) for thumbnail
            quality: Quality level for thumbnail
            
        Returns:
            ContentFile: Thumbnail image file
        """
        return cls.optimize_image(
            image_file, 
            image_type='thumbnail',
            quality=quality,
            max_width=size[0],
            max_height=size[1]
        )
    
    @classmethod
    def get_image_info(cls, image_file):
        """
        Get information about an image file.
        
        Args:
            image_file: Image file to analyze
            
        Returns:
            dict: Image information including dimensions, format, size
        """
        try:
            with Image.open(image_file) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size': image_file.size if hasattr(image_file, 'size') else None
                }
        except Exception as e:
            logger.error(f'Error getting image info: {e}')
            return {}
    
    @classmethod
    def should_optimize(cls, image_file, max_size_mb=2):
        """
        Determine if an image should be optimized based on size and dimensions.
        
        Args:
            image_file: Image file to check
            max_size_mb: Maximum file size in MB before optimization
            
        Returns:
            bool: True if image should be optimized
        """
        try:
            # Check file size
            file_size_mb = image_file.size / (1024 * 1024) if hasattr(image_file, 'size') else 0
            if file_size_mb > max_size_mb:
                return True
            
            # Check dimensions
            info = cls.get_image_info(image_file)
            if info.get('width', 0) > 1200 or info.get('height', 0) > 800:
                return True
            
            return False
            
        except Exception:
            return False


def optimize_uploaded_image(image_field, image_type='project', quality='medium'):
    """
    Convenience function to optimize an image field during model save.
    
    Args:
        image_field: Django ImageField instance
        image_type: Type of image for optimization settings
        quality: Quality level for optimization
        
    Returns:
        bool: True if image was optimized, False otherwise
    """
    if not image_field or not image_field.file:
        return False
    
    try:
        # Get the original file
        original_file = image_field.file
        original_file.seek(0)
        
        # Use specific optimization for profile images
        if image_type == 'profile':
            optimized_file = ImageOptimizer.optimize_profile_image(
                original_file,
                target_size=500,
                quality=quality
            )
        else:
            # Check if optimization is needed for other image types
            if not ImageOptimizer.should_optimize(original_file):
                return False
            
            optimized_file = ImageOptimizer.optimize_image(
                original_file, 
                image_type=image_type, 
                quality=quality
            )
        
        # Replace the field content
        image_field.save(
            optimized_file.name,
            optimized_file,
            save=False  # Don't save the model yet
        )
        
        logger.info(f'Optimized {image_type} image: {optimized_file.name}')
        return True
        
    except Exception as e:
        logger.error(f'Error in optimize_uploaded_image: {e}')
        return False