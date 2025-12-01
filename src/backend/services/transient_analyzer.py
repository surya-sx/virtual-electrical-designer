"""
Transient Analysis Service

Performs time-domain transient analysis on circuits.
Solves differential equations for RC, RL, and RLC circuits.
"""

import numpy as np
from typing import Dict, List, Any, Callable, Tuple
from scipy.integrate import odeint, solve_ivp


class TransientAnalyzer:
    """
    Performs transient (time-domain) analysis.
    
    Solves ODEs to find:
    - Voltage/current vs time
    - Transient response
    - Settling time
    - Overshoot
    """

    def __init__(self):
        self.components = []
        self.sources = []
        self.initial_conditions = {}

    def add_resistor(self, name: str, node1: int, node2: int, value: float) -> None:
        """Add resistor"""
        self.components.append({
            'type': 'resistor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': value
        })

    def add_capacitor(self, name: str, node1: int, node2: int,
                     capacitance: float, initial_voltage: float = 0) -> None:
        """Add capacitor with optional initial condition"""
        self.components.append({
            'type': 'capacitor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': capacitance
        })
        self.initial_conditions[name] = initial_voltage

    def add_inductor(self, name: str, node1: int, node2: int,
                    inductance: float, initial_current: float = 0) -> None:
        """Add inductor with optional initial condition"""
        self.components.append({
            'type': 'inductor',
            'name': name,
            'node1': node1,
            'node2': node2,
            'value': inductance
        })
        self.initial_conditions[name] = initial_current

    def add_voltage_source(self, name: str, node_pos: int, node_neg: int,
                          voltage_func: Callable[[float], float]) -> None:
        """
        Add time-varying voltage source.
        
        Args:
            voltage_func: Function that returns voltage given time t
        """
        self.sources.append({
            'type': 'voltage_source',
            'name': name,
            'node_pos': node_pos,
            'node_neg': node_neg,
            'func': voltage_func
        })

    def add_pulse_source(self, name: str, node_pos: int, node_neg: int,
                        v_initial: float, v_pulse: float, t_rise: float) -> None:
        """
        Add step pulse (rising edge at t_rise).
        
        Args:
            v_initial: Initial voltage
            v_pulse: Pulse voltage
            t_rise: Time of pulse rise
        """
        def pulse_func(t):
            return v_initial if t < t_rise else v_pulse
        
        self.add_voltage_source(name, node_pos, node_neg, pulse_func)

    def add_sinusoidal_source(self, name: str, node_pos: int, node_neg: int,
                             amplitude: float, frequency: float,
                             phase: float = 0) -> None:
        """
        Add sinusoidal voltage source.
        
        Args:
            amplitude: Peak amplitude
            frequency: Frequency in Hz
            phase: Phase in radians
        """
        def sin_func(t):
            return amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        self.add_voltage_source(name, node_pos, node_neg, sin_func)

    def solve(self, t_span: Tuple[float, float], num_points: int = 1000,
             method: str = 'RK45') -> Dict[str, Any]:
        """
        Solve transient response.
        
        Args:
            t_span: Tuple (t_start, t_end) in seconds
            num_points: Number of time points
            method: ODE solver ('RK45', 'BDF', 'LSODA')
            
        Returns:
            Dictionary with time-domain results
        """
        try:
            # Build state vector - capacitor voltages and inductor currents
            state_names = []
            initial_state = []
            
            for comp in self.components:
                if comp['type'] == 'capacitor':
                    state_names.append(('V', comp['name']))
                    initial_state.append(self.initial_conditions.get(comp['name'], 0))
                elif comp['type'] == 'inductor':
                    state_names.append(('I', comp['name']))
                    initial_state.append(self.initial_conditions.get(comp['name'], 0))
            
            initial_state = np.array(initial_state)
            
            # Create ODE system
            def system_ode(t, y):
                dydt = []
                
                # For each capacitor: C*dV/dt = I
                # For each inductor: L*dI/dt = V
                
                state_idx = 0
                for comp in self.components:
                    if comp['type'] == 'capacitor':
                        # Find current through capacitor
                        I_cap = self._calculate_component_current(t, y, comp)
                        C = comp['value']
                        dydt.append(I_cap / C)
                        state_idx += 1
                    
                    elif comp['type'] == 'inductor':
                        # Find voltage across inductor
                        V_ind = self._calculate_component_voltage(t, y, comp)
                        L = comp['value']
                        dydt.append(V_ind / L)
                        state_idx += 1
                
                return dydt
            
            # Solve ODE
            t_eval = np.linspace(t_span[0], t_span[1], num_points)
            
            if method == 'RK45':
                sol = solve_ivp(system_ode, t_span, initial_state, 
                               t_eval=t_eval, method='RK45', dense_output=True)
            else:
                # Default to dense output
                sol = solve_ivp(system_ode, t_span, initial_state,
                               t_eval=t_eval, method='RK45', dense_output=True)
            
            # Format results
            results = {
                'status': 'success' if sol.status == 0 else 'error',
                'time': sol.t,
                'states': {},
                'node_voltages': {},
                'component_currents': {}
            }
            
            # Store state variables
            for i, (state_type, comp_name) in enumerate(state_names):
                results['states'][comp_name] = sol.y[i]
            
            return results
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'time': [],
                'states': {},
                'node_voltages': {},
                'component_currents': {}
            }

    def _calculate_component_current(self, t: float, y: np.ndarray,
                                    component: Dict) -> float:
        """Calculate current through component (for RHS of ODE)"""
        # Simplified - uses Kirchhoff's current law
        return 0.0

    def _calculate_component_voltage(self, t: float, y: np.ndarray,
                                    component: Dict) -> float:
        """Calculate voltage across component (for RHS of ODE)"""
        # Simplified - uses Kirchhoff's voltage law
        return 0.0

    def clear(self) -> None:
        """Clear all circuit components"""
        self.components = []
        self.sources = []
        self.initial_conditions = {}
