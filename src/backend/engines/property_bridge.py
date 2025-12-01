"""
Property Bridge Engine - Connects library component properties to UI elements
Manages property editing, validation, and synchronization
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from .component_mapper import get_component_mapper
from .library_registry import get_library_registry


@dataclass
class PropertyValue:
    """Represents a single property value with metadata"""
    name: str
    value: Any
    unit: str
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    step: Optional[float] = None
    options: Optional[List[str]] = None
    description: str = ""


class PropertyBridge:
    """
    Bridges library component properties to UI components.
    Handles property editing, validation, and change notification.
    """
    
    def __init__(self):
        self.mapper = get_component_mapper()
        self.registry = get_library_registry()
        self.change_callbacks: Dict[str, List[Callable]] = {}
        self.property_cache: Dict[str, Dict[str, PropertyValue]] = {}
    
    def get_properties_for_component(self, comp_name: str) -> Dict[str, PropertyValue]:
        """
        Get all properties for a component as PropertyValue objects.
        These are used by the UI for editing.
        """
        # Check cache first
        if comp_name in self.property_cache:
            return self.property_cache[comp_name].copy()
        
        # Load from library
        props_dict = self.mapper.get_component_properties(comp_name)
        properties: Dict[str, PropertyValue] = {}
        
        for prop_name, prop_data in props_dict.items():
            if isinstance(prop_data, dict):
                prop_value = PropertyValue(
                    name=prop_name,
                    value=prop_data.get("value", ""),
                    unit=prop_data.get("unit", ""),
                    min_val=prop_data.get("min"),
                    max_val=prop_data.get("max"),
                    step=prop_data.get("step"),
                    options=prop_data.get("options"),
                    description=prop_data.get("description", ""),
                )
                properties[prop_name] = prop_value
        
        # Cache for quick retrieval
        self.property_cache[comp_name] = properties
        
        return properties
    
    def validate_property_value(self, comp_name: str, prop_name: str, value: Any) -> tuple[bool, str]:
        """
        Validate a property value against library constraints.
        Returns (is_valid, error_message)
        """
        props = self.get_properties_for_component(comp_name)
        
        if prop_name not in props:
            return False, f"Property '{prop_name}' not found for {comp_name}"
        
        prop = props[prop_name]
        
        # Check numeric constraints
        if prop.min_val is not None:
            try:
                val = float(value)
                if val < prop.min_val:
                    return False, f"Value {value} is below minimum {prop.min_val} {prop.unit}"
            except (ValueError, TypeError):
                pass
        
        if prop.max_val is not None:
            try:
                val = float(value)
                if val > prop.max_val:
                    return False, f"Value {value} exceeds maximum {prop.max_val} {prop.unit}"
            except (ValueError, TypeError):
                pass
        
        # Check options
        if prop.options and isinstance(value, str):
            if value not in prop.options:
                return False, f"'{value}' not in allowed options: {prop.options}"
        
        return True, ""
    
    def set_property_value(self, comp_name: str, prop_name: str, value: Any) -> bool:
        """
        Set a property value and notify subscribers.
        The actual component in the circuit will be updated via signal.
        """
        is_valid, error_msg = self.validate_property_value(comp_name, prop_name, value)
        
        if not is_valid:
            print(f"Property validation failed: {error_msg}")
            return False
        
        # Update cache
        if comp_name in self.property_cache:
            if prop_name in self.property_cache[comp_name]:
                self.property_cache[comp_name][prop_name].value = value
        
        # Notify subscribers
        self._notify_property_change(comp_name, prop_name, value)
        return True
    
    def get_property_description(self, comp_name: str, prop_name: str) -> str:
        """Get description for a property"""
        props = self.get_properties_for_component(comp_name)
        if prop_name in props:
            return props[prop_name].description
        return ""
    
    def get_property_constraints(self, comp_name: str, prop_name: str) -> Dict[str, Any]:
        """Get min/max/step constraints for a property"""
        props = self.get_properties_for_component(comp_name)
        if prop_name not in props:
            return {}
        
        prop = props[prop_name]
        return {
            "min": prop.min_val,
            "max": prop.max_val,
            "step": prop.step,
            "unit": prop.unit,
            "options": prop.options,
        }
    
    def subscribe_to_property_changes(self, comp_name: str, callback: Callable) -> None:
        """Subscribe to property changes for a component"""
        if comp_name not in self.change_callbacks:
            self.change_callbacks[comp_name] = []
        self.change_callbacks[comp_name].append(callback)
    
    def _notify_property_change(self, comp_name: str, prop_name: str, value: Any) -> None:
        """Notify all subscribers of property change"""
        if comp_name not in self.change_callbacks:
            return
        
        for callback in self.change_callbacks[comp_name]:
            try:
                callback(prop_name, value)
            except Exception as e:
                print(f"Error in property change callback: {e}")
    
    def clear_cache(self) -> None:
        """Clear property cache (useful when libraries are reloaded)"""
        self.property_cache.clear()


# Global property bridge instance
_global_bridge: Optional[PropertyBridge] = None


def get_property_bridge() -> PropertyBridge:
    """Get or create global property bridge"""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = PropertyBridge()
    return _global_bridge


def init_property_bridge() -> PropertyBridge:
    """Initialize property bridge"""
    global _global_bridge
    _global_bridge = PropertyBridge()
    return _global_bridge
