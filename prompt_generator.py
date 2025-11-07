#!/usr/bin/env python3
"""
prompt_generator.py - Generates hyper-specific XML prompts for AI image generation
Team 4: AI Integration & Processing
"""

import argparse
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from string import Template
from typing import Dict, List
from xml.dom import minidom

import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generates hyper-specific XML prompts from element configurations.

    Converts YAML element configs into detailed XML prompts for nano-banana
    image generation, using template-based substitution.
    """

    # Default configuration constants
    DEFAULT_DIMENSIONS = [800, 600]
    DEFAULT_DPI = 300
    DEFAULT_COLOR_SPACE = "sRGB"
    DEFAULT_FILM_STOCK = "Kodak Gold 400"
    DEFAULT_GRAIN = "moderate"
    DEFAULT_LENS = "100mm macro"
    DEFAULT_APERTURE = "f/11"
    DEFAULT_SOFTWARE = "MacPaint"
    DEFAULT_RESOLUTION = "512x342"
    DEFAULT_COLOR_DEPTH = "monochrome"
    DEFAULT_SHAPE = "irregular blob"
    DEFAULT_BORDER_WIDTH = "4px"
    DEFAULT_BORDER_COLOR = "#000000"
    DEFAULT_FILL_COLOR = "#F57D0D"
    DEFAULT_SHADOW = "hard drop shadow, 3px right, 3px down, pure black"
    DEFAULT_GRID_SIZE = "16x16"
    DEFAULT_PALETTE = "16-color"
    DEFAULT_PIXEL_STYLE = "NES/SNES era sprite"

    def __init__(self, templates_dir: str = "config/templates"):
        """
        Initialize prompt generator with template system.

        Args:
            templates_dir: Directory containing prompt templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()

        # Load forbidden terms from validation
        self.forbidden_terms = self._load_forbidden_terms()
        # Pre-compute lowercase forbidden terms for O(1) lookup performance
        self.forbidden_terms_lower = set(term.lower() for term in self.forbidden_terms)

        logger.info(f"PromptGenerator initialized with {len(self.templates)} templates")

    def _load_templates(self) -> Dict[str, str]:
        """Load all prompt templates from templates directory."""
        templates = {}

        # Default templates embedded in code if directory doesn't exist
        default_templates = {
            "photo": self._get_photo_template(),
            "container": self._get_container_template(),
            "gui": self._get_gui_template(),
            "pixelart": self._get_pixelart_template(),
            "text": self._get_text_template(),
            "doodle": self._get_doodle_template(),
        }

        # Try to load from files if they exist
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.yaml"):
                try:
                    with open(template_file, "r") as f:
                        template_data = yaml.safe_load(f)
                        templates.update(template_data.get("templates", {}))
                    logger.info(f"Loaded template: {template_file.name}")
                except Exception as e:
                    logger.warning(f"Could not load template {template_file}: {e}")

        # Use defaults if no templates loaded
        if not templates:
            templates = default_templates
            logger.info("Using default embedded templates")

        return templates

    def _load_forbidden_terms(self) -> List[str]:
        """Load forbidden anachronistic terms."""
        return [
            "gradient",
            "web 2.0",
            "flat design",
            "material design",
            "minimalist",
            "responsive",
            "user experience",
            "UX",
            "UI",
            "wireframe",
            "mobile",
            "touch",
            "swipe",
            "drag and drop",
            "USB",
            "wireless",
            "bluetooth",
            "LED",
            "LCD",
            "plasma",
            "broadband",
            "wifi",
            "streaming",
            "social media",
            "tweet",
            "post",
            "share",
            "like",
            "hashtag",
            "smartphone",
            "tablet",
            "app",
            "notification",
            "cloud",
            "sync",
            "HD",
            "4K",
            "1080p",
            "widescreen",
            "16:9",
            "retina",
            "SSD",
            "flash drive",
            "emoji",
            "gif",
            "meme",
            "Google",
            "Facebook",
            "Twitter",
            "Instagram",
            "Pinterest",
            "Windows 95",
            "Windows 98",
            "Windows XP",
            "opacity slider",
            "layer mask",
            "SVG",
            "photoshop",
        ]

    def generate_element_prompt(self, element_config: Dict) -> str:
        """
        Generate XML prompt from element configuration.

        Args:
            element_config: Dictionary containing element specifications

        Returns:
            XML prompt string

        Raises:
            ValueError: If prompt contains forbidden terms
        """
        element_type = element_config.get("type", "photo")

        # Map element type to template category
        template_key = self._get_template_key(element_type)

        if template_key not in self.templates:
            logger.warning(f"No template for {template_key}, using photo template")
            template_key = "photo"

        # Build XML structure
        root = ET.Element("nano_banana_prompt")

        # Element identification
        elem_id = ET.SubElement(root, "element_id")
        elem_id.text = element_config.get("id", "unknown")

        # Image specifications
        self._add_image_specs(root, element_config)

        # Type-specific parameters
        if template_key == "photo":
            self._add_photo_parameters(root, element_config)
        elif template_key == "gui":
            self._add_gui_parameters(root, element_config)
        elif template_key == "pixelart":
            self._add_pixelart_parameters(root, element_config)
        elif template_key == "container":
            self._add_container_parameters(root, element_config)

        # Generate prompts using templates
        positive_prompt, negative_prompt = self._generate_prompts_from_template(
            template_key, element_config
        )

        # Add prompts to XML
        pos_elem = ET.SubElement(root, "positive_prompt")
        pos_elem.text = positive_prompt

        neg_elem = ET.SubElement(root, "negative_prompt")
        neg_elem.text = negative_prompt

        # Convert to pretty XML string
        xml_string = self._prettify_xml(root)

        # Validate prompt
        self._validate_prompt(xml_string)

        logger.info(f"Generated prompt for {element_config.get('id', 'unknown')}")

        return xml_string

    def _get_template_key(self, element_type: str) -> str:
        """Map element type to template key."""
        type_mapping = {
            "graphic_photo_instructional": "photo",
            "graphic_gui_recreation": "gui",
            "graphic_pixelart": "pixelart",
            "container_featurebox": "container",
            "container_splat": "container",
            "text_headline": "text",
            "doodle": "doodle",
        }
        return type_mapping.get(element_type, "photo")

    def _add_image_specs(self, root: ET.Element, config: Dict):
        """Add image specifications to XML."""
        specs = ET.SubElement(root, "image_specifications")

        dims = ET.SubElement(specs, "dimensions")
        width, height = config.get("dimensions", self.DEFAULT_DIMENSIONS)
        dims.set("width", str(width))
        dims.set("height", str(height))
        dims.set("dpi", str(config.get("dpi", self.DEFAULT_DPI)))

        color_space = ET.SubElement(specs, "color_space")
        color_space.text = config.get("color_space", self.DEFAULT_COLOR_SPACE)

    def _add_photo_parameters(self, root: ET.Element, config: Dict):
        """Add photographic parameters to XML."""
        params = ET.SubElement(root, "photographic_parameters")

        # Film stock
        film = ET.SubElement(params, "film_stock")
        film.text = config.get("film_stock", self.DEFAULT_FILM_STOCK)

        # Grain
        grain = ET.SubElement(params, "grain_intensity")
        grain.text = config.get("grain", self.DEFAULT_GRAIN)

        # Color characteristics
        color_char = ET.SubElement(params, "color_characteristics")
        highlights = ET.SubElement(color_char, "highlights")
        highlights.text = "warm_bias"
        shadows = ET.SubElement(color_char, "shadows")
        shadows.text = "cyan_shift"

        # Lens and aperture
        lens = ET.SubElement(params, "lens")
        lens.text = config.get("lens", self.DEFAULT_LENS)

        aperture = ET.SubElement(params, "aperture")
        aperture.text = config.get("aperture", self.DEFAULT_APERTURE)

        # Lighting setup
        self._add_lighting_setup(params, config)

    def _add_lighting_setup(self, parent: ET.Element, config: Dict):
        """Add lighting setup parameters."""
        lighting = ET.SubElement(parent, "lighting_setup")

        # Key light
        key_light = ET.SubElement(lighting, "key_light")
        key_type = ET.SubElement(key_light, "type")
        key_type.text = "24x36 inch softbox"
        key_pos = ET.SubElement(key_light, "position")
        key_pos.text = "45 degrees camera left"
        key_elev = ET.SubElement(key_light, "elevation")
        key_elev.text = "30 degrees above subject"
        key_power = ET.SubElement(key_light, "power")
        key_power.text = "full"

        # Fill light
        fill_light = ET.SubElement(lighting, "fill_light")
        fill_type = ET.SubElement(fill_light, "type")
        fill_type.text = "white foam core reflector"
        fill_pos = ET.SubElement(fill_light, "position")
        fill_pos.text = "60 degrees camera right"
        fill_ratio = ET.SubElement(fill_light, "ratio")
        fill_ratio.text = "1:2 relative to key"

    def _add_gui_parameters(self, root: ET.Element, config: Dict):
        """Add GUI recreation parameters."""
        params = ET.SubElement(root, "gui_parameters")

        # Software being recreated
        software = ET.SubElement(params, "software")
        software.text = config.get("software", self.DEFAULT_SOFTWARE)

        # Display specs
        display = ET.SubElement(params, "display_specifications")
        resolution = ET.SubElement(display, "resolution")
        resolution.text = config.get("resolution", self.DEFAULT_RESOLUTION)
        color_depth = ET.SubElement(display, "color_depth")
        color_depth.text = config.get("color_depth", self.DEFAULT_COLOR_DEPTH)

        # Interface style
        style = ET.SubElement(params, "interface_style")
        style.text = "1996 Macintosh System 6"

    def _add_pixelart_parameters(self, root: ET.Element, config: Dict):
        """Add pixel art parameters."""
        params = ET.SubElement(root, "pixelart_parameters")

        # Grid size
        grid = ET.SubElement(params, "grid_size")
        grid.text = config.get("grid_size", self.DEFAULT_GRID_SIZE)

        # Color palette
        palette = ET.SubElement(params, "color_palette")
        palette.text = config.get("palette", self.DEFAULT_PALETTE)

        # Scaling
        scaling = ET.SubElement(params, "scaling_method")
        scaling.text = "nearest-neighbor"

        # Style
        style = ET.SubElement(params, "pixel_style")
        style.text = config.get("style", self.DEFAULT_PIXEL_STYLE)

    def _add_container_parameters(self, root: ET.Element, config: Dict):
        """Add container/shape parameters."""
        params = ET.SubElement(root, "container_parameters")

        # Shape
        shape = ET.SubElement(params, "shape")
        shape.text = config.get("shape", self.DEFAULT_SHAPE)

        # Border
        border = ET.SubElement(params, "border")
        border_width = ET.SubElement(border, "width")
        border_width.text = str(config.get("border_width", self.DEFAULT_BORDER_WIDTH))
        border_color = ET.SubElement(border, "color")
        border_color.text = config.get("border_color", self.DEFAULT_BORDER_COLOR)

        # Fill
        fill = ET.SubElement(params, "fill")
        fill.text = config.get("fill_color", self.DEFAULT_FILL_COLOR)

        # Shadow
        shadow = ET.SubElement(params, "shadow")
        shadow.text = self.DEFAULT_SHADOW

    def _generate_prompts_from_template(self, template_key: str, config: Dict) -> tuple:
        """
        Generate positive and negative prompts from templates.

        Args:
            template_key: Template category to use
            config: Element configuration

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        template = self.templates.get(template_key, self.templates["photo"])

        # Prepare substitution variables
        dims = config.get("dimensions", [800, 600])
        variables = {
            "TAG_ID": config.get("id", "element"),
            "DIMENSIONS": f"{dims[0]}x{dims[1]}",
            "WIDTH": str(config.get("dimensions", [800, 600])[0]),
            "HEIGHT": str(config.get("dimensions", [800, 600])[1]),
            "COLOR": config.get("color", "#FF6600"),
            "SUBJECT": config.get("subject", "computer hardware"),
            "SOFTWARE": config.get("software", "MacPaint"),
            "STYLE": config.get("style", "Klutz Press 1996"),
            "BORDER_COLOR": config.get("border_color", "#000000"),
            "FILL_COLOR": config.get("fill_color", "#F57D0D"),
            "FONT": config.get("font", "Chicago"),
            "TEXT_CONTENT": config.get("content", ""),
        }

        # Extract positive and negative from template
        if isinstance(template, dict):
            positive_template = template.get("positive", "")
            negative_template = template.get("negative", "")
        else:
            # Template is a string - split on separator
            parts = template.split("|||")
            positive_template = parts[0] if len(parts) > 0 else template
            negative_template = parts[1] if len(parts) > 1 else self._get_default_negative()

        # Perform substitution
        positive_prompt = Template(positive_template).safe_substitute(variables)
        negative_prompt = Template(negative_template).safe_substitute(variables)

        return positive_prompt.strip(), negative_prompt.strip()

    def _get_default_negative(self) -> str:
        """Get default negative prompt."""
        return """modern optical mouse, wireless mouse, gaming mouse, RGB lighting,
        adult hands, dramatic lighting, shallow depth of field, bokeh,
        digital photography, clean grain-free image, HDR, post-processing effects,
        color grading, Instagram filters, black and white, monochrome,
        low key lighting, dark mood, modern technology, touchpad, trackball,
        Windows mouse, two-button mouse, scroll wheel, gradients, soft shadows,
        antialiasing, blur, smooth edges"""

    def _validate_prompt(self, xml_string: str):
        """
        Validate prompt doesn't contain forbidden terms.

        Args:
            xml_string: XML prompt to validate

        Raises:
            ValueError: If forbidden terms found
        """
        xml_lower = xml_string.lower()

        # Check for forbidden terms using pre-computed lowercase set for O(1) lookups
        found_terms = []
        for term_lower in self.forbidden_terms_lower:
            if term_lower in xml_lower:
                # Find original term for error message
                found_terms.append(next(t for t in self.forbidden_terms if t.lower() == term_lower))

        if found_terms:
            error_msg = f"Prompt contains forbidden anachronistic terms: {', '.join(found_terms)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug("Prompt validation passed")

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Convert XML element to pretty-printed string."""
        rough_string = ET.tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    # Template definitions
    def _get_photo_template(self) -> Dict:
        """Get photo template."""
        return {
            "positive": """Professional instructional photograph circa 1996, ${SUBJECT},
            shot on Kodak Gold 400 35mm film, moderate grain visible, slight warm color cast,
            clean composition, high-angle view, sharp focus throughout, even lighting from softbox
            creating soft shadows, educational photography style, bright and cheerful mood,
            period-accurate hardware visible""",
            "negative": """modern optical mouse, wireless mouse, gaming mouse, RGB lighting,
            dramatic lighting, shallow depth of field, bokeh, digital photography,
            clean grain-free image, HDR, post-processing effects, color grading,
            Instagram filters, low key lighting, dark mood, modern technology,
            smartphone, tablet, LCD screen, LED lighting""",
        }

    def _get_container_template(self) -> Dict:
        """Get container/shape template."""
        return {
            "positive": """1996 Klutz Press style irregular shape container,
            hand-drawn appearance, hard black outline ${BORDER_COLOR} exactly 4 pixels wide,
            solid fill color ${FILL_COLOR}, hard drop shadow 3 pixels right and 3 pixels down
            pure black, no gradients, no soft edges, no antialiasing, bold primary colors,
            energetic Nickelodeon-style shape, clean sharp edges""",
            "negative": """gradient fills, soft shadows, drop shadow blur,
            antialiasing, smooth edges, rounded corners with feathering,
            opacity variations, layer effects, modern flat design,
            material design, web 2.0 aesthetics, subtle shading,
            three-dimensional effects, emboss, bevel""",
        }

    def _get_gui_template(self) -> Dict:
        """Get GUI recreation template."""
        return {
            "positive": """Exact pixel-perfect recreation of 1996 ${SOFTWARE} interface,
            Macintosh System 6 style, monochrome black and white display,
            512x342 resolution, hard-edged pixels, no antialiasing,
            classic Mac OS menu bar, tool palette with grid layout,
            bitmapped Chicago font for labels, crisp pixel boundaries,
            authentic period software interface""",
            "negative": """modern software interface, color GUI, Windows interface,
            antialiased text, smooth fonts, TrueType rendering, gradient buttons,
            drop shadows on UI elements, transparency effects, modern icons,
            flat design, material design, iOS interface, rounded UI elements,
            touch interface elements, mobile UI patterns""",
        }

    def _get_pixelart_template(self) -> Dict:
        """Get pixel art template."""
        return {
            "positive": """Pixel art sprite, NES/SNES era style, 16x16 grid,
            16-color palette maximum, hard pixel edges, nearest-neighbor scaling,
            no antialiasing, no sub-pixel rendering, clean pixel boundaries,
            classic video game sprite aesthetic, bold readable shapes,
            high contrast between colors, Nintendo-style character design""",
            "negative": """antialiased edges, smooth gradients, soft shadows,
            blurred pixels, sub-pixel rendering, rotated pixels,
            modern high-resolution sprites, too many colors,
            smooth shading, dithering gradients, photo-realistic textures,
            3D rendered sprites, modern game graphics""",
        }

    def _get_text_template(self) -> Dict:
        """Get text element template."""
        return {
            "positive": """1996 desktop publishing typography, ${FONT} font,
            bitmapped font rendering at exact pixel sizes, no antialiasing,
            hard pixel edges on letterforms, high contrast black on white,
            clean baseline alignment, proper kerning for display text,
            bold energetic headline style""",
            "negative": """antialiased text, smooth font rendering, TrueType hinting,
            sub-pixel antialiasing, gradient text fills, drop shadow on text,
            text effects, 3D text, embossed text, outlined text with soft edges,
            modern web fonts, variable fonts""",
        }

    def _get_doodle_template(self) -> Dict:
        """Get doodle/hand-drawn template."""
        return {
            "positive": """Hand-drawn doodle illustration, thick black marker line art,
            Klutz Press style, energetic imperfect lines, cartoon style,
            simple bold shapes, high contrast, solid black lines on white,
            playful energetic style, visible pen strokes, authentic hand-drawn look,
            no computer perfection""",
            "negative": """vector graphics, perfectly smooth curves, Bezier paths,
            uniform line weight, computer-generated symmetry, gradient strokes,
            soft edges, antialiasing, digital brush effects, Photoshop brushes,
            tablet pen pressure variation, modern digital illustration""",
        }


def main():
    """CLI interface for prompt generator."""
    parser = argparse.ArgumentParser(description="Generate XML prompts from element configurations")
    parser.add_argument("--config", required=True, help="Path to element configuration YAML file")
    parser.add_argument("--output", required=True, help="Output path for XML prompt file")
    parser.add_argument(
        "--templates-dir", default="config/templates", help="Directory containing prompt templates"
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate config, do not generate prompt"
    )

    args = parser.parse_args()

    # Load element configuration
    with open(args.config, "r") as f:
        element_config = yaml.safe_load(f)

    # Initialize generator
    generator = PromptGenerator(templates_dir=args.templates_dir)

    if args.validate_only:
        logger.info(f"Validating configuration: {args.config}")
        # Validation happens during generation
        try:
            _ = generator.generate_element_prompt(element_config)
            print(f"✓ Configuration valid: {args.config}")
        except ValueError as e:
            print(f"✗ Validation failed: {e}")
            return 1
    else:
        # Generate prompt
        try:
            xml_prompt = generator.generate_element_prompt(element_config)

            # Write to file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                f.write(xml_prompt)

            logger.info(f"Prompt written to: {output_path}")
            print(f"✓ Generated prompt: {output_path}")

        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            print(f"✗ Error: {e}")
            return 1

    return 0


if __name__ == "__main__":
    exit(main())
