"""
Component Service

Manages component instances, their properties, and lifecycle.
Handles component creation, updates, deletion, and state management.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import uuid


class ComponentType(Enum):
    """Component type enumeration"""
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    DIODE = "diode"
    TRANSISTOR = "transistor"
    VOLTAGE_SOURCE = "voltage_source"
    CURRENT_SOURCE = "current_source"
    OP_AMP = "op_amp"
    IC = "ic"
    CONNECTOR = "connector"
    SWITCH = "switch"


@dataclass
class ComponentInstance:
    """Represents a component instance on the canvas"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    component_type: ComponentType = ComponentType.RESISTOR
    value: float = 0.0
    unit: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    connections: Dict[str, int] = field(default_factory=dict)  # pin -> node mapping
    position: tuple = field(default=(0, 0))  # x, y coordinates
    rotation: int = 0  # 0, 90, 180, 270
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComponentService:
    """
    Manages component instances and their operations.
    
    Responsibilities:
    - Create/read/update/delete component instances
    - Track component connections
    - Manage component properties
    - Validate component parameters
    """

    def __init__(self):
        self.components: Dict[str, ComponentInstance] = {}
        self.component_library: Dict[str, Dict[str, Any]] = {}

    def create_component(
        self,
        name: str,
        component_type: ComponentType,
        value: float,
        unit: str = "",
        properties: Optional[Dict[str, Any]] = None,
        position: tuple = (0, 0)
    ) -> ComponentInstance:
        """
        Create a new component instance.
        
        Args:
            name: Component name (e.g., "R1", "C1")
            component_type: Type of component
            value: Numeric value
            unit: Unit suffix (Ω, F, H, V, A)
            properties: Optional property dictionary
            position: Canvas position (x, y)
            
        Returns:
            ComponentInstance object
        """
        component = ComponentInstance(
            name=name,
            component_type=component_type,
            value=value,
            unit=unit,
            properties=properties or {},
            position=position
        )
        self.components[component.id] = component
        return component

    def get_component(self, component_id: str) -> Optional[ComponentInstance]:
        """Get component by ID"""
        return self.components.get(component_id)

    def get_component_by_name(self, name: str) -> Optional[ComponentInstance]:
        """Get component by name"""
        for component in self.components.values():
            if component.name == name:
                return component
        return None

    def get_all_components(self) -> List[ComponentInstance]:
        """Get all component instances"""
        return list(self.components.values())

    def get_components_by_type(self, component_type: ComponentType) -> List[ComponentInstance]:
        """Get all components of a specific type"""
        return [c for c in self.components.values() if c.component_type == component_type]

    def update_component(self, component_id: str, **kwargs) -> bool:
        """
        Update component properties.
        
        Args:
            component_id: Component ID
            **kwargs: Properties to update (value, unit, properties, position, rotation)
            
        Returns:
            True if successful
        """
        if component_id not in self.components:
            return False
        
        component = self.components[component_id]
        
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
            elif key == 'properties' and isinstance(value, dict):
                component.properties.update(value)
        
        return True

    def set_component_property(self, component_id: str, prop_name: str,
                               prop_value: Any) -> bool:
        """Set a specific component property"""
        if component_id not in self.components:
            return False
        
        self.components[component_id].properties[prop_name] = prop_value
        return True

    def get_component_property(self, component_id: str, prop_name: str) -> Optional[Any]:
        """Get a specific component property"""
        if component_id not in self.components:
            return None
        
        return self.components[component_id].properties.get(prop_name)

    def connect_component(self, component_id: str, pin: str, node: int) -> bool:
        """
        Connect a component pin to a circuit node.
        
        Args:
            component_id: Component ID
            pin: Pin name (e.g., "1", "2", "A", "B")
            node: Node number
            
        Returns:
            True if successful
        """
        if component_id not in self.components:
            return False
        
        self.components[component_id].connections[pin] = node
        return True

    def get_component_connections(self, component_id: str) -> Dict[str, int]:
        """Get all connections for a component"""
        if component_id not in self.components:
            return {}
        
        return dict(self.components[component_id].connections)

    def delete_component(self, component_id: str) -> bool:
        """Delete a component"""
        if component_id in self.components:
            del self.components[component_id]
            return True
        return False

    def clear_all_components(self) -> None:
        """Clear all components"""
        self.components.clear()

    def duplicate_component(self, component_id: str, name: str,
                           offset: tuple = (50, 50)) -> Optional[ComponentInstance]:
        """
        Duplicate an existing component with new position and name.
        
        Args:
            component_id: Component to duplicate
            name: New component name
            offset: Position offset from original
            
        Returns:
            New ComponentInstance or None if source not found
        """
        source = self.get_component(component_id)
        if not source:
            return None
        
        new_x = source.position[0] + offset[0]
        new_y = source.position[1] + offset[1]
        
        return self.create_component(
            name=name,
            component_type=source.component_type,
            value=source.value,
            unit=source.unit,
            properties=dict(source.properties),
            position=(new_x, new_y)
        )

    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about current components"""
        stats = {
            'total_components': len(self.components),
            'by_type': {},
            'connected': 0,
            'disconnected': 0,
        }
        
        for component_type in ComponentType:
            count = len(self.get_components_by_type(component_type))
            if count > 0:
                stats['by_type'][component_type.value] = count
        
        for component in self.components.values():
            if component.connections:
                stats['connected'] += 1
            else:
                stats['disconnected'] += 1
        
        return stats

    def to_dict(self, component_id: str) -> Dict[str, Any]:
        """Convert component to dictionary for serialization"""
        component = self.get_component(component_id)
        if not component:
            return {}
        
        return {
            'id': component.id,
            'name': component.name,
            'type': component.component_type.value,
            'value': component.value,
            'unit': component.unit,
            'properties': component.properties,
            'connections': component.connections,
            'position': component.position,
            'rotation': component.rotation,
            'metadata': component.metadata,
        }

    def from_dict(self, data: Dict[str, Any]) -> Optional[ComponentInstance]:
        """Create component from dictionary"""
        try:
            component_type = ComponentType(data['type'])
            component = self.create_component(
                name=data['name'],
                component_type=component_type,
                value=data['value'],
                unit=data.get('unit', ''),
                properties=data.get('properties', {}),
                position=tuple(data.get('position', (0, 0)))
            )
            component.id = data.get('id', component.id)
            component.rotation = data.get('rotation', 0)
            component.metadata = data.get('metadata', {})
            component.connections = data.get('connections', {})
            return component
        except Exception as e:
            print(f"Error creating component from dict: {e}")
            return None
