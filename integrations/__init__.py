# integrations/__init__.py

from .external_apis import ExternalAPIClient
from .exporters import ExporterManager
from .connectors import ConnectorRegistry, registry

# GLOBAL INSTANCES (VERY USEFUL)
external_api = ExternalAPIClient()
exporter = ExporterManager()

__all__ = [
    "ExternalAPIClient",
    "ExporterManager",
    "ConnectorRegistry",
    "registry",
    "external_api",
    "exporter"
]
