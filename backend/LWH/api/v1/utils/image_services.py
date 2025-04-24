import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _

def validate_image(image, max_size=10*1024*1024, formats=None):
    """
    Validate image by size and format

    Args:
        image: Uploaded image object
        max_size: Maximum file size in bytes (default 10MB)
        formats: List of allowed formats (default None - all formats)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not image:
        return False, _("Image not provided")

    # Check size
    if image.size > max_size:
        return False, _("Image size exceeds the allowed limit")

    # Check format
    if formats:
        img_extension = os.path.splitext(image.name)[1].lower()
        if img_extension not in formats:
            return False, _("Image format not supported")

    return True, None

def process_image(image, quality=85, max_width=2000, max_height=2000, format=None):
    """
    Process image - resize and compress

    Args:
        image: Uploaded image object
        quality: Compression quality (1-100)
        max_width: Maximum width
        max_height: Maximum height
        format: Format for conversion (None - keep original)

    Returns:
        ContentFile: Processed image
    """
    img = Image.open(image)

    # Save original format
    original_format = img.format
    if not format:
        format = original_format

    # Resize if needed
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.LANCZOS)

    # Save with optimization
    img_io = BytesIO()
    img.save(img_io, format=format, quality=quality, optimize=True)

    # Create new file
    img_file = ContentFile(img_io.getvalue())
    return img_file

def generate_unique_filename(instance, filename):
    """
    Generate unique filename

    Args:
        instance: Model instance
        filename: Original filename

    Returns:
        str: Unique filename
    """
    # Get file extension
    ext = filename.split('.')[-1]

    # Generate unique name
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    # Get save path
    if hasattr(instance, 'get_upload_path'):
        return os.path.join(instance.get_upload_path(), unique_name)

    # Default
    return unique_name

def create_thumbnail(image, size=(300, 300), quality=85, format=None):
    """
    Create image thumbnail

    Args:
        image: Uploaded image object
        size: Tuple of (width, height)
        quality: Compression quality (1-100)
        format: Format for conversion (None - keep original)

    Returns:
        ContentFile: Thumbnail image
    """
    img = Image.open(image)

    # Save original format
    original_format = img.format
    if not format:
        format = original_format

    # Create thumbnail
    img.thumbnail(size, Image.LANCZOS)

    # Save
    thumb_io = BytesIO()
    img.save(thumb_io, format=format, quality=quality, optimize=True)

    # Create new file
    thumb_file = ContentFile(thumb_io.getvalue())
    return thumb_file

def get_image_metadata(image):
    """
    Get image metadata

    Args:
        image: Uploaded image object

    Returns:
        dict: Image metadata
    """
    metadata = {
        'filename': image.name,
        'size': image.size,
    }

    # Additional metadata from EXIF
    try:
        img = Image.open(image)
        metadata['format'] = img.format
        metadata['mode'] = img.mode
        metadata['width'] = img.width
        metadata['height'] = img.height

        # Get EXIF data if available
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            metadata['exif'] = exif
    except Exception as e:
        metadata['error'] = str(e)

    return metadata

def update_image_order(model_class, instance_id, image_id, new_order):
    """
    Update image order

    Args:
        model_class: Image model class
        instance_id: ID of the object to which the images belong
        image_id: ID of the image to update
        new_order: New order

    Returns:
        bool: Operation result
    """
    try:
        # Find the image
        image = model_class.objects.get(id=image_id)

        # Update order
        image.order = new_order
        image.save(update_fields=['order'])

        return True
    except model_class.DoesNotExist:
        return False


def get_thumbnail_url(image_url, size='medium'):
    """
    Generate a thumbnail URL for a given image URL

    Args:
        image_url: Original image URL
        size: Thumbnail size ('small', 'medium', 'large')

    Returns:
        str: Thumbnail URL
    """
    if not image_url:
        return None

    # Split the URL into parts
    path_parts = image_url.split('/')
    filename = path_parts[-1]
    base_path = '/'.join(path_parts[:-1])

    # Split filename into name and extension
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) < 2:
        return image_url  # Not a valid filename with extension

    name, ext = name_parts

    # Define size suffix
    size_suffix = {
        'small': '_thumb_sm',
        'medium': '_thumb_md',
        'large': '_thumb_lg'
    }.get(size, '_thumb')

    # Create new filename with size suffix
    thumb_filename = f"{name}{size_suffix}.{ext}"

    # Create and return thumbnail URL
    return f"{base_path}/thumbnails/{thumb_filename}"

def generate_thumbnails(image, filename, sizes=None):
    """
    Generate thumbnails for an image

    Args:
        image: Source image
        filename: Original filename
        sizes: Dict of size names and dimensions

    Returns:
        dict: Dict of thumbnail filenames by size
    """
    if sizes is None:
        sizes = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600)
        }

    # Get file extension
    ext = os.path.splitext(filename)[1].lower()

    # Generate thumbnails
    thumbnails = {}
    img = Image.open(image)

    # Create thumbnails directory if it doesn't exist
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True)

    for size_name, dimensions in sizes.items():
        # Create a copy of the image
        thumb = img.copy()
        thumb.thumbnail(dimensions, Image.LANCZOS)

        # Generate thumbnail filename
        basename = os.path.basename(filename)
        name, ext = os.path.splitext(basename)
        thumb_filename = f"{name}_thumb_{size_name}{ext}"

        # Save thumbnail
        thumb_path = os.path.join(thumbnails_dir, thumb_filename)
        thumb.save(thumb_path, quality=85, optimize=True)

        # Store thumbnail filename
        thumbnails[size_name] = os.path.join('thumbnails', thumb_filename)

    return thumbnails
