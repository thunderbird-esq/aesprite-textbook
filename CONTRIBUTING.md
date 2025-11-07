# Contributing to Klutz Workbook Project

Thank you for your interest in contributing! This document provides guidelines and standards for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Asset Standards](#asset-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the project
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Harassment, trolling, or insulting comments
- Personal or political attacks
- Publishing others' private information
- Any conduct that would be unprofessional

### Enforcement

Project maintainers will address any unacceptable behavior. Report incidents to thunderbird-esq.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Basic understanding of PIL/Pillow
- Familiarity with YAML

### First-Time Contributors

1. Read the [README.md](README.md) for project overview
2. Review [docs/architecture/system-overview.md](docs/architecture/system-overview.md)
3. Check [open issues](https://github.com/thunderbird-esq/aesprite-textbook/issues) for good first issues
4. Join our [Discussions](https://github.com/thunderbird-esq/aesprite-textbook/discussions)

### Areas for Contribution

- **Code:** Bug fixes, new features, optimizations
- **Documentation:** Improve guides, add examples, fix typos
- **Design:** Create layouts, design assets, style guides
- **Testing:** Write tests, improve coverage, find bugs
- **Curriculum:** Enhance educational content
- **Assets:** Generate period-accurate visual elements

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/thunderbird-esq/aesprite-textbook.git
cd aesprite-textbook
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry (recommended)
poetry install
```

### 3. Verify Installation

```bash
python -c "import yaml; import PIL; import numpy; print('Setup complete!')"
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions or modifications
- `refactor/` - Code refactoring
- `style/` - Code style changes

---

## Contribution Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

### 2. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_compositor.py

# Run with coverage
pytest --cov=. tests/
```

### 3. Validate Assets (if applicable)

```bash
# Validate generated assets
python asset_validator.py assets/generated/

# Validate prompts
python asset_validator.py prompts/
```

### 4. Update Documentation

- Update relevant `.md` files
- Add docstrings to new functions
- Update API reference if needed
- Add usage examples for new features

### 5. Commit Your Changes

```bash
git add .
git commit -m "Type: Brief description

Detailed explanation of changes (if needed)
"
```

**Commit message types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin your-branch-name
```

Then create a pull request on GitHub.

---

## Code Standards

### Python Style Guide

**Follow PEP 8 with these specifics:**

```python
# Use 4 spaces for indentation (no tabs)
def example_function(param1, param2):
    """Docstring describing function.

    Args:
        param1 (type): Description
        param2 (type): Description

    Returns:
        type: Description
    """
    result = param1 + param2
    return result

# Maximum line length: 100 characters (Black formatter)
very_long_variable_name = some_function_call(
    argument1, argument2, argument3
)

# Use type hints
def process_image(image: Image.Image, scale: float = 1.0) -> Image.Image:
    pass

# Use descriptive variable names
# Good:
user_count = 10
image_width = 800

# Bad:
uc = 10
w = 800
```

### Code Formatting

**Use Black formatter:**

```bash
# Format all Python files
black .

# Check without formatting
black --check .
```

### Type Checking

**Use mypy for type checking:**

```bash
# Run type checker
mypy *.py

# Ignore specific errors (use sparingly)
# type: ignore[error-type]
```

### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import yaml
import numpy as np
from PIL import Image

# Local imports
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
```

### Function Guidelines

- **Single Responsibility:** Each function should do one thing
- **Maximum Length:** ~50 lines (refactor if longer)
- **Clear Names:** Use descriptive, action-oriented names
- **Type Hints:** Always include type hints
- **Docstrings:** All public functions must have docstrings

### Class Guidelines

```python
class ExampleClass:
    """Brief description of class.

    Detailed explanation of purpose and usage.

    Attributes:
        attribute1 (type): Description
        attribute2 (type): Description
    """

    def __init__(self, param: str):
        """Initialize ExampleClass.

        Args:
            param: Description
        """
        self.attribute1 = param
        self.attribute2 = None

    def public_method(self) -> None:
        """Public methods have docstrings."""
        pass

    def _private_method(self) -> None:
        """Private methods (underscore prefix) also documented."""
        pass
```

---

## Testing Requirements

### Test Coverage

- **Minimum Coverage:** 80% for new code
- **Critical Paths:** 100% coverage for core functions
- **Test Files:** Match source file structure

### Writing Tests

```python
# tests/unit/test_compositor.py
import pytest
from klutz_compositor import KlutzCompositor

def test_create_base_canvas():
    """Test base canvas creation."""
    compositor = KlutzCompositor()
    canvas = compositor.create_base_canvas()

    assert canvas.width == 3400
    assert canvas.height == 2200
    assert canvas.mode == 'RGB'

def test_spine_intrusion_detection():
    """Test spine dead zone detection."""
    compositor = KlutzCompositor()

    # Element in spine zone should be detected
    assert compositor.check_spine_intrusion(1500, 100, 400, 300) == True

    # Element outside spine zone should pass
    assert compositor.check_spine_intrusion(500, 100, 400, 300) == False

@pytest.fixture
def sample_layout():
    """Fixture providing a sample layout."""
    return {
        'spread_info': {'number': '04-05'},
        'left_page': {'elements': []},
        'right_page': {'elements': []}
    }

def test_with_fixture(sample_layout):
    """Test using a fixture."""
    assert 'spread_info' in sample_layout
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_compositor.py

# Run specific test
pytest tests/unit/test_compositor.py::test_create_base_canvas

# Run with output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html tests/
```

### Test Categories

**Unit Tests (`tests/unit/`):**
- Test individual functions in isolation
- Mock external dependencies
- Fast execution (< 1s per test)

**Integration Tests (`tests/integration/`):**
- Test component interactions
- Use real dependencies where practical
- Moderate execution time (< 10s per test)

**Visual Tests (`tests/visual/`):**
- Compare generated images to references
- Detect visual regressions
- Require manual approval for changes

---

## Documentation Standards

### Markdown Files

**File Structure:**

```markdown
---
title: Document Title
date: YYYY-MM-DD
status: Active | Draft | Deprecated
---

# Document Title

Brief introduction (1-2 paragraphs)

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1

Content with examples...

## See Also

- [Related Doc](link.md)
```

**Style Guidelines:**

- Use sentence case for headings
- One sentence per line (easier diffs)
- Add code examples where relevant
- Include links to related documentation
- Use consistent terminology

### Code Documentation

**Docstring Format:**

```python
def function_name(param1: type, param2: type = default) -> return_type:
    """Brief one-line description.

    Longer description explaining purpose, behavior, and usage.
    Can span multiple lines if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: value)

    Returns:
        Description of return value

    Raises:
        ErrorType: When this error occurs

    Examples:
        >>> function_name("test", 42)
        result
    """
```

### API Documentation

When adding new public classes or methods:

1. Add to `docs/api/api-reference.md`
2. Add usage example to `docs/api/usage-examples.md`
3. Update configuration guide if applicable
4. Add to docstring with full details

---

## Asset Standards

### Visual Assets

**All visual assets must:**

1. Pass the Period Police validator
2. Be generated at 300 DPI
3. Use only period-accurate (1996) styling
4. Include transparency where appropriate
5. Be saved as PNG files

### Validation Checklist

```bash
# Validate a prompt
python asset_validator.py --prompt "your prompt here"

# Validate an image
python asset_validator.py --image path/to/image.png

# Validate entire directory
python asset_validator.py assets/generated/
```

**Forbidden Elements:**
- Gradients or soft shadows
- Modern UI patterns (flat design, material design)
- Post-1997 technology (USB, wireless, LCD, etc.)
- Modern terminology (UX, UI, mobile, cloud, etc.)

**Required Elements (when depicting):**
- Period-accurate hardware (Macintosh Plus, beige Apple mouse)
- Appropriate software (MacPaint, System 6)
- 1996-era photography (film grain, period lighting)

### Color Guidelines

**70/20/10 Rule:**
- 70% Klutz Primary Colors (Red, Blue, Yellow)
- 20% Nickelodeon Orange (#F57D0D) maximum
- 10% Goosebumps Acid Green (#95C120) maximum

**Validation:**

```python
from asset_validator import AssetValidator

validator = AssetValidator()
violations = validator.check_color_distribution(image)
```

### Layout Standards

**Spine Dead Zone:**
- X: 1469-1931 (no elements allowed)
- Automatic detection and warnings
- Adjust positions to avoid intrusion

**Safe Zones:**
- 150px margin on all sides
- Keep important content within safe zones
- Binding area clear of critical elements

**Rotation Limits:**
- Text elements: ±5° maximum
- Image elements: ±15° maximum
- Container elements: ±10° maximum

---

## Pull Request Process

### Before Submitting

**Checklist:**

- [ ] Code follows style guidelines (Black formatted)
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new features
- [ ] Type hints included (`mypy` passes)
- [ ] Documentation updated
- [ ] Assets validated (if applicable)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
- Describe tests added
- Include test results
- Note any manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Assets validated (if applicable)

## Screenshots (if applicable)
Add before/after images for visual changes

## Related Issues
Fixes #123
Relates to #456
```

### Review Process

1. **Automated Checks:**
   - Code formatting (Black)
   - Type checking (mypy)
   - Tests (pytest)
   - Coverage (minimum 80%)

2. **Maintainer Review:**
   - Code quality
   - Design patterns
   - Performance considerations
   - Documentation completeness

3. **Approval & Merge:**
   - At least one approval required
   - All checks must pass
   - Squash and merge (default)

### After Merge

- Delete your branch
- Close related issues
- Update CHANGELOG.md (maintainers)

---

## Issue Reporting

### Bug Reports

**Use this template:**

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.10.5]
- Version: [e.g., 0.1.0]

## Additional Context
Screenshots, error logs, etc.
```

### Feature Requests

```markdown
## Feature Description
Clear description of proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How could this be implemented?

## Alternatives Considered
What other approaches were considered?

## Additional Context
Examples, mockups, references
```

### Good First Issues

Look for issues labeled:
- `good first issue` - Beginner friendly
- `documentation` - Docs improvements
- `help wanted` - Seeking contributors

---

## Questions?

- **Documentation:** Check [docs/](docs/)
- **Discussions:** [GitHub Discussions](https://github.com/thunderbird-esq/aesprite-textbook/discussions)
- **Issues:** [GitHub Issues](https://github.com/thunderbird-esq/aesprite-textbook/issues)

---

## Recognition

Contributors are recognized in:
- `README.md` acknowledgments
- Release notes
- Project documentation

Thank you for contributing to the Klutz Workbook Project!

---

*This contributing guide is maintained by the project team. Suggestions welcome via PR.*
