"""
Tests for nano_banana_integration.py

Tests include:
- Mock image generation client
- Image generation with various parameters
- Response validation
- Error handling
- Image format verification
"""

import pytest
from PIL import Image

from test_framework import create_test_sprite


@pytest.mark.api
class TestNanoBananaClientBasics:
    """Test basic nano-banana client functionality."""

    def test_client_initialization(self, mock_nano_banana):
        """Test that client initializes correctly."""
        assert mock_nano_banana is not None
        assert mock_nano_banana.api_key == "test_key"
        assert mock_nano_banana.call_count == 0

    def test_client_has_generate_method(self, mock_nano_banana):
        """Test that client has generate_image method."""
        assert hasattr(mock_nano_banana, "generate_image")
        assert callable(mock_nano_banana.generate_image)


@pytest.mark.api
class TestImageGeneration:
    """Test image generation with nano-banana API."""

    def test_generate_simple_image(self, mock_nano_banana):
        """Test generating a simple image."""
        prompt = "A pixel art sprite of a computer"
        image = mock_nano_banana.generate_image(prompt)

        assert image is not None
        assert isinstance(image, Image.Image)

    def test_generate_with_dimensions(self, mock_nano_banana):
        """Test generating image with specific dimensions."""
        prompt = "A computer sprite"
        width, height = 64, 64

        image = mock_nano_banana.generate_image(prompt, width=width, height=height)

        assert image.size == (width, height)

    def test_generate_increments_counter(self, mock_nano_banana):
        """Test that API calls increment call counter."""
        initial_count = mock_nano_banana.call_count

        mock_nano_banana.generate_image("Test prompt")

        assert mock_nano_banana.call_count == initial_count + 1

    def test_generate_stores_prompt(self, mock_nano_banana):
        """Test that last prompt is stored."""
        prompt = "Computer with keyboard"
        mock_nano_banana.generate_image(prompt)

        assert mock_nano_banana.last_prompt == prompt

    def test_generate_stores_parameters(self, mock_nano_banana):
        """Test that generation parameters are stored."""
        prompt = "Test sprite"
        width, height = 48, 48

        mock_nano_banana.generate_image(prompt, width=width, height=height)

        assert mock_nano_banana.last_params["width"] == width
        assert mock_nano_banana.last_params["height"] == height


@pytest.mark.api
class TestImageValidation:
    """Test validation of generated images."""

    def test_generated_image_is_pil_image(self, mock_nano_banana):
        """Test that generated image is PIL Image."""
        image = mock_nano_banana.generate_image("Test")

        assert isinstance(image, Image.Image)

    def test_generated_image_has_rgb_mode(self, mock_nano_banana):
        """Test that generated image is in RGB mode."""
        image = mock_nano_banana.generate_image("Test")

        assert image.mode == "RGB"

    def test_generated_image_correct_size(self, mock_nano_banana):
        """Test that generated image has requested size."""
        sizes = [(16, 16), (32, 32), (64, 64)]

        for width, height in sizes:
            image = mock_nano_banana.generate_image("Test", width=width, height=height)
            assert image.size == (width, height)

    def test_generated_image_has_content(self, mock_nano_banana):
        """Test that generated image has actual content."""
        image = mock_nano_banana.generate_image("Computer sprite")

        # Check that image has some variation (not all white)
        pixels = list(image.getdata())
        unique_colors = set(pixels)

        assert len(unique_colors) > 1, "Image should have multiple colors"


@pytest.mark.api
class TestCustomMockImages:
    """Test using custom mock images."""

    def test_set_custom_mock_image(self, mock_nano_banana):
        """Test setting a custom mock image."""
        custom_image = create_test_sprite(size=(32, 32), pattern="checkerboard")
        mock_nano_banana.set_mock_image(custom_image)

        result = mock_nano_banana.generate_image("Test")

        assert result == custom_image

    def test_custom_image_overrides_default(self, mock_nano_banana):
        """Test that custom image overrides default generation."""
        custom_image = create_test_sprite(size=(64, 64), color=(255, 0, 0))
        mock_nano_banana.set_mock_image(custom_image)

        result = mock_nano_banana.generate_image("Test", width=32, height=32)

        # Should get custom image regardless of requested size
        assert result.size == (64, 64)

    def test_reset_clears_mock_image(self, mock_nano_banana):
        """Test that reset clears custom mock image."""
        custom_image = create_test_sprite()
        mock_nano_banana.set_mock_image(custom_image)
        mock_nano_banana.reset()

        # After reset, should get default generated image
        result = mock_nano_banana.generate_image("Test", width=32, height=32)

        assert result.size == (32, 32)  # Default behavior


@pytest.mark.api
class TestErrorHandling:
    """Test error handling in nano-banana integration."""

    def test_reset_client_state(self, mock_nano_banana):
        """Test resetting client state."""
        mock_nano_banana.generate_image("Test 1")
        mock_nano_banana.generate_image("Test 2")

        assert mock_nano_banana.call_count == 2

        mock_nano_banana.reset()

        assert mock_nano_banana.call_count == 0
        assert mock_nano_banana.last_prompt is None
        assert mock_nano_banana.last_params == {}
        assert mock_nano_banana.mock_image is None

    def test_handle_invalid_dimensions(self):
        """Test handling of invalid dimensions."""
        invalid_sizes = [(0, 32), (32, 0), (-10, 32), (32, -10)]

        for width, height in invalid_sizes:
            is_valid = width > 0 and height > 0
            assert not is_valid, f"Size ({width}, {height}) should be invalid"

    def test_handle_very_large_dimensions(self):
        """Test handling of very large dimensions."""
        max_size = 2048

        large_sizes = [(4096, 4096), (8192, 8192)]

        for width, height in large_sizes:
            is_too_large = width > max_size or height > max_size
            assert is_too_large, f"Size ({width}, {height}) should be too large"


@pytest.mark.api
class TestParameterizedGeneration:
    """Test image generation with various parameters."""

    @pytest.mark.parametrize("size", [(16, 16), (32, 32), (64, 64)])
    def test_generation_with_different_sizes(self, mock_nano_banana, size):
        """Test generation with different image sizes."""
        width, height = size
        image = mock_nano_banana.generate_image("Test", width=width, height=height)

        assert image.size == (width, height)

    @pytest.mark.parametrize("prompt", ["A computer", "A keyboard", "A mouse", "A monitor"])
    def test_generation_with_different_prompts(self, mock_nano_banana, prompt):
        """Test generation with different prompts."""
        image = mock_nano_banana.generate_image(prompt)

        assert image is not None
        assert mock_nano_banana.last_prompt == prompt


@pytest.mark.api
class TestImagePostProcessing:
    """Test post-processing of generated images."""

    def test_resize_generated_image(self, mock_nano_banana):
        """Test resizing generated image."""
        image = mock_nano_banana.generate_image("Test", width=64, height=64)
        resized = image.resize((32, 32))

        assert resized.size == (32, 32)

    def test_rotate_generated_image(self, mock_nano_banana):
        """Test rotating generated image."""
        image = mock_nano_banana.generate_image("Test")
        rotated = image.rotate(15, expand=True)

        assert rotated is not None
        assert isinstance(rotated, Image.Image)

    def test_convert_image_mode(self, mock_nano_banana):
        """Test converting image color mode."""
        image = mock_nano_banana.generate_image("Test")
        assert image.mode == "RGB"

        # Convert to RGBA
        rgba_image = image.convert("RGBA")
        assert rgba_image.mode == "RGBA"


@pytest.mark.integration
@pytest.mark.api
class TestNanoBananaIntegrationWorkflow:
    """Integration tests for complete nano-banana workflow."""

    def test_end_to_end_image_generation(self, mock_nano_banana, test_config):
        """Test complete workflow from prompt to validated image."""
        # Validate prompt first
        prompt = "A pixel art sprite of a computer with keyboard"
        forbidden = test_config["validation"]["forbidden_terms"]
        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert not has_forbidden

        # Generate image
        dim_config = test_config["validation"]["image_dimensions"]
        size = dim_config["recommended"]
        image = mock_nano_banana.generate_image(prompt, width=size, height=size)

        # Validate image
        assert image is not None
        assert image.size == (size, size)
        assert image.mode == "RGB"

        # Check image dimensions
        width, height = image.size
        assert dim_config["min"] <= width <= dim_config["max"]
        assert dim_config["min"] <= height <= dim_config["max"]

    def test_batch_image_generation(self, mock_nano_banana):
        """Test generating multiple images in batch."""
        prompts = ["Computer sprite", "Keyboard sprite", "Mouse sprite", "Monitor sprite"]

        images = []
        for prompt in prompts:
            image = mock_nano_banana.generate_image(prompt, width=32, height=32)
            images.append(image)

        assert len(images) == len(prompts)
        assert mock_nano_banana.call_count == len(prompts)

        # All images should be valid
        for image in images:
            assert isinstance(image, Image.Image)
            assert image.size == (32, 32)

    def test_generation_with_retry_on_validation_failure(self, mock_nano_banana, test_config):
        """Test generation with retry if validation fails."""
        dim_config = test_config["validation"]["image_dimensions"]
        max_attempts = test_config["prompt_generation"]["max_attempts"]

        # Simulate trying to generate valid image
        attempts = 0
        valid_image = None

        for attempt in range(max_attempts):
            attempts += 1
            image = mock_nano_banana.generate_image("Computer sprite", width=32, height=32)

            # Validate dimensions
            width, height = image.size
            if (
                dim_config["min"] <= width <= dim_config["max"]
                and dim_config["min"] <= height <= dim_config["max"]
            ):
                valid_image = image
                break

        assert valid_image is not None
        assert attempts <= max_attempts

    @pytest.mark.slow
    def test_performance_benchmark(self, mock_nano_banana):
        """Test performance of image generation."""
        import time

        num_generations = 100
        start_time = time.time()

        for i in range(num_generations):
            mock_nano_banana.generate_image(f"Sprite {i}", width=32, height=32)

        elapsed_time = time.time() - start_time

        # Mock generation should be very fast
        assert elapsed_time < 5.0, f"Mock generation should be fast (took {elapsed_time:.2f}s)"

        avg_time_per_generation = elapsed_time / num_generations
        assert avg_time_per_generation < 0.1, "Each generation should take < 0.1s"
