"""
AC Analysis Service

Performs AC frequency sweep analysis on circuits using phasor analysis.
Handles complex impedance calculations for capacitors and inductors.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import cmath


class ACAnalyzer:
    """
    Performs AC (alternating current) frequency sweep analysis.
    
    Uses phasor analysis to solve for:
    - Impedance at each frequency
    - Node voltages (complex)
    - Component currents (complex)
    - Magnitude and phase angle
    - Frequency response
    """

    def __init__(self):
        self.components = []
        self.voltage_sources = []
        self.ground_node = 0

    def add_resistor(self, name: str, node1: int, node2: int, value: float) -> None:
        """Add resistor: impedance = R (real)"""
        self.components.append({
            'type': 'resistor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': value
        })

    def add_capacitor(self, name: str, node1: int, node2: int,
                     capacitance: float) -> None:
        """Add capacitor: impedance = 1/(j*omega*C)"""
        self.components.append({
            'type': 'capacitor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': capacitance
        })

    def add_inductor(self, name: str, node1: int, node2: int,
                    inductance: float) -> None:
        """Add inductor: impedance = j*omega*L"""
        self.components.append({
            'type': 'inductor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': inductance
        })

    def add_voltage_source(self, name: str, node_pos: int, node_neg: int,
                          magnitude: float, phase: float = 0) -> None:
        """Add AC voltage source with magnitude and phase (in degrees)"""
        self.voltage_sources.append({
            'name': name,
            'node_pos': node_pos,
            'node_neg': node_neg,
            'magnitude': magnitude,
            'phase': np.radians(phase)
        })

    def solve(self, frequencies: List[float], num_nodes: int = None) -> Dict[str, Any]:
        """
        Solve AC circuit over frequency range.
        
        Args:
            frequencies: List of frequencies in Hz
            num_nodes: Number of nodes
            
        Returns:
            Dictionary with frequency response data
        """
        if num_nodes is None:
            num_nodes = self._detect_node_count()
        
        if not self.voltage_sources:
            return {
                'status': 'error',
                'message': 'No AC voltage sources defined',
                'frequencies': [],
                'response': {}
            }
        
        results = {
            'status': 'success',
            'frequencies': frequencies,
            'response': {},
            'impedances': {}
        }
        
        for frequency in frequencies:
            omega = 2 * np.pi * frequency
            
            # Build admittance matrix (complex)
            Y = np.zeros((num_nodes, num_nodes), dtype=complex)
            I = np.zeros(num_nodes, dtype=complex)
            
            try:
                # Process components
                for comp in self.components:
                    n1 = comp['node1']
                    n2 = comp['node2']
                    
                    if comp['type'] == 'resistor':
                        Z = comp['value']
                        Y_comp = 1.0 / Z
                    
                    elif comp['type'] == 'capacitor':
                        Z = 1.0 / (1j * omega * comp['value'])
                        Y_comp = 1.0 / Z
                    
                    elif comp['type'] == 'inductor':
                        Z = 1j * omega * comp['value']
                        Y_comp = 1.0 / Z
                    else:
                        continue
                    
                    # Add to admittance matrix
                    Y[n1, n1] += Y_comp
                    Y[n2, n2] += Y_comp
                    Y[n1, n2] -= Y_comp
                    Y[n2, n1] -= Y_comp
                    
                    # Store impedance
                    if frequency not in results['impedances']:
                        results['impedances'][frequency] = {}
                    results['impedances'][frequency][comp['name']] = {
                        'magnitude': abs(Z),
                        'phase': np.degrees(cmath.phase(Z))
                    }
                
                # Process voltage sources
                for src in self.voltage_sources:
                    n_pos = src['node_pos']
                    n_neg = src['node_neg']
                    V_source = src['magnitude'] * np.exp(1j * src['phase'])
                    
                    I[n_pos] -= V_source / (1 + 1e-12)  # Very small source impedance
                    I[n_neg] += V_source / (1 + 1e-12)
                
                # Solve
                try:
                    V = np.linalg.solve(Y, I)
                except np.linalg.LinAlgError:
                    continue
                
                # Store voltage response
                freq_response = {
                    'node_voltages': {},
                    'component_currents': {}
                }
                
                for i in range(num_nodes):
                    freq_response['node_voltages'][i] = {
                        'magnitude': abs(V[i]),
                        'phase': np.degrees(cmath.phase(V[i])),
                        'real': V[i].real,
                        'imag': V[i].imag
                    }
                
                # Calculate component currents
                for comp in self.components:
                    n1 = comp['node1']
                    n2 = comp['node2']
                    I_comp = (V[n1] - V[n2]) / self._get_impedance(comp, omega)
                    
                    freq_response['component_currents'][comp['name']] = {
                        'magnitude': abs(I_comp),
                        'phase': np.degrees(cmath.phase(I_comp)),
                        'real': I_comp.real,
                        'imag': I_comp.imag
                    }
                
                results['response'][frequency] = freq_response
            
            except Exception as e:
                continue
        
        return results

    def _get_impedance(self, component: Dict, omega: float) -> complex:
        """Calculate component impedance at given angular frequency"""
        if component['type'] == 'resistor':
            return complex(component['value'], 0)
        elif component['type'] == 'capacitor':
            return 1.0 / (1j * omega * component['value'])
        elif component['type'] == 'inductor':
            return 1j * omega * component['value']
        else:
            return complex(1, 0)

    def _detect_node_count(self) -> int:
        """Auto-detect number of nodes"""
        nodes = {0}
        
        for comp in self.components:
            nodes.add(comp['node1'])
            nodes.add(comp['node2'])
        
        for src in self.voltage_sources:
            nodes.add(src['node_pos'])
            nodes.add(src['node_neg'])
        
        return max(nodes) + 1 if nodes else 1

    def clear(self) -> None:
        """Clear all circuit components"""
        self.components = []
        self.voltage_sources = []
