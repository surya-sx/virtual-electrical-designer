# Virtual Electrical Designer - Microservices Architecture

## Overview

The Virtual Electrical Designer uses a modular microservices architecture with independent, loosely-coupled services that can be upgraded, configured, and tested independently.

## Core Services

### Data Services
- **ConfigurationManager** - Manages system configuration with profiles and runtime updates
- **ComponentService** - Manages component instances and lifecycle (CRUD operations)
- **LibraryService** - Loads and provides access to component library data
- **ComponentValidator** - Validates component parameters and circuit connectivity

### Analysis Services
- **DCAnalyzer** - DC operating point analysis using modified nodal analysis
- **ACAnalyzer** - AC frequency sweep with phasor and complex impedance analysis
- **TransientAnalyzer** - Time-domain analysis with ODE solving (RK45, BDF)
- **ParametricAnalyzer** - Parameter sweep analysis for sensitivity studies
- **MonteCarloAnalyzer** - Statistical analysis with component tolerances

### Utility Services
- **ValueParser** - Parses component values ("1k", "100n", "1M") and conversions
- **UnitConverter** - Converts between electrical units and performs calculations
- **SimulationCoordinator** - High-level simulation orchestration and request queuing

### Master Service
- **ServiceManager** - Central coordinator that manages all services and provides unified interface

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Service Manager                           │
│  (Central Orchestrator - coordinates all services)          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐   ┌──────▼────┐  ┌───────▼───┐
    │  Data  │   │ Analysis  │  │ Utilities │
    │Services│   │ Services  │  │ Services  │
    └────────┘   └───────────┘  └───────────┘
        │                │                │
   Config         DC/AC/Transient    ValueParser
   Component      Parametric         UnitConverter
   Library        MonteCarlo
   Validator
```

## Configuration

Configuration is managed through:
1. **default_config.json** - System-wide defaults
2. **services_manifest.json** - Service descriptions and metadata
3. Runtime configuration updates via ConfigurationManager

### Configuration Structure

```json
{
  "system": {
    "debug_mode": false,
    "log_level": "INFO",
    "enable_profiling": false
  },
  "simulation": {
    "max_iterations": 1000,
    "convergence_tolerance": 1e-6,
    "time_step_default": 1e-6,
    "transient_solver": "RK45"
  },
  "component": {
    "library_path": "data/libraries",
    "auto_load_on_start": true,
    "cache_libraries": true
  },
  "service": {
    "enable_threading": true,
    "thread_pool_size": 4,
    "service_timeout": 30
  }
}
```

## Using the Services

### Basic Usage

```python
from src.backend.services import ServiceManager

# Initialize service manager
manager = ServiceManager()

# Parse component values
resistance = manager.parse_value("1.5k")  # Returns 1500

# Create components
component = manager.create_component(
    name="R1",
    comp_type="resistor",
    value=1000,
    unit="Ω"
)

# Search library
components = manager.search_library("100n")

# Convert units
voltage_in_mV = manager.convert_unit(5, 'V', 'mV')

# Get system info
info = manager.get_system_info()
```

### DC Analysis

```python
from src.backend.services import ServiceManager

manager = ServiceManager()
dc = manager.dc_analyzer

# Add components
dc.add_resistor("R1", 1, 0, 1000)
dc.add_resistor("R2", 2, 1, 2000)
dc.add_voltage_source("V1", 2, 0, 5)

# Run analysis
result = dc.solve(num_nodes=3)
print(result['node_voltages'])  # Node voltages
print(result['currents'])        # Component currents
print(result['power'])          # Power dissipation
```

### AC Analysis

```python
from src.backend.services import ServiceManager
import numpy as np

manager = ServiceManager()
ac = manager.ac_analyzer

# Add components
ac.add_resistor("R1", 1, 0, 1000)
ac.add_capacitor("C1", 2, 1, 1e-6)
ac.add_voltage_source("V1", 2, 0, 1, 0)

# Frequency sweep
frequencies = np.logspace(0, 5, 100)  # 1 Hz to 100 kHz
result = ac.solve(frequencies, num_nodes=3)

# Access frequency response
for freq in result['response']:
    print(f"At {freq} Hz: {result['response'][freq]['node_voltages']}")
```

### Component Management

```python
from src.backend.services import ServiceManager, ComponentType

manager = ServiceManager()
comp_service = manager.component_service

# Create component
component = comp_service.create_component(
    name="R1",
    component_type=ComponentType.RESISTOR,
    value=1000,
    unit="Ω",
    position=(100, 50)
)

# Update component
comp_service.update_component(component.id, value=2000, rotation=90)

# Connect pins
comp_service.connect_component(component.id, "1", 1)
comp_service.connect_component(component.id, "2", 0)

# Get statistics
stats = comp_service.get_component_stats()
```

### Library Operations

```python
from src.backend.services import ServiceManager

manager = ServiceManager()
lib = manager.library_service

# Get library statistics
stats = lib.get_library_stats()
print(f"Total components: {stats['total_components']}")

# Search components
results = lib.search_components("1k", library_name="resistors")

# Get component details
resistor = lib.get_component("resistors", "r_1k")
print(resistor['description'])
print(resistor['instructions'])

# Validate library
validation = lib.validate_library_structure("resistors")
```

## Service Upgrade Patterns

### Adding a New Analysis Type

1. Create new file: `src/backend/services/my_analyzer.py`
2. Implement analyzer class following the pattern
3. Add to ServiceManager.__init__()
4. Update services/__init__.py exports

### Adding New Components

1. Update ComponentType enum in component_service.py
2. Create library JSON file in data/libraries/
3. Service auto-loads on startup

### Custom Configuration

1. Create profile config: `config/profile_config.json`
2. Load with: `ConfigurationManager('config/profile_config.json')`
3. Update values at runtime: `config.set_simulation_config('key', value)`

## Performance Features

- **Library Caching** - Components libraries cached in memory
- **Result Caching** - Simulation results cached via SimulationCoordinator
- **Threading Support** - Parallel analysis execution
- **Sparse Matrix Support** - Efficient circuit solver for large circuits

## Error Handling

All services include:
- Validation before operations
- Descriptive error messages
- Graceful degradation
- Error tracking in ServiceManager

```python
manager = ServiceManager()
try:
    result = manager.dc_analyzer.solve()
except Exception as e:
    print(f"Analysis error: {e}")
    # Service stats track errors
    print(manager.get_service_statistics())
```

## Testing Services Independently

Each service can be tested independently:

```python
# Test value parser
from src.backend.services import ValueParser
assert ValueParser.parse("1k") == 1000
assert ValueParser.parse("100n") == 1e-7

# Test unit converter
from src.backend.services import UnitConverter
assert UnitConverter.convert(1000, 'Ω', 'kΩ') == 1

# Test component service
from src.backend.services import ComponentService, ComponentType
cs = ComponentService()
comp = cs.create_component("R1", ComponentType.RESISTOR, 1000)
assert comp.name == "R1"
```

## File Structure

```
src/backend/services/
├── __init__.py                    # Service exports
├── configuration_manager.py       # Configuration management
├── component_service.py           # Component lifecycle
├── library_service.py             # Library data
├── component_validator.py         # Validation
├── simulation_coordinator.py      # Request orchestration
├── dc_analyzer.py                 # DC analysis
├── ac_analyzer.py                 # AC analysis
├── transient_analyzer.py          # Transient analysis
├── parametric_analyzer.py         # Parameter sweeps
├── monte_carlo_analyzer.py        # Statistical analysis
├── value_parser.py                # Value parsing
├── unit_converter.py              # Unit conversion
└── service_manager.py             # Master coordinator

config/
├── default_config.json            # Default settings
└── services_manifest.json         # Service metadata

data/libraries/
├── resistors.json
├── capacitors.json
├── inductors.json
├── diodes.json
├── transistors.json
└── sources.json
```

## Key Advantages

✅ **Modularity** - Each service has single responsibility  
✅ **Testability** - Services can be tested independently  
✅ **Upgradability** - Update services without affecting others  
✅ **Configurability** - Runtime configuration changes  
✅ **Extensibility** - Easy to add new services or analyzers  
✅ **Scalability** - Parallel execution support  
✅ **Maintainability** - Clear interfaces and documentation  

## Future Enhancements

- REST API for service operations
- Service health monitoring
- Automatic backup/recovery
- Advanced caching strategies
- Distributed simulation support
- Real-time analysis monitoring
