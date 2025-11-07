#!/usr/bin/env python3
"""
post_processor.py - Post-processing effects for 1996 print aesthetic
Team 4: AI Integration & Processing
"""

import argparse
import logging
import yaml
from pathlib import Path
from typing import Dict, Tuple, Optional
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageChops, ImageDraw
from scipy import ndimage

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PostProcessor:
    """
    Apply period-authentic post-processing effects.

    Simulates 1996 print artifacts including paper texture, CMYK shifts,
    dot gain, and vignetting.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize post-processor.

        Args:
            config_path: Path to configuration YAML (optional)
        """
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded config from {config_path}")
        else:
            self.config = self._get_default_config()
            logger.info("Using default configuration")

    def _get_default_config(self) -> Dict:
        """Get default processing configuration"""
        return {
            'paper_texture': {
                'enabled': True,
                'opacity': 0.08,
                'grain_size': 1.5
            },
            'cmyk_shift': {
                'enabled': True,
                'magenta': [1, 0],
                'yellow': [0, -1]
            },
            'dot_gain': {
                'enabled': True,
                'gamma': 0.95
            },
            'vignette': {
                'enabled': True,
                'opacity': 0.15,
                'feather': 1.5
            }
        }

    def apply_paper_texture(self,
                            image: Image.Image,
                            texture_path: Optional[str] = None,
                            opacity: float = 0.08) -> Image.Image:
        """
        Apply paper texture overlay.

        Args:
            image: Input image
            texture_path: Path to texture image (optional, generates if None)
            opacity: Texture opacity (0-1)

        Returns:
            Image with paper texture applied
        """
        logger.debug("Applying paper texture")

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Load or generate texture
        if texture_path and Path(texture_path).exists():
            texture = Image.open(texture_path).convert('RGB')
            texture = texture.resize(image.size, Image.Resampling.LANCZOS)
        else:
            texture = self._generate_paper_texture(image.size)

        # Blend texture with image
        result = Image.blend(image, texture, alpha=opacity)

        logger.debug(f"Applied texture with opacity {opacity}")
        return result

    def _generate_paper_texture(self, size: Tuple[int, int]) -> Image.Image:
        """
        Generate procedural paper texture.

        Args:
            size: Image dimensions (width, height)

        Returns:
            Paper texture image
        """
        # Generate noise
        grain_size = self.config['paper_texture'].get('grain_size', 1.5)

        noise = np.random.normal(128, 20, (size[1], size[0], 3))

        # Apply slight blur for paper fiber effect
        texture_array = ndimage.gaussian_filter(noise, sigma=grain_size)

        # Ensure values are in valid range
        texture_array = np.clip(texture_array, 0, 255).astype(np.uint8)

        # Add subtle paper color (aged newsprint)
        paper_color = np.array([248, 243, 229])
        texture_array = (texture_array * 0.1 + paper_color * 0.9).astype(np.uint8)

        return Image.fromarray(texture_array, 'RGB')

    def apply_cmyk_shift(self,
                         image: Image.Image,
                         magenta_shift: Tuple[int, int] = (1, 0),
                         yellow_shift: Tuple[int, int] = (0, -1)) -> Image.Image:
        """
        Apply CMYK color misregistration.

        Args:
            image: Input image
            magenta_shift: Magenta channel offset (x, y)
            yellow_shift: Yellow channel offset (x, y)

        Returns:
            Image with CMYK shift applied
        """
        logger.debug(f"Applying CMYK shift: M{magenta_shift} Y{yellow_shift}")

        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Split into RGB channels
        r, g, b = image.split()

        # Shift magenta (red channel)
        if magenta_shift != (0, 0):
            r = ImageChops.offset(r, magenta_shift[0], magenta_shift[1])

        # Shift yellow (blue channel inverted logic)
        if yellow_shift != (0, 0):
            b = ImageChops.offset(b, yellow_shift[0], yellow_shift[1])

        # Merge back
        result = Image.merge('RGB', (r, g, b))

        logger.debug("CMYK shift applied")
        return result

    def apply_dot_gain(self,
                       image: Image.Image,
                       gamma: float = 0.95) -> Image.Image:
        """
        Apply dot gain (ink spreading on paper).

        Args:
            image: Input image
            gamma: Gamma correction value (< 1.0 darkens, simulating dot gain)

        Returns:
            Image with dot gain applied
        """
        logger.debug(f"Applying dot gain (gamma={gamma})")

        # Apply gamma correction to simulate ink spreading
        enhancer = ImageEnhance.Brightness(image)
        result = enhancer.enhance(gamma)

        logger.debug("Dot gain applied")
        return result

    def apply_vignette(self,
                       image: Image.Image,
                       opacity: float = 0.15) -> Image.Image:
        """
        Apply vignette effect (edge darkening).

        Args:
            image: Input image
            opacity: Vignette strength (0-1)

        Returns:
            Image with vignette applied
        """
        logger.debug(f"Applying vignette (opacity={opacity})")

        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Create radial gradient mask
        width, height = image.size
        center_x, center_y = width // 2, height // 2

        # Create vignette mask
        vignette_mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(vignette_mask)

        # Create radial gradient
        max_radius = int(1.5 * max(width, height))

        for i in range(256):
            # Calculate radius for this brightness level
            radius = int(max_radius * (1 - i / 255.0))

            # Calculate alpha (vignette strength)
            alpha = int(255 - opacity * i)

            # Draw ellipse
            draw.ellipse(
                [center_x - radius, center_y - radius,
                 center_x + radius, center_y + radius],
                fill=alpha
            )

        # Apply vignette
        # Create darkened version
        darkened = ImageEnhance.Brightness(image).enhance(0.7)

        # Blend using vignette mask
        result = Image.composite(darkened, image, vignette_mask)

        logger.debug("Vignette applied")
        return result

    def apply_all_artifacts(self,
                            image: Image.Image,
                            config: Optional[Dict] = None) -> Image.Image:
        """
        Apply all post-processing effects in one pass.

        Args:
            image: Input image
            config: Optional configuration override

        Returns:
            Fully processed image
        """
        cfg = config or self.config

        result = image.copy()

        # Apply effects in order
        if cfg.get('paper_texture', {}).get('enabled', True):
            opacity = cfg['paper_texture'].get('opacity', 0.08)
            result = self.apply_paper_texture(result, opacity=opacity)

        if cfg.get('cmyk_shift', {}).get('enabled', True):
            magenta = tuple(cfg['cmyk_shift'].get('magenta', [1, 0]))
            yellow = tuple(cfg['cmyk_shift'].get('yellow', [0, -1]))
            result = self.apply_cmyk_shift(result, magenta, yellow)

        if cfg.get('dot_gain', {}).get('enabled', True):
            gamma = cfg['dot_gain'].get('gamma', 0.95)
            result = self.apply_dot_gain(result, gamma)

        if cfg.get('vignette', {}).get('enabled', True):
            opacity = cfg['vignette'].get('opacity', 0.15)
            result = self.apply_vignette(result, opacity)

        logger.info("All artifacts applied")
        return result

    def batch_process(self,
                      input_dir: str,
                      output_dir: str,
                      config: Optional[Dict] = None) -> int:
        """
        Process multiple images.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            config: Optional configuration override

        Returns:
            Number of images processed
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all images
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(input_path.glob(ext))

        if not image_files:
            logger.warning(f"No images found in {input_dir}")
            return 0

        logger.info(f"Processing {len(image_files)} images")

        # Progress bar
        if TQDM_AVAILABLE:
            progress = tqdm(image_files, desc="Processing")
        else:
            progress = image_files

        processed = 0

        for image_file in progress:
            try:
                # Load image
                img = Image.open(image_file)

                # Process
                result = self.apply_all_artifacts(img, config)

                # Save
                output_file = output_path / image_file.name
                result.save(output_file)

                processed += 1
                logger.debug(f"Processed: {image_file.name}")

            except Exception as e:
                logger.error(f"Failed to process {image_file.name}: {e}")

        logger.info(f"Processed {processed}/{len(image_files)} images")
        return processed


def main():
    """CLI interface for post-processor"""
    parser = argparse.ArgumentParser(
        description='Apply 1996 print artifacts to images'
    )
    parser.add_argument(
        '--input',
        help='Input image file (for single image processing)'
    )
    parser.add_argument(
        '--input-dir',
        help='Input directory (for batch processing)'
    )
    parser.add_argument(
        '--output',
        help='Output image file (for single image)'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (for batch processing)'
    )
    parser.add_argument(
        '--config',
        help='Configuration YAML file'
    )
    parser.add_argument(
        '--no-texture',
        action='store_true',
        help='Disable paper texture'
    )
    parser.add_argument(
        '--no-cmyk',
        action='store_true',
        help='Disable CMYK shift'
    )
    parser.add_argument(
        '--no-dot-gain',
        action='store_true',
        help='Disable dot gain'
    )
    parser.add_argument(
        '--no-vignette',
        action='store_true',
        help='Disable vignette'
    )

    args = parser.parse_args()

    # Initialize processor
    processor = PostProcessor(config_path=args.config)

    # Override config based on flags
    if args.no_texture:
        processor.config['paper_texture']['enabled'] = False
    if args.no_cmyk:
        processor.config['cmyk_shift']['enabled'] = False
    if args.no_dot_gain:
        processor.config['dot_gain']['enabled'] = False
    if args.no_vignette:
        processor.config['vignette']['enabled'] = False

    # Single or batch mode
    if args.input and args.output:
        # Single image processing
        logger.info(f"Processing: {args.input}")

        try:
            img = Image.open(args.input)
            result = processor.apply_all_artifacts(img)

            # Ensure output directory exists
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)

            result.save(args.output)
            print(f" Processed: {args.output}")
            return 0

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            print(f" Error: {e}")
            return 1

    elif args.input_dir and args.output_dir:
        # Batch processing
        try:
            count = processor.batch_process(args.input_dir, args.output_dir)

            if count > 0:
                print(f" Processed {count} images to {args.output_dir}")
                return 0
            else:
                print(f" No images processed")
                return 1

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            print(f" Error: {e}")
            return 1

    else:
        parser.print_help()
        print("\nError: Must specify either:")
        print("  --input and --output for single image")
        print("  --input-dir and --output-dir for batch processing")
        return 1


if __name__ == '__main__':
    exit(main())
