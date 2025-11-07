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

        self.logger.info(f"Created {len(directories)} directories")

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
        sys.exit(1)
