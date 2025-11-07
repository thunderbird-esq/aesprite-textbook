---
title: System Overview
date: 2025-11-05
status: Active
---

# Klutz Workbook Project - System Architecture

## Overview

The Klutz Workbook generation system is a multi-stage pipeline that creates period-accurate (1996-era) educational workbook pages using modern AI image generation and composition techniques.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KLUTZ WORKBOOK PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   YAML       │
│  Layouts     │──┐
└──────────────┘  │
                  │    ┌──────────────────┐
┌──────────────┐  │    │  Prompt          │
│   Master     │  ├───▶│  Generator       │
│   Config     │──┘    └──────────────────┘
└──────────────┘              │
                              ▼
                       ┌──────────────────┐
                       │  Gemini API      │
                       │  (Refinement)    │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  nano-banana     │
                       │  (Generation)    │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Asset           │
                       │  Validator       │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
┌──────────────┐      │  Generated       │
│  Manual      │─────▶│  Assets          │
│  Assets      │      │  (PNG files)     │
└──────────────┘      └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Klutz           │
                       │  Compositor      │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Post            │
                       │  Processor       │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Quality         │
                       │  Assurance       │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Final Spread    │
                       │  (PNG 3400x2200) │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Workbook        │
                       │  Assembly (PDF)  │
                       └──────────────────┘
```

## Core Components

### 1. Configuration Layer

**Purpose:** Central configuration management

**Components:**
- `master_config.yaml` - Canvas specs, colors, fonts, binding
- `layouts/*.yaml` - Individual spread layouts
- `config/` directory structure

**Responsibilities:**
- Define canvas dimensions and dead zones
- Specify color palettes and limits
- Configure typography and fonts
- Set print effect parameters

### 2. Prompt Generation

**Purpose:** Generate hyper-specific prompts for AI image generation

**Components:**
- `prompt_generator.py` - Main prompt generation engine
- Template system for different element types

**Responsibilities:**
- Parse layout YAML configurations
- Generate XML-formatted prompts
- Ensure period-accurate terminology
- Include component-specific details

**Input:** Layout YAML + Master Config
**Output:** XML prompt files

### 3. AI Integration

**Purpose:** Interface with AI services for image generation

**Components:**
- `gemini_integration.py` - Gemini API for prompt refinement
- `nano_banana_integration.py` - nano-banana for image generation

**Responsibilities:**
- Refine prompts for clarity and specificity
- Generate images from refined prompts
- Handle API authentication and rate limiting
- Manage generation parameters

**Input:** XML prompts
**Output:** Raw generated images

### 4. Asset Validation

**Purpose:** Ensure all assets meet period-authentic specifications

**Components:**
- `asset_validator.py` - Comprehensive validation system

**Responsibilities:**
- Check prompts for anachronistic terms
- Validate image dimensions and colors
- Detect forbidden effects (gradients, soft shadows)
- Verify color distribution ratios
- Enforce rotation and positioning limits

**Input:** Prompts and images
**Output:** Validation reports

### 5. Composition Engine

**Purpose:** Assemble final spread from individual assets

**Components:**
- `klutz_compositor.py` - Main compositor

**Responsibilities:**
- Create base canvas with paper texture
- Add spiral binding holes (4:1 pitch)
- Composite all elements at specified positions
- Apply borders and hard shadows
- Handle spine dead zone avoidance
- Render text with period-accurate fonts

**Input:** Layout YAML + validated assets
**Output:** Composed spread (pre-effects)

### 6. Post-Processing

**Purpose:** Apply print artifacts and aging effects

**Components:**
- `post_processor.py` - Print effect simulator

**Responsibilities:**
- Apply CMYK misregistration (1-2px channel shift)
- Simulate dot gain on uncoated paper
- Add vignette for photographed book effect
- Apply subtle color shifts for aged look

**Input:** Composed spread
**Output:** Final spread with print effects

### 7. Quality Assurance

**Purpose:** Automated quality checks on final spreads

**Components:**
- `quality_assurance.py` - QA automation

**Responsibilities:**
- Check for spine intrusion
- Verify color balance
- Measure element contrast
- Ensure readability
- Generate quality reports

**Input:** Final spread
**Output:** Pass/fail + metrics

### 8. Production Support

**Purpose:** Monitoring, optimization, and deployment

**Components:**
- `production_monitoring.py` - Metrics and logging
- `performance_optimization.py` - Batch processing optimization
- `deploy_workbook.py` - Final PDF assembly

**Responsibilities:**
- Log generation times and metrics
- Optimize batch processing order
- Monitor API usage and costs
- Assemble spreads into final PDF
- Generate production reports

## Data Flow

### Detailed Generation Flow

1. **Layout Definition**
   - Designer creates YAML layout file
   - Specifies all elements with positions, sizes, rotations
   - References manual assets and defines AI-generated needs

2. **Prompt Generation**
   - PromptGenerator reads layout YAML
   - For each AI-generated element:
     - Selects appropriate template
     - Populates with element-specific details
     - Adds period-accurate constraints
     - Outputs XML prompt file

3. **Prompt Refinement**
   - GeminiIntegration receives base prompts
   - Refines for clarity and specificity
   - Adds contextual details
   - Returns enhanced prompts

4. **Image Generation**
   - NanoBananaIntegration receives refined prompts
   - Generates images at specified dimensions
   - Returns raw PNG files
   - Saves to assets/generated/

5. **Asset Validation**
   - AssetValidator checks all prompts and images
   - Identifies violations of period authenticity
   - Generates violation reports
   - Flags assets needing regeneration

6. **Composition**
   - KlutzCompositor loads layout configuration
   - Creates base canvas with paper texture and binding
   - For each element:
     - Loads asset (manual or generated)
     - Applies transformations (rotation, borders, shadows)
     - Checks spine dead zone
     - Composites onto canvas
   - Renders text blocks with period fonts
   - Returns composed spread

7. **Post-Processing**
   - PostProcessor applies print effects:
     - CMYK misregistration
     - Dot gain simulation
     - Vignette overlay
   - Returns final spread

8. **Quality Assurance**
   - QualityAssurance runs automated checks
   - Generates metrics report
   - Flags issues for review
   - Approves or rejects spread

9. **Assembly**
   - DeployWorkbook collects all approved spreads
   - Assembles in correct page order
   - Generates final PDF
   - Adds metadata and bookmarks

## Canvas Specifications

### Two-Page Spread Layout

```
                    3400px total width
    ├───────────────────────────────────────────────┤

    ┌─────────────┬──────┬─────────────┐
    │             │      │             │
    │             │      │             │
    │  LEFT PAGE  │SPINE │ RIGHT PAGE  │  2200px
    │             │      │             │
    │             │      │             │
    └─────────────┴──────┴─────────────┘

    ├────1469px───┤462px ├────1469px───┤

    Safe Zone Margins: 150px all sides
    Binding: 4:1 pitch spiral (57px holes, 18px spacing)
```

### Coordinate System

- **Origin:** Top-left corner (0, 0)
- **Left Page:** X: 0-1469, Y: 0-2200
- **Spine Dead Zone:** X: 1469-1931, Y: 0-2200
- **Right Page:** X: 1931-3400, Y: 0-2200
- **Safe Zones:**
  - Left: X: 150-1319, Y: 150-2050
  - Right: X: 2081-3250, Y: 150-2050

## Technology Stack

### Core Technologies

- **Python 3.8+** - Main programming language
- **PIL/Pillow** - Image manipulation and composition
- **NumPy** - Numerical operations and texture generation
- **YAML** - Configuration file format
- **Google Gemini API** - Prompt refinement
- **nano-banana** - Image generation service

### Key Libraries

```python
PIL (Pillow)      # Image manipulation
  - Image         # Core image class
  - ImageDraw     # Drawing primitives
  - ImageFont     # Typography
  - ImageFilter   # Blur, sharpen, etc.
  - ImageEnhance  # Brightness, contrast, color

numpy             # Array operations
  - Array math for textures
  - Channel manipulation
  - Displacement mapping

yaml              # Configuration parsing
  - safe_load() for security
  - safe_dump() for generation

pathlib           # File system operations
  - Path for cross-platform paths
  - glob() for file finding

hashlib           # Deterministic randomization
  - md5() for element seeds

re                # Regular expressions
  - Pattern matching in validation
```

## Design Patterns

### 1. Configuration-Driven Design

All spread layouts are defined in YAML, allowing non-programmers to create new spreads without code changes.

### 2. Pipeline Architecture

Each stage has a single responsibility and can be run independently or as part of the full pipeline.

### 3. Validation at Every Stage

Validation occurs at prompt generation, image generation, and composition to catch issues early.

### 4. Deterministic Chaos

Rotations and positions use element IDs as random seeds, ensuring consistent results across runs.

### 5. Separation of Concerns

- **Configuration** - YAML files
- **Logic** - Python classes
- **Assets** - PNG files
- **Output** - PNG spreads and PDF

## Scalability

### Parallel Processing

Individual spreads are independent and can be generated in parallel:

```python
from multiprocessing import Pool

def generate_spread(layout_path):
    # ... generation code ...
    return spread

with Pool(8) as pool:
    spreads = pool.map(generate_spread, layout_paths)
```

### Caching

- Generated assets are cached by prompt hash
- Composition results can be cached by layout hash
- Reduces regeneration time for iterations

### Optimization

- Batch API calls to reduce overhead
- Preload fonts and textures
- Reuse compositor instances
- Use appropriate image formats (PNG vs JPEG)

## Error Handling

### Graceful Degradation

- Missing assets trigger warnings, not failures
- Validation violations are logged but generation continues
- Quality assurance flags issues without blocking

### Recovery Mechanisms

- Failed generations are retried with adjusted parameters
- Validation failures trigger automatic regeneration
- Spine intrusion is automatically corrected

## Testing Strategy

### Unit Tests

- Test individual methods in isolation
- Mock external API calls
- Validate calculations (spine zones, rotations, etc.)

### Integration Tests

- Test full pipeline with sample layouts
- Verify asset validation catches known violations
- Ensure composition produces expected output

### Visual Regression Tests

- Compare generated spreads to approved references
- Flag visual differences beyond tolerance
- Require human approval for changes

## Deployment

### Development Workflow

1. Create layout YAML
2. Generate prompts
3. Review and refine prompts
4. Generate assets
5. Validate assets
6. Compose spread
7. Review output
8. Iterate as needed

### Production Workflow

1. Batch generate all spreads
2. Run quality assurance
3. Manual review of flagged spreads
4. Assemble approved spreads into PDF
5. Generate production report

## Performance Metrics

### Target Performance

- Prompt generation: < 1s per element
- Image generation: < 30s per element (API dependent)
- Composition: < 5s per spread
- Post-processing: < 2s per spread
- Full spread: < 3 minutes (including AI generation)

### Bottlenecks

- **AI generation** - Slowest step, API rate limited
- **Validation** - Can be cached for repeated assets
- **Composition** - Negligible with proper optimization

## See Also

- [data-flow.md](data-flow.md) - Detailed data flow diagrams
- [directory-structure.md](directory-structure.md) - Project organization
- [../api/](../api/) - API reference documentation
- [../technical/](../technical/) - Implementation details
