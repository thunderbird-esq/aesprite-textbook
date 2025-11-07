#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
asset_validator.py - Validates all VISUAL ASSETS and GENERATION PROMPTS
to meet period-authentic specifications for 1996 Klutz Press aesthetic.

This script is the "Period Police" - the guardian of visual authenticity.
It must be run on all prompts and generated assets before they are added
to the library.

Usage:
    python asset_validator.py --prompt <file>   # Validate a prompt file
    python asset_validator.py --image <file>    # Validate an image asset
    python asset_validator.py --layout <file>   # Validate a layout config

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

import numpy as np
import yaml
from PIL import Image


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AssetValidator:
    """Complete validation system for 1996 period authenticity in visual design.

    This validator enforces strict rules for:
    - Visual design prompts (no anachronistic terms)
    - Image assets (dimensions, format, color distribution)
    - Layout configurations (spine safety, rotation limits, safe zones)

    The forbidden terms list applies to prompts for generating DESIGN ELEMENTS.
    It does NOT apply to the body text content of the workbook, which may use
    modern technical terms when explaining Aseprite.

    Attributes:
        forbidden_design_terms (List[str]): Terms prohibited in visual prompts
        allowed_modern_terms_in_prompts (List[str]): Modern terms allowed for Aseprite
        required_visual_terms (Dict[str, List[str]]): Required terms for hardware/software
        color_limits (Dict[str, float]): Maximum color usage ratios

    Example:
        >>> validator = AssetValidator()
        >>> violations = validator.validate_visual_prompt("Create a flat design button")
        >>> if violations:
        ...     print("Validation failed:", violations)
    """

    def __init__(self, config_path: str = 'config/master_config.yaml') -> None:
        """Initialize the validator with 1996 authenticity rules.

        Sets up forbidden terms, allowed exceptions, required terminology,
        and color distribution limits based on the Klutz Press aesthetic.

        Args:
            config_path: Path to master configuration YAML file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        logger.info(f"Initializing AssetValidator with config: {config_path}")

        # Load configuration from master_config.yaml
        config_file = Path(config_path)
        if config_file.exists():
            logger.info(f"Loading configuration from {config_path}")
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self.config = {}

        # MODIFIED: This list applies to prompts for generating DESIGN ELEMENTS.
        # It does NOT apply to the body text of the workbook.
        self.forbidden_design_terms: List[str] = [
            'gradient', 'web 2.0', 'flat design', 'material design', 'minimalist',
            'responsive', 'user experience', 'UX', 'UI', 'wireframe',
            'mobile', 'touch', 'swipe', 'drag and drop',
            'USB', 'wireless', 'bluetooth', 'LED', 'LCD', 'plasma',
            'broadband', 'wifi', 'streaming',
            'social media', 'tweet', 'post', 'share', 'like', 'hashtag',
            'smartphone', 'tablet', 'app', 'notification', 'cloud', 'sync',
            'HD', '4K', '1080p', 'widescreen', '16:9', 'retina',
            'SSD', 'flash drive',
            'emoji', 'gif', 'meme',
            'Google', 'Facebook', 'Twitter', 'Instagram', 'Pinterest',
            'Windows 95', 'Windows 98', 'Windows XP',
            'anti-aliasing', 'smoothing', 'blur radius', 'soft shadow',
            'opacity slider', 'layer mask',
            'bezier curve', 'vector graphics', 'SVG', 'AI', 'photoshop'
        ]

        # Allowed modern terms for discussing Aseprite's technical features in prompts
        self.allowed_modern_terms_in_prompts: List[str] = [
            'aseprite', 'github', 'version control', 'export', 'layer',
            'sprite sheet', 'animation', 'timeline', 'pixel-perfect',
            'hex code', 'rgb', 'alpha channel', 'transparent', 'png'
        ]

        # Required terms to ensure authenticity in visual depictions
        self.required_visual_terms: Dict[str, List[str]] = {
            'mouse': ['Apple', 'Macintosh', 'M0100', 'beige', 'one-button'],
            'computer': ['Macintosh Plus', 'System 6', 'black and white'],
            'software': ['MacPaint', 'pixel', 'bitmap', '72 DPI'],
            'storage': ['floppy disk', '1.44MB', '3.5 inch'],
            'display': ['CRT', 'monitor', '512x342', 'monochrome']
        }

        # Load canvas dimensions from config (with fallback defaults)
        if self.config and 'technical' in self.config:
            canvas_size = self.config['technical'].get('canvas_size', [3400, 2200])
            self.canvas_width: int = canvas_size[0]
            self.canvas_height: int = canvas_size[1]
            logger.info(f"Canvas dimensions from config: {self.canvas_width}x{self.canvas_height}")
        else:
            # Fallback to hardcoded defaults
            self.canvas_width: int = 3400
            self.canvas_height: int = 2200
            logger.info(f"Canvas dimensions from defaults: {self.canvas_width}x{self.canvas_height}")

        # Load color distribution limits from config (with fallback defaults)
        if self.config and 'aesthetic_rules' in self.config and 'color_distribution' in self.config['aesthetic_rules']:
            color_dist = self.config['aesthetic_rules']['color_distribution']
            # Map config values to validator's color limits
            # nickelodeon_accent is 20% target, but we allow 30% as buffer (20% * 1.5)
            nickelodeon_limit = color_dist.get('nickelodeon_accent', 0.20) * 1.5
            goosebumps_limit = color_dist.get('goosebumps_theme', 0.10)

            self.color_limits: Dict[str, float] = {
                'nickelodeon_orange': nickelodeon_limit,
                'goosebumps_acid': goosebumps_limit
            }
            logger.info(f"Color limits from config: orange={nickelodeon_limit:.2%}, acid={goosebumps_limit:.2%}")
        else:
            # Fallback to hardcoded defaults
            self.color_limits: Dict[str, float] = {
                'nickelodeon_orange': 0.30,  # Maximum 30% (actually 20% target + buffer)
                'goosebumps_acid': 0.10      # Maximum 10%
            }
            logger.info(f"Color limits from defaults: orange=30%, acid=10%")

        # Calculate spine dead zone boundaries from config (with fallback defaults)
        if self.config and 'technical' in self.config:
            spine_width = self.config['technical'].get('spine_width', None)
            if spine_width is not None:
                # Calculate spine boundaries like klutz_compositor does
                spine_center = self.canvas_width // 2
                self.spine_start: int = spine_center - (spine_width // 2)
                self.spine_end: int = spine_center + (spine_width // 2)
                logger.info(f"Spine boundaries from config: {self.spine_start}-{self.spine_end} (width={spine_width})")
            else:
                # Fallback to hardcoded defaults
                self.spine_start: int = 1469
                self.spine_end: int = 1931
                logger.info(f"Spine boundaries from defaults: {self.spine_start}-{self.spine_end}")
        else:
            # Fallback to hardcoded defaults
            self.spine_start: int = 1469
            self.spine_end: int = 1931
            logger.info(f"Spine boundaries from defaults: {self.spine_start}-{self.spine_end}")

        # Load rotation limits from config (with fallback defaults)
        if self.config and 'aesthetic_rules' in self.config and 'rotation_limits' in self.config['aesthetic_rules']:
            rotation_cfg = self.config['aesthetic_rules']['rotation_limits']
            self.rotation_limits: Dict[str, float] = {
                'text': float(rotation_cfg.get('text', 5)),
                'text_headline': float(rotation_cfg.get('text', 5)),
                'text_body': float(rotation_cfg.get('text', 5)),
                'containers': float(rotation_cfg.get('containers', 15)),
                'container_featurebox': float(rotation_cfg.get('containers', 15)),
                'photos': float(rotation_cfg.get('photos', 10)),
                'graphic_photo_instructional': float(rotation_cfg.get('photos', 10))
            }
            logger.info(f"Rotation limits from config: text={self.rotation_limits['text']}°, "
                       f"containers={self.rotation_limits['containers']}°, "
                       f"photos={self.rotation_limits['photos']}°")
        else:
            # Fallback to hardcoded defaults
            self.rotation_limits: Dict[str, float] = {
                'text': 5.0,
                'text_headline': 5.0,
                'text_body': 5.0,
                'containers': 15.0,
                'container_featurebox': 15.0,
                'photos': 10.0,
                'graphic_photo_instructional': 10.0
            }
            logger.info(f"Rotation limits from defaults: text=5°, containers=15°, photos=10°")

        # Load safe zone margins from config (with fallback defaults)
        if self.config and 'layout' in self.config and 'safe_zones' in self.config['layout']:
            safe_zones = self.config['layout']['safe_zones']
            self.safe_zone_left: int = safe_zones.get('left', 100)
            self.safe_zone_right: int = safe_zones.get('right', 100)
            self.safe_zone_top: int = safe_zones.get('top', 100)
            self.safe_zone_bottom: int = safe_zones.get('bottom', 100)
            logger.info(f"Safe zones from config: L={self.safe_zone_left}, R={self.safe_zone_right}, "
                       f"T={self.safe_zone_top}, B={self.safe_zone_bottom}")
        else:
            # Fallback to hardcoded defaults
            self.safe_zone_left: int = 100
            self.safe_zone_right: int = 100
            self.safe_zone_top: int = 100
            self.safe_zone_bottom: int = 100
            logger.info(f"Safe zones from defaults: L=R=T=B=100px")

        logger.info(f"Loaded {len(self.forbidden_design_terms)} forbidden terms")
        logger.info(f"Loaded {len(self.allowed_modern_terms_in_prompts)} allowed modern terms")
        logger.info(f"Loaded {len(self.required_visual_terms)} required term categories")

    def validate_visual_prompt(self, prompt_text: str) -> List[str]:
        """Check a generation prompt for anachronistic design terms.

        This validation ensures that prompts used to generate visual assets
        maintain 1996 authenticity. Modern terms are flagged unless they are
        in the allowed list (for Aseprite-specific functionality).

        Args:
            prompt_text (str): The prompt text to validate

        Returns:
            List[str]: List of violation messages. Empty list if validation passes.

        Example:
            >>> validator = AssetValidator()
            >>> violations = validator.validate_visual_prompt(
            ...     "Create a gradient button with flat design"
            ... )
            >>> print(violations)
            ['Forbidden design term in prompt: gradient',
             'Forbidden design term in prompt: flat design']
        """
        logger.info("Validating visual prompt")
        violations: List[str] = []
        prompt_lower = prompt_text.lower()

        # Check for forbidden design terms, respecting the allow-list
        for term in self.forbidden_design_terms:
            term_lower = term.lower()
            # Skip if term is in allowed list
            if term_lower in [allowed.lower() for allowed in self.allowed_modern_terms_in_prompts]:
                continue

            # Use word boundary matching for better accuracy
            # Match whole words or phrases, not substrings
            pattern = r'\b' + re.escape(term_lower) + r'\b'
            if re.search(pattern, prompt_lower):
                violations.append(
                    f"Forbidden design term in prompt: '{term}' - "
                    f"This term represents post-1996 design concepts"
                )
                logger.warning(f"Found forbidden term: {term}")

        # Check for required terms when depicting hardware/software
        for category, required_terms in self.required_visual_terms.items():
            if category.lower() in prompt_lower:
                # Check if at least one required term is present
                if not any(term.lower() in prompt_lower for term in required_terms):
                    violations.append(
                        f"Missing required visual terminology for '{category}'. "
                        f"Must include one of: {', '.join(required_terms)}"
                    )
                    logger.warning(
                        f"Missing required terms for category: {category}"
                    )

        if violations:
            logger.error(f"Prompt validation failed with {len(violations)} violations")
        else:
            logger.info("Prompt validation passed")

        return violations

    def validate_image_asset(self, image_path: str) -> List[str]:
        """Validate an image meets all technical and aesthetic specifications.

        Checks:
        - File exists and is readable
        - Dimensions are sensible (not 0x0, not > 10000px)
        - File format is PNG with transparency support
        - Color distribution against limits (Nickelodeon orange, Goosebumps acid)
        - Rotation metadata if present

        Args:
            image_path (str): Path to the image file to validate

        Returns:
            List[str]: List of violation messages. Empty list if validation passes.

        Example:
            >>> validator = AssetValidator()
            >>> violations = validator.validate_image_asset("assets/photo_mouse_01.png")
            >>> if violations:
            ...     print("Image validation failed:", violations)
        """
        logger.info(f"Validating image asset: {image_path}")
        violations: List[str] = []
        path = Path(image_path)

        # Check file existence
        if not path.exists():
            violations.append(f"Image file does not exist: {image_path}")
            logger.error(f"File not found: {image_path}")
            return violations

        if not path.is_file():
            violations.append(f"Path is not a file: {image_path}")
            logger.error(f"Not a file: {image_path}")
            return violations

        try:
            # Open and analyze image
            image = Image.open(image_path)
            width, height = image.size

            logger.info(f"Image dimensions: {width}x{height}, mode: {image.mode}")

            # Check dimensions are sensible
            if width == 0 or height == 0:
                violations.append(
                    f"Invalid dimensions: {width}x{height} - "
                    f"Image has zero width or height"
                )
                logger.error("Image has zero dimensions")

            if width > 10000 or height > 10000:
                violations.append(
                    f"Excessive dimensions: {width}x{height} - "
                    f"Maximum dimension is 10000px"
                )
                logger.warning("Image dimensions exceed maximum")

            # Verify file format (PNG with transparency support)
            if image.format != 'PNG':
                violations.append(
                    f"Invalid file format: {image.format} - "
                    f"Only PNG format is supported for transparency"
                )
                logger.error(f"Invalid format: {image.format}")

            # Check for transparency support
            if image.mode not in ('RGBA', 'LA', 'PA'):
                violations.append(
                    f"No alpha channel: Image mode is {image.mode} - "
                    f"PNG assets must support transparency (RGBA mode)"
                )
                logger.warning(f"No transparency support: {image.mode}")

            # Check color distribution
            if image.mode in ('RGBA', 'RGB'):
                color_violations = self._check_color_distribution(image)
                violations.extend(color_violations)

            # Validate rotation metadata if present
            if hasattr(image, 'info') and 'rotation' in image.info:
                rotation = float(image.info['rotation'])
                if abs(rotation) > 15:
                    violations.append(
                        f"Excessive rotation in metadata: {rotation}� - "
                        f"Maximum rotation is 15�"
                    )
                    logger.warning(f"Excessive rotation: {rotation}�")

            image.close()

        except Exception as e:
            violations.append(f"Error opening/analyzing image: {str(e)}")
            logger.exception(f"Failed to analyze image: {image_path}")

        if violations:
            logger.error(
                f"Image validation failed with {len(violations)} violations"
            )
        else:
            logger.info("Image validation passed")

        return violations

    def _check_color_distribution(self, image: Image.Image) -> List[str]:
        """Check if color usage ratios are within limits.

        Args:
            image (Image.Image): PIL Image object to analyze

        Returns:
            List[str]: List of color distribution violations
        """
        violations: List[str] = []

        try:
            # Convert to RGB for analysis
            if image.mode == 'RGBA':
                # Create white background
                bg = Image.new('RGB', image.size, (255, 255, 255))
                bg.paste(image, mask=image.split()[3])  # Use alpha as mask
                rgb_image = bg
            else:
                rgb_image = image.convert('RGB')

            # Get pixel data
            pixels = np.array(rgb_image)
            total_pixels = pixels.shape[0] * pixels.shape[1]

            # Define color ranges (with tolerance)
            # Nickelodeon Orange: #F57D0D (245, 125, 13)
            nickelodeon_color = np.array([245, 125, 13])
            tolerance = 30

            # Count pixels within tolerance of Nickelodeon orange
            orange_mask = np.all(
                np.abs(pixels - nickelodeon_color) < tolerance, axis=2
            )
            orange_count = np.sum(orange_mask)
            orange_ratio = orange_count / total_pixels

            if orange_ratio > self.color_limits['nickelodeon_orange']:
                violations.append(
                    f"Excessive Nickelodeon Orange usage: {orange_ratio:.2%} - "
                    f"Maximum allowed is {self.color_limits['nickelodeon_orange']:.0%} "
                    f"(70/20/10 rule)"
                )
                logger.warning(f"Orange usage: {orange_ratio:.2%}")

            # Goosebumps Acid Green: #95C120 (149, 193, 32)
            goosebumps_color = np.array([149, 193, 32])

            # Count pixels within tolerance of Goosebumps acid green
            green_mask = np.all(
                np.abs(pixels - goosebumps_color) < tolerance, axis=2
            )
            green_count = np.sum(green_mask)
            green_ratio = green_count / total_pixels

            if green_ratio > self.color_limits['goosebumps_acid']:
                violations.append(
                    f"Excessive Goosebumps Acid Green usage: {green_ratio:.2%} - "
                    f"Maximum allowed is {self.color_limits['goosebumps_acid']:.0%} "
                    f"(70/20/10 rule)"
                )
                logger.warning(f"Acid green usage: {green_ratio:.2%}")

            logger.info(
                f"Color distribution - Orange: {orange_ratio:.2%}, "
                f"Acid Green: {green_ratio:.2%}"
            )

        except Exception as e:
            violations.append(f"Error analyzing color distribution: {str(e)}")
            logger.exception("Color distribution analysis failed")

        return violations

    def validate_layout_config(self, yaml_path: str) -> List[str]:
        """Validate a YAML layout configuration meets all specifications.

        Checks:
        - YAML file is valid and parseable
        - No spine intrusion (elements in dead zone 1469-1931)
        - Rotation limits (text d5�, containers d15�, photos d10�)
        - Safe zones for left/right pages
        - Color usage ratios (if color data present)

        Args:
            yaml_path (str): Path to the YAML layout configuration file

        Returns:
            List[str]: List of violation messages. Empty list if validation passes.

        Example:
            >>> validator = AssetValidator()
            >>> violations = validator.validate_layout_config(
            ...     "config/layouts/spread_04_05.yaml"
            ... )
            >>> if not violations:
            ...     print("Layout is valid for production")
        """
        logger.info(f"Validating layout config: {yaml_path}")
        violations: List[str] = []
        path = Path(yaml_path)

        # Check file existence
        if not path.exists():
            violations.append(f"Layout file does not exist: {yaml_path}")
            logger.error(f"File not found: {yaml_path}")
            return violations

        try:
            # Parse YAML layout file
            with open(yaml_path, 'r') as f:
                layout = yaml.safe_load(f)

            if not layout:
                violations.append("Empty or invalid YAML file")
                logger.error("YAML file is empty")
                return violations

            logger.info("YAML file parsed successfully")

            # Validate both left and right pages
            for page_key in ['left_page', 'right_page']:
                if page_key not in layout:
                    logger.warning(f"No {page_key} defined in layout")
                    continue

                page_data = layout[page_key]
                elements = page_data.get('elements', [])

                logger.info(
                    f"Validating {len(elements)} elements in {page_key}"
                )

                for element in elements:
                    element_id = element.get('id', 'unknown')
                    element_type = element.get('type', 'unknown')
                    position = element.get('position', [0, 0])
                    dimensions = element.get('dimensions', [0, 0])
                    rotation = element.get('rotation', 0)

                    # Check spine intrusion
                    spine_violations = self._check_spine_intrusion(
                        element_id, position, dimensions
                    )
                    violations.extend(spine_violations)

                    # Check rotation limits
                    rotation_violations = self._check_rotation_limits(
                        element_id, element_type, rotation
                    )
                    violations.extend(rotation_violations)

                    # Check safe zones
                    safe_zone_violations = self._check_safe_zones(
                        element_id, page_key, position, dimensions
                    )
                    violations.extend(safe_zone_violations)

        except yaml.YAMLError as e:
            violations.append(f"YAML parsing error: {str(e)}")
            logger.exception(f"Failed to parse YAML: {yaml_path}")
        except Exception as e:
            violations.append(f"Error validating layout: {str(e)}")
            logger.exception(f"Layout validation failed: {yaml_path}")

        if violations:
            logger.error(
                f"Layout validation failed with {len(violations)} violations"
            )
        else:
            logger.info("Layout validation passed")

        return violations

    def _check_spine_intrusion(
        self,
        element_id: str,
        position: List[int],
        dimensions: List[int]
    ) -> List[str]:
        """Check if an element intrudes into the spine dead zone.

        Args:
            element_id (str): Unique identifier for the element
            position (List[int]): [x, y] position of element
            dimensions (List[int]): [width, height] of element

        Returns:
            List[str]: List of spine intrusion violations
        """
        violations: List[str] = []

        if len(position) < 2 or len(dimensions) < 2:
            return violations

        x, y = position[0], position[1]
        width, height = dimensions[0], dimensions[1]

        element_left = x
        element_right = x + width

        # Check if element overlaps with spine dead zone
        if element_left < self.spine_end and element_right > self.spine_start:
            violations.append(
                f"Spine intrusion detected for element '{element_id}' - "
                f"Element at x={element_left}-{element_right} overlaps "
                f"dead zone {self.spine_start}-{self.spine_end}"
            )
            logger.warning(f"Spine intrusion: {element_id}")

        return violations

    def _check_rotation_limits(
        self,
        element_id: str,
        element_type: str,
        rotation: float
    ) -> List[str]:
        """Check if element rotation is within allowed limits.

        Args:
            element_id (str): Unique identifier for the element
            element_type (str): Type of element (text, container, photo, etc.)
            rotation (float): Rotation in degrees

        Returns:
            List[str]: List of rotation limit violations
        """
        violations: List[str] = []

        # Determine rotation limit based on element type
        max_rotation = None

        # Check for specific type matches
        if element_type in self.rotation_limits:
            max_rotation = self.rotation_limits[element_type]
        # Check for category matches
        elif 'text' in element_type.lower():
            max_rotation = self.rotation_limits['text']
        elif 'container' in element_type.lower():
            max_rotation = self.rotation_limits['containers']
        elif 'photo' in element_type.lower() or 'graphic' in element_type.lower():
            max_rotation = self.rotation_limits['photos']

        # Validate rotation if limit exists
        if max_rotation is not None and abs(rotation) > max_rotation:
            violations.append(
                f"Excessive rotation for element '{element_id}' - "
                f"{rotation}� exceeds {max_rotation}� limit for {element_type}"
            )
            logger.warning(
                f"Rotation violation: {element_id} ({rotation}� > {max_rotation}�)"
            )

        return violations

    def _check_safe_zones(
        self,
        element_id: str,
        page_key: str,
        position: List[int],
        dimensions: List[int]
    ) -> List[str]:
        """Check if element respects safe zone margins.

        Args:
            element_id (str): Unique identifier for the element
            page_key (str): 'left_page' or 'right_page'
            position (List[int]): [x, y] position of element
            dimensions (List[int]): [width, height] of element

        Returns:
            List[str]: List of safe zone violations
        """
        violations: List[str] = []

        if len(position) < 2 or len(dimensions) < 2:
            return violations

        x, y = position[0], position[1]
        width, height = dimensions[0], dimensions[1]

        # Check top margin
        if y < self.safe_zone_top:
            violations.append(
                f"Safe zone violation for element '{element_id}' - "
                f"Too close to top edge (y={y}, minimum={self.safe_zone_top})"
            )
            logger.warning(f"Top safe zone violation: {element_id}")

        # Check bottom margin
        if y + height > self.canvas_height - self.safe_zone_bottom:
            violations.append(
                f"Safe zone violation for element '{element_id}' - "
                f"Too close to bottom edge (y+h={y+height}, "
                f"maximum={self.canvas_height - self.safe_zone_bottom})"
            )
            logger.warning(f"Bottom safe zone violation: {element_id}")

        # Check left/right margins based on page
        if page_key == 'left_page':
            # Left page: check left margin
            if x < self.safe_zone_left:
                violations.append(
                    f"Safe zone violation for element '{element_id}' - "
                    f"Too close to left edge (x={x}, minimum={self.safe_zone_left})"
                )
                logger.warning(f"Left safe zone violation: {element_id}")
        elif page_key == 'right_page':
            # Right page: check right margin
            if x + width > self.canvas_width - self.safe_zone_right:
                violations.append(
                    f"Safe zone violation for element '{element_id}' - "
                    f"Too close to right edge (x+w={x+width}, "
                    f"maximum={self.canvas_width - self.safe_zone_right})"
                )
                logger.warning(f"Right safe zone violation: {element_id}")

        return violations


def main() -> int:
    """Main CLI entry point for asset validation.

    Parses command line arguments and runs appropriate validation.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description='Validate assets for 1996 Klutz Press authenticity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a visual prompt file
  python asset_validator.py --prompt prompts/components/mouse_photo.txt

  # Validate a generated image asset
  python asset_validator.py --image assets/generated/photo_mouse_01.png

  # Validate a layout configuration
  python asset_validator.py --layout config/layouts/spread_04_05.yaml

  # Use verbose logging
  python asset_validator.py --image photo.png --verbose

  # Use custom config file
  python asset_validator.py --layout spread.yaml --config my_config.yaml
        """
    )

    # Create mutually exclusive group for validation type
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--prompt',
        type=str,
        help='Validate a prompt file for anachronistic terms'
    )
    group.add_argument(
        '--image',
        type=str,
        help='Validate an image asset (dimensions, format, colors)'
    )
    group.add_argument(
        '--layout',
        type=str,
        help='Validate a YAML layout configuration'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )

    parser.add_argument(
        '--config',
        default='config/master_config.yaml',
        help='Path to master config file (default: config/master_config.yaml)'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Initialize validator with config path
    validator = AssetValidator(config_path=args.config)
    violations: List[str] = []

    # Run appropriate validation
    try:
        if args.prompt:
            logger.info(f"Validating prompt file: {args.prompt}")
            prompt_path = Path(args.prompt)
            if not prompt_path.exists():
                logger.error(f"Prompt file not found: {args.prompt}")
                print(f"ERROR: Prompt file not found: {args.prompt}")
                return 1

            with open(prompt_path, 'r') as f:
                prompt_text = f.read()

            violations = validator.validate_visual_prompt(prompt_text)

        elif args.image:
            logger.info(f"Validating image asset: {args.image}")
            violations = validator.validate_image_asset(args.image)

        elif args.layout:
            logger.info(f"Validating layout config: {args.layout}")
            violations = validator.validate_layout_config(args.layout)

    except Exception as e:
        logger.exception("Unexpected error during validation")
        print(f"ERROR: Validation failed with exception: {str(e)}")
        return 1

    # Report results
    print("\n" + "=" * 70)
    if violations:
        print("VALIDATION FAILED")
        print("=" * 70)
        print(f"\nFound {len(violations)} violation(s):\n")
        for i, violation in enumerate(violations, 1):
            print(f"{i}. {violation}")
        print("\n" + "=" * 70)
        logger.error(f"Validation failed with {len(violations)} violations")
        return 1
    else:
        print("VALIDATION PASSED")
        print("=" * 70)
        print("\nAll checks passed! Asset meets 1996 authenticity standards.")
        print("=" * 70)
        logger.info("Validation passed successfully")
        return 0


if __name__ == '__main__':
    sys.exit(main())
