# Virtual Electrical Designer - Component Library System v3.0

## Overview
The new library system provides comprehensive component definitions with full editable properties for circuit simulation. All components include descriptions, specifications, and adjustable parameters for real-time analysis.

## Library Structure

### Files
- **resistors_library.json** - 8 resistor types with 10 editable properties each
- **capacitors_library.json** - 8 capacitor types with 10-12 editable properties each
- **library_index.json** - Master index for quick reference and component discovery

### Resistor Types (8 Total)

#### 1. Standard Resistor (Carbon Film)
- **Range**: 0.1Ω - 10MΩ
- **Tolerance**: ±5% typical
- **Power**: 1/8W - 2W
- **Use Cases**: Pull-up/pull-down, LED limiting, general impedance
- **Editable Properties**: 10 (Resistance, Tolerance, Power Rating, Temperature Coefficient, Operating Temp, Manufacturer, Part Number, Unit Cost)

#### 2. SMD Resistor (Thin Film)
- **Range**: 0.1Ω - 10MΩ
- **Tolerance**: ±1% 
- **Power**: 1/16W - 1W
- **Frequency**: Up to 1000MHz
- **Use Cases**: Modern PCBs, high-speed digital, automated assembly
- **Editable Properties**: 10 (includes ESR, Frequency, Package Type)

#### 3. High Power Resistor (Wire Wound)
- **Range**: 0.1Ω - 100kΩ
- **Power**: 1W - 500W+
- **Temperature Coefficient**: 20-50 ppm/°C (very stable)
- **Use Cases**: Power supplies, motor control, brake resistors
- **Editable Properties**: 9 (includes Max Peak Current, Thermal Resistance)

#### 4. High Frequency Resistor (RF Thin Film)
- **Range**: 25Ω - 150Ω (characteristic impedance)
- **Frequency**: Up to 10GHz
- **VSWR**: 1.1 typical
- **Use Cases**: RF circuits, antenna matching, impedance networks
- **Editable Properties**: 9 (includes VSWR, Return Loss, Characteristic Impedance)

#### 5. Precision Resistor (Thin Film)
- **Range**: 1Ω - 10MΩ
- **Tolerance**: 0.01% - 1%
- **Temperature Coefficient**: 5-100 ppm/°C
- **Long-term Stability**: < 0.5% per year
- **Use Cases**: DAC/ADC circuits, measurement, instrumentation
- **Editable Properties**: 9 (includes Noise Figure, Long-term Stability)

#### 6. Thin Film Audio Resistor (Low Noise)
- **Range**: 1Ω - 10MΩ
- **Noise Figure**: -20dB (ultra-low)
- **Temperature Coefficient**: 50 ppm/°C
- **Use Cases**: Audio amplifiers, microphone preamps, oscillators
- **Editable Properties**: 9 (includes Noise Figure, Humidity Stability)

#### 7. Thick Film SMD Resistor (Cost-Effective)
- **Range**: 0.1Ω - 10MΩ
- **Tolerance**: ±1%
- **Cost**: ~$0.005 per unit (cheapest option)
- **Use Cases**: Consumer electronics, high-volume production
- **Editable Properties**: 10 (RoHS compliant, standard packages)

#### 8. Wire Wound Precision Resistor
- **Range**: 0.1Ω - 100kΩ
- **Tolerance**: 0.1% - 5%
- **Power**: 0.5W - 200W+
- **Temperature Coefficient**: 5-50 ppm/°C (excellent)
- **MTBF**: >10 million hours
- **Use Cases**: Precision audio, test equipment, aerospace
- **Editable Properties**: 10 (most comprehensive, includes MTBF)

### Capacitor Types (8 Total)

#### 1. Ceramic Capacitor (Multi-Layer)
- **Range**: 1pF - 100μF
- **Voltage**: 6.3V - 1000V
- **Grades**: X7R (±15%), Y5V (±20%), Z5U (±20%), C0G/NP0
- **Use Cases**: Bypass, coupling, high-frequency filtering
- **Editable Properties**: 12 (includes ESR, ESL, Dielectric Grade)

#### 2. Electrolytic Capacitor (Al/Ta)
- **Range**: 1μF - 100,000μF
- **Voltage**: 6.3V - 500V
- **Types**: Aluminum (common), Tantalum (compact)
- **Use Cases**: Bulk filtering, power supply decoupling
- **Editable Properties**: 10 (includes Ripple Current, Lifespan)

#### 3. Film Capacitor (PP/PET/PS/PTFE)
- **Range**: 1nF - 100μF
- **Voltage**: 50V - 1000V
- **Dielectrics**: Polypropylene, Polyester, Polystyrene, PTFE
- **Use Cases**: AC coupling, RF circuits, audio quality
- **Editable Properties**: 10 (includes Dissipation Factor, non-polarized)

#### 4. Tantalum Capacitor (MnO2/Polymer)
- **Range**: 0.1μF - 220μF
- **Voltage**: 4V - 125V
- **Types**: MnO2 (ultra-reliable), Polymer (lower ESR)
- **MTBF**: Often >1 million hours
- **Use Cases**: Military/aerospace, high-reliability circuits
- **Editable Properties**: 10 (includes Voltage Derating)

#### 5. Mica Capacitor (Silver-Mica)
- **Range**: 1pF - 10μF
- **Voltage**: 100V - 5000V
- **Tolerance**: 0.5% - 5% (ultra-precise)
- **Q Factor**: >10,000 at 1MHz
- **Use Cases**: RF matching, precision filters, oscillators
- **Editable Properties**: 10 (includes Q Factor, Annual Drift)

#### 6. Supercapacitor (EDLC/Hybrid/Li-ion)
- **Range**: 0.1F - 5000F (enormous!)
- **Voltage**: 2.7V - 63V (can be stacked)
- **Types**: EDLC, Hybrid, Li-ion
- **Cycle Life**: >1 million cycles
- **Use Cases**: Energy storage, peak power, backup power
- **Editable Properties**: 10 (includes Leakage Current, Peak Current)

#### 7. Variable Capacitor (Air Gap/Vacuum Tuning)
- **Range**: 1pF - 1000pF
- **Voltage**: 100V - 5000V
- **Types**: Air-gap (common), Vacuum (higher Q)
- **Q Factor**: 100-1000+
- **Use Cases**: Radio tuning, impedance matching adjustment
- **Editable Properties**: 10 (includes Tuning Range, Mechanical Life)

#### 8. Paper Capacitor (Oil/Wax Impregnated)
- **Range**: 0.1μF - 100μF
- **Voltage**: 250V - 50kV (very high!)
- **Types**: Oil (high-voltage), Wax (vintage restoration)
- **Use Cases**: Power transmission, vintage audio, high-voltage systems
- **Editable Properties**: 10 (including Application Notes)

## Editable Properties Guide

### Property Categories

**Electrical Properties**
- Resistance/Capacitance (primary value)
- Tolerance percentage
- Voltage rating
- Power rating (resistors)
- Temperature coefficients

**Physical Properties**
- Package type/size
- Operating temperature range
- Frequency response

**Quality Metrics**
- ESR (Equivalent Series Resistance)
- ESL (Equivalent Series Inductance)
- Q Factor (capacitors)
- MTBF (reliability)
- Stability specifications

**Cost**
- Unit cost in USD
- Volume pricing information

### Property Ranges

Each property has:
- **Value**: Current setting
- **Unit**: Measurement unit (Ω, V, W, pF, etc.)
- **Min**: Minimum allowed value
- **Max**: Maximum allowed value
- **Step**: Increment for adjustment
- **Description**: Usage notes and examples

### Simulation Integration

Properties are fully editable during circuit design:
1. Select component in CircuitCanvas
2. Open Inspector Panel
3. Adjust any editable property
4. Changes propagate to SimulationPanel
5. Real-time analysis updates with new values

## Usage Examples

### Example 1: Adjusting Resistor Value
```
Component: Standard Resistor
Original: 1000Ω
Modified: 2200Ω  ← Adjust Resistance property
Tolerance: ±5%
Result: Component updates to 2200Ω ± 110Ω
```

### Example 2: Changing Power Rating
```
Component: High Power Resistor
Original: 5W
Modified: 10W  ← Increase Power Rating
Thermal Resistance: 50°C/W
Result: Better heat handling, larger component
```

### Example 3: Tuning Capacitor Value
```
Component: Ceramic Capacitor
Original: 100nF
Modified: 10μF  ← Change Capacitance
Voltage: 50V
Grade: X7R
Result: Larger capacitance, different frequency response
```

## Library Statistics

- **Total Component Types**: 16
- **Resistor Types**: 8
- **Capacitor Types**: 8
- **Total Editable Properties**: ~288
- **Average Properties/Component**: 18
- **All Components Simulation-Ready**: Yes

## Component Discovery

### By Application
- **Power Supply**: Electrolytic, Film capacitors + High-power resistors
- **RF/Microwave**: SMD, High-frequency, Mica capacitors + Precision resistors
- **Audio**: Thin-film audio resistors + Film/Paper capacitors
- **Cost-Sensitive**: Thick-film SMD resistors + Ceramic capacitors
- **Precision**: Precision resistors + Mica capacitors
- **High-Voltage**: Paper capacitors + High-power resistors
- **Vintage/Restoration**: Paper capacitors + Wire-wound resistors

### Common Values Reference

**E12 Decade Multipliers** (Standard Series)
1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2

**E24 Decade Multipliers** (Preferred)
1, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1

## Best Practices

1. **Start with Standard Components** - Use Standard Resistor and Ceramic Capacitor for prototyping
2. **Match Voltage Ratings** - Always use components rated above your supply voltage
3. **Consider Temperature** - Check operating temperature ranges for your circuit environment
4. **Adjust for Frequency** - Use high-frequency types for RF circuits
5. **Account for Tolerance** - Critical circuits benefit from precision components
6. **Power Dissipation** - Calculate resistor power and select appropriately rated component
7. **ESR/ESL Effects** - SMD components have lower parasitics for high-speed circuits

## Backward Compatibility

The new library system maintains simulation compatibility while providing enhanced component definitions. The property editing framework allows real-time adjustments without requiring circuit reconstruction.

## Future Enhancements

- Additional component types (Inductors, Transformers, Semiconductors)
- Component derating calculators
- Automatic component selection wizards
- Reliability prediction tools
- Cost optimization analysis

---
**Library Version**: 3.0  
**Last Updated**: 2024  
**Status**: Fully Operational
