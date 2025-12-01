"""
Library Registry Engine - Manages all component definitions from library files
Provides centralized access to component data with hot-reload capability
"""
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ComponentDefinition:
    """Represents a single component with all its properties"""
    id: str
    name: str
    type: str
    category: str
    symbol: str
    description: str
    use_cases: Optional[str] = None
    editable_properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "symbol": self.symbol,
            "description": self.description,
            "use_cases": self.use_cases,
            "editable_properties": self.editable_properties,
        }


class LibraryRegistry:
    """
    Central registry for all components loaded from library files.
    Acts as single source of truth for component definitions.
    Supports hot-reload and change notifications.
    """
    
    def __init__(self, libraries_path: Path = None):
        self.libraries_path = libraries_path or Path("data/libraries")
        self.components: Dict[str, ComponentDefinition] = {}
        self.libraries: Dict[str, Dict[str, Any]] = {}
        self.change_callbacks: List[Callable] = []
        self.file_mtimes: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Load all libraries
        self._load_all_libraries()
    
    def _load_all_libraries(self) -> None:
        """Load all library JSON files from disk"""
        with self.lock:
            if not self.libraries_path.exists():
                print(f"Warning: Libraries path not found: {self.libraries_path}")
                return
            
            # Find all .json files in libraries folder
            for json_file in self.libraries_path.glob("*.json"):
                # Skip index files and other metadata
                if "index" in json_file.name or "README" in json_file.name:
                    continue
                
                self._load_library_file(json_file)
    
    def _load_library_file(self, filepath: Path) -> None:
        """Load a single library file and register its components"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lib_data = json.load(f)
            
            # Store raw library data
            lib_name = filepath.stem
            self.libraries[lib_name] = lib_data
            self.file_mtimes[str(filepath)] = filepath.stat().st_mtime
            
            # Register components from this library
            components = lib_data.get("components", [])
            for comp_data in components:
                comp_def = ComponentDefinition(
                    id=comp_data.get("id", comp_data.get("name", "")),
                    name=comp_data.get("name", ""),
                    type=comp_data.get("type", ""),
                    category=comp_data.get("type", ""),
                    symbol=comp_data.get("symbol", "?"),
                    description=comp_data.get("description", ""),
                    use_cases=comp_data.get("use_cases", ""),
                    editable_properties=comp_data.get("editable_properties", {}),
                )
                
                # Store by both ID and name for lookup
                self.components[comp_def.id] = comp_def
                self.components[comp_def.name] = comp_def
            
            print(f"[OK] Loaded library '{lib_name}': {len(components)} components")
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in {filepath}: {e}")
        except Exception as e:
            print(f"[ERROR] Error loading {filepath}: {e}")
    
    def reload_all(self) -> bool:
        """Reload all libraries from disk - useful for detecting file changes"""
        with self.lock:
            old_count = len(self.components)
            self.components.clear()
            self.libraries.clear()
            self._load_all_libraries()
            new_count = len(self.components)
            
            if new_count != old_count:
                self._notify_changes()
                return True
            return False
    
    def check_for_changes(self) -> bool:
        """Check if any library files have been modified on disk"""
        with self.lock:
            changed = False
            for json_file in self.libraries_path.glob("*.json"):
                if "index" in json_file.name or "README" in json_file.name:
                    continue
                
                current_mtime = json_file.stat().st_mtime
                old_mtime = self.file_mtimes.get(str(json_file), 0)
                
                if current_mtime > old_mtime:
                    print(f"Detected change in {json_file.name}")
                    self._load_library_file(json_file)
                    changed = True
            
            if changed:
                self._notify_changes()
            return changed
    
    def get_component(self, component_id: str) -> Optional[ComponentDefinition]:
        """Get a component definition by ID or name"""
        return self.components.get(component_id)
    
    def get_components_by_type(self, comp_type: str) -> List[ComponentDefinition]:
        """Get all components of a specific type (Resistor, Capacitor, etc.)"""
        return [c for c in self.components.values() if c.type == comp_type]
    
    def get_all_components(self) -> List[ComponentDefinition]:
        """Get all registered components"""
        # Return unique components (avoid duplicates from id/name keys)
        seen = set()
        result = []
        for comp in self.components.values():
            if comp.id not in seen:
                result.append(comp)
                seen.add(comp.id)
        return result
    
    def get_component_categories(self) -> Dict[str, List[ComponentDefinition]]:
        """Get components organized by category"""
        categories: Dict[str, List[ComponentDefinition]] = {}
        
        for comp in self.get_all_components():
            category = comp.category or "Other"
            if category not in categories:
                categories[category] = []
            if comp not in categories[category]:
                categories[category].append(comp)
        
        return categories
    
    def subscribe_to_changes(self, callback: Callable) -> None:
        """Subscribe to library changes. Callback receives (event_type, components_changed)"""
        self.change_callbacks.append(callback)
    
    def _notify_changes(self) -> None:
        """Notify all subscribers of changes"""
        for callback in self.change_callbacks:
            try:
                callback("library_updated", self.get_all_components())
            except Exception as e:
                print(f"Error in change callback: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        all_comps = self.get_all_components()
        categories = self.get_component_categories()
        
        return {
            "total_components": len(all_comps),
            "total_libraries": len(self.libraries),
            "categories": {k: len(v) for k, v in categories.items()},
            "library_names": list(self.libraries.keys()),
            "last_updated": datetime.now().isoformat(),
        }


# Global registry instance - accessible from anywhere
_global_registry: Optional[LibraryRegistry] = None


def get_library_registry() -> LibraryRegistry:
    """Get or create the global library registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = LibraryRegistry()
    return _global_registry


def init_library_registry(libraries_path: Optional[Path] = None) -> LibraryRegistry:
    """Initialize the global library registry with custom path"""
    global _global_registry
    _global_registry = LibraryRegistry(libraries_path)
    return _global_registry
