---
title: API Reference
date: 2025-11-05
status: Active
---

# Klutz Workbook Project - API Reference

This document provides a comprehensive reference for all public classes and methods in the Klutz Workbook generation system.

## Table of Contents

- [KlutzCompositor](#klutzcompositor)
- [AssetValidator](#assetvalidator)
- [PromptGenerator](#promptgenerator)
- [PostProcessor](#postprocessor)
- [GeminiIntegration](#geminiintegration)
- [NanoBananaIntegration](#nanobananaintegration)
- [QualityAssurance](#qualityassurance)
- [ProductionMonitoring](#productionmonitoring)
- [PerformanceOptimization](#performanceoptimization)
- [DeployWorkbook](#deployworkbook)

---

## KlutzCompositor

**File:** `klutz_compositor.py`

Main composition engine for creating Klutz workbook pages with period-accurate visual styling.

### Class: `KlutzCompositor`

**Constructor:**
```python
KlutzCompositor(config_path='config/master_config.yaml')
```

Initializes the compositor with canvas specifications and color palettes.

**Parameters:**
- `config_path` (str): Path to master YAML configuration file

**Attributes:**
- `canvas_width` (int): Canvas width in pixels (3400)
- `canvas_height` (int): Canvas height in pixels (2200)
- `spine_center` (int): X-coordinate of spiral binding center (1700)
- `spine_width` (int): Width of spine dead zone in pixels (462)
- `safe_zone_margin` (int): Safe zone margin in pixels (150)
- `colors` (dict): Dictionary of named color tuples

### Methods

#### `create_base_canvas(template='aged_newsprint')`

Creates the base canvas with paper texture and spiral binding.

**Parameters:**
- `template` (str): Color template name (default: 'aged_newsprint')

**Returns:**
- PIL.Image: Base canvas with texture and binding

#### `generate_paper_texture()`

Generates procedural uncoated paper texture using Perlin noise.

**Returns:**
- PIL.Image: Texture overlay image

#### `add_spiral_binding(canvas)`

Adds photorealistic spiral binding holes with 4:1 pitch specification.

**Parameters:**
- `canvas` (PIL.Image): Canvas to add binding to

**Returns:**
- PIL.Image: Canvas with binding added

#### `load_and_process_asset(asset_config)`

Loads an asset and applies transformations (rotation, borders, shadows).

**Parameters:**
- `asset_config` (dict): Asset configuration dictionary containing:
  - `filename` (str): Asset filename
  - `dimensions` (tuple, optional): Target dimensions
  - `rotation` (float, optional): Maximum rotation angle
  - `border` (str, optional): Border specification
  - `shadow` (dict, optional): Shadow parameters

**Returns:**
- PIL.Image: Processed asset image

#### `composite_element(canvas, element, position)`

Composites an element onto the canvas at specified position, avoiding spine dead zone.

**Parameters:**
- `canvas` (PIL.Image): Canvas to composite onto
- `element` (PIL.Image): Element to composite
- `position` (tuple): (x, y) position tuple

**Returns:**
- PIL.Image: Canvas with element composited

#### `compose_spread(layout_config)`

Main method to compose a complete two-page spread.

**Parameters:**
- `layout_config` (dict): Complete layout configuration

**Returns:**
- PIL.Image: Completed spread image

---

## AssetValidator

**File:** `asset_validator.py`

Validates all assets meet period-authentic specifications (1996 era).

### Class: `AssetValidator`

**Constructor:**
```python
AssetValidator()
```

Initializes validator with forbidden terms and color specifications.

### Methods

#### `validate_prompt(prompt_text)`

Checks prompt text for anachronistic terms and missing required terminology.

**Parameters:**
- `prompt_text` (str): Prompt text to validate

**Returns:**
- list[str]: List of violation messages (empty if valid)

#### `validate_image_asset(image_path)`

Validates an image meets dimensional, color, and style specifications.

**Parameters:**
- `image_path` (str): Path to image file

**Returns:**
- list[str]: List of violation messages (empty if valid)

#### `check_forbidden_effects(image)`

Detects modern effects that shouldn't exist (gradients, soft shadows, transparency).

**Parameters:**
- `image` (PIL.Image): Image to check

**Returns:**
- list[str]: List of detected forbidden effects

#### `check_color_distribution(image)`

Verifies color usage follows 70/20/10 rule.

**Parameters:**
- `image` (PIL.Image): Image to analyze

**Returns:**
- list[str]: List of color distribution violations

#### `validate_layout(layout_config)`

Validates a complete layout configuration for spine intrusion and rotation limits.

**Parameters:**
- `layout_config` (dict): Layout configuration dictionary

**Returns:**
- list[str]: List of layout violations

#### `validate_complete_project(project_dir)`

Runs all validations on entire project directory.

**Parameters:**
- `project_dir` (str): Path to project directory

**Returns:**
- dict: Validation report with violations and summary statistics

---

## PromptGenerator

**File:** `prompt_generator.py`

Generates hyper-specific XML prompts for nano-banana image generation via Gemini.

### Class: `PromptGenerator`

**Constructor:**
```python
PromptGenerator()
```

Initializes generator with master configuration and prompt templates.

### Methods

#### `generate_prompt(element_config)`

Generates a complete XML prompt for an element.

**Parameters:**
- `element_config` (dict): Element configuration from layout YAML

**Returns:**
- str: XML-formatted prompt string

#### `generate_photo_prompt(config)`

Generates prompt for instructional photography elements.

**Parameters:**
- `config` (dict): Photo element configuration

**Returns:**
- str: Photo-specific prompt

#### `generate_container_prompt(config)`

Generates prompt for container/featurebox elements.

**Parameters:**
- `config` (dict): Container element configuration

**Returns:**
- str: Container-specific prompt

---

## PostProcessor

**File:** `post_processor.py`

Applies post-processing effects to simulate 1996 printing technology.

### Class: `PostProcessor`

**Methods:**

#### `apply_cmyk_misregistration(image)`

Applies CMYK channel shifts to simulate printing misregistration.

**Parameters:**
- `image` (PIL.Image): Input image

**Returns:**
- PIL.Image: Image with misregistration applied

#### `apply_dot_gain(image, gamma=0.95)`

Simulates dot gain on uncoated paper.

**Parameters:**
- `image` (PIL.Image): Input image
- `gamma` (float): Gamma correction value

**Returns:**
- PIL.Image: Image with dot gain applied

#### `add_vignette(image, opacity=0.15)`

Adds circular vignette to simulate photographed book.

**Parameters:**
- `image` (PIL.Image): Input image
- `opacity` (float): Vignette opacity (0.0-1.0)

**Returns:**
- PIL.Image: Image with vignette applied

---

## GeminiIntegration

**File:** `gemini_integration.py`

Handles integration with Google Gemini API for prompt refinement.

### Class: `GeminiIntegration`

**Methods:**

#### `refine_prompt(base_prompt)`

Refines a base prompt using Gemini API.

**Parameters:**
- `base_prompt` (str): Base prompt to refine

**Returns:**
- str: Refined prompt

---

## NanoBananaIntegration

**File:** `nano_banana_integration.py`

Handles integration with nano-banana image generation service.

### Class: `NanoBananaIntegration`

**Methods:**

#### `generate_image(prompt, dimensions)`

Generates an image using nano-banana service.

**Parameters:**
- `prompt` (str): XML prompt
- `dimensions` (tuple): (width, height) tuple

**Returns:**
- PIL.Image: Generated image

---

## QualityAssurance

**File:** `quality_assurance.py`

Quality assurance checks for generated spreads.

### Class: `QualityAssurance`

**Methods:**

#### `check_spread_quality(spread_image)`

Runs comprehensive quality checks on a spread.

**Parameters:**
- `spread_image` (PIL.Image): Spread to check

**Returns:**
- dict: Quality metrics and pass/fail status

---

## ProductionMonitoring

**File:** `production_monitoring.py`

Monitors production pipeline and logs metrics.

### Class: `ProductionMonitoring`

**Methods:**

#### `log_generation_time(spread_id, duration)`

Logs generation time for a spread.

**Parameters:**
- `spread_id` (str): Spread identifier
- `duration` (float): Generation time in seconds

---

## PerformanceOptimization

**File:** `performance_optimization.py`

Performance optimization utilities for batch processing.

### Class: `PerformanceOptimization`

**Methods:**

#### `optimize_batch_processing(spread_configs)`

Optimizes batch processing of multiple spreads.

**Parameters:**
- `spread_configs` (list): List of spread configurations

**Returns:**
- list: Optimized processing order

---

## DeployWorkbook

**File:** `deploy_workbook.py`

Deployment utilities for final workbook assembly.

### Class: `DeployWorkbook`

**Methods:**

#### `assemble_workbook(spread_images)`

Assembles individual spreads into complete workbook PDF.

**Parameters:**
- `spread_images` (list): List of spread image paths

**Returns:**
- str: Path to assembled PDF

---

## Configuration Schema

See [configuration-guide.md](configuration-guide.md) for detailed YAML schema documentation.

## Usage Examples

See [usage-examples.md](usage-examples.md) for code examples demonstrating each component.
