# KlutzCompositor Usage Guide

## Overview

The `klutz_compositor.py` module implements the complete compositor engine for assembling Klutz-style workbook spreads. It handles all aspects of page composition, from base canvas creation to final print artifact simulation.

**Total Implementation:** 807 lines of Python

## Features

### Core Capabilities

1. **Base Canvas Generation**
   - Aged newsprint paper color (#F8F3E5)
   - Realistic paper texture using NumPy noise
   - Photorealistic 4:1 pitch spiral binding
   - Page curvature shadow near spine

2. **Asset Processing**
   - Load graphics from `assets/generated/`
   - High-quality resize (Lanczos resampling)
   - Deterministic chaos rotation (hash-based)
   - Hard-edged borders (1996 style)
   - Automatic format conversion to RGBA

3. **Typography Engine**
   - Programmatic text rendering with TTF fonts
   - Intelligent word wrapping
   - Precise leading (line spacing) control
   - Configurable font size and color

4. **Layout Intelligence**
   - Spine intrusion detection
   - Automatic position adjustment
   - Z-order control via element sequence
   - Safe zone enforcement

5. **Print Artifact Simulation**
   - CMYK misregistration (+1px magenta, -1px yellow)
   - Dot gain (gamma 0.95 for ink spread)
   - Radial vignette (natural light falloff)
   - Authentic 1996 offset printing look

## Installation

### Requirements

```bash
pip install pillow pyyaml numpy
```

### Directory Structure

```
aesprite-textbook/
├── klutz_compositor.py
├── config/
│   ├── master_config.yaml
│   └── layouts/
│       └── spread_04_05.yaml
├── assets/
│   ├── generated/          # Generated image assets
│   │   ├── photo_mouse_hand_01.png
│   │   └── aseprite_color_picker_01.png
│   ├── fonts/              # TrueType fonts
│   │   ├── Chicago.ttf
│   │   └── Helvetica.ttf
│   └── textures/           # Paper textures (future)
└── output/                 # Rendered spreads
```

## Quick Start

### Basic Usage

```bash
# Compose a spread with all effects
python klutz_compositor.py config/layouts/spread_04_05.yaml output/spread_04_05.png
```

### Without Print Artifacts (Testing)

```bash
# Faster rendering for layout testing
python klutz_compositor.py config/layouts/spread_04_05.yaml output/test.png --no-artifacts
```

### Custom Configuration

```bash
# Use alternate config file
python klutz_compositor.py layout.yaml output.png --config my_config.yaml
```

### Verbose Logging

```bash
# Enable debug output
python klutz_compositor.py layout.yaml output.png --verbose
```

## Layout YAML Format

### Complete Example

```yaml
# spread_04_05.yaml
template: "workshop_layout"
canvas: "aged_newsprint"

left_page:
  elements:
    - id: "L_headline_pixelart_01"
      type: "text_headline"
      position: [200, 180]
      dimensions: [800, 100]
      rotation: 0
      content: "PIXEL PERFECT!"
      font: "Chicago"
      size: 48
      color: "#000000"

    - id: "L_photo_mouse_01"
      type: "graphic_photo_instructional"
      asset: "photo_mouse_hand_01.png"
      position: [250, 300]
      dimensions: [600, 450]
      rotation: 2
      border: "4px solid #F57D0D"

    - id: "L_textcontainer_intro_01"
      type: "text_body"
      position: [180, 800]
      dimensions: [900, 400]
      rotation: -1
      content: |
        Time to make some pixel art! Remember those awesome
        Nintendo characters? They're just colored squares
        arranged in a grid.
      font: "Helvetica"
      size: 16
      leading: 22
      color: "#000000"

right_page:
  elements:
    - id: "R_gui_aseprite_01"
      type: "graphic_gui_recreation"
      asset: "aseprite_color_picker_01.png"
      position: [1950, 200]
      dimensions: [1200, 800]
      rotation: 0
```

### Element Types

#### Text Elements

- `text_headline`: Large display text
- `text_body`: Paragraph content
- `text_caption`: Small annotations

**Required fields:**
- `id`: Unique identifier
- `type`: Element type
- `position`: [x, y] coordinates
- `dimensions`: [width, height] for text area
- `content`: Text string (supports multiline with `|`)
- `font`: Font name (without .ttf)
- `size`: Font size in points

**Optional fields:**
- `rotation`: Max rotation in degrees (uses chaos rotation)
- `color`: Hex color (default: #000000)
- `leading`: Line spacing override

#### Graphic Elements

- `graphic_photo_instructional`: Photos of hands/peripherals
- `graphic_gui_recreation`: Screenshots of software
- `graphic_pixelart`: Pixel art sprites
- `graphic_splat_container`: Nickelodeon-style shapes
- `graphic_doodle`: Hand-drawn elements

**Required fields:**
- `id`: Unique identifier
- `type`: Element type
- `asset`: Filename in assets/generated/
- `position`: [x, y] coordinates

**Optional fields:**
- `dimensions`: [width, height] for resize
- `rotation`: Max rotation in degrees
- `border`: "Npx solid #RRGGBB" format

## Configuration Reference

### master_config.yaml Structure

```yaml
technical:
  canvas_size: [3400, 2200]  # Two-page spread dimensions
  dpi: 300
  spine_width: 462  # Dead zone at center

aesthetic_rules:
  palettes:
    klutz_primary:
      red: "#ED1C24"
      blue: "#0080C9"
      yellow: "#FFD500"
    nickelodeon_accent:
      orange: "#F57D0D"  # The iconic splat
    goosebumps_theme:
      acid_green: "#95C120"

  texture_opacity:
    global: 0.12
    displacement: 0.05

print_simulation:
  cmyk_shift:
    magenta: [1, 0]
    yellow: [0, -1]
  dot_gain: 0.95
  vignette: 0.3
  spine_shadow: 0.15

rotation:
  max_rotation:
    photo: 5.0
    doodle: 15.0
    text_block: 2.0
    splat: 180.0
```

## Python API

### Basic Usage

```python
from klutz_compositor import KlutzCompositor

# Initialize compositor
compositor = KlutzCompositor(config_path='config/master_config.yaml')

# Compose spread
spread = compositor.compose_spread(
    'config/layouts/spread_04_05.yaml',
    apply_artifacts=True
)

# Save output
spread.save('output/spread_04_05.png', 'PNG')
```

### Advanced Usage

```python
from klutz_compositor import KlutzCompositor
from PIL import Image

# Initialize
compositor = KlutzCompositor()

# Create custom canvas
canvas = compositor.create_base_canvas(template='aged_newsprint')

# Load and process asset
asset_config = {
    'asset': 'photo_mouse_hand_01.png',
    'id': 'test_element',
    'dimensions': [600, 450],
    'rotation': 5.0,
    'border': '4px solid #F57D0D'
}
element = compositor.load_and_process_asset(asset_config)

# Composite element
canvas = compositor.composite_element(
    canvas=canvas,
    element=element,
    position=(250, 300),
    element_id='test_element'
)

# Apply print effects
final = compositor.apply_print_artifacts(canvas)

# Save
final.save('output/custom_spread.png')
```

### Text Rendering

```python
# Render programmatic text
text_config = {
    'content': 'Hello Klutz World!',
    'font': 'Chicago',
    'size': 48,
    'dimensions': [800, 100],
    'color': '#000000',
    'leading': 60
}

text_img = compositor.render_text_block(text_config)
```

### Deterministic Rotation

```python
# Get repeatable rotation for element
rotation = compositor.get_chaos_rotation('L_photo_01', max_rotation=5.0)
# 'L_photo_01' always returns same value: e.g., -3.24°
```

## Method Reference

### KlutzCompositor Class

#### `__init__(self, config_path='config/master_config.yaml')`
Initialize compositor with configuration.

#### `get_chaos_rotation(self, element_id: str, max_rotation: float) -> float`
Generate deterministic rotation based on element ID hash.

#### `create_base_canvas(self, template='aged_newsprint') -> Image`
Create base canvas with paper texture, binding, and shadows.

#### `add_spiral_binding(self, canvas: Image) -> Image`
Add photorealistic 4:1 pitch spiral binding.

#### `add_page_curvature(self, canvas: Image) -> Image`
Add shadow gradient near spine for page depth.

#### `load_and_process_asset(self, asset_config: Dict) -> Image`
Load asset and apply transformations (resize, rotate, border).

#### `render_text_block(self, text_config: Dict) -> Image`
Render text programmatically with word wrapping.

#### `composite_element(self, canvas: Image, element: Image, position: Tuple[int, int], element_id: str) -> Image`
Paste element onto canvas with spine intrusion detection.

#### `apply_print_artifacts(self, image: Image) -> Image`
Apply CMYK shift, dot gain, and vignette effects.

#### `compose_spread(self, layout_path: str, apply_artifacts=True) -> Image`
Main composition method - orchestrates entire pipeline.

## Technical Details

### Spine Dead Zone

The compositor automatically detects when elements would intrude into the spine dead zone (462px wide at canvas center) and adjusts their position:

- Elements on left page: moved further left
- Elements on right page: moved further right
- Buffer distance: 10px

```python
# Automatic adjustment logged:
# WARNING: Element 'L_photo_01' intrudes into spine dead zone.
# Original position: (1050, 300)
# Adjusted position: (837, 300) [moved left]
```

### Deterministic Rotation

Uses MD5 hash of element ID as random seed:

```python
seed = int(hashlib.md5(element_id.encode()).hexdigest(), 16) % (2**32)
random.seed(seed)
rotation = random.uniform(-max_rotation, max_rotation)
```

This ensures:
- Same element ID = same rotation every render
- Different IDs = different rotations
- Repeatable builds
- Git-trackable results

### Print Artifact Details

**CMYK Misregistration:**
- Simulates printing press registration errors
- Red channel (magenta): +1px horizontal
- Blue channel (yellow): -1px vertical
- Creates subtle color fringing

**Dot Gain:**
- Simulates ink spread on uncoated paper
- Gamma adjustment: 0.95
- Slightly darkens and saturates

**Vignette:**
- Radial gradient from center
- Intensity: 0.3 (configurable)
- Simulates natural light falloff

## Troubleshooting

### Common Issues

**FileNotFoundError: Asset not found**
```
Error: Asset not found: assets/generated/photo_mouse_hand_01.png
```
Solution: Ensure all referenced assets exist in `assets/generated/`

**FileNotFoundError: Font not found**
```
Error: Font not found: assets/fonts/Chicago.ttf
```
Solution: Install required TTF fonts in `assets/fonts/`

**Element intrusion warnings**
```
WARNING: Element 'L_photo_01' intrudes into spine dead zone.
```
Solution: Adjust element position in YAML, or allow auto-adjustment

**Text overflow**
```
Text extends beyond specified dimensions
```
Solution: Increase `dimensions` height or reduce `size`/`leading`

## Performance

### Typical Render Times

- Base canvas creation: ~0.5s
- Asset loading/processing: ~0.1s per element
- Text rendering: ~0.05s per block
- Print artifacts: ~1.0s
- **Total for 2-page spread: ~3-5 seconds**

### Optimization Tips

1. Use `--no-artifacts` flag during layout testing
2. Pre-process assets to exact dimensions
3. Cache base canvas templates
4. Use smaller canvas size for proofs (scale config values)

## Examples

### Example 1: Minimal Spread

```yaml
canvas: "aged_newsprint"
left_page:
  elements:
    - id: "L_title"
      type: "text_headline"
      position: [200, 200]
      dimensions: [800, 100]
      content: "Hello World"
      font: "Chicago"
      size: 48

right_page:
  elements: []
```

### Example 2: Photo-Heavy Layout

```yaml
canvas: "aged_newsprint"
left_page:
  elements:
    - id: "L_photo_01"
      type: "graphic_photo_instructional"
      asset: "photo_keyboard.png"
      position: [150, 200]
      dimensions: [1000, 750]
      rotation: 3
      border: "6px solid #ED1C24"
```

### Example 3: Text-Heavy Layout

```yaml
canvas: "aged_newsprint"
left_page:
  elements:
    - id: "L_body_01"
      type: "text_body"
      position: [200, 200]
      dimensions: [1000, 1800]
      rotation: 0
      content: |
        Welcome to the world of computer graphics!
        In this workbook, you'll learn how to create
        amazing pixel art, just like the pros.

        Let's get started!
      font: "Helvetica"
      size: 18
      leading: 28
      color: "#000000"
```

## Future Enhancements

Planned features for future versions:

- [ ] Paper texture displacement for text
- [ ] Hard-edged shadow rendering
- [ ] Embossed container effects
- [ ] Multiple page template support
- [ ] Batch composition mode
- [ ] Asset library management
- [ ] Live preview server

## Support

For issues or questions:
- Check logs with `--verbose` flag
- Review YAML syntax
- Verify asset paths
- Check config values

## License

Part of the Klutz Press Computer Graphics Workbook project.
