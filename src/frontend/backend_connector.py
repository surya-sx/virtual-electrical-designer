"""
Direct Backend Connector
Direct integration between frontend and backend services (no HTTP API)
Uses Python module imports for efficient direct communication
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Setup paths for backend imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.service_manager import ServiceManager
from backend.circuit.project_manager import ProjectManager
from backend.circuit.circuit_model import Circuit
from backend.circuit.component_library import ComponentLibraryManager

logger = logging.getLogger(__name__)


class BackendConnector:
    """
    Direct connector to backend services
    Provides unified interface to all backend functionality
    """
    
    def __init__(self):
        """Initialize backend connector"""
        try:
            logger.info("Initializing backend services...")
            
            # Initialize service manager
            self.service_manager = ServiceManager()
            
            # Initialize project manager
            self.project_manager = ProjectManager()
            
            # Initialize component library
            self.component_library = ComponentLibraryManager()
            
            # Current circuit context
            self.current_circuit: Optional[Circuit] = None
            self.current_circuit_id: Optional[str] = None
            
            # Library change callbacks
            self.on_library_changed = []
            self._setup_library_callbacks()
            
            logger.info("✓ Backend services initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize backend services: {e}")
            raise
    
    def _setup_library_callbacks(self) -> None:
        """Setup callbacks for library changes from backend."""
        try:
            library_service = self.service_manager.library_service
            if library_service:
                library_service.register_change_callback(self._on_library_changed)
                logger.info("✓ Library change callbacks registered")
        except Exception as e:
            logger.warning(f"Could not register library callbacks: {e}")
    
    def _on_library_changed(self, library_name: str) -> None:
        """Called when a library file changes."""
        logger.info(f"Library changed: {library_name}")
        for callback in self.on_library_changed:
            try:
                callback(library_name)
            except Exception as e:
                logger.error(f"Error in library change callback: {e}")
    
    def register_library_change_callback(self, callback) -> None:
        """Register callback to be called when libraries change."""
        if callback not in self.on_library_changed:
            self.on_library_changed.append(callback)
    
    def unregister_library_change_callback(self, callback) -> None:
        """Unregister library change callback."""
        if callback in self.on_library_changed:
            self.on_library_changed.remove(callback)
    
    # ============================================================================
    # SYSTEM INFORMATION
    # ============================================================================
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return self.service_manager.get_system_info()
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            return self.service_manager.get_service_statistics()
        except Exception as e:
            logger.error(f"Error getting service statistics: {e}")
            return {}
    
    # ============================================================================
    # COMPONENT LIBRARY
    # ============================================================================
    
    def get_all_components(self) -> List[Dict]:
        """Get all available components"""
        try:
            components = self.component_library.get_all_components()
            return [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
        except Exception as e:
            logger.error(f"Error getting components: {e}")
            return []
    
    def get_component_categories(self) -> Dict[str, List]:
        """Get component categories"""
        try:
            return self.component_library.get_categories_with_components()
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return {}
    
    def get_components_by_category(self, category: str) -> List[Dict]:
        """Get components in a category"""
        try:
            components = self.component_library.list_components_by_category(category)
            return [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
        except Exception as e:
            logger.error(f"Error getting category components: {e}")
            return []
    
    def search_components(self, query: str) -> List[Dict]:
        """Search components by name/type"""
        try:
            results = self.service_manager.search_library(query)
            return [c.to_dict() if hasattr(c, 'to_dict') else c for c in results]
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            return []
    
    def get_component_details(self, component_id: str) -> Optional[Dict]:
        """Get component details"""
        try:
            component = self.component_library.get_component_by_id(component_id)
            if component:
                return component.to_dict() if hasattr(component, 'to_dict') else component
            return None
        except Exception as e:
            logger.error(f"Error getting component details: {e}")
            return None
    
    # ============================================================================
    # CIRCUIT MANAGEMENT
    # ============================================================================
    
    def create_new_circuit(self, name: str = "Untitled Circuit") -> str:
        """Create new circuit"""
        try:
            circuit = self.project_manager.create_circuit(name)
            self.current_circuit = circuit
            self.current_circuit_id = circuit.circuit_id if hasattr(circuit, 'circuit_id') else str(id(circuit))
            
            logger.info(f"Created circuit: {name}")
            return self.current_circuit_id
        except Exception as e:
            logger.error(f"Error creating circuit: {e}")
            raise
    
    def load_circuit(self, circuit_id: str) -> bool:
        """Load circuit by ID"""
        try:
            circuit = self.project_manager.load_circuit(circuit_id)
            if circuit:
                self.current_circuit = circuit
                self.current_circuit_id = circuit_id
                logger.info(f"Loaded circuit: {circuit_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading circuit: {e}")
            return False
    
    def save_circuit(self, circuit_id: Optional[str] = None) -> bool:
        """Save circuit"""
        try:
            cid = circuit_id or self.current_circuit_id
            if not cid or not self.current_circuit:
                logger.warning("No circuit to save")
                return False
            
            self.project_manager.save_circuit(self.current_circuit)
            logger.info(f"Saved circuit: {cid}")
            return True
        except Exception as e:
            logger.error(f"Error saving circuit: {e}")
            return False
    
    def get_current_circuit_id(self) -> Optional[str]:
        """Get current circuit ID"""
        return self.current_circuit_id
    
    # ============================================================================
    # CIRCUIT COMPONENTS
    # ============================================================================
    
    def add_component_to_circuit(
        self,
        component_id: str,
        x: float = 0,
        y: float = 0,
        rotation: float = 0,
        properties: Optional[Dict] = None
    ) -> Optional[str]:
        """Add component to current circuit"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return None
            
            instance_id = self.current_circuit.add_component(
                component_id=component_id,
                x=x,
                y=y,
                rotation=rotation,
                properties=properties or {}
            )
            
            logger.debug(f"Added component {component_id} as {instance_id}")
            return instance_id
        except Exception as e:
            logger.error(f"Error adding component: {e}")
            return None
    
    def update_component(
        self,
        instance_id: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        rotation: Optional[float] = None,
        properties: Optional[Dict] = None
    ) -> bool:
        """Update component"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return False
            
            self.current_circuit.update_component(
                instance_id=instance_id,
                x=x,
                y=y,
                rotation=rotation,
                properties=properties
            )
            
            logger.debug(f"Updated component {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating component: {e}")
            return False
    
    def delete_component(self, instance_id: str) -> bool:
        """Delete component"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return False
            
            self.current_circuit.delete_component(instance_id)
            logger.debug(f"Deleted component {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting component: {e}")
            return False
    
    def get_circuit_components(self) -> Dict[str, Any]:
        """Get all components in current circuit"""
        try:
            if not self.current_circuit:
                return {}
            
            return self.current_circuit.get_components()
        except Exception as e:
            logger.error(f"Error getting circuit components: {e}")
            return {}
    
    # ============================================================================
    # CIRCUIT CONNECTIONS
    # ============================================================================
    
    def add_connection(
        self,
        from_instance: str,
        from_port: str,
        to_instance: str,
        to_port: str
    ) -> Optional[str]:
        """Add connection between components"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return None
            
            connection_id = self.current_circuit.add_connection(
                from_instance=from_instance,
                from_port=from_port,
                to_instance=to_instance,
                to_port=to_port
            )
            
            logger.debug(f"Added connection {connection_id}")
            return connection_id
        except Exception as e:
            logger.error(f"Error adding connection: {e}")
            return None
    
    def delete_connection(self, connection_id: str) -> bool:
        """Delete connection"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return False
            
            self.current_circuit.delete_connection(connection_id)
            logger.debug(f"Deleted connection {connection_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting connection: {e}")
            return False
    
    def get_circuit_connections(self) -> Dict[str, Any]:
        """Get all connections in current circuit"""
        try:
            if not self.current_circuit:
                return {}
            
            return self.current_circuit.get_connections()
        except Exception as e:
            logger.error(f"Error getting circuit connections: {e}")
            return {}
    
    # ============================================================================
    # CIRCUIT ANALYSIS
    # ============================================================================
    
    def validate_circuit(self) -> Tuple[bool, List[str], List[str]]:
        """Validate circuit"""
        try:
            if not self.current_circuit:
                return False, ["No active circuit"], []
            
            errors = []
            warnings = []
            
            # Check for unconnected components
            if len(self.current_circuit.get_components()) > 0:
                if len(self.current_circuit.get_connections()) == 0:
                    warnings.append("Circuit has no connections")
            
            # Check for isolated nodes
            components = self.current_circuit.get_components()
            connections = self.current_circuit.get_connections()
            
            connected_instances = set()
            for conn in connections.values():
                connected_instances.add(conn.get('from_instance'))
                connected_instances.add(conn.get('to_instance'))
            
            for instance_id in components.keys():
                if instance_id not in connected_instances:
                    warnings.append(f"Component {instance_id} is not connected")
            
            return len(errors) == 0, errors, warnings
        
        except Exception as e:
            logger.error(f"Error validating circuit: {e}")
            return False, [str(e)], []
    
    def run_dc_analysis(self) -> Optional[Dict]:
        """Run DC analysis"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return None
            
            logger.info("Running DC analysis...")
            dc_analyzer = self.service_manager.get_service('dc')
            
            # Setup analysis with circuit data
            results = dc_analyzer.analyze(self.current_circuit.get_circuit_data())
            logger.info("DC analysis completed")
            return results
        except Exception as e:
            logger.error(f"Error running DC analysis: {e}")
            return None
    
    def run_ac_analysis(
        self,
        frequency_start: float = 1,
        frequency_end: float = 1e6,
        points: int = 100
    ) -> Optional[Dict]:
        """Run AC analysis"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return None
            
            logger.info("Running AC analysis...")
            ac_analyzer = self.service_manager.get_service('ac')
            
            results = ac_analyzer.analyze(
                self.current_circuit.get_circuit_data(),
                frequency_start=frequency_start,
                frequency_end=frequency_end,
                points=points
            )
            logger.info("AC analysis completed")
            return results
        except Exception as e:
            logger.error(f"Error running AC analysis: {e}")
            return None
    
    def run_transient_analysis(
        self,
        duration: float = 1.0,
        time_step: float = 0.001
    ) -> Optional[Dict]:
        """Run transient analysis"""
        try:
            if not self.current_circuit:
                logger.error("No active circuit")
                return None
            
            logger.info("Running transient analysis...")
            transient_analyzer = self.service_manager.get_service('transient')
            
            results = transient_analyzer.analyze(
                self.current_circuit.get_circuit_data(),
                duration=duration,
                time_step=time_step
            )
            logger.info("Transient analysis completed")
            return results
        except Exception as e:
            logger.error(f"Error running transient analysis: {e}")
            return None


# Global instance
_backend_connector: Optional[BackendConnector] = None


def get_backend_connector() -> BackendConnector:
    """Get global backend connector instance"""
    global _backend_connector
    if _backend_connector is None:
        _backend_connector = BackendConnector()
    return _backend_connector


def reset_backend_connector():
    """Reset backend connector"""
    global _backend_connector
    _backend_connector = None
