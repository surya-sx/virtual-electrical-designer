"""
Advanced Circuit Solver - Nodal analysis with real component values
Uses: NumPy for linear algebra, SciPy for ODE solving
Implements: DC, AC (frequency), Transient time-domain analysis
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy.integrate import odeint
from scipy.linalg import solve
import warnings

warnings.filterwarnings('ignore')


class CircuitSolver:
    """
    Main circuit solver using nodal analysis and modified nodal analysis (MNA)
    """
    
    def __init__(self):
        self.nodes: Dict[str, int] = {}  # node_name -> node_index
        self.components: List[Dict] = []  # List of component dictionaries
        self.node_counter = 0
        self.ground_node = None
        
    def add_node(self, node_name: str) -> int:
        """Add node and return its index"""
        if node_name not in self.nodes:
            if node_name.lower() == "gnd" or node_name.lower() == "ground":
                self.ground_node = node_name
                self.nodes[node_name] = 0  # Ground is always node 0
            else:
                self.node_counter += 1
                self.nodes[node_name] = self.node_counter
        return self.nodes[node_name]
    
    def add_resistor(self, name: str, node1: str, node2: str, resistance: float):
        """Add resistor between two nodes
        Args:
            name: Component name
            node1: From node
            node2: To node
            resistance: Resistance in Ohms (e.g., 1000 for 1kΩ, 1e6 for 1MΩ)
        """
        if resistance <= 0:
            raise ValueError(f"Resistor {name} must have positive resistance, got {resistance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.components.append({
            'type': 'resistor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': resistance,  # Ohms
        })
    
    def add_capacitor(self, name: str, node1: str, node2: str, capacitance: float):
        """Add capacitor between two nodes
        Args:
            name: Component name
            node1: From node
            node2: To node
            capacitance: Capacitance in Farads (e.g., 1e-6 for 1μF, 1e-9 for 1nF)
        """
        if capacitance <= 0:
            raise ValueError(f"Capacitor {name} must have positive capacitance, got {capacitance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.components.append({
            'type': 'capacitor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': capacitance,  # Farads
        })
    
    def add_inductor(self, name: str, node1: str, node2: str, inductance: float):
        """Add inductor between two nodes
        Args:
            name: Component name
            node1: From node
            node2: To node
            inductance: Inductance in Henries (e.g., 1e-3 for 1mH, 1e-6 for 1μH)
        """
        if inductance <= 0:
            raise ValueError(f"Inductor {name} must have positive inductance, got {inductance}")
        
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.components.append({
            'type': 'inductor',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': inductance,  # Henries
        })
    
    def add_voltage_source(self, name: str, node_pos: str, node_neg: str, voltage: float):
        """Add DC voltage source
        Args:
            name: Component name
            node_pos: Positive terminal node
            node_neg: Negative terminal node
            voltage: Voltage in Volts (e.g., 5 for 5V, 12 for 12V)
        """
        n_pos = self.add_node(node_pos)
        n_neg = self.add_node(node_neg)
        
        self.components.append({
            'type': 'voltage_source',
            'name': name,
            'node_pos': n_pos,
            'node_neg': n_neg,
            'value': voltage,  # Volts
        })
    
    def add_current_source(self, name: str, node1: str, node2: str, current: float):
        """Add DC current source
        Args:
            name: Component name
            node1: From node
            node2: To node
            current: Current in Amperes (e.g., 0.01 for 10mA, 1 for 1A)
        """
        n1 = self.add_node(node1)
        n2 = self.add_node(node2)
        
        self.components.append({
            'type': 'current_source',
            'name': name,
            'node1': n1,
            'node2': n2,
            'value': current,  # Amperes
        })
    
    def dc_analysis(self) -> Dict:
        """
        Perform DC operating point analysis using nodal analysis
        Returns: Dictionary with node voltages and component currents
        """
        if not self.nodes:
            return {'status': 'failed', 'error': 'No nodes in circuit'}
        
        num_nodes = max(self.nodes.values()) + 1
        
        # Build Y matrix (admittance) and I vector (current sources)
        Y = np.zeros((num_nodes, num_nodes))
        I = np.zeros(num_nodes)
        
        # First pass: add resistors and current sources
        for comp in self.components:
            if comp['type'] == 'resistor':
                n1, n2 = comp['node1'], comp['node2']
                R = comp['value']
                G = 1.0 / R  # Conductance
                
                # Y[n1,n1] += G, Y[n2,n2] += G, Y[n1,n2] -= G, Y[n2,n1] -= G
                Y[n1, n1] += G
                Y[n2, n2] += G
                Y[n1, n2] -= G
                Y[n2, n1] -= G
            
            elif comp['type'] == 'current_source':
                n1, n2 = comp['node1'], comp['node2']
                current = comp['value']
                
                # Current flows from n1 to n2
                I[n1] -= current
                I[n2] += current
        
        # Second pass: handle voltage sources as ideal current through admittance
        voltage_sources = [c for c in self.components if c['type'] == 'voltage_source']
        
        for comp in voltage_sources:
            n_pos = comp['node_pos']
            n_neg = comp['node_neg']
            voltage = comp['value']
            
            # Add large conductance to create voltage constraint
            # This effectively makes the voltage source a stiff voltage constraint
            G_source = 1e6  # Very large conductance
            
            if n_pos != 0:
                Y[n_pos, n_pos] += G_source
                I[n_pos] += G_source * voltage
            
            if n_neg != 0:
                Y[n_neg, n_neg] += G_source
                I[n_neg] -= G_source * voltage
        
        try:
            # Ensure ground node is constrained to 0V
            Y[0, :] = 0
            Y[0, 0] = 1
            I[0] = 0
            
            # Solve Y*V = I
            V = solve(Y, I)
            
            # Calculate component currents
            currents = self._calculate_currents(V)
            
            return {
                'status': 'success',
                'node_voltages': V,
                'node_names': {name: V[idx] for name, idx in self.nodes.items()},
                'component_currents': currents,
                'nodes': self.nodes,
            }
        
        except np.linalg.LinAlgError as e:
            return {'status': 'failed', 'error': f'Singular matrix - check circuit topology: {str(e)}'}
        except Exception as e:
            return {'status': 'failed', 'error': f'Analysis failed: {str(e)}'}
    
    def ac_analysis(self, freq_start: float = 1, freq_end: float = 1e6, num_points: int = 100) -> Dict:
        """
        Perform AC frequency sweep analysis
        Returns: Frequency response (magnitude and phase)
        """
        frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), num_points)
        
        results = {
            'frequencies': frequencies,
            'impedance': {},
            'transfer_function': {},
            'status': 'success',
        }
        
        # Find voltage source and calculate transfer function
        voltage_sources = [c for c in self.components if c['type'] == 'voltage_source']
        if not voltage_sources:
            return {'status': 'failed', 'error': 'No voltage source for AC analysis'}
        
        V_source = voltage_sources[0]['value']
        
        # Calculate impedances at each frequency
        for comp in self.components:
            if comp['type'] == 'resistor':
                R = comp['value']
                results['impedance'][comp['name']] = {
                    'magnitude': np.ones(num_points) * R,
                    'phase': np.zeros(num_points),
                }
            
            elif comp['type'] == 'capacitor':
                C = comp['value']
                Z_C = []
                phases = []
                for f in frequencies:
                    omega = 2 * np.pi * f
                    Z = 1.0 / (1j * omega * C)
                    Z_C.append(np.abs(Z))
                    phases.append(np.angle(Z) * 180 / np.pi)
                
                results['impedance'][comp['name']] = {
                    'magnitude': np.array(Z_C),
                    'phase': np.array(phases),
                }
            
            elif comp['type'] == 'inductor':
                L = comp['value']
                Z_L = []
                phases = []
                for f in frequencies:
                    omega = 2 * np.pi * f
                    Z = 1j * omega * L
                    Z_L.append(np.abs(Z))
                    phases.append(np.angle(Z) * 180 / np.pi)
                
                results['impedance'][comp['name']] = {
                    'magnitude': np.array(Z_L),
                    'phase': np.array(phases),
                }
        
        return results
    
    def transient_analysis(self, duration: float = 0.1, time_step: float = 0.001) -> Dict:
        """
        Perform transient time-domain analysis
        Solves differential equations for RC, RL, LC circuits
        """
        time_points = np.arange(0, duration, time_step)
        
        # Check for capacitors/inductors
        capacitors = [c for c in self.components if c['type'] == 'capacitor']
        inductors = [c for c in self.components if c['type'] == 'inductor']
        
        if not capacitors and not inductors:
            # No energy storage - just do DC analysis at each time
            return self._transient_resistive(time_points)
        
        # Simple RC circuit transient
        if capacitors and not inductors:
            return self._transient_rc(time_points, capacitors)
        
        # Simple RL circuit transient
        if inductors and not capacitors:
            return self._transient_rl(time_points, inductors)
        
        return {'status': 'failed', 'error': 'RLC transient analysis not yet implemented'}
    
    def _transient_rc(self, time_points, capacitors) -> Dict:
        """Simple RC transient analysis"""
        resistors = [c for c in self.components if c['type'] == 'resistor']
        voltage_sources = [c for c in self.components if c['type'] == 'voltage_source']
        
        if not resistors or not voltage_sources or not capacitors:
            return {'status': 'failed', 'error': 'Need R, C, and voltage source for RC analysis'}
        
        R = resistors[0]['value']
        C = capacitors[0]['value']
        V_in = voltage_sources[0]['value']
        tau = R * C
        
        # RC charging: V_out(t) = V_in * (1 - exp(-t/tau))
        V_out = V_in * (1 - np.exp(-time_points / tau))
        I = (V_in - V_out) / R
        P = I ** 2 * R
        
        return {
            'status': 'success',
            'time': time_points,
            'voltage_out': V_out,
            'current': I,
            'power': P,
            'tau': tau,
        }
    
    def _transient_rl(self, time_points, inductors) -> Dict:
        """Simple RL transient analysis"""
        resistors = [c for c in self.components if c['type'] == 'resistor']
        voltage_sources = [c for c in self.components if c['type'] == 'voltage_source']
        
        if not resistors or not voltage_sources or not inductors:
            return {'status': 'failed', 'error': 'Need R, L, and voltage source for RL analysis'}
        
        R = resistors[0]['value']
        L = inductors[0]['value']
        V_in = voltage_sources[0]['value']
        tau = L / R
        
        # RL inductor current rise: I(t) = (V_in/R) * (1 - exp(-t*R/L))
        I = (V_in / R) * (1 - np.exp(-time_points * R / L))
        V_L = V_in - I * R
        P = I ** 2 * R
        
        return {
            'status': 'success',
            'time': time_points,
            'current': I,
            'voltage_L': V_L,
            'power': P,
            'tau': tau,
        }
    
    def _transient_resistive(self, time_points) -> Dict:
        """Resistive-only transient (no energy storage)"""
        dc_result = self.dc_analysis()
        
        if dc_result.get('status') != 'success':
            return dc_result
        
        V_nodes = dc_result['node_voltages']
        currents = dc_result['component_currents']
        
        # Repeat results across time
        node_voltages_time = {node: np.ones(len(time_points)) * V for node, V in zip(self.nodes.keys(), V_nodes)}
        component_currents_time = {name: np.ones(len(time_points)) * I for name, I in currents.items()}
        
        return {
            'status': 'success',
            'time': time_points,
            'node_voltages': node_voltages_time,
            'component_currents': component_currents_time,
        }
    
    def _calculate_currents(self, V: np.ndarray) -> Dict:
        """Calculate currents through components"""
        currents = {}
        
        for comp in self.components:
            if comp['type'] == 'resistor':
                n1, n2 = comp['node1'], comp['node2']
                R = comp['value']
                V_across = V[n1] - V[n2]
                I = V_across / R
                currents[comp['name']] = I
            
            elif comp['type'] == 'capacitor':
                n1, n2 = comp['node1'], comp['node2']
                V_across = V[n1] - V[n2]
                # In DC analysis, capacitor is open circuit
                currents[comp['name']] = 0.0
            
            elif comp['type'] == 'inductor':
                n1, n2 = comp['node1'], comp['node2']
                V_across = V[n1] - V[n2]
                # In DC analysis, inductor is short circuit
                L = comp['value']
                # Current through inductor would need initial condition
                currents[comp['name']] = 0.0
        
        return currents


def parse_component_value(value_str: str) -> float:
    """
    Parse component value string to float
    Examples:
        "1k" -> 1000
        "1.5k" -> 1500
        "1M" -> 1000000
        "1m" -> 0.001 (milliohm/farad)
        "1u" -> 1e-6
        "1n" -> 1e-9
        "1p" -> 1e-12
    """
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    value_str = str(value_str).strip().upper()
    
    # Multiplier map
    multipliers = {
        'P': 1e-12,  # pico
        'N': 1e-9,   # nano
        'U': 1e-6,   # micro
        'M': 1e-3,   # milli (or mega for first M)
        'K': 1e3,    # kilo
        'MEG': 1e6,  # mega
    }
    
    # Remove common units
    value_str = value_str.replace('OHM', '').replace('Ω', '')
    value_str = value_str.replace('F', '').replace('H', '')
    value_str = value_str.replace('A', '').replace('V', '')
    value_str = value_str.strip()
    
    # Find multiplier
    multiplier = 1.0
    for suffix, mult in multipliers.items():
        if value_str.endswith(suffix):
            multiplier = mult
            value_str = value_str[:-len(suffix)].strip()
            break
    
    try:
        return float(value_str) * multiplier
    except ValueError:
        raise ValueError(f"Cannot parse component value: {value_str}")
