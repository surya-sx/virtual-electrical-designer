"""
Service Manager

Central coordinator for all microservices.
Manages service lifecycle, configuration, and inter-service communication.
"""

from typing import Dict, Any, Optional
from .configuration_manager import ConfigurationManager
from .component_service import ComponentService
from .library_service import LibraryService
from .value_parser import ValueParser
from .unit_converter import UnitConverter
from .dc_analyzer import DCAnalyzer
from .ac_analyzer import ACAnalyzer
from .transient_analyzer import TransientAnalyzer


class ServiceManager:
    """
    Central service manager and orchestrator.
    
    Coordinates all microservices and provides unified interface.
    """

    def __init__(self, config_file: Optional[str] = None):
        # Configuration
        self.config = ConfigurationManager(config_file)
        
        # Data services
        self.component_service = ComponentService()
        self.library_service = LibraryService(self.config.get_component_config().library_path)
        
        # Utility services
        self.value_parser = ValueParser
        self.unit_converter = UnitConverter
        
        # Analysis services
        self.dc_analyzer = DCAnalyzer()
        self.ac_analyzer = ACAnalyzer()
        self.transient_analyzer = TransientAnalyzer()
        
        self._service_stats = {
            'components_processed': 0,
            'analyses_completed': 0,
            'errors_encountered': 0
        }

    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get a service by name.
        
        Args:
            service_name: Service identifier
            
        Returns:
            Service instance or None
        """
        services = {
            'config': self.config,
            'component': self.component_service,
            'library': self.library_service,
            'dc': self.dc_analyzer,
            'ac': self.ac_analyzer,
            'transient': self.transient_analyzer,
        }
        return services.get(service_name)

    def get_all_services(self) -> Dict[str, Any]:
        """Get all services"""
        return {
            'config': self.config,
            'component': self.component_service,
            'library': self.library_service,
            'dc': self.dc_analyzer,
            'ac': self.ac_analyzer,
            'transient': self.transient_analyzer,
        }

    def parse_value(self, value_str: str) -> float:
        """Parse component value string"""
        return self.value_parser.parse(value_str)

    def format_value(self, value: float, unit: str = '', precision: int = 3) -> str:
        """Format numeric value with prefix"""
        return self.value_parser.format_value(value, unit, precision)

    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units"""
        return self.unit_converter.convert(value, from_unit, to_unit)

    def get_common_units(self, category: str) -> list:
        """Get common units for category"""
        return self.unit_converter.get_common_units(category)

    def create_component(self, name: str, comp_type: str, value: float,
                        unit: str = "", **kwargs) -> Optional[Any]:
        """Create component instance"""
        from .component_service import ComponentType
        try:
            component_type = ComponentType(comp_type)
            return self.component_service.create_component(
                name=name,
                component_type=component_type,
                value=value,
                unit=unit,
                **kwargs
            )
        except Exception as e:
            self._service_stats['errors_encountered'] += 1
            print(f"Error creating component: {e}")
            return None

    def get_component_stats(self) -> Dict[str, Any]:
        """Get component statistics"""
        return self.component_service.get_component_stats()

    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        return self.library_service.get_library_stats()

    def search_library(self, query: str, library: Optional[str] = None) -> list:
        """Search component library"""
        return self.library_service.search_components(query, library)

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service usage statistics"""
        return {
            'service_stats': self._service_stats,
            'components': self.component_service.get_component_stats(),
            'libraries': self.library_service.get_library_stats(),
        }

    def reload_configuration(self) -> None:
        """Reload configuration from disk"""
        self.config = ConfigurationManager()

    def reload_libraries(self) -> None:
        """Reload all component libraries"""
        self.library_service.reload_all_libraries()

    def reset_services(self) -> None:
        """Reset all services to initial state"""
        self.component_service.clear_all_components()
        self.dc_analyzer.clear()
        self.ac_analyzer.clear()
        self.transient_analyzer.clear()
        self._service_stats = {
            'components_processed': 0,
            'analyses_completed': 0,
            'errors_encountered': 0
        }

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        return {
            'system': self.config.get_system_config(),
            'simulation': self.config.get_simulation_config(),
            'component': self.config.get_component_config(),
            'service': self.config.get_service_config(),
        }

    def export_system_state(self) -> Dict[str, Any]:
        """Export complete system state for serialization"""
        return {
            'configuration': self.config.get_all_config(),
            'components': [
                self.component_service.to_dict(comp_id)
                for comp_id in [c.id for c in self.component_service.get_all_components()]
            ],
            'statistics': self.get_service_statistics(),
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get complete system information"""
        return {
            'version': '1.0',
            'services': list(self.get_all_services().keys()),
            'libraries': self.library_service.get_library_names(),
            'components': self.get_component_stats(),
            'statistics': self.get_service_statistics(),
        }
