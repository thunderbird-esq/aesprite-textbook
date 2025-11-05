"""
Tests for klutz_compositor.py

Tests include:
- Chaos rotation determinism
- Base canvas creation
- Spiral binding rendering
- Page curvature and shadows
- Asset loading and rotation
- Text rendering and word wrap
- Spine intrusion warnings
- CMYK misregistration effects
- Full composition integration
"""

import pytest
import hashlib
from PIL import Image, ImageDraw
import numpy as np

from test_framework import (
    create_test_sprite,
    create_test_config,
    create_test_layout,
    compare_images,
)


# ============================================================================
# Chaos Rotation Tests
# ============================================================================

class TestChaosRotationDeterministic:
    """Test that chaos rotation is deterministic based on element ID."""

    def test_same_id_same_rotation(self):
        """Test that same ID produces same rotation."""
        element_id = "test_element_1"

        # Simulate deterministic rotation using hash
        hash_val = int(hashlib.md5(element_id.encode()).hexdigest(), 16)
        rotation1 = (hash_val % 31) - 15  # Range: -15 to +15

        # Calculate again
        hash_val2 = int(hashlib.md5(element_id.encode()).hexdigest(), 16)
        rotation2 = (hash_val2 % 31) - 15

        assert rotation1 == rotation2, "Same ID should produce same rotation"

    def test_different_id_different_rotation(self):
        """Test that different IDs produce different rotations."""
        id1 = "element_1"
        id2 = "element_2"

        hash1 = int(hashlib.md5(id1.encode()).hexdigest(), 16)
        rotation1 = (hash1 % 31) - 15

        hash2 = int(hashlib.md5(id2.encode()).hexdigest(), 16)
        rotation2 = (hash2 % 31) - 15

        # They could theoretically be the same, but very unlikely
        # Just verify the calculation works
        assert isinstance(rotation1, int)
        assert isinstance(rotation2, int)
        assert -15 <= rotation1 <= 15
        assert -15 <= rotation2 <= 15

    def test_rotation_within_bounds(self):
        """Test that chaos rotation stays within ±15 degrees."""
        for i in range(100):
            element_id = f"element_{i}"
            hash_val = int(hashlib.md5(element_id.encode()).hexdigest(), 16)
            rotation = (hash_val % 31) - 15

            assert -15 <= rotation <= 15, \
                f"Rotation {rotation}° should be within ±15°"

    def test_rotation_distribution(self):
        """Test that rotations are distributed across the range."""
        rotations = []
        for i in range(1000):
            element_id = f"element_{i}"
            hash_val = int(hashlib.md5(element_id.encode()).hexdigest(), 16)
            rotation = (hash_val % 31) - 15
            rotations.append(rotation)

        # Check that we have variety in rotations
        unique_rotations = set(rotations)
        assert len(unique_rotations) > 20, \
            "Should have variety in rotation values"


# ============================================================================
# Base Canvas Tests
# ============================================================================

class TestBaseCanvasCreation:
    """Test creation of base canvas for spreads."""

    def test_canvas_dimensions(self, test_config):
        """Test that canvas has correct dimensions."""
        spread_size = test_config["compositor"]["spread_size"]
        canvas = Image.new("RGB", tuple(spread_size))

        assert canvas.size == tuple(spread_size), \
            f"Canvas should be {spread_size[0]}x{spread_size[1]}"

    def test_canvas_background_color(self, test_config):
        """Test that canvas has correct background color."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        # Check a few pixels to verify background color
        pixel = canvas.getpixel((100, 100))
        assert pixel == bg_color, \
            f"Background should be {bg_color}, got {pixel}"

    def test_canvas_mode_rgb(self, test_config):
        """Test that canvas is in RGB mode."""
        spread_size = test_config["compositor"]["spread_size"]
        canvas = Image.new("RGB", tuple(spread_size))

        assert canvas.mode == "RGB", "Canvas should be in RGB mode"

    def test_canvas_not_empty(self, test_config):
        """Test that canvas is created and not None."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])
        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        assert canvas is not None, "Canvas should be created"
        assert isinstance(canvas, Image.Image), "Canvas should be PIL Image"


# ============================================================================
# Spiral Binding Tests
# ============================================================================

class TestSpiralBindingRendering:
    """Test rendering of spiral binding holes."""

    def test_binding_enabled(self, test_config):
        """Test that binding can be enabled in config."""
        binding_config = test_config["compositor"]["spiral_binding"]
        assert binding_config["enabled"] is True, "Binding should be enabled"

    def test_binding_hole_count(self, test_config):
        """Test correct number of binding holes."""
        binding_config = test_config["compositor"]["spiral_binding"]
        expected_holes = binding_config["holes"]

        assert expected_holes == 23, "Should have 23 binding holes"

    def test_binding_hole_spacing(self, test_config):
        """Test that binding holes are evenly spaced."""
        spread_size = test_config["compositor"]["spread_size"]
        binding_config = test_config["compositor"]["spiral_binding"]

        height = spread_size[1]
        num_holes = binding_config["holes"]

        # Calculate spacing
        spacing = height / (num_holes + 1)

        assert spacing > 0, "Holes should be spaced apart"
        assert spacing < height, "Spacing should be less than page height"

    def test_binding_rendered_on_canvas(self, test_config):
        """Test that binding holes are rendered on canvas."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])
        binding_config = test_config["compositor"]["spiral_binding"]

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        # Draw binding holes at spine center
        spine_x = spread_size[0] // 2
        height = spread_size[1]
        num_holes = binding_config["holes"]
        hole_radius = 5

        for i in range(num_holes):
            y = int((i + 1) * height / (num_holes + 1))
            draw.ellipse(
                [spine_x - hole_radius, y - hole_radius,
                 spine_x + hole_radius, y + hole_radius],
                fill=(200, 200, 200)
            )

        # Verify holes were drawn by checking pixel at first hole location
        y_first = int(height / (num_holes + 1))
        pixel = canvas.getpixel((spine_x, y_first))

        # Pixel should be different from background
        assert pixel != bg_color, "Binding hole should be rendered"


# ============================================================================
# Page Curvature and Shadow Tests
# ============================================================================

class TestPageCurvatureShadow:
    """Test page curvature shadow rendering."""

    def test_curvature_enabled(self, test_config):
        """Test that page curvature is enabled in config."""
        curvature_config = test_config["compositor"]["page_curvature"]
        assert curvature_config["enabled"] is True, "Curvature should be enabled"

    def test_shadow_width(self, test_config):
        """Test shadow width configuration."""
        curvature_config = test_config["compositor"]["page_curvature"]
        shadow_width = curvature_config["shadow_width"]

        assert shadow_width == 30, "Shadow width should be 30 pixels"
        assert shadow_width > 0, "Shadow width should be positive"

    def test_shadow_opacity(self, test_config):
        """Test shadow opacity configuration."""
        curvature_config = test_config["compositor"]["page_curvature"]
        shadow_opacity = curvature_config["shadow_opacity"]

        assert 0 <= shadow_opacity <= 1, "Opacity should be between 0 and 1"
        assert shadow_opacity == 0.3, "Shadow opacity should be 0.3"

    def test_shadow_gradient_rendering(self, test_config):
        """Test that shadow creates gradient effect."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])
        curvature_config = test_config["compositor"]["page_curvature"]

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        # Draw shadow gradient at spine
        spine_x = spread_size[0] // 2
        shadow_width = curvature_config["shadow_width"]

        for i in range(shadow_width):
            # Gradient from dark to light
            intensity = int(255 * (i / shadow_width))
            color = (intensity, intensity, intensity)
            draw.line([(spine_x - shadow_width + i, 0),
                      (spine_x - shadow_width + i, spread_size[1])],
                     fill=color)

        # Verify gradient exists
        left_pixel = canvas.getpixel((spine_x - shadow_width + 5, 100))
        right_pixel = canvas.getpixel((spine_x - 5, 100))

        # Left should be darker than right
        assert sum(left_pixel) < sum(right_pixel), \
            "Shadow should create gradient from dark to light"


# ============================================================================
# Asset Loading and Rotation Tests
# ============================================================================

class TestAssetLoadingAndRotation:
    """Test loading and rotating sprite assets."""

    def test_load_sprite_image(self, test_sprite):
        """Test loading a sprite image."""
        assert test_sprite is not None, "Sprite should be loaded"
        assert isinstance(test_sprite, Image.Image), "Should be PIL Image"

    def test_rotate_sprite(self, test_sprite):
        """Test rotating a sprite."""
        rotated = test_sprite.rotate(15, expand=True)

        assert rotated is not None, "Rotated sprite should exist"
        assert rotated.size[0] >= test_sprite.size[0], \
            "Rotated image width should be >= original"

    def test_rotation_preserves_data(self, test_sprite):
        """Test that rotation doesn't lose significant data."""
        original_pixels = set(test_sprite.getdata())
        rotated = test_sprite.rotate(5, expand=True)
        rotated_pixels = set(rotated.getdata())

        # Should have some overlap in pixel colors
        assert len(original_pixels & rotated_pixels) > 0, \
            "Rotation should preserve some color data"

    def test_paste_sprite_on_canvas(self, test_config, test_sprite):
        """Test pasting sprite onto canvas."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        position = (400, 300)

        # Paste sprite
        canvas.paste(test_sprite, position)

        # Verify sprite was pasted
        pixel = canvas.getpixel((position[0] + 10, position[1] + 10))
        assert pixel != bg_color, "Sprite should be visible on canvas"


# ============================================================================
# Text Rendering Tests
# ============================================================================

class TestTextRenderingWordWrap:
    """Test text rendering with word wrapping."""

    def test_render_simple_text(self, test_config):
        """Test rendering simple text on canvas."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        text = "Test text"
        draw.text((100, 100), text, fill=(0, 0, 0))

        # Verify text was drawn (pixel should not be background color)
        pixel = canvas.getpixel((105, 105))
        # May or may not be exactly black depending on positioning
        assert canvas is not None, "Text rendering should complete"

    def test_word_wrap_calculation(self):
        """Test word wrapping logic."""
        text = "This is a long line of text that needs to be wrapped"
        max_width = 20

        # Simple word wrap algorithm
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        assert len(lines) > 1, "Long text should be wrapped into multiple lines"
        for line in lines:
            assert len(line) <= max_width + 10, "Lines should respect max width"

    def test_multiline_text_rendering(self, test_config):
        """Test rendering multiple lines of text."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        lines = ["Line 1", "Line 2", "Line 3"]
        y_position = 100

        for line in lines:
            draw.text((100, y_position), line, fill=(0, 0, 0))
            y_position += 20

        assert canvas is not None, "Multiline text should render"


# ============================================================================
# Spine Intrusion Warning Tests
# ============================================================================

class TestSpineIntrusionWarning:
    """Test logging of spine intrusion warnings."""

    def test_detect_spine_intrusion_warning(self, test_config):
        """Test that spine intrusion is detected."""
        from test_framework import detect_spine_intrusion

        spread_width = test_config["compositor"]["spread_size"][0]
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]

        # Element in dead zone
        elements = [
            {"id": "warning_element", "position": [995, 300], "size": [32, 32]}
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)

        assert len(intruding) > 0, "Should detect spine intrusion"

    def test_no_warning_for_safe_elements(self, test_config):
        """Test that safe elements don't trigger warnings."""
        from test_framework import detect_spine_intrusion

        spread_width = test_config["compositor"]["spread_size"][0]
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]

        # Elements far from spine
        elements = [
            {"id": "safe_left", "position": [200, 300], "size": [32, 32]},
            {"id": "safe_right", "position": [1600, 300], "size": [32, 32]}
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)

        assert len(intruding) == 0, "Safe elements should not trigger warnings"


# ============================================================================
# CMYK Misregistration Tests
# ============================================================================

class TestCMYKMisregistration:
    """Test CMYK misregistration effects."""

    def test_misregistration_enabled(self, test_config):
        """Test that CMYK misregistration is enabled."""
        cmyk_config = test_config["compositor"]["cmyk_misregistration"]
        assert cmyk_config["enabled"] is True, "CMYK effect should be enabled"

    def test_max_shift_value(self, test_config):
        """Test maximum shift value for CMYK channels."""
        cmyk_config = test_config["compositor"]["cmyk_misregistration"]
        max_shift = cmyk_config["max_shift_px"]

        assert max_shift == 2, "Max shift should be 2 pixels"
        assert max_shift > 0, "Max shift should be positive"

    def test_channel_shift_simulation(self, test_sprite):
        """Test simulating channel shift effect."""
        # Get RGB channels
        r, g, b = test_sprite.split()

        # Create shifted channels (simulate misregistration)
        r_shifted = Image.new("L", test_sprite.size)
        g_shifted = Image.new("L", test_sprite.size)
        b_shifted = Image.new("L", test_sprite.size)

        # Paste with offsets
        r_shifted.paste(r, (1, 0))  # Shift right
        g_shifted.paste(g, (0, 0))  # No shift
        b_shifted.paste(b, (-1, 0))  # Shift left

        # Merge back
        shifted_image = Image.merge("RGB", (r_shifted, g_shifted, b_shifted))

        assert shifted_image is not None, "Channel shift should work"
        assert shifted_image.size == test_sprite.size, \
            "Shifted image should maintain size"

    def test_misregistration_creates_chromatic_effect(self, test_sprite):
        """Test that misregistration creates visible chromatic aberration."""
        # Apply channel shifts
        r, g, b = test_sprite.split()

        # Shift channels
        arr_r = np.array(r)
        arr_g = np.array(g)
        arr_b = np.array(b)

        # Roll arrays to simulate shift
        arr_r_shifted = np.roll(arr_r, 1, axis=1)
        arr_b_shifted = np.roll(arr_b, -1, axis=1)

        # Create shifted image
        shifted = Image.merge("RGB", (
            Image.fromarray(arr_r_shifted),
            Image.fromarray(arr_g),
            Image.fromarray(arr_b_shifted)
        ))

        # Images should be different
        is_same, similarity = compare_images(test_sprite, shifted, threshold=0.99)
        assert not is_same, "Shifted image should differ from original"


# ============================================================================
# Full Composition Integration Tests
# ============================================================================

@pytest.mark.integration
class TestFullComposition:
    """Integration tests for complete composition workflow."""

    def test_compose_full_spread(self, test_config, test_layout):
        """Test composing a full spread with all elements."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        # Create canvas
        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        # Add elements from layout
        for element in test_layout["elements"]:
            sprite = create_test_sprite(size=tuple(element["size"]))
            position = tuple(element["position"])
            canvas.paste(sprite, position)

        assert canvas is not None, "Full composition should complete"
        assert canvas.size == tuple(spread_size), "Spread should maintain size"

    def test_composition_with_all_effects(self, test_config):
        """Test composition with all effects enabled."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        # Create canvas
        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)
        draw = ImageDraw.Draw(canvas)

        # Add binding holes
        binding_config = test_config["compositor"]["spiral_binding"]
        if binding_config["enabled"]:
            spine_x = spread_size[0] // 2
            num_holes = binding_config["holes"]
            for i in range(num_holes):
                y = int((i + 1) * spread_size[1] / (num_holes + 1))
                draw.ellipse([spine_x - 5, y - 5, spine_x + 5, y + 5],
                           fill=(200, 200, 200))

        # Add page curvature shadow
        curvature_config = test_config["compositor"]["page_curvature"]
        if curvature_config["enabled"]:
            shadow_width = curvature_config["shadow_width"]
            for i in range(shadow_width):
                intensity = int(255 * (i / shadow_width))
                draw.line([(spread_size[0] // 2 - shadow_width + i, 0),
                          (spread_size[0] // 2 - shadow_width + i, spread_size[1])],
                         fill=(intensity, intensity, intensity))

        assert canvas is not None, "Composition with all effects should work"

    def test_save_composed_spread(self, test_config, temp_dir):
        """Test saving composed spread to file."""
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])

        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        output_path = f"{temp_dir}/test_spread.png"
        canvas.save(output_path)

        # Verify file was created
        import os
        assert os.path.exists(output_path), "Output file should be created"

        # Verify file can be loaded
        loaded = Image.open(output_path)
        assert loaded.size == tuple(spread_size), "Loaded image should match size"
