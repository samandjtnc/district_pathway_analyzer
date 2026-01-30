"""
LLM client for interacting with Claude API.
"""

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from district_pathway_analyzer.config import get_config


class LLMClient:
    """Client for interacting with Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM client.

        Args:
            api_key: Optional API key. If not provided, will use ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable must be set or api_key must be provided"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.config = get_config().llm

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a completion request to Claude.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Optional max tokens (defaults to config)
            temperature: Optional temperature (defaults to config)

        Returns:
            The model's response text
        """
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature,
            system=system or "",
            messages=messages,
        )

        return response.content[0].text

    def complete_with_images(
        self,
        prompt: str,
        image_paths: List[str],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a completion request with images to Claude.

        Args:
            prompt: The user prompt
            image_paths: List of paths to image files
            system: Optional system prompt
            max_tokens: Optional max tokens (defaults to config)
            temperature: Optional temperature (defaults to config)

        Returns:
            The model's response text
        """
        content = []

        # Add images
        for path in image_paths:
            image_data = self._encode_image(path)
            if image_data:
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_data["media_type"],
                            "data": image_data["data"],
                        },
                    }
                )

        # Add text prompt
        content.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content}]

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature,
            system=system or "",
            messages=messages,
        )

        return response.content[0].text

    def complete_structured(
        self,
        prompt: str,
        system: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a completion request expecting structured JSON output.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            response_format: Optional JSON schema for response
            max_tokens: Optional max tokens (defaults to config)
            temperature: Optional temperature (defaults to config)

        Returns:
            The model's response text (should be valid JSON)
        """
        # Append JSON instruction to prompt
        structured_prompt = f"""{prompt}

Please respond with valid JSON only, no additional text or markdown formatting."""

        return self.complete(
            prompt=structured_prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _encode_image(self, path: str) -> Optional[Dict[str, str]]:
        """Encode an image file to base64.

        Args:
            path: Path to the image file

        Returns:
            Dict with media_type and data, or None if encoding fails
        """
        path_obj = Path(path)
        if not path_obj.exists():
            return None

        # Determine media type
        suffix = path_obj.suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_types.get(suffix)
        if not media_type:
            return None

        # Read and encode
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        return {"media_type": media_type, "data": data}


# Global client instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


def set_llm_client(client: LLMClient) -> None:
    """Set the global LLM client instance."""
    global _client
    _client = client
