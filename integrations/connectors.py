# integrations/connectors.py

from typing import Dict, Callable, Optional


class ConnectorRegistry:
    def __init__(self):
        self.connectors: Dict[str, Callable] = {}

    def register(self, name: str, connector: Callable):
        self.connectors[name] = connector

    def get(self, name: str) -> Optional[Callable]:
        return self.connectors.get(name)


# GLOBAL INSTANCE
registry = ConnectorRegistry()
