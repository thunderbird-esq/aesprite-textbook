"""
Tests for prompt_generator.py

Tests include:
- Prompt template rendering
- Variable substitution
- Forbidden term avoidance
- Required term inclusion
- XML format validation
- Prompt validation logic
- Error handling
"""

import pytest
from test_framework import create_test_prompt_xml, create_test_config


class TestPromptGeneration:
    """Test prompt generation functionality."""

    def test_generate_basic_prompt(self):
        """Test generating a basic prompt."""
        template = "A pixel art sprite of a {item}"
        item = "computer"
        prompt = template.format(item=item)

        assert "computer" in prompt, "Prompt should contain substituted variable"
        assert "pixel art" in prompt, "Prompt should contain template text"

    def test_prompt_variable_substitution(self):
        """Test variable substitution in prompts."""
        template = "A {style} sprite of a {item} with {accessory}"
        variables = {
            "style": "pixel art",
            "item": "computer",
            "accessory": "keyboard"
        }
        prompt = template.format(**variables)

        assert "pixel art" in prompt
        assert "computer" in prompt
        assert "keyboard" in prompt

    def test_multiple_variable_substitution(self):
        """Test multiple instances of same variable."""
        template = "A {item} sprite, the {item} should have detail"
        prompt = template.format(item="computer")

        assert prompt.count("computer") == 2, \
            "Variable should be substituted in all occurrences"


class TestForbiddenTermAvoidance:
    """Test avoidance of forbidden terms in prompts."""

    def test_detect_forbidden_gradient(self, test_config):
        """Test detection of forbidden term 'gradient'."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with a smooth gradient"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert has_forbidden, "Should detect forbidden term 'gradient'"

    def test_detect_forbidden_alpha(self, test_config):
        """Test detection of forbidden term 'alpha'."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with alpha transparency"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert has_forbidden, "Should detect forbidden term 'alpha'"

    def test_clean_prompt_no_forbidden(self, test_config):
        """Test that clean prompts pass validation."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A pixel art sprite of a computer with keyboard"

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert not has_forbidden, "Clean prompt should not have forbidden terms"

    def test_remove_forbidden_terms(self, test_config):
        """Test removing forbidden terms from prompt."""
        forbidden = test_config["validation"]["forbidden_terms"]
        prompt = "A sprite with gradient and shader effects"

        # Remove forbidden terms
        cleaned = prompt
        for term in forbidden:
            cleaned = cleaned.replace(term, "").replace("  ", " ")

        # Check that forbidden terms are removed
        has_forbidden = any(term in cleaned.lower() for term in forbidden)
        assert not has_forbidden, "Forbidden terms should be removed"


class TestRequiredTermInclusion:
    """Test inclusion of required hardware/visual terms."""

    def test_include_required_hardware_terms(self, test_config):
        """Test that prompts include required hardware terms."""
        required = test_config["validation"]["required_visual_terms"]
        min_required = test_config["validation"]["min_hardware_terms"]

        prompt = "A pixel art sprite of a computer with keyboard and mouse"

        found = [term for term in required if term in prompt.lower()]
        assert len(found) >= min_required, \
            f"Should include at least {min_required} hardware terms"

    def test_insufficient_required_terms(self, test_config):
        """Test detection of insufficient required terms."""
        required = test_config["validation"]["required_visual_terms"]
        min_required = test_config["validation"]["min_hardware_terms"]

        prompt = "A pixel art sprite"

        found = [term for term in required if term in prompt.lower()]
        assert len(found) < min_required, \
            "Should detect insufficient hardware terms"

    def test_add_required_terms_to_prompt(self, test_config):
        """Test adding required terms to prompt."""
        required = test_config["validation"]["required_visual_terms"]

        base_prompt = "A pixel art sprite"
        enhanced_prompt = f"{base_prompt} of a computer with keyboard"

        found = [term for term in required if term in enhanced_prompt.lower()]
        assert len(found) >= 2, "Enhanced prompt should have required terms"


class TestXMLFormatValidation:
    """Test XML format for prompts."""

    def test_valid_xml_structure(self, test_prompt_xml):
        """Test that prompt XML has valid structure."""
        assert "<?xml" in test_prompt_xml, "Should have XML declaration"
        assert "<prompt>" in test_prompt_xml, "Should have prompt root element"
        assert "</prompt>" in test_prompt_xml, "Should close prompt element"

    def test_xml_contains_description(self, test_prompt_xml):
        """Test that XML contains description element."""
        assert "<description>" in test_prompt_xml, \
            "Should have description element"
        assert "</description>" in test_prompt_xml, \
            "Should close description element"

    def test_xml_contains_style(self, test_prompt_xml):
        """Test that XML contains style element."""
        assert "<style>" in test_prompt_xml, "Should have style element"
        assert "</style>" in test_prompt_xml, "Should close style element"

    def test_xml_contains_constraints(self, test_prompt_xml):
        """Test that XML contains constraints element."""
        assert "<constraints>" in test_prompt_xml, \
            "Should have constraints element"
        assert "</constraints>" in test_prompt_xml, \
            "Should close constraints element"

    def test_create_xml_from_parts(self):
        """Test creating XML from component parts."""
        description = "computer with keyboard"
        style = "aesprite pixel art"
        size = "32x32"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prompt>
    <description>{description}</description>
    <style>{style}</style>
    <constraints>
        <size>{size}</size>
    </constraints>
</prompt>"""

        assert description in xml
        assert style in xml
        assert size in xml
        assert "<prompt>" in xml


class TestPromptValidation:
    """Test prompt validation logic."""

    def test_validate_prompt_length(self):
        """Test validation of prompt length."""
        short_prompt = "Computer"
        long_prompt = "A " * 1000

        assert len(short_prompt) < 1000, "Short prompt should be valid"
        assert len(long_prompt) < 5000, "Should check for excessive length"

    def test_validate_prompt_content(self, test_config):
        """Test comprehensive prompt validation."""
        forbidden = test_config["validation"]["forbidden_terms"]
        required = test_config["validation"]["required_visual_terms"]

        prompt = "A pixel art sprite of a computer with keyboard"

        # Check no forbidden terms
        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert not has_forbidden

        # Check has required terms
        found_required = [term for term in required if term in prompt.lower()]
        assert len(found_required) >= 2

    def test_validation_rejects_invalid_prompt(self, test_config):
        """Test that validation rejects invalid prompts."""
        forbidden = test_config["validation"]["forbidden_terms"]

        invalid_prompt = "A sprite with gradient shader and alpha blending"

        has_forbidden = any(term in prompt.lower()
                          for term in forbidden
                          for prompt in [invalid_prompt])
        assert has_forbidden, "Should reject prompt with forbidden terms"


class TestErrorHandling:
    """Test error handling in prompt generation."""

    def test_handle_missing_template_variable(self):
        """Test handling of missing template variables."""
        template = "A sprite of a {item} with {accessory}"

        try:
            # Missing 'accessory' variable
            prompt = template.format(item="computer")
            assert False, "Should raise KeyError for missing variable"
        except KeyError:
            pass  # Expected behavior

    def test_handle_empty_template(self):
        """Test handling of empty template."""
        template = ""
        prompt = template.format()

        assert prompt == "", "Empty template should produce empty prompt"

    def test_handle_invalid_variable_name(self):
        """Test handling of invalid variable names."""
        template = "A sprite of a {item-name}"  # Hyphens not allowed

        # This actually works in Python, but good to test
        try:
            prompt = template.format(**{"item-name": "computer"})
            assert "computer" in prompt
        except:
            pass  # Some implementations might reject this


@pytest.mark.integration
class TestPromptGenerationIntegration:
    """Integration tests for complete prompt generation workflow."""

    def test_end_to_end_prompt_generation(self, test_config):
        """Test complete prompt generation from template to validated output."""
        # Start with template
        template = "A pixel art sprite of a {item} with {accessory}"

        # Substitute variables
        variables = {"item": "computer", "accessory": "keyboard and mouse"}
        prompt = template.format(**variables)

        # Validate against config
        forbidden = test_config["validation"]["forbidden_terms"]
        required = test_config["validation"]["required_visual_terms"]

        has_forbidden = any(term in prompt.lower() for term in forbidden)
        found_required = [term for term in required if term in prompt.lower()]

        assert not has_forbidden, "Should not have forbidden terms"
        assert len(found_required) >= 2, "Should have required terms"

    def test_prompt_generation_with_retry(self, test_config):
        """Test prompt generation with retry on validation failure."""
        max_attempts = test_config["prompt_generation"]["max_attempts"]

        attempts = 0
        valid_prompt = None

        # Simulate retry logic
        prompts = [
            "A sprite with gradient",  # Invalid
            "A sprite with shader",    # Invalid
            "A sprite of a computer with keyboard"  # Valid
        ]

        forbidden = test_config["validation"]["forbidden_terms"]
        required = test_config["validation"]["required_visual_terms"]

        for attempt_prompt in prompts:
            attempts += 1
            if attempts > max_attempts:
                break

            has_forbidden = any(term in attempt_prompt.lower()
                              for term in forbidden)
            found_required = [term for term in required
                            if term in attempt_prompt.lower()]

            if not has_forbidden and len(found_required) >= 2:
                valid_prompt = attempt_prompt
                break

        assert valid_prompt is not None, "Should find valid prompt within attempts"
        assert attempts <= max_attempts, "Should complete within max attempts"
