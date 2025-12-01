"""
Configuration Manager Service

Handles all configuration loading, validation, defaults, and system settings.
Supports multiple configuration profiles and environment-specific settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SimulationConfig:
    """Simulation engine configuration"""
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-6
    time_step_default: float = 1e-6
    frequency_points_default: int = 100
    transient_solver: str = 'RK45'  # RK45, BDF, LSODA
    enable_caching: bool = True


@dataclass
class ComponentConfig:
    """Component library configuration"""
    library_path: str = 'data/libraries'
    auto_load_on_start: bool = True
    cache_libraries: bool = True
    validation_strict: bool = False


@dataclass
class ServiceConfig:
    """Service configuration"""
    enable_threading: bool = True
    thread_pool_size: int = 4
    service_timeout: int = 30  # seconds
    retry_attempts: int = 3


@dataclass
class SystemConfig:
    """Overall system configuration"""
    debug_mode: bool = False
    log_level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR
    enable_profiling: bool = False


class ConfigurationManager:
    """
    Manages all system configuration with support for:
    - Multiple configuration profiles
    - Environment-specific overrides
    - Runtime configuration updates
    - Configuration validation
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or 'config/default_config.json'
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profile = 'default'
        self.system_config = SystemConfig()
        self.simulation_config = SimulationConfig()
        self.component_config = ComponentConfig()
        self.service_config = ServiceConfig()
        
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self._apply_configuration(config_data)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                self._use_defaults()
        else:
            self._use_defaults()

    def _use_defaults(self) -> None:
        """Use default configuration values"""
        self.system_config = SystemConfig()
        self.simulation_config = SimulationConfig()
        self.component_config = ComponentConfig()
        self.service_config = ServiceConfig()

    def _apply_configuration(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data from file"""
        if 'system' in config_data:
            for key, value in config_data['system'].items():
                setattr(self.system_config, key, value)
        
        if 'simulation' in config_data:
            for key, value in config_data['simulation'].items():
                setattr(self.simulation_config, key, value)
        
        if 'component' in config_data:
            for key, value in config_data['component'].items():
                setattr(self.component_config, key, value)
        
        if 'service' in config_data:
            for key, value in config_data['service'].items():
                setattr(self.service_config, key, value)

    def get_simulation_config(self) -> SimulationConfig:
        """Get simulation configuration"""
        return self.simulation_config

    def get_component_config(self) -> ComponentConfig:
        """Get component configuration"""
        return self.component_config

    def get_service_config(self) -> ServiceConfig:
        """Get service configuration"""
        return self.service_config

    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.system_config

    def set_simulation_config(self, key: str, value: Any) -> None:
        """Update simulation configuration at runtime"""
        if hasattr(self.simulation_config, key):
            setattr(self.simulation_config, key, value)
        else:
            raise KeyError(f"Unknown simulation config key: {key}")

    def set_component_config(self, key: str, value: Any) -> None:
        """Update component configuration at runtime"""
        if hasattr(self.component_config, key):
            setattr(self.component_config, key, value)
        else:
            raise KeyError(f"Unknown component config key: {key}")

    def get_library_path(self) -> str:
        """Get library data path"""
        base_path = Path(__file__).parent.parent.parent.parent
        return str(base_path / self.component_config.library_path)

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'system': asdict(self.system_config),
            'simulation': asdict(self.simulation_config),
            'component': asdict(self.component_config),
            'service': asdict(self.service_config),
        }

    def save_configuration(self, filepath: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        filepath = filepath or self.config_file
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.get_all_config(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
