"""
Component Mapper Engine - Maps library components to UI representations
Handles component categorization, search, and UI element generation
"""
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from .library_registry import get_library_registry, ComponentDefinition


class ComponentMapper:
    """
    Maps library components to UI categories and representations.
    Automatically generates UI structure from library data.
    """
    
    def __init__(self):
        self.registry = get_library_registry()
        self.component_cache: Dict[str, ComponentDefinition] = {}
        self.category_cache: Dict[str, List[Tuple[str, str]]] = {}
        self._build_ui_structure()
    
    def _build_ui_structure(self) -> None:
        """Build UI categories from library components"""
        categories = self.registry.get_component_categories()
        
        self.category_cache.clear()
        
        for category, components in categories.items():
            if category not in self.category_cache:
                self.category_cache[category] = []
            
            for comp in components:
                # Create tuple: (component_type, component_name)
                # component_type comes from comp.type or comp.category
                comp_type = comp.type or comp.category or "Generic"
                self.category_cache[category].append((comp_type, comp.name))
                
                # Cache the component for quick lookup
                self.component_cache[comp.name] = comp
                self.component_cache[comp.id] = comp
    
    def refresh(self) -> None:
        """Refresh UI structure from updated registry"""
        self._build_ui_structure()
    
    def get_ui_categories(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Get all UI categories with components.
        Returns: {category_name: [(comp_type, comp_name), ...]}
        """
        return self.category_cache.copy()
    
    def get_category_items(self, category: str) -> List[Tuple[str, str]]:
        """Get components for a specific category"""
        return self.category_cache.get(category, [])
    
    def get_component_by_name(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by display name"""
        return self.component_cache.get(name)
    
    def search_components(self, query: str) -> List[ComponentDefinition]:
        """Search components by name, description, or use cases"""
        query_lower = query.lower()
        results = []
        
        for comp in self.registry.get_all_components():
            if (query_lower in comp.name.lower() or
                query_lower in comp.description.lower() or
                (comp.use_cases and query_lower in comp.use_cases.lower())):
                results.append(comp)
        
        return results
    
    def get_component_properties(self, comp_name: str) -> Dict[str, Any]:
        """Get all editable properties for a component"""
        comp = self.get_component_by_name(comp_name)
        if comp:
            return comp.editable_properties
        return {}
    
    def get_component_description(self, comp_name: str) -> str:
        """Get full description of a component"""
        comp = self.get_component_by_name(comp_name)
        if comp:
            desc = f"{comp.description}\n\n"
            if comp.use_cases:
                desc += f"Use Cases: {comp.use_cases}"
            return desc
        return ""
    
    def get_component_info(self, comp_name: str) -> Dict[str, Any]:
        """Get complete component information for UI display"""
        comp = self.get_component_by_name(comp_name)
        if not comp:
            return {}
        
        return {
            "id": comp.id,
            "name": comp.name,
            "type": comp.type,
            "symbol": comp.symbol,
            "description": comp.description,
            "use_cases": comp.use_cases,
            "properties": comp.editable_properties,
            "property_count": len(comp.editable_properties),
        }
    
    def get_all_components_flat(self) -> List[Dict[str, Any]]:
        """Get all components as flat list with info"""
        return [comp.to_dict() for comp in self.registry.get_all_components()]


# Global mapper instance
_global_mapper: Optional['ComponentMapper'] = None


def get_component_mapper() -> ComponentMapper:
    """Get or create global component mapper"""
    global _global_mapper
    if _global_mapper is None:
        _global_mapper = ComponentMapper()
    return _global_mapper


def init_component_mapper() -> ComponentMapper:
    """Initialize component mapper"""
    global _global_mapper
    _global_mapper = ComponentMapper()
    return _global_mapper
