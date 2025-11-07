# Section 8: Gemini-2.0-Flash-Exp Integration Protocol (Complete)

python#!/usr/bin/env python3
"""
gemini_integration.py - Complete Gemini-2.0-Flash-Exp integration for XML prompt generation
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import json
import time
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from enum import Enum

class ElementType(Enum):
    """Valid element types for generation"""
    PHOTO_INSTRUCTIONAL = "graphic_photo_instructional"
    CONTAINER_FEATUREBOX = "container_featurebox"
    SPLAT_CONTAINER = "graphic_splat_container"
    PIXELART = "graphic_pixelart"
    GUI_RECREATION = "graphic_gui_recreation"
    DOODLE = "graphic_doodle"
    EMBOSSED_FEATUREBOX = "container_embossed_featurebox"
    SPIRAL_BINDING = "graphic_spiral_binding"
    TEXT_HEADLINE = "text_headline"

@dataclass
class GeminiConfig:
    """Configuration for Gemini model"""
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.2
    top_p: float = 0.8
    top_k: int = 40
    max_output_tokens: int = 8192
    requests_per_minute: int = 60
    retry_attempts: int = 3
    retry_delay: float = 2.0

class GeminiXMLGenerator:
    """Handles all Gemini API interactions for XML prompt generation"""

    def __init__(self, config: GeminiConfig):
        self.config = config
        genai.configure(api_key=config.api_key)

        # Model configuration
        self.generation_config = genai.GenerationConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            max_output_tokens=config.max_output_tokens,
        )

        self.model = genai.GenerativeModel(
            config.model_name,
            generation_config=self.generation_config
        )

        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 60.0 / config.requests_per_minute

        # Logging
        self.logger = logging.getLogger(__name__)

        # Load comprehensive system instruction
        self.system_instruction = self.load_system_instruction()

        # Element-specific templates
        self.element_templates = self.load_element_templates()

    def load_system_instruction(self) -> str:
        """Load the comprehensive system instruction for Gemini"""

        return """You are an XML prompt engineer for the nano-banana image generation model,
creating assets for a 1996 Klutz Press computer graphics workbook.

CRITICAL CONSTRAINTS:
1. Output ONLY valid XML - no markdown, no explanations, no commentary
2. Use EXCLUSIVELY quantitative specifications (pixels, degrees, hex codes)
3. Reference ONLY technology available in 1996
4. Include comprehensive negative prompts for every element
5. Never use subjective terms (nice, beautiful, modern, clean)

XML SCHEMA REQUIREMENTS:
- Root element: <nano_banana_prompt>
- Required child elements: element_id, element_type, specifications, positive_prompt, negative_prompt
- All measurements in pixels (integer values only)
- All colors in hex format (#RRGGBB)
- All angles in degrees (-180 to 180)
- All percentages as decimals (0.0 to 1.0)

FORBIDDEN TERMS (NEVER USE):
gradient, modern, sleek, minimal, UX, UI, responsive, mobile, wireless, USB,
LED, LCD, HD, 4K, anti-aliasing, transparency, blur, soft shadow, web 2.0,
rounded corners, glassmorphism, neumorphism, flat design, material design,
iOS, Android, smartphone, tablet, touchscreen, swipe, pinch, zoom

REQUIRED 1996 TECHNOLOGY TERMS:
- Computer: Macintosh Plus, System 6, 512x342 display, black and white
- Mouse: Apple Desktop Bus M0100, beige, rectangular, one button
- Storage: 3.5" floppy disk, 1.44MB capacity
- Display: CRT monitor, phosphor glow, scanlines
- Software: MacPaint, bitmap graphics, 72 DPI

ELEMENT-SPECIFIC REQUIREMENTS:

graphic_photo_instructional:
- Film: Kodak Gold 400 (grain index 39, warm highlights)
- Camera: 100mm macro lens, f/11 aperture, 1/125 shutter
- Lighting: Key light 45° left 30° up, fill reflector 60° right
- Subject: Child's hand (8-10 years), Apple M0100 mouse, beige
- Background: Solid color mousepad, no patterns

container_featurebox:
- Border: 4px solid black, perfect 90° corners
- Shadow: Hard-edged, 3px X offset, 3px Y offset, no blur, pure black
- Background: Solid color only from Klutz palette
- Rotation: Maximum ±15 degrees

graphic_pixelart:
- Base resolution: 32x32 or 16x16 pixels
- Scaling: Nearest-neighbor interpolation only
- Colors: Maximum 16 from NES/SNES palette
- Style: 8-bit console aesthetic, hard pixel edges

graphic_gui_recreation:
- Software: MacPaint 1.0 or simplified Aseprite
- Colors: Black and white only for MacPaint
- Font: Chicago bitmap font, no anti-aliasing
- UI elements: Single pixel borders, stippled patterns

graphic_doodle:
- Style: Hand-drawn with black marker
- Line weight: 3-5 pixels, slightly uneven
- Character: Confident single strokes, organic imperfections
- No perfect geometry or computer-generated appearance

container_embossed_featurebox:
- Technique: Blind embossing (no ink)
- Depth: 15-25 microns raised
- Highlights: Top-left edges of raised areas
- Shadows: Bottom-right edges, hard-edged

COLOR SPECIFICATIONS:
Klutz Primary Palette (Use 70% of time):
- Red: #FF0000
- Blue: #0000FF
- Yellow: #FFFF00
- Green: #00FF00
- Orange: #FFA500
- Purple: #800080

Accent Colors (Use sparingly):
- Nickelodeon Orange: #F57D0D (splats only, max 20%)
- Goosebumps Acid: #95C120 (monsters only, max 10%)

Generate XML now for the following element:"""

    def load_element_templates(self) -> Dict[str, str]:
        """Load element-specific XML templates"""

        templates = {}
        template_dir = Path('config/xml_templates')

        if template_dir.exists():
            for template_file in template_dir.glob('*.xml'):
                element_type = template_file.stem
                templates[element_type] = template_file.read_text()

        return templates

    def rate_limit(self):
        """Enforce rate limiting"""

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def generate_xml_prompt(self, element_config: Dict) -> Optional[str]:
        """Generate XML prompt for a single element with retry logic"""

        for attempt in range(self.config.retry_attempts):
            try:
                # Rate limiting
                self.rate_limit()

                # Build the request
                request = self.build_request(element_config)

                # Generate content
                response = self.model.generate_content(request)

                # Extract and validate XML
                xml_content = self.extract_xml(response.text)

                if self.validate_xml_structure(xml_content, element_config):
                    self.logger.info(f"Successfully generated XML for {element_config['id']}")
                    return xml_content
                else:
                    raise ValueError("Generated XML failed validation")

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {element_config['id']}: {str(e)}")

                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    self.logger.error(f"All attempts failed for {element_config['id']}")
                    return self.fallback_xml_generation(element_config)

        return None

    def build_request(self, element_config: Dict) -> str:
        """Build the complete request for Gemini"""

        # Add element-specific instructions based on type
        element_type = element_config.get('type', 'unknown')
        specific_instructions = self.get_type_specific_instructions(element_type)

        request = f"""{self.system_instruction}

{specific_instructions}

Element Configuration:
{json.dumps(element_config, indent=2)}

Remember:
- Output ONLY the XML, no explanations
- Use exact specifications from the configuration
- Include all required negative prompts
- Reference only 1996 technology

Output the complete XML prompt now:"""

        return request

    def get_type_specific_instructions(self, element_type: str) -> str:
        """Get additional instructions for specific element types"""

        instructions = {
            ElementType.PHOTO_INSTRUCTIONAL.value: """
For this instructional photograph:
- Specify exact film characteristics (Kodak Gold 400, grain index 39)
- Include precise lighting setup (softbox positions, reflector angles)
- Describe child's hand position and grip detail
- Ensure beige Apple M0100 mouse is accurately described""",

            ElementType.CONTAINER_FEATUREBOX.value: """
For this container element:
- Ensure border is exactly 4px solid black
- Shadow must be hard-edged with 3px offset
- Background must be solid color from Klutz palette
- No rounded corners or modern effects""",

            ElementType.PIXELART.value: """
For this pixel art sprite:
- Base resolution must be 16x16 or 32x32
- Use nearest-neighbor scaling only
- Maximum 16 colors from period-appropriate palette
- Ensure hard pixel edges with no anti-aliasing""",

            ElementType.GUI_RECREATION.value: """
For this GUI recreation:
- MacPaint must be monochrome (black and white only)
- Use Chicago bitmap font exclusively
- Include stippled patterns for gray simulation
- Single pixel borders on all UI elements"""
        }

        return instructions.get(element_type, "")

    def extract_xml(self, response_text: str) -> str:
        """Extract clean XML content from Gemini response"""

        # Remove any markdown code blocks
        response_text = re.sub(r'```xml\s*\n?', '', response_text)
        response_text = re.sub(r'```\s*\n?', '', response_text)

        # Remove any commentary before or after XML
        response_text = re.sub(r'^.*?(?=<nano_banana_prompt>)', '', response_text, flags=re.DOTALL)
        response_text = re.sub(r'(?<=</nano_banana_prompt>).*?$', '', response_text, flags=re.DOTALL)

        # Find XML content
        match = re.search(r'<nano_banana_prompt>.*?</nano_banana_prompt>',
                         response_text, re.DOTALL)

        if match:
            xml_content = match.group(0)
            # Clean up whitespace
            xml_content = re.sub(r'\s+', ' ', xml_content)
            xml_content = re.sub(r'> <', '><', xml_content)
            return xml_content
        else:
            raise ValueError("No valid XML found in response")

    def validate_xml_structure(self, xml_content: str, element_config: Dict) -> bool:
        """Comprehensive XML validation"""

        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Check root element
            if root.tag != 'nano_banana_prompt':
                self.logger.error("Invalid root element")
                return False

            # Required elements
            required = ['element_id', 'element_type', 'positive_prompt', 'negative_prompt']

            for req in required:
                if root.find(req) is None:
                    self.logger.error(f"Missing required element: {req}")
                    return False

            # Validate element_id matches config
            element_id = root.find('element_id').text
            if element_id != element_config['id']:
                self.logger.error(f"Element ID mismatch: {element_id} != {element_config['id']}")
                return False

            # Check for forbidden terms in prompts
            positive_prompt = root.find('positive_prompt').text or ""
            negative_prompt = root.find('negative_prompt').text or ""

            forbidden = ['gradient', 'modern', 'blur', 'transparency', 'rounded',
                        'anti-aliasing', 'smooth', 'soft shadow', 'web 2.0']

            for term in forbidden:
                if term.lower() in positive_prompt.lower():
                    self.logger.error(f"Forbidden term '{term}' in positive prompt")
                    return False

            # Validate dimensions if present
            dimensions = root.find('.//dimensions')
            if dimensions is not None:
                width = dimensions.get('width')
                height = dimensions.get('height')

                if not (width and height and width.isdigit() and height.isdigit()):
                    self.logger.error("Invalid dimensions format")
                    return False

            # Validate colors are in hex format
            for color_elem in root.findall('.//*[@color]'):
                color = color_elem.get('color')
                if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    self.logger.error(f"Invalid color format: {color}")
                    return False

            return True

        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False

    def fallback_xml_generation(self, element_config: Dict) -> str:
        """Generate XML using templates when Gemini fails"""

        element_type = element_config.get('type', 'unknown')

        # Check for pre-defined template
        if element_type in self.element_templates:
            template = self.element_templates[element_type]
            return self.fill_template(template, element_config)

        # Use programmatic generation
        generators = {
            ElementType.PHOTO_INSTRUCTIONAL.value: self.generate_photo_xml,
            ElementType.CONTAINER_FEATUREBOX.value: self.generate_container_xml,
            ElementType.PIXELART.value: self.generate_pixelart_xml,
            ElementType.GUI_RECREATION.value: self.generate_gui_xml,
            ElementType.DOODLE.value: self.generate_doodle_xml,
            ElementType.EMBOSSED_FEATUREBOX.value: self.generate_embossed_xml
        }

        generator = generators.get(element_type, self.generate_generic_xml)
        return generator(element_config)

    def fill_template(self, template: str, config: Dict) -> str:
        """Fill template with configuration values"""

        # Simple template variable replacement
        for key, value in config.items():
            if isinstance(value, list):
                value = ','.join(map(str, value))
            template = template.replace(f'{{{key}}}', str(value))

        return template

    def generate_photo_xml(self, config: Dict) -> str:
        """Generate XML for photo elements"""

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_photo_instructional</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <photographic_specs>
        <film_stock>Kodak Gold 400</film_stock>
        <grain_index>39</grain_index>
        <iso>400</iso>
        <aperture>f/11</aperture>
        <shutter_speed>1/125</shutter_speed>
        <lens>100mm macro</lens>
    </photographic_specs>

    <lighting>
        <key_light position="45 degrees left" elevation="30 degrees" type="softbox 24x36 inches" />
        <fill_light position="60 degrees right" type="white foamcore reflector" ratio="1:2" />
    </lighting>

    <subject>
        <primary>{config.get('subject', 'child hand using computer mouse')}</primary>
        <hand_age>8-10 years</hand_age>
        <mouse_model>Apple Desktop Bus M0100</mouse_model>
        <mouse_color>beige</mouse_color>
    </subject>

    <positive_prompt>
        Instructional photograph from 1996 Klutz book, child's hand age 8-10
        gripping beige Apple M0100 rectangular mouse with single button,
        index finger on mouse button, coiled ADB cable visible, shot on
        Kodak Gold 400 35mm film with characteristic grain and warm highlights,
        f/11 aperture for sharp detail, softbox lighting from 45 degrees left,
        royal blue mousepad background, educational photography style
    </positive_prompt>

    <negative_prompt>
        modern optical mouse, wireless, USB, two buttons, scroll wheel, LED,
        adult hands, gradient, blur, depth of field, bokeh, artistic,
        dramatic lighting, black and white, HDR, digital photography,
        anti-aliasing, smooth, professional model
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_container_xml(self, config: Dict) -> str:
        """Generate XML for container elements"""

        bg_color = config.get('background', '#FFD700')

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>container_featurebox</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />
    <rotation degrees="{config.get('rotation', 0)}" />

    <appearance>
        <background color="{bg_color}" type="solid" />
        <border width="4" style="solid" color="#000000" />
        <shadow offset_x="3" offset_y="3" blur="0" color="#000000" />
        <corners type="square" angle="90" />
    </appearance>

    <positive_prompt>
        Flat rectangular container with solid {bg_color} background color,
        thick 4 pixel solid black border, perfect 90 degree square corners,
        hard-edged drop shadow offset 3 pixels right and 3 pixels down,
        pure black shadow with zero blur, 1996 desktop publishing aesthetic
    </positive_prompt>

    <negative_prompt>
        gradient, soft shadow, blur, rounded corners, transparency,
        bevel, emboss, 3D effect, modern design, anti-aliasing
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_pixelart_xml(self, config: Dict) -> str:
        """Generate XML for pixel art elements"""

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_pixelart</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <pixel_specs>
        <base_resolution width="32" height="32" />
        <magnification>{config.get('magnification', 8)}</magnification>
        <interpolation>nearest_neighbor</interpolation>
    </pixel_specs>

    <palette>
        <color index="0">#000000</color>
        <color index="1">#FFFFFF</color>
        <color index="2">#FF0000</color>
        <color index="3">#00FF00</color>
        <color index="4">#0000FF</color>
        <color index="5">#FFFF00</color>
        <color index="6">#FF00FF</color>
        <color index="7">#00FFFF</color>
    </palette>

    <positive_prompt>
        8-bit pixel art sprite, 32x32 base resolution, scaled {config.get('magnification', 8)}x
        with nearest neighbor interpolation, hard pixel edges, no anti-aliasing,
        limited color palette, retro NES aesthetic, clear sprite design
    </positive_prompt>

    <negative_prompt>
        smooth edges, anti-aliasing, gradient, blur, high resolution,
        modern pixel art, soft pixels, transparency, 3D shading
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_gui_xml(self, config: Dict) -> str:
        """Generate XML for GUI recreation"""

        software = config.get('software', 'MacPaint')

        if software == 'MacPaint':
            return self.generate_macpaint_xml(config)
        else:
            return self.generate_aseprite_xml(config)

    def generate_macpaint_xml(self, config: Dict) -> str:
        """Generate MacPaint interface XML"""

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <software>
        <name>MacPaint 1.0</name>
        <os>Apple System 6</os>
        <color_mode>1-bit monochrome</color_mode>
    </software>

    <interface>
        <title_bar text="untitled" font="Chicago" />
        <menu_bar items="File Edit Goodies Font FontSize Style" />
        <tool_palette position="left" rows="6" />
        <pattern_palette position="bottom" patterns="38" />
        <canvas width="576" height="720" />
    </interface>

    <positive_prompt>
        MacPaint 1.0 interface recreation, pure black and white monochrome,
        Chicago bitmap font, no anti-aliasing, tool palette on left side,
        pattern palette at bottom, single pixel black borders,
        stippled patterns for gray simulation, Atkinson dithering
    </positive_prompt>

    <negative_prompt>
        color, grayscale, anti-aliasing, smooth fonts, gradients,
        modern UI, Windows, transparency, rounded corners
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_aseprite_xml(self, config: Dict) -> str:
        """Generate simplified Aseprite interface XML"""

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <software>
        <name>Aseprite (simplified)</name>
        <style>1996 software aesthetic</style>
    </software>

    <interface>
        <tool_palette tools="pencil,eraser,bucket,rectangle" />
        <color_picker type="grid" colors="16" />
        <canvas grid="visible" size="32x32" />
    </interface>

    <positive_prompt>
        Simplified pixel art software interface for children,
        basic tool palette, 16 color grid, visible pixel grid,
        1996 software design with gray 3D borders, simple icons
    </positive_prompt>

    <negative_prompt>
        modern UI, dark theme, complex interface, transparency,
        layers panel, timeline, advanced tools
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_doodle_xml(self, config: Dict) -> str:
        """Generate XML for doodle elements"""

        doodle_type = config.get('doodle_type', 'arrow')

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_doodle</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />
    <rotation degrees="{config.get('rotation', 0)}" />

    <doodle_specs>
        <type>{doodle_type}</type>
        <line_weight>4</line_weight>
        <color>#000000</color>
        <style>hand_drawn_marker</style>
    </doodle_specs>

    <positive_prompt>
        Hand-drawn {doodle_type} with thick black marker,
        confident single stroke, slightly uneven line weight,
        natural imperfections, organic appearance, 4 pixel thickness
    </positive_prompt>

    <negative_prompt>
        perfect geometry, vector graphics, thin line, multiple strokes,
        computer generated, precise, mathematical
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_embossed_xml(self, config: Dict) -> str:
        """Generate XML for embossed elements"""

        text = config.get('embossed_text', 'REMEMBER!')

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>container_embossed_featurebox</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <embossing>
        <text>{text}</text>
        <technique>blind_emboss</technique>
        <depth>20</depth>
        <font>Chicago</font>
    </embossing>

    <positive_prompt>
        Blind embossed text "{text}" raised from paper surface,
        no ink or color, hard-edged highlights on top-left edges,
        shadows on bottom-right, paper texture visible on raised areas,
        tactile 3D appearance like Goosebumps book covers
    </positive_prompt>

    <negative_prompt>
        printed text, ink, color, flat, Photoshop bevel, soft glow,
        gradient, smooth, digital effect, metallic
    </negative_prompt>
</nano_banana_prompt>"""

    def generate_generic_xml(self, config: Dict) -> str:
        """Generic XML generation for unknown types"""

        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>{config.get('type', 'unknown')}</element_type>

    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />

    <positive_prompt>
        1996 Klutz Press aesthetic element, period appropriate design
    </positive_prompt>

    <negative_prompt>
        modern, gradient, transparency, anti-aliasing
    </negative_prompt>
</nano_banana_prompt>"""

    def batch_generate(self, elements: List[Dict], output_dir: str = 'prompts/gemini') -> Dict[str, str]:
        """Generate XML prompts for multiple elements efficiently"""

        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Starting batch generation for {len(elements)} elements")

        for i, element in enumerate(elements):
            element_id = element['id']

            # Check if already exists
            cache_file = output_path / f"{element_id}.xml"
            if cache_file.exists():
                self.logger.info(f"Using cached XML for {element_id}")
                results[element_id] = cache_file.read_text()
                continue

            # Generate new XML
            self.logger.info(f"Generating XML for {element_id} ({i+1}/{len(elements)})")

            try:
                xml_prompt = self.generate_xml_prompt(element)

                if xml_prompt:
                    # Save to file
                    cache_file.write_text(xml_prompt)
                    results[element_id] = xml_prompt
                    self.logger.info(f"Successfully generated and cached {element_id}")
                else:
                    self.logger.error(f"Failed to generate {element_id}")
                    results[element_id] = None

            except Exception as e:
                self.logger.error(f"Exception generating {element_id}: {str(e)}")
                results[element_id] = None

        # Summary
        successful = sum(1 for v in results.values() if v is not None)
        self.logger.info(f"Batch generation complete: {successful}/{len(elements)} successful")

        return results

    def validate_batch_results(self, results: Dict[str, str]) -> Dict:
        """Validate all generated XML prompts"""

        validation_report = {
            'total': len(results),
            'valid': 0,
            'invalid': 0,
            'missing': 0,
            'details': {}
        }

        for element_id, xml_content in results.items():
            if xml_content is None:
                validation_report['missing'] += 1
                validation_report['details'][element_id] = 'Missing'
            else:
                # Create minimal config for validation
                config = {'id': element_id}
                if self.validate_xml_structure(xml_content, config):
                    validation_report['valid'] += 1
                    validation_report['details'][element_id] = 'Valid'
                else:
                    validation_report['invalid'] += 1
                    validation_report['details'][element_id] = 'Invalid'

        return validation_report


# Usage example
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize generator
    config = GeminiConfig(
        api_key="your-api-key-here",
        temperature=0.2,
        requests_per_minute=60
    )

    generator = GeminiXMLGenerator(config)

    # Test single element
    test_element = {
        'id': 'L_photo_mouse_01',
        'type': 'graphic_photo_instructional',
        'dimensions': [600, 450],
        'position': [250, 300],
        'subject': 'child hand using Apple mouse'
    }

    xml_result = generator.generate_xml_prompt(test_element)
    if
xml_result = generator.generate_xml_prompt(test_element)
    if xml_result:
        print("Generated XML:")
        print(xml_result)

    # Test batch generation
    test_batch = [
        {
            'id': 'L_photo_mouse_01',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 450],
            'subject': 'child hand using Apple mouse'
        },
        {
            'id': 'L_container_tip_01',
            'type': 'container_featurebox',
            'dimensions': [400, 200],
            'background': '#FFD700',
            'rotation': -2
        },
        {
            'id': 'R_pixelart_mario_01',
            'type': 'graphic_pixelart',
            'dimensions': [256, 256],
            'magnification': 8,
            'subject': 'simple Mario sprite'
        }
    ]

    # Generate batch
    results = generator.batch_generate(test_batch)

    # Validate results
    validation_report = generator.validate_batch_results(results)
    print(f"\nValidation Report:")
    print(f"Total: {validation_report['total']}")
    print(f"Valid: {validation_report['valid']}")
    print(f"Invalid: {validation_report['invalid']}")
    print(f"Missing: {validation_report['missing']}")
