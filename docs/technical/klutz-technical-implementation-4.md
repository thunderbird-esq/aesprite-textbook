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
