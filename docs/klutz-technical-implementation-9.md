# Section 9: Nano-Banana Integration Protocol

#!/usr/bin/env python3
"""
nano_banana_integration.py - Complete interface for nano-banana image generation model
"""

import requests
import base64
from PIL import Image
import io
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, Dict, List
import hashlib
import time
import json
from pathlib import Path
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class GenerationStatus(Enum):
    """Status codes for generation results"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INVALID_XML = "invalid_xml"
    DIMENSION_MISMATCH = "dimension_mismatch"
    RETRY_EXCEEDED = "retry_exceeded"

@dataclass
class NanoBananaConfig:
    """Configuration for nano-banana API"""
    api_endpoint: str
    api_key: str
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 2.0
    max_concurrent: int = 4
    
    # Generation parameters
    steps: int = 50
    cfg_scale: float = 7.5
    sampler: str = "k_euler_ancestral"
    seed: int = -1  # -1 for random
    
    # Quality settings
    quality_preset: str = "high"  # low, medium, high
    denoise_strength: float = 0.7
    
    # Validation settings
    validate_dimensions: bool = True
    max_dimension_variance: int = 10  # pixels
    validate_content: bool = True

class NanoBananaGenerator:
    """Handles all nano-banana API interactions for image generation"""
    
    def __init__(self, config: NanoBananaConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Cache for generated images
        self.cache_dir = Path('cache/nano_banana')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'cache_hits': 0,
            'total_time': 0
        }
        
    def parse_xml_prompt(self, xml_prompt: str) -> Dict:
        """Parse XML prompt to extract generation parameters"""
        
        try:
            root = ET.fromstring(xml_prompt)
            
            params = {
                'element_id': root.findtext('element_id', ''),
                'element_type': root.findtext('element_type', ''),
                'positive_prompt': root.findtext('positive_prompt', ''),
                'negative_prompt': root.findtext('negative_prompt', ''),
            }
            
            # Extract dimensions if present
            dims = root.find('.//dimensions')
            if dims is not None:
                params['width'] = int(dims.get('width', 512))
                params['height'] = int(dims.get('height', 512))
            else:
                # Default dimensions based on element type
                params.update(self.get_default_dimensions(params['element_type']))
            
            # Extract element-specific parameters
            if params['element_type'] == 'graphic_pixelart':
                pixel_specs = root.find('.//pixel_specs')
                if pixel_specs is not None:
                    base_res = pixel_specs.find('base_resolution')
                    if base_res is not None:
                        params['base_width'] = int(base_res.get('width', 32))
                        params['base_height'] = int(base_res.get('height', 32))
                    params['magnification'] = int(pixel_specs.findtext('magnification', 8))
            
            # Extract photographic parameters
            if params['element_type'] == 'graphic_photo_instructional':
                photo_specs = root.find('.//photographic_specs')
                if photo_specs is not None:
                    params['film_stock'] = photo_specs.findtext('film_stock', 'Kodak Gold 400')
                    params['grain_index'] = int(photo_specs.findtext('grain_index', 39))
            
            return params
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {str(e)}")
            raise ValueError(f"Invalid XML prompt: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error parsing XML: {str(e)}")
            raise
    
    def get_default_dimensions(self, element_type: str) -> Dict[str, int]:
        """Get default dimensions for element type"""
        
        defaults = {
            'graphic_photo_instructional': {'width': 600, 'height': 450},
            'container_featurebox': {'width': 800, 'height': 400},
            'graphic_splat_container': {'width': 300, 'height': 200},
            'graphic_pixelart': {'width': 256, 'height': 256},
            'graphic_gui_recreation': {'width': 1200, 'height': 800},
            'graphic_doodle': {'width': 200, 'height': 150},
            'container_embossed_featurebox': {'width': 800, 'height': 200},
            'graphic_spiral_binding': {'width': 462, 'height': 2200}
        }
        
        return defaults.get(element_type, {'width': 512, 'height': 512})
    
    def build_generation_request(self, xml_params: Dict) -> Dict:
        """Build complete generation request for API"""
        
        request = {
            'prompt': xml_params['positive_prompt'],
            'negative_prompt': xml_params['negative_prompt'],
            'width': xml_params['width'],
            'height': xml_params['height'],
            'num_inference_steps': self.config.steps,
            'guidance_scale': self.config.cfg_scale,
            'sampler': self.config.sampler,
            'seed': self.config.seed,
            'denoise_strength': self.config.denoise_strength
        }
        
        # Add element-specific parameters
        element_type = xml_params['element_type']
        
        if element_type == 'graphic_pixelart':
            # Pixel art needs special handling
            request['sampler'] = 'k_euler'  # Better for pixel art
            request['guidance_scale'] = 10.0  # Higher guidance for crisp pixels
            request['custom_params'] = {
                'interpolation': 'nearest',
                'base_resolution': f"{xml_params.get('base_width', 32)}x{xml_params.get('base_height', 32)}",
                'scaling': xml_params.get('magnification', 8)
            }
        
        elif element_type == 'graphic_photo_instructional':
            # Photography needs film grain
            request['custom_params'] = {
                'film_emulation': xml_params.get('film_stock', 'Kodak Gold 400'),
                'grain_amount': xml_params.get('grain_index', 39) / 100,
                'color_profile': 'warm_highlights'
            }
        
        elif element_type == 'graphic_gui_recreation':
            # GUI needs high precision
            request['guidance_scale'] = 12.0
            request['custom_params'] = {
                'style': 'technical_drawing',
                'precision': 'high'
            }
        
        return request
    
    def get_cache_key(self, xml_params: Dict) -> str:
        """Generate cache key from parameters"""
        
        # Create deterministic hash from key parameters
        cache_data = {
            'element_id': xml_params['element_id'],
            'positive_prompt': xml_params['positive_prompt'],
            'negative_prompt': xml_params['negative_prompt'],
            'width': xml_params['width'],
            'height': xml_params['height'],
            'seed': self.config.seed if self.config.seed != -1 else 'random'
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def check_cache(self, cache_key: str) -> Optional[Image.Image]:
        """Check if image exists in cache"""
        
        cache_path = self.cache_dir / f"{cache_key}.png"
        if cache_path.exists():
            self.logger.info(f"Cache hit for {cache_key[:8]}...")
            self.stats['cache_hits'] += 1
            return Image.open(cache_path)
        return None
    
    def save_to_cache(self, cache_key: str, image: Image.Image):
        """Save image to cache"""
        
        cache_path = self.cache_dir / f"{cache_key}.png"
        image.save(cache_path, 'PNG', compress_level=9)
        self.logger.debug(f"Cached image as {cache_key[:8]}...")
    
    def call_api(self, request: Dict) -> requests.Response:
        """Make API call with error handling"""
        
        try:
            response = self.session.post(
                self.config.api_endpoint,
                json=request,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"API call timed out after {self.config.timeout}s")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def decode_image_response(self, response: requests.Response) -> Image.Image:
        """Decode image from API response"""
        
        try:
            response_data = response.json()
            
            # Check for error in response
            if 'error' in response_data:
                raise Exception(f"API error: {response_data['error']}")
            
            # Get base64 image data
            if 'image' not in response_data:
                raise Exception("No image in API response")
            
            image_data = response_data['image']
            
            # Handle different encoding formats
            if isinstance(image_data, str):
                # Remove data URL prefix if present
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                # Decode base64
                img_bytes = base64.b64decode(image_data)
            else:
                # Assume bytes
                img_bytes = image_data
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_bytes))
            
            return image
            
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")
        except Exception as e:
            raise Exception(f"Failed to decode image: {str(e)}")
    
    def validate_generated_image(self, image: Image.Image, xml_params: Dict) -> Tuple[bool, str]:
        """Validate generated image meets specifications"""
        
        # Check dimensions
        if self.config.validate_dimensions:
            expected_width = xml_params['width']
            expected_height = xml_params['height']
            
            width_diff = abs(image.width - expected_width)
            height_diff = abs(image.height - expected_height)
            
            if width_diff > self.config.max_dimension_variance or height_diff > self.config.max_dimension_variance:
                return False, f"Dimension mismatch: got {image.size}, expected ({expected_width}, {expected_height})"
        
        # Check image mode
        if image.mode not in ['RGB', 'RGBA']:
            image = image.convert('RGB')
        
        # Element-specific validation
        element_type = xml_params['element_type']
        
        if element_type == 'graphic_pixelart':
            # Check for proper pixelation
            if not self.validate_pixelart(image, xml_params):
                return False, "Image does not appear to be proper pixel art"
        
        elif element_type == 'graphic_gui_recreation':
            # Check for monochrome if MacPaint
            if 'MacPaint' in xml_params.get('positive_prompt', ''):
                if not self.validate_monochrome(image):
                    return False, "MacPaint GUI should be monochrome"
        
        elif element_type == 'container_featurebox':
            # Check for hard edges
            if not self.validate_hard_edges(image):
                return False, "Container should have hard edges, no blur"
        
        return True, "Validation passed"
    
    def validate_pixelart(self, image: Image.Image, params: Dict) -> bool:
        """Validate pixel art characteristics"""
        
        # Downscale to check for proper pixelation
        base_width = params.get('base_width', 32)
        base_height = params.get('base_height', 32)
        
        # Resize to base resolution
        small = image.resize((base_width, base_height), Image.Resampling.NEAREST)
        
        # Scale back up
        scaled = small.resize(image.size, Image.Resampling.NEAREST)
        
        # Compare with original - should be nearly identical for true pixel art
        diff = np.array(image) - np.array(scaled)
        max_diff = np.max(np.abs(diff))
        
        # Allow small differences due to compression
        return max_diff < 30
    
    def validate_monochrome(self, image: Image.Image) -> bool:
        """Check if image is truly monochrome"""
        
        # Convert to grayscale
        gray = image.convert('L')
        
        # Get unique values
        unique_values = len(set(gray.getdata()))
        
        # True monochrome should have very few unique values
        return unique_values < 10
    
    def validate_hard_edges(self, image: Image.Image) -> bool:
        """Check for hard edges (no blur)"""
        
        # Convert to numpy array
        img_array = np.array(image.convert('L'))
        
        # Calculate gradients
        grad_x = np.gradient(img_array, axis=1)
        grad_y = np.gradient(img_array, axis=0)
        
        # Calculate edge magnitudes
        edges = np.sqrt(grad_x**2 + grad_y**2)
        
        # Hard edges have high gradient values
        strong_edges = edges > 50
        
        # Check for sharp transitions (not gradual)
        edge_widths = []
        for row in strong_edges:
            transitions = np.diff(row.astype(int))
            if np.any(transitions):
                edge_widths.append(np.sum(np.abs(transitions)))
        
        # Hard edges should have narrow transitions
        if edge_widths:
            avg_width = np.mean(edge_widths)
            return avg_width < 5
        
        return True
    
    def apply_post_processing(self, image: Image.Image, element_type: str) -> Image.Image:
        """Apply element-specific post-processing"""
        
        if element_type == 'graphic_photo_instructional':
            # Add film grain
            image = self.add_film_grain(image, grain_amount=0.39)
        
        elif element_type == 'graphic_pixelart':
            # Ensure nearest-neighbor scaling
            image = self.ensure_pixel_perfection(image)
        
        elif element_type == 'container_embossed_featurebox':
            # Enhance embossing effect
            image = self.enhance_embossing(image)
        
        return image
    
    def add_film_grain(self, image: Image.Image, grain_amount: float = 0.39) -> Image.Image:
        """Add Kodak Gold 400 style film grain"""
        
        img_array = np.array(image)
        
        # Generate grain pattern
        grain = np.random.normal(0, grain_amount * 20, img_array.shape)
        
        # Add color-specific grain (Kodak Gold has more grain in shadows)
        luminance = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        shadow_mask = luminance < 128
        grain[shadow_mask] *= 1.5
        
        # Apply grain
        result = img_array + grain
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return Image.fromarray(result)
    
    def ensure_pixel_perfection(self, image: Image.Image) -> Image.Image:
        """Ensure pixel art has perfect hard edges"""
        
        # Find the likely base resolution
        # This is a simplified approach - in production, use the actual base resolution
        base_size = 32
        
        # Downscale then upscale with nearest neighbor
        small = image.resize((base_size, base_size), Image.Resampling.NEAREST)
        perfect = small.resize(image.size, Image.Resampling.NEAREST)
        
        return perfect
    
    def enhance_embossing(self, image: Image.Image) -> Image.Image:
        """Enhance embossed effect"""
        
        from PIL import ImageFilter
        
        # Apply edge enhancement to make embossing more visible
        enhanced = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Blend with original
        result = Image.blend(image, enhanced, 0.3)
        
        return result
    
    def generate_image(self, xml_prompt: str) -> Tuple[Optional[Image.Image], GenerationStatus, str]:
        """Main method to generate image from XML prompt"""
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Parse XML prompt
            xml_params = self.parse_xml_prompt(xml_prompt)
            element_id = xml_params['element_id']
            
            self.logger.info(f"Generating image for {element_id}")
            
            # Check cache
            cache_key = self.get_cache_key(xml_params)
            cached_image = self.check_cache(cache_key)
            if cached_image:
                self.stats['successful'] += 1
                return cached_image, GenerationStatus.SUCCESS, "Retrieved from cache"
            
            # Build generation request
            request = self.build_generation_request(xml_params)
            
            # Try generation with retries
            for attempt in range(self.config.max_retries):
                try:
                    # Make API call
                    response = self.call_api(request)
                    
                    # Decode image
                    image = self.decode_image_response(response)
                    
                    # Validate image
                    valid, message = self.validate_generated_image(image, xml_params)
                    if not valid:
                        self.logger.warning(f"Validation failed: {message}")
                        if attempt < self.config.max_retries - 1:
                            time.sleep(self.config.retry_delay * (attempt + 1))
                            continue
                    
                    # Apply post-processing
                    image = self.apply_post_processing(image, xml_params['element_type'])
                    
                    # Save to cache
                    self.save_to_cache(cache_key, image)
                    
                    # Update stats
                    self.stats['successful'] += 1
                    self.stats['total_time'] += time.time() - start_time
                    
                    self.logger.info(f"Successfully generated {element_id}")
                    return image, GenerationStatus.SUCCESS, "Generation successful"
                    
                except TimeoutError:
                    self.logger.warning(f"Attempt {attempt + 1} timed out")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                    else:
                        self.stats['failed'] += 1
                        return None, GenerationStatus.TIMEOUT, "Generation timed out"
                
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                    else:
                        self.stats['failed'] += 1
                        return None, GenerationStatus.FAILED, str(e)
            
            self.stats['failed'] += 1
            return None, GenerationStatus.RETRY_EXCEEDED, "Max retries exceeded"
            
        except ValueError as e:
            self.stats['failed'] += 1
            return None, GenerationStatus.INVALID_XML, str(e)
        except Exception as e:
            self.stats['failed'] += 1
            self.logger.error(f"Unexpected error: {str(e)}")
            return None, GenerationStatus.FAILED, str(e)
    
    def batch_generate(self, xml_prompts: List[str], output_dir: str = 'assets/generated') -> Dict:
        """Generate multiple images in parallel"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'successful': [],
            'failed': [],
            'details': {}
        }
        
        self.logger.info(f"Starting batch generation for {len(xml_prompts)} images")
        
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent) as executor:
            # Submit all tasks
            future_to_xml = {
                executor.submit(self.generate_image, xml): xml 
                for xml in xml_prompts
            }
            
            # Process results as they complete
            for future in as_completed(future_to_xml):
                xml_prompt = future_to_xml[future]
                
                try:
                    # Parse element ID for tracking
                    root = ET.fromstring(xml_prompt)
                    element_id = root.findtext('element_id', 'unknown')
                    
                    # Get result
                    image, status, message = future.result()
                    
                    if status == GenerationStatus.SUCCESS and image:
                        # Save image
                        output_file = output_path / f"{element_id}.png"
                        image.save(output_file, 'PNG', compress_level=9)
                        
                        results['successful'].append(element_id)
                        results['details'][element_id] = {
                            'status': status.value,
                            'message': message,
                            'path': str(output_file)
                        }
                        
                        self.logger.info(f"✓ Generated {element_id}")
                    else:
                        results['failed'].append(element_id)
                        results['details'][element_id] = {
                            'status': status.value,
                            'message': message
                        }
                        
                        self.logger.error(f"✗ Failed {element_id}: {message}")
                        
                except Exception as e:
                    self.logger.error(f"Exception processing result: {str(e)}")
                    results['failed'].append('unknown')
        
        # Summary
        self.logger.info(f"Batch complete: {len(results['successful'])}/{len(xml_prompts)} successful")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get generation statistics"""
        
        stats = self.stats.copy()
        
        if stats['successful'] > 0:
            stats['avg_time'] = stats['total_time'] / stats['successful']
            stats['success_rate'] = stats['successful'] / stats['total_requests'] * 100
        else:
            stats['avg_time'] = 0
            stats['success_rate'] = 0
        
        stats['cache_hit_rate'] = stats['cache_hits'] / max(stats['total_requests'], 1) * 100
        
        return stats


# Usage example
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize generator
    config = NanoBananaConfig(
        api_endpoint="https://api.nano-banana.com/v1/generate",
        api_key="your-api-key-here",
        max_concurrent=4,
        steps=50,
        cfg_scale=7.5
    )
    
    generator = NanoBananaGenerator(config)
    
    # Test XML prompt
    test_xml = """<nano_banana_prompt>
        <element_id>L_photo_mouse_01</element_id>
        <element_type>graphic_photo_instructional</element_type>
        <dimensions width="600" height="450" />
        <positive_prompt>
            Child's hand using beige Apple M0100 mouse, Kodak Gold 400 film,
            instructional photography, 1996 style
        </positive_prompt>
        <negative_prompt>
            modern, wireless, optical mouse, gradient, blur
        </negative_prompt>
    </nano_banana_prompt>"""
    
    # Generate single image
    image, status, message = generator.generate_image(test_xml)
    
    if status == GenerationStatus.SUCCESS:
        print(f"Success! Image size: {image.size}")
        image.save("test_output.png")
    else:
        print(f"Failed: {status.value} - {message}")
    
    # Print statistics
    stats = generator.get_statistics()
    print("\nGeneration Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
