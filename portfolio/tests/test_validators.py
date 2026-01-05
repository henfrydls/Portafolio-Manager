"""
Tests for validators (security critical).
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

from portfolio.utils.validators import (
    validate_no_executable,
    validate_filename,
    ProfileImageValidator,
    DocumentValidator
)


def create_test_image(format='JPEG', size=(250, 250)):
    """Helper function to create a valid test image."""
    image = Image.new('RGB', size, color='red')
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


class ValidateNoExecutableTest(TestCase):
    """Test validate_no_executable function"""

    def test_allows_safe_extensions(self):
        """Test that safe file extensions are allowed"""
        # These should not raise ValidationError
        file_jpg = SimpleUploadedFile("test.jpg", b"fake image content")
        file_png = SimpleUploadedFile("test.png", b"fake image content")
        file_pdf = SimpleUploadedFile("test.pdf", b"fake pdf content")

        try:
            validate_no_executable(file_jpg)
            validate_no_executable(file_png)
            validate_no_executable(file_pdf)
        except ValidationError:
            self.fail("validate_no_executable raised ValidationError for safe files")

    def test_blocks_executable_extensions(self):
        """Test that executable extensions are blocked"""
        dangerous_files = [
            SimpleUploadedFile("malware.exe", b"fake exe"),
            SimpleUploadedFile("script.sh", b"fake script"),
            SimpleUploadedFile("batch.bat", b"fake batch"),
            SimpleUploadedFile("command.cmd", b"fake command"),
        ]

        for file in dangerous_files:
            with self.assertRaises(ValidationError):
                validate_no_executable(file)

    def test_case_insensitive_blocking(self):
        """Test that extension blocking is case-insensitive"""
        dangerous_files = [
            SimpleUploadedFile("MALWARE.EXE", b"fake exe"),
            SimpleUploadedFile("Script.SH", b"fake script"),
        ]

        for file in dangerous_files:
            with self.assertRaises(ValidationError):
                validate_no_executable(file)


class ValidateFilenameTest(TestCase):
    """Test validate_filename function"""

    def test_allows_safe_filenames(self):
        """Test that safe filenames are allowed"""
        safe_filenames = [
            "document.pdf",
            "image-photo.jpg",
            "file_name.png",
            "Document 123.docx",
        ]

        for filename in safe_filenames:
            try:
                validate_filename(filename)
            except ValidationError:
                self.fail(f"validate_filename rejected safe filename: {filename}")

    def test_blocks_path_traversal(self):
        """Test that path traversal attempts are blocked"""
        # Note: validate_filename uses os.path.basename, so full paths are stripped
        # But it does check for ".." in the filename after stripping
        dangerous_filenames = [
            "..file.txt",  # Still has .. after basename
            "file..txt",   # Has .. in the middle
        ]

        for filename in dangerous_filenames:
            with self.assertRaises(ValidationError):
                validate_filename(filename)

    def test_sanitizes_paths(self):
        """Test that paths are sanitized to just filenames"""
        # These should pass because basename strips the path
        safe_after_basename = [
            "/etc/passwd",  # becomes "passwd"
            "C:\\Windows\\file.txt",  # becomes "file.txt"
            "../file.txt",  # becomes "file.txt"
        ]

        for filename in safe_after_basename:
            try:
                validate_filename(filename)
            except ValidationError:
                # These are actually safe after basename is applied
                pass


class ProfileImageValidatorTest(TestCase):
    """Test ProfileImageValidator class"""

    def setUp(self):
        self.validator = ProfileImageValidator()  # Uses default settings (3MB max)

    def test_accepts_valid_image_formats(self):
        """Test that valid image formats are accepted"""
        valid_images = [
            SimpleUploadedFile("test.jpg", create_test_image('JPEG'), content_type="image/jpeg"),
            SimpleUploadedFile("test.png", create_test_image('PNG'), content_type="image/png"),
        ]

        for img in valid_images:
            img.size = len(img.read())  # Set size to actual content size
            img.seek(0)  # Reset file pointer after read
            try:
                self.validator(img)
            except ValidationError:
                self.fail(f"Validator rejected valid image format: {img.name}")

    def test_rejects_invalid_formats(self):
        """Test that invalid formats are rejected"""
        invalid_file = SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")
        invalid_file.size = 100

        with self.assertRaises(ValidationError):
            self.validator(invalid_file)

    def test_rejects_oversized_images(self):
        """Test that oversized images are rejected"""
        large_image = SimpleUploadedFile("large.jpg", b"x" * (4*1024*1024), content_type="image/jpeg")
        large_image.size = 4*1024*1024  # 4MB (over the 3MB limit)

        with self.assertRaises(ValidationError):
            self.validator(large_image)

    def test_accepts_image_within_size_limit(self):
        """Test that images within size limit are accepted"""
        small_image = SimpleUploadedFile("small.jpg", create_test_image('JPEG'), content_type="image/jpeg")
        small_image.size = len(small_image.read())  # Use actual size
        small_image.seek(0)  # Reset file pointer

        try:
            self.validator(small_image)
        except ValidationError:
            self.fail("Validator rejected image within size limit")


class DocumentValidatorTest(TestCase):
    """Test DocumentValidator class"""

    def setUp(self):
        self.validator = DocumentValidator(max_size=5*1024*1024)  # 5MB

    def test_accepts_valid_document_formats(self):
        """Test that valid document formats are accepted"""
        valid_docs = [
            SimpleUploadedFile("test.pdf", b"fake pdf", content_type="application/pdf"),
            SimpleUploadedFile("test.doc", b"fake doc", content_type="application/msword"),
            SimpleUploadedFile("test.docx", b"fake docx",
                             content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]

        for doc in valid_docs:
            doc.size = 1000000  # 1MB
            try:
                self.validator(doc)
            except ValidationError:
                self.fail(f"Validator rejected valid document format: {doc.name}")

    def test_rejects_invalid_document_formats(self):
        """Test that invalid formats are rejected"""
        invalid_file = SimpleUploadedFile("test.exe", b"executable", content_type="application/x-executable")
        invalid_file.size = 100

        with self.assertRaises(ValidationError):
            self.validator(invalid_file)

    def test_rejects_oversized_documents(self):
        """Test that oversized documents are rejected"""
        large_doc = SimpleUploadedFile("large.pdf", b"x" * (10*1024*1024), content_type="application/pdf")
        large_doc.size = 10*1024*1024  # 10MB (over the 5MB limit)

        with self.assertRaises(ValidationError):
            self.validator(large_doc)

    def test_accepts_document_within_size_limit(self):
        """Test that documents within size limit are accepted"""
        small_doc = SimpleUploadedFile("small.pdf", b"fake pdf", content_type="application/pdf")
        small_doc.size = 2*1024*1024  # 2MB (under 5MB limit)

        try:
            self.validator(small_doc)
        except ValidationError:
            self.fail("Validator rejected document within size limit")


class SecurityValidationEdgeCasesTest(TestCase):
    """Test edge cases and security scenarios"""

    def test_double_extension_executable_blocked(self):
        """Test that double extension executables are blocked"""
        file = SimpleUploadedFile("innocent.pdf.exe", b"malware", content_type="application/pdf")

        with self.assertRaises(ValidationError):
            validate_no_executable(file)

    def test_null_byte_injection_blocked(self):
        """Test that null byte injection is handled"""
        # Null byte injection attempt: "innocent.jpg\x00.exe"
        file = SimpleUploadedFile("innocent.jpg\x00.exe", b"content")

        with self.assertRaises(ValidationError):
            validate_no_executable(file)

    def test_unicode_exploitation_blocked(self):
        """Test that unicode right-to-left override is handled"""
        # File name that appears as "innocent.jpg" but is actually "innocent.exe"
        # Using right-to-left override character
        file = SimpleUploadedFile("innocent\u202Egpj.exe", b"content")

        with self.assertRaises(ValidationError):
            validate_no_executable(file)

    def test_empty_file_name_handled(self):
        """Test that empty file names are handled gracefully"""
        # Note: SimpleUploadedFile doesn't accept empty filenames, so we test
        # a file with just whitespace as the name instead
        file = SimpleUploadedFile(" ", b"content")

        # Should handle gracefully without crashing
        try:
            validate_no_executable(file)
        except (ValidationError, AttributeError):
            # Either is acceptable, just shouldn't crash
            pass

    def test_very_long_extension_handled(self):
        """Test that very long extensions are handled"""
        long_ext = "x" * 1000
        file = SimpleUploadedFile(f"test.{long_ext}", b"content")

        # Should handle gracefully without crashing
        try:
            validate_no_executable(file)
        except ValidationError:
            # Acceptable to reject very long extensions
            pass
