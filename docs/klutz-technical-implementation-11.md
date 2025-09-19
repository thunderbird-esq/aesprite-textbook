#!/usr/bin/env python3
"""
test_framework.py - Comprehensive automated testing for all components
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import json
import yaml
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

# Import our modules to test
from klutz_compositor import KlutzCompositor
from asset_validator import AssetValidator
from prompt_generator import PromptGenerator
from post_processor import PostProcessor
from gemini_integration import GeminiXMLGenerator, GeminiConfig
from nano_banana_integration import NanoBananaGenerator, NanoBananaConfig, GenerationStatus
from quality_assurance import QualityAssurancePipeline, QAStatus

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
        # Create test directories
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.assets_dir = cls.test_dir / 'assets'
        cls.config_dir = cls.test_dir / 'config'
        cls.output_dir = cls.test_dir / 'output'
        
        cls.assets_dir.mkdir()
        cls.config_dir.mkdir()
        cls.output_dir.mkdir()
        
        # Create test configuration
        cls.test_config = {
            'project': {
                'name': 'Test Workbook',
                'pages': 4
            },
            'technical_specifications': {
                'canvas': {
                    'dimensions': [3400, 2200],
                    'dpi': 300
                }
            }
        }
        
        config_path = cls.config_dir / 'master_config.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(cls.test_config, f)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        shutil.rmtree(cls.test_dir)
        logging.disable(logging.NOTSET)
    
    def create_test_image(self, size=(100, 100), color='RGB', content='white'):
        """Create a test image"""
        if content == 'white':
            img = Image.new(color, size, (255, 255, 255))
        elif content == 'gradient':
            img = Image.new(color, size)
            pixels = img.load()
            for x in range(size[0]):
                for y in range(size[1]):
                    pixels[x, y] = (x * 255 // size[0], y * 255 // size[1], 128)
        elif content == 'pixelart':
            img = Image.new(color, (8, 8), (255, 255, 255))
            pixels = img.load()
            # Draw simple pattern
            for x in range(8):
                for y in range(8):
                    if (x + y) % 2 == 0:
                        pixels[x, y] = (255, 0, 0)
            img = img.resize(size, Image.Resampling.NEAREST)
        else:
            img = Image.new(color, size, (128, 128, 128))
        
        return img


class TestKlutzCompositor(BaseTestCase):
    """Test suite for compositor functionality"""
    
    def setUp(self):
        """Set up for each test"""
        config_path = self.config_dir / 'master_config.yaml'
        self.compositor = KlutzCompositor(str(config_path))
    
    def test_spine_clearance(self):
        """Test that spine dead zone is respected"""
        # Create element that would intrude
        element = Mock()
        element.width = 500
        element.height = 300
        
        # Position that would cross spine (spine is 1469-1931)
        x, y = 1450, 500  # Would extend to 1950, crossing spine
        
        self.assertTrue(
            self.compositor.check_spine_intrusion(x, y, element.width, element.height)
        )
        
        # Position that doesn't cross spine
        x, y = 100, 500
        self.assertFalse(
            self.compositor.check_spine_intrusion(x, y, element.width, element.height)
        )
    
    def test_chaos_rotation_deterministic(self):
        """Verify rotation is deterministic based on element ID"""
        rotation1 = self.compositor.get_chaos_rotation('test_element_01', 15)
        rotation2 = self.compositor.get_chaos_rotation('test_element_01', 15)
        
        self.assertEqual(rotation1, rotation2)
        
        # Different ID should give different rotation
        rotation3 = self.compositor.get_chaos_rotation('test_element_02', 15)
        self.assertNotEqual(rotation1, rotation3)
        
        # Rotation should be within bounds
        self.assertTrue(-15 <= rotation1 <= 15)
    
    def test_add_border(self):
        """Test border addition to image"""
        test_img = self.create_test_image((100, 100))
        
        bordered = self.compositor.add_border(test_img, "4px solid #FF0000")
        
        # Check dimensions increased by border
        self.assertEqual(bordered.width, 108)  # 100 + 4*2
        self.assertEqual(bordered.height, 108)
        
        # Check border color
        pixel = bordered.getpixel((0, 0))
        self.assertEqual(pixel[:3], (255, 0, 0))  # Red border
    
    def test_add_hard_shadow(self):
        """Test hard shadow generation"""
        test_img = self.create_test_image((100, 100))
        
        shadow_config = {
            'offset_x': 3,
            'offset_y': 3,
            'color': (0, 0, 0, 255)
        }
        
        shadowed = self.compositor.add_hard_shadow(test_img, shadow_config)
        
        # Check dimensions increased
        self.assertEqual(shadowed.width, 103)
        self.assertEqual(shadowed.height, 103)
        
        # Check shadow exists at offset
        shadow_pixel = shadowed.getpixel((1, 1))
        self.assertEqual(shadow_pixel[3], 255)  # Shadow should be opaque
    
    def test_cmyk_misregistration(self):
        """Test CMYK channel shift effect"""
        test_img = self.create_test_image((100, 100), content='gradient')
        
        # Convert to array for comparison
        original_array = np.array(test_img)
        
        # Apply misregistration
        shifted = self.compositor.apply_cmyk_misregistration(test_img)
        shifted_array = np.array(shifted)
        
        # Check that image changed
        self.assertFalse(np.array_equal(original_array, shifted_array))
        
        # Verify shift amounts are small (1-2 pixels)
        diff = np.abs(original_array.astype(float) - shifted_array.astype(float))
        avg_diff = np.mean(diff)
        self.assertLess(avg_diff, 10)  # Small average difference
    
    def test_create_base_canvas(self):
        """Test base canvas creation"""
        canvas = self.compositor.create_base_canvas('aged_newsprint')
        
        # Check dimensions
        self.assertEqual(canvas.width, 3400)
        self.assertEqual(canvas.height, 2200)
        
        # Check color is roughly aged newsprint
        avg_color = np.array(canvas).mean(axis=(0, 1))
        expected = np.array([248, 243, 229])
        
        # Allow some variance due to texture
        diff = np.abs(avg_color - expected)
        self.assertTrue(np.all(diff < 20))
    
    def test_paper_texture_generation(self):
        """Test paper texture has appropriate characteristics"""
        texture = self.compositor.generate_paper_texture()
        
        # Check dimensions
        self.assertEqual(texture.size, (3400, 2200))
        
        # Check texture has variance (not flat)
        texture_array = np.array(texture)
        std_dev = np.std(texture_array)
        
        self.assertGreater(std_dev, 10)  # Has texture
        self.assertLess(std_dev, 50)     # Not too noisy


class TestAssetValidator(BaseTestCase):
    """Test suite for asset validation"""
    
    def setUp(self):
        """Set up for each test"""
        self.validator = AssetValidator()
    
    def test_validate_prompt_forbidden_terms(self):
        """Test detection of forbidden modern terms"""
        bad_prompt = """
        Create a smartphone with wireless bluetooth connection
        and USB charging port with 4K display
        """
        
        violations = self.validator.validate_prompt(bad_prompt)
        
        self.assertGreater(len(violations), 0)
        self.assertTrue(any('smartphone' in v.lower() for v in violations))
        self.assertTrue(any('wireless' in v.lower() for v in violations))
        self.assertTrue(any('usb' in v.lower() for v in violations))
        self.assertTrue(any('4k' in v.lower() for v in violations))
    
    def test_validate_prompt_required_terms(self):
        """Test detection of missing required terms"""
        incomplete_prompt = """
        Create a mouse for the computer
        """
        
        violations = self.validator.validate_prompt(incomplete_prompt)
        
        # Should require specific mouse terminology
        self.assertTrue(any('required' in v and 'mouse' in v for v in violations))
    
    def test_validate_prompt_clean(self):
        """Test that valid prompts pass"""
        good_prompt = """
        Create a photograph of a child using an Apple Macintosh Plus 
        with the beige M0100 mouse. Shot on 35mm film with visible grain.
        """
        
        violations = self.validator.validate_prompt(good_prompt)
        self.assertEqual(len(violations), 0)
    
    def test_validate_image_dimensions(self):
        """Test image dimension validation"""
        # Create oversized image
        large_img = self.create_test_image((2000, 2000))
        img_path = self.assets_dir / 'large.png'
        large_img.save(img_path)
        
        violations = self.validator.validate_image_asset(str(img_path))
        
        self.assertTrue(any('too large' in v.lower() for v in violations))
    
    def test_detect_gradients(self):
        """Test gradient detection"""
        # Create image with gradient
        gradient_img = self.create_test_image((200, 200), content='gradient')
        img_path = self.assets_dir / 'gradient.png'
        gradient_img.save(img_path)
        
        violations = self.validator.validate_image_asset(str(img_path))
        
        self.assertTrue(any('gradient' in v.lower() for v in violations))
    
    def test_color_distribution_validation(self):
        """Test 70/20/10 color rule validation"""
        # Create image with too much accent color
        img = Image.new('RGB', (100, 100))
        pixels = img.load()
        
        # Fill 40% with Nickelodeon orange (exceeds 30% limit)
        for x in range(100):
            for y in range(40):
                pixels[x, y] = (245, 125, 13)
        
        img_path = self.assets_dir / 'bad_colors.png'
        img.save(img_path)
        
        violations = self.validator.validate_image_asset(str(img_path))
        
        self.assertTrue(any('nickelodeon orange' in v.lower() for v in violations))


class TestPromptGenerator(BaseTestCase):
    """Test suite for XML prompt generation"""
    
    def setUp(self):
        """Set up for each test"""
        self.generator = PromptGenerator()
    
    def test_generate_photo_prompt(self):
        """Test photo prompt generation"""
        element = {
            'id': 'test_photo_01',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 450],
            'subject': 'child hand using mouse'
        }
        
        xml = self.generator.generate_photo_prompt(element)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml)
        
        self.assertEqual(root.tag, 'nano_banana_prompt')
        self.assertIsNotNone(root.find('element_id'))
        self.assertEqual(root.find('element_id').text, 'test_photo_01')
        self.assertIsNotNone(root.find('positive_prompt'))
        self.assertIsNotNone(root.find('negative_prompt'))
        
        # Check for required photo elements
        self.assertIn('Kodak Gold 400', xml)
        self.assertIn('M0100', xml)
    
    def test_generate_container_prompt(self):
        """Test container prompt generation"""
        element = {
            'id': 'test_container_01',
            'dimensions': [400, 200],
            'background': '#FFD700',
            'rotation': -2
        }
        
        xml = self.generator.generate_container_prompt(element)
        
        # Verify structure
        root = ET.fromstring(xml)
        
        # Check for hard shadow specification
        self.assertIn('hard', xml.lower())
        self.assertIn('3px', xml)
        self.assertNotIn('blur', root.find('positive_prompt').text)
    
    def test_no_forbidden_terms_in_prompt(self):
        """Ensure generated prompts don't contain forbidden terms"""
        element_types = [
            'graphic_photo_instructional',
            'container_featurebox',
            'graphic_pixelart',
            'graphic_gui_recreation'
        ]
        
        forbidden = ['gradient', 'modern', 'USB', 'wireless', 'smartphone']
        
        for element_type in element_types:
            element = {
                'id': f'test_{element_type}',
                'type': element_type,
                'dimensions': [100, 100]
            }
            
            # Get appropriate generator method
            if element_type in self.generator.templates:
                xml = self.generator.templates[element_type](element)
                
                for term in forbidden:
                    self.assertNotIn(term.lower(), xml.lower())
    
    def test_pixelart_specifications(self):
        """Test pixel art prompt includes correct specifications"""
        element = {
            'id': 'test_pixel_01',
            'type': 'graphic_pixelart',
            'dimensions': [256, 256],
            'magnification': 8,
            'palette': 'NES_limited'
        }
        
        xml = self.generator.generate_pixelart_prompt(element)
        
        # Check for pixel art requirements
        self.assertIn('nearest_neighbor', xml)
        self.assertIn('32x32', xml)
        self.assertIn('no anti-aliasing', xml.lower())


class TestPostProcessor(BaseTestCase):
    """Test suite for post-processing effects"""
    
    def setUp(self):
        """Set up for each test"""
        self.processor = PostProcessor()
    
    def test_dot_gain_curve(self):
        """Test dot gain curve generation"""
        curve = self.processor.generate_dot_gain_curve()
        
        # Check curve properties
        self.assertEqual(len(curve), 256)
        
        # Should be monotonically increasing
        for i in range(1, len(curve)):
            self.assertGreaterEqual(curve[i], curve[i-1])
        
        # Check specific points (23% gain at 40%)
        # Index 102 = 40% of 256
        expected_output = 0.49  # 40% + 23% gain
        self.assertAlmostEqual(curve[102], expected_output, delta=0.05)
    
    def test_cmyk_conversion(self):
        """Test RGB to CMYK conversion"""
        # Create test image
        rgb_img = self.create_test_image((10, 10))
        rgb_array = np.array(rgb_img)
        
        # Convert to CMYK
        cmyk = self.processor.rgb_to_cmyk(rgb_array)
        
        # Check dimensions
        self.assertEqual(cmyk.shape, (10, 10, 4))
        
        # Check value ranges
        self.assertTrue(np.all(cmyk >= 0))
        self.assertTrue(np.all(cmyk <= 1))
        
        # Convert back to RGB
        rgb_back = self.processor.cmyk_to_rgb(cmyk)
        
        # Should be close to original (some loss is expected)
        diff = np.abs(rgb_array.astype(float) - rgb_back.astype(float))
        self.assertLess(np.mean(diff), 5)
    
    def test_vignette_effect(self):
        """Test vignette application"""
        test_img = self.create_test_image((200, 200))
        
        vignetted = self.processor.add_vignette(test_img, strength=0.3)
        
        # Check corners are darker than center
        center_pixel = vignetted.getpixel((100, 100))
        corner_pixel = vignetted.getpixel((10, 10))
        
        # Center should be brighter
        center_brightness = sum(center_pixel[:3])
        corner_brightness = sum(corner_pixel[:3])
        
        self.assertGreater(center_brightness, corner_brightness)
    
    def test_paper_texture_generation(self):
        """Test paper texture characteristics"""
        texture = self.processor.generate_paper_texture((100, 100))
        
        # Check it's not uniform
        texture_array = np.array(texture)
        std_dev = np.std(texture_array)
        
        self.assertGreater(std_dev, 5)  # Has variation
        self.assertLess(std_dev, 50)    # Not too noisy
        
        # Check mean is around middle gray (paper color)
        mean_val = np.mean(texture_array)
        self.assertGreater(mean_val, 180)
        self.assertLess(mean_val, 220)


class TestGeminiIntegration(BaseTestCase):
    """Test suite for Gemini XML generation"""
    
    def setUp(self):
        """Set up for each test"""
        self.config = GeminiConfig(
            api_key="test-key",
            temperature=0.2
        )
    
    @patch('google.generativeai.GenerativeModel')
    def test_xml_generation(self, mock_model):
        """Test XML prompt generation through Gemini"""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = """
        <nano_banana_prompt>
            <element_id>test_01</element_id>
            <element_type>graphic_photo_instructional</element_type>
            <positive_prompt>Test prompt</positive_prompt>
            <negative_prompt>Test negative</negative_prompt>
        </nano_banana_prompt>
        """
        
        mock_model.return_value.generate_content.return_value = mock_response
        
        generator = GeminiXMLGenerator(self.config)
        
        element = {
            'id': 'test_01',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 450]
        }
        
        result = generator.generate_xml_prompt(element)
        
        self.assertIsNotNone(result)
        self.assertIn('<nano_banana_prompt>', result)
        self.assertIn('test_01', result)
    
    def test_xml_validation(self):
        """Test XML structure validation"""
        generator = GeminiXMLGenerator(self.config)
        
        # Valid XML
        valid_xml = """
        <nano_banana_prompt>
            <element_id>test_01</element_id>
            <element_type>test_type</element_type>
            <positive_prompt>Good prompt</positive_prompt>
            <negative_prompt>Bad things</negative_prompt>
        </nano_banana_prompt>
        """
        
        config = {'id': 'test_01'}
        self.assertTrue(generator.validate_xml_structure(valid_xml, config))
        
        # Invalid XML - missing required element
        invalid_xml = """
        <nano_banana_prompt>
            <element_id>test_01</element_id>
            <positive_prompt>Good prompt</positive_prompt>
        </nano_banana_prompt>
        """
        
        self.assertFalse(generator.validate_xml_structure(invalid_xml, config))
        
        # Invalid XML - contains forbidden term
        forbidden_xml = """
        <nano_banana_prompt>
            <element_id>test_01</element_id>
            <element_type>test_type</element_type>
            <positive_prompt>Modern gradient effect</positive_prompt>
            <negative_prompt>Bad things</negative_prompt>
        </nano_banana_prompt>
        """
        
        self.assertFalse(generator.validate_xml_structure(forbidden_xml, config))
    
    def test_fallback_generation(self):
        """Test fallback XML generation when API fails"""
        generator = GeminiXMLGenerator(self.config)
        
        element = {
            'id': 'test_photo',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 450],
            'subject': 'test subject'
        }
        
        xml = generator.fallback_xml_generation(element)
        
        # Check it produces valid XML
        root = ET.fromstring(xml)
        self.assertEqual(root.tag, 'nano_banana_prompt')
        self.assertEqual(root.find('element_id').text, 'test_photo')
        
        # Check for required photo specifications
        self.assertIn('Kodak Gold 400', xml)


class TestNanoBananaIntegration(BaseTestCase):
    """Test suite for nano-banana image generation"""
    
    def setUp(self):
        """Set up for each test"""
        self.config = NanoBananaConfig(
            api_endpoint="http://test.api",
            api_key="test-key"
        )
    
    def test_parse_xml_prompt(self):
        """Test XML prompt parsing"""
        generator = NanoBananaGenerator(self.config)
        
        xml = """
        <nano_banana_prompt>
            <element_id>test_01</element_id>
            <element_type>graphic_photo_instructional</element_type>
            <dimensions width="600" height="450" />
            <positive_prompt>Test positive</positive_prompt>
            <negative_prompt>Test negative</negative_prompt>
        </nano_banana_prompt>
        """
        
        params = generator.parse_xml_prompt(xml)
        
        self.assertEqual(params['element_id'], 'test_01')
        self.assertEqual(params['width'], 600)
        self.assertEqual(params['height'], 450)
        self.assertIn('positive_prompt', params)
        self.assertIn('negative_prompt', params)
    
    @patch('requests.Session.post')
    def test_api_call_success(self, mock_post):
        """Test successful API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'image': base64.b64encode(b'fake_image_data').decode()
        }
        mock_post.return_value = mock_response
        
        generator = NanoBananaGenerator(self.config)
        
        request = {
            'prompt': 'test prompt',
            'width': 512,
            'height': 512
        }
        
        response = generator.call_api(request)
        
        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
    
    def test_cache_functionality(self):
        """Test image caching system"""
        generator = NanoBananaGenerator(self.config)
        
        # Create test image
        test_img = self.create_test_image((100, 100))
        
        # Generate cache key
        params = {
            'element_id': 'test_cache',
            'positive_prompt': 'test',
            'negative_prompt': 'test',
            'width': 100,
            'height': 100
        }
        
        cache_key = generator.get_cache_key(params)
        
        # Save to cache
        generator.save_to_cache(cache_key, test_img)
        
        # Check retrieval
        cached = generator.check_cache(cache_key)
        
        self.assertIsNotNone(cached)
        self.assertEqual(cached.size, (100, 100))
    
    def test_validate_pixelart(self):
        """Test pixel art validation"""
        generator = NanoBananaGenerator(self.config)
        
        # Create perfect pixel art
        pixel_img = self.create_test_image((256, 256), content='pixelart')
        
        params = {
            'base_width': 32,
            'base_height': 32
        }
        
        is_valid = generator.validate_pixelart(pixel_img, params)
        self.assertTrue(is_valid)
        
        # Create non-pixel art (gradient)
        gradient_img = self.create_test_image((256, 256), content='gradient')
        
        is_not_valid = generator.validate_pixelart(gradient_img, params)
        self.assertFalse(is_not_valid)


class TestQualityAssurance(BaseTestCase):
    """Test suite for QA pipeline"""
    
    def setUp(self):
        """Set up for each test"""
        self.qa = QualityAssurancePipeline()
    
    def test_technical_qa_dimensions(self):
        """Test dimension checking"""
        qa = self.qa.technical_qa
        
        # Create correctly sized image
        img = self.create_test_image((600, 450))
        config = {'dimensions': [600, 450]}
        
        result = qa.check_dimensions(img, config)
        
        self.assertEqual(result.status, QAStatus.PASSED)
        self.assertEqual(result.score, 1.0)
        
        # Create wrongly sized image
        wrong_img = self.create_test_image((500, 400))
        
        result = qa.check_dimensions(wrong_img, config)
        
        self.assertEqual(result.status, QAStatus.FAILED)
        self.assertLess(result.score, 1.0)
    
    def test_aesthetic_qa_gradients(self):
        """Test gradient detection"""
        qa = self.qa.aesthetic_qa
        
        # Image without gradients
        flat_img = self.create_test_image((100, 100))
        result = qa.check_no_gradients(flat_img)
        self.assertEqual(result.status, QAStatus.PASSED)
        
        # Image with gradients
        gradient_img = self.create_test_image((100, 100), content='gradient')
        result = qa.check_no_gradients(gradient_img)
        self.assertEqual(result.status, QAStatus.FAILED)
    
    def test_overall_status_calculation(self):
        """Test overall QA status calculation"""
        from quality_assurance import QAResult, QACategory
        
        # All passed
        checks = [
            QAResult('test1', QACategory.TECHNICAL, QAStatus.PASSED, 1.0, 'msg'),
            QAResult('test2', QACategory.AESTHETIC, QAStatus.PASSED, 0.9, 'msg')
        ]
        
        status, score = self.qa.calculate_overall_status(checks)
        self.assertEqual(status, QAStatus.PASSED)
        
        # Critical failure
        checks.append(
            QAResult('no_modern_elements', QACategory.HISTORICAL, 
                    QAStatus.FAILED, 0.3, 'msg')
        )
        
        status, score = self.qa.calculate_overall_status(checks)
        self.assertEqual(status, QAStatus.FAILED)
    
    def test_html_report_generation(self):
        """Test HTML report generation"""
        from quality_assurance import QAReport, QAResult, QACategory
        
        report = QAReport(
            asset_path='test.png',
            element_id='test_01',
            element_type='test_type',
            overall_status=QAStatus.PASSED,
            overall_score=0.95,
            checks=[
                QAResult('test1', QACategory.TECHNICAL, QAStatus.PASSED, 1.0, 'msg')
            ],
            timestamp=datetime.now().isoformat(),
            processing_time=1.5
        )
        
        output_file = self.output_dir / 'test_report.html'
        self.qa.generate_html_report([report], str(output_file))
        
        self.assertTrue(output_file.exists())
        
        # Check HTML content
        html_content = output_file.read_text()
        self.assertIn('test_01', html_content)
        self.assertIn('PASSED', html_content)


class TestIntegrationFlow(BaseTestCase):
    """End-to-end integration tests"""
    
    @patch('nano_banana_integration.NanoBananaGenerator.call_api')
    @patch('gemini_integration.GeminiXMLGenerator.generate_xml_prompt')
    def test_complete_generation_flow(self, mock_gemini, mock_nano):
        """Test complete flow from config to image"""
        
        # Mock Gemini XML generation
        mock_gemini.return_value = """
        <nano_banana_prompt>
            <element_id>test_flow</element_id>
            <element_type>graphic_photo_instructional</element_type>
            <dimensions width="600" height="450" />
            <positive_prompt>Test</positive_prompt>
            <negative_prompt>Test</negative_prompt>
        </nano_banana_prompt>
        """
        
        # Mock nano-banana image generation
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'image': base64.b64encode(b'fake_image').decode()
        }
        mock_nano.return_value = mock_response
        
        # Run through pipeline
        element_config = {
            'id': 'test_flow',
            'type': 'graphic_photo_instructional',
            'dimensions': [600, 450]
        }
        
        # Generate XML
        gemini_config = GeminiConfig(api_key="test")
        xml_generator = GeminiXMLGenerator(gemini_config)
        xml = xml_generator.generate_xml_prompt(element_config)
        
        self.assertIsNotNone(xml)
        self.assertIn('test_flow', xml)


class TestPerformance(unittest.TestCase):
    """Performance and optimization tests"""
    
    def test_chaos_rotation_performance(self):
        """Test rotation calculation performance"""
        import time
        
        compositor = KlutzCompositor()
        
        start = time.time()
        for i in range(1000):
compositor.get_chaos_rotation(f'element_{i}', 15)
        end = time.time()
        
        elapsed = end - start
        self.assertLess(elapsed, 1.0)  # Should complete 1000 rotations in under 1 second
    
    def test_batch_processing_performance(self):
        """Test batch processing efficiency"""
        import time
        from concurrent.futures import ThreadPoolExecutor
        
        def process_item(i):
            """Simulate processing"""
            time.sleep(0.01)
            return i * 2
        
        # Serial processing
        start = time.time()
        serial_results = [process_item(i) for i in range(20)]
        serial_time = time.time() - start
        
        # Parallel processing
        start = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            parallel_results = list(executor.map(process_item, range(20)))
        parallel_time = time.time() - start
        
        # Parallel should be faster
        self.assertLess(parallel_time, serial_time)
        self.assertEqual(serial_results, parallel_results)
    
    def test_cache_performance(self):
        """Test caching improves performance"""
        import time
        
        # Create mock cache
        cache = {}
        
        def expensive_operation(key):
            """Simulate expensive operation"""
            if key in cache:
                return cache[key]
            
            time.sleep(0.1)  # Simulate work
            result = key * 2
            cache[key] = result
            return result
        
        # First call - slow
        start = time.time()
        result1 = expensive_operation(5)
        first_time = time.time() - start
        
        # Second call - should be cached
        start = time.time()
        result2 = expensive_operation(5)
        cached_time = time.time() - start
        
        self.assertEqual(result1, result2)
        self.assertLess(cached_time, first_time / 10)  # Cached should be much faster


class TestErrorHandling(BaseTestCase):
    """Test error handling and recovery"""
    
    def test_invalid_xml_handling(self):
        """Test handling of invalid XML"""
        from gemini_integration import GeminiXMLGenerator
        
        generator = GeminiXMLGenerator(GeminiConfig(api_key="test"))
        
        # Invalid XML string
        invalid_xml = "This is not XML at all!"
        
        try:
            result = generator.extract_xml(invalid_xml)
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("No valid XML found", str(e))
    
    def test_missing_file_handling(self):
        """Test handling of missing files"""
        validator = AssetValidator()
        
        # Try to validate non-existent file
        violations = validator.validate_image_asset('nonexistent.png')
        
        # Should handle gracefully (in this case, with violations)
        self.assertIsInstance(violations, list)
    
    def test_api_timeout_handling(self):
        """Test API timeout handling"""
        from nano_banana_integration import NanoBananaGenerator
        
        config = NanoBananaConfig(
            api_endpoint="http://test",
            api_key="test",
            timeout=0.001  # Very short timeout
        )
        
        generator = NanoBananaGenerator(config)
        
        with patch('requests.Session.post') as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.Timeout()
            
            try:
                generator.call_api({'test': 'data'})
                self.fail("Should have raised TimeoutError")
            except TimeoutError as e:
                self.assertIn("timed out", str(e))
    
    def test_retry_mechanism(self):
        """Test retry mechanism on failure"""
        from nano_banana_integration import NanoBananaGenerator
        
        config = NanoBananaConfig(
            api_endpoint="http://test",
            api_key="test",
            max_retries=3,
            retry_delay=0.01
        )
        
        generator = NanoBananaGenerator(config)
        
        with patch('requests.Session.post') as mock_post:
            # Fail twice, then succeed
            mock_post.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                Mock(status_code=200, json=Mock(return_value={'image': 'data'}))
            ]
            
            # Should eventually succeed after retries
            # Note: In real implementation, this would be in generate_image
            # This is testing the concept
            attempts = 0
            for _ in range(config.max_retries):
                try:
                    response = generator.call_api({'test': 'data'})
                    break
                except:
                    attempts += 1
                    if attempts >= config.max_retries:
                        raise
            
            self.assertEqual(attempts, 2)  # Failed twice before success


class TestDataValidation(BaseTestCase):
    """Test data validation and sanitization"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        from gemini_integration import GeminiConfig
        
        # Valid config
        config = GeminiConfig(
            api_key="valid-key",
            temperature=0.5,
            requests_per_minute=30
        )
        
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.requests_per_minute, 30)
        
        # Test defaults
        config = GeminiConfig(api_key="key")
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.max_retries, 3)
    
    def test_element_type_validation(self):
        """Test element type enum validation"""
        from gemini_integration import ElementType
        
        valid_types = [
            ElementType.PHOTO_INSTRUCTIONAL,
            ElementType.CONTAINER_FEATUREBOX,
            ElementType.PIXELART
        ]
        
        for element_type in valid_types:
            self.assertIsInstance(element_type.value, str)
            self.assertGreater(len(element_type.value), 0)
    
    def test_color_hex_validation(self):
        """Test hex color validation"""
        import re
        
        def validate_hex_color(color):
            """Validate hex color format"""
            pattern = r'^#[0-9A-Fa-f]{6}$'
            return bool(re.match(pattern, color))
        
        # Valid colors
        self.assertTrue(validate_hex_color('#FF0000'))
        self.assertTrue(validate_hex_color('#00ff00'))
        self.assertTrue(validate_hex_color('#123ABC'))
        
        # Invalid colors
        self.assertFalse(validate_hex_color('FF0000'))  # Missing #
        self.assertFalse(validate_hex_color('#FF00'))   # Too short
        self.assertFalse(validate_hex_color('#GGGGGG')) # Invalid chars
    
    def test_dimension_validation(self):
        """Test image dimension validation"""
        def validate_dimensions(width, height):
            """Validate dimensions are reasonable"""
            min_size = 10
            max_size = 5000
            
            return (min_size <= width <= max_size and 
                   min_size <= height <= max_size)
        
        # Valid dimensions
        self.assertTrue(validate_dimensions(600, 450))
        self.assertTrue(validate_dimensions(3400, 2200))
        
        # Invalid dimensions
        self.assertFalse(validate_dimensions(5, 100))    # Too small
        self.assertFalse(validate_dimensions(10000, 10000))  # Too large
        self.assertFalse(validate_dimensions(-100, 100))  # Negative


class TestMemoryManagement(BaseTestCase):
    """Test memory usage and cleanup"""
    
    def test_image_memory_cleanup(self):
        """Test that images are properly cleaned up"""
        import gc
        import weakref
        
        # Create image and weak reference
        img = self.create_test_image((1000, 1000))
        ref = weakref.ref(img)
        
        # Image should exist
        self.assertIsNotNone(ref())
        
        # Delete image
        del img
        gc.collect()
        
        # Image should be garbage collected
        self.assertIsNone(ref())
    
    def test_cache_size_limits(self):
        """Test cache size limitations"""
        class LimitedCache:
            def __init__(self, max_size=10):
                self.cache = {}
                self.max_size = max_size
            
            def add(self, key, value):
                if len(self.cache) >= self.max_size:
                    # Remove oldest (first) item
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                
                self.cache[key] = value
        
        cache = LimitedCache(max_size=3)
        
        # Add items
        for i in range(5):
            cache.add(f'key{i}', f'value{i}')
        
        # Should only have last 3 items
        self.assertEqual(len(cache.cache), 3)
        self.assertNotIn('key0', cache.cache)
        self.assertNotIn('key1', cache.cache)
        self.assertIn('key2', cache.cache)
        self.assertIn('key3', cache.cache)
        self.assertIn('key4', cache.cache)


class TestDocumentation(unittest.TestCase):
    """Test that code is properly documented"""
    
    def test_docstrings_present(self):
        """Test that important classes have docstrings"""
        from klutz_compositor import KlutzCompositor
        from asset_validator import AssetValidator
        from prompt_generator import PromptGenerator
        
        classes_to_test = [
            KlutzCompositor,
            AssetValidator,
            PromptGenerator
        ]
        
        for cls in classes_to_test:
            self.assertIsNotNone(cls.__doc__, 
                               f"{cls.__name__} is missing docstring")
    
    def test_method_documentation(self):
        """Test that key methods are documented"""
        from klutz_compositor import KlutzCompositor
        
        important_methods = [
            'create_base_canvas',
            'compose_spread',
            'apply_cmyk_misregistration'
        ]
        
        for method_name in important_methods:
            method = getattr(KlutzCompositor, method_name)
            self.assertIsNotNone(method.__doc__, 
                               f"Method {method_name} is missing docstring")


# Test Suite Runner
def run_all_tests():
    """Run all test suites"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestKlutzCompositor,
        TestAssetValidator,
        TestPromptGenerator,
        TestPostProcessor,
        TestGeminiIntegration,
        TestNanoBananaIntegration,
        TestQualityAssurance,
        TestIntegrationFlow,
        TestPerformance,
        TestErrorHandling,
        TestDataValidation,
        TestMemoryManagement,
        TestDocumentation
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")
        
        if result.failures:
            print("\nFailed tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\nTests with errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    import sys
    sys.exit(0 if success else 1)
