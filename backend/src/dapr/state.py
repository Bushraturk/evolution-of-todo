"""Dapr state management client wrapper."""

import json
import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class DaprStateClient:
    """Client for Dapr state management operations."""

    def __init__(
        self,
        dapr_http_port: int = 3500,
        state_store_name: str = "statestore",
    ):
        """Initialize Dapr state client.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            state_store_name: Name of the state store component
        """
        self.dapr_url = f"http://localhost:{dapr_http_port}"
        self.state_store_name = state_store_name
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state by key.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        url = f"{self.dapr_url}/v1.0/state/{self.state_store_name}/{key}"

        try:
            response = await self.client.get(url)
            if response.status_code == 204:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get state for key '{key}': {e}")
            return None

    async def save_state(
        self,
        key: str,
        value: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """Save state.

        Args:
            key: State key
            value: State value
            metadata: Optional metadata

        Raises:
            HTTPException: If saving fails
        """
        url = f"{self.dapr_url}/v1.0/state/{self.state_store_name}"

        state_data = [
            {
                "key": key,
                "value": value,
                "metadata": metadata or {},
            }
        ]

        try:
            response = await self.client.post(
                url,
                json=state_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info(f"Saved state for key '{key}'")
        except httpx.HTTPError as e:
            logger.error(f"Failed to save state for key '{key}': {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save state: {str(e)}",
            )

    async def delete_state(self, key: str) -> None:
        """Delete state by key.

        Args:
            key: State key
        """
        url = f"{self.dapr_url}/v1.0/state/{self.state_store_name}/{key}"

        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.info(f"Deleted state for key '{key}'")
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete state for key '{key}': {e}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_state_client: Optional[DaprStateClient] = None


def get_state_client() -> DaprStateClient:
    """Get or create the global state client instance.

    Returns:
        DaprStateClient instance
    """
    global _state_client
    if _state_client is None:
        _state_client = DaprStateClient()
    return _state_client
