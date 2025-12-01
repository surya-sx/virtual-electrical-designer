"""
Component Library Manager - built-in and user component libraries
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


class ComponentDefinition:
    """Definition of a component in the library"""
    
    def __init__(self, name: str, category: str, description: str = ""):
        self.name = name
        self.category = category
        self.description = description
        self.parameters = {}
        self.ports = []
        
    def to_dict(self):
        return {
            "id": self.name.lower().replace(" ", "_"),
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "parameters": self.parameters,
            "ports": self.ports,
        }


class ComponentLibraryManager:
    """Manages built-in and user component libraries"""
    
    def __init__(self, builtin_lib_path: Optional[Path] = None, user_lib_path: Optional[Path] = None):
        self.builtin_lib_path = builtin_lib_path or Path(__file__).parent / "builtin_library.vedlib"
        self.user_lib_path = user_lib_path or Path.home() / ".ved" / "libraries" / "user_library.vedlib"
        self.builtin_components: Dict[str, ComponentDefinition] = {}
        self.user_components: Dict[str, ComponentDefinition] = {}
        
        self._load_builtin_library()
        self._load_user_library()
        self.load_extended_libraries()  # Load all JSON library files
        
    def _load_builtin_library(self):
        """Load built-in component library"""
        # Create default built-in components with parameters
        builtin_comps = {
            "Resistor": {
                "category": "Passive",
                "description": "Resistive element",
                "parameters": {"resistance": 1000.0},  # 1k ohm default
                "ports": 2,
                "symbol": "R",
            },
            "Capacitor": {
                "category": "Passive",
                "description": "Capacitive element",
                "parameters": {"capacitance": 1e-6},  # 1µF default
                "ports": 2,
                "symbol": "C",
            },
            "Inductor": {
                "category": "Passive",
                "description": "Inductive element",
                "parameters": {"inductance": 0.001},  # 1mH default
                "ports": 2,
                "symbol": "L",
            },
            "Voltage Source": {
                "category": "Sources",
                "description": "Ideal voltage source",
                "parameters": {"voltage": 5.0, "frequency": 0.0},
                "ports": 2,
                "symbol": "V",
            },
            "Current Source": {
                "category": "Sources",
                "description": "Ideal current source",
                "parameters": {"current": 0.001, "frequency": 0.0},
                "ports": 2,
                "symbol": "I",
            },
            "Diode": {
                "category": "Semiconductors",
                "description": "Ideal diode",
                "parameters": {"forward_voltage": 0.7},
                "ports": 2,
                "symbol": "D",
            },
            "BJT": {
                "category": "Semiconductors",
                "description": "Bipolar junction transistor",
                "parameters": {"hfe": 100, "vbe": 0.7},
                "ports": 3,
                "symbol": "Q",
            },
            "MOSFET": {
                "category": "Semiconductors",
                "description": "Metal-oxide-semiconductor transistor",
                "parameters": {"kp": 0.02, "vth": 1.0},
                "ports": 3,
                "symbol": "M",
            },
            "Transformer": {
                "category": "Power",
                "description": "Ideal transformer",
                "parameters": {"turns_ratio": 1.0, "coupling": 1.0},
                "ports": 4,
                "symbol": "T",
            },
            "Motor": {
                "category": "Power",
                "description": "DC motor model",
                "parameters": {"back_emf": 0.1, "resistance": 10.0},
                "ports": 2,
                "symbol": "M",
            },
            "Generator": {
                "category": "Power",
                "description": "AC generator model",
                "parameters": {"frequency": 50.0, "voltage": 230.0},
                "ports": 2,
                "symbol": "G",
            },
        }
        
        for name, config in builtin_comps.items():
            comp_def = ComponentDefinition(name, config["category"], config["description"])
            comp_def.parameters = config["parameters"]
            comp_def.ports = [{"id": i, "name": f"P{i+1}"} for i in range(config["ports"])]
            self.builtin_components[name] = comp_def
            
    def _load_user_library(self):
        """Load user component library"""
        if self.user_lib_path.exists():
            try:
                with open(self.user_lib_path, 'r') as f:
                    data = json.load(f)
                    for comp_data in data.get("components", []):
                        comp_def = ComponentDefinition(
                            comp_data["name"],
                            comp_data["category"],
                            comp_data.get("description", "")
                        )
                        self.user_components[comp_def.name] = comp_def
            except (json.JSONDecodeError, IOError):
                pass
                
    def get_component(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by name"""
        return self.builtin_components.get(name) or self.user_components.get(name)
        
    def list_components_by_category(self, category: str) -> List[ComponentDefinition]:
        """List components in a category"""
        all_components = {**self.builtin_components, **self.user_components}
        return [comp for comp in all_components.values() if comp.category == category]
        
    def get_all_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set()
        all_components = {**self.builtin_components, **self.user_components}
        for comp in all_components.values():
            categories.add(comp.category)
        return sorted(list(categories))
    
    def get_categories_with_components(self) -> Dict[str, List[Dict]]:
        """Get all categories with their components as dictionaries"""
        result = {}
        for category in self.get_all_categories():
            components = self.list_components_by_category(category)
            result[category] = [c.to_dict() for c in components]
        return result
    
    def load_extended_libraries(self, libraries_path: Optional[Path] = None):
        """Load extended component libraries from JSON files"""
        if libraries_path is None:
            libraries_path = Path(__file__).parent.parent.parent.parent / "data" / "libraries"
        
        if not libraries_path.exists():
            return
        
        # Load all available library files except library_index.json
        try:
            for lib_file in libraries_path.iterdir():
                if lib_file.suffix == '.json' and lib_file.name != 'library_index.json':
                    self._load_extended_library(lib_file)
        except Exception as e:
            print(f"Error loading extended libraries: {e}")
    
    def _load_extended_library(self, lib_path: Path):
        """Load a single extended library JSON file"""
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get library metadata
            library_category = data.get("category", "Other")
            
            # Load components from this library
            for comp_data in data.get("components", []):
                # Create component definition with library category
                comp_def = ComponentDefinition(
                    comp_data.get("name", "Unknown"),
                    library_category,  # Use library's category
                    comp_data.get("description", "")
                )
                
                # Add parameters from editable_properties if available
                if "editable_properties" in comp_data:
                    for prop_name, prop_data in comp_data["editable_properties"].items():
                        if isinstance(prop_data, dict):
                            comp_def.parameters[prop_name] = prop_data.get("value", 0)
                else:
                    comp_def.parameters = comp_data.get("parameters", {})
                
                # Add ports/pins - library files use editable_properties, so default to 2
                comp_def.ports = [{"id": "1", "name": "P1"}, {"id": "2", "name": "P2"}]
                
                # Store with unique key using component ID
                comp_id = comp_data.get("id", comp_data.get("name", "").lower().replace(" ", "_"))
                self.user_components[comp_id] = comp_def
                
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"Error loading library {lib_path}: {str(e)}")
        
    def list_all_components(self) -> Dict[str, ComponentDefinition]:
        """Get all components (builtin + user + extended)"""
        return {**self.builtin_components, **self.user_components}
    
    def search_components(self, query: str) -> List[ComponentDefinition]:
        """Search components by name or description"""
        all_components = self.list_all_components()
        query_lower = query.lower()
        results = []
        
        for comp in all_components.values():
            if (query_lower in comp.name.lower() or 
                query_lower in comp.description.lower() or
                query_lower in comp.category.lower()):
                results.append(comp)
        
        return sorted(results, key=lambda c: c.name)
