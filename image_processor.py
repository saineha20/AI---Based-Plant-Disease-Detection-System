# backend/image_processor.py
"""
Image processing, validation, and AI tensor preparation for leaf disease analysis.
"""
import io
import numpy as np
from PIL import Image, ImageOps

class ImageProcessingError(Exception):
    """Exception raised during image decoding or processing."""
    pass

class LeafImageProcessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def load_image(self, file_source) -> Image.Image:
        """
        Loads and verifies a PIL Image from file stream, bytes, or path.
        Automatically applies EXIF orientation if present.
        """
        try:
            if isinstance(file_source, bytes):
                img = Image.open(io.BytesIO(file_source))
            elif hasattr(file_source, 'read'):
                file_source.seek(0)
                img = Image.open(file_source)
            elif isinstance(file_source, str):
                img = Image.open(file_source)
            else:
                raise ImageProcessingError("Unrecognized image source format.")

            # Apply EXIF rotation for smartphone photos taken at different angles
            img = ImageOps.exif_transpose(img)
            img.load()  # Verify image can be decoded fully
            return img
        except Exception as e:
            raise ImageProcessingError(f"Failed to decode image data: {str(e)}")

    def assess_quality(self, img: Image.Image) -> dict:
        """
        Performs clarity, exposure, and leaf coloration checks.
        """
        width, height = img.size
        warnings = []
        is_acceptable = True

        if width < 100 or height < 100:
            warnings.append("Image resolution is very low (under 100x100). Details may be missed.")
            is_acceptable = False

        # Convert to RGB array
        rgb_img = img.convert("RGB")
        arr = np.array(rgb_img, dtype=np.float32)

        # 1. Luminance & Exposure check
        gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        mean_brightness = float(np.mean(gray))

        if mean_brightness < 28.0:
            warnings.append("Photo is underexposed / too dark. Please take photo in natural daylight.")
            is_acceptable = False
        elif mean_brightness > 238.0:
            warnings.append("Photo is overexposed / too bright. Move away from direct glare.")
            is_acceptable = False

        # 2. Blur / Sharpness check using high-frequency gradient variance
        # (Discrete 2D Laplacian kernel approximation)
        pad_gray = np.pad(gray, 1, mode='edge')
        laplacian = (
            pad_gray[:-2, 1:-1] +
            pad_gray[2:, 1:-1] +
            pad_gray[1:-1, :-2] +
            pad_gray[1:-1, 2:] -
            4.0 * gray
        )
        blur_variance = float(np.var(laplacian))

        if blur_variance < 20.0:
            warnings.append("Photo appears blurry or out of focus. Hold the camera steady.")
            is_acceptable = False

        # 3. Leaf & Vegetation check (Excess Green Index: ExG = 2*G - R - B)
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]
        total_intensity = r + g + b + 1e-5
        
        # Calculate ratio of green-dominated vegetative pixels
        is_greenish = (g > r * 0.9) & (g > b * 0.9)
        # Also allow for yellow/brown disease blights
        is_yellow_brown = (r > 60) & (g > 50) & (b < 120) & (r >= g * 0.8)
        vegetative_ratio = float(np.mean(is_greenish | is_yellow_brown))

        if vegetative_ratio < 0.10:
            warnings.append("Image does not show significant plant foliage or leaf coloration.")
            # Note: We flag a warning, but don't hard-fail if lighting is unusual

        return {
            "acceptable": is_acceptable,
            "warnings": warnings,
            "metrics": {
                "width": width,
                "height": height,
                "brightness": round(mean_brightness, 2),
                "sharpness_score": round(blur_variance, 2),
                "vegetative_ratio": round(vegetative_ratio, 3)
            }
        }

    def preprocess_tensor(self, img: Image.Image, layout="NCHW") -> np.ndarray:
        """
        Converts PIL image to normalized float32 tensor:
        - Layout NCHW: [1, 3, 224, 224] (ONNX / PyTorch)
        - Layout NHWC: [1, 224, 224, 3] (TensorFlow)
        """
        rgb_img = img.convert("RGB")
        resized = rgb_img.resize(self.target_size, Image.Resampling.LANCZOS)
        
        arr = np.array(resized, dtype=np.float32) / 255.0  # Scale to [0, 1]
        
        # Normalize: (arr - mean) / std
        norm_arr = (arr - self.mean) / self.std

        if layout.upper() == "NCHW":
            # Transpose HWC to CHW: (224, 224, 3) -> (3, 224, 224)
            transposed = np.transpose(norm_arr, (2, 0, 1))
            batch = np.expand_dims(transposed, axis=0)  # [1, 3, 224, 224]
        else:
            batch = np.expand_dims(norm_arr, axis=0)    # [1, 224, 224, 3]

        return batch.astype(np.float32)

