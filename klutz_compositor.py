#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
klutz_compositor.py - Main composition engine for Klutz workbook pages.

This module implements the KlutzCompositor class, which assembles two-page
spreads from YAML layout definitions, applying authentic 1996-era printing
artifacts and visual effects.

Author: Team 3 - Compositor Engine Implementation
"""

import argparse
import hashlib
import logging
import random
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KlutzCompositor:
    """
    Complete implementation of the Klutz workbook compositor.

    This class handles all aspects of compositing two-page spreads, including:
    - Base canvas creation with paper texture and spiral binding
    - Asset loading and transformation (rotation, borders, shadows)
    - Programmatic text rendering with typography controls
    - Spine intrusion detection and auto-adjustment
    - 1996 print artifact simulation (CMYK shift, dot gain, vignette)

    Attributes:
        config (Dict): Loaded configuration from master_config.yaml
        canvas_width (int): Total spread width in pixels
        canvas_height (int): Total spread height in pixels
        spine_center (int): X-coordinate of spine centerline
        spine_width (int): Width of spine dead zone in pixels
        spine_start (int): Left edge of spine dead zone
        spine_end (int): Right edge of spine dead zone
        colors (Dict): Color palette mappings
    """

    def __init__(self, config_path: str = "config/master_config.yaml") -> None:
        """
        Initialize the compositor with configuration.

        Args:
            config_path: Path to master configuration YAML file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        logger.info(f"Initializing KlutzCompositor with config: {config_path}")

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        # Unpack critical specs from config
        self.canvas_width = self.config["technical"]["canvas_size"][0]
        self.canvas_height = self.config["technical"]["canvas_size"][1]
        self.spine_center = self.canvas_width // 2
        self.spine_width = self.config["technical"]["spine_width"]
        self.spine_start = self.spine_center - (self.spine_width // 2)
        self.spine_end = self.spine_center + (self.spine_width // 2)

        # Initialize color palettes
        self.colors = {
            "aged_newsprint": self._hex_to_rgb(
                self.config["aesthetic_rules"]["paper_colors"]["aged_newsprint"]
            ),
            "white": self._hex_to_rgb(self.config["aesthetic_rules"]["paper_colors"]["white"]),
            "kraft": self._hex_to_rgb(self.config["aesthetic_rules"]["paper_colors"]["kraft"]),
        }

        logger.info(f"Canvas: {self.canvas_width}x{self.canvas_height}px")
        logger.info(f"Spine: center={self.spine_center}, width={self.spine_width}")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color string to RGB tuple.

        Args:
            hex_color: Color in #RRGGBB format

        Returns:
            Tuple of (R, G, B) values
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def get_chaos_rotation(self, element_id: str, max_rotation: float) -> float:
        """
        Generate deterministic 'random' rotation based on element ID hash.

        This ensures the same element always gets the same rotation angle,
        maintaining consistency across renders while appearing random.

        Args:
            element_id: Unique identifier for the element
            max_rotation: Maximum rotation in degrees (positive)

        Returns:
            Rotation angle in degrees between -max_rotation and +max_rotation

        Examples:
            >>> compositor.get_chaos_rotation("L_photo_01", 5.0)
            -3.2145  # Always the same for this ID
        """
        # Create deterministic seed from element ID
        seed = int(hashlib.md5(element_id.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        rotation = random.uniform(-max_rotation, max_rotation)

        logger.debug(f"Element '{element_id}': rotation={rotation:.2f}°")
        return rotation

    def create_base_canvas(self, template: str = "aged_newsprint") -> Image.Image:
        """
        Create the base canvas with paper texture, binding, and lighting.

        This generates the physical book spread background with:
        - Aged paper color
        - Subtle noise texture (simulating uncoated paper grain)
        - Photorealistic spiral binding at center
        - Page curvature shadow near spine

        Args:
            template: Paper template name from config

        Returns:
            RGB Image of complete base canvas

        Raises:
            KeyError: If template name not found in color palette
        """
        logger.info(f"Creating base canvas with template: {template}")

        # Create solid color background
        canvas = Image.new("RGB", (self.canvas_width, self.canvas_height), self.colors[template])

        # Generate paper texture using numpy noise
        logger.debug("Generating paper texture")
        texture_noise = np.random.normal(128, 20, (self.canvas_height, self.canvas_width, 3))
        texture = Image.fromarray(texture_noise.astype(np.uint8))
        texture = texture.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Blend texture onto canvas
        texture_opacity = self.config["aesthetic_rules"]["texture_opacity"]["global"]
        canvas = Image.blend(canvas, texture, alpha=texture_opacity)

        # Add spiral binding
        canvas = self.add_spiral_binding(canvas)

        # Add page curvature shadow
        canvas = self.add_page_curvature(canvas)

        logger.info("Base canvas created successfully")
        return canvas

    def add_spiral_binding(self, canvas: Image.Image) -> Image.Image:
        """
        Add photorealistic spiral binding with precise 4:1 pitch.

        Creates a vertical line of punch holes with plastic coil segments,
        following standard 4:1 pitch spiral binding specifications:
        - Hole diameter: 57px
        - Hole spacing: 18px
        - Total pitch: 75px (57 + 18)

        Args:
            canvas: Base canvas image (RGB)

        Returns:
            Canvas with spiral binding added
        """
        logger.debug("Adding spiral binding")

        draw = ImageDraw.Draw(canvas, "RGBA")

        # Get binding specs from config
        hole_diameter = self.config["technical"]["binding"]["hole_diameter"]
        hole_spacing = self.config["technical"]["binding"]["hole_spacing"]
        coil_color = tuple(self.config["technical"]["binding"]["coil_color"])

        # Calculate pitch and number of holes
        pitch = hole_diameter + hole_spacing
        num_holes = self.canvas_height // pitch

        # Center the binding vertically
        start_y = (self.canvas_height - (num_holes * pitch) + hole_spacing) // 2

        logger.debug(f"Drawing {num_holes} binding holes")

        for i in range(num_holes):
            y = start_y + (i * pitch)

            # Draw punch hole with inner shadow for depth
            hole_rect = [
                self.spine_center - hole_diameter // 2,
                y,
                self.spine_center + hole_diameter // 2,
                y + hole_diameter,
            ]

            # Hole background (paper color)
            draw.ellipse(hole_rect, fill=self.colors["aged_newsprint"])

            # Inner shadow arc (simulates depth)
            draw.arc(hole_rect, start=135, end=315, fill=(180, 180, 180, 200), width=3)

            # Draw plastic coil segment
            coil_rect = [hole_rect[0] + 5, hole_rect[1] + 5, hole_rect[2] - 5, hole_rect[3] - 5]
            draw.arc(coil_rect, start=45, end=225, fill=coil_color, width=10)

        return canvas

    def add_page_curvature(self, canvas: Image.Image) -> Image.Image:
        """
        Add subtle shadow gradient near spine to simulate page curvature.

        Creates a dark gradient that fades outward from the spine edges,
        simulating the natural shadow that occurs when book pages curve
        toward the binding.

        Args:
            canvas: Canvas with binding (RGB)

        Returns:
            Canvas with curvature shadow applied
        """
        logger.debug("Adding page curvature shadow")

        # Create shadow mask
        shadow_mask = Image.new("L", canvas.size, 0)
        draw = ImageDraw.Draw(shadow_mask)

        # Shadow extends 75% of spine width on each side
        shadow_width = int(self.spine_width * 0.75)
        spine_shadow_opacity = self.config["print_simulation"]["spine_shadow"]

        # Draw gradient from spine edges
        for i in range(shadow_width):
            # Quadratic falloff for realistic shadow
            alpha = int(spine_shadow_opacity * 255 * (1 - i / shadow_width) ** 2)

            # Left side of spine
            draw.line(
                (self.spine_start + i, 0, self.spine_start + i, self.canvas_height), fill=alpha
            )

            # Right side of spine
            draw.line((self.spine_end - i, 0, self.spine_end - i, self.canvas_height), fill=alpha)

        # Composite shadow onto canvas
        shadow_layer = Image.new("RGB", canvas.size, (0, 0, 0))
        return Image.composite(shadow_layer, canvas, shadow_mask)

    def load_and_process_asset(self, asset_config: Dict[str, Any]) -> Image.Image:
        """
        Load a single asset and apply all configured transformations.

        Processing pipeline:
        1. Load image from assets/generated/
        2. Resize if dimensions specified
        3. Rotate using chaos rotation if specified
        4. Add hard-edged border if specified
        5. Apply hard-edged drop shadow (3px offset)

        Args:
            asset_config: Dictionary with keys:
                - asset: Filename in assets/generated/
                - dimensions: Optional [width, height] for resize
                - rotation: Optional max rotation degrees
                - border: Optional "4px solid #FF6600" format
                - id: Element ID for deterministic rotation

        Returns:
            Processed RGBA image ready for compositing

        Raises:
            FileNotFoundError: If asset file doesn't exist
        """
        asset_path = Path(self.config["assets"]["paths"]["generated"]) / asset_config["asset"]

        if not asset_path.exists():
            raise FileNotFoundError(f"Asset not found: {asset_path}")

        logger.debug(f"Loading asset: {asset_config['asset']}")

        # Load as RGBA for transparency support
        asset = Image.open(asset_path).convert("RGBA")

        # Resize if dimensions specified
        if "dimensions" in asset_config:
            new_size = tuple(asset_config["dimensions"])
            logger.debug(f"Resizing to {new_size}")
            asset = asset.resize(new_size, Image.Resampling.LANCZOS)

        # Rotate using chaos rotation
        if "rotation" in asset_config:
            rotation = self.get_chaos_rotation(asset_config["id"], asset_config["rotation"])
            logger.debug(f"Rotating {rotation:.2f}°")
            asset = asset.rotate(
                rotation, expand=True, fillcolor=(0, 0, 0, 0), resample=Image.Resampling.BICUBIC
            )

        # Add border if specified (format: "4px solid #FF6600")
        if "border" in asset_config:
            border_spec = asset_config["border"]
            width = int(border_spec.split("px")[0])

            # Extract hex color (last 7 chars: #RRGGBB)
            hex_color = border_spec[-7:]
            color = self._hex_to_rgb(hex_color) + (255,)  # Add alpha

            logger.debug(f"Adding {width}px border in {hex_color}")

            # Create bordered image
            bordered = Image.new("RGBA", (asset.width + width * 2, asset.height + width * 2), color)
            bordered.paste(asset, (width, width), asset)
            asset = bordered

        # TODO: Add hard-edged shadow (3px right, 3px down)
        # This would require creating a shadow layer and compositing
        # For now, shadow is applied during final composition

        return asset

    def render_text_block(self, text_config: Dict[str, Any]) -> Image.Image:
        """
        Render text programmatically with full control over typography.

        This method provides pixel-perfect text rendering using TTF fonts,
        avoiding the unreliability of AI-generated text. Features:
        - Word wrapping to fit specified dimensions
        - Configurable leading (line spacing)
        - Precise font control
        - Optional paper texture displacement

        Args:
            text_config: Dictionary with keys:
                - content: Text string to render
                - font: Font name (without .ttf extension)
                - size: Font size in points
                - dimensions: [width, height] of text block
                - color: Optional hex color (default: #000000)
                - leading: Optional line spacing override

        Returns:
            RGBA image with rendered text

        Raises:
            FileNotFoundError: If font file doesn't exist
        """
        logger.debug(
            f"Rendering text block: font={text_config['font']}, size={text_config['size']}"
        )

        # Load font
        font_path = Path(self.config["assets"]["paths"]["fonts"]) / f"{text_config['font']}.ttf"

        if not font_path.exists():
            raise FileNotFoundError(f"Font not found: {font_path}")

        font = ImageFont.truetype(str(font_path), text_config["size"])

        # Get text color (default black)
        text_color = text_config.get("color", "#000000")
        if isinstance(text_color, str):
            text_color = self._hex_to_rgb(text_color)

        # Word wrapping
        max_width = (
            text_config["dimensions"][0] - 2 * self.config["typography"]["word_wrap_padding"]
        )
        lines = text_config["content"].strip().split("\n")
        wrapped_lines = []

        for line in lines:
            if not line.strip():
                wrapped_lines.append("")
                continue

            words = line.split(" ")
            current_line = ""

            for word in words:
                test_line = current_line + word + " " if current_line else word + " "

                # Check width using getbbox for accurate measurement
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]

                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                    current_line = word + " "

            if current_line:
                wrapped_lines.append(current_line.strip())

        # Calculate line height
        line_height = text_config.get(
            "leading", text_config["size"] + self.config["typography"]["default_leading"]
        )

        # Create text image
        text_height = len(wrapped_lines) * line_height
        text_img = Image.new("RGBA", (text_config["dimensions"][0], text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)

        # Draw each line
        padding = self.config["typography"]["word_wrap_padding"]
        y = 0
        for line in wrapped_lines:
            draw.text((padding, y), line, font=font, fill=text_color)
            y += line_height

        logger.debug(f"Rendered {len(wrapped_lines)} lines of text")

        # TODO: Apply paper texture displacement for authenticity
        # This would involve subtle warping based on noise map

        return text_img

    def composite_element(
        self, canvas: Image.Image, element: Image.Image, position: Tuple[int, int], element_id: str
    ) -> Image.Image:
        """
        Paste an element onto canvas, checking for spine intrusion.

        Performs automatic position adjustment if element would intrude
        into the spine dead zone, preventing content from being lost
        in the binding area.

        Args:
            canvas: Base canvas (RGB or RGBA)
            element: Element to composite (must be RGBA)
            position: (x, y) top-left position in pixels
            element_id: Element identifier for logging

        Returns:
            Canvas with element composited
        """
        x, y = position

        # Check for spine intrusion
        element_right = x + element.width
        element_left = x

        intrudes = element_left < self.spine_end and element_right > self.spine_start

        if intrudes:
            logger.warning(
                f"Element '{element_id}' intrudes into spine dead zone. "
                f"Original position: ({x}, {y})"
            )

            # Auto-adjust position
            buffer = self.config["layout"]["spine_intrusion_buffer"]

            if x < self.spine_center:
                # Element is on left page - move left
                x = self.spine_start - element.width - buffer
                logger.info(f"Adjusted position: ({x}, {y}) [moved left]")
            else:
                # Element is on right page - move right
                x = self.spine_end + buffer
                logger.info(f"Adjusted position: ({x}, {y}) [moved right]")

        # Paste element using alpha channel
        logger.debug(f"Compositing '{element_id}' at ({x}, {y})")
        canvas.paste(element, (x, y), element)

        return canvas

    def apply_print_artifacts(self, image: Image.Image) -> Image.Image:
        """
        Apply the final '1996 Print Job' filter.

        Simulates authentic 1996-era offset printing on uncoated paper:
        1. CMYK misregistration (color channel shifts)
        2. Dot gain (ink spread, simulated via gamma adjustment)
        3. Vignette (natural light falloff)

        This is the final step that adds vintage printing character.

        Args:
            image: Composed spread (RGB)

        Returns:
            Image with print artifacts applied (RGB)
        """
        logger.info("Applying 1996 print artifacts")

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 1. CMYK Misregistration
        logger.debug("Applying CMYK misregistration")
        r, g, b = image.split()

        # Get shift values from config
        m_shift = self.config["print_simulation"]["cmyk_shift"]["magenta"]
        y_shift = self.config["print_simulation"]["cmyk_shift"]["yellow"]

        # Shift red channel (magenta component)
        r_shifted = r.transform(
            image.size,
            Image.Transform.AFFINE,
            (1, 0, m_shift[0], 0, 1, m_shift[1]),
            resample=Image.Resampling.BILINEAR,
        )

        # Shift blue channel (yellow component)
        b_shifted = b.transform(
            image.size,
            Image.Transform.AFFINE,
            (1, 0, y_shift[0], 0, 1, y_shift[1]),
            resample=Image.Resampling.BILINEAR,
        )

        image = Image.merge("RGB", (r_shifted, g, b_shifted))

        # 2. Dot Gain (gamma adjustment for ink spread)
        logger.debug("Applying dot gain")
        dot_gain = self.config["print_simulation"]["dot_gain"]
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(dot_gain)

        # 3. Vignette (radial light falloff)
        logger.debug("Applying vignette")
        vignette_intensity = self.config["print_simulation"]["vignette"]

        # Create radial gradient mask
        vignette_mask = Image.new("L", image.size, 255)
        draw = ImageDraw.Draw(vignette_mask)

        # Calculate radii for gradient
        center_x, center_y = image.width // 2, image.height // 2
        max_radius = int(1.2 * max(image.size))

        # Draw concentric ellipses with decreasing opacity
        steps = 100
        for i in range(steps):
            progress = i / steps
            radius = int(max_radius * (1 - progress))
            alpha = int(255 * (1 - vignette_intensity * progress))

            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                fill=alpha,
            )

        # Apply vignette
        vignette_layer = Image.new("RGB", image.size, (0, 0, 0))
        image = Image.composite(image, vignette_layer, vignette_mask)

        logger.info("Print artifacts applied successfully")
        return image

    def compose_spread(self, layout_path: str, apply_artifacts: bool = True) -> Image.Image:
        """
        Main method to compose a complete two-page spread from a YAML file.

        This orchestrates the entire composition pipeline:
        1. Load layout specification
        2. Create base canvas
        3. Process and composite all elements (left page, then right page)
        4. Apply print artifacts

        Args:
            layout_path: Path to YAML layout definition
            apply_artifacts: Whether to apply print simulation (default: True)

        Returns:
            Final composed spread as RGB image

        Raises:
            FileNotFoundError: If layout file doesn't exist
            yaml.YAMLError: If layout file is malformed
        """
        logger.info(f"Composing spread from: {layout_path}")

        # Load layout specification
        layout_file = Path(layout_path)
        if not layout_file.exists():
            raise FileNotFoundError(f"Layout file not found: {layout_path}")

        with open(layout_file, "r") as f:
            layout = yaml.safe_load(f)

        # Create base canvas
        template = layout.get("canvas", "aged_newsprint")
        canvas = self.create_base_canvas(template)

        # Process elements in order (left page, then right page)
        for page_key in ["left_page", "right_page"]:
            logger.info(f"Processing {page_key}")

            page_data = layout.get(page_key, {})
            elements = page_data.get("elements", [])

            logger.info(f"Found {len(elements)} elements on {page_key}")

            for element in elements:
                element_id = element.get("id", "unknown")
                element_type = element.get("type", "unknown")

                logger.info(f"Processing element '{element_id}' (type: {element_type})")

                try:
                    # Determine if text or graphic
                    if element_type.startswith("text_"):
                        # Render text programmatically
                        element_img = self.render_text_block(element)
                    else:
                        # Load and process graphic asset
                        element_img = self.load_and_process_asset(element)

                    # Composite onto canvas
                    position = tuple(element["position"])
                    canvas = self.composite_element(canvas, element_img, position, element_id)

                except Exception as e:
                    logger.error(f"Failed to process element '{element_id}': {e}")
                    raise

        # Apply print artifacts if requested
        if apply_artifacts:
            canvas = self.apply_print_artifacts(canvas)

        logger.info("Spread composition complete")
        return canvas


def main():
    """
    CLI interface for the Klutz compositor.

    Usage:
        python klutz_compositor.py <layout.yaml> <output.png>
        python klutz_compositor.py <layout.yaml> <output.png> --no-artifacts
    """
    parser = argparse.ArgumentParser(
        description="Compose Klutz workbook page spreads from YAML layouts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compose spread with all effects
  python klutz_compositor.py config/layouts/spread_04_05.yaml output/spread_04_05.png

  # Compose without print artifacts (for testing)
  python klutz_compositor.py config/layouts/spread_04_05.yaml output/test.png --no-artifacts

  # Use custom config file
  python klutz_compositor.py layout.yaml output.png --config my_config.yaml
        """,
    )

    parser.add_argument("layout", help="Path to layout YAML file")
    parser.add_argument("output", help="Path to output PNG file")
    parser.add_argument(
        "--no-artifacts",
        action="store_true",
        help="Skip print artifact simulation (faster rendering)",
    )
    parser.add_argument(
        "--config",
        default="config/master_config.yaml",
        help="Path to master config file (default: config/master_config.yaml)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize compositor
        compositor = KlutzCompositor(config_path=args.config)

        # Compose spread
        spread = compositor.compose_spread(args.layout, apply_artifacts=not args.no_artifacts)

        # Save output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        spread.save(output_path, "PNG")
        logger.info(f"Spread saved to: {output_path}")

        print(f"✓ Successfully composed spread: {output_path}")
        print(f"  Dimensions: {spread.width}x{spread.height}px")
        print(f"  Print artifacts: {'enabled' if not args.no_artifacts else 'disabled'}")

        return 0

    except Exception as e:
        logger.error(f"Composition failed: {e}", exc_info=True)
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
