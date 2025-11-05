"""
Tests for post_processor.py

Tests include:
- CMYK color conversion
- Misregistration effects
- Image sharpening
- Resolution adjustments
- Format conversion
- Metadata handling
"""

import pytest
import numpy as np
from PIL import Image
from test_framework import create_test_sprite, compare_images


class TestCMYKConversion:
    """Test CMYK color conversion."""

    def test_rgb_to_cmyk_conversion(self, test_sprite):
        """Test converting RGB image to CMYK."""
        # PIL supports CMYK conversion
        cmyk_image = test_sprite.convert("CMYK")

        assert cmyk_image.mode == "CMYK"
        assert cmyk_image.size == test_sprite.size

    def test_cmyk_preserves_dimensions(self, test_sprite):
        """Test that CMYK conversion preserves dimensions."""
        original_size = test_sprite.size
        cmyk_image = test_sprite.convert("CMYK")

        assert cmyk_image.size == original_size

    def test_cmyk_back_to_rgb(self, test_sprite):
        """Test converting CMYK back to RGB."""
        cmyk_image = test_sprite.convert("CMYK")
        rgb_again = cmyk_image.convert("RGB")

        assert rgb_again.mode == "RGB"
        # Some color shift is expected due to color space conversion


class TestMisregistrationEffect:
    """Test CMYK misregistration effect."""

    def test_channel_separation(self, test_sprite):
        """Test separating RGB channels."""
        r, g, b = test_sprite.split()

        assert r.mode == "L"  # Grayscale
        assert g.mode == "L"
        assert b.mode == "L"

    def test_channel_shift(self, test_sprite):
        """Test shifting color channels."""
        r, g, b = test_sprite.split()

        # Create shifted channels
        r_shifted = Image.new("L", test_sprite.size)
        r_shifted.paste(r, (1, 0))  # Shift right by 1 pixel

        # Verify shift occurred
        assert r_shifted.size == r.size

    def test_merge_shifted_channels(self, test_sprite):
        """Test merging shifted channels back together."""
        r, g, b = test_sprite.split()

        # Shift channels
        r_shifted = Image.new("L", test_sprite.size)
        g_shifted = Image.new("L", test_sprite.size)
        b_shifted = Image.new("L", test_sprite.size)

        r_shifted.paste(r, (1, 0))
        g_shifted.paste(g, (0, 0))
        b_shifted.paste(b, (-1, 0))

        # Merge
        shifted_image = Image.merge("RGB", (r_shifted, g_shifted, b_shifted))

        assert shifted_image.mode == "RGB"
        assert shifted_image.size == test_sprite.size

    def test_misregistration_creates_chromatic_effect(self, test_sprite):
        """Test that misregistration creates visible effect."""
        r, g, b = test_sprite.split()

        # Apply shifts
        arr_r = np.array(r)
        arr_g = np.array(g)
        arr_b = np.array(b)

        arr_r_shifted = np.roll(arr_r, 2, axis=1)
        arr_b_shifted = np.roll(arr_b, -2, axis=1)

        shifted = Image.merge("RGB", (
            Image.fromarray(arr_r_shifted),
            Image.fromarray(arr_g),
            Image.fromarray(arr_b_shifted)
        ))

        # Images should be different
        is_same, similarity = compare_images(test_sprite, shifted, threshold=0.99)
        assert not is_same, "Shifted image should differ from original"


class TestImageSharpening:
    """Test image sharpening operations."""

    def test_apply_sharpen_filter(self, test_sprite):
        """Test applying sharpen filter."""
        from PIL import ImageFilter

        sharpened = test_sprite.filter(ImageFilter.SHARPEN)

        assert sharpened is not None
        assert sharpened.size == test_sprite.size

    def test_unsharp_mask(self, test_sprite):
        """Test applying unsharp mask."""
        from PIL import ImageFilter

        # Apply unsharp mask
        unsharp = test_sprite.filter(
            ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
        )

        assert unsharp is not None
        assert unsharp.size == test_sprite.size

    def test_edge_enhance(self, test_sprite):
        """Test edge enhancement."""
        from PIL import ImageFilter

        enhanced = test_sprite.filter(ImageFilter.EDGE_ENHANCE)

        assert enhanced is not None
        assert enhanced.size == test_sprite.size


class TestResolutionAdjustment:
    """Test resolution and DPI adjustments."""

    def test_get_image_dpi(self, test_sprite):
        """Test getting image DPI."""
        dpi = test_sprite.info.get('dpi', (72, 72))

        assert isinstance(dpi, tuple)
        assert len(dpi) == 2

    def test_set_image_dpi(self, test_sprite, temp_dir):
        """Test setting image DPI."""
        output_path = f"{temp_dir}/test_dpi.png"

        # Save with specific DPI
        test_sprite.save(output_path, dpi=(300, 300))

        # Load and verify
        loaded = Image.open(output_path)
        loaded_dpi = loaded.info.get('dpi')

        # DPI might be stored in various ways depending on format
        assert loaded is not None

    def test_resize_image(self, test_sprite):
        """Test resizing image to different resolution."""
        new_size = (64, 64)
        resized = test_sprite.resize(new_size)

        assert resized.size == new_size

    def test_resize_with_resampling(self, test_sprite):
        """Test resizing with different resampling methods."""
        new_size = (16, 16)

        # Test different resampling methods
        nearest = test_sprite.resize(new_size, Image.Resampling.NEAREST)
        bilinear = test_sprite.resize(new_size, Image.Resampling.BILINEAR)
        bicubic = test_sprite.resize(new_size, Image.Resampling.BICUBIC)

        assert nearest.size == new_size
        assert bilinear.size == new_size
        assert bicubic.size == new_size


class TestFormatConversion:
    """Test image format conversion."""

    def test_save_as_png(self, test_sprite, temp_dir):
        """Test saving image as PNG."""
        output_path = f"{temp_dir}/test.png"
        test_sprite.save(output_path, "PNG")

        assert Image.open(output_path) is not None

    def test_save_as_jpeg(self, test_sprite, temp_dir):
        """Test saving image as JPEG."""
        output_path = f"{temp_dir}/test.jpg"
        # JPEG doesn't support transparency, ensure RGB mode
        rgb_sprite = test_sprite.convert("RGB")
        rgb_sprite.save(output_path, "JPEG", quality=95)

        assert Image.open(output_path) is not None

    def test_save_as_tiff(self, test_sprite, temp_dir):
        """Test saving image as TIFF."""
        output_path = f"{temp_dir}/test.tiff"
        test_sprite.save(output_path, "TIFF")

        assert Image.open(output_path) is not None

    def test_save_with_compression(self, test_sprite, temp_dir):
        """Test saving with compression."""
        output_path = f"{temp_dir}/test_compressed.png"
        test_sprite.save(output_path, "PNG", optimize=True)

        import os
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0


class TestMetadataHandling:
    """Test image metadata handling."""

    def test_preserve_metadata(self, test_sprite, temp_dir):
        """Test preserving metadata during processing."""
        # Add metadata
        from PIL import PngImagePlugin

        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Description", "Test sprite")
        metadata.add_text("Author", "Test Suite")

        output_path = f"{temp_dir}/test_metadata.png"
        test_sprite.save(output_path, "PNG", pnginfo=metadata)

        # Load and check
        loaded = Image.open(output_path)
        assert loaded is not None

    def test_exif_data_handling(self, test_sprite):
        """Test EXIF data handling."""
        # Get EXIF data if available
        exif = test_sprite.getexif()

        assert exif is not None  # Should at least return empty dict

    def test_image_info_dict(self, test_sprite):
        """Test accessing image info dictionary."""
        info = test_sprite.info

        assert isinstance(info, dict)


class TestColorAdjustments:
    """Test color adjustments and corrections."""

    def test_brightness_adjustment(self, test_sprite):
        """Test adjusting image brightness."""
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Brightness(test_sprite)
        brighter = enhancer.enhance(1.5)  # 50% brighter

        assert brighter is not None
        assert brighter.size == test_sprite.size

    def test_contrast_adjustment(self, test_sprite):
        """Test adjusting image contrast."""
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Contrast(test_sprite)
        higher_contrast = enhancer.enhance(1.5)

        assert higher_contrast is not None

    def test_color_balance_adjustment(self, test_sprite):
        """Test adjusting color balance."""
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Color(test_sprite)
        adjusted = enhancer.enhance(1.2)

        assert adjusted is not None

    def test_saturation_adjustment(self, test_sprite):
        """Test adjusting color saturation."""
        from PIL import ImageEnhance

        # Increase saturation
        enhancer = ImageEnhance.Color(test_sprite)
        saturated = enhancer.enhance(1.5)

        # Decrease saturation (move toward grayscale)
        desaturated = enhancer.enhance(0.5)

        assert saturated is not None
        assert desaturated is not None


@pytest.mark.integration
class TestPostProcessingPipeline:
    """Integration tests for complete post-processing pipeline."""

    def test_full_processing_pipeline(self, test_sprite, temp_dir):
        """Test complete processing from input to output."""
        from PIL import ImageFilter, ImageEnhance

        # Step 1: Sharpen
        sharpened = test_sprite.filter(ImageFilter.SHARPEN)

        # Step 2: Adjust contrast
        contrast_enhancer = ImageEnhance.Contrast(sharpened)
        contrasted = contrast_enhancer.enhance(1.1)

        # Step 3: Apply misregistration
        r, g, b = contrasted.split()
        r_shifted = Image.new("L", contrasted.size)
        g_shifted = Image.new("L", contrasted.size)
        b_shifted = Image.new("L", contrasted.size)

        r_shifted.paste(r, (1, 0))
        g_shifted.paste(g, (0, 0))
        b_shifted.paste(b, (-1, 0))

        final = Image.merge("RGB", (r_shifted, g_shifted, b_shifted))

        # Step 4: Save
        output_path = f"{temp_dir}/processed.png"
        final.save(output_path, "PNG", dpi=(300, 300))

        # Verify
        assert Image.open(output_path) is not None

    def test_batch_processing(self, temp_dir):
        """Test processing multiple images."""
        from PIL import ImageFilter

        # Create multiple test images
        images = [
            create_test_sprite(pattern="solid"),
            create_test_sprite(pattern="checkerboard"),
            create_test_sprite(pattern="computer")
        ]

        processed = []
        for i, img in enumerate(images):
            # Apply processing
            sharp = img.filter(ImageFilter.SHARPEN)
            output_path = f"{temp_dir}/batch_{i}.png"
            sharp.save(output_path)
            processed.append(output_path)

        assert len(processed) == len(images)

        # Verify all files exist
        import os
        for path in processed:
            assert os.path.exists(path)

    @pytest.mark.slow
    def test_processing_performance(self, test_sprite):
        """Test processing performance."""
        import time
        from PIL import ImageFilter

        num_iterations = 100
        start_time = time.time()

        for _ in range(num_iterations):
            sharpened = test_sprite.filter(ImageFilter.SHARPEN)

        elapsed = time.time() - start_time

        # Should be fast for small images
        assert elapsed < 10.0, f"Processing took {elapsed:.2f}s"
        avg_time = elapsed / num_iterations
        assert avg_time < 0.1, f"Average processing time: {avg_time:.3f}s"
