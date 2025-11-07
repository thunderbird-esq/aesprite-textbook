# Klutz Press Computer Graphics Workbook

A hypothetical 1996 Klutz Press-style workbook generator for teaching Aseprite pixel art and computer graphics. This project recreates the distinctive visual aesthetic of mid-90s educational publishing while teaching modern pixel art techniques.

## Project Description

This project generates a complete, print-ready workbook that captures the chaotic energy, vibrant colors, and hands-on teaching philosophy of 1996-era Klutz Press books. The system uses AI for creative asset generation and Python for precision layout composition, combining the best of both approaches.

Key Features:
- Period-authentic 1996 visual aesthetic
- Modular, asset-based generation pipeline
- Code-driven precision layout and typography
- Automated validation for period accuracy
- Print-ready output with vintage printing artifacts

## Architecture Overview

### The Core Philosophy: Modular & Code-Driven

The project uses a three-stage workflow that separates concerns for maximum reliability:

1. **Atomic Asset Generation**: Individual visual components (photos, doodles, containers) are generated in isolation using AI models. This isolates failures and makes iteration inexpensive.

2. **Code-Based Composition**: A Python compositor assembles pre-generated assets according to YAML configuration files, ensuring pixel-perfect precision and repeatability.

3. **Programmatic Typography**: All text is rendered using Pillow with FreeType, giving absolute control over fonts, leading, and kerning.

4. **Continuous Validation**: Every asset and prompt passes through the "Period Police" validator to ensure 1996 authenticity.

### Asset-Based Generation

Rather than generating complete page layouts, the system creates individual components:
- Instructional photographs (shot on period-accurate Kodak Gold 400 film stock)
- Hand-drawn doodles and annotations
- GUI recreations of Aseprite interface elements
- Feature boxes and containers with period-accurate styling
- Pixel art sprites and examples

### Code-Based Composition

The Python compositor handles:
- Page layout and element positioning
- Typography with precise kerning and leading
- Spiral binding simulation with correct 4:1 pitch
- Paper texture and aging effects
- Print artifacts (CMYK misregistration, dot gain, vignetting)
- Safe zone validation and spine intrusion prevention

## Installation

### Requirements

- Python 3.10 or higher
- pip package manager
- Period-accurate TrueType fonts (see Configuration section)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd aesprite-textbook
```

2. Install dependencies using pip:
```bash
pip install -r requirements.txt
```

Or using Poetry (recommended):
```bash
poetry install
```

3. Verify installation:
```bash
python -c "import yaml; import PIL; import numpy; print('All dependencies installed successfully')"
```

## Quick Start

### Generate Your First Spread

1. Prepare your assets in the `assets/generated/` directory
2. Create or modify a layout configuration in `config/layouts/`
3. Run the compositor:

```bash
python klutz_compositor.py config/layouts/spread_04_05.yaml
```

The output will be saved to `output/spreads/`.

## Documentation

### 📚 Complete Documentation Index

All documentation is now organized in the `docs/` directory:

#### For Developers
- **[API Reference](docs/api/api-reference.md)** - Complete API for all classes and methods
- **[Configuration Guide](docs/api/configuration-guide.md)** - YAML schema and examples
- **[Usage Examples](docs/api/usage-examples.md)** - Code samples for common tasks
- **[System Overview](docs/architecture/system-overview.md)** - High-level architecture
- **[Data Flow](docs/architecture/data-flow.md)** - Pipeline data movement
- **[Directory Structure](docs/architecture/directory-structure.md)** - Project organization

#### For Designers
- **[Design Rules](docs/design/designrules3.md)** - Core design constraints
- **[Klutz Press Design](docs/design/klutz-press-design.md)** - Style analysis
- **[Style Guide](docs/design/new-stylebook.md)** - Updated guidelines
- **[90s Aesthetic](docs/design/nickelodeon-goosebumps-design.md)** - Period reference

#### For Educators
- **[Curriculum Overview](docs/curriculum/)** - All AESPRITE modules
- **[Module 1](docs/curriculum/AESPRITE-TIER1-MODULE-1.md)** - Introduction
- **[Module 2](docs/curriculum/AESPRITE-TIER1-MODULE-2.md)** - Fundamentals
- **[Module 3](docs/curriculum/AESPRITE-TIER1-MODULE-3.md)** - Advanced topics
- **[Module 4](docs/curriculum/AESPRITE-TIER1-MODULE-4.md)** - Applications

#### For Project Managers
- **[Project Plan](docs/planning/gemini-klutz-plan-v2.md)** - Overall strategy
- **[Action Plan](docs/planning/klutz-workbook-action-plan.md)** - Task breakdown

#### For Quality Reviewers
- **[Critical Analysis](docs/reviews/criticism-091425.md)** - Detailed critique
- **[Improvement Guide](docs/reviews/kimi-improvement-guide.md)** - Enhancement recommendations

#### Technical Implementation
- **[Technical Docs](docs/technical/)** - Complete implementation details (chapters 1-15)

**See [docs/README.md](docs/README.md) for the complete documentation index.**

### Validate Assets

Before using any generated assets, run them through the Period Police validator:

```bash
python asset_validator.py assets/generated/photo_mouse_hand_01.png
```

## Directory Structure

```
aesprite-textbook/
├── docs/                    # 📚 Complete documentation (NEW!)
│   ├── api/                # API reference and usage guides
│   ├── architecture/       # System design and data flow
│   ├── curriculum/         # Educational modules
│   ├── design/            # Design guidelines and style guides
│   ├── planning/          # Project plans and strategy
│   ├── reviews/           # Critical analysis and improvements
│   ├── technical/         # Implementation details (chapters 1-15)
│   └── README.md          # Documentation index
├── config/                  # Configuration files
│   ├── layouts/            # YAML layout definitions for each spread
│   └── master_config.yaml  # Global project settings
├── assets/                  # Visual assets
│   ├── fonts/              # Period-accurate TTF/OTF files
│   ├── generated/          # AI-generated components (PNGs with transparency)
│   ├── manual/             # Hand-created assets
│   └── textures/           # Scanned paper and binding textures
├── prompts/                 # Generated prompt files
│   ├── spread_02_03/       # Prompts for each spread
│   └── ...
├── output/                  # Generated files
│   ├── spreads/            # Final rendered two-page spreads (PNGs)
│   └── workbooks/          # Assembled PDF workbooks
├── temp/                    # Temporary processing files
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── *.py                     # Core Python modules (see below)
├── requirements.txt         # Python dependencies
├── CHANGELOG.md            # Version history
└── CONTRIBUTING.md         # Contribution guidelines
```

### Core Python Modules

| Module | Purpose |
|--------|---------|
| `klutz_compositor.py` | Main composition engine |
| `prompt_generator.py` | Generate AI prompts from layouts |
| `asset_validator.py` | Period Police validation |
| `post_processor.py` | Apply print artifacts |
| `gemini_integration.py` | Gemini API integration |
| `nano_banana_integration.py` | nano-banana integration |
| `quality_assurance.py` | Automated QA checks |
| `performance_optimization.py` | Batch processing optimization |
| `production_monitoring.py` | Metrics and logging |
| `deploy_workbook.py` | PDF assembly |

**See [docs/architecture/directory-structure.md](docs/architecture/directory-structure.md) for complete details.**

## Usage Examples

### Creating a New Page Layout

Create a YAML file in `config/layouts/`:

```yaml
template: "workshop_layout"
canvas: "aged_newsprint"

left_page:
  elements:
    - id: "L_headline_01"
      type: "text_headline"
      position: [200, 180]
      content: "PIXEL PERFECT!"
      font: "Chicago"
      size: 48

    - id: "L_photo_01"
      type: "graphic_photo_instructional"
      asset: "photo_mouse_hand_01.png"
      position: [250, 300]
      dimensions: [600, 450]
      rotation: 2
      border: "4px solid #F57D0D"
```

### Validating a Prompt

```python
from asset_validator import AssetValidator

validator = AssetValidator()
violations = validator.validate_visual_prompt("Generate a photo of a child using a Macintosh Plus...")
if violations:
    print("Violations found:", violations)
```

## Configuration Guide

### Master Configuration

The `config/master_config.yaml` file controls global project settings:

- **Project metadata**: Name, year, page count
- **Technical specs**: Canvas size (3400x2200), DPI (300), color space
- **Aesthetic rules**: Color distribution (70/20/10), rotation limits, texture opacity
- **Print simulation**: CMYK shift, dot gain, vignette, spine shadow
- **Validation rules**: Period accuracy enforcement, color ratio checking

### Color System (70/20/10 Rule)

- **Klutz Primary (70%)**: Foundation palette (Red, Blue, Yellow)
- **Nickelodeon Accent (20%)**: #F57D0D (Pantone 021 C) for energetic containers
- **Goosebumps Theme (10%)**: #95C120 (Acid Green) for monster sprites

### Typography

Required period-accurate fonts:
- **Helvetica**: 1995 Linotype version for body copy
- **Chicago**: Classic Mac system font for headlines
- **Monaco**: For code/terminal text
- **Courier New**: Fallback for monospaced text

## Technical Specifications

### Canvas & Print

- **Spread size**: 3400x2200 pixels
- **DPI**: 300 (print-quality)
- **Color space**: sRGB
- **Spine width**: 462 pixels (centered)
- **Safe zones**: Configured per element type

### Print Simulation

- **CMYK misregistration**: Magenta [1, 0], Yellow [0, -1]
- **Dot gain**: 0.95 brightness multiplier
- **Vignette**: 0.15 intensity
- **Spine shadow**: 0.20 opacity

## Contributing Guidelines

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Document all functions with docstrings
- Keep functions focused and modular

### Asset Standards

All visual assets must:
- Pass the Period Police validator
- Be generated at 300 DPI
- Use only period-accurate colors and styling
- Include transparency where appropriate
- Be saved as PNG files

### Commit Guidelines

- Use descriptive commit messages
- Validate all assets before committing
- Test layout changes with validation script
- Document any configuration changes

## Validation & Quality Control

### The Period Police

The `asset_validator.py` script enforces 1996 authenticity:

**Forbidden terms in visual design prompts**:
- Modern design aesthetics (gradient, flat design, material design)
- Post-1997 hardware (USB, wireless, bluetooth, LED, LCD)
- Modern software concepts (UX, UI, mobile, touch, cloud)
- Contemporary terminology (hashtag, emoji, meme, HD, 4K)

**Required visual terms** when depicting:
- Mouse: Apple, Macintosh, M0100, beige, one-button
- Computer: Macintosh Plus, System 6, black and white
- Storage: Floppy disk, 1.44MB, 3.5 inch

### Content vs. Visual Style

Important distinction:
- **Visual prompts**: Must strictly adhere to 1996 aesthetics
- **Body text**: May use modern terms when teaching Aseprite features

The validator applies only to visual design elements, not instructional content.

## Development Tools

- **Python 3.10+**: Core runtime
- **Pillow (PIL)**: Image manipulation and composition
- **PyYAML**: Configuration file parsing
- **NumPy**: High-performance array operations
- **Poetry**: Dependency management (optional but recommended)

## Testing & Validation

Run the test suite:
```bash
pytest tests/
```

Validate a complete spread:
```bash
python asset_validator.py --layout config/layouts/spread_04_05.yaml
```

## Project Status

This is an active development project recreating the aesthetic and teaching philosophy of 1996-era Klutz Press publications for teaching modern pixel art with Aseprite.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Klutz Press educational books from the mid-1990s
- Design aesthetic influenced by Nickelodeon and Goosebumps book series
- Built for teaching Aseprite pixel art software
- Utilizes Gemini-2.0-Flash-Exp and nano-banana AI models

## Support

For questions, issues, or contributions, please refer to the project repository.
