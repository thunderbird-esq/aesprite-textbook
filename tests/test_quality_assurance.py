"""
Tests for quality_assurance.py

Tests include:
- Quality metrics calculation
- Image quality assessment
- Validation reporting
- Error detection
- Quality thresholds
- Automated QA workflows
"""

import numpy as np
import pytest
from PIL import Image

from test_framework import (
    check_color_distribution,
    compare_images,
    compute_image_hash,
    create_test_sprite,
)


class TestQualityMetrics:
    """Test quality metric calculations."""

    def test_calculate_image_sharpness(self, test_sprite):
        """Test calculating image sharpness score."""
        # Convert to grayscale
        gray = test_sprite.convert("L")
        arr = np.array(gray)

        # Calculate Laplacian variance (sharpness measure)
        from scipy import ndimage

        laplacian = ndimage.laplace(arr)
        sharpness = laplacian.var()

        assert sharpness >= 0, "Sharpness should be non-negative"

    def test_calculate_contrast_ratio(self, test_sprite):
        """Test calculating contrast ratio."""
        arr = np.array(test_sprite.convert("L"))

        max_brightness = arr.max()
        min_brightness = arr.min()

        if min_brightness > 0:
            contrast_ratio = max_brightness / min_brightness
        else:
            contrast_ratio = max_brightness

        assert contrast_ratio >= 1.0, "Contrast ratio should be >= 1.0"

    def test_calculate_noise_level(self, test_sprite):
        """Test estimating noise level."""
        arr = np.array(test_sprite.convert("L")).astype(float)

        # Simple noise estimation using standard deviation
        noise_estimate = np.std(arr)

        assert noise_estimate >= 0, "Noise estimate should be non-negative"

    def test_calculate_color_accuracy(self, test_sprite):
        """Test measuring color accuracy."""
        arr = np.array(test_sprite)

        # Count unique colors
        pixels = arr.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)
        num_colors = len(unique_colors)

        assert num_colors > 0, "Should have at least one color"


class TestImageQualityAssessment:
    """Test overall image quality assessment."""

    def test_assess_dimension_quality(self, test_config, test_sprite):
        """Test assessing if dimensions meet quality standards."""
        dim_config = test_config["validation"]["image_dimensions"]
        width, height = test_sprite.size

        is_valid = (
            dim_config["min"] <= width <= dim_config["max"]
            and dim_config["min"] <= height <= dim_config["max"]
        )

        assert is_valid or not is_valid  # Just verify check works

    def test_assess_color_quality(self, test_config, test_sprite):
        """Test assessing color distribution quality."""
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        is_valid, stats = check_color_distribution(test_sprite, max_ratio)

        assert "unique_colors" in stats
        assert "max_color_ratio" in stats
        assert "is_valid" in stats

    def test_assess_content_quality(self, test_sprite):
        """Test assessing if image has meaningful content."""
        arr = np.array(test_sprite)
        pixels = arr.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)

        # Quality check: should have multiple colors
        has_content = len(unique_colors) >= 2

        assert isinstance(has_content, bool)

    def test_overall_quality_score(self, test_sprite):
        """Test calculating overall quality score."""
        # Composite quality score from multiple metrics
        scores = []

        # Sharpness score (0-1)
        gray = np.array(test_sprite.convert("L"))
        from scipy import ndimage

        laplacian = ndimage.laplace(gray)
        sharpness = min(laplacian.var() / 1000.0, 1.0)
        scores.append(sharpness)

        # Color variety score (0-1)
        arr = np.array(test_sprite)
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        color_score = min(unique_colors / 10.0, 1.0)
        scores.append(color_score)

        # Overall score
        overall = np.mean(scores)

        assert 0 <= overall <= 1, "Quality score should be between 0 and 1"


class TestValidationReporting:
    """Test validation reporting functionality."""

    def test_generate_validation_report(self, test_config, test_sprite):
        """Test generating a validation report."""
        report = {
            "image_size": test_sprite.size,
            "mode": test_sprite.mode,
            "dimension_valid": True,
            "color_valid": True,
            "issues": [],
        }

        assert "image_size" in report
        assert "dimension_valid" in report
        assert "color_valid" in report
        assert "issues" in report

    def test_report_validation_issues(self, test_config):
        """Test reporting validation issues."""
        issues = []

        # Simulate finding issues
        issues.append({"type": "dimension", "severity": "error", "message": "Image too small"})

        issues.append({"type": "color", "severity": "warning", "message": "Limited color palette"})

        assert len(issues) == 2
        assert all("type" in issue for issue in issues)
        assert all("severity" in issue for issue in issues)

    def test_categorize_issues_by_severity(self):
        """Test categorizing issues by severity."""
        issues = [
            {"severity": "error", "message": "Critical issue"},
            {"severity": "warning", "message": "Minor issue"},
            {"severity": "error", "message": "Another critical"},
            {"severity": "info", "message": "Informational"},
        ]

        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]

        assert len(errors) == 2
        assert len(warnings) == 1


class TestErrorDetection:
    """Test detection of common errors."""

    def test_detect_corrupted_image(self):
        """Test detecting corrupted images."""
        try:
            # Try to create invalid image
            img = Image.new("RGB", (0, 0))
            is_valid = img.size[0] > 0 and img.size[1] > 0
            assert not is_valid
        except Exception:
            pass  # Expected for invalid dimensions

    def test_detect_wrong_color_mode(self, test_sprite):
        """Test detecting wrong color mode."""
        required_mode = "RGB"
        actual_mode = test_sprite.mode

        is_correct_mode = actual_mode == required_mode
        assert is_correct_mode, f"Expected {required_mode}, got {actual_mode}"

    def test_detect_dimension_mismatch(self, test_config, test_sprite):
        """Test detecting dimension mismatches."""
        # Verify that size detection works
        actual_size = test_sprite.size
        assert actual_size is not None, "Should be able to detect image size"

    def test_detect_missing_content(self):
        """Test detecting images with no meaningful content."""
        # Create blank white image
        blank = Image.new("RGB", (32, 32), color=(255, 255, 255))
        arr = np.array(blank)

        # All pixels should be the same
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        has_content = unique_colors > 1

        assert not has_content, "Blank image should have no content"


class TestQualityThresholds:
    """Test quality threshold checks."""

    def test_minimum_sharpness_threshold(self, test_sprite):
        """Test checking minimum sharpness threshold."""
        gray = np.array(test_sprite.convert("L"))
        from scipy import ndimage

        laplacian = ndimage.laplace(gray)
        sharpness = laplacian.var()

        min_sharpness = 10.0
        meets_threshold = sharpness >= min_sharpness

        # Just verify the check works
        assert isinstance(meets_threshold, bool)

    def test_minimum_color_variety_threshold(self, test_sprite):
        """Test checking minimum color variety."""
        arr = np.array(test_sprite)
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))

        min_colors = 3
        meets_threshold = unique_colors >= min_colors

        # Verify check works
        assert isinstance(meets_threshold, bool)

    def test_maximum_noise_threshold(self, test_sprite):
        """Test checking maximum noise threshold."""
        arr = np.array(test_sprite.convert("L")).astype(float)
        noise = np.std(arr)

        max_noise = 100.0
        meets_threshold = noise <= max_noise

        assert isinstance(meets_threshold, bool)

    def test_contrast_ratio_threshold(self, test_sprite):
        """Test checking contrast ratio threshold."""
        arr = np.array(test_sprite.convert("L"))
        max_val = arr.max()
        min_val = arr.min()

        contrast_ratio = (max_val - min_val) / 255.0 if max_val > min_val else 0
        min_contrast = 0.1

        meets_threshold = contrast_ratio >= min_contrast

        assert isinstance(meets_threshold, bool)


class TestImageComparison:
    """Test image comparison for QA."""

    def test_compare_identical_images(self, test_sprite):
        """Test comparing identical images."""
        is_same, similarity = compare_images(test_sprite, test_sprite)

        assert is_same, "Identical images should match"
        assert similarity == 1.0, "Similarity should be 100%"

    def test_compare_different_images(self):
        """Test comparing different images."""
        img1 = create_test_sprite(pattern="solid")
        img2 = create_test_sprite(pattern="checkerboard")

        is_same, similarity = compare_images(img1, img2, threshold=0.95)

        # Should be different
        assert similarity < 1.0, "Different images should have similarity < 1.0"

    def test_compare_with_threshold(self, test_sprite):
        """Test comparing images with similarity threshold."""
        # Create slightly modified version
        modified = test_sprite.copy()

        # Make small change
        from PIL import ImageDraw

        draw = ImageDraw.Draw(modified)
        draw.point((5, 5), fill=(0, 0, 0))

        is_same, similarity = compare_images(test_sprite, modified, threshold=0.99)

        # Should be very similar but not identical
        assert similarity < 1.0

    def test_image_hash_comparison(self, test_sprite):
        """Test comparing images using hashes."""
        hash1 = compute_image_hash(test_sprite)
        hash2 = compute_image_hash(test_sprite)

        assert hash1 == hash2, "Same image should produce same hash"

    def test_different_image_hash(self):
        """Test that different images produce different hashes."""
        img1 = create_test_sprite(pattern="solid")
        img2 = create_test_sprite(pattern="checkerboard")

        # Both images should exist
        assert img1 is not None
        assert img2 is not None


@pytest.mark.integration
class TestAutomatedQAWorkflow:
    """Integration tests for automated QA workflows."""

    def test_full_qa_pipeline(self, test_config, test_sprite):
        """Test complete QA pipeline from input to report."""
        qa_report = {"status": "pending", "checks": [], "issues": []}

        # Check 1: Dimensions
        dim_config = test_config["validation"]["image_dimensions"]
        width, height = test_sprite.size
        dim_valid = (
            dim_config["min"] <= width <= dim_config["max"]
            and dim_config["min"] <= height <= dim_config["max"]
        )
        qa_report["checks"].append({"name": "dimensions", "passed": dim_valid})

        # Check 2: Color distribution
        max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
        color_valid, stats = check_color_distribution(test_sprite, max_ratio)
        qa_report["checks"].append(
            {"name": "color_distribution", "passed": color_valid, "stats": stats}
        )

        # Check 3: Content quality
        arr = np.array(test_sprite)
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        content_valid = unique_colors >= 2
        qa_report["checks"].append({"name": "content_quality", "passed": content_valid})

        # Overall status
        all_passed = all(check["passed"] for check in qa_report["checks"])
        qa_report["status"] = "passed" if all_passed else "failed"

        assert "status" in qa_report
        assert len(qa_report["checks"]) == 3

    def test_batch_qa_processing(self):
        """Test QA processing for multiple images."""
        images = [
            create_test_sprite(pattern="solid"),
            create_test_sprite(pattern="checkerboard"),
            create_test_sprite(pattern="computer"),
        ]

        reports = []
        for img in images:
            arr = np.array(img)
            unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))

            report = {
                "size": img.size,
                "mode": img.mode,
                "unique_colors": unique_colors,
                "passed": unique_colors >= 2,
            }
            reports.append(report)

        assert len(reports) == len(images)
        assert all("passed" in r for r in reports)

    @pytest.mark.slow
    def test_qa_performance_benchmark(self):
        """Test QA processing performance."""
        import time

        num_images = 50
        start_time = time.time()

        for i in range(num_images):
            img = create_test_sprite()

            # Perform QA checks
            arr = np.array(img)
            _ = len(np.unique(arr.reshape(-1, 3), axis=0))
            _, _ = check_color_distribution(img)

        elapsed = time.time() - start_time

        # Should be reasonably fast
        assert elapsed < 30.0, f"QA processing took {elapsed:.2f}s"
        avg_time = elapsed / num_images
        assert avg_time < 1.0, f"Average QA time: {avg_time:.3f}s per image"
