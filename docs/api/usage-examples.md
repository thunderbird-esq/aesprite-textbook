---
title: Usage Examples
date: 2025-11-05
status: Active
---

# Usage Examples

This document provides practical code examples for using each component of the Klutz Workbook generation system.

## Table of Contents

- [Basic Spread Generation](#basic-spread-generation)
- [Asset Validation](#asset-validation)
- [Prompt Generation](#prompt-generation)
- [Batch Processing](#batch-processing)
- [Custom Post-Processing](#custom-post-processing)

---

## Basic Spread Generation

### Example 1: Generate a Single Spread

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
import yaml

# Initialize compositor
compositor = KlutzCompositor('config/master_config.yaml')

# Load layout configuration
with open('config/layouts/spread_04_05.yaml', 'r') as f:
    layout = yaml.safe_load(f)

# Compose the spread
spread_image = compositor.compose_spread(layout)

# Save result
spread_image.save('output/spreads/spread_04_05.png', 'PNG', dpi=(300, 300))
print("Spread generated successfully!")
```

### Example 2: Generate Multiple Spreads

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
from pathlib import Path
import yaml

compositor = KlutzCompositor()

# Find all layout files
layout_dir = Path('config/layouts')
layout_files = sorted(layout_dir.glob('spread_*.yaml'))

for layout_file in layout_files:
    print(f"Processing {layout_file.name}...")

    # Load layout
    with open(layout_file, 'r') as f:
        layout = yaml.safe_load(f)

    # Generate spread
    spread = compositor.compose_spread(layout)

    # Save with matching filename
    output_name = layout_file.stem + '.png'
    output_path = Path('output/spreads') / output_name
    spread.save(str(output_path), 'PNG', dpi=(300, 300))

    print(f"✓ {output_name} complete")

print(f"\nGenerated {len(layout_files)} spreads")
```

---

## Asset Validation

### Example 3: Validate a Prompt

```python
#!/usr/bin/env python3
from asset_validator import AssetValidator

validator = AssetValidator()

prompt = """
A photograph of a beige one-button Apple Macintosh M0100 mouse
on a wooden desk, taken from above. The mouse is connected to
a Macintosh Plus computer visible in the background.
MacPaint is open on the black and white CRT monitor.
"""

violations = validator.validate_prompt(prompt)

if violations:
    print("Validation failed:")
    for violation in violations:
        print(f"  - {violation}")
else:
    print("✓ Prompt is valid and period-accurate")
```

### Example 4: Validate an Image Asset

```python
#!/usr/bin/env python3
from asset_validator import AssetValidator
from pathlib import Path

validator = AssetValidator()

image_path = 'assets/generated/photo_mouse_01.png'

violations = validator.validate_image_asset(image_path)

if violations:
    print(f"Image validation failed for {image_path}:")
    for violation in violations:
        print(f"  - {violation}")
else:
    print(f"✓ Image {image_path} is valid")
```

### Example 5: Validate Entire Project

```python
#!/usr/bin/env python3
from asset_validator import AssetValidator
import json

validator = AssetValidator()

# Run complete validation
report = validator.validate_complete_project('.')

# Print summary
print(f"\nValidation Summary:")
print(f"  Passed: {report['summary']['passed']}")
print(f"  Failed: {report['summary']['failed']}")

# Print failures
if report['summary']['failed'] > 0:
    print("\nFailures:")

    for file_path, violations in report['prompts'].items():
        if violations:
            print(f"\n{file_path}:")
            for violation in violations:
                print(f"  - {violation}")

    for file_path, violations in report['assets'].items():
        if violations:
            print(f"\n{file_path}:")
            for violation in violations:
                print(f"  - {violation}")

# Save full report
with open('validation_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

---

## Prompt Generation

### Example 6: Generate Prompts for All Elements

```python
#!/usr/bin/env python3
from prompt_generator import PromptGenerator
from pathlib import Path
import yaml

generator = PromptGenerator()

# Load layout
with open('config/layouts/spread_04_05.yaml', 'r') as f:
    layout = yaml.safe_load(f)

# Create prompts directory
prompts_dir = Path('prompts/spread_04_05')
prompts_dir.mkdir(parents=True, exist_ok=True)

# Generate prompts for left page elements
for element in layout['left_page']['elements']:
    if element['type'].startswith('graphic_'):
        prompt = generator.generate_prompt(element)

        # Save prompt to file
        prompt_file = prompts_dir / f"{element['id']}.xml"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        print(f"Generated prompt for {element['id']}")

# Generate prompts for right page elements
for element in layout['right_page']['elements']:
    if element['type'].startswith('graphic_'):
        prompt = generator.generate_prompt(element)

        prompt_file = prompts_dir / f"{element['id']}.xml"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        print(f"Generated prompt for {element['id']}")
```

---

## Batch Processing

### Example 7: Process Entire Workbook

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
from pathlib import Path
import yaml
import time

def process_workbook():
    """Process all spreads with validation and timing"""

    compositor = KlutzCompositor()
    validator = AssetValidator()

    layout_dir = Path('config/layouts')
    layout_files = sorted(layout_dir.glob('spread_*.yaml'))

    total_start = time.time()
    results = []

    for layout_file in layout_files:
        spread_start = time.time()

        print(f"\n{'='*60}")
        print(f"Processing {layout_file.name}")
        print(f"{'='*60}")

        # Load layout
        with open(layout_file, 'r') as f:
            layout = yaml.safe_load(f)

        # Validate layout
        print("Validating layout...")
        violations = validator.validate_layout(layout)
        if violations:
            print("❌ Layout validation failed:")
            for violation in violations:
                print(f"  - {violation}")
            continue
        print("✓ Layout valid")

        # Generate spread
        print("Generating spread...")
        spread = compositor.compose_spread(layout)

        # Save
        output_name = layout_file.stem + '.png'
        output_path = Path('output/spreads') / output_name
        spread.save(str(output_path), 'PNG', dpi=(300, 300))

        # Calculate timing
        duration = time.time() - spread_start
        print(f"✓ Complete in {duration:.2f}s")

        results.append({
            'spread': layout_file.name,
            'duration': duration,
            'status': 'success'
        })

    # Print summary
    total_duration = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Spreads processed: {len(results)}")
    print(f"Total time: {total_duration:.2f}s")
    print(f"Average time per spread: {total_duration/len(results):.2f}s")

if __name__ == '__main__':
    process_workbook()
```

---

## Custom Post-Processing

### Example 8: Custom Print Effects

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
from PIL import Image, ImageEnhance
import yaml

# Generate base spread
compositor = KlutzCompositor()
with open('config/layouts/spread_04_05.yaml', 'r') as f:
    layout = yaml.safe_load(f)

spread = compositor.compose_spread(layout)

# Apply custom adjustments
print("Applying custom post-processing...")

# Increase vignette for more photographed look
spread = compositor.add_vignette(spread, opacity=0.25)

# Add extra dot gain for uncoated paper effect
spread = compositor.apply_dot_gain(spread, gamma=0.90)

# Reduce saturation slightly for aged look
enhancer = ImageEnhance.Color(spread)
spread = enhancer.enhance(0.92)

# Add slight sepia tone
# (This is optional and not period-accurate, but can enhance the aged look)
width, height = spread.size
sepia_overlay = Image.new('RGB', (width, height), (40, 26, 13))
spread = Image.blend(spread, sepia_overlay, alpha=0.05)

# Save with custom settings
spread.save(
    'output/spreads/spread_04_05_custom.png',
    'PNG',
    dpi=(300, 300),
    optimize=True
)

print("✓ Custom post-processing complete")
```

### Example 9: Compare Print Effects

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
from PIL import Image
import yaml

compositor = KlutzCompositor()

with open('config/layouts/spread_04_05.yaml', 'r') as f:
    layout = yaml.safe_load(f)

# Generate base spread WITHOUT print effects
layout_no_effects = layout.copy()
layout_no_effects['global_settings']['print_settings'] = {
    'cmyk_misregistration': False,
    'dot_gain': 1.0,
    'vignette_opacity': 0.0
}

spread_clean = compositor.compose_spread(layout_no_effects)
spread_clean.save('output/comparison/spread_clean.png', 'PNG', dpi=(300, 300))

# Generate WITH standard print effects
spread_standard = compositor.compose_spread(layout)
spread_standard.save('output/comparison/spread_standard.png', 'PNG', dpi=(300, 300))

# Generate WITH extreme print effects
layout_extreme = layout.copy()
layout_extreme['global_settings']['print_settings'] = {
    'cmyk_misregistration': True,
    'dot_gain': 0.85,
    'vignette_opacity': 0.30
}

spread_extreme = compositor.compose_spread(layout_extreme)
spread_extreme.save('output/comparison/spread_extreme.png', 'PNG', dpi=(300, 300))

print("✓ Generated 3 comparison versions")
```

---

## Integration Examples

### Example 10: Full Pipeline with Gemini and nano-banana

```python
#!/usr/bin/env python3
from prompt_generator import PromptGenerator
from gemini_integration import GeminiIntegration
from nano_banana_integration import NanoBananaIntegration
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
from pathlib import Path
import yaml

def generate_spread_with_ai(layout_path):
    """Complete pipeline from layout to final spread"""

    # Initialize components
    prompt_gen = PromptGenerator()
    gemini = GeminiIntegration()
    nano_banana = NanoBananaIntegration()
    compositor = KlutzCompositor()
    validator = AssetValidator()

    # Load layout
    with open(layout_path, 'r') as f:
        layout = yaml.safe_load(f)

    spread_id = layout['spread_info']['number']
    print(f"Processing spread {spread_id}")

    # Generate assets for each element
    for page in ['left_page', 'right_page']:
        for element in layout[page]['elements']:
            if not element['type'].startswith('graphic_'):
                continue

            element_id = element['id']
            print(f"\n  Generating {element_id}...")

            # Generate base prompt
            base_prompt = prompt_gen.generate_prompt(element)

            # Validate prompt
            violations = validator.validate_prompt(base_prompt)
            if violations:
                print(f"    ❌ Prompt validation failed")
                for v in violations:
                    print(f"       - {v}")
                continue

            # Refine with Gemini
            refined_prompt = gemini.refine_prompt(base_prompt)

            # Generate image with nano-banana
            dimensions = element.get('dimensions', (800, 600))
            image = nano_banana.generate_image(refined_prompt, dimensions)

            # Validate generated image
            asset_path = f"assets/generated/{element['filename']}"
            image.save(asset_path, 'PNG')

            violations = validator.validate_image_asset(asset_path)
            if violations:
                print(f"    ⚠ Image validation warnings:")
                for v in violations:
                    print(f"       - {v}")
            else:
                print(f"    ✓ {element_id} generated successfully")

    # Compose final spread
    print(f"\nComposing final spread...")
    spread = compositor.compose_spread(layout)

    # Save
    output_path = f"output/spreads/spread_{spread_id}.png"
    spread.save(output_path, 'PNG', dpi=(300, 300))

    print(f"✓ Spread {spread_id} complete: {output_path}")

if __name__ == '__main__':
    generate_spread_with_ai('config/layouts/spread_04_05.yaml')
```

---

## Error Handling

### Example 11: Robust Error Handling

```python
#!/usr/bin/env python3
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
import yaml
import sys
import traceback

def generate_spread_safely(layout_path):
    """Generate spread with comprehensive error handling"""

    try:
        # Initialize
        compositor = KlutzCompositor()
        validator = AssetValidator()

        # Load layout
        try:
            with open(layout_path, 'r') as f:
                layout = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Layout file not found: {layout_path}")
            return False
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in {layout_path}:")
            print(f"   {e}")
            return False

        # Validate layout
        violations = validator.validate_layout(layout)
        if violations:
            print(f"❌ Layout validation failed:")
            for v in violations:
                print(f"   - {v}")
            return False

        # Generate spread
        try:
            spread = compositor.compose_spread(layout)
        except FileNotFoundError as e:
            print(f"❌ Asset file not found:")
            print(f"   {e}")
            return False
        except Exception as e:
            print(f"❌ Error during composition:")
            print(f"   {e}")
            traceback.print_exc()
            return False

        # Save
        spread_id = layout['spread_info']['number']
        output_path = f"output/spreads/spread_{spread_id}.png"

        try:
            spread.save(output_path, 'PNG', dpi=(300, 300))
        except Exception as e:
            print(f"❌ Error saving spread:")
            print(f"   {e}")
            return False

        print(f"✓ Spread {spread_id} generated successfully")
        return True

    except Exception as e:
        print(f"❌ Unexpected error:")
        print(f"   {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_spread_safe.py <layout_file>")
        sys.exit(1)

    success = generate_spread_safely(sys.argv[1])
    sys.exit(0 if success else 1)
```

---

## See Also

- [api-reference.md](api-reference.md) - Complete API documentation
- [configuration-guide.md](configuration-guide.md) - YAML schema reference
- [../technical/](../technical/) - Implementation details
