"""LLM service for generating route descriptions."""
import logging
from typing import Optional

from openai import OpenAI
from openai import OpenAIError

from pathypotomus.models.route import Route

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM generation fails."""


class LLMService:
    """Service for generating route descriptions using LLM."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        provider: str = "openai"
    ):
        """
        Initialize the LLM service.

        Args:
            api_key: API key for the LLM provider
            model: Model name to use
            provider: Provider name (currently only 'openai' supported)
        """
        self.model = model
        self.provider = provider
        
        if not api_key:
            logger.warning("No LLM API key provided. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
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

            logger.info(f"Generating description for route via {summary}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful navigation assistant that gives character to routes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            response_text = completion.choices[0].message.content.strip()
            
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
            logger.error(f"OpenAI API error: {e}")
            # Return route unmodified on error, rather than raising, to allow graceful degradation
            return route
        except Exception as e:
            logger.error(f"Unexpected error generating description: {e}")
            return route
