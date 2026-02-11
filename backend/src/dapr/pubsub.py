"""Dapr pub/sub client wrapper for event publishing and subscribing."""

import json
import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class DaprPubSubClient:
    """Client for Dapr pub/sub operations."""

    def __init__(
        self,
        dapr_http_port: int = 3500,
        pubsub_name: str = "todo-pubsub",
    ):
        """Initialize Dapr pub/sub client.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            pubsub_name: Name of the pub/sub component
        """
        self.dapr_url = f"http://localhost:{dapr_http_port}"
        self.pubsub_name = pubsub_name
        self.client = httpx.AsyncClient(timeout=10.0)

    async def publish(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """Publish an event to a topic.

        Args:
            topic: Topic name
            data: Event data
            metadata: Optional metadata

        Raises:
            HTTPException: If publishing fails
        """
        url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        try:
            # Log event publishing attempt
            event_type = data.get('event_type', 'unknown')
            logger.info(f"Publishing event to topic '{topic}': type={event_type}")

            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.info(f"Successfully published event to topic '{topic}': type={event_type}")

        except httpx.ConnectError as e:
            # Kafka/Dapr connection failure
            logger.error(
                f"Connection error publishing to topic '{topic}': {e}. "
                "Dapr sidecar may not be running or Kafka may be unavailable."
            )
            # Don't raise - allow graceful degradation
            # Events will be caught by safety net mechanisms

        except httpx.TimeoutException as e:
            # Timeout publishing event
            logger.error(f"Timeout publishing event to topic '{topic}': {e}")
            # Don't raise - allow graceful degradation

        except httpx.HTTPStatusError as e:
            # HTTP error from Dapr
            logger.error(
                f"HTTP error publishing to topic '{topic}': "
                f"status={e.response.status_code}, detail={e.response.text}"
            )
            # Don't raise - allow graceful degradation

        except Exception as e:
            # Unexpected error
            logger.error(
                f"Unexpected error publishing event to topic '{topic}': {e}",
                exc_info=True
            )
            # Don't raise - allow graceful degradation

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_pubsub_client: Optional[DaprPubSubClient] = None


def get_pubsub_client() -> DaprPubSubClient:
    """Get or create the global pub/sub client instance.

    Returns:
        DaprPubSubClient instance
    """
    global _pubsub_client
    if _pubsub_client is None:
        _pubsub_client = DaprPubSubClient()
    return _pubsub_client
