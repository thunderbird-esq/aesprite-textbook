Section 8: Gemini-2.0-Flash-Exp Integration Protocol
python#!/usr/bin/env python3
"""
gemini_integration.py - Complete Gemini-2.0-Flash-Exp integration for XML prompt generation
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import json
import time
import re
from pathlib import Path

class GeminiXMLGenerator:
    """Handles all Gemini API interactions for XML prompt generation"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Model configuration for XML generation
        self.generation_config = {
            'temperature': 0.2,  # Low for consistency
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
        
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config=self.generation_config
        )
        
        # System instruction for XML generation
        self.system_instruction = self.load_system_instruction()
        
    def load_system_instruction(self) -> str:
        """Load the comprehensive system instruction for Gemini"""
        
        return """You are an XML prompt engineer for the nano-banana image generation model, 
creating assets for a 1996 Klutz Press computer graphics workbook.

CRITICAL CONSTRAINTS:
1. Output ONLY valid XML - no markdown, no explanations
2. Use EXCLUSIVELY quantitative specifications (pixels, degrees, hex codes)
3. Reference ONLY technology available in 1996
4. Include comprehensive negative prompts for every element

XML SCHEMA REQUIREMENTS:
- Root element: <nano_banana_prompt>
- Required child elements: element_id, element_type, specifications, positive_prompt, negative_prompt
- All measurements in pixels
- All colors in hex format (#RRGGBB)
- All angles in degrees (-180 to 180)

FORBIDDEN TERMS:
gradient, modern, sleek, minimal, UX, UI, responsive, mobile, wireless, USB, 
LED, LCD, HD, 4K, anti-aliasing, transparency, blur, soft shadow, web 2.0

REQUIRED SPECIFICATIONS BY TYPE:

graphic_photo_instructional:
- Film: Kodak Gold 400 (grain index 39)
- Camera: 100mm macro lens, f/11 aperture
- Lighting: 45° key light, 60° fill reflector
- Subject: Apple M0100 mouse, beige, rectangular

container_featurebox:
- Border: 4px solid black
- Shadow: hard-edged, 3px offset, no blur
- Background: solid color only
- Corners: perfect 90° angles

graphic_pixelart:
- Resolution: 32x32 base
- Scaling: nearest-neighbor only
- Colors: maximum 16
- Style: 8-bit console aesthetic

Generate XML now for the following element:"""
    
    def generate_xml_prompt(self, element_config: Dict) -> str:
        """Generate XML prompt for a single element"""
        
        # Build the specific request
        request = f"""{self.system_instruction}

Element Configuration:
{json.dumps(element_config, indent=2)}

Output the complete XML prompt following all specifications."""
        
        try:
            response = self.model.generate_content(request)
            xml_content = self.extract_xml(response.text)
            
            if self.validate_xml_structure(xml_content):
                return xml_content
            else:
                raise ValueError("Generated XML failed validation")
                
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {str(e)}")
            return self.fallback_xml_generation(element_config)
    
    def extract_xml(self, response_text: str) -> str:
        """Extract XML content from Gemini response"""
        
        # Remove any markdown code blocks
        response_text = re.sub(r'```xml\n?', '', response_text)
        response_text = re.sub(r'```\n?', '', response_text)
        
        # Find XML content
        match = re.search(r'<nano_banana_prompt>.*</nano_banana_prompt>', 
                         response_text, re.DOTALL)
        
        if match:
            return match.group(0)
        else:
            raise ValueError("No valid XML found in response")
    
    def validate_xml_structure(self, xml_content: str) -> bool:
        """Validate XML meets our schema requirements"""
        
        required_elements = [
            '<element_id>',
            '<element_type>',
            '<positive_prompt>',
            '<negative_prompt>'
        ]
        
        for element in required_elements:
            if element not in xml_content:
                return False
        
        # Check for forbidden terms
        forbidden = ['gradient', 'modern', 'blur', 'transparency']
        for term in forbidden:
            if term.lower() in xml_content.lower():
                return False
        
        return True
    
    def batch_generate(self, elements: List[Dict]) -> Dict[str, str]:
        """Generate XML prompts for multiple elements with rate limiting"""
        
        results = {}
        
        for i, element in enumerate(elements):
            # Rate limiting (60 requests per minute for Gemini)
            if i > 0:
                time.sleep(1.1)
            
            try:
                xml_prompt = self.generate_xml_prompt(element)
                results[element['id']] = xml_prompt
                
                # Save to file
                output_path = Path(f"prompts/gemini/{element['id']}.xml")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(xml_prompt)
                
            except Exception as e:
                print(f"Failed to generate {element['id']}: {str(e)}")
                results[element['id']] = None
        
        return results
    
    def fallback_xml_generation(self, element_config: Dict) -> str:
        """Fallback template-based generation if Gemini fails"""
        
        element_type = element_config.get('type', 'unknown')
        
        templates = {
            'graphic_photo_instructional': self.photo_template,
            'container_featurebox': self.container_template,
            'graphic_pixelart': self.pixelart_template
        }
        
        template_func = templates.get(element_type, self.generic_template)
        return template_func(element_config)
    
    def photo_template(self, config: Dict) -> str:
        """Template for photo elements"""
        
        return f"""<nano_banana_prompt>
    <element_id>{config['id']}</element_id>
    <element_type>graphic_photo_instructional</element_type>
    <dimensions width="{config['dimensions'][0]}" height="{config['dimensions'][1]}" />
    <film_stock>Kodak Gold 400</film_stock>
    <subject>{config.get('subject', 'instructional photograph')}</subject>
    <positive_prompt>
        1996 instructional photo, Kodak Gold 400 film, grain visible,
        {config.get('subject', 'educational subject')}, high angle,
        softbox lighting, sharp focus, f/11 aperture
    </positive_prompt>
    <negative_prompt>
        modern, digital, gradient, blur, HDR, artistic, dramatic
    </negative_prompt>
</nano_banana_prompt>"""
Section 9: Nano-Banana Integration Protocol
python#!/usr/bin/env python3
"""
nano_banana_integration.py - Interface for nano-banana image generation
"""

import requests
import base64
from PIL import Image
import io
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
import hashlib

class NanoBananaGenerator:
    """Handles nano-banana API calls and image generation"""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.endpoint = api_endpoint
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/xml'
        }
        
        # Generation parameters
        self.default_params = {
            'steps': 50,
            'cfg_scale': 7.5,
            'seed': -1,  # Random
            'sampler': 'k_euler_ancestral'
        }
    
    def generate_image(self, xml_prompt: str, params: Optional[Dict] = None) -> Image.Image:
        """Generate image from XML prompt"""
        
        # Parse XML to extract key parameters
        root = ET.fromstring(xml_prompt)
        element_id = root.find('element_id').text
        
        # Merge with default parameters
        generation_params = self.default_params.copy()
        if params:
            generation_params.update(params)
        
        # Add XML to parameters
        generation_params['prompt_xml'] = xml_prompt
        
        # Make API call
        response = requests.post(
            self.endpoint,
            json=generation_params,
            headers=self.headers,
            timeout=60
        )
        
        if response.status_code == 200:
            # Decode base64 image
            img_data = base64.b64decode(response.json()['image'])
            img = Image.open(io.BytesIO(img_data))
            
            # Validate dimensions
            expected_dims = self.extract_dimensions(xml_prompt)
            if expected_dims and img.size != expected_dims:
                img = self.resize_to_spec(img, expected_dims)
            
            return img
        else:
            raise Exception(f"Generation failed: {response.status_code}")
    
    def extract_dimensions(self, xml_prompt: str) -> Optional[Tuple[int, int]]:
        """Extract expected dimensions from XML"""
        
        try:
            root = ET.fromstring(xml_prompt)
            dims = root.find('.//dimensions')
            if dims is not None:
                width = int(dims.get('width'))
                height = int(dims.get('height'))
                return (width, height)
        except:
            pass
        return None
    
    def resize_to_spec(self, img: Image.Image, target_dims: Tuple[int, int]) -> Image.Image:
        """Resize image to match specifications"""
        
        # Use LANCZOS for photos, NEAREST for pixel art
        resample = Image.Resampling.LANCZOS
        
        if 'pixelart' in str(target_dims):  # Crude check, improve this
            resample = Image.Resampling.NEAREST
        
        return img.resize(target_dims, resample)
    
    def generate_with_retry(self, xml_prompt: str, max_retries: int = 3) -> Image.Image:
        """Generate with automatic retry on failure"""
        
        for attempt in range(max_retries):
            try:
                return self.generate_image(xml_prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
Section 10: Quality Assurance Pipeline
python#!/usr/bin/env python3
"""
quality_assurance.py - Comprehensive QA system for generated assets
"""

class QualityAssurancePipeline:
    """Multi-stage quality checks for all generated content"""
    
    def __init__(self):
        self.checks = {
            'technical': TechnicalQA(),
            'aesthetic': AestheticQA(),
            'historical': HistoricalAccuracyQA(),
            'safety': ContentSafetyQA()
        }
    
    def validate_asset(self, asset_path: str, element_config: Dict) -> Dict:
        """Run all QA checks on an asset"""
        
        results = {
            'asset': asset_path,
            'passed': True,
            'checks': {}
        }
        
        for check_name, checker in self.checks.items():
            check_result = checker.validate(asset_path, element_config)
            results['checks'][check_name] = check_result
            
            if not check_result['passed']:
                results['passed'] = False
        
        return results

class TechnicalQA:
    """Technical quality checks"""
    
    def validate(self, asset_path: str, config: Dict) -> Dict:
        img = Image.open(asset_path)
        
        checks = {
            'dimensions': img.size == tuple(config['dimensions']),
            'color_mode': img.mode in ['RGB', 'RGBA'],
            'dpi': img.info.get('dpi', (72, 72))[0] >= 300,
            'file_size': Path(asset_path).stat().st_size < 10_000_000
        }
        
        return {
            'passed': all(checks.values()),
            'details': checks
        }

class AestheticQA:
    """Period-appropriate aesthetic validation"""
    
    def validate(self, asset_path: str, config: Dict) -> Dict:
        img = Image.open(asset_path)
        img_array = np.array(img)
        
        # Check for forbidden modern aesthetics
        checks = {
            'no_gradients': not self.has_gradients(img_array),
            'hard_shadows': self.has_hard_shadows(img_array),
            'correct_colors': self.check_color_palette(img_array),
            'proper_grain': self.has_film_grain(img_array) if 'photo' in config['type'] else True
        }
        
        return {
            'passed': all(checks.values()),
            'details': checks
        }
    
    def has_gradients(self, img_array: np.ndarray) -> bool:
        """Detect smooth gradients (forbidden)"""
        
        # Check color transitions in horizontal lines
        for row in img_array[::10]:  # Sample every 10th row
            colors = np.unique(row.reshape(-1, 3), axis=0)
            if len(colors) > 50:  # Too many unique colors = gradient
                return True
        return False
    
    def has_hard_shadows(self, img_array: np.ndarray) -> bool:
        """Verify shadows are hard-edged"""
        
        # Edge detection on dark regions
        gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        edges = np.gradient(gray)
        
        # Hard shadows have sharp transitions
        edge_magnitudes = np.sqrt(edges[0]**2 + edges[1]**2)
        sharp_edges = np.sum(edge_magnitudes > 50)
        
        return sharp_edges > 100  # Threshold for minimum sharp edges
Section 11: Automated Testing Framework
python#!/usr/bin/env python3
"""
test_framework.py - Automated testing for all components
"""

import unittest
from unittest.mock import Mock, patch

class TestKlutzCompositor(unittest.TestCase):
    """Test suite for compositor functionality"""
    
    def setUp(self):
        self.compositor = KlutzCompositor('config/test_config.yaml')
    
    def test_spine_clearance(self):
        """Verify spine dead zone is respected"""
        
        # Create element that would intrude
        element = Mock()
        element.width = 500
        element.height = 300
        
        # Position that would cross spine
        x, y = 1450, 500  # Would extend into spine at 1469
        
        self.assertTrue(
            self.compositor.check_spine_intrusion(x, y, element.width, element.height)
        )
    
    def test_chaos_rotation_deterministic(self):
        """Verify rotation is deterministic based on ID"""
        
        rotation1 = self.compositor.get_chaos_rotation('test_element_01', 15)
        rotation2 = self.compositor.get_chaos_rotation('test_element_01', 15)
        
        self.assertEqual(rotation1, rotation2)
    
    def test_cmyk_shift_accuracy(self):
        """Verify CMYK misregistration matches specifications"""
        
        test_img = Image.new('RGB', (100, 100), (128, 128, 128))
        shifted = self.compositor.apply_cmyk_misregistration(test_img)
        
        # Verify shifts occurred
        self.assertNotEqual(np.array(test_img), np.array(shifted))

class TestPromptGeneration(unittest.TestCase):
    """Test XML prompt generation"""
    
    def test_no_forbidden_terms(self):
        """Ensure prompts don't contain forbidden terms"""
        
        generator = PromptGenerator()
        
        element = {
            'id': 'test_01',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 400]
        }
        
        xml = generator.generate_photo_prompt(element)
        
        forbidden = ['gradient', 'modern', 'USB', 'wireless']
        for term in forbidden:
            self.assertNotIn(term.lower(), xml.lower())
    
    def test_required_xml_structure(self):
        """Verify XML has required elements"""
        
        generator = PromptGenerator()
        
        xml = generator.generate_container_prompt({'id': 'test', 'dimensions': [100, 100]})
        
        self.assertIn('<nano_banana_prompt>', xml)
        self.assertIn('</nano_banana_prompt>', xml)
        self.assertIn('<element_id>', xml)
        self.assertIn('<positive_prompt>', xml)
        self.assertIn('<negative_prompt>', xml)
Section 12: Performance Optimization
python#!/usr/bin/env python3
"""
performance_optimization.py - Speed and resource optimization
"""

class PerformanceOptimizer:
    """Optimize generation pipeline for speed and resources"""
    
    def __init__(self):
        self.cache = AssetCache()
        self.parallel_executor = ParallelExecutor()
    
    def optimize_spread_generation(self, spread_config: Dict) -> Dict:
        """Optimize a spread generation plan"""
        
        optimizations = {
            'cached_assets': [],
            'parallel_generations': [],
            'sequential_required': []
        }
        
        for element in spread_config['elements']:
            # Check cache first
            if self.cache.exists(element['id']):
                optimizations['cached_assets'].append(element['id'])
            
            # Check if can be parallelized
            elif self.can_parallelize(element):
                optimizations['parallel_generations'].append(element)
            
            else:
                optimizations['sequential_required'].append(element)
        
        return optimizations
    
    def can_parallelize(self, element: Dict) -> bool:
        """Determine if element can be generated in parallel"""
        
        # Photos and simple containers can be parallel
        parallelizable_types = [
            'graphic_photo_instructional',
            'container_featurebox',
            'graphic_doodle'
        ]
        
        return element['type'] in parallelizable_types

class AssetCache:
    """Cache for generated assets"""
    
    def __init__(self, cache_dir: str = 'cache/assets'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index = self.load_index()
    
    def get_cache_key(self, element_config: Dict) -> str:
        """Generate cache key from element configuration"""
        
        # Create deterministic hash from config
        config_str = json.dumps(element_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def exists(self, element_id: str) -> bool:
        """Check if asset exists in cache"""
        
        return element_id in self.index
    
    def store(self, element_id: str, asset_path: str):
        """Store asset in cache"""
        
        cache_key = self.get_cache_key({'id': element_id})
        cache_path = self.cache_dir / f"{cache_key}.png"
        
        shutil.copy(asset_path, cache_path)
        self.index[element_id] = str(cache_path)
        self.save_index()

class ParallelExecutor:
    """Execute generation tasks in parallel"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def generate_parallel(self, elements: List[Dict], generator_func) -> Dict:
        """Generate multiple elements in parallel"""
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_element = {
                executor.submit(generator_func, elem): elem 
                for elem in elements
            }
            
            for future in as_completed(future_to_element):
                element = future_to_element[future]
                try:
                    result = future.result()
                    results[element['id']] = result
                except Exception as e:
                    print(f"Failed to generate {element['id']}: {e}")
                    results[element['id']] = None
        
        return results
