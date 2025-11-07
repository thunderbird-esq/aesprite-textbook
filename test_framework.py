"""
Test Framework for Aesprite Textbook Project
=============================================

Main test runner with pytest integration, fixture definitions, helper functions,
mock objects for AI API clients, and test utilities for image comparison.

This module provides:
- Pytest integration and fixtures
- Mock objects for Gemini and nano-banana API clients
- Helper functions for creating test assets
- Image comparison utilities
- Test data generators
"""

import hashlib
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest
from PIL import Image, ImageDraw

# ============================================================================
# Configuration Constants
# ============================================================================

TEST_IMAGE_SIZE = (32, 32)
TEST_SPREAD_SIZE = (2000, 1400)
TEST_ASSETS_DIR = Path(__file__).parent / "tests" / "fixtures"


# ============================================================================
# Mock API Clients
# ============================================================================


class MockGeminiClient:
    """Mock Gemini API client for testing without actual API calls."""

    def __init__(self, api_key: str = "test_key"):
        self.api_key = api_key
        self.call_count = 0
        self.last_prompt = None
        self.responses = []
        self._default_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "This is a mock sprite of a computer with keyboard and mouse."}
                        ]
                    }
                }
            ]
        }

    def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Mock content generation."""
        self.call_count += 1
        self.last_prompt = prompt

        if self.responses:
            return self.responses.pop(0)
        return self._default_response

    def set_response(self, response: Dict[str, Any]):
        """Set a custom response for the next call."""
        self.responses.append(response)

    def reset(self):
        """Reset mock state."""
        self.call_count = 0
        self.last_prompt = None
        self.responses = []


class MockNanoBananaClient:
    """Mock nano-banana API client for testing without actual API calls."""

    def __init__(self, api_key: str = "test_key"):
        self.api_key = api_key
        self.call_count = 0
        self.last_prompt = None
        self.last_params = {}
        self.mock_image = None

    def generate_image(
        self, prompt: str, width: int = 32, height: int = 32, **kwargs
    ) -> Image.Image:
        """Mock image generation - returns a simple test sprite."""
        self.call_count += 1
        self.last_prompt = prompt
        self.last_params = {"width": width, "height": height, **kwargs}

        if self.mock_image is not None:
            return self.mock_image

        # Generate a simple test sprite
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw a simple computer-like shape
        draw.rectangle([5, 8, 27, 20], fill=(100, 100, 100))  # Screen
        draw.rectangle([10, 22, 22, 28], fill=(150, 150, 150))  # Keyboard

        return img

    def set_mock_image(self, image: Image.Image):
        """Set a custom image to return."""
        self.mock_image = image

    def reset(self):
        """Reset mock state."""
        self.call_count = 0
        self.last_prompt = None
        self.last_params = {}
        self.mock_image = None


# ============================================================================
# Test Asset Creators
# ============================================================================


def create_test_sprite(
    size: Tuple[int, int] = TEST_IMAGE_SIZE,
    color: Tuple[int, int, int] = (200, 100, 50),
    pattern: str = "solid",
) -> Image.Image:
    """
    Create a test sprite image.

    Args:
        size: Image dimensions (width, height)
        color: RGB color tuple
        pattern: Pattern type - 'solid', 'gradient', 'checkerboard', 'computer'

    Returns:
        PIL Image object
    """
    img = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    if pattern == "solid":
        draw.rectangle([0, 0, size[0], size[1]], fill=color)

    elif pattern == "gradient":
        # Simple vertical gradient
        for y in range(size[1]):
            intensity = int(255 * (y / size[1]))
            draw.line([(0, y), (size[0], y)], fill=(intensity, intensity, intensity))

    elif pattern == "checkerboard":
        square_size = max(4, size[0] // 8)
        for x in range(0, size[0], square_size):
            for y in range(0, size[1], square_size):
                if (x // square_size + y // square_size) % 2 == 0:
                    draw.rectangle([x, y, x + square_size, y + square_size], fill=color)

    elif pattern == "computer":
        # Draw a simple computer sprite
        draw.rectangle([5, 8, size[0] - 5, size[1] // 2], fill=(100, 100, 100))  # Screen
        draw.rectangle(
            [size[0] // 4, size[1] // 2 + 2, 3 * size[0] // 4, size[1] - 4], fill=(150, 150, 150)
        )  # Keyboard

    return img


def create_test_config(
    forbidden_terms: Optional[List[str]] = None,
    allowed_terms: Optional[List[str]] = None,
    required_visual_terms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a test configuration dictionary.

    Args:
        forbidden_terms: List of forbidden words
        allowed_terms: List of allowed modern terms
        required_visual_terms: List of required visual terms

    Returns:
        Configuration dictionary
    """
    return {
        "validation": {
            "forbidden_terms": forbidden_terms
            or ["gradient", "shader", "alpha", "transparency", "blend"],
            "allowed_modern_terms": allowed_terms or ["computer", "keyboard", "mouse", "monitor"],
            "required_visual_terms": required_visual_terms
            or ["keyboard", "mouse", "monitor", "computer"],
            "min_hardware_terms": 2,
            "image_dimensions": {"min": 16, "max": 64, "recommended": 32},
            "color_distribution": {"max_single_color_ratio": 0.8, "min_unique_colors": 3},
            "layout": {
                "spine_dead_zone_mm": 5,
                "spine_dead_zone_px": 50,
                "max_rotation_degrees": 15,
            },
        },
        "compositor": {
            "spread_size": [2000, 1400],
            "background_color": [255, 242, 204],
            "spiral_binding": {"enabled": True, "holes": 23, "hole_diameter_mm": 6},
            "page_curvature": {"enabled": True, "shadow_width": 30, "shadow_opacity": 0.3},
            "cmyk_misregistration": {"enabled": True, "max_shift_px": 2},
        },
        "prompt_generation": {"temperature": 0.7, "max_attempts": 3},
    }


def create_test_layout(num_elements: int = 2) -> Dict[str, Any]:
    """
    Create a test layout configuration.

    Args:
        num_elements: Number of elements in the layout

    Returns:
        Layout configuration dictionary
    """
    elements = []
    for i in range(num_elements):
        elements.append(
            {
                "id": f"element_{i}",
                "type": "sprite",
                "position": [200 + i * 400, 300 + i * 200],
                "size": [32, 32],
                "rotation": 0,
                "prompt_template": "A pixel art sprite of a {topic} in Aesprite style",
            }
        )

    return {
        "spread_id": "test_spread",
        "elements": elements,
        "metadata": {"page_numbers": [4, 5], "section": "test_section"},
    }


def create_test_prompt_xml(
    description: str = "computer with keyboard", forbidden_word: Optional[str] = None
) -> str:
    """
    Create a test prompt in XML format.

    Args:
        description: Description text
        forbidden_word: Optional forbidden word to include

    Returns:
        XML string
    """
    if forbidden_word:
        description = f"{description} with {forbidden_word}"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<prompt>
    <description>{description}</description>
    <style>aesprite pixel art</style>
    <constraints>
        <size>32x32</size>
        <colors>limited palette</colors>
    </constraints>
</prompt>"""


# ============================================================================
# Image Comparison Utilities
# ============================================================================


def compare_images(
    img1: Image.Image, img2: Image.Image, threshold: float = 0.95
) -> Tuple[bool, float]:
    """
    Compare two images for similarity.

    Args:
        img1: First image
        img2: Second image
        threshold: Similarity threshold (0.0 to 1.0)

    Returns:
        Tuple of (are_similar, similarity_score)
    """
    if img1.size != img2.size:
        return False, 0.0

    # Convert to numpy arrays
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    # Calculate MSE
    mse = np.mean((arr1 - arr2) ** 2)
    max_mse = 255**2
    similarity = 1.0 - (mse / max_mse)

    return similarity >= threshold, similarity


def compute_image_hash(img: Image.Image) -> str:
    """
    Compute a hash of an image for comparison.

    Args:
        img: PIL Image object

    Returns:
        Hexadecimal hash string
    """
    return hashlib.md5(img.tobytes()).hexdigest()


def check_color_distribution(
    img: Image.Image, max_single_color_ratio: float = 0.8
) -> Tuple[bool, Dict[str, float]]:
    """
    Check if image color distribution is within acceptable limits.

    Args:
        img: PIL Image object
        max_single_color_ratio: Maximum ratio for a single color

    Returns:
        Tuple of (is_valid, stats_dict)
    """
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    total_pixels = len(pixels)

    # Count unique colors
    unique_colors = np.unique(pixels, axis=0)
    num_unique = len(unique_colors)

    # Find most common color
    color_counts = {}
    for pixel in pixels:
        color = tuple(pixel)
        color_counts[color] = color_counts.get(color, 0) + 1

    max_count = max(color_counts.values())
    max_ratio = max_count / total_pixels

    stats = {
        "unique_colors": num_unique,
        "max_color_ratio": max_ratio,
        "is_valid": max_ratio <= max_single_color_ratio and num_unique >= 3,
    }

    return stats["is_valid"], stats


def detect_spine_intrusion(
    elements: List[Dict[str, Any]], spread_width: int = 2000, dead_zone_px: int = 50
) -> List[str]:
    """
    Detect if any elements intrude into the spine dead zone.

    Args:
        elements: List of element dictionaries with position and size
        spread_width: Width of the spread
        dead_zone_px: Dead zone width in pixels

    Returns:
        List of element IDs that intrude into dead zone
    """
    spine_center = spread_width // 2
    spine_min = spine_center - dead_zone_px // 2
    spine_max = spine_center + dead_zone_px // 2

    intruding = []
    for elem in elements:
        x, y = elem["position"]
        w, h = elem.get("size", [32, 32])

        # Check if element overlaps with dead zone
        elem_left = x
        elem_right = x + w

        if elem_left < spine_max and elem_right > spine_min:
            intruding.append(elem["id"])

    return intruding


# ============================================================================
# Pytest Fixtures (to be used in conftest.py)
# ============================================================================


def get_mock_gemini_client():
    """Fixture for mock Gemini client."""
    return MockGeminiClient()


def get_mock_nano_banana_client():
    """Fixture for mock nano-banana client."""
    return MockNanoBananaClient()


def get_test_config():
    """Fixture for test configuration."""
    return create_test_config()


def get_test_layout():
    """Fixture for test layout."""
    return create_test_layout()


def get_test_sprite():
    """Fixture for test sprite image."""
    return create_test_sprite()


def get_temp_dir():
    """Fixture for temporary directory."""
    return tempfile.mkdtemp()


# ============================================================================
# Test Runner Integration
# ============================================================================


def run_tests(
    test_path: Optional[str] = None,
    coverage: bool = True,
    verbose: bool = True,
    markers: Optional[str] = None,
) -> int:
    """
    Run pytest tests with coverage.

    Args:
        test_path: Path to tests directory or specific test file
        coverage: Enable coverage reporting
        verbose: Verbose output
        markers: Pytest markers to filter tests (e.g., "not slow")

    Returns:
        Exit code (0 for success)
    """
    args = []

    if test_path:
        args.append(test_path)
    else:
        args.append("tests/")

    if verbose:
        args.append("-v")

    if coverage:
        args.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    if markers:
        args.extend(["-m", markers])

    return pytest.main(args)


if __name__ == "__main__":
    # Run tests when executed directly
    sys.exit(run_tests())
