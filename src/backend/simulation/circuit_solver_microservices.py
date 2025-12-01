"""
Circuit Solver Microservices Adapter
Bridges the existing CircuitSolver interface with new microservices architecture
Provides backward compatibility while leveraging all new services
"""
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# Add parent path to imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import (
    ServiceManager, 
    DCAnalyzer, 
    ACAnalyzer, 
    TransientAnalyzer,
    ComponentService,
    ComponentValidator,
    SimulationCoordinator
)


class CircuitSolverMicroservices:
    """
    Enhanced circuit solver using the new microservices architecture
    Provides the same interface as CircuitSolver but uses ServiceManager internally
    """
    
    def __init__(self):
        """Initialize with ServiceManager"""
        self.service_manager = ServiceManager()
        self.dc_analyzer = self.service_manager.dc_analyzer
        self.ac_analyzer = self.service_manager.ac_analyzer
        self.transient_analyzer = self.service_manager.transient_analyzer
        self.component_service = self.service_manager.component_service
        self.library_service = self.service_manager.library_service
        
        self.nodes: Dict[str, int] = {}
        self.node_counter = 0
        self.components_list: List[Dict] = []
        self.circuit_name = "Circuit"
    
    def add_node(self, node_name: str) -> int:
        """Add node and return its index"""
        if node_name not in self.nodes:
            if node_name.lower() in ["gnd", "ground", "0"]:
                self.nodes[node_name] = 0
            else:
                self.node_counter += 1
                self.nodes[node_name] = self.node_counter
        return self.nodes[node_name]
    
    def add_resistor(self, name: str, node1: str, node2: str, resistance: float):
        """Add resistor with value in Ohms"""
        if resistance <= 0:
            raise ValueError(f"Resistor {name}: resistance must be positive, got {resistance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.dc_analyzer.add_resistor(name, n1, n2, resistance)
        self.ac_analyzer.add_resistor(name, n1, n2, resistance)
        self.transient_analyzer.add_resistor(name, n1, n2, resistance)
        
        self.components_list.append({
            'type': 'resistor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': resistance,
        })
    
    def add_capacitor(self, name: str, node1: str, node2: str, capacitance: float):
        """Add capacitor with value in Farads"""
        if capacitance <= 0:
            raise ValueError(f"Capacitor {name}: capacitance must be positive, got {capacitance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.ac_analyzer.add_capacitor(name, n1, n2, capacitance)
        self.transient_analyzer.add_capacitor(name, n1, n2, capacitance)
        
        self.components_list.append({
            'type': 'capacitor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': capacitance,
        })
    
    def add_inductor(self, name: str, node1: str, node2: str, inductance: float):
        """Add inductor with value in Henries"""
        if inductance <= 0:
            raise ValueError(f"Inductor {name}: inductance must be positive, got {inductance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.ac_analyzer.add_inductor(name, n1, n2, inductance)
        self.transient_analyzer.add_inductor(name, n1, n2, inductance)
        
        self.components_list.append({
            'type': 'inductor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': inductance,
        })
    
    def add_voltage_source(self, name: str, node_pos: str, node_neg: str, voltage: float):
        """Add voltage source with value in Volts"""
        n_pos = self.add_node(node_pos)
        n_neg = self.add_node(node_neg)
        
        self.dc_analyzer.add_voltage_source(name, n_pos, n_neg, voltage)
        self.ac_analyzer.add_voltage_source(name, n_pos, n_neg, voltage, phase=0)
        # For transient, add as pulse with rise at t=0
        self.transient_analyzer.add_pulse_source(name, n_pos, n_neg, 0, voltage, 0)
        
        self.components_list.append({
            'type': 'voltage_source',
            'name': name,
            'node_pos': n_pos,
            'node_neg': n_neg,
            'value': voltage,
        })
    
    def add_current_source(self, name: str, node1: str, node2: str, current: float):
        """Add current source with value in Amperes"""
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.dc_analyzer.add_current_source(name, n1, n2, current)
        
        self.components_list.append({
            'type': 'current_source',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': current,
        })
    
    def dc_analysis(self) -> Dict:
        """Perform DC analysis using DCAnalyzer service"""
        try:
            if not self.nodes:
                return {'status': 'failed', 'error': 'No nodes in circuit'}
            
            num_nodes = max(self.nodes.values()) + 1
            result = self.dc_analyzer.solve(num_nodes)
            
            # Ensure result has all required fields
            if isinstance(result, dict) and result.get('node_voltages') is not None:
                return {
                    'status': 'success',
                    'node_voltages': result.get('node_voltages'),
                    'node_names': {name: result['node_voltages'][idx] 
                                  for name, idx in self.nodes.items() 
                                  if idx < len(result['node_voltages'])},
                    'component_currents': result.get('currents', {}),
                    'nodes': self.nodes,
                }
            else:
                return {'status': 'failed', 'error': 'Invalid DC analyzer result'}
        except Exception as e:
            import traceback
            return {'status': 'failed', 'error': f'DC analysis error: {str(e)}\n{traceback.format_exc()}'}
    
    def ac_analysis(self, freq_start: float = 1, freq_end: float = 1e6, num_points: int = 100) -> Dict:
        """Perform AC analysis using ACAnalyzer service"""
        try:
            num_nodes = max(self.nodes.values()) + 1
            result = self.ac_analyzer.solve(
                frequencies=list(range(num_points)),
                num_nodes=num_nodes
            )
            
            return {
                'status': 'success',
                'frequencies': result.get('frequencies'),
                'impedance': result.get('impedances', {}),
                'transfer_function': result.get('transfer_function', {}),
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def transient_analysis(self, duration: float = 0.1, time_step: float = 0.001) -> Dict:
        """Perform transient analysis using TransientAnalyzer service"""
        try:
            result = self.transient_analyzer.solve(
                t_span=(0, duration),
                num_points=int(duration / time_step),
                method='RK45'
            )
            
            return {
                'status': 'success',
                'time': result.get('time'),
                'voltage': result.get('voltage'),
                'current': result.get('current'),
                'power': result.get('power'),
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def validate_circuit(self) -> Tuple[bool, List[str]]:
        """Validate circuit components"""
        try:
            # Basic validation
            if not self.nodes:
                return False, ["No nodes in circuit"]
            
            if not self.components_list:
                return False, ["No components in circuit"]
            
            errors = []
            
            # Validate each component
            for comp in self.components_list:
                if comp['type'] == 'resistor':
                    if comp['value'] <= 0:
                        errors.append(f"{comp['name']}: Resistance must be positive")
                elif comp['type'] == 'capacitor':
                    if comp['value'] <= 0:
                        errors.append(f"{comp['name']}: Capacitance must be positive")
                elif comp['type'] == 'inductor':
                    if comp['value'] <= 0:
                        errors.append(f"{comp['name']}: Inductance must be positive")
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [str(e)]
    
    def get_system_info(self) -> Dict:
        """Get system information and statistics"""
        return {
            'nodes': len(self.nodes),
            'components': len(self.components_list),
            'services': {
                'dc_analyzer': 'active',
                'ac_analyzer': 'active',
                'transient_analyzer': 'active',
                'component_validator': 'active',
                'simulation_coordinator': 'active',
            },
            'libraries': len(self.library_service.libraries),
            'total_components_available': sum(
                len(lib_data.get('components', [])) 
                for lib_data in self.library_service.libraries.values()
            )
        }


def parse_component_value(value_str: str) -> float:
    """
    Parse component value string to float using ValueParser service
    Examples: "1k" -> 1000, "1.5M" -> 1500000, "100n" -> 1e-7
    """
    try:
        from services import ValueParser
        parser = ValueParser()
        return parser.parse(value_str)
    except Exception:
        # Fallback to simple parsing
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        value_str = str(value_str).strip().upper()
        multipliers = {
            'P': 1e-12, 'N': 1e-9, 'U': 1e-6, 'M': 1e-3, 'K': 1e3, 'MEG': 1e6,
        }
        
        value_str = value_str.replace('OHM', '').replace('Ω', '')
        value_str = value_str.replace('F', '').replace('H', '')
        value_str = value_str.replace('A', '').replace('V', '')
        value_str = value_str.strip()
        
        multiplier = 1.0
        for suffix, mult in multipliers.items():
            if value_str.endswith(suffix):
                multiplier = mult
                value_str = value_str[:-len(suffix)].strip()
                break
        
        return float(value_str) * multiplier
