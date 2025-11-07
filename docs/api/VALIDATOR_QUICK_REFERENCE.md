# Asset Validator - Quick Reference Guide

## Quick Start

```bash
# Validate a prompt file
python asset_validator.py --prompt path/to/prompt.txt

# Validate an image
python asset_validator.py --image path/to/image.png

# Validate a layout
python asset_validator.py --layout path/to/layout.yaml

# Enable verbose output
python asset_validator.py --image path/to/image.png --verbose
```

## Configuration with --config Flag

The `--config` flag allows you to customize validation rules by providing a custom configuration file. This is useful for different projects or validation scenarios.

### Default Configuration

By default, AssetValidator uses `config/master_config.yaml`:

```bash
# These are equivalent:
python asset_validator.py --prompt path/to/prompt.txt
python asset_validator.py --prompt path/to/prompt.txt --config config/master_config.yaml
```

If the config file is not found, the validator will use built-in defaults.

### Custom Configuration Usage

```bash
# Use a custom config file for specific validation rules
python asset_validator.py --layout spread.yaml --config my_config.yaml

# Validate with a project-specific configuration
python asset_validator.py --image photo.png --config projects/project_a/config.yaml

# Use custom config with verbose output
python asset_validator.py --prompt prompt.txt --config custom_rules.yaml --verbose
```

### Configuration File Structure

A valid configuration file must be a YAML file with the following structure:

```yaml
# master_config.yaml
# Master Configuration for validation rules

project:
  name: "Your Project Name"
  year: 1996
  pages: 20

technical:
  canvas_size: [3400, 2200]    # Two-page spread dimensions in pixels
  spine_width: 462             # Spine dead zone width (center binding area)
  dpi: 300                     # Print-quality resolution
  color_space: "sRGB"          # Color space standard

aesthetic_rules:
  # Color distribution ratios (must sum to 1.0 or less)
  color_distribution:
    klutz_primary: 0.70        # Foundation palette: 70%
    nickelodeon_accent: 0.20   # Energetic orange (#F57D0D): 20%
    goosebumps_theme: 0.10     # Acid green (#95C120): 10%

  # Maximum rotation angles for element types (in degrees)
  rotation_limits:
    text: 5                    # Text blocks: 5° maximum
    containers: 15             # Boxes: 15° maximum
    photos: 10                 # Images: 10° maximum

  # Texture overlay opacity
  texture_opacity:
    global: 0.08               # Overall paper texture opacity

print_simulation:
  # CMYK channel misregistration (in pixels)
  cmyk_shift:
    magenta: [1, 0]            # Magenta shift offset
    yellow: [0, -1]            # Yellow shift offset

  dot_gain: 0.95               # Ink spread on paper
  vignette: 0.15               # Light falloff intensity
  spine_shadow: 0.20           # Page curvature opacity

validation:
  # Validation enforcement flags
  enforce_period_accuracy: true      # Check for anachronistic terms
  check_color_ratios: true           # Verify color distribution
  validate_safe_zones: true          # Ensure content respects margins
  prevent_spine_intrusion: true      # Block spine dead zone content

layout:
  # Safe zone margins (in pixels from canvas edges)
  safe_zones:
    left: 100                        # Left page outer margin
    right: 100                       # Right page outer margin
    top: 100                         # Top margin
    bottom: 100                      # Bottom margin
```

### Configuration Examples

**Example 1: Default Usage (No Custom Config)**
```bash
python asset_validator.py --layout spread.yaml
# Uses: config/master_config.yaml (default)
# Canvas: 3400x2200, Spine: 462px, Color ratio: 70/20/10
```

**Example 2: Stricter Validation**
```bash
# Create strict_config.yaml
# - Reduce color distribution tolerances
# - Tighten rotation limits
# - Smaller safe zones
python asset_validator.py --layout spread.yaml --config strict_config.yaml
```

**Example 3: Lenient Validation**
```bash
# Create lenient_config.yaml with:
# - Increased color distribution tolerances
# - Relaxed rotation limits
# - Larger safe zones
python asset_validator.py --prompt prompt.txt --config lenient_config.yaml
```

**Example 4: Project-Specific Configuration**
```bash
# Different projects may have different requirements
python asset_validator.py --image photo.png --config projects/textbook_a/config.yaml
python asset_validator.py --image photo.png --config projects/workbook_b/config.yaml
```

### Key Configuration Requirements

1. **YAML Format:** File must be valid YAML syntax
2. **Color Ratios:** Colors should sum to ≤1.0 (70/20/10 in default)
3. **Rotation Limits:** Values in degrees (0-360, but typically 0-15)
4. **Canvas Size:** Array of [width, height] in pixels
5. **Safe Zones:** Pixel measurements from canvas edges
6. **Validation Flags:** Boolean values (true/false)

### Configuration Loading Behavior

- If `--config` is specified but file not found: Validator logs a warning and uses defaults
- If `--config` is not specified: Uses default `config/master_config.yaml`
- If config has missing sections: Missing values fall back to validator defaults
- Config validation happens at initialization time

## Exit Codes
- `0` = Validation passed
- `1` = Validation failed or error occurred

## Forbidden Design Terms (65 total)

**Modern Design Concepts:**
gradient, web 2.0, flat design, material design, minimalist, responsive, UX, UI, wireframe

**Modern Technology:**
mobile, touch, swipe, USB, wireless, bluetooth, LED, LCD, smartphone, tablet, app, cloud, HD, 4K, SSD

**Social Media:**
tweet, post, share, like, hashtag, Google, Facebook, Twitter, Instagram

**Modern Software:**
Windows 95/98/XP, anti-aliasing, opacity slider, layer mask, photoshop

## Allowed Modern Terms (14 total)

These can be used when discussing Aseprite:
aseprite, github, version control, export, layer, sprite sheet, animation, timeline, pixel-perfect, hex code, rgb, alpha channel, transparent, png

## Required Visual Terms

When depicting these items, you MUST include specific terms:

**mouse** → Must mention: Apple, Macintosh, M0100, beige, or one-button
**computer** → Must mention: Macintosh Plus, System 6, or black and white
**software** → Must mention: MacPaint, pixel, bitmap, or 72 DPI
**storage** → Must mention: floppy disk, 1.44MB, or 3.5 inch
**display** → Must mention: CRT, monitor, 512x342, or monochrome

## Image Requirements

- **Format:** PNG with RGBA transparency
- **Max dimensions:** 10000x10000 pixels
- **Nickelodeon Orange (#F57D0D):** ≤30% of image
- **Goosebumps Acid Green (#95C120):** ≤10% of image
- **Rotation metadata:** ≤15°

## Layout Requirements

**Spine Dead Zone:** x = 1469 to 1931 (no elements allowed)

**Rotation Limits:**
- Text elements: ≤5°
- Containers: ≤15°
- Photos/Graphics: ≤10°

**Safe Zones:** 100px minimum from all edges

**Canvas:** 3400x2200 pixels

## Common Validation Errors

### Prompt Validation
```
❌ "Create a gradient button"
   → 'gradient' is forbidden

❌ "Show a mouse on the desk"
   → Missing required term (need: Apple/Macintosh/M0100/beige/one-button)

✅ "Show a beige Apple M0100 mouse"
   → Passes validation
```

### Image Validation
```
❌ image.jpg (JPEG format)
   → Must be PNG with transparency

❌ 0x0 dimensions
   → Invalid dimensions

❌ 50% orange coverage
   → Exceeds 30% limit

✅ 600x450 PNG, RGBA mode, <30% orange
   → Passes validation
```

### Layout Validation
```
❌ Element at x=1500 (in spine zone)
   → Spine intrusion detected

❌ Text rotated 20°
   → Exceeds 5° limit for text

❌ Element at x=50 (left page)
   → Too close to edge (minimum 100px)

✅ Element at x=200, rotation=3°
   → Passes validation
```

## Integration Examples

### Shell Script
```bash
#!/bin/bash
for prompt in prompts/*.txt; do
    if python asset_validator.py --prompt "$prompt"; then
        echo "✓ $prompt validated"
    else
        echo "✗ $prompt failed validation"
        exit 1
    fi
done
```

### Python Integration
```python
from asset_validator import AssetValidator

validator = AssetValidator()
violations = validator.validate_image_asset("photo.png")

if violations:
    print("Validation failed:")
    for v in violations:
        print(f"  - {v}")
else:
    print("Asset validated successfully!")
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate all new/modified image assets
for img in $(git diff --cached --name-only --diff-filter=ACM | grep '\.png$'); do
    python asset_validator.py --image "$img" || exit 1
done

# Validate all layout configs
for layout in $(git diff --cached --name-only --diff-filter=ACM | grep 'layouts/.*\.yaml$'); do
    python asset_validator.py --layout "$layout" || exit 1
done
```

## File Locations

```
aesprite-textbook/
├── asset_validator.py              # Main validator (741 lines)
├── ASSET_VALIDATOR_IMPLEMENTATION.md  # Full documentation
├── VALIDATOR_QUICK_REFERENCE.md    # This file
└── test_examples/                  # Test suite
    ├── prompts/
    │   ├── bad_prompt.txt
    │   ├── good_prompt.txt
    │   └── missing_required_terms.txt
    ├── layouts/
    │   ├── test_layout_good.yaml
    │   └── test_layout_bad.yaml
    └── test_image_good.png
```

## Troubleshooting

**Q: Getting "module not found" errors?**
A: Install dependencies: `pip install numpy Pillow PyYAML`

**Q: False positive on allowed terms?**
A: The validator uses word boundaries. "Apple" won't trigger "app" violation.

**Q: Need to validate multiple files?**
A: Create a bash script to loop through files, checking exit codes.

**Q: Want JSON output for CI/CD?**
A: Currently outputs human-readable text. Pipe stderr to file for logs.

**Q: Color detection seems wrong?**
A: Uses ±30 RGB tolerance. Check if colors are within range of targets.

## Support

For issues or questions:
1. Check ASSET_VALIDATOR_IMPLEMENTATION.md for detailed documentation
2. Review test_examples/ for working examples
3. Run with --verbose flag for detailed logging
4. Check that dependencies are installed correctly
