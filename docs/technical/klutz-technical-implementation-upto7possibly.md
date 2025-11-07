    result = processor.process_complete_spread(input_path, output_path)
```

## 5. Complete YAML Layout Configuration Examples

```yaml
# config/layouts/spread_04_05.yaml
# Complete layout specification for pages 4-5: Introduction to Pixel Art

spread_info:
  number: "04-05"
  title: "Pixel Perfect! Making Your First Sprite"
  template: "workshop_layout"
  canvas: "aged_newsprint"

global_settings:
  color_distribution:
    klutz_primary: 0.72
    nickelodeon_accent: 0.20
    goosebumps_theme: 0.08

  texture_settings:
    paper_grain: 0.08
    emboss_depth: 20  # microns

  print_settings:
    cmyk_misregistration: true
    dot_gain: 0.95
    vignette_opacity: 0.15

left_page:
  elements:
    - id: "L_headline_pixelart_01"
      type: "text_headline"
      position: [200, 180]
      dimensions: [800, 100]
      rotation: -3
      content: "PIXEL PERFECT!"
      font: "Chicago"
      size: 48
      color: "#000000"
      border: "none"
      shadow:
        offset_x: 2
        offset_y: 2
        color: "#808080"

    - id: "L_photo_mouse_01"
      type: "graphic_photo_instructional"
      filename: "photo_mouse_hand_01.png"
      position: [250, 300]
      dimensions: [600, 450]
      rotation: 2
      border: "4px solid #FF6600"
      shadow:
        offset_x: 3
        offset_y: 3
        color: "#000000"
      subject: "child hand on Apple M0100 mouse"
      camera:
        lens: "100mm macro"
        aperture: "f/11"
        shutter: "1/125"
      lighting:
        key: "45 degrees left, 30 degrees up"
        fill: "60 degrees right, reflector"

    - id: "L_textcontainer_intro_01"
      type: "container_featurebox"
      position: [180, 800]
      dimensions: [900, 400]
      rotation: -1
      background: "#FFD700"
      border: "4px solid black"
      internal_padding: 20
      text_content: |
        Time to make some pixel art! Remember those
        awesome Nintendo characters? They're just
        colored squares arranged in a grid. You're
        going to learn the same tricks the pros use,
        but way easier because you're using Aseprite
        instead of typing mysterious code!

        First, let's set up your workspace. Move your
        mouse (that beige thing in the photo above)
        and click on the color palette. Don't worry
        if you mess up - that's what Undo is for!
      font: "Helvetica"
      font_size: 16
      leading: 22
      color: "#000000"
      simplified_glyphs: true

    - id: "L_splat_tip_01"
      type: "graphic_splat_container"
      position: [950, 650]
      dimensions: [300, 200]
      rotation: 15
      color: "#F57D0D"
      content: "PRO TIP!"
      content_font: "Balloon_ExtraBold"
      content_size: 24
      content_color: "#FFFFFF"

    - id: "L_doodle_arrow_01"
      type: "graphic_doodle"
      position: [850, 750]
      dimensions: [150, 100]
      rotation: -25
      doodle_type: "curved_arrow"
      points_to: "L_photo_mouse_01"
      line_weight: 4
      color: "#000000"

    - id: "L_embossed_remember_01"
      type: "container_embossed_featurebox"
      position: [200, 1300]
      dimensions: [800, 200]
      rotation: 0
      background: "#F8F3E5"
      embossed_text: "REMEMBER!"
      emboss_depth: 20
      border: "2px solid #808080"
      content: "Save your work every 5 minutes!"
      content_position: "below_emboss"

right_page:
  elements:
    - id: "R_gui_aseprite_01"
      type: "graphic_gui_recreation"
      position: [1950, 200]
      dimensions: [1200, 800]
      rotation: 0
      software: "Aseprite"
      interface_elements:
        - "color_picker"
        - "tool_palette"
        - "canvas_grid"
      border: "1px solid black"

    - id: "R_pixelart_mario_01"
      type: "graphic_pixelart"
      position: [2100, 1100]
      dimensions: [400, 400]
      rotation: -5
      magnification: 8
      base_resolution: [32, 32]
      palette: "NES_limited"
      subject: "simple Mario-like character"
      colors:
        - "#000000"  # Black (outline)
        - "#FFFFFF"  # White (eyes)
        - "#FF0000"  # Red (hat, shirt)
        - "#0000FF"  # Blue (overalls)
        - "#FDB5A4"  # Peach (skin)
        - "#8B4513"  # Brown (shoes, hair)
      border: "2px solid black"

    - id: "R_textcontainer_steps_01"
      type: "container_featurebox"
      position: [2050, 1550]
      dimensions: [1000, 500]
      rotation: 1
      background: "#E6F3FF"
      border: "4px solid #0000FF"
      text_content: |
        STEPS TO PIXEL GREATNESS:
        1. Pick a color from the palette
        2. Click the pencil tool (one pixel at a time!)
        3. Draw your outline first (pros always do this)
        4. Fill in the colors with the paint bucket
        5. Add shading with darker versions of each color

        Start with something simple like a mushroom or
        a ghost. Once you get the hang of it, try making
        your own video game character!
      font: "Helvetica"
      font_size: 15
      leading: 20
      list_style: "numbered"
      list_indent: 30

    - id: "R_photo_screen_01"
      type: "graphic_photo_instructional"
      position: [2700, 300]
      dimensions: [500, 375]
      rotation: -3
      subject: "CRT monitor showing pixel art"
      border: "3px solid #808080"
      film_effect: "Kodak_Gold_400"

global_elements:
  - id: "spiral_binding"
    type: "graphic_spiral_binding"
    position: [1469, 0]
    dimensions: [462, 2200]
    specifications:
      pitch: "4:1"
      holes: 29
      hole_diameter: 57
      hole_spacing: 18
      coil_color: "#141414"
      coil_thickness: 8
      shadow_depth: 3

validation_rules:
  enforce_safe_zones: true
  check_spine_clearance: true
  validate_color_ratios: true
  maximum_element_overlap: 0.20
  minimum_text_contrast: 4.5
```

## 6. Complete Master Configuration File

```yaml
# config/master_config.yaml
# Master configuration for 1996 Klutz Computer Graphics Workbook

project:
  name: "Klutz Press Computer Graphics Workbook"
  subtitle: "Learn Pixel Art the Klutz Way!"
  year: 1996
  pages: 48
  binding: "spiral"
  format: "landscape"

technical_specifications:
  canvas:
    dimensions: [3400, 2200]
    dpi: 300
    color_space: "sRGB"
    bit_depth: 24

  margins:
    top: 150
    bottom: 150
    outer_left: 150
    outer_right: 150
    spine_margin: 231  # Total spine width: 462px

  safe_zones:
    left_page:
      x_range: [150, 1469]
      y_range: [150, 2050]
    right_page:
      x_range: [1931, 3250]
      y_range: [150, 2050]

  spine_specifications:
    center_x: 1700
    width: 462
    dead_zone: [1469, 1931]
    binding_holes:
      pitch: "4:1"
      diameter: 57
      spacing: 18
      count: 29

color_specifications:
  primary_palette:
    red: "#FF0000"
    blue: "#0000FF"
    yellow: "#FFFF00"
    green: "#00FF00"
    orange: "#FFA500"
    purple: "#800080"
    black: "#000000"
    white: "#FFFFFF"

  accent_palette:
    nickelodeon_orange: "#F57D0D"
    nickelodeon_slime: "#C4D600"
    goosebumps_acid: "#95C120"
    goosebumps_toxic: "#68EA34"

  usage_rules:
    primary_minimum: 0.70
    nickelodeon_maximum: 0.20
    goosebumps_maximum: 0.10

  paper_colors:
    bright_white: "#FFFFFF"
    aged_newsprint: "#F8F3E5"
    recycled_gray: "#F0F0E8"

typography_specifications:
  body_text:
    fonts: ["Helvetica", "Frutiger"]
    sizes: [14, 15, 16, 17, 18]
    leading_multiplier: 1.4
    color: "#000000"
    simplified_glyphs: true

  headlines:
    fonts: ["Chicago", "Charcoal"]
    sizes: [24, 36, 48, 60, 72]
    style: "bitmap_no_antialiasing"
    color: "#000000"

  accent_text:
    fonts: ["Monaco", "Courier New"]
    sizes: [9, 10, 12]
    usage: "code_and_technical"

  special_effects:
    embossed:
      depth: "15-25 microns"
      style: "blind_emboss"
      no_ink: true

    dripping:
      fonts: ["custom_slime"]
      colors: ["#C4D600"]
      usage: "special_headlines_only"

element_specifications:
  rotation_limits:
    text_blocks: 5
    containers: 15
    photos: 10
    decorative: 30

  shadow_specifications:
    type: "hard_edge_only"
    offset: [3, 3]
    blur: 0
    color: "#000000"
    opacity: 1.0

  border_specifications:
    standard_widths: [2, 3, 4, 6]
    style: "solid"
    colors: ["#000000", "#FF0000", "#0000FF", "#FF6600"]

print_simulation:
  cmyk_misregistration:
    cyan: [0, 0]
    magenta: [1, 0]
    yellow: [0, -1]
    black: [0, 0]

  dot_gain:
    uncoated_paper: 0.23
    gamma_adjustment: 0.95

  paper_texture:
    type: "uncoated_newsprint"
    opacity: 0.08
    grain_direction: "horizontal"

  physical_effects:
    vignette_opacity: 0.15
    spine_shadow_opacity: 0.20
    page_curl_size: 100

photographic_specifications:
  film_stock: "Kodak Gold 400"
  alternative: "Fuji Superia 400"

  characteristics:
    grain_index: 39
    color_profile: "warm_highlights_neutral_midtones"
    typical_settings:
      iso: 400
      aperture: "f/8-f/16"
      shutter: "1/60-1/250"

  lighting_setup:
    key_light:
      type: "softbox"
      size: "24x36 inches"
      position: "45° left, 30° elevation"
      distance: "24 inches"

    fill_light:
      type: "reflector"
      position: "60° right"
      ratio: "1:2"

validation_settings:
  strict_mode: true

  forbidden_terms:
    - "gradient"
    - "web 2.0"
    - "UX"
    - "mobile"
    - "responsive"
    - "modern"
    - "minimal"
    - "clean"
    - "sleek"

  required_elements:
    - spiral_binding
    - paper_texture
    - cmyk_misregistration

  quality_checks:
    - color_distribution
    - spine_clearance
    - text_legibility
    - period_authenticity
    - rotation_compliance

file_organization:
  naming_convention: "[page]_[type]_[description]_[index]"

  directory_structure:
    assets: "assets/generated/"
    prompts: "prompts/components/"
    layouts: "config/layouts/"
    output: "output/spreads/"
    validation: "output/validation/"

  version_control:
    track_prompts: true
    track_assets: true
    track_layouts: true

output_specifications:
  file_format: "PNG"
  compression: "lossless"
  metadata:
    include_dpi: true
    include_color_profile: true
    include_creation_date: true

  deliverables:
    raw_composites: true
    processed_spreads: true
    individual_assets: true
    validation_reports: true
```

## 7. Complete Deployment Script

```python
#!/usr/bin/env python3
"""
deploy_workbook.py - Complete deployment script for generating the workbook
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
import subprocess
import logging

# Import our modules
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
from prompt_generator import PromptGenerator
from post_processor import PostProcessor

class WorkbookDeployer:
    """Orchestrates the complete workbook generation pipeline"""

    def __init__(self, config_path='config/master_config.yaml'):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deployment.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.compositor = KlutzCompositor(config_path)
        self.validator = AssetValidator()
        self.prompt_generator = PromptGenerator()
        self.post_processor = PostProcessor()

        # Create directory structure
        self.setup_directories()

    def setup_directories(self):
        """Create all required directories"""

        directories = [
            'config/layouts',
            'config/palettes',
            'config/typography',
            'assets/generated',
            'assets/textures',
            'assets/fonts',
            'assets/reference',
            'prompts/components',
            'prompts/compiled',
            'output/spreads',
            'output/validation',
            'scripts',
            'logs'
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        self.logger.info(f"✓ Spread {spread_number}-{spread_number+1} complete!")

        return True

    def generate_complete_workbook(self, start_page=0, end_page=None):
        """Generate the complete workbook or a range of pages"""

        if end_page is None:
            end_page = self.config['project']['pages']

        self.logger.info(f"Generating workbook pages {start_page} to {end_page}")

        successful = []
        failed = []

        # Generate spreads (2 pages at a time)
        for spread_num in range(start_page, end_page, 2):
            try:
                if self.generate_spread(spread_num):
                    successful.append(spread_num)
                else:
                    failed.append(spread_num)
            except Exception as e:
                self.logger.error(f"Failed to generate spread {spread_num}: {str(e)}")
                failed.append(spread_num)

        # Generate final report
        self.generate_production_report(successful, failed)

        return len(failed) == 0

    def generate_production_report(self, successful, failed):
        """Generate comprehensive production report"""

        report = {
            'timestamp': datetime.now().isoformat(),
            'project': self.config['project']['name'],
            'successful_spreads': successful,
            'failed_spreads': failed,
            'statistics': {},
            'validation_results': {},
            'color_analysis': {},
            'file_inventory': {}
        }

        # Analyze color distribution across all spreads
        self.logger.info("Analyzing color distribution...")
        for spread_num in successful:
            spread_path = f"output/spreads/spread_{spread_num:02d}_{spread_num+1:02d}_final.png"
            if Path(spread_path).exists():
                report['color_analysis'][f"spread_{spread_num}"] = self.analyze_color_distribution(spread_path)

        # Validate all assets
        self.logger.info("Running comprehensive validation...")
        validation_report = self.validator.validate_complete_project('.')
        report['validation_results'] = validation_report

        # File inventory
        report['file_inventory'] = {
            'prompts': len(list(Path('prompts/components').glob('*.xml'))),
            'assets': len(list(Path('assets/generated').glob('*.png'))),
            'spreads': len(list(Path('output/spreads').glob('*_final.png'))),
            'layouts': len(list(Path('config/layouts').glob('*.yaml')))
        }

        # Statistics
        report['statistics'] = {
            'total_spreads': len(successful) + len(failed),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / (len(successful) + len(failed)) * 100 if (successful or failed) else 0,
            'total_assets': report['file_inventory']['assets'],
            'validation_passed': report['validation_results']['summary']['passed'],
            'validation_failed': report['validation_results']['summary']['failed']
        }

        # Save report
        report_path = f"output/validation/production_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Production report saved to {report_path}")

        # Print summary
        self.print_summary(report)

    def analyze_color_distribution(self, image_path):
        """Analyze color distribution in a spread"""

        from PIL import Image
        import numpy as np

        image = Image.open(image_path)
        img_array = np.array(image.convert('RGB'))

        # Define color ranges
        colors = {
            'nickelodeon_orange': (245, 125, 13),
            'goosebumps_acid': (149, 193, 32),
            'primary_colors': [
                (255, 0, 0),    # Red
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (0, 255, 0),    # Green
                (255, 165, 0),  # Orange
                (128, 0, 128)   # Purple
            ]
        }

        total_pixels = img_array.shape[0] * img_array.shape[1]

        # Count color usage
        nick_count = 0
        goose_count = 0
        primary_count = 0

        # Flatten array for faster processing
        pixels = img_array.reshape(-1, 3)

        for pixel in pixels:
            # Check Nickelodeon orange (with tolerance)
            if np.linalg.norm(pixel - colors['nickelodeon_orange']) < 30:
                nick_count += 1
            # Check Goosebumps acid
            elif np.linalg.norm(pixel - colors['goosebumps_acid']) < 30:
                goose_count += 1
            # Check primary colors
            else:
                for primary in colors['primary_colors']:
                    if np.linalg.norm(pixel - primary) < 40:
                        primary_count += 1
                        break

        return {
            'nickelodeon_percentage': (nick_count / total_pixels) * 100,
            'goosebumps_percentage': (goose_count / total_pixels) * 100,
            'primary_percentage': (primary_count / total_pixels) * 100,
            'compliant': (
                (nick_count / total_pixels) <= 0.30 and
                (goose_count / total_pixels) <= 0.10
            )
        }

    def print_summary(self, report):
        """Print formatted summary to console"""

        print("\n" + "="*60)
        print("PRODUCTION SUMMARY")
        print("="*60)
        print(f"Project: {report['project']}")
        print(f"Timestamp: {report['timestamp']}")
        print("\nSTATISTICS:")
        print(f"  Total Spreads: {report['statistics']['total_spreads']}")
        print(f"  Successful: {report['statistics']['successful']}")
        print(f"  Failed: {report['statistics']['failed']}")
        print(f"  Success Rate: {report['statistics']['success_rate']:.1f}%")
        print(f"\nVALIDATION:")
        print(f"  Tests Passed: {report['statistics']['validation_passed']}")
        print(f"  Tests Failed: {report['statistics']['validation_failed']}")
        print(f"\nFILE INVENTORY:")
        for key, value in report['file_inventory'].items():
            print(f"  {key.capitalize()}: {value}")

        if report['failed_spreads']:
            print(f"\n⚠ FAILED SPREADS: {report['failed_spreads']}")
        else:
            print("\n✓ All spreads generated successfully!")

        print("="*60 + "\n")

    def repair_failed_spread(self, spread_number):
        """Attempt to repair a failed spread"""

        self.logger.info(f"Attempting to repair spread {spread_number}-{spread_number+1}")

        # Check what's missing
        layout_file = f"config/layouts/spread_{spread_number:02d}_{spread_number+1:02d}.yaml"

        if not Path(layout_file).exists():
            self.logger.error(f"Layout file missing: {layout_file}")
            return False

        with open(layout_file, 'r') as f:
            layout = yaml.safe_load(f)

        missing_assets = []

        # Check for missing assets
        for page in ['left_page', 'right_page']:
            for element in layout[page]['elements']:
                asset_path = f"assets/generated/{element['id']}.png"
                if not Path(asset_path).exists():
                    missing_assets.append(element['id'])
                    self.logger.warning(f"Missing asset: {element['id']}")

        # Regenerate missing assets
        if missing_assets:
            self.logger.info(f"Regenerating {len(missing_assets)} missing assets...")
            for asset_id in missing_assets:
                # Find element config
                element = None
                for page in ['left_page', 'right_page']:
                    for el in layout[page]['elements']:
                        if el['id'] == asset_id:
                            element = el
                            break

                if element:
                    # Generate prompt
                    xml_prompt = self.prompt_generator.templates[element['type']](element)

                    # Generate asset
                    output_path = f"assets/generated/{asset_id}.png"
                    self.call_nano_banana(xml_prompt, output_path)

        # Retry spread generation
        return self.generate_spread(spread_number)

    def batch_validate_assets(self):
        """Validate all generated assets in batch"""

        asset_dir = Path('assets/generated')
        results = {
            'passed': [],
            'failed': {},
            'total': 0
        }

        for asset_path in asset_dir.glob('*.png'):
            results['total'] += 1
            violations = self.validator.validate_image_asset(asset_path)

            if violations:
                results['failed'][str(asset_path)] = violations
            else:
                results['passed'].append(str(asset_path))

        # Save validation report
        report_path = 'output/validation/asset_validation.json'
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Asset validation complete: {len(results['passed'])}/{results['total']} passed")

        return results

    def emergency_recovery(self):
        """Emergency recovery mode for critical failures"""

        self.logger.warning("Entering emergency recovery mode...")

        # Create backup of current state
        backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        # Copy all important files
        import shutil

        dirs_to_backup = ['assets/generated', 'output/spreads', 'config/layouts']
        for dir_path in dirs_to_backup:
            if Path(dir_path).exists():
                shutil.copytree(dir_path, f"{backup_dir}/{dir_path.replace('/', '_')}")

        self.logger.info(f"Backup created at {backup_dir}")

        # Attempt to recover failed spreads
        all_spreads = list(range(0, self.config['project']['pages'], 2))
        completed_spreads = []

        for spread_path in Path('output/spreads').glob('*_final.png'):
            spread_num = int(spread_path.stem.split('_')[1])
            completed_spreads.append(spread_num)

        failed_spreads = [s for s in all_spreads if s not in completed_spreads]

        self.logger.info(f"Found {len(failed_spreads)} failed spreads to recover")

        # Attempt repair
        recovered = []
        for spread_num in failed_spreads:
            if self.repair_failed_spread(spread_num):
                recovered.append(spread_num)

        self.logger.info(f"Recovery complete: {len(recovered)}/{len(failed_spreads)} spreads recovered")

        return recovered


# Main execution block
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Deploy Klutz Workbook')
    parser.add_argument('--start', type=int, default=0, help='Starting page number')
    parser.add_argument('--end', type=int, default=None, help='Ending page number')
    parser.add_argument('--repair', type=int, help='Repair specific spread')
    parser.add_argument('--validate', action='store_true', help='Run validation only')
    parser.add_argument('--emergency', action='store_true', help='Emergency recovery mode')
    parser.add_argument('--config', default='config/master_config.yaml', help='Config file path')

    args = parser.parse_args()

    # Initialize deployer
    deployer = WorkbookDeployer(args.config)

    try:
        if args.emergency:
            # Emergency recovery mode
            recovered = deployer.emergency_recovery()
            print(f"Recovered {len(recovered)} spreads")

        elif args.validate:
            # Validation only mode
            results = deployer.batch_validate_assets()
            print(f"Validation complete: {len(results['passed'])}/{results['total']} assets passed")

        elif args.repair is not None:
            # Repair specific spread
            if deployer.repair_failed_spread(args.repair):
                print(f"Successfully repaired spread {args.repair}-{args.repair+1}")
            else:
                print(f"Failed to repair spread {args.repair}-{args.repair+1}")
                sys.exit(1)

        else:
            # Normal generation mode
            if deployer.generate_complete_workbook(args.start, args.end):
                print("✓ Workbook generation complete!")
            else:
                print("⚠ Some spreads failed. Run with --emergency for recovery mode.")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Current progress has been saved.")
        print("Run with --emergency flag to recover incomplete spreads.")
        sys.exit(130)

    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        print("Run with --emergency flag to attempt recovery")
        sys.exit(1)"Created {len(directories)} directories")

    def generate_prompts_for_spread(self, spread_number):
        """Generate all prompts for a specific spread"""

        layout_file = f"config/layouts/spread_{spread_number:02d}_{spread_number+1:02d}.yaml"

        if not Path(layout_file).exists():
            self.logger.error(f"Layout file not found: {layout_file}")
            return False

        self.logger.info(f"Generating prompts for spread {spread_number}-{spread_number+1}")

        # Generate prompts
        prompts = self.prompt_generator.generate_all_prompts(layout_file)

        # Validate each prompt
        for element_id, prompt in prompts.items():
            violations = self.validator.validate_prompt(prompt)
            if violations:
                self.logger.warning(f"Prompt validation failed for {element_id}:")
                for v in violations:
                    self.logger.warning(f"  - {v}")
            else:
                self.logger.info(f"✓ Prompt validated: {element_id}")

        return prompts

    def call_gemini_api(self, metaprompt):
        """Call Gemini API to generate XML prompt"""

        # This would be the actual API call
        # For now, return a placeholder
        self.logger.info("Calling Gemini API...")

        # In production:
        # response = gemini_client.generate(metaprompt)
        # return response.text

        return "<placeholder_xml_prompt/>"

    def call_nano_banana(self, xml_prompt, output_path):
        """Call nano-banana to generate image"""

        # This would be the actual image generation
        # For now, create a placeholder
        self.logger.info(f"Generating image with nano-banana: {output_path}")

        # In production:
        # image = nano_banana.generate(xml_prompt)
        # image.save(output_path)

        return True

    def generate_spread(self, spread_number):
        """Generate a complete two-page spread"""

        self.logger.info(f"="*50)
        self.logger.info(f"Generating spread {spread_number}-{spread_number+1}")
        self.logger.info(f"="*50)

        # Step 1: Generate prompts
        prompts = self.generate_prompts_for_spread(spread_number)
        if not prompts:
            return False

        # Step 2: Generate assets via nano-banana
        for element_id, xml_prompt in prompts.items():
            output_path = f"assets/generated/{element_id}.png"

            if not Path(output_path).exists():
                self.logger.info(f"Generating asset: {element_id}")
                self.call_nano_banana(xml_prompt, output_path)
            else:
                self.logger.info(f"Asset already exists: {element_id}")

        # Step 3: Validate all assets
        self.logger.info("Validating generated assets...")
        for element_id in prompts.keys():
            asset_path = f"assets/generated/{element_id}.png"
            if Path(asset_path).exists():
                violations = self.validator.validate_image_asset(asset_path)
                if violations:
                    self.logger.warning(f"Asset validation issues for {element_id}:")
                    for v in violations:
                        self.logger.warning(f"  - {v}")

        # Step 4: Compose the spread
        layout_file = f"config/layouts/spread_{spread_number:02d}_{spread_number+1:02d}.yaml"
        with open(layout_file, 'r') as f:
            layout = yaml.safe_load(f)

        self.logger.info("Composing spread...")
        spread_image = self.compositor.compose_spread(layout)

        # Step 5: Apply post-processing
        raw_path = f"output/spreads/spread_{spread_number:02d}_{spread_number+1:02d}_raw.png"
        spread_image.save(raw_path)

        self.logger.info("Applying post-processing effects...")
        final_path = f"output/spreads/spread_{spread_number:02d}_{spread_number+1:02d}_final.png"
        self.post_processor.process_complete_spread(raw_path, final_path)

        self.logger.info(f        # Convert to RGB
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)

        rgb = np.stack([r, g, b], axis=2)

        return rgb.astype(np.uint8)

    def apply_cmyk_misregistration(self, image):
        """Apply precise CMYK channel shifts"""

        # Convert to CMYK
        cmyk = self.rgb_to_cmyk(np.array(image))

        # Apply shifts to each channel
        shifted_cmyk = np.zeros_like(cmyk)

        for i, (channel_name, (dx, dy)) in enumerate(zip(
            ['cyan', 'magenta', 'yellow', 'black'],
            [self.cmyk_shifts[c] for c in ['cyan', 'magenta', 'yellow', 'black']]
        )):
            if dx != 0 or dy != 0:
                shifted_cmyk[:,:,i] = ndimage.shift(cmyk[:,:,i], [dy, dx],
                                                    mode='nearest')
            else:
                shifted_cmyk[:,:,i] = cmyk[:,:,i]

        # Convert back to RGB
        rgb = self.cmyk_to_rgb(shifted_cmyk)

        return Image.fromarray(rgb)

    def apply_dot_gain(self, image):
        """Apply dot gain compensation for uncoated paper"""

        img_array = np.array(image).astype(float) / 255.0

        # Apply dot gain curve to each channel
        for i in range(3):
            img_array[:,:,i] = np.interp(img_array[:,:,i],
                                         np.linspace(0, 1, 256),
                                         self.dot_gain_curve)

        # Apply gamma correction (0.95 for uncoated paper)
        img_array = np.power(img_array, 0.95)

        # Convert back to 8-bit
        result = (img_array * 255).astype(np.uint8)

        return Image.fromarray(result)

    def add_paper_texture(self, image, strength=0.08):
        """Add scanned paper texture overlay"""

        # Generate or load paper texture
        texture = self.generate_paper_texture(image.size)

        # Blend with original
        result = Image.blend(image, texture, alpha=strength)

        return result

    def generate_paper_texture(self, size):
        """Generate procedural paper texture"""

        width, height = size

        # Create base noise
        noise = np.random.normal(200, 15, (height, width, 3))

        # Add horizontal paper grain
        for y in range(0, height, 3):
            noise[y, :] += np.random.normal(0, 8, (width, 3))

        # Add vertical fibers (less prominent)
        for x in range(0, width, 7):
            noise[:, x] += np.random.normal(0, 4, (height, 3))

        # Add paper imperfections (random spots)
        num_spots = int(width * height / 10000)
        for _ in range(num_spots):
            x, y = np.random.randint(0, width), np.random.randint(0, height)
            radius = np.random.randint(1, 4)
            darkness = np.random.randint(-30, -10)

            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    if 0 <= y+dy < height and 0 <= x+dx < width:
                        if dx*dx + dy*dy <= radius*radius:
                            noise[y+dy, x+dx] += darkness

        # Clip and convert
        noise = np.clip(noise, 0, 255).astype(np.uint8)

        return Image.fromarray(noise)

    def add_printing_artifacts(self, image):
        """Add various printing imperfections"""

        img_array = np.array(image)

        # Ink spread simulation (very subtle blur)
        kernel = np.array([[0, 1, 0],
                          [1, 4, 1],
                          [0, 1, 0]]) / 8.0

        for i in range(3):
            img_array[:,:,i] = ndimage.convolve(img_array[:,:,i], kernel)

        # Halftone pattern simulation (simplified)
        # Add very subtle regular pattern
        pattern = np.zeros((4, 4))
        pattern[::2, ::2] = 1
        pattern[1::2, 1::2] = 1
        pattern = pattern * 2 - 1  # Convert to -1, 1

        # Tile pattern
        tiled = np.tile(pattern, (img_array.shape[0]//4 + 1,
                                  img_array.shape[1]//4 + 1, 1))
        tiled = tiled[:img_array.shape[0], :img_array.shape[1], :3]

        # Apply very subtly
        img_array = img_array + tiled * 1.5
        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def add_binding_shadows(self, image):
        """Add shadows near spiral binding area"""

        draw = ImageDraw.Draw(image, 'RGBA')

        # Spine center at x=1700, width=462
        spine_start = 1700 - 231
        spine_end = 1700 + 231

        # Create gradient shadow on both sides
        shadow_width = 150

        for i in range(shadow_width):
            opacity = int(30 * (1 - i / shadow_width))

            # Left side shadow
            draw.line([(spine_start - i, 0),
                      (spine_start - i, image.height)],
                     fill=(0, 0, 0, opacity))

            # Right side shadow
            draw.line([(spine_end + i, 0),
                      (spine_end + i, image.height)],
                     fill=(0, 0, 0, opacity))

        return image

    def add_page_curl(self, image):
        """Add subtle page curl effect at corners"""

        img_array = np.array(image)
        height, width = img_array.shape[:2]

        # Create curl shadow in bottom-right corner
        curl_size = 100

        for y in range(height - curl_size, height):
            for x in range(width - curl_size, width):
                # Distance from corner
                dist_x = width - x
                dist_y = height - y
                dist = np.sqrt(dist_x**2 + dist_y**2)

                if dist < curl_size:
                    # Darken based on distance
                    darkness = int(20 * (1 - dist / curl_size))
                    img_array[y, x] = np.maximum(0, img_array[y, x] - darkness)

        return Image.fromarray(img_array)

    def process_complete_spread(self, image_path, output_path=None):
        """Apply all post-processing effects in correct order"""

        # Load image
        image = Image.open(image_path)

        # Stage 1: Paper and texture
        print("Applying paper texture...")
        image = self.add_paper_texture(image)

        # Stage 2: Printing artifacts
        print("Applying CMYK misregistration...")
        image = self.apply_cmyk_misregistration(image)

        print("Applying dot gain...")
        image = self.apply_dot_gain(image)

        print("Adding printing artifacts...")
        image = self.add_printing_artifacts(image)

        # Stage 3: Physical effects
        print("Adding binding shadows...")
        image = self.add_binding_shadows(image)

        print("Adding page curl...")
        image = self.add_page_curl(image)

        # Stage 4: Photography simulation
        print("Adding vignette...")
        image = self.add_vignette(image)

        # Save result
        if output_path:
            image.save(output_path, 'PNG', dpi=(300, 300))
            print(f"Saved to {output_path}")

        return image

    def add_vignette(self, image, strength=0.15):
        """Add photographic vignette"""

        # Create vignette mask
        width, height = image.size

        # Create radial gradient
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)

        # Calculate distance from center
        dist = np.sqrt(X**2 + Y**2)

        # Create vignette (darker at edges)
        vignette = 1 - (dist / np.max(dist)) * strength
        vignette = np.clip(vignette, 0, 1)

        # Apply to image
        img_array = np.array(image).astype(float)
        for i in range(3):
            img_array[:,:,i] *= vignette

        result = Image.fromarray(img_array.astype(np.uint8))

        return result


# Usage example
if __name__ == "__main__":
    processor = PostProcessor()

    # Process a complete spread
    input_path = "output/spreads/spread_04_05_raw.png"
    output_path = "output/spreads/spread_04_05_final.png"

    result = processor.process_complete_spread(input_path, output_path)
```

## 4. Complete Post-Processing Pipeline

```python
#!/usr/bin/env python3
"""
post_processor.py - Apply authentic 1996 print effects to composed images
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cv2
from scipy import ndimage
from typing import Tuple

class PostProcessor:
    """Apply period-accurate print artifacts and effects"""

    def __init__(self):
        # CMYK shift specifications from research
        self.cmyk_shifts = {
            'cyan': (0, 0),
            'magenta': (1, 0),    # 1px right
            'yellow': (0, -1),     # 1px up
            'black': (0, 0)
        }

        # Dot gain curve for uncoated paper
        self.dot_gain_curve = self.generate_dot_gain_curve()

        # Paper characteristics
        self.paper_specs = {
            'uncoated': {
                'dot_gain': 0.23,  # 23% at 40% coverage
                'max_density': {'C': 1.45, 'M': 1.45, 'Y': 1.05, 'K': 1.75},
                'show_through': 0.05,
                'texture_strength': 0.08
            }
        }

    def generate_dot_gain_curve(self):
        """Generate dot gain compensation curve for uncoated paper"""

        # Based on FOGRA 29 standards
        input_values = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        output_values = np.array([0, 13, 26, 38, 49, 59, 68, 76, 84, 92, 100])

        # Interpolate for all 256 values
        curve = np.interp(np.linspace(0, 100, 256),
                         input_values, output_values)

        return curve / 100.0  # Normalize to 0-1

    def rgb_to_cmyk(self, rgb_image):
        """Convert RGB to CMYK color space"""

        # Normalize RGB to 0-1
        rgb = rgb_image.astype(float) / 255.0

        # Extract channels
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

        # Calculate K (black)
        k = 1 - np.max(rgb, axis=2)

        # Calculate CMY
        c = (1 - r - k) / (1 - k + 1e-10)
        m = (1 - g - k) / (1 - k + 1e-10)
        y = (1 - b - k) / (1 - k + 1e-10)

        # Stack channels
        cmyk = np.stack([c, m, y, k], axis=2)

        return cmyk

    def cmyk_to_rgb(self, cmyk_image):
        """Convert CMYK back to RGB"""

        c, m, y, k = cmyk_image[:,:,0], cmyk_image[:,:,1], \
                     cmyk_image[:,:,2], cmyk_image[:,:,3]

        # Convert to RGB
        r = 255 * (1 -# Complete Technical Implementation Details for Klutz Workbook Project

## 1. Complete Python Compositor Implementation

```python
#!/usr/bin/env python3
"""
klutz_compositor.py - Main composition engine for Klutz workbook pages
"""

import yaml
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import random
import hashlib
import math

class KlutzCompositor:
    """Complete implementation of the Klutz workbook compositor"""

    def __init__(self, config_path='config/master_config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Canvas specifications from research
        self.canvas_width = 3400
        self.canvas_height = 2200
        self.spine_center = 1700
        self.spine_width = 462
        self.safe_zone_margin = 150

        # Dead zones
        self.spine_start = self.spine_center - (self.spine_width // 2)
        self.spine_end = self.spine_center + (self.spine_width // 2)

        # Color specifications
        self.colors = {
            'aged_newsprint': (248, 243, 229),  # #F8F3E5
            'nickelodeon_orange': (245, 125, 13),  # #F57D0D
            'goosebumps_acid': (149, 193, 32),  # #95C120
            'klutz_yellow': (255, 215, 0),  # #FFD700
            'pure_black': (0, 0, 0)
        }

    def create_base_canvas(self, template='aged_newsprint'):
        """Create the base canvas with paper texture and binding"""

        # Create base with paper color
        canvas = Image.new('RGB', (self.canvas_width, self.canvas_height),
                          self.colors[template])

        # Apply paper texture
        texture = self.generate_paper_texture()
        canvas = Image.blend(canvas, texture, alpha=0.08)

        # Add spiral binding holes
        canvas = self.add_spiral_binding(canvas)

        # Add subtle page curvature near spine
        canvas = self.add_page_curvature(canvas)

        return canvas

    def generate_paper_texture(self):
        """Generate procedural uncoated paper texture"""

        # Create noise array
        noise = np.random.normal(128, 20,
                                 (self.canvas_height, self.canvas_width, 3))

        # Add horizontal grain pattern (paper direction)
        for y in range(0, self.canvas_height, 2):
            noise[y, :] += np.random.normal(0, 5)

        # Convert to PIL Image
        texture = Image.fromarray(noise.astype(np.uint8))

        # Apply slight Gaussian blur to soften
        texture = texture.filter(ImageFilter.GaussianBlur(radius=0.5))

        return texture

    def add_spiral_binding(self, canvas):
        """Add photorealistic spiral binding with precise specifications"""

        draw = ImageDraw.Draw(canvas)

        # 4:1 pitch specifications from research
        hole_diameter = 57  # pixels
        hole_spacing = 18  # pixels between holes
        pitch = hole_diameter + hole_spacing  # 75 pixels total

        # Calculate number of holes
        num_holes = self.canvas_height // pitch

        # Starting position (centered vertically)
        start_y = (self.canvas_height - (num_holes * pitch)) // 2

        for i in range(num_holes):
            y_center = start_y + (i * pitch) + (hole_diameter // 2)

            # Draw hole with inner shadow for depth
            self.draw_binding_hole(draw, self.spine_center, y_center,
                                  hole_diameter)

            # Draw spiral coil segment
            self.draw_coil_segment(draw, self.spine_center, y_center,
                                  hole_diameter)

        return canvas

    def draw_binding_hole(self, draw, x, y, diameter):
        """Draw a single binding hole with realistic shadow"""

        radius = diameter // 2

        # Outer shadow ring (paper thickness illusion)
        for offset in range(3, 0, -1):
            shadow_color = (200 - offset * 20,) * 3
            draw.ellipse([x - radius - offset, y - radius - offset,
                         x + radius + offset, y + radius + offset],
                        fill=shadow_color)

        # Main hole (white/page color showing through)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=self.colors['aged_newsprint'])

        # Inner shadow (top-left, simulating depth)
        shadow_arc_color = (180, 180, 180)
        draw.arc([x - radius + 2, y - radius + 2,
                 x + radius - 2, y + radius - 2],
                start=135, end=315, fill=shadow_arc_color, width=3)

    def draw_coil_segment(self, draw, x, y, hole_diameter):
        """Draw black plastic coil visible through hole"""

        coil_thickness = 8
        coil_color = (20, 20, 20)  # Very dark gray, not pure black

        # Draw coil as thick arc through the hole
        radius = hole_diameter // 2 - 5
        draw.arc([x - radius, y - radius, x + radius, y + radius],
                start=0, end=360, fill=coil_color, width=coil_thickness)

    def add_page_curvature(self, canvas):
        """Add subtle shadow gradient near spine for page curvature"""

        gradient = Image.new('L', (self.canvas_width, self.canvas_height), 255)
        draw = ImageDraw.Draw(gradient)

        # Create gradient from spine outward
        shadow_width = 200
        for i in range(shadow_width):
            opacity = int(255 - (i / shadow_width) * 50)  # Max 20% shadow

            # Left side of spine
            x_left = self.spine_center - i
            draw.line([(x_left, 0), (x_left, self.canvas_height)],
                     fill=opacity)

            # Right side of spine
            x_right = self.spine_center + i
            draw.line([(x_right, 0), (x_right, self.canvas_height)],
                     fill=opacity)

        # Apply gradient as overlay
        shadow = Image.new('RGB', (self.canvas_width, self.canvas_height),
                          (0, 0, 0))
        canvas = Image.composite(canvas, shadow, gradient)

        return canvas

    def load_and_process_asset(self, asset_config):
        """Load an asset and apply transformations"""

        asset_path = Path('assets/generated') / asset_config['filename']
        asset = Image.open(asset_path).convert('RGBA')

        # Resize if needed
        if 'dimensions' in asset_config:
            asset = asset.resize(asset_config['dimensions'],
                                Image.Resampling.LANCZOS)

        # Apply rotation with deterministic chaos
        if 'rotation' in asset_config:
            rotation = self.get_chaos_rotation(asset_config['id'],
                                              asset_config['rotation'])
            asset = asset.rotate(rotation, expand=True,
                                fillcolor=(0, 0, 0, 0))

        # Apply border if specified
        if 'border' in asset_config:
            asset = self.add_border(asset, asset_config['border'])

        # Apply hard shadow if specified
        if 'shadow' in asset_config:
            asset = self.add_hard_shadow(asset, asset_config['shadow'])

        return asset

    def get_chaos_rotation(self, element_id, max_rotation):
        """Deterministic 'random' rotation based on element ID"""

        # Use hash for consistent randomization
        seed = int(hashlib.md5(element_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Return rotation between -max and +max
        return random.uniform(-max_rotation, max_rotation)

    def add_border(self, image, border_config):
        """Add a solid color border to an image"""

        # Parse border config (e.g., "4px solid #FF6600")
        parts = border_config.split()
        width = int(parts[0].replace('px', ''))
        color = parts[2] if parts[2].startswith('#') else parts[1]

        # Convert hex to RGB
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        # Create new image with border
        bordered = Image.new('RGBA',
                           (image.width + width * 2,
                            image.height + width * 2),
                           color_rgb + (255,))

        # Paste original image in center
        bordered.paste(image, (width, width), image)

        return bordered

    def add_hard_shadow(self, image, shadow_config):
        """Add hard-edged drop shadow (no blur)"""

        # Default shadow parameters
        offset_x = shadow_config.get('offset_x', 3)
        offset_y = shadow_config.get('offset_y', 3)
        color = shadow_config.get('color', (0, 0, 0, 255))

        # Create shadow layer
        shadow = Image.new('RGBA',
                         (image.width + abs(offset_x),
                          image.height + abs(offset_y)),
                         (0, 0, 0, 0))

        # Create solid shadow shape
        shadow_shape = Image.new('RGBA', image.size, color)
        shadow_shape.putalpha(image.getchannel('A'))

        # Position shadow with offset
        shadow.paste(shadow_shape,
                    (max(0, offset_x), max(0, offset_y)),
                    shadow_shape)

        # Paste original image on top
        shadow.paste(image,
                    (max(0, -offset_x), max(0, -offset_y)),
                    image)

        return shadow

    def composite_element(self, canvas, element, position):
        """Composite an element onto the canvas at specified position"""

        x, y = position

        # Check if element would intrude into spine dead zone
        if self.check_spine_intrusion(x, y, element.width, element.height):
            print(f"WARNING: Element would intrude into spine dead zone")
            # Adjust position to avoid spine
            if x < self.spine_center:
                x = min(x, self.spine_start - element.width - 20)
            else:
                x = max(x, self.spine_end + 20)

        # Composite with alpha channel
        canvas.paste(element, (x, y), element)

        return canvas

    def check_spine_intrusion(self, x, y, width, height):
        """Check if element would overlap spine dead zone"""

        element_right = x + width
        element_left = x

        # Check if element overlaps spine area
        if element_left < self.spine_end and element_right > self.spine_start:
            return True

        return False

    def apply_cmyk_misregistration(self, image):
        """Apply CMYK channel shifts to simulate 1996 printing"""

        # Convert to numpy array for channel manipulation
        img_array = np.array(image)

        # Shift magenta channel (roughly G channel in RGB)
        # Magenta = RGB(255, 0, 255), affects R and B channels
        shifted = img_array.copy()
        shifted[:-1, :, 0] = img_array[1:, :, 0]  # Shift red down 1px

        # Shift yellow channel (roughly B channel in RGB)
        # Yellow = RGB(255, 255, 0), affects R and G channels
        shifted[:, 1:, 2] = img_array[:, :-1, 2]  # Shift blue right 1px

        return Image.fromarray(shifted)

    def apply_dot_gain(self, image, gamma=0.95):
        """Simulate dot gain on uncoated paper"""

        # Apply gamma correction to simulate ink spread
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(gamma)

        # Slightly reduce contrast (ink bleeding effect)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(0.95)

        return image

    def add_vignette(self, image, opacity=0.15):
        """Add circular vignette to simulate photographed book"""

        # Create radial gradient
        vignette = Image.new('L', (image.width, image.height), 0)
        draw = ImageDraw.Draw(vignette)

        # Calculate ellipse parameters
        center_x = image.width // 2
        center_y = image.height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)

        # Draw concentric ellipses for smooth gradient
        for i in range(255, 0, -2):
            radius = int(max_radius * (i / 255))
            opacity_val = int(255 * (1 - (i / 255) * opacity))

            draw.ellipse([center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius],
                        fill=opacity_val)

        # Apply vignette
        black = Image.new('RGB', (image.width, image.height), (0, 0, 0))
        image = Image.composite(image, black, vignette)

        return image

    def render_text_block(self, text_config):
        """Render text with period-accurate typography"""

        # Load font
        font_path = Path('assets/fonts') / f"{text_config['font']}.ttf"
        font = ImageFont.truetype(str(font_path), text_config['size'])

        # Calculate text dimensions
        lines = text_config['content'].split('\n')
        line_height = text_config.get('leading', text_config['size'] + 6)

        # Create transparent canvas for text
        width = text_config['dimensions'][0]
        height = len(lines) * line_height + 20
        text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)

        # Render each line
        y_position = 10
        for line in lines:
            # Handle single-story 'a' and 'g' for Klutz style
            if text_config.get('simplified_glyphs', False):
                line = self.simplify_glyphs(line)

            draw.text((10, y_position), line,
                     font=font,
                     fill=text_config.get('color', (0, 0, 0, 255)))
            y_position += line_height

        # Apply paper texture displacement
        if text_config.get('apply_texture', True):
            text_img = self.apply_texture_displacement(text_img)

        return text_img

    def simplify_glyphs(self, text):
        """Replace double-story a and g with single-story versions"""
        # This would require a special font or glyph substitution
        # For now, return unchanged
        return text

    def apply_texture_displacement(self, image, strength=2):
        """Apply subtle displacement based on paper texture"""

        # Load displacement map
        texture = Image.open('assets/textures/newsprint_grain.png')
        texture = texture.resize(image.size).convert('L')

        # Convert to numpy for manipulation
        img_array = np.array(image)
        texture_array = np.array(texture)

        # Create displacement map
        displacement_x = (texture_array / 255.0 - 0.5) * strength
        displacement_y = (texture_array / 255.0 - 0.5) * strength

        # Apply displacement (simplified version)
        # In production, use scipy.ndimage.map_coordinates
        result = img_array.copy()

        return Image.fromarray(result)

    def compose_spread(self, layout_config):
        """Main method to compose a complete two-page spread"""

        # Create base canvas
        canvas = self.create_base_canvas()

        # Process left page elements
        for element in layout_config['left_page']['elements']:
            asset = self.load_and_process_asset(element)
            canvas = self.composite_element(canvas, asset, element['position'])

        # Process right page elements
        for element in layout_config['right_page']['elements']:
            asset = self.load_and_process_asset(element)
            canvas = self.composite_element(canvas, asset, element['position'])

        # Render and add text blocks
        for text_block in layout_config.get('text_blocks', []):
            text_img = self.render_text_block(text_block)
            canvas = self.composite_element(canvas, text_img,
                                          text_block['position'])

        # Apply print artifacts
        canvas = self.apply_cmyk_misregistration(canvas)
        canvas = self.apply_dot_gain(canvas)
        canvas = self.add_vignette(canvas)

        return canvas


# Usage example
if __name__ == "__main__":
    compositor = KlutzCompositor()

    # Load layout configuration
    with open('config/layouts/spread_04_05.yaml', 'r') as f:
        layout = yaml.safe_load(f)

    # Compose the spread
    result = compositor.compose_spread(layout)

    # Save result
    result.save('output/spreads/spread_04_05.png', 'PNG', dpi=(300, 300))
```

## 2. Complete Asset Validation System

```python
#!/usr/bin/env python3
"""
asset_validator.py - Validates all assets meet period-authentic specifications
"""

import re
from PIL import Image
from pathlib import Path
import numpy as np
from collections import Counter

class AssetValidator:
    """Complete validation system for period authenticity"""

    def __init__(self):
        # Forbidden modern terms that would break authenticity
        self.forbidden_terms = [
            'gradient', 'web 2.0', 'flat design', 'material design',
            'responsive', 'user experience', 'UX', 'UI', 'wireframe',
            'mobile', 'touch', 'swipe', 'click and drag', 'drag and drop',
            'USB', 'wireless', 'bluetooth', 'LED', 'LCD', 'plasma',
            'broadband', 'wifi', 'streaming', 'download', 'upload',
            'social media', 'tweet', 'post', 'share', 'like',
            'smartphone', 'tablet', 'app', 'notification',
            'HD', '4K', '1080p', 'widescreen', '16:9',
            'SSD', 'flash drive', 'cloud', 'sync',
            'emoji', 'emoticon', 'gif', 'meme',
            'Google', 'Facebook', 'Twitter', 'Instagram',
            'Windows 95', 'Windows 98', 'Windows XP',
            'anti-aliasing', 'smoothing', 'blur radius',
            'transparency', 'opacity slider', 'layer mask',
            'bezier curve', 'vector graphics', 'SVG'
        ]

        # Required 1996-era terms for authenticity
        self.required_terms = {
            'mouse': ['Apple', 'Macintosh', 'M0100', 'beige', 'one-button'],
            'computer': ['Macintosh Plus', 'System 6', 'black and white'],
            'software': ['MacPaint', 'pixel', 'bitmap', '72 DPI'],
            'storage': ['floppy disk', '1.44MB', '3.5 inch'],
            'display': ['CRT', 'monitor', '512x342', 'monochrome']
        }

        # Valid color ranges (RGB)
        self.valid_colors = {
            'klutz_primary': [
                (255, 0, 0),      # Red
                (0, 0, 255),      # Blue
                (255, 255, 0),    # Yellow
                (0, 255, 0),      # Green
                (255, 165, 0),    # Orange
                (128, 0, 128)     # Purple
            ],
            'nickelodeon_orange': [(245, 125, 13)],
            'goosebumps_acid': [(149, 193, 32), (104, 234, 52)]
        }

        # Maximum percentages for accent colors
        self.color_limits = {
            'nickelodeon_orange': 0.30,
            'goosebumps_acid': 0.10
        }

    def validate_prompt(self, prompt_text):
        """Check prompt for anachronistic terms"""

        violations = []

        # Check for forbidden terms
        for term in self.forbidden_terms:
            if term.lower() in prompt_text.lower():
                violations.append(f"Forbidden term found: '{term}'")

        # Check for missing required terms based on context
        for category, terms in self.required_terms.items():
            if category.lower() in prompt_text.lower():
                has_required = any(term.lower() in prompt_text.lower()
                                 for term in terms)
                if not has_required:
                    violations.append(
                        f"Missing required {category} terminology. "
                        f"Must include one of: {terms}"
                    )

        # Check for modern design language
        modern_patterns = [
            r'\bflat\s+\w+\b',
            r'\bminimal(?:ist)?\b',
            r'\bclean\s+(?:and\s+)?modern\b',
            r'\buser\s+friendly\b',
            r'\bintuitive\s+interface\b'
        ]

        for pattern in modern_patterns:
            if re.search(pattern, prompt_text, re.IGNORECASE):
                violations.append(f"Modern design language detected: {pattern}")

        return violations

    def validate_image_asset(self, image_path):
        """Validate an image meets specifications"""

        image = Image.open(image_path)
        violations = []

        # Check dimensions
        if image.width > 1200 or image.height > 1200:
            violations.append(
                f"Image too large: {image.width}x{image.height}. "
                f"Max component size is 1200x1200"
            )

        # Check for forbidden effects
        violations.extend(self.check_forbidden_effects(image))

        # Check color distribution
        violations.extend(self.check_color_distribution(image))

        # Check for proper shadows
        violations.extend(self.check_shadow_style(image))

        return violations

    def check_forbidden_effects(self, image):
        """Detect modern effects that shouldn't exist"""

        violations = []
        img_array = np.array(image)

        # Check for gradients (more than 10 unique colors in a row)
        for row in img_array:
            unique_colors = len(np.unique(row.reshape(-1, row.shape[-1]),
                                         axis=0))
            if unique_colors > 50:
                violations.append("Gradient detected - use solid colors only")
                break

        # Check for soft shadows (blur detection)
        edges = self.detect_edges(img_array)
        if self.has_soft_edges(edges):
            violations.append("Soft shadows detected - use hard shadows only")

        # Check for transparency (besides full transparent)
        if image.mode == 'RGBA':
            alpha = np.array(image.getchannel('A'))
            unique_alphas = np.unique(alpha)
            if len(unique_alphas) > 2:  # More than just 0 and 255
                violations.append("Partial transparency detected - not period accurate")

        return violations

    def detect_edges(self, img_array):
        """Simple edge detection for shadow analysis"""

        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])

        # Sobel edge detection (simplified)
        dx = np.diff(gray, axis=1)
        dy = np.diff(gray, axis=0)

        edges = np.sqrt(dx[:-1]**2 + dy[:,:-1]**2)

        return edges

    def has_soft_edges(self, edges, threshold=0.3):
        """Check if edges are soft (blurred)"""

        # Count pixels with intermediate edge values
        soft_pixels = np.sum((edges > 0.1) & (edges < 0.9))
        total_pixels = edges.size

        soft_ratio = soft_pixels / total_pixels

        return soft_ratio > threshold

    def check_color_distribution(self, image):
        """Verify color usage follows 70/20/10 rule"""

        violations = []
        img_array = np.array(image.convert('RGB'))

        # Flatten and count colors
        pixels = img_array.reshape(-1, 3)
        total_pixels = len(pixels)

        # Categorize colors
        nickelodeon_count = 0
        goosebumps_count = 0

        for pixel in pixels:
            if self.is_color_match(pixel, self.valid_colors['nickelodeon_orange']):
                nickelodeon_count += 1
            elif self.is_color_match(pixel, self.valid_colors['goosebumps_acid']):
                goosebumps_count += 1

        # Check ratios
        nick_ratio = nickelodeon_count / total_pixels
        goose_ratio = goosebumps_count / total_pixels

        if nick_ratio > self.color_limits['nickelodeon_orange']:
            violations.append(
                f"Too much Nickelodeon orange: {nick_ratio:.1%} "
                f"(max {self.color_limits['nickelodeon_orange']:.0%})"
            )

        if goose_ratio > self.color_limits['goosebumps_acid']:
            violations.append(
                f"Too much Goosebumps acid green: {goose_ratio:.1%} "
                f"(max {self.color_limits['goosebumps_acid']:.0%})"
            )

        return violations

    def is_color_match(self, pixel, valid_colors, tolerance=30):
        """Check if a pixel matches any valid color within tolerance"""

        for valid_color in valid_colors:
            distance = np.sqrt(sum((p - v)**2 for p, v in zip(pixel, valid_color)))
            if distance < tolerance:
                return True
        return False

    def check_shadow_style(self, image):
        """Verify shadows are hard-edged, not soft"""

        violations = []

        # Look for characteristic hard shadow pattern
        # (solid black pixels adjacent to colored pixels)
        img_array = np.array(image.convert('RGBA'))

        # Find potential shadow pixels (dark, not pure black)
        shadow_mask = np.all(img_array[:,:,:3] < 50, axis=2)

        if np.any(shadow_mask):
            # Check if shadow has hard edges
            shadow_edges = np.diff(shadow_mask.astype(int))

            # Hard shadows should have sharp transitions (values of 1 or -1)
            edge_values = np.unique(shadow_edges)

            if len(edge_values) > 3:  # More than just -1, 0, 1
                violations.append("Shadow edges are not hard enough")

        return violations

    def validate_layout(self, layout_config):
        """Validate a complete layout configuration"""

        violations = []

        # Check spine intrusion
        for page in ['left_page', 'right_page']:
            for element in layout_config[page]['elements']:
                x, y = element['position']
                w, h = element.get('dimensions', (100, 100))

                # Check if element intrudes into spine dead zone (1469-1931)
                if x < 1931 and x + w > 1469:
                    violations.append(
                        f"Element {element['id']} intrudes into spine dead zone"
                    )

        # Check rotation limits
        for page in ['left_page', 'right_page']:
            for element in layout_config[page]['elements']:
                rotation = abs(element.get('rotation', 0))

                if 'text' in element['type'] and rotation > 5:
                    violations.append(
                        f"Text element {element['id']} rotated too much: {rotation}° (max 5°)"
                    )
                elif rotation > 15:
                    violations.append(
                        f"Element {element['id']} rotated too much: {rotation}° (max 15°)"
                    )

        return violations

    def validate_complete_project(self, project_dir):
        """Run all validations on entire project"""

        project_path = Path(project_dir)
        report = {
            'prompts': {},
            'assets': {},
            'layouts': {},
            'summary': {'passed': 0, 'failed': 0}
        }

        # Validate all prompts
        for prompt_file in project_path.glob('prompts/**/*.txt'):
            violations = self.validate_prompt(prompt_file.read_text())
            report['prompts'][str(prompt_file)] = violations

            if violations:
                report['summary']['failed'] += 1
            else:
                report['summary']['passed'] += 1

        # Validate all layouts
        for layout_file in project_path.glob('config/layouts/*.yaml'):
            with open(layout_file, 'r') as f:
                layout = yaml.safe_load(f)
            violations = self.validate_layout(layout)
            report['layouts'][str(layout_file)] = violations

            if violations:
                report['summary']['failed'] += 1
            else:
                report['summary']['passed'] += 1

        return report


# Usage example
if __name__ == "__main__":
    validator = AssetValidator()

    # Test prompt validation
    test_prompt = """
    Create a photograph of a child using an Apple Macintosh Plus mouse.
    The mouse should be beige, model M0100, with sharp focus and no gradients.
    """

    violations = validator.validate_prompt(test_prompt)
    if violations:
        print("Prompt violations found:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("Prompt passed validation!")

    # Run complete project validation
    report = validator.validate_complete_project('.')
    print(f"\nValidation Summary: {report['summary']}")
```

## 3. Complete Prompt Generation System for Gemini

```python
#!/usr/bin/env python3
"""
prompt_generator.py - Generates XML prompts for nano-banana via Gemini
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class PromptGenerator:
    """Generates hyper-specific XML prompts from layout configs"""

    def __init__(self):
        # Load master configuration
        with open('config/master_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # Component-specific prompt templates
        self.templates = {
            'graphic_photo_instructional': self.generate_photo_prompt,
            'container_featurebox': self.generate_container_prompt,
            'graphic_splat_container': self.generate_splat_prompt,
            'graphic_pixelart': self.generate_pixelart_prompt,
            'graphic_gui_recreation': self.generate_gui_prompt,
            'graphic_doodle': self.generate_doodle_prompt,
            'container_embossed_featurebox': self.generate_embossed_prompt
        }

        # Standard negative prompts by category
        self.negative_prompts = {
            'modern_tech': [
                'wireless mouse', 'optical mouse', 'gaming mouse', 'RGB lighting',
                'USB cable', 'wireless', 'bluetooth', 'LED', 'LCD screen',
                'flat screen', 'widescreen', 'smartphone', 'tablet'
            ],
            'modern_design': [
                'gradient', 'soft shadow', 'blur', 'transparency', 'glow',
                'bevel effect', '3D rendering', 'photorealistic', 'HDR',
                'depth of field', 'bokeh', 'lens flare', 'modern', 'minimal',
                'flat design', 'material design', 'anti-aliasing'
            ],
            'wrong_era': [
                'Windows 95', 'Windows', 'PC', 'IBM', 'modern computer',
                '2000s', '2010s', 'contemporary', 'current', 'new'
            ],
            'wrong_style': [
                'professional photography', 'stock photo', 'artistic',
                'dramatic lighting', 'moody', 'cinematic', 'stylized',
                'abstract', 'conceptual', 'fine art'
            ]
        }

    def generate_photo_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for instructional photography"""

        # Extract specifications
        subject = element.get('subject', 'hand using mouse')
        camera_settings = element.get('camera', {})
        lighting = element.get('lighting', {})

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_photo_instructional</element_type>

    <image_specifications>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <resolution dpi="300" />
        <color_mode>RGB</color_mode>
        <bit_depth>24</bit_depth>
    </image_specifications>

    <photographic_parameters>
        <film_stock>Kodak Gold 400</film_stock>
        <film_characteristics>
            <grain_index>39</grain_index>
            <grain_pattern>silver_halide_cubic</grain_pattern>
            <color_profile>
                <highlights>warm_bias</highlights>
                <midtones>neutral</midtones>
                <shadows>slight_cyan_shift</shadows>
            </color_profile>
        </film_characteristics>

        <camera_settings>
            <lens>{camera_settings.get('lens', '100mm macro')}</lens>
            <aperture>{camera_settings.get('aperture', 'f/11')}</aperture>
            <shutter_speed>{camera_settings.get('shutter', '1/125')}</shutter_speed>
            <focus_distance>{camera_settings.get('focus', '8 inches')}</focus_distance>
        </camera_settings>

        <lighting_setup>
            <ambient_level>moderate</ambient_level>
            <key_light>
                <type>softbox_24x36_inch</type>
                <position_horizontal>45_degrees_left</position_horizontal>
                <position_vertical>30_degrees_above</position_vertical>
                <distance>24_inches</distance>
                <power>100_percent</power>
                <color_temperature>5500K</color_temperature>
            </key_light>
            <fill_light>
                <type>white_foamcore_reflector</type>
                <position_horizontal>60_degrees_right</position_horizontal>
                <distance>18_inches</distance>
                <efficiency>50_percent</efficiency>
            </fill_light>
        </lighting_setup>
    </photographic_parameters>

    <subject_description>
        <primary>{subject}</primary>
        <details>
            <hand_age>8-10 years old</hand_age>
            <hand_characteristics>child-sized, natural, unprofessional</hand_characteristics>
            <mouse_model>Apple Desktop Bus Mouse M0100</mouse_model>
            <mouse_color>beige plastic with slight yellowing from age</mouse_color>
            <mouse_details>rectangular shape, single button, visible ADB cable</mouse_details>
            <background>solid color mousepad, royal blue fabric surface</background>
        </details>
    </subject_description>

    <composition>
        <angle>high angle, approximately 45 degrees from horizontal</angle>
        <framing>mouse fills 60% of frame, hand partially visible</framing>
        <focus_point>mouse button and index finger</focus_point>
        <depth_of_field>moderate, f/11 for sharp detail throughout</depth_of_field>
    </composition>

    <positive_prompt>
        Professional instructional photograph from 1996 children's computer book,
        8-year-old child's hand demonstrating proper grip on beige Apple M0100
        rectangular mouse, single button mouse with coiled ADB cable visible,
        index finger positioned correctly on mouse button, natural child grip,
        photographed on Kodak Gold 400 35mm film with visible grain structure,
        characteristic warm highlights and neutral midtones of Gold 400 film,
        high angle view showing mouse and partial hand, royal blue mousepad
        background, even lighting from softbox creating soft but defined shadows,
        sharp focus throughout with f/11 aperture, educational photography style,
        bright and approachable mood, slight film grain visible, authentic
        1990s color reproduction
    </positive_prompt>

    <negative_prompt>
        {', '.join(self.negative_prompts['modern_tech'])},
        {', '.join(self.negative_prompts['modern_design'])},
        {', '.join(self.negative_prompts['wrong_style'])},
        adult hands, professional hand model, manicured nails,
        jewelry, watches, dramatic shadows, artistic composition,
        shallow depth of field, two-button mouse, scroll wheel,
        dark mood, low key lighting, high contrast
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def generate_container_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for feature box containers"""

        bg_color = element.get('background', '#FFD700')
        border = element.get('border', '4px solid black')

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>container_featurebox</element_type>

    <geometry>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <rotation degrees="{element.get('rotation', 0)}" />
    </geometry>

    <visual_properties>
        <background>
            <type>solid_color</type>
            <color>{bg_color}</color>
            <texture>none</texture>
        </background>

        <border>
            <style>solid</style>
            <width>4px</width>
            <color>#000000</color>
            <corners>square</corners>
        </border>

        <shadow>
            <type>hard_drop_shadow</type>
            <offset_x>3px</offset_x>
            <offset_y>3px</offset_y>
            <blur>0px</blur>
            <color>#000000</color>
            <opacity>100%</opacity>
        </shadow>
    </visual_properties>

    <positive_prompt>
        Flat rectangular container with solid {bg_color} background,
        thick 4 pixel black border with perfectly square corners,
        hard-edged drop shadow offset 3 pixels right and 3 pixels down,
        pure black shadow with no blur or softness, 1996 desktop
        publishing aesthetic, primitive digital graphic design,
        no gradients or modern effects
    </positive_prompt>

    <negative_prompt>
        gradient, soft shadow, blur, rounded corners, bevel,
        3D effect, transparency, anti-aliasing, modern design,
        subtle, sophisticated, professional, glossy, texture
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def generate_splat_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for Nickelodeon-style splat containers"""

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_splat_container</element_type>

    <geometry>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <rotation degrees="{element.get('rotation', 0)}" />
    </geometry>

    <visual_properties>
        <splat_characteristics>
            <color>#F57D0D</color>  <!-- Nickelodeon Orange -->
            <style>organic_blob</style>
            <edges>irregular</edges>
            <splatter_points>3-5</splatter_points>
        </splat_characteristics>
    </visual_properties>

    <positive_prompt>
        Nickelodeon-style orange splat shape, Pantone Orange 021 C color
        (#F57D0D), organic blob with irregular edges and 3-5 splatter points,
        flat solid color with no gradients, hard edges, 1996 Nickelodeon
        branding aesthetic, energetic and playful shape, slightly asymmetric,
        like spilled paint or slime
    </positive_prompt>

    <negative_prompt>
        gradient, soft edges, blur, drop shadow, 3D effect,
        perfect circle, geometric shape, modern design, subtle,
        transparency, texture, shading, highlights
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def generate_pixelart_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for pixel art sprites"""

        palette = element.get('palette', 'NES_limited')
        magnification = element.get('magnification', 8)

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_pixelart</element_type>

    <pixel_specifications>
        <base_resolution>32x32</base_resolution>
        <display_magnification>{magnification}x</display_magnification>
        <interpolation>nearest_neighbor</interpolation>
        <antialiasing>none</antialiasing>
    </pixel_specifications>

    <color_palette>
        <type>{palette}</type>
        <colors>
            <color index="0">#000000</color>  <!-- Black -->
            <color index="1">#FFFFFF</color>  <!-- White -->
            <color index="2">#FF0000</color>  <!-- Red -->
            <color index="3">#00FF00</color>  <!-- Green -->
            <color index="4">#0000FF</color>  <!-- Blue -->
            <color index="5">#FFFF00</color>  <!-- Yellow -->
            <color index="6">#FF00FF</color>  <!-- Magenta -->
            <color index="7">#00FFFF</color>  <!-- Cyan -->
            <color index="8">#C0C0C0</color>  <!-- Light Gray -->
            <color index="9">#808080</color>  <!-- Dark Gray -->
            <color index="10">#800000</color> <!-- Dark Red -->
            <color index="11">#008000</color> <!-- Dark Green -->
            <color index="12">#000080</color> <!-- Dark Blue -->
            <color index="13">#808000</color> <!-- Olive -->
            <color index="14">#800080</color> <!-- Purple -->
            <color index="15">#008080</color> <!-- Teal -->
        </colors>
    </color_palette>

    <subject>{element.get('subject', 'pixel monster sprite')}</subject>

    <positive_prompt>
        8-bit pixel art sprite, 32x32 pixel base resolution scaled up {magnification}x
        with nearest neighbor interpolation, hard pixel edges with no anti-aliasing,
        limited {palette} color palette, retro video game aesthetic circa 1990,
        clear readable sprite design, solid colors per pixel, no blending
    </positive_prompt>

    <negative_prompt>
        anti-aliasing, smooth edges, gradient, blur, high resolution,
        modern pixel art, detailed shading, transparency, soft pixels,
        interpolation artifacts, photorealistic, 3D rendering
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def generate_gui_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for GUI recreation (MacPaint/Aseprite)"""

        software = element.get('software', 'MacPaint')

        if software == 'MacPaint':
            xml_prompt = self.generate_macpaint_gui(element)
        else:
            xml_prompt = self.generate_aseprite_gui(element)

        return xml_prompt

    def generate_macpaint_gui(self, element: Dict[str, Any]) -> str:
        """Generate MacPaint interface recreation"""

        return f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>

    <software_interface>
        <application>MacPaint 1.0</application>
        <os>Apple System 6</os>
        <year>1984-1990</year>
    </software_interface>

    <interface_elements>
        <window>
            <title_bar>
                <text>untitled</text>
                <font>Chicago 12pt</font>
                <close_box>left</close_box>
                <zoom_box>none</zoom_box>
            </title_bar>

            <menu_bar>
                <items>File Edit Goodies Font FontSize Style</items>
                <font>Chicago 12pt</font>
            </menu_bar>

            <tool_palette>
                <position>left</position>
                <tools>
                    <row1>line_thickness_options</row1>
                    <row2>selection_rectangle lasso</row2>
                    <row3>pencil paintbrush</row3>
                    <row4>paint_bucket spray_can</row4>
                    <row5>line rectangle</row5>
                    <row6>oval polygon</row6>
                </tools>
            </tool_palette>

            <pattern_palette>
                <position>bottom</position>
                <patterns>38 standard MacPaint patterns</patterns>
                <display>8x5 grid</display>
            </pattern_palette>
        </window>

        <canvas>
            <dimensions>576x720</dimensions>
            <color_mode>1-bit monochrome</color_mode>
            <dithering>Atkinson dithering</dithering>
        </canvas>
    </interface_elements>

    <visual_style>
        <colors>pure black and white only</colors>
        <fonts>Chicago bitmap font</fonts>
        <shadows>none</shadows>
        <effects>stippled patterns for gray simulation</effects>
    </visual_style>

    <positive_prompt>
        Perfect recreation of MacPaint 1.0 interface from Apple System 6,
        monochrome black and white only, Chicago bitmap font for all text,
        no anti-aliasing, tool palette on left with 6 rows of tools,
        pattern palette at bottom with 38 patterns in grid, single pixel
        black borders, stippled patterns to simulate grayscale,
        Atkinson dithering for images, authentic 1984-1990 Macintosh
        software interface
    </positive_prompt>

    <negative_prompt>
        color, grayscale, anti-aliasing, smooth fonts, gradients,
        shadows, modern UI, Windows, transparency, 3D effects,
        rounded corners, subtle design, contemporary interface
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_aseprite_gui(self, element: Dict[str, Any]) -> str:
        """Generate simplified Aseprite interface for teaching"""

        return f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>

    <software_interface>
        <application>Aseprite (simplified for kids)</application>
        <style>1996 software aesthetic</style>
    </software_interface>

    <interface_elements>
        <color_picker>
            <type>RGB sliders</type>
            <display>simplified grid</display>
            <preset_palette>16 colors</preset_palette>
        </color_picker>

        <tool_icons>
            <pencil>single pixel drawing</pencil>
            <eraser>pixel removal</eraser>
            <paint_bucket>flood fill</paint_bucket>
            <rectangle>shape tool</rectangle>
        </tool_icons>

        <canvas_grid>
            <visible>true</visible>
            <size>32x32 pixels</size>
            <grid_lines>1px gray</grid_lines>
        </canvas_grid>
    </interface_elements>

    <positive_prompt>
        Simplified pixel art software interface designed for children,
        basic tool palette with pencil eraser bucket and shapes,
        16 color palette grid, visible pixel grid on canvas,
        1996 software design aesthetic with gray 3D borders,
        simple and clear icons, educational software appearance
    </positive_prompt>

    <negative_prompt>
        modern UI, flat design, complex interface, professional software,
        dark theme, transparency, advanced tools, layers panel,
        timeline, animation controls
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_doodle_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for hand-drawn doodles"""

        doodle_type = element.get('doodle_type', 'arrow')

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_doodle</element_type>

    <doodle_specifications>
        <type>{doodle_type}</type>
        <style>hand_drawn</style>
        <line_weight>3-5px</line_weight>
        <color>#000000</color>
        <consistency>slightly_uneven</consistency>
    </doodle_specifications>

    <characteristics>
        <line_quality>confident but imperfect</line_quality>
        <corners>slightly rounded from marker tip</corners>
        <ends>natural taper or blob from lifting marker</ends>
    </characteristics>

    <positive_prompt>
        Hand-drawn {doodle_type} with thick black marker, confident
        single stroke, slightly uneven line weight, natural imperfections,
        looks like drawn by enthusiastic teacher on whiteboard,
        3-5 pixel thick line, no perfectly straight lines,
        organic and energetic appearance
    </positive_prompt>

    <negative_prompt>
        perfect geometry, vector graphics, thin line, pencil,
        tentative strokes, multiple strokes, shading, gradient,
        computer-generated, precise, mathematical, ruler-drawn
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def generate_embossed_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for embossed feature boxes"""

        text = element.get('embossed_text', 'TIP!')

        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>container_embossed_featurebox</element_type>

    <embossing_specifications>
        <technique>blind_embossing</technique>
        <depth>15-25 microns</depth>
        <style>raised_from_behind</style>
        <text>{text}</text>
        <font>Chicago or similar bold sans-serif</font>
    </embossing_specifications>

    <visual_effect>
        <highlights>top and left edges of raised areas</highlights>
        <shadows>bottom and right edges of raised areas</shadows>
        <surface>paper texture visible on raised portions</surface>
        <no_ink>true</no_ink>
        <no_foil>true</no_foil>
    </visual_effect>

    <positive_prompt>
        Blind embossed text "{text}" pressed into paper from behind,
        raised bumpy 3D letters with hard-edged highlights on top-left,
        hard shadows on bottom-right, no ink or color on letters,
        paper texture visible on raised surface, authentic embossing
        effect like Goosebumps book covers, tactile appearance
    </positive_prompt>

    <negative_prompt>
        printed text, ink, foil, color, flat, 2D, Photoshop bevel effect,
        soft inner glow, gradient, smooth, digital effect, letterpress,
        debossing, metallic, glossy
    </negative_prompt>
</nano_banana_prompt>"""

        return xml_prompt

    def create_gemini_metaprompt(self, element: Dict[str, Any]) -> str:
        """Create the prompt to send to Gemini for XML generation"""

        metaprompt = f"""
You are a specialized prompt engineer for a 1996 Klutz Press computer graphics workbook.
Generate a hyper-specific XML prompt for the nano-banana image model.

Element specifications:
- ID: {element['id']}
- Type: {element['type']}
- Dimensions: {element['dimensions']}
- Position: {element['position']}
- Additional specs: {json.dumps(element, indent=2)}

CRITICAL RULES:
1. Use ONLY quantitative language (pixels, degrees, hex colors)
2. NO subjective terms (nice, good, beautiful, modern)
3. Specify everything as if explaining to a machine
4. Include comprehensive negative prompts
5. Reference only 1996-available technology

The XML must follow this exact structure:
<nano_banana_prompt>
    <element_id>...</element_id>
    <element_type>...</element_type>
    [element-specific sections]
    <positive_prompt>...</positive_prompt>
    <negative_prompt>...</negative_prompt>
</nano_banana_prompt>

Generate the complete XML prompt now.
"""

        return metaprompt

    def generate_all_prompts(self, layout_file: str) -> Dict[str, str]:
        """Generate all prompts for a layout"""

        with open(layout_file, 'r') as f:
            layout = yaml.safe_load(f)

        prompts = {}

        for page in ['left_page', 'right_page']:
            for element in layout[page]['elements']:
                element_type = element['type']

                if element_type in self.templates:
                    # Generate specific prompt
                    xml_prompt = self.templates[element_type](element)
                    prompts[element['id']] = xml_prompt

                    # Save to file
                    output_path = Path('prompts/components') / f"{element['id']}.xml"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(xml_prompt)

        return prompts


# Usage example
if __name__ == "__main__":
    generator = PromptGenerator()

    # Test element
    test_element = {
        'id': 'L_photo_mouse_01',
        'type': 'graphic_photo_instructional',
        'dimensions': [600, 450],
        'position': [250, 300],
        'subject': 'child hand using Apple mouse',
        'camera': {'lens': '100mm macro', 'aperture': 'f/11'}
    }

    # Generate prompt
    xml_prompt = generator.generate_photo_prompt(test_element)
    print(xml_prompt)

    # Generate all prompts for a layout
    prompts = generator.generate_all_prompts('config/layouts/spread_04_05.yaml')
    print(f"Generated {len(prompts)} prompts")

        # Validate all image assets
        for image_file in project_path.glob('assets/**/*.png'):
            violations = self.validate_image_asset(image_file)
            report['assets'][str(image_file)] = violations

            if violations:
                report['summary']['failed'] += 1
            else:
                report['summary']['passed'] += 1
