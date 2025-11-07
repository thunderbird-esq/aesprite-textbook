#!/usr/bin/env python3
"""
quality_assurance.py - Comprehensive QA system for generated content
Team 4: AI Integration & Processing
"""

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image

try:
    import pytesseract

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("pytesseract not available, text legibility checks disabled")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class QAResult:
    """Result of a single QA check"""

    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Optional[Dict] = None


class QualityChecker:
    """
    Quality assurance checker for generated assets.

    Validates color distribution, text legibility, period authenticity.
    """

    def __init__(self):
        """Initialize QA checker"""
        self.color_ratios = {
            "nickelodeon_orange_max": 0.30,
            "goosebumps_acid_max": 0.10,
            "primary_colors_min": 0.70,
        }

        self.nickelodeon_orange = np.array([245, 125, 13])  # #F57D0D
        self.goosebumps_acid = np.array([149, 193, 32])  # #95C120

        logger.info("QualityChecker initialized")

    def check_color_distribution(self, image_path: str, ratios: Optional[Dict] = None) -> bool:
        """
        Verify 70/20/10 color rule.

        Args:
            image_path: Path to image file
            ratios: Optional custom ratio limits

        Returns:
            True if color distribution is valid
        """
        ratios = ratios or self.color_ratios

        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)
            pixels = img_array.reshape(-1, 3)
            total_pixels = len(pixels)

            # Count special color usage
            nick_count = 0
            goose_count = 0

            # Sample every 10th pixel for performance
            for pixel in pixels[::10]:
                # Check if close to Nickelodeon orange
                if np.linalg.norm(pixel - self.nickelodeon_orange) < 30:
                    nick_count += 10

                # Check if close to Goosebumps acid green
                elif np.linalg.norm(pixel - self.goosebumps_acid) < 30:
                    goose_count += 10

            # Calculate ratios
            nick_ratio = nick_count / total_pixels
            goose_ratio = goose_count / total_pixels

            logger.info(
                f"Color ratios - Nickelodeon: {nick_ratio:.1%}, Goosebumps: {goose_ratio:.1%}"
            )

            # Check limits
            if nick_ratio > ratios["nickelodeon_orange_max"]:
                logger.warning(f"Too much Nickelodeon orange: {nick_ratio:.1%}")
                return False

            if goose_ratio > ratios["goosebumps_acid_max"]:
                logger.warning(f"Too much Goosebumps acid: {goose_ratio:.1%}")
                return False

            logger.info("Color distribution check passed")
            return True

        except Exception as e:
            logger.error(f"Color distribution check failed: {e}")
            return False

    def check_text_legibility(self, image_path: str, min_contrast: float = 4.5) -> bool:
        """
        Check text legibility using OCR and contrast analysis.

        Args:
            image_path: Path to image file
            min_contrast: Minimum contrast ratio (WCAG AA = 4.5)

        Returns:
            True if text is legible
        """
        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # Calculate global contrast
            contrast = self._calculate_contrast(gray)

            logger.info(f"Image contrast ratio: {contrast:.2f}")

            if contrast < min_contrast:
                logger.warning(f"Low contrast: {contrast:.2f} < {min_contrast}")
                return False

            # If OCR available, try to detect text
            if OCR_AVAILABLE:
                try:
                    text = pytesseract.image_to_string(img)
                    if len(text.strip()) > 0:
                        logger.info(f"OCR detected {len(text)} characters")
                except Exception as e:
                    logger.debug(f"OCR failed: {e}")

            logger.info("Text legibility check passed")
            return True

        except Exception as e:
            logger.error(f"Text legibility check failed: {e}")
            return False

    def _calculate_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate contrast ratio of grayscale image"""
        # Calculate RMS contrast
        std_dev = np.std(gray_image)
        mean_val = np.mean(gray_image)

        if mean_val > 0:
            rms_contrast = std_dev / mean_val
            # Convert to rough WCAG-style ratio
            contrast_ratio = 1 + (rms_contrast * 10)
            return min(contrast_ratio, 21.0)  # Cap at WCAG maximum
        else:
            return 0.0

    def check_period_authenticity(self, image_path: str) -> List[str]:
        """
        Detect anachronistic visual elements.

        Args:
            image_path: Path to image file

        Returns:
            List of detected anachronisms (empty if none)
        """
        violations = []

        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)

            # Check for smooth gradients (forbidden in 1996)
            if self._detect_gradients(img_array):
                violations.append("Smooth gradients detected")

            # Check for soft shadows
            if self._detect_soft_shadows(img_array):
                violations.append("Soft shadows detected")

            # Check for modern flat design colors
            if self._detect_modern_colors(img_array):
                violations.append("Modern flat design colors detected")

            if violations:
                logger.warning(f"Authenticity violations: {', '.join(violations)}")
            else:
                logger.info("Period authenticity check passed")

        except Exception as e:
            logger.error(f"Authenticity check failed: {e}")
            violations.append(f"Check error: {e}")

        return violations

    def _detect_gradients(self, img_array: np.ndarray) -> bool:
        """Detect smooth gradients in image"""
        # Sample horizontal lines for gradient detection
        gradient_detected = False

        for y in range(0, img_array.shape[0], 20):
            row = img_array[y]
            if len(row.shape) == 2:
                unique_colors = len(np.unique(row))
            else:
                unique_colors = len(np.unique(row.reshape(-1, row.shape[-1]), axis=0))

            # More than 50 unique colors in a row suggests gradient
            if unique_colors > 50:
                gradient_detected = True
                break

        return gradient_detected

    def _detect_soft_shadows(self, img_array: np.ndarray) -> bool:
        """Detect soft shadows (should be hard-edged)"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Dilate edges and check transition width
        dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

        # Calculate average transition width
        transition_pixels = np.sum(dilated) - np.sum(edges)
        total_edges = np.sum(edges)

        if total_edges > 0:
            avg_transition = transition_pixels / total_edges
            # Soft shadows have wide transitions
            return avg_transition > 4
        else:
            return False

    def _detect_modern_colors(self, img_array: np.ndarray) -> bool:
        """Detect modern flat design color palette"""
        # Modern iOS/Material Design colors (too pure/saturated for 1996)
        modern_colors = [
            [0, 122, 255],  # iOS blue
            [52, 199, 89],  # iOS green
            [255, 59, 48],  # iOS red
            [33, 150, 243],  # Material blue
            [76, 175, 80],  # Material green
        ]

        pixels = img_array.reshape(-1, 3)

        # Check for pure modern colors
        for modern_color in modern_colors:
            mask = np.all(np.abs(pixels - modern_color) < 10, axis=1)
            if np.sum(mask) > len(pixels) * 0.01:  # More than 1% of pixels
                return True

        return False

    def generate_qa_report(self, spread_path: str) -> Dict:
        """
        Generate comprehensive QA report for a spread.

        Args:
            spread_path: Path to spread image

        Returns:
            Dictionary containing all QA results
        """
        logger.info(f"Generating QA report for {spread_path}")

        report = {"spread_path": spread_path, "checks": [], "overall_passed": True, "score": 0.0}

        # Color distribution check
        color_passed = self.check_color_distribution(spread_path)
        report["checks"].append(
            QAResult(
                check_name="color_distribution",
                passed=color_passed,
                score=1.0 if color_passed else 0.5,
                message="Color distribution within limits"
                if color_passed
                else "Color ratio violations",
            )
        )

        # Text legibility check
        legibility_passed = self.check_text_legibility(spread_path)
        report["checks"].append(
            QAResult(
                check_name="text_legibility",
                passed=legibility_passed,
                score=1.0 if legibility_passed else 0.6,
                message="Text is legible" if legibility_passed else "Low contrast detected",
            )
        )

        # Period authenticity check
        violations = self.check_period_authenticity(spread_path)
        auth_passed = len(violations) == 0
        report["checks"].append(
            QAResult(
                check_name="period_authenticity",
                passed=auth_passed,
                score=1.0 if auth_passed else 0.4,
                message="No anachronisms detected"
                if auth_passed
                else f"Violations: {', '.join(violations)}",
                details={"violations": violations},
            )
        )

        # Calculate overall score
        scores = [check.score for check in report["checks"]]
        report["score"] = np.mean(scores)
        report["overall_passed"] = all(check.passed for check in report["checks"])

        # Convert dataclasses to dicts for JSON serialization
        report["checks"] = [asdict(check) for check in report["checks"]]

        logger.info(
            f"QA report complete - Score: {report['score']:.2f}, Passed: {report['overall_passed']}"
        )

        return report


def main():
    """CLI interface for quality assurance"""
    parser = argparse.ArgumentParser(description="Quality assurance for generated spreads")
    parser.add_argument("--spread", required=True, help="Path to spread image file")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--output", help="Output path for JSON report")
    parser.add_argument(
        "--min-contrast", type=float, default=4.5, help="Minimum contrast ratio for text"
    )

    args = parser.parse_args()

    # Initialize checker
    checker = QualityChecker()

    if args.report:
        # Generate full report
        try:
            report = checker.generate_qa_report(args.spread)

            # Print summary
            print(f"\nQA Report for {Path(args.spread).name}")
            print("=" * 60)
            print(f"Overall Score: {report['score']:.2f}/1.00")
            print(f"Status: {'PASSED' if report['overall_passed'] else 'FAILED'}")
            print("\nIndividual Checks:")

            for check in report["checks"]:
                status = "✓" if check["passed"] else "✗"
                print(f"  {status} {check['check_name']}: {check['message']}")

            # Save to file if requested
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"\nDetailed report saved to: {args.output}")

            return 0 if report["overall_passed"] else 1

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            print(f"✗ Error: {e}")
            return 1

    else:
        # Quick checks only
        try:
            print(f"Running QA checks on {args.spread}")

            # Color distribution
            color_ok = checker.check_color_distribution(args.spread)
            print(f"  {'✓' if color_ok else '✗'} Color distribution")

            # Text legibility
            legibility_ok = checker.check_text_legibility(args.spread, args.min_contrast)
            print(f"  {'✓' if legibility_ok else '✗'} Text legibility")

            # Period authenticity
            violations = checker.check_period_authenticity(args.spread)
            auth_ok = len(violations) == 0
            print(f"  {'✓' if auth_ok else '✗'} Period authenticity")

            if not auth_ok:
                for violation in violations:
                    print(f"      - {violation}")

            all_passed = color_ok and legibility_ok and auth_ok
            print(f"\nOverall: {'PASSED' if all_passed else 'FAILED'}")

            return 0 if all_passed else 1

        except Exception as e:
            logger.error(f"QA check failed: {e}")
            print(f"✗ Error: {e}")
            return 1


if __name__ == "__main__":
    exit(main())
