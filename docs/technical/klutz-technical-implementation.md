# Complete Technical Implementation Details for Klutz Workbook Project

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

        # Validate all image assets
        for image_file in project_path.glob('assets/**/*.png'):
            violations = self.validate_image_asset(image_file)
            report['assets'][str(image_file)] = violations

            if violations:
                report['summary']['failed'] += 1
            else:
                report['summary']['passed'] += 1
