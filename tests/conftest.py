"""
Pytest configuration and fixtures for Aesprite Textbook tests.

This module provides shared fixtures for all tests including:
- Mock API clients
- Test configurations
- Test images and sprites
- Temporary directories
- Sample data
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402

import pytest  # noqa: E402
import yaml  # noqa: E402

from test_framework import (  # noqa: E402
    MockGeminiClient,
    MockNanoBananaClient,
    create_test_config,
    create_test_layout,
    create_test_prompt_xml,
    create_test_sprite,
)

# ============================================================================
# Session-level fixtures
# ============================================================================


@pytest.fixture(scope="session")
def test_assets_dir():
    """Get the test assets directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


# ============================================================================
# Function-level fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_gemini():
    """Provide a mock Gemini API client."""
    client = MockGeminiClient()
    yield client
    client.reset()


@pytest.fixture
def mock_nano_banana():
    """Provide a mock nano-banana API client."""
    client = MockNanoBananaClient()
    yield client
    client.reset()


@pytest.fixture
def test_config():
    """Provide a test configuration dictionary."""
    return create_test_config()


@pytest.fixture
def test_layout():
    """Provide a test layout configuration."""
    return create_test_layout()


@pytest.fixture
def test_sprite():
    """Provide a test sprite image."""
    return create_test_sprite()


@pytest.fixture
def test_sprite_computer():
    """Provide a computer-pattern test sprite."""
    return create_test_sprite(pattern="computer")


@pytest.fixture
def test_sprite_checkerboard():
    """Provide a checkerboard-pattern test sprite."""
    return create_test_sprite(pattern="checkerboard")


@pytest.fixture
def test_prompt_xml():
    """Provide a valid test prompt XML."""
    return create_test_prompt_xml()


@pytest.fixture
def test_prompt_xml_forbidden():
    """Provide a test prompt XML with forbidden terms."""
    return create_test_prompt_xml(forbidden_word="gradient")


@pytest.fixture
def sample_config_file(temp_dir, test_config):
    """Create a sample config YAML file."""
    config_path = Path(temp_dir) / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    return config_path


@pytest.fixture
def sample_layout_file(temp_dir, test_layout):
    """Create a sample layout YAML file."""
    layout_path = Path(temp_dir) / "test_layout.yaml"
    with open(layout_path, "w") as f:
        yaml.dump(test_layout, f)
    return layout_path


@pytest.fixture
def sample_sprite_file(temp_dir, test_sprite):
    """Create a sample sprite PNG file."""
    sprite_path = Path(temp_dir) / "test_sprite.png"
    test_sprite.save(sprite_path)
    return sprite_path


@pytest.fixture
def mock_api_responses():
    """Provide mock API response data."""
    return {
        "gemini_success": {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "A pixel art sprite showing a computer with "
                                    "keyboard and mouse on desk"
                                )
                            }
                        ]
                    }
                }
            ]
        },
        "gemini_forbidden": {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "A sprite with gradient effects and alpha transparency"}]
                    }
                }
            ]
        },
    }


# ============================================================================
# Parametrized fixtures for multiple test cases
# ============================================================================


@pytest.fixture(
    params=[
        {"size": (16, 16), "pattern": "solid"},
        {"size": (32, 32), "pattern": "computer"},
        {"size": (64, 64), "pattern": "checkerboard"},
    ]
)
def parametrized_sprite(request):
    """Provide sprites with different sizes and patterns."""
    return create_test_sprite(size=request.param["size"], pattern=request.param["pattern"])


@pytest.fixture(params=[0, 5, 10, 15])
def rotation_angles(request):
    """Provide different rotation angles for testing."""
    return request.param


@pytest.fixture(params=[1, 2, 5, 10])
def element_counts(request):
    """Provide different element counts for layout testing."""
    return request.param


# ============================================================================
# Pytest configuration hooks
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests that mock API calls")
    config.addinivalue_line("markers", "performance: marks performance benchmark tests")


def pytest_collection_modifyitems(config, items):
    """Modify test items based on markers and configuration."""
    # Add marker to tests based on their location
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "full_pipeline" in item.nodeid or "batch" in item.nodeid:
            item.add_marker(pytest.mark.slow)
