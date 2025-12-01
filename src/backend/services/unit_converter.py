"""
Unit Converter Service

Converts between different unit systems and dimensions.
Supports resistance, capacitance, inductance, voltage, current, power, frequency, and time.
"""

from typing import Dict, Tuple, Optional
from enum import Enum


class UnitSystem(Enum):
    """Supported unit systems"""
    SI = "SI"  # Standard International
    CGS = "CGS"  # Centimeter-Gram-Second
    IMPERIAL = "IMPERIAL"  # Imperial/US


class UnitConverter:
    """
    Converts values between different electrical units.
    Maintains conversion relationships and validates unit compatibility.
    """

    # Resistance conversions (base: Ohm)
    RESISTANCE = {
        'Ω': 1.0,
        'mΩ': 1e-3,
        'kΩ': 1e3,
        'MΩ': 1e6,
        'GΩ': 1e9,
    }

    # Capacitance conversions (base: Farad)
    CAPACITANCE = {
        'F': 1.0,
        'mF': 1e-3,
        'µF': 1e-6,
        'nF': 1e-9,
        'pF': 1e-12,
    }

    # Inductance conversions (base: Henry)
    INDUCTANCE = {
        'H': 1.0,
        'mH': 1e-3,
        'µH': 1e-6,
        'nH': 1e-9,
    }

    # Voltage conversions (base: Volt)
    VOLTAGE = {
        'V': 1.0,
        'mV': 1e-3,
        'µV': 1e-6,
        'kV': 1e3,
    }

    # Current conversions (base: Ampere)
    CURRENT = {
        'A': 1.0,
        'mA': 1e-3,
        'µA': 1e-6,
        'nA': 1e-9,
        'pA': 1e-12,
    }

    # Power conversions (base: Watt)
    POWER = {
        'W': 1.0,
        'mW': 1e-3,
        'µW': 1e-6,
        'kW': 1e3,
        'MW': 1e6,
    }

    # Frequency conversions (base: Hz)
    FREQUENCY = {
        'Hz': 1.0,
        'kHz': 1e3,
        'MHz': 1e6,
        'GHz': 1e9,
        'THz': 1e12,
    }

    # Time conversions (base: second)
    TIME = {
        's': 1.0,
        'ms': 1e-3,
        'µs': 1e-6,
        'ns': 1e-9,
        'ps': 1e-12,
        'fs': 1e-15,
    }

    # Charge conversions (base: Coulomb)
    CHARGE = {
        'C': 1.0,
        'mC': 1e-3,
        'µC': 1e-6,
        'nC': 1e-9,
        'pC': 1e-12,
    }

    # Temperature conversions (special handling needed)
    TEMPERATURE = {
        'K': 'kelvin',      # Absolute
        '°C': 'celsius',    # Relative
        '°F': 'fahrenheit', # Relative
    }

    # Unit categories for validation
    UNIT_CATEGORIES = {
        'resistance': RESISTANCE,
        'capacitance': CAPACITANCE,
        'inductance': INDUCTANCE,
        'voltage': VOLTAGE,
        'current': CURRENT,
        'power': POWER,
        'frequency': FREQUENCY,
        'time': TIME,
        'charge': CHARGE,
        'temperature': TEMPERATURE,
    }

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str,
                category: Optional[str] = None) -> float:
        """
        Convert value from one unit to another.
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit (e.g., 'kΩ', 'mV')
            to_unit: Target unit (e.g., 'Ω', 'V')
            category: Optional category to speed up lookup
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If units are incompatible or unknown
        """
        # Find unit category if not provided
        if category is None:
            category = UnitConverter._find_category(from_unit)
            if category is None:
                raise ValueError(f"Unknown unit: {from_unit}")
        
        conversion_table = UnitConverter.UNIT_CATEGORIES.get(category)
        if conversion_table is None:
            raise ValueError(f"Unknown category: {category}")
        
        if from_unit not in conversion_table:
            raise ValueError(f"Unknown {category} unit: {from_unit}")
        if to_unit not in conversion_table:
            raise ValueError(f"Unknown {category} unit: {to_unit}")
        
        # Convert to base unit, then to target unit
        base_value = value * conversion_table[from_unit]
        return base_value / conversion_table[to_unit]

    @staticmethod
    def _find_category(unit: str) -> Optional[str]:
        """Find the category of a unit"""
        for category, units in UnitConverter.UNIT_CATEGORIES.items():
            if unit in units:
                return category
        return None

    @staticmethod
    def get_common_units(category: str) -> list:
        """
        Get list of common units for a category.
        
        Args:
            category: Component category (e.g., 'resistance', 'capacitance')
            
        Returns:
            List of unit strings in order of common usage
        """
        units_dict = UnitConverter.UNIT_CATEGORIES.get(category, {})
        if category == 'resistance':
            return ['Ω', 'kΩ', 'MΩ', 'mΩ', 'GΩ']
        elif category == 'capacitance':
            return ['µF', 'nF', 'pF', 'F', 'mF']
        elif category == 'inductance':
            return ['µH', 'mH', 'H', 'nH']
        elif category == 'voltage':
            return ['V', 'mV', 'kV', 'µV']
        elif category == 'current':
            return ['A', 'mA', 'µA', 'nA', 'pA']
        elif category == 'power':
            return ['W', 'mW', 'kW', 'µW', 'MW']
        elif category == 'frequency':
            return ['Hz', 'kHz', 'MHz', 'GHz']
        elif category == 'time':
            return ['s', 'ms', 'µs', 'ns', 'ps']
        else:
            return list(units_dict.keys())

    @staticmethod
    def get_base_unit(category: str) -> str:
        """Get the base SI unit for a category"""
        base_units = {
            'resistance': 'Ω',
            'capacitance': 'F',
            'inductance': 'H',
            'voltage': 'V',
            'current': 'A',
            'power': 'W',
            'frequency': 'Hz',
            'time': 's',
            'charge': 'C',
        }
        return base_units.get(category, '')

    @staticmethod
    def get_conversion_factors(category: str) -> Dict[str, float]:
        """
        Get all conversion factors for a category relative to base unit.
        
        Args:
            category: Component category
            
        Returns:
            Dictionary mapping units to their conversion factor
        """
        return UnitConverter.UNIT_CATEGORIES.get(category, {})

    @staticmethod
    def ohms_law(voltage: float, current: float = None,
                 resistance: float = None) -> Tuple[float, float, float]:
        """
        Calculate values using Ohm's Law: V = I * R
        Provide any two values, returns all three.
        
        Args:
            voltage: Voltage in Volts (or None to calculate)
            current: Current in Amperes (or None to calculate)
            resistance: Resistance in Ohms (or None to calculate)
            
        Returns:
            Tuple of (voltage, current, resistance)
            
        Raises:
            ValueError: If not exactly two values provided
        """
        provided = sum([voltage is not None, current is not None,
                       resistance is not None])
        if provided != 2:
            raise ValueError("Provide exactly two of: voltage, current, resistance")
        
        if voltage is None:
            voltage = current * resistance
        elif current is None:
            current = voltage / resistance
        else:  # resistance is None
            resistance = voltage / current
        
        return voltage, current, resistance

    @staticmethod
    def power_calculations(voltage: float = None, current: float = None,
                          resistance: float = None, power: float = None
                          ) -> Dict[str, float]:
        """
        Calculate electrical power relationships.
        P = V*I = V²/R = I²*R
        
        Args:
            voltage: Voltage in Volts
            current: Current in Amperes
            resistance: Resistance in Ohms
            power: Power in Watts
            
        Returns:
            Dictionary with all calculated values
        """
        results = {}
        
        # Determine what we have and calculate missing values
        if power is not None and voltage is not None:
            current = power / voltage
            resistance = voltage / current
        elif power is not None and current is not None:
            voltage = power / current
            resistance = voltage / current
        elif power is not None and resistance is not None:
            current = (power / resistance) ** 0.5
            voltage = current * resistance
        elif voltage is not None and current is not None:
            resistance = voltage / current
            power = voltage * current
        elif voltage is not None and resistance is not None:
            current = voltage / resistance
            power = voltage * current
        elif current is not None and resistance is not None:
            voltage = current * resistance
            power = current * current * resistance
        
        return {
            'voltage': voltage,
            'current': current,
            'resistance': resistance,
            'power': power,
        }

    @staticmethod
    def thermal_voltage(temperature_k: float) -> float:
        """
        Calculate thermal voltage Vt = kT/q at given temperature.
        
        Args:
            temperature_k: Temperature in Kelvin
            
        Returns:
            Thermal voltage in Volts (typically ~26mV at room temperature)
        """
        k = 1.380649e-23  # Boltzmann constant (J/K)
        q = 1.602176634e-19  # Elementary charge (C)
        return (k * temperature_k) / q
