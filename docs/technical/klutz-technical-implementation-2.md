#!/usr/bin/env python3
"""
asset_validator.py - Validates all assets meet period-authentic specifications
"""

import re
from PIL import Image
from pathlib import Path
import numpy as np
from collections import Counter
import yaml

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
