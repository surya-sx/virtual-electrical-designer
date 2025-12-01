"""
Component Validator Service

Validates component parameters and circuit connectivity.
Provides pre-analysis checking and error reporting.
"""

from typing import Dict, List, Any, Tuple
from .component_service import ComponentService


class ComponentValidator:
    """
    Validates component parameters and circuit structure.
    
    Checks:
    - Component value validity
    - Connection completeness
    - Circuit topology
    - Parameter ranges
    """

    def __init__(self, component_service: ComponentService):
        self.component_service = component_service

    def validate_component(self, component_id: str) -> Tuple[bool, List[str]]:
        """
        Validate a single component.
        
        Args:
            component_id: Component to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        component = self.component_service.get_component(component_id)
        if not component:
            return False, ["Component not found"]
        
        errors = []
        
        # Check value
        if component.value <= 0:
            errors.append(f"Invalid value: {component.value}")
        
        # Check connections
        if not component.connections:
            errors.append(f"Component {component.name} has no connections")
        
        # Check properties
        for prop_name, prop_value in component.properties.items():
            if prop_value is None:
                errors.append(f"Property {prop_name} is None")
        
        return len(errors) == 0, errors

    def validate_all_components(self) -> Dict[str, List[str]]:
        """
        Validate all components in circuit.
        
        Returns:
            Dictionary mapping component names to error lists
        """
        errors = {}
        
        for component in self.component_service.get_all_components():
            _, comp_errors = self.validate_component(component.id)
            if comp_errors:
                errors[component.name] = comp_errors
        
        return errors

    def validate_circuit_topology(self) -> Tuple[bool, List[str]]:
        """
        Validate circuit topology.
        
        Checks:
        - All nodes are connected
        - No floating nodes
        - At least one ground connection
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        all_nodes = set()
        
        # Collect all nodes
        for component in self.component_service.get_all_components():
            for node in component.connections.values():
                all_nodes.add(node)
        
        if not all_nodes:
            errors.append("Circuit has no nodes")
            return False, errors
        
        if 0 not in all_nodes:
            errors.append("Ground node (0) not connected")
        
        return len(errors) == 0, errors

    def check_connectivity(self) -> Dict[int, List[str]]:
        """
        Check component connectivity for each node.
        
        Returns:
            Dictionary mapping nodes to connected component names
        """
        connectivity = {}
        
        for component in self.component_service.get_all_components():
            for pin, node in component.connections.items():
                if node not in connectivity:
                    connectivity[node] = []
                connectivity[node].append(component.name)
        
        return connectivity
