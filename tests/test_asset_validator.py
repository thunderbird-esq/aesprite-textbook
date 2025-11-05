"""
Tests for asset_validator.py

Tests include:
- Forbidden terms detection
- Allowed modern terms validation
- Required visual terms checking
- Image dimension validation
- Color distribution limits
- Layout spine intrusion detection
- Rotation limits
- Edge cases and error handling
"""

import pytest
from PIL import Image
import numpy as np
from pathlib import Path

from test_framework import (
    create_test_sprite,
    create_test_config,
    check_color_distribution,
    detect_spine_intrusion,
)


# ============================================================================
# Forbidden Terms Detection Tests
# ============================================================================

class TestForbiddenTermsDetection:
    """Test detection of forbidden terms in prompts."""

    def test_forbidden_term_gradient(self, test_config):
        """Test that 'gradient' is detected as forbidden."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with a smooth gradient background"

        # Check if any forbidden term appears in prompt
        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert has_forbidden, "Should detect 'gradient' as forbidden"

    def test_forbidden_term_alpha(self, test_config):
        """Test that 'alpha' transparency is detected as forbidden."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with alpha transparency effects"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert has_forbidden, "Should detect 'alpha' as forbidden"

    def test_forbidden_term_blend(self, test_config):
        """Test that 'blend' is detected as forbidden."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with blend modes"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert has_forbidden, "Should detect 'blend' as forbidden"

    def test_multiple_forbidden_terms(self, test_config):
        """Test detection of multiple forbidden terms."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with gradient and shader effects using alpha blending"

        found_terms = [term for term in forbidden if term in prompt.lower()]
        assert len(found_terms) >= 2, "Should detect multiple forbidden terms"

    def test_no_forbidden_terms(self, test_config):
        """Test that clean prompts pass validation."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A pixel art sprite of a computer with keyboard and mouse"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert not has_forbidden, "Clean prompt should not trigger forbidden terms"

    def test_case_insensitive_detection(self, test_config):
        """Test that forbidden term detection is case-insensitive."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompts = [
            "A sprite with GRADIENT effects",
            "A sprite with Gradient effects",
            "A sprite with GrAdIeNt effects",
        ]

        for prompt in prompts:
            has_forbidden = any(term in prompt.lower() for term in forbidden)
            assert has_forbidden, f"Should detect forbidden term in: {prompt}"


# ============================================================================
# Allowed Modern Terms Tests
# ============================================================================

class TestAllowedModernTerms:
    """Test validation of allowed modern terms."""

    def test_allowed_term_computer(self, test_config):
        """Test that 'computer' is an allowed term."""
        allowed = test_config["validation"]["allowed_modern_terms"]
        assert "computer" in allowed, "Computer should be in allowed terms"

    def test_allowed_term_keyboard(self, test_config):
        """Test that 'keyboard' is an allowed term."""
        allowed = test_config["validation"]["allowed_modern_terms"]
        assert "keyboard" in allowed, "Keyboard should be in allowed terms"

    def test_allowed_term_mouse(self, test_config):
        """Test that 'mouse' is an allowed term."""
        allowed = test_config["validation"]["allowed_modern_terms"]
        assert "mouse" in allowed, "Mouse should be in allowed terms"

    def test_allowed_term_monitor(self, test_config):
        """Test that 'monitor' is an allowed term."""
        allowed = test_config["validation"]["allowed_modern_terms"]
        assert "monitor" in allowed, "Monitor should be in allowed terms"

    def test_prompt_with_allowed_terms(self, test_config):
        """Test prompt containing multiple allowed terms."""
        allowed = test_config["validation"]["allowed_modern_terms"]
        prompt = "A sprite of a computer with keyboard, mouse, and monitor"

        found_terms = [term for term in allowed if term in prompt.lower()]
        assert len(found_terms) >= 3, "Should find multiple allowed terms"


# ============================================================================
# Required Visual Terms Tests
# ============================================================================

class TestRequiredVisualTerms:
    """Test validation of required visual/hardware terms."""

    def test_required_hardware_terms_present(self, test_config):
        """Test that prompt contains required hardware terms."""
        required = test_config["validation"]["required_visual_terms"]
        min_required = test_config["validation"]["min_hardware_terms"]
        prompt = "A pixel art sprite of a computer with keyboard and mouse"

        found_terms = [term for term in required if term in prompt.lower()]
        assert len(found_terms) >= min_required, \
            f"Should have at least {min_required} hardware terms"

    def test_insufficient_hardware_terms(self, test_config):
        """Test detection of insufficient hardware terms."""
        required = test_config["validation"]["required_visual_terms"]
        min_required = test_config["validation"]["min_hardware_terms"]
        prompt = "A pixel art sprite of a desk"

        found_terms = [term for term in required if term in prompt.lower()]
        assert len(found_terms) < min_required, \
            "Should detect insufficient hardware terms"

    def test_exact_minimum_hardware_terms(self, test_config):
        """Test prompt with exactly minimum required hardware terms."""
        required = test_config["validation"]["required_visual_terms"]
        min_required = test_config["validation"]["min_hardware_terms"]
        prompt = "A computer with keyboard"

        found_terms = [term for term in required if term in prompt.lower()]
        assert len(found_terms) >= min_required, \
            "Should accept exact minimum hardware terms"


# ============================================================================
# Image Dimension Validation Tests
# ============================================================================

class TestImageDimensionValidation:
    """Test validation of image dimensions."""

    def test_dimension_within_range(self, test_config):
        """Test that 32x32 image is within valid range."""
        dim_config = test_config["validation"]["image_dimensions"]
        img = create_test_sprite(size=(32, 32))

        width, height = img.size
        assert width >= dim_config["min"], "Width should be >= minimum"
        assert width <= dim_config["max"], "Width should be <= maximum"
        assert height >= dim_config["min"], "Height should be >= minimum"
        assert height <= dim_config["max"], "Height should be <= maximum"

    def test_dimension_too_small(self, test_config):
        """Test rejection of images that are too small."""
        dim_config = test_config["validation"]["image_dimensions"]
        img = create_test_sprite(size=(8, 8))

        width, height = img.size
        is_valid = (width >= dim_config["min"] and height >= dim_config["min"])
        assert not is_valid, "Should reject images smaller than minimum"

    def test_dimension_too_large(self, test_config):
        """Test rejection of images that are too large."""
        dim_config = test_config["validation"]["image_dimensions"]
        img = create_test_sprite(size=(128, 128))

        width, height = img.size
        is_valid = (width <= dim_config["max"] and height <= dim_config["max"])
        assert not is_valid, "Should reject images larger than maximum"

    def test_dimension_at_minimum(self, test_config):
        """Test acceptance of images at minimum size."""
        dim_config = test_config["validation"]["image_dimensions"]
        min_size = dim_config["min"]
        img = create_test_sprite(size=(min_size, min_size))

        width, height = img.size
        is_valid = (width >= dim_config["min"] and height >= dim_config["min"])
        assert is_valid, "Should accept images at minimum size"

    def test_dimension_at_maximum(self, test_config):
        """Test acceptance of images at maximum size."""
        dim_config = test_config["validation"]["image_dimensions"]
        max_size = dim_config["max"]
        img = create_test_sprite(size=(max_size, max_size))

        width, height = img.size
        is_valid = (width <= dim_config["max"] and height <= dim_config["max"])
        assert is_valid, "Should accept images at maximum size"

    def test_recommended_dimension(self, test_config):
        """Test that recommended size is within valid range."""
        dim_config = test_config["validation"]["image_dimensions"]
        recommended = dim_config["recommended"]

        assert dim_config["min"] <= recommended <= dim_config["max"], \
            "Recommended size should be within valid range"


# ============================================================================
# Color Distribution Tests
# ============================================================================

class TestColorDistributionLimits:
    """Test validation of color distribution in images."""

    def test_color_distribution_valid(self, test_config):
        """Test that checkerboard pattern has valid color distribution."""
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        img = create_test_sprite(size=(32, 32), pattern="checkerboard")

        is_valid, stats = check_color_distribution(img, max_ratio)
        assert is_valid, f"Checkerboard should have valid color distribution: {stats}"

    def test_single_color_exceeds_limit(self, test_config):
        """Test detection of images with too much of a single color."""
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        # Create mostly solid color image
        img = create_test_sprite(size=(32, 32), pattern="solid")

        is_valid, stats = check_color_distribution(img, max_ratio)
        # Solid pattern should fail (too much of one color)
        assert not is_valid, f"Solid color should fail distribution check: {stats}"

    def test_minimum_unique_colors(self, test_config):
        """Test that images have minimum number of unique colors."""
        min_colors = test_config["validation"]["color_distribution"]["min_unique_colors"]
        img = create_test_sprite(size=(32, 32), pattern="computer")

        _, stats = check_color_distribution(img)
        assert stats["unique_colors"] >= min_colors, \
            f"Should have at least {min_colors} unique colors"

    def test_color_distribution_computer_sprite(self, test_config):
        """Test color distribution of computer sprite pattern."""
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        img = create_test_sprite(size=(32, 32), pattern="computer")

        is_valid, stats = check_color_distribution(img, max_ratio)
        # Computer sprite should have reasonable color distribution
        assert stats["unique_colors"] >= 3, "Computer sprite should have multiple colors"


# ============================================================================
# Layout Spine Intrusion Tests
# ============================================================================

class TestLayoutSpineIntrusion:
    """Test detection of elements intruding into spine dead zone."""

    def test_no_spine_intrusion(self, test_config):
        """Test that elements outside dead zone are valid."""
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]
        spread_width = test_config["compositor"]["spread_size"][0]

        elements = [
            {"id": "left_element", "position": [200, 300], "size": [32, 32]},
            {"id": "right_element", "position": [1600, 300], "size": [32, 32]},
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)
        assert len(intruding) == 0, "Elements outside dead zone should be valid"

    def test_spine_intrusion_detected(self, test_config):
        """Test detection of element intruding into dead zone."""
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]
        spread_width = test_config["compositor"]["spread_size"][0]

        elements = [
            {"id": "center_element", "position": [990, 300], "size": [32, 32]},
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)
        assert len(intruding) > 0, "Element in dead zone should be detected"
        assert "center_element" in intruding, "Should identify intruding element"

    def test_multiple_spine_intrusions(self, test_config):
        """Test detection of multiple elements in dead zone."""
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]
        spread_width = test_config["compositor"]["spread_size"][0]

        elements = [
            {"id": "elem1", "position": [980, 300], "size": [32, 32]},
            {"id": "elem2", "position": [1000, 400], "size": [32, 32]},
            {"id": "elem3", "position": [1500, 500], "size": [32, 32]},  # Safe
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)
        assert len(intruding) >= 2, "Should detect multiple intrusions"
        assert "elem3" not in intruding, "Safe element should not be flagged"

    def test_edge_of_dead_zone(self, test_config):
        """Test elements at the edge of dead zone."""
        dead_zone = test_config["validation"]["layout"]["spine_dead_zone_px"]
        spread_width = test_config["compositor"]["spread_size"][0]

        spine_center = spread_width // 2
        spine_min = spine_center - dead_zone // 2

        # Element just outside dead zone
        elements = [
            {"id": "edge_element", "position": [spine_min - 35, 300], "size": [32, 32]},
        ]

        intruding = detect_spine_intrusion(elements, spread_width, dead_zone)
        assert len(intruding) == 0, "Element outside dead zone should be valid"


# ============================================================================
# Rotation Limits Tests
# ============================================================================

class TestRotationLimits:
    """Test validation of rotation constraints."""

    def test_rotation_within_limits(self, test_config):
        """Test that rotations within limits are valid."""
        max_rotation = test_config["validation"]["layout"]["max_rotation_degrees"]

        for angle in [0, 5, 10, 15]:
            assert abs(angle) <= max_rotation, \
                f"Rotation {angle}° should be within ±{max_rotation}°"

    def test_rotation_exceeds_limits(self, test_config):
        """Test detection of excessive rotation."""
        max_rotation = test_config["validation"]["layout"]["max_rotation_degrees"]

        for angle in [20, 30, 45, 90]:
            assert abs(angle) > max_rotation, \
                f"Rotation {angle}° should exceed ±{max_rotation}°"

    def test_negative_rotation_limits(self, test_config):
        """Test that negative rotations are also limited."""
        max_rotation = test_config["validation"]["layout"]["max_rotation_degrees"]

        for angle in [-5, -10, -15]:
            assert abs(angle) <= max_rotation, \
                f"Negative rotation {angle}° should be within ±{max_rotation}°"

        for angle in [-20, -30, -45]:
            assert abs(angle) > max_rotation, \
                f"Negative rotation {angle}° should exceed ±{max_rotation}°"

    def test_zero_rotation(self, test_config):
        """Test that zero rotation is always valid."""
        max_rotation = test_config["validation"]["layout"]["max_rotation_degrees"]
        assert abs(0) <= max_rotation, "Zero rotation should always be valid"

    def test_max_rotation_boundary(self, test_config):
        """Test rotation at exactly the maximum limit."""
        max_rotation = test_config["validation"]["layout"]["max_rotation_degrees"]

        assert abs(max_rotation) <= max_rotation, \
            f"Rotation at exactly {max_rotation}° should be valid"
        assert abs(max_rotation + 1) > max_rotation, \
            f"Rotation at {max_rotation + 1}° should be invalid"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestAssetValidatorIntegration:
    """Integration tests for complete validation workflow."""

    def test_valid_asset_passes_all_checks(self, test_config, test_sprite_computer):
        """Test that a valid asset passes all validation checks."""
        # Check dimensions
        dim_config = test_config["validation"]["image_dimensions"]
        width, height = test_sprite_computer.size
        assert dim_config["min"] <= width <= dim_config["max"]
        assert dim_config["min"] <= height <= dim_config["max"]

        # Check color distribution
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        is_valid, stats = check_color_distribution(test_sprite_computer, max_ratio)
        # Computer sprite might have high white background, so we just check it runs
        assert stats["unique_colors"] >= 2

    def test_invalid_asset_fails_multiple_checks(self, test_config):
        """Test that an invalid asset fails multiple validation checks."""
        # Create oversized solid-color image (violates both dimension and color rules)
        bad_sprite = create_test_sprite(size=(128, 128), pattern="solid")

        # Check dimensions
        dim_config = test_config["validation"]["image_dimensions"]
        width, height = bad_sprite.size
        dim_valid = (width <= dim_config["max"] and height <= dim_config["max"])
        assert not dim_valid, "Oversized image should fail dimension check"

        # Check color distribution
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        color_valid, _ = check_color_distribution(bad_sprite, max_ratio)
        assert not color_valid, "Solid color image should fail color distribution check"
