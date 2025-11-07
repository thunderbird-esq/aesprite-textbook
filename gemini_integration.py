#!/usr/bin/env python3
"""Integrate with Google Gemini API for prompt generation.

Integrate with Google Gemini API for prompt generation
Team 4: AI Integration & Processing
"""

import argparse
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml

try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google-generativeai not available, using mock mode")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1500
    retry_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0


class ResponseCache:
    """Cache for API responses to avoid duplicate calls."""

    def __init__(self, cache_dir: str = ".cache/gemini"):
        """Initialize the response cache.

        Args:
            cache_dir: Directory path for storing cached responses.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Response cache initialized at {self.cache_dir}")

    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> Optional[str]:
        """Retrieve cached response."""
        cache_key = self._get_cache_key(prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cached = json.load(f)
                # Check if cache is still valid (24 hours)
                cached_time = datetime.fromisoformat(cached["timestamp"])
                if datetime.now() - cached_time < timedelta(hours=24):
                    logger.debug("Cache hit for prompt hash %s", cache_key[:8])
                    response: str = cached["response"]
                    return response
                else:
                    logger.debug("Cache expired for %s", cache_key[:8])
            except Exception as e:
                logger.warning("Error reading cache: %s", e)

        return None

    def set(self, prompt: str, response: str):
        """Store response in cache."""
        cache_key = self._get_cache_key(prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "prompt_preview": prompt[:100],
                        "response": response,
                    },
                    f,
                    indent=2,
                )
            logger.debug("Cached response for %s", cache_key[:8])
        except Exception as e:
            logger.warning("Error writing cache: %s", e)


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, config: RateLimitConfig):
        """Initialize the rate limiter.

        Args:
            config: Rate limit configuration object.
        """
        self.config = config
        self.minute_calls: List[float] = []
        self.hour_calls: List[float] = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        current_time = time.time()

        # Clean old entries
        self.minute_calls = [t for t in self.minute_calls if current_time - t < 60]
        self.hour_calls = [t for t in self.hour_calls if current_time - t < 3600]

        # Check limits
        if len(self.minute_calls) >= self.config.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_calls[0])
            if wait_time > 0:
                logger.info("Rate limit: waiting {wait_time:.1f}s")
                time.sleep(wait_time)

        if len(self.hour_calls) >= self.config.requests_per_hour:
            wait_time = 3600 - (current_time - self.hour_calls[0])
            if wait_time > 0:
                logger.warning("Hourly rate limit: waiting {wait_time:.1f}s")
                time.sleep(wait_time)

        # Record this call
        current_time = time.time()
        self.minute_calls.append(current_time)
        self.hour_calls.append(current_time)


class GeminiClient:
    """
    Client for Google Gemini API with rate limiting and caching.

    Transforms layout YAML files into detailed prompts for image generation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp",
        rate_limit_config: Optional[RateLimitConfig] = None,
        enable_cache: bool = True,
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
            model: Model to use
            rate_limit_config: Rate limiting configuration
            enable_cache: Enable response caching
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self.cache = ResponseCache() if enable_cache else None

        if not self.api_key:
            logger.warning("No API key provided, using mock mode")
            self.mock_mode = True
            self.model = None
        else:
            self.mock_mode = False
            if GENAI_AVAILABLE:
                self.init_client(self.api_key)
            else:
                logger.error("google-generativeai not installed")
                self.mock_mode = True

        logger.info("GeminiClient initialized (mock={self.mock_mode})")

    def init_client(self, api_key: str):
        """Initialize the Gemini API client."""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("Gemini API initialized with model %s", self.model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini API: %s", e)
            self.mock_mode = True

    def transform_layout_to_prompts(self, layout_yaml: str) -> List[str]:
        """
        Transform a layout YAML file into prompts for all elements.

        Args:
            layout_yaml: Path to layout YAML file

        Returns:
            List of generated XML prompts
        """
        # Load layout
        with open(layout_yaml, "r") as f:
            layout = yaml.safe_load(f)

        prompts = []

        # Process both pages
        for page_key in ["left_page", "right_page"]:
            if page_key not in layout:
                continue

            elements = layout[page_key].get("elements", [])
            logger.info("Processing {len(elements)} elements from {page_key}")

            for element in elements:
                try:
                    prompt = self.generate_component_prompt(element.get("type", "unknown"), element)
                    prompts.append(prompt)
                    logger.info("Generated prompt for %s", element.get("id", "unknown"))
                except Exception as e:
                    logger.error("Failed to generate prompt for %s: %s", element.get("id"), e)

        return prompts

    def generate_component_prompt(self, element_type: str, params: Dict) -> str:
        """
        Generate a detailed prompt for a single element.

        Args:
            element_type: Type of element (photo, gui, pixelart, container)
            params: Element parameters from layout

        Returns:
            Generated XML prompt string
        """
        # Build the request for Gemini
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(element_type, params)

        # Check cache first
        if self.cache:
            cache_key = f"{system_prompt}|||{user_prompt}"
            cached_response = self.cache.get(cache_key)
            if cached_response:
                logger.info("Using cached response for {params.get('id', 'unknown')}")
                return cached_response

        # Make API call with retry
        response = self._call_api_with_retry(system_prompt, user_prompt)

        # Cache the response
        if self.cache and response:
            self.cache.set(f"{system_prompt}|||{user_prompt}", response)

        return response

    def _call_api_with_retry(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call API with exponential backoff retry logic.

        Args:
            system_prompt: System instructions
            user_prompt: User request

        Returns:
            API response text
        """
        if self.mock_mode:
            return self._generate_mock_response(user_prompt)

        for attempt in range(self.rate_limiter.config.retry_attempts):
            try:
                # Wait if needed for rate limiting
                self.rate_limiter.wait_if_needed()

                # Make the API call
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                if self.model is None:
                    raise RuntimeError("Model is not initialized")
                response = self.model.generate_content(full_prompt)

                if response and response.text:
                    result: str = response.text
                    return result
                else:
                    logger.warning("Empty response on attempt %s", attempt + 1)

            except Exception as e:
                logger.warning("API call failed (attempt %s): %s", attempt + 1, e)

                if attempt < self.rate_limiter.config.retry_attempts - 1:
                    # Exponential backoff
                    delay = min(
                        self.rate_limiter.config.base_delay * (2**attempt),
                        self.rate_limiter.config.max_delay,
                    )
                    logger.info("Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error("All retry attempts failed")
                    raise

        return ""

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Gemini."""
        return (
            "You are a specialized prompt engineer for a project recreating a 1996 "
            "Klutz Press computer graphics workbook. Your task is to transform simple "
            "descriptions into hyper-specific, quantitative XML prompts for the "
            "'nano-banana' image generation model.\n\n"
            "**CRITICAL RULES FOR VISUAL PROMPT GENERATION:**\n"
            '1. **NO SUBJECTIVITY:** Never use words like "nice," "good," "cool," '
            'or "awesome." Every instruction must be a number, a coordinate, a hex '
            "code, or a precise technical term.\n"
            "2. **QUANTIFY EVERYTHING:** Use pixels (px), degrees (deg), hex codes "
            "(#FF6600), and specific photographic terms (f/11, 100mm macro lens).\n"
            "3. **1996 TECHNOLOGY ONLY:** The final aesthetic must be achievable with "
            "1996-era desktop publishing tools. This means no gradients, no soft "
            "shadows, no modern blurs, and no antialiasing on bitmapped fonts.\n"
            "4. **FORBIDDEN AESTHETICS:** Any visual element, style, or design trend "
            "originating after 1997 is strictly forbidden from all generated "
            "images.\n\n"
            "**COLOR SYSTEM (70/20/10 RULE):**\n"
            "* **Klutz Primary (70%):** The foundational palette (Red, Blue, "
            "Yellow, etc.).\n"
            "* **Nickelodeon Accent (20%):** `#F57D0D` (Pantone 021 C) for energetic "
            '"splat" containers only.\n'
            "* **Goosebumps Theme (10%):** `#95C120` (Acid Green) for monster sprites "
            'or "glitch" effects only.\n\n'
            "You will be given a component description and must output a complete, "
            "valid XML prompt following the nano-banana schema."
        )

    def _build_user_prompt(self, element_type: str, params: Dict) -> str:
        """Build user prompt from element parameters."""
        element_id = params.get("id", "unknown")
        dimensions = params.get("dimensions", [800, 600])

        prompt = f"""Generate an XML prompt for nano-banana to create element {element_id}:
- Type: {element_type}
- Dimensions: {dimensions[0]}x{dimensions[1]}
- Position: {params.get('position', [0, 0])}
"""

        # Add type-specific details
        if element_type == "graphic_photo_instructional":
            prompt += f"""- Subject: {params.get('subject', 'computer hardware')}
- Film: Kodak Gold 400
- Style: 1996 Klutz Press instructional photography
- Lighting: Professional softbox setup
"""
        elif element_type == "graphic_gui_recreation":
            prompt += f"""- Software: {params.get('software', 'MacPaint')}
- Display: Macintosh Plus monochrome
- Resolution: 512x342
- Style: 1996 System 6 interface
"""
        elif element_type == "graphic_pixelart":
            prompt += """- Grid: 16x16 pixels
- Palette: 16-color maximum
- Style: NES/SNES era sprite
- Scaling: Nearest-neighbor only
"""
        elif element_type in ["container_featurebox", "container_splat"]:
            prompt += f"""- Shape: Irregular blob/splat
- Border: 4px hard black outline
- Fill: {params.get('fill_color', '#F57D0D')}
- Shadow: Hard drop shadow, 3px right, 3px down
"""

        if "content" in params:
            prompt += f"- Text Content: {params['content'][:100]}\n"

        prompt += """
Follow the exact XML schema. Be hyper-specific about all parameters.
Output ONLY the XML, no explanations."""

        return prompt

    def _generate_mock_response(self, user_prompt: str) -> str:
        """Generate a mock XML response for testing."""
        # Extract element ID from prompt
        import re

        match = re.search(r"element (\S+):", user_prompt)
        element_id = match.group(1) if match else "mock_element"

        return f"""<?xml version="1.0"?>
<nano_banana_prompt>
  <element_id>{element_id}</element_id>
  <image_specifications>
    <dimensions width="800" height="600" dpi="300"/>
    <color_space>sRGB</color_space>
  </image_specifications>
  <positive_prompt>
    Professional 1996 Klutz Press style image, period-accurate hardware,
    Kodak Gold 400 film grain, bright educational photography,
    hard shadows, no gradients, bold primary colors
  </positive_prompt>
  <negative_prompt>
    modern technology, soft shadows, gradients, antialiasing,
    smartphone, tablet, wireless, LED, LCD
  </negative_prompt>
</nano_banana_prompt>"""


def main():
    """CLI interface for Gemini integration."""
    parser = argparse.ArgumentParser(description="Transform layouts to prompts using Gemini API")
    parser.add_argument("--layout", required=True, help="Path to layout YAML file")
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for generated prompts"
    )
    parser.add_argument("--api-key", help="Gemini API key (or use GEMINI_API_KEY env var)")
    parser.add_argument("--model", default="gemini-2.0-flash-exp", help="Gemini model to use")
    parser.add_argument("--no-cache", action="store_true", help="Disable response caching")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize client
    client = GeminiClient(api_key=args.api_key, model=args.model, enable_cache=not args.no_cache)

    # Transform layout
    try:
        logger.info("Processing layout: {args.layout}")
        prompts = client.transform_layout_to_prompts(args.layout)

        # Write prompts to files
        layout_name = Path(args.layout).stem
        for i, prompt in enumerate(prompts):
            output_file = output_dir / f"{layout_name}_element_{i:03d}.xml"
            with open(output_file, "w") as f:
                f.write(prompt)
            logger.info("Wrote prompt to {output_file}")

        print(f"✓ Generated {len(prompts)} prompts in {output_dir}")

    except Exception as e:
        logger.error("Failed to process layout: {e}")
        print(f"✗ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
