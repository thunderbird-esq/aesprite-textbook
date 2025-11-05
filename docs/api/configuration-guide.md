---
title: Configuration Guide
date: 2025-11-05
status: Active
---

# YAML Configuration Schema

This document describes the YAML configuration schema used throughout the Klutz Workbook project.

## Master Configuration

**File:** `config/master_config.yaml`

### Structure

```yaml
canvas:
  width: 3400              # Total canvas width (pixels)
  height: 2200             # Total canvas height (pixels)
  spine_center: 1700       # X-coordinate of spine center
  spine_width: 462         # Width of spine dead zone
  safe_zone_margin: 150    # Safe zone margin

colors:
  aged_newsprint: "#F8F3E5"
  nickelodeon_orange: "#F57D0D"
  goosebumps_acid: "#95C120"
  klutz_yellow: "#FFD700"
  pure_black: "#000000"

binding:
  type: "spiral"
  pitch: "4:1"             # 4 holes per inch
  hole_diameter: 57        # pixels
  hole_spacing: 18         # pixels between holes

textures:
  paper_grain: 0.08        # Grain opacity (0.0-1.0)
  emboss_depth: 20         # Emboss depth in microns

print_effects:
  cmyk_misregistration: true
  dot_gain: 0.95           # Gamma value for dot gain
  vignette_opacity: 0.15   # Vignette opacity

fonts:
  headline: "Chicago"
  body: "Geneva"
  handwriting: "Tekton"
  code: "Monaco"
```

---

## Layout Configuration

**File:** `config/layouts/spread_XX_YY.yaml`

### Structure

```yaml
spread_info:
  number: "04-05"
  title: "Spread Title"
  template: "workshop_layout"
  canvas: "aged_newsprint"

global_settings:
  color_distribution:
    klutz_primary: 0.72      # 72% primary colors
    nickelodeon_accent: 0.20  # 20% orange accent
    goosebumps_theme: 0.08    # 8% acid green

  texture_settings:
    paper_grain: 0.08
    emboss_depth: 20

  print_settings:
    cmyk_misregistration: true
    dot_gain: 0.95
    vignette_opacity: 0.15

left_page:
  elements:
    - id: "L_headline_01"
      type: "text_headline"
      position: [200, 180]       # [x, y] in pixels
      dimensions: [800, 100]      # [width, height]
      rotation: -3                # degrees
      content: "HEADLINE TEXT"
      font: "Chicago"
      size: 48
      color: "#000000"
      border: "none"
      shadow:
        offset_x: 2
        offset_y: 2
        color: "#808080"

    - id: "L_photo_01"
      type: "graphic_photo_instructional"
      filename: "photo_asset_01.png"
      position: [250, 320]
      dimensions: [400, 300]
      rotation: 2
      border: "4px solid #000000"
      shadow:
        offset_x: 3
        offset_y: 3
        color: "#000000"

right_page:
  elements:
    - id: "R_container_01"
      type: "container_featurebox"
      position: [1931, 200]
      dimensions: [1000, 800]
      background_color: "#FFD700"
      border: "8px solid #000000"

text_blocks:
  - id: "TB_instructions_01"
    position: [300, 600]
    dimensions: [600, 200]
    content: |
      Multi-line text content
      with proper formatting
      and line breaks
    font: "Geneva"
    size: 14
    leading: 20
    color: "#000000"
    simplified_glyphs: true
    apply_texture: true
```

---

## Element Types

### Text Elements

#### `text_headline`
Large headline text with optional rotation and shadow.

**Required fields:**
- `id`, `type`, `position`, `content`, `font`, `size`, `color`

**Optional fields:**
- `dimensions`, `rotation`, `border`, `shadow`

#### `text_body`
Body text blocks with proper leading and glyph handling.

**Required fields:**
- `id`, `type`, `position`, `content`, `font`, `size`

**Optional fields:**
- `leading`, `color`, `simplified_glyphs`, `apply_texture`

### Graphic Elements

#### `graphic_photo_instructional`
Photographed instructional content (hands, objects, etc.).

**Required fields:**
- `id`, `type`, `filename`, `position`

**Optional fields:**
- `dimensions`, `rotation`, `border`, `shadow`

#### `graphic_pixelart`
Pixel art created in MacPaint style.

**Required fields:**
- `id`, `type`, `filename`, `position`

**Optional fields:**
- `dimensions`, `rotation`, `border`, `shadow`, `scale_filter`

#### `graphic_gui_recreation`
Recreation of vintage Macintosh GUI elements.

**Required fields:**
- `id`, `type`, `filename`, `position`

**Optional fields:**
- `dimensions`, `rotation`, `border`, `shadow`

#### `graphic_doodle`
Hand-drawn doodle elements for visual interest.

**Required fields:**
- `id`, `type`, `filename`, `position`

**Optional fields:**
- `dimensions`, `rotation`, `color_override`

### Container Elements

#### `container_featurebox`
Colored box for feature content.

**Required fields:**
- `id`, `type`, `position`, `dimensions`, `background_color`, `border`

**Optional fields:**
- `rotation`, `shadow`

#### `container_embossed_featurebox`
Embossed feature box with physical texture.

**Required fields:**
- `id`, `type`, `position`, `dimensions`, `background_color`, `border`

**Optional fields:**
- `emboss_depth`, `rotation`, `shadow`

#### `graphic_splat_container`
Organic splat-shaped container.

**Required fields:**
- `id`, `type`, `position`, `dimensions`, `color`

**Optional fields:**
- `rotation`, `shape_seed`

---

## Position and Dimension Guidelines

### Canvas Regions

```
Left Page:  X: 0-1469
Dead Zone:  X: 1469-1931
Right Page: X: 1931-3400
```

### Safe Zones

Content should remain within:
- Left page: X: 150-1319, Y: 150-2050
- Right page: X: 2081-3250, Y: 150-2050

### Element Rotation Limits

- Text elements: ±5 degrees maximum
- Image elements: ±15 degrees maximum
- Container elements: ±10 degrees maximum

---

## Color Specifications

### Primary Klutz Colors
- Red: `#FF0000`
- Blue: `#0000FF`
- Yellow: `#FFFF00`
- Green: `#00FF00`
- Orange: `#FFA500`
- Purple: `#800080`

### Accent Colors
- Nickelodeon Orange: `#F57D0D` (max 30% coverage)
- Goosebumps Acid Green: `#95C120` (max 10% coverage)

### Background Colors
- Aged Newsprint: `#F8F3E5`
- Pure Black: `#000000`

---

## Font Specifications

### Available Fonts

| Font Name | Usage | Size Range | Notes |
|-----------|-------|------------|-------|
| Chicago | Headlines | 36-72pt | Macintosh system font |
| Geneva | Body text | 10-16pt | Readable, period-accurate |
| Tekton | Handwriting | 12-24pt | Casual, friendly |
| Monaco | Code | 9-12pt | Monospace, technical |
| Courier | Typewriter | 10-14pt | Mechanical look |

### Leading (Line Height)

- Headlines: font_size + 4pt
- Body text: font_size + 6pt
- Code blocks: font_size + 2pt

---

## Border Specifications

### Format

```
"<width>px solid <color>"
```

### Examples

```yaml
border: "4px solid #000000"    # Thin black border
border: "8px solid #F57D0D"    # Thick orange border
border: "2px solid #FFFFFF"    # Thin white border
border: "none"                  # No border
```

---

## Shadow Specifications

### Hard Shadow (Period-Accurate)

```yaml
shadow:
  offset_x: 3         # Horizontal offset (pixels)
  offset_y: 3         # Vertical offset (pixels)
  color: "#000000"    # Shadow color (hex)
```

### Notes

- All shadows must be hard-edged (no blur)
- Typical offsets: 2-5 pixels
- Shadow color usually black or dark gray

---

## Validation Rules

### Enforced by AssetValidator

1. No anachronistic terms in prompts
2. No soft shadows or gradients
3. Color distribution within limits
4. No spine intrusion
5. Rotation within limits
6. Maximum image dimensions: 1200x1200px

---

## Example: Complete Spread Configuration

See `config/layouts/spread_04_05.yaml` for a complete, working example.

---

## Configuration Best Practices

1. **Use descriptive IDs**: `L_headline_pixelart_01` not `h1`
2. **Comment complex sections**: Explain why non-standard values are used
3. **Validate before generation**: Run `AssetValidator.validate_layout()` first
4. **Keep backups**: Version control all configuration files
5. **Test incrementally**: Add elements one at a time to isolate issues

---

## See Also

- [api-reference.md](api-reference.md) - API documentation
- [usage-examples.md](usage-examples.md) - Code examples
- [../technical/](../technical/) - Technical implementation details
