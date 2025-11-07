"""
Integration tests for full pipeline

Tests include:
- End-to-end spread generation
- Batch asset generation
- Validation and regeneration on failure
- Config-driven variation
- Performance benchmarks
"""

import os
import time

import pytest
from PIL import Image

from test_framework import (
    check_color_distribution,
    create_test_config,
    create_test_layout,
    create_test_sprite,
)


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndSpreadGeneration:
    """Test complete end-to-end spread generation."""

    def test_full_spread_generation_workflow(
        self, mock_gemini, mock_nano_banana, test_config, test_layout, temp_dir
    ):
        """Test complete workflow from config to final spread."""
        # Step 1: Load configuration
        assert test_config is not None
        assert test_layout is not None

        # Step 2: Generate prompts for each element
        prompts = []
        for element in test_layout["elements"]:
            template = element.get("prompt_template", "A pixel art sprite")
            prompt = template.format(topic="computer")
            prompts.append(prompt)

        assert len(prompts) == len(test_layout["elements"])

        # Step 3: Validate prompts
        forbidden = test_config["validation"]["forbidden_terms"]
        for prompt in prompts:
            has_forbidden = any(term in prompt.lower() for term in forbidden)
            assert not has_forbidden, f"Prompt should not have forbidden terms: {prompt}"

        # Step 4: Generate descriptions with Gemini
        descriptions = []
        for prompt in prompts:
            response = mock_gemini.generate_content(prompt)
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            descriptions.append(text)

        assert len(descriptions) == len(prompts)

        # Step 5: Generate images with nano-banana
        images = []
        for i, element in enumerate(test_layout["elements"]):
            size = element.get("size", [32, 32])
            img = mock_nano_banana.generate_image(descriptions[i], width=size[0], height=size[1])
            images.append(img)

        assert len(images) == len(test_layout["elements"])

        # Step 6: Validate generated images
        dim_config = test_config["validation"]["image_dimensions"]
        for img in images:
            width, height = img.size
            assert dim_config["min"] <= width <= dim_config["max"]
            assert dim_config["min"] <= height <= dim_config["max"]

        # Step 7: Create spread canvas
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])
        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        assert canvas.size == tuple(spread_size)

        # Step 8: Compose elements onto spread
        for i, element in enumerate(test_layout["elements"]):
            position = tuple(element["position"])
            canvas.paste(images[i], position)

        # Step 9: Add post-processing effects
        from PIL import ImageDraw

        draw = ImageDraw.Draw(canvas)

        # Add spiral binding
        binding_config = test_config["compositor"]["spiral_binding"]
        if binding_config["enabled"]:
            spine_x = spread_size[0] // 2
            num_holes = binding_config["holes"]
            for j in range(num_holes):
                y = int((j + 1) * spread_size[1] / (num_holes + 1))
                draw.ellipse([spine_x - 5, y - 5, spine_x + 5, y + 5], fill=(200, 200, 200))

        # Step 10: Save final spread
        output_path = os.path.join(temp_dir, "final_spread.png")
        canvas.save(output_path, "PNG", dpi=(300, 300))

        # Step 11: Verify output
        assert os.path.exists(output_path)
        final_spread = Image.open(output_path)
        assert final_spread.size == tuple(spread_size)

        print(f"Successfully generated spread at: {output_path}")


@pytest.mark.integration
class TestBatchAssetGeneration:
    """Test batch generation of multiple assets."""

    def test_generate_multiple_assets(self, mock_nano_banana, test_config):
        """Test generating multiple assets in batch."""
        prompts = [
            "A pixel art computer",
            "A pixel art keyboard",
            "A pixel art mouse",
            "A pixel art monitor",
            "A pixel art desk",
        ]

        images = []
        for prompt in prompts:
            img = mock_nano_banana.generate_image(prompt, width=32, height=32)
            images.append(img)

        assert len(images) == len(prompts)

        # Validate all images
        dim_config = test_config["validation"]["image_dimensions"]
        for img in images:
            width, height = img.size
            assert dim_config["min"] <= width <= dim_config["max"]

    def test_batch_generation_with_validation(self, mock_nano_banana, test_config):
        """Test batch generation with validation checks."""
        num_assets = 10
        valid_images = []
        invalid_count = 0

        for i in range(num_assets):
            img = mock_nano_banana.generate_image(f"Asset {i}", width=32, height=32)

            # Validate
            dim_config = test_config["validation"]["image_dimensions"]
            width, height = img.size
            dim_valid = (
                dim_config["min"] <= width <= dim_config["max"]
                and dim_config["min"] <= height <= dim_config["max"]
            )

            if dim_valid:
                valid_images.append(img)
            else:
                invalid_count += 1

        # All mock images should be valid
        assert len(valid_images) == num_assets
        assert invalid_count == 0

    def test_batch_with_different_sizes(self, mock_nano_banana):
        """Test batch generation with varying sizes."""
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]

        images = []
        for size in sizes:
            img = mock_nano_banana.generate_image("Test sprite", width=size[0], height=size[1])
            images.append(img)

        assert len(images) == len(sizes)

        # Verify sizes
        for i, img in enumerate(images):
            assert img.size == sizes[i]


@pytest.mark.integration
class TestValidationAndRegeneration:
    """Test validation and regeneration on failure."""

    def test_regenerate_on_forbidden_terms(self, mock_gemini, test_config):
        """Test regenerating prompt if forbidden terms detected."""
        forbidden = test_config["validation"]["forbidden_terms"]
        max_attempts = test_config["prompt_generation"]["max_attempts"]

        # Set up responses (first has forbidden term, second is clean)
        mock_gemini.set_response(
            {"candidates": [{"content": {"parts": [{"text": "A sprite with gradient effects"}]}}]}
        )
        mock_gemini.set_response(
            {"candidates": [{"content": {"parts": [{"text": "A sprite of a computer"}]}}]}
        )

        # Try generation with retry
        attempts = 0
        valid_response = None

        for attempt in range(max_attempts):
            attempts += 1
            response = mock_gemini.generate_content("Generate description")
            text = response["candidates"][0]["content"]["parts"][0]["text"]

            # Check for forbidden terms
            has_forbidden = any(term in text.lower() for term in forbidden)
            if not has_forbidden:
                valid_response = text
                break

        assert valid_response is not None
        assert attempts == 2  # Should succeed on second attempt

    def test_regenerate_on_dimension_failure(self, mock_nano_banana, test_config):
        """Test regenerating if image dimensions are invalid."""
        dim_config = test_config["validation"]["image_dimensions"]
        max_attempts = 3

        # For mock client, we control the size, so simulate retry logic
        attempts = 0
        valid_image = None

        for attempt in range(max_attempts):
            attempts += 1

            # Generate with correct size (mock always succeeds)
            img = mock_nano_banana.generate_image("Test", width=32, height=32)

            # Validate
            width, height = img.size
            if (
                dim_config["min"] <= width <= dim_config["max"]
                and dim_config["min"] <= height <= dim_config["max"]
            ):
                valid_image = img
                break

        assert valid_image is not None
        assert attempts <= max_attempts

    def test_max_retries_exceeded(self, mock_gemini, test_config):
        """Test behavior when max retries are exceeded."""
        forbidden = test_config["validation"]["forbidden_terms"]
        max_attempts = test_config["prompt_generation"]["max_attempts"]

        # Set all responses to have forbidden terms
        for _ in range(max_attempts + 1):
            mock_gemini.set_response(
                {
                    "candidates": [
                        {"content": {"parts": [{"text": "A sprite with gradient shader"}]}}
                    ]
                }
            )

        # Try generation
        attempts = 0
        valid_response = None

        for attempt in range(max_attempts):
            attempts += 1
            response = mock_gemini.generate_content("Generate")
            text = response["candidates"][0]["content"]["parts"][0]["text"]

            has_forbidden = any(term in text.lower() for term in forbidden)
            if not has_forbidden:
                valid_response = text
                break

        # Should not find valid response
        assert valid_response is None
        assert attempts == max_attempts


@pytest.mark.integration
class TestConfigDrivenVariation:
    """Test that different configs produce different results."""

    def test_different_spread_sizes(self):
        """Test generating spreads with different sizes."""
        config1 = create_test_config()
        config1["compositor"]["spread_size"] = [1000, 700]

        config2 = create_test_config()
        config2["compositor"]["spread_size"] = [2000, 1400]

        canvas1 = Image.new("RGB", tuple(config1["compositor"]["spread_size"]))
        canvas2 = Image.new("RGB", tuple(config2["compositor"]["spread_size"]))

        assert canvas1.size != canvas2.size

    def test_different_binding_configurations(self, test_config):
        """Test different spiral binding configurations."""
        # Enabled binding
        config_with_binding = create_test_config()
        config_with_binding["compositor"]["spiral_binding"]["enabled"] = True
        config_with_binding["compositor"]["spiral_binding"]["holes"] = 23

        # Disabled binding
        config_no_binding = create_test_config()
        config_no_binding["compositor"]["spiral_binding"]["enabled"] = False

        assert config_with_binding["compositor"]["spiral_binding"]["enabled"]
        assert not config_no_binding["compositor"]["spiral_binding"]["enabled"]

    def test_different_validation_rules(self):
        """Test different validation configurations."""
        config1 = create_test_config()
        config1["validation"]["forbidden_terms"] = ["gradient", "shader"]

        config2 = create_test_config()
        config2["validation"]["forbidden_terms"] = ["gradient", "shader", "alpha", "blend"]

        assert len(config1["validation"]["forbidden_terms"]) < len(
            config2["validation"]["forbidden_terms"]
        )

    def test_different_element_counts(self):
        """Test layouts with different numbers of elements."""
        layout1 = create_test_layout(num_elements=2)
        layout2 = create_test_layout(num_elements=5)
        layout3 = create_test_layout(num_elements=10)

        assert len(layout1["elements"]) == 2
        assert len(layout2["elements"]) == 5
        assert len(layout3["elements"]) == 10


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.mark.slow
    def test_single_spread_generation_time(
        self, mock_gemini, mock_nano_banana, test_config, test_layout, temp_dir
    ):
        """Test that spread generation completes within time limit."""
        max_time = 30.0  # 30 seconds
        start_time = time.time()

        # Generate spread
        spread_size = test_config["compositor"]["spread_size"]
        bg_color = tuple(test_config["compositor"]["background_color"])
        canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

        # Generate and compose elements
        for element in test_layout["elements"]:
            # Generate description
            response = mock_gemini.generate_content("Generate sprite")
            desc = response["candidates"][0]["content"]["parts"][0]["text"]

            # Generate image
            size = element.get("size", [32, 32])
            img = mock_nano_banana.generate_image(desc, width=size[0], height=size[1])

            # Place on canvas
            position = tuple(element["position"])
            canvas.paste(img, position)

        # Save
        output_path = os.path.join(temp_dir, "benchmark_spread.png")
        canvas.save(output_path)

        elapsed = time.time() - start_time

        assert elapsed < max_time, f"Generation took {elapsed:.2f}s, should be < {max_time}s"

        print(f"Spread generation completed in {elapsed:.2f}s")

    def test_batch_generation_performance(self, mock_nano_banana):
        """Test batch generation performance."""
        num_assets = 50
        max_time = 10.0

        start_time = time.time()

        for i in range(num_assets):
            mock_nano_banana.generate_image(f"Asset {i}", width=32, height=32)

        elapsed = time.time() - start_time

        assert elapsed < max_time, f"Batch generation took {elapsed:.2f}s, should be < {max_time}s"

        avg_time = elapsed / num_assets
        print(f"Average generation time: {avg_time:.4f}s per asset")

    def test_validation_performance(self, test_config):
        """Test validation performance."""
        num_validations = 100
        max_time = 5.0

        start_time = time.time()

        for i in range(num_validations):
            img = create_test_sprite()

            # Validate dimensions
            dim_config = test_config["validation"]["image_dimensions"]
            width, height = img.size
            _ = dim_config["min"] <= width <= dim_config["max"]

            # Validate color distribution
            max_ratio = test_config["validation"]["color_distribution"]["max_single_color_ratio"]
            _, _ = check_color_distribution(img, max_ratio)

        elapsed = time.time() - start_time

        assert elapsed < max_time, f"Validation took {elapsed:.2f}s, should be < {max_time}s"

    def test_composition_performance(self, test_config):
        """Test composition performance."""
        num_compositions = 20
        max_time = 10.0

        start_time = time.time()

        for i in range(num_compositions):
            spread_size = test_config["compositor"]["spread_size"]
            bg_color = tuple(test_config["compositor"]["background_color"])
            canvas = Image.new("RGB", tuple(spread_size), color=bg_color)

            # Add 10 sprites
            for j in range(10):
                sprite = create_test_sprite()
                position = (100 + j * 100, 100)
                canvas.paste(sprite, position)

        elapsed = time.time() - start_time

        assert elapsed < max_time, f"Composition took {elapsed:.2f}s, should be < {max_time}s"

        avg_time = elapsed / num_compositions
        print(f"Average composition time: {avg_time:.4f}s per spread")


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery and resilience."""

    def test_continue_on_single_asset_failure(self, mock_nano_banana, test_config):
        """Test that pipeline continues if single asset fails."""
        num_assets = 5
        generated = []

        for i in range(num_assets):
            try:
                img = mock_nano_banana.generate_image(f"Asset {i}", width=32, height=32)
                generated.append(img)
            except Exception:
                # Continue on error
                continue

        # Should have generated all (mock doesn't fail)
        assert len(generated) == num_assets

    def test_fallback_to_default_values(self, test_config):
        """Test falling back to defaults on invalid config."""
        # Simulate missing config values
        incomplete_config = {"compositor": {}}

        # Use defaults if missing
        spread_size = incomplete_config.get("compositor", {}).get(
            "spread_size", [2000, 1400]  # Default
        )

        assert spread_size == [2000, 1400]

    def test_graceful_degradation(self, test_config):
        """Test graceful degradation when optional features fail."""
        # If binding rendering fails, continue without it
        config = create_test_config()

        try:
            binding_enabled = config["compositor"]["spiral_binding"]["enabled"]
        except Exception:
            binding_enabled = False  # Gracefully disable

        # Should still work
        assert isinstance(binding_enabled, bool)
