"""
Value Parser Service

Parses and converts component value strings (e.g., "1k", "100n", "1M")
Handles standard electrical units and provides value conversion.
"""

import re
from typing import Union, Optional, Tuple


class ValueParser:
    """
    Parses electrical component values with unit prefixes.
    
    Supported prefixes:
    - p (pico): 1e-12
    - n (nano): 1e-9
    - u (micro): 1e-6
    - m (milli): 1e-3
    - (none): 1
    - k (kilo): 1e3
    - M (mega): 1e6
    - G (giga): 1e9
    """

    # Unit multipliers
    MULTIPLIERS = {
        'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3,
        '': 1, 'k': 1e3, 'M': 1e6, 'G': 1e9
    }

    # Component-specific base units
    UNITS = {
        'resistance': 'Ω',
        'capacitance': 'F',
        'inductance': 'H',
        'voltage': 'V',
        'current': 'A',
        'frequency': 'Hz',
        'time': 's',
    }

    @staticmethod
    def parse(value: str, component_type: Optional[str] = None) -> float:
        """
        Parse component value string to numeric value.
        
        Args:
            value: String like "1k", "100n", "1.5M"
            component_type: Optional component type for validation
            
        Returns:
            Numeric value in base units
            
        Raises:
            ValueError: If value cannot be parsed
        """
        if isinstance(value, (int, float)):
            return float(value)
        
        if not isinstance(value, str):
            raise ValueError(f"Invalid value type: {type(value)}")
        
        # Clean up the input - convert to lowercase for prefix matching
        value = value.strip().lower()
        
        # Remove common unit suffixes (Ω, F, H, V, A, Hz)
        for unit_char in ['ω', 'Ω', 'f', 'h', 'v', 'a', 'z']:
            value = value.replace(unit_char, '')
        
        # Pattern: number(s) followed by optional prefix
        pattern = r'^([\d.]+)\s*([pnumkMG]?)$'
        match = re.match(pattern, value)
        
        if not match:
            raise ValueError(f"Cannot parse value: {value}")
        
        numeric_part = float(match.group(1))
        prefix = match.group(2) or ''
        
        if prefix not in ValueParser.MULTIPLIERS:
            raise ValueError(f"Unknown prefix: {prefix}")
        
        return numeric_part * ValueParser.MULTIPLIERS[prefix]

    @staticmethod
    def format_value(value: float, unit: str = '', precision: int = 3) -> str:
        """
        Format numeric value with appropriate prefix.
        
        Args:
            value: Numeric value
            unit: Unit suffix (Ω, F, H, V, A, Hz)
            precision: Decimal places
            
        Returns:
            Formatted string like "1.5k", "100n", "1M"
        """
        if value == 0:
            return f"0 {unit}"
        
        abs_value = abs(value)
        sign = '-' if value < 0 else ''
        
        # Find appropriate prefix
        prefixes = [
            ('G', 1e9), ('M', 1e6), ('k', 1e3),
            ('', 1), ('m', 1e-3), ('u', 1e-6),
            ('n', 1e-9), ('p', 1e-12)
        ]
        
        for prefix, multiplier in prefixes:
            scaled = abs_value / multiplier
            if scaled >= 1 and scaled < 1000:
                formatted = f"{scaled:.{precision}g}".rstrip('0').rstrip('.')
                return f"{sign}{formatted}{prefix}{unit}".strip()
        
        # Fallback for very small/large values
        return f"{sign}{abs_value:.{precision}e}{unit}"

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert value between different SI prefixes.
        
        Args:
            value: Numeric value
            from_unit: Source prefix (e.g., 'k', 'm', 'n')
            to_unit: Target prefix (e.g., 'u', 'p')
            
        Returns:
            Converted value
        """
        if from_unit not in ValueParser.MULTIPLIERS:
            raise ValueError(f"Unknown source unit: {from_unit}")
        if to_unit not in ValueParser.MULTIPLIERS:
            raise ValueError(f"Unknown target unit: {to_unit}")
        
        base_value = value * ValueParser.MULTIPLIERS[from_unit]
        return base_value / ValueParser.MULTIPLIERS[to_unit]

    @staticmethod
    def validate_range(value: float, min_val: Optional[float] = None,
                       max_val: Optional[float] = None) -> bool:
        """
        Validate if value is within acceptable range.
        
        Args:
            value: Numeric value to check
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value
            
        Returns:
            True if value is within range
        """
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True

    @staticmethod
    def parse_tolerance(tolerance_str: str) -> Tuple[float, float]:
        """
        Parse tolerance string and return (min_multiplier, max_multiplier).
        
        Args:
            tolerance_str: String like "±5%", "10%", "0.1pF"
            
        Returns:
            Tuple of (min_factor, max_factor) for calculating range
        """
        tolerance_str = tolerance_str.strip()
        
        # Handle percentage tolerance
        if '%' in tolerance_str:
            percent = float(tolerance_str.replace('%', '').replace('±', '').strip())
            factor = percent / 100
            return (1 - factor, 1 + factor)
        
        # Handle absolute tolerance
        try:
            abs_tol = ValueParser.parse(tolerance_str)
            return (1 - abs_tol, 1 + abs_tol)
        except:
            raise ValueError(f"Cannot parse tolerance: {tolerance_str}")
