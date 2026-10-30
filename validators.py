# backend/validators.py
"""
File validation utilities for secure leaf image uploads.
"""
import os
import re

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/pjpeg'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_FILE_SIZE_BYTES = 1024  # 1 KB

MAGIC_HEADERS = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'RIFF': 'webp'
}

class ValidationError(Exception):
    """Custom validation exception."""
    pass

def sanitize_filename(filename: str) -> str:
    """Removes unsafe characters and path navigation tokens."""
    if not filename:
        return "leaf_upload.jpg"
    # Strip directory paths
    base = os.path.basename(filename)
    # Remove all characters except alphanumeric, underscore, hyphen, and period
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    # Avoid double dots
    sanitized = re.sub(r'\.{2,}', '.', sanitized)
    if not sanitized or sanitized.startswith('.'):
        sanitized = f"leaf_{sanitized}"
    return sanitized[:100]

def validate_image_file(file_storage) -> dict:
    """
    Validates uploaded file for presence, size, extension, and binary header.
    Returns: dict with status and details, or raises ValidationError.
    """
    if file_storage is None or not hasattr(file_storage, 'filename') or not file_storage.filename:
        raise ValidationError("No image file provided in the upload request.")

    filename = file_storage.filename.strip()
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file extension '.{ext}'. Supported image formats are JPG, JPEG, PNG, and WebP."
        )

    # Read binary stream to inspect size and magic bytes
    stream = file_storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)

    if size < MIN_FILE_SIZE_BYTES:
        raise ValidationError(f"File size ({size} bytes) is too small to be a valid leaf photo.")

    if size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise ValidationError(f"File size ({actual_mb:.2f} MB) exceeds maximum allowed limit ({max_mb:.0f} MB).")

    # Header check
    header = stream.read(32)
    stream.seek(0)

    is_valid_magic = False
    for magic, fmt in MAGIC_HEADERS.items():
        if header.startswith(magic):
            is_valid_magic = True
            break
        # Special check for WEBP: RIFF...WEBP
        if magic == b'RIFF' and len(header) >= 12 and header.startswith(b'RIFF') and header[8:12] == b'WEBP':
            is_valid_magic = True
            break

    if not is_valid_magic:
        raise ValidationError("File content does not match a valid JPEG, PNG, or WebP image signature.")

    return {
        "valid": True,
        "sanitized_filename": sanitize_filename(filename),
        "extension": ext,
        "size_bytes": size
    }

