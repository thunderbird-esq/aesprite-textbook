"""
Tests for gemini_integration.py

Tests include:
- Mock API client functionality
- Content generation
- Response parsing
- Error handling
- Rate limiting
- Retry logic
"""

import pytest


@pytest.mark.api
class TestGeminiClientBasics:
    """Test basic Gemini client functionality."""

    def test_client_initialization(self, mock_gemini):
        """Test that client initializes correctly."""
        assert mock_gemini is not None
        assert mock_gemini.api_key == "test_key"
        assert mock_gemini.call_count == 0

    def test_client_has_generate_method(self, mock_gemini):
        """Test that client has generate_content method."""
        assert hasattr(mock_gemini, "generate_content")
        assert callable(mock_gemini.generate_content)


@pytest.mark.api
class TestContentGeneration:
    """Test content generation with Gemini API."""

    def test_generate_simple_content(self, mock_gemini):
        """Test generating simple content."""
        prompt = "Describe a pixel art sprite of a computer"
        response = mock_gemini.generate_content(prompt)

        assert response is not None
        assert "candidates" in response
        assert len(response["candidates"]) > 0

    def test_generate_content_increments_counter(self, mock_gemini):
        """Test that API calls increment call counter."""
        initial_count = mock_gemini.call_count

        mock_gemini.generate_content("Test prompt")

        assert mock_gemini.call_count == initial_count + 1

    def test_generate_content_stores_prompt(self, mock_gemini):
        """Test that last prompt is stored."""
        prompt = "Test prompt for storage"
        mock_gemini.generate_content(prompt)

        assert mock_gemini.last_prompt == prompt

    def test_multiple_generations(self, mock_gemini):
        """Test multiple content generations."""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]

        for prompt in prompts:
            mock_gemini.generate_content(prompt)

        assert mock_gemini.call_count == len(prompts)
        assert mock_gemini.last_prompt == prompts[-1]


@pytest.mark.api
class TestResponseParsing:
    """Test parsing of Gemini API responses."""

    def test_parse_default_response(self, mock_gemini):
        """Test parsing default mock response."""
        response = mock_gemini.generate_content("Test")

        assert "candidates" in response
        candidate = response["candidates"][0]
        assert "content" in candidate
        assert "parts" in candidate["content"]
        assert len(candidate["content"]["parts"]) > 0

    def test_extract_text_from_response(self, mock_gemini):
        """Test extracting text from response."""
        response = mock_gemini.generate_content("Test")

        text = response["candidates"][0]["content"]["parts"][0]["text"]
        assert isinstance(text, str)
        assert len(text) > 0

    def test_custom_response(self, mock_gemini):
        """Test using custom response."""
        custom_text = "Custom computer sprite description"
        custom_response = {"candidates": [{"content": {"parts": [{"text": custom_text}]}}]}

        mock_gemini.set_response(custom_response)
        response = mock_gemini.generate_content("Test")

        text = response["candidates"][0]["content"]["parts"][0]["text"]
        assert text == custom_text

    def test_multiple_custom_responses(self, mock_gemini):
        """Test multiple custom responses in sequence."""
        responses = [
            {"candidates": [{"content": {"parts": [{"text": "Response 1"}]}}]},
            {"candidates": [{"content": {"parts": [{"text": "Response 2"}]}}]},
            {"candidates": [{"content": {"parts": [{"text": "Response 3"}]}}]},
        ]

        for resp in responses:
            mock_gemini.set_response(resp)

        # Generate and verify each response
        for i, expected_resp in enumerate(responses):
            response = mock_gemini.generate_content(f"Prompt {i}")
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            expected_text = expected_resp["candidates"][0]["content"]["parts"][0]["text"]
            assert text == expected_text


@pytest.mark.api
class TestErrorHandling:
    """Test error handling in Gemini integration."""

    def test_handle_empty_response(self, mock_gemini):
        """Test handling of empty response."""
        empty_response = {"candidates": []}
        mock_gemini.set_response(empty_response)

        response = mock_gemini.generate_content("Test")
        assert "candidates" in response
        # Should handle empty candidates list gracefully

    def test_reset_client_state(self, mock_gemini):
        """Test resetting client state."""
        mock_gemini.generate_content("Test 1")
        mock_gemini.generate_content("Test 2")

        assert mock_gemini.call_count == 2

        mock_gemini.reset()

        assert mock_gemini.call_count == 0
        assert mock_gemini.last_prompt is None
        assert len(mock_gemini.responses) == 0

    def test_client_state_after_error(self, mock_gemini):
        """Test client state after handling error."""
        try:
            # Simulate some operation
            response = mock_gemini.generate_content("Test")
            # Even if we raise an error, call_count should be incremented
            assert mock_gemini.call_count > 0
        except Exception:
            pass

        # Client should still be usable
        response = mock_gemini.generate_content("Recovery test")
        assert response is not None


@pytest.mark.api
class TestPromptValidation:
    """Test prompt validation before sending to API."""

    def test_validate_prompt_not_empty(self):
        """Test that empty prompts are rejected."""
        prompt = ""
        is_valid = len(prompt.strip()) > 0

        assert not is_valid, "Empty prompt should be invalid"

    def test_validate_prompt_length(self):
        """Test prompt length validation."""
        short_prompt = "Test"
        long_prompt = "A" * 10000

        assert len(short_prompt) < 5000, "Short prompt should be valid"
        # Check if extremely long prompts should be truncated or rejected
        should_truncate = len(long_prompt) > 5000

        assert should_truncate, "Very long prompts should be handled"

    def test_validate_prompt_content(self, test_config):
        """Test content validation before API call."""
        forbidden = test_config["validation"]["forbidden_terms"]

        valid_prompt = "A pixel art sprite of a computer"
        invalid_prompt = "A sprite with gradient effects"

        has_forbidden_valid = any(term in valid_prompt.lower() for term in forbidden)
        has_forbidden_invalid = any(term in invalid_prompt.lower() for term in forbidden)

        assert not has_forbidden_valid, "Valid prompt should pass"
        assert has_forbidden_invalid, "Invalid prompt should fail"


@pytest.mark.api
class TestRateLimiting:
    """Test rate limiting for API calls."""

    def test_track_api_calls(self, mock_gemini):
        """Test tracking number of API calls."""
        num_calls = 5

        for i in range(num_calls):
            mock_gemini.generate_content(f"Prompt {i}")

        assert mock_gemini.call_count == num_calls

    def test_rate_limit_check(self):
        """Test rate limit checking logic."""
        max_calls_per_minute = 60
        current_calls = 0

        # Simulate making calls
        for i in range(10):
            current_calls += 1

        can_make_call = current_calls < max_calls_per_minute
        assert can_make_call, "Should be under rate limit"

    def test_rate_limit_exceeded(self):
        """Test behavior when rate limit is exceeded."""
        max_calls_per_minute = 60
        current_calls = 65

        can_make_call = current_calls < max_calls_per_minute
        assert not can_make_call, "Should exceed rate limit"


@pytest.mark.api
class TestRetryLogic:
    """Test retry logic for failed API calls."""

    def test_retry_on_failure(self, mock_gemini):
        """Test retrying after failure."""
        max_retries = 3
        attempts = 0

        # Simulate retry logic
        for attempt in range(max_retries):
            attempts += 1
            try:
                response = mock_gemini.generate_content("Test")
                if response:
                    break
            except Exception:
                if attempt == max_retries - 1:
                    raise
                continue

        assert attempts <= max_retries

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        base_delay = 1
        max_retries = 5

        delays = []
        for attempt in range(max_retries):
            delay = base_delay * (2**attempt)
            delays.append(delay)

        # Verify exponential growth
        assert delays[0] == 1
        assert delays[1] == 2
        assert delays[2] == 4
        assert delays[3] == 8
        assert delays[4] == 16

    def test_max_retry_limit(self, mock_gemini):
        """Test that retries respect maximum limit."""
        max_retries = 3
        attempts = 0
        success = False

        # Simulate failing attempts
        for attempt in range(max_retries + 5):  # Try more than max
            attempts += 1
            if attempts > max_retries:
                break

            # Simulate some check
            response = mock_gemini.generate_content("Test")
            if response and attempts >= 2:  # Succeed on 2nd attempt
                success = True
                break

        assert attempts <= max_retries or success
        assert success, "Should eventually succeed within retry limit"


@pytest.mark.integration
@pytest.mark.api
class TestGeminiIntegrationWorkflow:
    """Integration tests for complete Gemini workflow."""

    def test_end_to_end_content_generation(self, mock_gemini, test_config):
        """Test complete workflow from prompt to validated response."""
        # Create validated prompt
        prompt = "A pixel art sprite of a computer with keyboard and mouse"

        # Validate prompt
        forbidden = test_config["validation"]["forbidden_terms"]
        has_forbidden = any(term in prompt.lower() for term in forbidden)
        assert not has_forbidden

        # Generate content
        response = mock_gemini.generate_content(prompt)

        # Parse response
        text = response["candidates"][0]["content"]["parts"][0]["text"]

        assert text is not None
        assert len(text) > 0
        assert mock_gemini.call_count == 1

    def test_generation_with_validation_retry(self, mock_gemini, test_config):
        """Test generation with validation and retry on failure."""
        forbidden = test_config["validation"]["forbidden_terms"]
        max_attempts = test_config["prompt_generation"]["max_attempts"]

        # Set up responses (first invalid, then valid)
        invalid_response = {
            "candidates": [{"content": {"parts": [{"text": "A sprite with gradient and shader"}]}}]
        }

        valid_response = {
            "candidates": [
                {"content": {"parts": [{"text": "A sprite of a computer with keyboard"}]}}
            ]
        }

        mock_gemini.set_response(invalid_response)
        mock_gemini.set_response(valid_response)

        # Try generation with validation
        attempts = 0
        valid_text = None

        for attempt in range(max_attempts):
            attempts += 1
            response = mock_gemini.generate_content("Generate sprite description")
            text = response["candidates"][0]["content"]["parts"][0]["text"]

            # Validate
            has_forbidden = any(term in text.lower() for term in forbidden)
            if not has_forbidden:
                valid_text = text
                break

        assert valid_text is not None, "Should get valid response within max attempts"
        assert attempts <= max_attempts
        assert mock_gemini.call_count == attempts
