"""
DC Analysis Service

Performs DC operating point analysis on circuits using nodal analysis.
Independent analyzer service that can be used standalone.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from scipy.linalg import solve


class DCAnalyzer:
    """
    Performs DC (direct current) steady-state analysis.
    
    Uses modified nodal analysis (MNA) to solve for:
    - Node voltages
    - Component currents
    - Power dissipation
    """

    def __init__(self):
        self.node_count = 0
        self.components = []
        self.voltage_sources = []
        self.current_sources = []
        self.ground_node = 0

    def add_resistor(self, name: str, node1: int, node2: int, value: float) -> None:
        """Add resistor: V1 - V2 = I*R"""
        if value <= 0:
            raise ValueError(f"Resistor {name}: value must be positive")
        self.components.append({
            'type': 'resistor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': value
        })

    def add_voltage_source(self, name: str, node_pos: int, node_neg: int,
                          voltage: float) -> None:
        """Add independent voltage source"""
        self.voltage_sources.append({
            'name': name,
            'node_pos': node_pos,
            'node_neg': node_neg,
            'voltage': voltage
        })

    def add_current_source(self, name: str, node1: int, node2: int,
                          current: float) -> None:
        """Add independent current source: current flows from node1 to node2"""
        self.current_sources.append({
            'name': name,
            'node1': node1,
            'node2': node2,
            'current': current
        })

    def solve(self, num_nodes: int = None) -> Dict[str, Any]:
        """
        Solve DC circuit using nodal analysis.
        
        Args:
            num_nodes: Number of nodes in circuit (or auto-detect)
            
        Returns:
            Dictionary with analysis results
        """
        if num_nodes is None:
            num_nodes = self._detect_node_count()
        
        self.node_count = num_nodes
        
        # Build Y matrix (admittance) and I vector (current sources)
        num_vars = num_nodes + len(self.voltage_sources)
        Y = np.zeros((num_vars, num_vars))
        I = np.zeros(num_vars)
        
        try:
            # Process resistors (conductances)
            for comp in self.components:
                if comp['type'] == 'resistor':
                    n1 = comp['node1']
                    n2 = comp['node2']
                    G = 1.0 / comp['value']  # Conductance
                    
                    # Diagonal terms
                    Y[n1, n1] += G
                    Y[n2, n2] += G
                    # Off-diagonal terms
                    Y[n1, n2] -= G
                    Y[n2, n1] -= G
            
            # Process independent current sources
            for src in self.current_sources:
                n1 = src['node1']
                n2 = src['node2']
                I_val = src['current']
                I[n1] -= I_val  # Current out of node
                I[n2] += I_val  # Current into node
            
            # Process independent voltage sources (KVL constraints)
            for i, src in enumerate(self.voltage_sources):
                eq_idx = num_nodes + i
                n_pos = src['node_pos']
                n_neg = src['node_neg']
                V_val = src['voltage']
                
                # V_pos - V_neg = V_val
                Y[eq_idx, n_pos] = 1
                Y[eq_idx, n_neg] = -1
                I[eq_idx] = V_val
                
                # Transpose for symmetric treatment
                Y[n_pos, eq_idx] = 1
                Y[n_neg, eq_idx] = -1
            
            # Solve system
            try:
                X = solve(Y, I)
            except np.linalg.LinAlgError:
                return {
                    'status': 'error',
                    'message': 'Circuit matrix singular - check for floating nodes',
                    'node_voltages': {},
                    'currents': {},
                    'power': {}
                }
            
            # Extract results
            node_voltages = {i: X[i] for i in range(num_nodes)}
            source_currents = {self.voltage_sources[i]['name']: X[num_nodes + i]
                              for i in range(len(self.voltage_sources))}
            
            # Calculate component currents and power
            currents = {}
            power = {}
            
            for comp in self.components:
                if comp['type'] == 'resistor':
                    n1 = comp['node1']
                    n2 = comp['node2']
                    V_diff = X[n1] - X[n2]
                    I_comp = V_diff / comp['value']
                    P_comp = I_comp * I_comp * comp['value']
                    
                    currents[comp['name']] = I_comp
                    power[comp['name']] = P_comp
            
            for src in self.current_sources:
                currents[src['name']] = src['current']
                n1 = src['node1']
                n2 = src['node2']
                V_diff = X[n1] - X[n2]
                P_comp = V_diff * src['current']
                power[src['name']] = P_comp
            
            for src in self.voltage_sources:
                currents[src['name']] = source_currents[src['name']]
                power[src['name']] = src['voltage'] * source_currents[src['name']]
            
            return {
                'status': 'success',
                'node_voltages': node_voltages,
                'currents': currents,
                'power': power,
                'source_currents': source_currents
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'node_voltages': {},
                'currents': {},
                'power': {}
            }

    def _detect_node_count(self) -> int:
        """Auto-detect number of nodes"""
        nodes = {0}  # Ground node
        
        for comp in self.components:
            nodes.add(comp['node1'])
            nodes.add(comp['node2'])
        
        for src in self.voltage_sources:
            nodes.add(src['node_pos'])
            nodes.add(src['node_neg'])
        
        for src in self.current_sources:
            nodes.add(src['node1'])
            nodes.add(src['node2'])
        
        return max(nodes) + 1 if nodes else 1

    def clear(self) -> None:
        """Clear all circuit components"""
        self.components = []
        self.voltage_sources = []
        self.current_sources = []
        self.node_count = 0
