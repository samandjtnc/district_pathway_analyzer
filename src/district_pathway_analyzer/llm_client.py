"""
LLM client for interacting with Claude API or OpenRouter.

Set ANTHROPIC_API_KEY for Claude models.
Set OPENROUTER_API_KEY for free/Google models via OpenRouter (https://openrouter.ai).
"""

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI

from district_pathway_analyzer.config import get_config

# ---------------------------------------------------------------------------
# Model tiers — used to populate the frontend model selector
# ---------------------------------------------------------------------------
MODEL_OPTIONS = [
    ("stepfun/step-3.5-flash:free",       "Free  |  Step 3.5 Flash (via OpenRouter)"),
    ("google/gemma-3-27b-it:free",        "Free  |  Gemma 3-27b (via OpenRouter)"),
    ("google/gemini-2.0-flash-exp:free",  "Free  |  Gemini 2.0 Flash Exp (via OpenRouter)"),
    ("claude-haiku-4-5-20251001",         "Budget  |  Claude Haiku 4.5"),
    ("claude-sonnet-4-5-20250929",        "Standard  |  Claude Sonnet 4.5"),
    ("claude-sonnet-4-6",                 "Standard  |  Claude Sonnet 4.6 (Latest)"),
    ("claude-opus-4-6",                   "Premium  |  Claude Opus 4.6"),
]


def _is_openrouter_model(model: str) -> bool:
    """Return True for models routed through OpenRouter."""
    return (
        model.startswith("google/")
        or model.startswith("meta/")
        or model.startswith("mistralai/")
        or ":free" in model
    )


def _is_no_system_prompt_model(model: str) -> bool:
    """Return True for models that don't support a separate system role (e.g. Gemma)."""
    return "gemma" in model.lower()


class LLMClient:
    """Client for interacting with Claude API or OpenRouter."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the LLM client.

        Args:
            api_key: Optional Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            model:   Optional model override. Falls back to config.yaml value.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable must be set or api_key must be provided"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.config = get_config().llm
        self._model_override = model  # None means use config default

    @property
    def _model(self) -> str:
        return self._model_override or self.config.model

    def _call_openrouter(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
    ) -> str:
        """Route a call through OpenRouter."""
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not openrouter_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. "
                "Free and Google models require an OpenRouter API key. "
                "Sign up at https://openrouter.ai and add OPENROUTER_API_KEY to your environment."
            )
        or_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
        )
        # Gemma doesn't support a system role — fold it into the user message
        if _is_no_system_prompt_model(self._model) and system:
            messages = [{"role": "user", "content": f"{system}\n\n{prompt}"}]
        else:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
        response = or_client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a completion request to the configured LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Optional max tokens (defaults to config)
            temperature: Optional temperature (defaults to config)

        Returns:
            The model's response text
        """
        resolved_max_tokens = max_tokens or self.config.max_tokens

        if _is_openrouter_model(self._model):
            return self._call_openrouter(prompt, system, resolved_max_tokens)

        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self._model,
            max_tokens=resolved_max_tokens,
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

        Note: Image support requires an Anthropic model. OpenRouter models that
        support vision can also be used but image encoding format may differ.

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
            model=self._model,
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

        raw = self.complete(
            prompt=structured_prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Strip markdown fences that some models (e.g. Gemma) add despite instructions
        import re
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return raw

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
