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
            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info(f"Published event to topic '{topic}': {data.get('event_type')}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to publish event to topic '{topic}': {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to publish event: {str(e)}",
            )

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
