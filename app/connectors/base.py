"""
BaseConnector - Abstract interface for external service connectors in JARVIS / Liseth.
Standardizes authenticate, list_actions, and execute_action.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseConnector(ABC):
    def __init__(self, connector_id: str, name: str, description: str):
        self.id = connector_id
        self.name = name
        self.description = description
        self.connected = False

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticates with the target external service."""
        pass

    @abstractmethod
    def list_actions(self) -> List[Dict[str, Any]]:
        """
        Lists available callable actions.
        Each action dictionary includes:
        - name: str (identifier)
        - description: str
        - parameters: dict (schema)
        - sensitive: bool (requires user confirmation before execution)
        """
        pass

    @abstractmethod
    async def execute_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a specific action."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Returns connection status and metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connected": self.connected,
        }
