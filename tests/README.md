# Test Suite Documentation

This directory contains comprehensive tests for the Aesprite Textbook project.

## Structure

```
tests/
├── __init__.py                      # Package initialization
├── conftest.py                      # Pytest fixtures and configuration
├── README.md                        # This file
│
├── fixtures/                        # Test data and sample files
│   ├── sample_config.yaml          # Sample configuration
│   ├── sample_layout.yaml          # Sample layout definition
│   ├── sample_image.png            # Sample sprite image
│   ├── sample_prompt.xml           # Valid prompt XML
│   └── forbidden_prompt.txt        # Prompt with forbidden terms
│
├── integration/                     # Integration tests
│   ├── __init__.py
│   └── test_full_pipeline.py       # End-to-end pipeline tests
│
├── test_asset_validator.py         # Asset validation tests
├── test_klutz_compositor.py        # Composition tests
├── test_prompt_generator.py        # Prompt generation tests
├── test_gemini_integration.py      # Gemini API mock tests
├── test_nano_banana_integration.py # Nano-banana API mock tests
├── test_post_processor.py          # Post-processing tests
└── test_quality_assurance.py       # QA workflow tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run only unit tests (fast)
```bash
pytest -m "not slow"
```

### Run only integration tests
```bash
pytest -m integration
```

### Run specific test file
```bash
pytest tests/test_asset_validator.py -v
```

### Run in parallel
```bash
pytest -n auto
```

## Test Categories

Tests are marked with the following markers:

- `unit` - Fast, isolated unit tests
- `integration` - Integration tests involving multiple components
- `slow` - Tests that take > 5 seconds
- `api` - Tests that mock API calls
- `performance` - Performance benchmark tests
- `smoke` - Quick validation tests

## Coverage Goals

- **Overall coverage target**: 80%+
- **Critical modules**: 90%+
  - asset_validator.py
  - klutz_compositor.py
  - prompt_generator.py

## Test Files Overview

### test_asset_validator.py (47 tests)
Tests for asset validation including:
- Forbidden terms detection (6 tests)
- Allowed modern terms validation (5 tests)
- Required visual terms checking (3 tests)
- Image dimension validation (6 tests)
- Color distribution limits (4 tests)
- Layout spine intrusion detection (4 tests)
- Rotation limits validation (5 tests)

### test_klutz_compositor.py (30 tests)
Tests for compositor functionality:
- Chaos rotation determinism (4 tests)
- Base canvas creation (4 tests)
- Spiral binding rendering (4 tests)
- Page curvature and shadows (4 tests)
- Asset loading and rotation (4 tests)
- Text rendering and word wrap (3 tests)
- Spine intrusion warnings (2 tests)
- CMYK misregistration effects (3 tests)

### test_prompt_generator.py (25 tests)
Tests for prompt generation:
- Template rendering (3 tests)
- Forbidden term avoidance (4 tests)
- Required term inclusion (3 tests)
- XML format validation (5 tests)
- Prompt validation logic (3 tests)
- Error handling (3 tests)

### test_gemini_integration.py (28 tests)
Tests for Gemini API integration:
- Client initialization (2 tests)
- Content generation (4 tests)
- Response parsing (4 tests)
- Error handling (3 tests)
- Prompt validation (3 tests)
- Rate limiting (3 tests)
- Retry logic (3 tests)

### test_nano_banana_integration.py (25 tests)
Tests for nano-banana API:
- Client basics (2 tests)
- Image generation (5 tests)
- Image validation (4 tests)
- Custom mock images (3 tests)
- Error handling (3 tests)
- Parametrized generation (2 tests)
- Image post-processing (3 tests)

### test_post_processor.py (25 tests)
Tests for post-processing:
- CMYK conversion (3 tests)
- Misregistration effects (4 tests)
- Image sharpening (3 tests)
- Resolution adjustments (4 tests)
- Format conversion (4 tests)
- Metadata handling (3 tests)
- Color adjustments (4 tests)

### test_quality_assurance.py (30 tests)
Tests for QA workflows:
- Quality metrics (4 tests)
- Image quality assessment (4 tests)
- Validation reporting (3 tests)
- Error detection (4 tests)
- Quality thresholds (4 tests)
- Image comparison (5 tests)
- Automated QA workflows (3 tests)

### integration/test_full_pipeline.py (20 tests)
Integration tests:
- End-to-end spread generation (1 test)
- Batch asset generation (3 tests)
- Validation and regeneration (3 tests)
- Config-driven variation (4 tests)
- Performance benchmarks (4 tests)
- Error recovery (3 tests)

## Total Test Count

**230+ comprehensive tests** covering all major components

## CI/CD Integration

Tests are automatically run on:
- Every push to main/develop branches
- Every pull request
- Multiple Python versions (3.9, 3.10, 3.11)

See `.github/workflows/ci.yml` for full CI/CD configuration.

## Writing New Tests

1. Create test file following naming convention: `test_*.py`
2. Import fixtures from conftest.py
3. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.)
4. Follow existing test structure and naming conventions
5. Aim for descriptive test names that explain what is being tested
6. Include docstrings for complex tests

Example:
```python
import pytest

class TestMyFeature:
    """Test suite for my feature."""

    def test_basic_functionality(self, test_config):
        """Test that basic functionality works as expected."""
        # Arrange
        expected = "result"

        # Act
        actual = my_function(test_config)

        # Assert
        assert actual == expected
```

## Continuous Improvement

- Regularly review and update tests
- Add tests for bug fixes
- Improve coverage for critical paths
- Keep test runtime reasonable (< 5 minutes for full suite)
- Maintain test isolation and independence
