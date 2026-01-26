"""LLM service for generating route descriptions."""
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

from openai import OpenAI
from openai import OpenAIError

from pathypotomus.models.route import Route

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM generation fails."""


class LLMCache:
    """Simple file-based cache for LLM responses."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / "llm_cache.json"
        self._cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self._cache = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupt cache file found, starting with empty cache")
                self._cache = {}
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self._cache = {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_key(self, prompt: str, model: str) -> str:
        """Generate a stable key for the prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response."""
        key = self._get_key(prompt, model)
        return self._cache.get(key)

    def set(self, prompt: str, model: str, response: str):
        """Cache response."""
        key = self._get_key(prompt, model)
        self._cache[key] = response
        self._save_cache()


class LLMService:
    """Service for generating route descriptions using LLM."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "google/gemini-flash-1.5",
        provider: str = "openrouter",
        cache_dir: str = ".cache"
    ):
        """
        Initialize the LLM service.

        Args:
            api_key: API key for the LLM provider
            base_url: Base URL for the LLM API
            model: Model name to use
            provider: Provider name
            cache_dir: Directory for caching
        """
        self.model = model
        self.provider = provider
        self.cache = LLMCache(cache_dir)
        
        if not api_key:
            logger.warning("No LLM API key provided. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI/OpenRouter client: {e}")
                self.client = None

    def generate_route_description(self, route: Route) -> Route:
        """
        Generate a creative name and description for the route.

        Args:
            route: The route to describe

        Returns:
            Route: The route with updated name and description
        """
        if not self.client:
            logger.info("LLM client not initialized, skipping description generation")
            return route

        try:
            summary = route.summary
            distance = route.distance_formatted
            duration = route.duration_formatted
            major_roads = ", ".join(route.major_roads) if route.major_roads else "local roads"

            prompt = (
                f"I have a driving route with the following details:\n"
                f"- Distance: {distance}\n"
                f"- Duration: {duration}\n"
                f"- Summary: {summary}\n"
                f"- Major Roads: {major_roads}\n\n"
                f"Please provide a creative, short name (max 5 words) and a "
                f"brief, helpful description (max 2 sentences) for this route. "
                f"The description should highlight the character of the route based on the roads used "
                f"(e.g., scenic, highway-heavy, direct, backroads).\n\n"
                f"Format the output as:\n"
                f"Name: [Route Name]\n"
                f"Description: [Route Description]"
            )

            # Check cache
            cached_response = self.cache.get(prompt, self.model)
            if cached_response:
                logger.info("Using cached LLM response")
                response_text = cached_response
            else:
                logger.info(f"Generating description for route via {summary} using {self.model}")
                
                # Add OpenRouter specific headers if needed via default_headers,
                # but standard OpenAI client works fine with just base_url usually.
                # OpenRouter recommends HTTP-Referer and X-Title, but they are optional.
                extra_headers = {}
                if self.provider == "openrouter":
                    extra_headers = {
                        "HTTP-Referer": "https://github.com/pathypotomus",
                        "X-Title": "Pathypotomus"
                    }

                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful navigation assistant that gives character to routes."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150,
                    extra_headers=extra_headers
                )

                response_text = completion.choices[0].message.content.strip()
                self.cache.set(prompt, self.model, response_text)
            
            # Parse the response
            lines = response_text.split('\n')
            name = None
            description = None

            for line in lines:
                if line.startswith("Name:"):
                    name = line.replace("Name:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()

            if name:
                route.name = name
            if description:
                route.description = description

            return route

        except OpenAIError as e:
            logger.error(f"LLM API error: {e}")
            # Return route unmodified on error, rather than raising, to allow graceful degradation
            return route
        except Exception as e:
            logger.error(f"Unexpected error generating description: {e}")
            return route
