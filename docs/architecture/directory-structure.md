---
title: Directory Structure
date: 2025-11-05
status: Active
---

# Project Directory Structure

This document explains the organization of the Klutz Workbook project and the purpose of each directory.

## Complete Directory Tree

```
aesprite-textbook/
├── .claude/                    # Claude Code configuration
├── .git/                       # Git repository data
├── assets/                     # Asset files
│   ├── fonts/                  # Period-accurate fonts
│   ├── generated/              # AI-generated assets
│   ├── manual/                 # Hand-created assets
│   └── textures/               # Paper textures, grains
├── config/                     # Configuration files
│   ├── layouts/                # Individual spread layouts
│   └── master_config.yaml      # Global configuration
├── docs/                       # Documentation
│   ├── api/                    # API reference
│   │   ├── api-reference.md
│   │   ├── configuration-guide.md
│   │   └── usage-examples.md
│   ├── architecture/           # System architecture
│   │   ├── data-flow.md
│   │   ├── directory-structure.md
│   │   └── system-overview.md
│   ├── curriculum/             # Educational curriculum
│   │   ├── AESPRITE-TIER1-MODULE-1.md
│   │   ├── AESPRITE-TIER1-MODULE-2.md
│   │   ├── AESPRITE-TIER1-MODULE-3.md
│   │   ├── AESPRITE-TIER1-MODULE-4.md
│   │   ├── AESPRITE-TIER1-MODULE1-EXPANDED.md
│   │   └── AESPRITE-TIER1-ADDITIONAL-RESOURCES.md
│   ├── design/                 # Design documentation
│   │   ├── designrules3.md
│   │   ├── klutz-press-design.md
│   │   ├── new-stylebook.md
│   │   └── nickelodeon-goosebumps-design.md
│   ├── planning/               # Project planning
│   │   ├── gemini-klutz-plan-v2.md
│   │   └── klutz-workbook-action-plan.md
│   ├── reviews/                # Criticism & improvements
│   │   ├── criticism-091425.md
│   │   └── kimi-improvement-guide.md
│   ├── technical/              # Technical implementation
│   │   ├── klutz-technical-implementation-1.md
│   │   ├── klutz-technical-implementation-2.md
│   │   ├── ... (3-15)
│   │   ├── klutz-technical-implementation-1and2.md
│   │   ├── klutz-technical-implementation-12and3.md
│   │   ├── klutz-technical-implementation-23and4.md
│   │   ├── klutz-technical-implementation-23456and7.md
│   │   ├── klutz-technical-implementation-89101112ish.md
│   │   ├── klutz-technical-implementation-upto7possibly.md
│   │   ├── klutz-technical-implementation.md
│   │   └── klutz-technical-documentation-toc.md
│   └── README.md               # Documentation index
├── output/                     # Generated output
│   ├── spreads/                # Individual spread images
│   └── workbooks/              # Assembled PDF workbooks
├── prompts/                    # Generated prompts
│   ├── spread_02_03/           # Prompts for spread 2-3
│   ├── spread_04_05/           # Prompts for spread 4-5
│   └── ...
├── temp/                       # Temporary files
│   └── intermediate/           # Intermediate processing files
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
├── aesprite-curriculum.pdf     # Main curriculum document
├── asset_validator.py          # Asset validation script
├── deploy_workbook.py          # Workbook deployment
├── gemini_integration.py       # Gemini API integration
├── klutz_compositor.py         # Main compositor
├── nano_banana_integration.py  # nano-banana integration
├── performance_optimization.py # Performance utilities
├── post_processor.py           # Post-processing effects
├── production_monitoring.py    # Production monitoring
├── prompt_generator.py         # Prompt generation
├── quality_assurance.py        # QA automation
├── requirements.txt            # Python dependencies
├── CHANGELOG.md                # Project changelog
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # Project overview
```

---

## Directory Descriptions

### Root Directory

**Purpose:** Main project files and entry points

**Key Files:**
- `README.md` - Project overview and quick start
- `requirements.txt` - Python package dependencies
- `CHANGELOG.md` - Version history and changes
- `CONTRIBUTING.md` - Guidelines for contributors
- `aesprite-curriculum.pdf` - Main curriculum document

**Python Scripts:**
All core functionality implemented as importable modules.

---

### `/assets/`

**Purpose:** Store all asset files used in workbook generation

#### `/assets/fonts/`

**Contents:**
- Chicago.ttf (Macintosh system font)
- Geneva.ttf (Body text font)
- Monaco.ttf (Monospace code font)
- Tekton.ttf (Handwriting font)
- Courier.ttf (Typewriter font)

**Format:** TrueType Font (.ttf)
**License:** Verify licensing for each font

#### `/assets/generated/`

**Contents:** AI-generated images from nano-banana

**Naming Convention:**
- `photo_<description>_<number>.png`
- `pixelart_<description>_<number>.png`
- `gui_<description>_<number>.png`
- `doodle_<description>_<number>.png`

**Format:** PNG with alpha channel
**Dimensions:** Vary by element (typically 400x300 to 1200x900)

#### `/assets/manual/`

**Contents:** Hand-created or sourced assets

**Examples:**
- Scanned textures
- Hand-drawn elements
- Photographed reference materials
- Manually created pixel art

**Format:** PNG preferred, JPEG acceptable for photos

#### `/assets/textures/`

**Contents:** Paper textures and grain patterns

**Examples:**
- `newsprint_grain.png` - Newsprint paper texture
- `uncoated_paper.png` - Uncoated paper texture
- `recycled_texture.png` - Recycled paper texture

**Format:** PNG, grayscale preferred
**Usage:** Applied as displacement maps and overlays

---

### `/config/`

**Purpose:** Configuration files for all aspects of generation

#### `/config/layouts/`

**Contents:** YAML layout files for each spread

**Naming Convention:** `spread_XX_YY.yaml`
- XX = left page number (02, 04, 06, ...)
- YY = right page number (03, 05, 07, ...)

**Example:** `spread_04_05.yaml` defines pages 4-5

**Format:** YAML
**Schema:** See `docs/api/configuration-guide.md`

#### `master_config.yaml`

**Contents:** Global configuration
- Canvas dimensions
- Color palettes
- Font specifications
- Binding parameters
- Print effect settings

**Shared by:** All layout files

---

### `/docs/`

**Purpose:** All project documentation

Organized by category for easy navigation.

#### `/docs/api/`

**Contents:** API reference and usage documentation

**Files:**
- `api-reference.md` - Complete API for all classes
- `configuration-guide.md` - YAML schema documentation
- `usage-examples.md` - Code examples for each component

**Audience:** Developers using the system

#### `/docs/architecture/`

**Contents:** System architecture documentation

**Files:**
- `system-overview.md` - High-level architecture
- `data-flow.md` - Data movement through pipeline
- `directory-structure.md` - This file

**Audience:** Developers and system designers

#### `/docs/curriculum/`

**Contents:** Educational curriculum modules

**Files:**
- Tier 1 modules (1-4)
- Expanded module content
- Additional resources

**Audience:** Students and educators

#### `/docs/design/`

**Contents:** Design philosophy and guidelines

**Files:**
- `designrules3.md` - Design rules and constraints
- `klutz-press-design.md` - Klutz Press style analysis
- `new-stylebook.md` - Updated style guide
- `nickelodeon-goosebumps-design.md` - 90s aesthetic reference

**Audience:** Designers and content creators

#### `/docs/planning/`

**Contents:** Project planning and strategy

**Files:**
- `gemini-klutz-plan-v2.md` - Overall project plan
- `klutz-workbook-action-plan.md` - Actionable task breakdown

**Audience:** Project managers and contributors

#### `/docs/reviews/`

**Contents:** Critical reviews and improvement guides

**Files:**
- `criticism-091425.md` - Critical analysis (Sept 14, 2025)
- `kimi-improvement-guide.md` - Improvement recommendations

**Audience:** Quality reviewers and improvers

#### `/docs/technical/`

**Contents:** Detailed technical implementation documentation

**Files:**
- Individual implementation chapters (1-15)
- Merged implementation documents
- Technical documentation TOC

**Audience:** Developers implementing features

**Note:** Contains both individual chapter files and merged versions for easier reading.

---

### `/output/`

**Purpose:** Generated output files

#### `/output/spreads/`

**Contents:** Individual spread PNG files

**Naming Convention:** `spread_XX_YY.png`

**Format:** PNG, 3400x2200px, 300 DPI
**Size:** ~10-20 MB per spread
**Usage:** Intermediate output, assembled into PDF

#### `/output/workbooks/`

**Contents:** Final assembled PDF workbooks

**Naming Convention:** `Klutz_Workbook_vX.Y.pdf`

**Format:** PDF 1.7
**Size:** ~50-150 MB depending on spread count
**Usage:** Final deliverable

---

### `/prompts/`

**Purpose:** Generated XML prompts for AI image generation

#### `/prompts/spread_XX_YY/`

**Contents:** All prompts for a specific spread

**Naming Convention:**
- `L_<type>_<description>_<number>.xml` (left page)
- `R_<type>_<description>_<number>.xml` (right page)

**Format:** XML
**Size:** ~2-3 KB per prompt
**Usage:** Input for nano-banana image generation

---

### `/temp/`

**Purpose:** Temporary and intermediate files

**Contents:**
- Partially composed spreads
- Cached assets
- Debug output
- Intermediate processing results

**Lifecycle:** Can be deleted and regenerated
**Not tracked:** Should be in .gitignore

---

### `/tests/`

**Purpose:** Automated test suite

#### `/tests/unit/`

**Contents:** Unit tests for individual functions and methods

**Example:**
```python
# test_compositor.py
def test_create_base_canvas():
    compositor = KlutzCompositor()
    canvas = compositor.create_base_canvas()
    assert canvas.width == 3400
    assert canvas.height == 2200
```

#### `/tests/integration/`

**Contents:** Integration tests for complete workflows

**Example:**
```python
# test_pipeline.py
def test_full_spread_generation():
    result = generate_spread('config/layouts/test_spread.yaml')
    assert result.exists()
    assert result.stat().st_size > 1000000  # > 1 MB
```

#### `/tests/fixtures/`

**Contents:** Test data and expected outputs

**Structure:**
- `layouts/` - Test layout YAML files
- `assets/` - Test assets
- `expected/` - Expected output images

---

## File Naming Conventions

### Layout Files

**Pattern:** `spread_XX_YY.yaml`

**Rules:**
- XX and YY are 2-digit page numbers
- XX must be even (left page)
- YY must be odd (right page)
- YY = XX + 1

**Examples:**
- `spread_02_03.yaml` ✓
- `spread_04_05.yaml` ✓
- `spread_2_3.yaml` ✗ (not zero-padded)
- `spread_03_04.yaml` ✗ (wrong order)

### Asset Files

**Pattern:** `<type>_<description>_<number>.png`

**Types:**
- `photo` - Photographic elements
- `pixelart` - Pixel art graphics
- `gui` - GUI recreations
- `doodle` - Hand-drawn doodles
- `container` - Container backgrounds
- `texture` - Texture overlays

**Examples:**
- `photo_mouse_hand_01.png`
- `pixelart_sprite_character_02.png`
- `gui_macpaint_toolbar_01.png`

### Prompt Files

**Pattern:** `<page>_<type>_<description>_<number>.xml`

**Page Prefixes:**
- `L_` - Left page element
- `R_` - Right page element

**Examples:**
- `L_photo_mouse_01.xml`
- `R_container_featurebox_02.xml`

### Output Files

**Spreads:** `spread_XX_YY.png`
**Workbooks:** `Klutz_Workbook_v<major>.<minor>.pdf`

**Examples:**
- `spread_04_05.png`
- `Klutz_Workbook_v1.0.pdf`
- `Klutz_Workbook_v2.1_draft.pdf`

---

## .gitignore Recommendations

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
.env

# Generated output
output/spreads/*.png
output/workbooks/*.pdf

# Temporary files
temp/
*.tmp

# Assets (too large for git)
assets/generated/*.png
assets/manual/*.jpg
assets/manual/*.png

# Prompts (regeneratable)
prompts/*/

# System files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

**Keep in Git:**
- Configuration files (config/)
- Documentation (docs/)
- Source code (*.py)
- Requirements (requirements.txt)
- Small reference assets
- Test fixtures

**Exclude from Git:**
- Generated assets (large, regeneratable)
- Temporary files
- Output files
- Cache files

---

## Disk Space Requirements

### Development Environment

- **Source code:** ~500 KB
- **Documentation:** ~5 MB
- **Configuration:** ~100 KB
- **Fonts:** ~2 MB
- **Manual assets:** ~50 MB
- **Test fixtures:** ~20 MB
- **Total (minimal):** ~80 MB

### Active Generation

- **Generated assets:** ~500 MB (50 assets × ~10 MB each)
- **Prompts:** ~1 MB
- **Temp files:** ~100 MB
- **Output spreads:** ~200 MB (20 spreads × ~10 MB each)
- **Total (active):** ~800 MB

### Complete Project

- **Full asset library:** ~2 GB
- **All output:** ~500 MB
- **Documentation:** ~10 MB
- **Total (complete):** ~3 GB

---

## Navigation Tips

### Finding Files

**By Purpose:**
- Need API docs? → `docs/api/`
- Need implementation details? → `docs/technical/`
- Need design guidelines? → `docs/design/`
- Need to edit a spread? → `config/layouts/`

**By File Type:**
- Python scripts → Root directory
- Configuration → `config/`
- Documentation → `docs/<category>/`
- Assets → `assets/<type>/`

### Quick Access

**Most Common Files:**
```bash
# Main compositor
less klutz_compositor.py

# API reference
less docs/api/api-reference.md

# Example layout
less config/layouts/spread_04_05.yaml

# Master config
less config/master_config.yaml
```

---

## See Also

- [system-overview.md](system-overview.md) - System architecture
- [data-flow.md](data-flow.md) - Data flow through pipeline
- [../api/configuration-guide.md](../api/configuration-guide.md) - Configuration details
