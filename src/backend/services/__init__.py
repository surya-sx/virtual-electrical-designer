"""
Microservices Architecture for Virtual Electrical Designer

Individual services for component management, simulation, analysis, and utilities.
Each service is independently upgradeable and configurable.

Services:
- ConfigurationManager: System configuration management
- ComponentService: Component instance lifecycle
- LibraryService: Component library data management
- ComponentValidator: Parameter and connectivity validation
- SimulationCoordinator: High-level simulation orchestration
- DCAnalyzer: DC operating point analysis
- ACAnalyzer: AC frequency response analysis
- TransientAnalyzer: Time-domain transient analysis
- ParametricAnalyzer: Parameter sweep analysis
- MonteCarloAnalyzer: Statistical tolerance analysis
- ValueParser: Value string parsing and conversion
- UnitConverter: Unit conversion and electrical calculations
- ServiceManager: Central coordinator for all services
"""

from .configuration_manager import ConfigurationManager
from .component_service import ComponentService, ComponentType, ComponentInstance
from .library_service import LibraryService
from .component_validator import ComponentValidator
from .simulation_coordinator import SimulationCoordinator, AnalysisType, SimulationRequest
from .dc_analyzer import DCAnalyzer
from .ac_analyzer import ACAnalyzer
from .transient_analyzer import TransientAnalyzer
from .value_parser import ValueParser
from .unit_converter import UnitConverter, UnitSystem
from .service_manager import ServiceManager

__all__ = [
    'ConfigurationManager',
    'ComponentService',
    'ComponentType',
    'ComponentInstance',
    'LibraryService',
    'ComponentValidator',
    'SimulationCoordinator',
    'AnalysisType',
    'SimulationRequest',
    'DCAnalyzer',
    'ACAnalyzer',
    'TransientAnalyzer',
    'ValueParser',
    'UnitConverter',
    'UnitSystem',
    'ServiceManager',
]
