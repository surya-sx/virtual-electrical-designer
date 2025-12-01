"""
Engines Package - Core backend engines for component management and synchronization

Engines provide:
- LibraryRegistry: Central component registry from library files
- ComponentMapper: Maps library components to UI categories
- PropertyBridge: Connects properties to UI elements
"""

from .library_registry import (
    LibraryRegistry,
    ComponentDefinition,
    get_library_registry,
    init_library_registry,
)

from .component_mapper import (
    ComponentMapper,
    get_component_mapper,
    init_component_mapper,
)

from .property_bridge import (
    PropertyBridge,
    PropertyValue,
    get_property_bridge,
    init_property_bridge,
)

__all__ = [
    "LibraryRegistry",
    "ComponentDefinition",
    "get_library_registry",
    "init_library_registry",
    "ComponentMapper",
    "get_component_mapper",
    "init_component_mapper",
    "PropertyBridge",
    "PropertyValue",
    "get_property_bridge",
    "init_property_bridge",
]
