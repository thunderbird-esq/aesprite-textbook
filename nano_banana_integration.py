#!/usr/bin/env python3
"""
nano_banana_integration.py - Image generation client for nano-banana
Team 4: AI Integration & Processing
"""

import argparse
import json
import logging
import os
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from PIL import Image

try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    logging.warning("tqdm not available, using basic progress")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class GenerationMetadata:
    """Metadata for generated assets"""

    element_id: str
    prompt_xml_path: str
    output_path: str
    timestamp: str
    generation_time: float
    dimensions: Tuple[int, int]
    validation_passed: bool
    error: Optional[str] = None


class NanoBananaClient:
    """
    Client for nano-banana image generation service.

    Handles single and batch image generation with validation and retry logic.
    """

    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        max_workers: int = 4,
        timeout: int = 300,
    ):
        """
        Initialize nano-banana client.

        Args:
            api_endpoint: API endpoint URL (or use NANO_BANANA_ENDPOINT env var)
            api_key: API key (or use NANO_BANANA_API_KEY env var)
            max_workers: Maximum parallel generation threads
            timeout: Request timeout in seconds
        """
        self.api_endpoint = api_endpoint or os.environ.get(
            "NANO_BANANA_ENDPOINT", "https://api.nano-banana.ai/v1/generate"
        )
        self.api_key = api_key or os.environ.get("NANO_BANANA_API_KEY")
        self.max_workers = max_workers
        self.timeout = timeout

        # Mock mode if no API key
        self.mock_mode = not self.api_key
        if self.mock_mode:
            logger.warning("No API key provided, using mock mode")

        logger.info("NanoBananaClient initialized (mock=%s)", self.mock_mode)

    def generate_asset(self, prompt_xml: str, output_path: str, max_retries: int = 3) -> bool:
        """
        Generate a single asset from XML prompt.

        Args:
            prompt_xml: Path to XML prompt file or XML string
            output_path: Where to save generated image
            max_retries: Maximum retry attempts on failure

        Returns:
            True if successful, False otherwise
        """
        # Parse XML prompt
        if Path(prompt_xml).exists():
            with open(prompt_xml, "r", encoding="utf-8") as f:
                xml_content = f.read()
        else:
            xml_content = prompt_xml

        # Extract parameters from XML
        try:
            root = ET.fromstring(xml_content)
            element_id_elem = root.find("element_id")
            positive_prompt_elem = root.find("positive_prompt")
            negative_prompt_elem = root.find("negative_prompt")

            if element_id_elem is None or element_id_elem.text is None:
                raise ValueError("Missing 'element_id' element in XML")
            if positive_prompt_elem is None or positive_prompt_elem.text is None:
                raise ValueError("Missing 'positive_prompt' element in XML")
            if negative_prompt_elem is None or negative_prompt_elem.text is None:
                raise ValueError("Missing 'negative_prompt' element in XML")

            element_id = element_id_elem.text
            positive_prompt = positive_prompt_elem.text
            negative_prompt = negative_prompt_elem.text

            dims = root.find(".//dimensions")
            if dims is None:
                width = 800
                height = 600
            else:
                width = int(dims.get("width", "800"))
                height = int(dims.get("height", "600"))
        except (ValueError, ET.ParseError) as e:
            logger.error("Failed to parse XML prompt: %s", e)
            return False

        logger.info("Generating asset: %s (%dx%d)", element_id, width, height)

        # Attempt generation with retries
        for attempt in range(max_retries):
            try:
                if self.mock_mode:
                    success = self._generate_mock_image(output_path, width, height, element_id)
                else:
                    success = self._call_api(
                        positive_prompt, negative_prompt, width, height, output_path
                    )

                if success:
                    # Validate generated image
                    if self._validate_generated_image(output_path, width, height):
                        logger.info("Successfully generated: %s", element_id)
                        return True
                    else:
                        logger.warning("Validation failed for %s", element_id)

            except Exception as e:
                logger.warning("Generation attempt %d failed: %s", attempt + 1, e)

            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.info("Retrying in %ds...", wait_time)
                time.sleep(wait_time)

        logger.error("Failed to generate %s after %d attempts", element_id, max_retries)
        return False

    def batch_generate(
        self, prompt_list: List[str], output_dir: str, metadata_file: Optional[str] = None
    ) -> Dict:
        """
        Generate multiple assets in parallel.

        Args:
            prompt_list: List of XML prompt file paths
            output_dir: Directory to save generated images
            metadata_file: Optional path to save generation metadata

        Returns:
            Dictionary with generation statistics
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        metadata: List[GenerationMetadata] = []
        stats = {
            "total": len(prompt_list),
            "success": 0,
            "failed": 0,
            "total_time": 0.0,
            "avg_generation_time": 0.0,
        }

        # Progress tracking
        if TQDM_AVAILABLE:
            progress = tqdm(total=len(prompt_list), desc="Generating assets")
        else:
            progress = None

        # Parallel generation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for prompt_path in prompt_list:
                # Determine output filename
                prompt_name = Path(prompt_path).stem
                output_file = output_path / f"{prompt_name}.png"

                future = executor.submit(
                    self._generate_with_timing, str(prompt_path), str(output_file)
                )
                futures[future] = (str(prompt_path), str(output_file))

            # Collect results
            for future in as_completed(futures):
                prompt_path_str, output_file_str = futures[future]

                try:
                    success, gen_time, dimensions, error = future.result()

                    # Extract element ID
                    with open(prompt_path_str, "r") as f:
                        root = ET.fromstring(f.read())
                        element_id_elem = root.find("element_id")
                        if element_id_elem is None or element_id_elem.text is None:
                            raise ValueError("Missing 'element_id' in XML")
                        element_id = element_id_elem.text

                    # Create metadata
                    meta = GenerationMetadata(
                        element_id=element_id,
                        prompt_xml_path=prompt_path_str,
                        output_path=output_file_str,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                        generation_time=gen_time,
                        dimensions=dimensions,
                        validation_passed=success,
                        error=error,
                    )
                    metadata.append(meta)

                    if success:
                        stats["success"] += 1
                        stats["total_time"] += gen_time
                    else:
                        stats["failed"] += 1

                except Exception as e:
                    logger.error("Unexpected error for %s: %s", prompt_path, e)
                    stats["failed"] += 1

                if progress:
                    progress.update(1)

        if progress:
            progress.close()

        # Save metadata
        if metadata_file:
            self._save_metadata(metadata, metadata_file)

        # Calculate statistics
        if stats["success"] > 0:
            stats["avg_generation_time"] = stats["total_time"] / stats["success"]

        logger.info("Batch complete: %d/%d successful", stats["success"], stats["total"])

        return stats

    def _generate_with_timing(self, prompt_xml: str, output_path: str) -> Tuple:
        """
        Generate asset with timing information.

        Returns:
            Tuple of (success, generation_time, dimensions, error)
        """
        start_time = time.time()
        error = None

        try:
            success = self.generate_asset(prompt_xml, output_path)
            generation_time = time.time() - start_time

            if success:
                # Get dimensions
                img = Image.open(output_path)
                dimensions = img.size
                img.close()
            else:
                dimensions = (0, 0)
                error = "Generation failed"

        except Exception as e:
            success = False
            generation_time = time.time() - start_time
            dimensions = (0, 0)
            error = str(e)

        return success, generation_time, dimensions, error

    def _call_api(
        self, positive_prompt: str, negative_prompt: str, width: int, height: int, output_path: str
    ) -> bool:
        """
        Call nano-banana API to generate image.

        Args:
            positive_prompt: Positive prompt text
            negative_prompt: Negative prompt text
            width: Image width
            height: Image height
            output_path: Where to save image

        Returns:
            True if successful
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
        }

        try:
            response = requests.post(
                self.api_endpoint, headers=headers, json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                # Save image
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                logger.error("API error %d: %s", response.status_code, response.text)
                return False

        except Exception as e:
            logger.error("API call failed: %s", e)
            return False

    def _generate_mock_image(
        self, output_path: str, width: int, height: int, element_id: str
    ) -> bool:
        """
        Generate a mock image for testing.

        Args:
            output_path: Where to save image
            width: Image width
            height: Image height
            element_id: Element identifier

        Returns:
            True if successful
        """
        from PIL import ImageDraw

        try:
            # Create a colorful test pattern
            img = Image.new("RGB", (width, height), color="#F8F3E5")

            # Add some visual elements
            draw = ImageDraw.Draw(img)

            # Draw border
            draw.rectangle([(0, 0), (width - 1, height - 1)], outline="#000000", width=4)

            # Add diagonal lines for visual interest
            draw.line([(0, 0), (width, height)], fill="#FF6600", width=2)
            draw.line([(width, 0), (0, height)], fill="#0066FF", width=2)

            # Add element ID text
            try:
                # Try to use a basic font, fall back to default
                draw.text(
                    (width // 2, height // 2), f"MOCK: {element_id}", fill="#000000", anchor="mm"
                )
            except (OSError, FileNotFoundError):
                # Font not available, skip text
                pass

            # Save image
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "PNG")

            logger.debug("Generated mock image: %s", output_path)
            return True

        except Exception as e:
            logger.error("Mock generation failed: %s", e)
            return False

    def _validate_generated_image(
        self, image_path: str, expected_width: int, expected_height: int
    ) -> bool:
        """
        Validate a generated image.

        Args:
            image_path: Path to image file
            expected_width: Expected width in pixels
            expected_height: Expected height in pixels

        Returns:
            True if validation passes
        """
        try:
            if not Path(image_path).exists():
                logger.error("Image file not found: %s", image_path)
                return False

            img = Image.open(image_path)

            # Check dimensions
            if img.size != (expected_width, expected_height):
                logger.warning(
                    "Dimension mismatch: got %s, expected (%d, %d)",
                    img.size,
                    expected_width,
                    expected_height,
                )
                # Allow small variance
                width_diff = abs(img.width - expected_width)
                height_diff = abs(img.height - expected_height)
                if max(width_diff, height_diff) > 10:
                    return False

            # Check transparency (should have alpha channel)
            if img.mode not in ["RGBA", "LA", "P"]:
                logger.warning("Image missing transparency: %s", img.mode)

            # Check file isn't corrupted
            img.verify()

            img.close()
            return True

        except Exception as e:
            logger.error("Image validation failed: %s", e)
            return False

    def _save_metadata(self, metadata: List[GenerationMetadata], output_file: str):
        """Save generation metadata to JSON file"""
        try:
            metadata_dict = {
                "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_assets": len(metadata),
                "assets": [
                    {
                        "element_id": m.element_id,
                        "prompt_xml": m.prompt_xml_path,
                        "output_path": m.output_path,
                        "timestamp": m.timestamp,
                        "generation_time": m.generation_time,
                        "dimensions": m.dimensions,
                        "validation_passed": m.validation_passed,
                        "error": m.error,
                    }
                    for m in metadata
                ],
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, indent=2)

            logger.info("Metadata saved to %s", output_file)

        except Exception as e:
            logger.error("Failed to save metadata: %s", e)


def main():
    """CLI interface for nano-banana integration"""
    parser = argparse.ArgumentParser(description="Generate images using nano-banana API")
    parser.add_argument("--prompt", help="Path to single XML prompt file")
    parser.add_argument("--prompt-dir", help="Directory containing multiple XML prompts")
    parser.add_argument("--output", help="Output path for single image")
    parser.add_argument("--output-dir", help="Output directory for batch generation")
    parser.add_argument("--api-endpoint", help="API endpoint URL")
    parser.add_argument("--api-key", help="API key (or use NANO_BANANA_API_KEY env var)")
    parser.add_argument(
        "--max-workers", type=int, default=4, help="Maximum parallel workers for batch generation"
    )
    parser.add_argument("--metadata", help="Path to save generation metadata JSON")

    args = parser.parse_args()

    # Initialize client
    client = NanoBananaClient(
        api_endpoint=args.api_endpoint, api_key=args.api_key, max_workers=args.max_workers
    )

    # Single or batch mode
    if args.prompt and args.output:
        # Single generation
        logger.info("Generating single asset from %s", args.prompt)
        success = client.generate_asset(args.prompt, args.output)

        if success:
            print(f"✓ Generated: {args.output}")
            return 0
        else:
            print("✗ Failed to generate asset")
            return 1

    elif args.prompt_dir and args.output_dir:
        # Batch generation
        prompt_files = list(Path(args.prompt_dir).glob("*.xml"))
        logger.info("Found %d prompts in %s", len(prompt_files), args.prompt_dir)

        if not prompt_files:
            print(f"✗ No XML prompts found in {args.prompt_dir}")
            return 1

        stats = client.batch_generate(
            [str(p) for p in prompt_files], args.output_dir, metadata_file=args.metadata
        )

        print("\n✓ Batch generation complete:")
        print(f"  Total: {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Failed: {stats['failed']}")
        if stats["avg_generation_time"] > 0:
            print(f"  Avg time: {stats['avg_generation_time']:.2f}s")

        return 0 if stats["success"] > 0 else 1

    else:
        parser.print_help()
        print("\nError: Must specify either:")
        print("  --prompt and --output for single generation")
        print("  --prompt-dir and --output-dir for batch generation")
        return 1


if __name__ == "__main__":
    exit(main())
