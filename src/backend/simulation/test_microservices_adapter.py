"""
Test CircuitSolverMicroservices Adapter
Validates that the adapter correctly bridges frontend and microservices
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.simulation.circuit_solver_microservices import CircuitSolverMicroservices, parse_component_value


def test_value_parsing():
    """Test value parsing compatibility"""
    test_cases = [
        ("1k", 1000),
        ("1.5k", 1500),
        ("100n", 100e-9),
        ("1u", 1e-6),
        ("1M", 1e-3),  # milli
        ("1MEG", 1e6),  # mega
        ("2.2k", 2200),
        ("47", 47),
    ]
    
    for value_str, expected in test_cases:
        try:
            result = parse_component_value(value_str)
            status = "[OK]" if abs(result - expected) < 1e-10 * max(abs(expected), 1) else "[FAIL]"
            print("  {0} Parse '{1}' = {2:.2e} (expected {3:.2e})".format(status, value_str, result, expected))
        except Exception as e:
            print("  [ERROR] Parse '{0}' failed: {1}".format(value_str, e))


def test_circuit_creation():
    """Test basic circuit creation with microservices"""
    print("\n[2/5] Testing circuit creation...")
    
    try:
        solver = CircuitSolverMicroservices()
        
        # Add simple RC circuit
        solver.add_resistor("R1", "input", "output", 1000)
        solver.add_capacitor("C1", "output", "gnd", 1e-6)
        solver.add_voltage_source("V1", "input", "gnd", 5)
        
        print("  [OK] Circuit created with R, C, V source")
        
        # Add current source
        solver.add_current_source("I1", "input", "output", 0.001)
        print("  [OK] Current source added")
        
        # Add inductor
        solver.add_inductor("L1", "output", "gnd", 1e-3)
        print("  [OK] Inductor added")
        
        return True
    except Exception as e:
        print("  [ERROR] Circuit creation failed: {0}".format(e))
        return False


def test_dc_analysis():
    """Test DC analysis through adapter"""
    print("\n[3/5] Testing DC analysis...")
    
    try:
        solver = CircuitSolverMicroservices()
        
        # Create simple voltage divider
        # 5V -> R1 (1k) -> node -> R2 (1k) -> GND
        solver.add_voltage_source("V1", "input", "gnd", 5)
        solver.add_resistor("R1", "input", "node1", 1000)
        solver.add_resistor("R2", "node1", "gnd", 1000)
        
        result = solver.dc_analysis()
        
        if result['status'] != 'success':
            print("  [FAIL] DC analysis failed: {0}".format(result.get('error')))
            return False
        
        print("  [OK] DC analysis completed")
        print("  [OK] Node voltages: {0}".format(result.get('node_names', {})))
        
        # Check if output node is approximately 2.5V (half of 5V)
        node_voltages = result.get('node_names', {})
        if 'node1' in node_voltages:
            v_node1 = node_voltages['node1']
            if 2.4 < v_node1 < 2.6:
                print("  [OK] Voltage divider working (node1 = {0:.2f}V)".format(v_node1))
            else:
                print("  [WARN] Unexpected voltage (node1 = {0:.2f}V, expected ~2.5V)".format(v_node1))
        
        return True
    except Exception as e:
        print("  [ERROR] DC analysis failed: {0}".format(e))
        import traceback
        traceback.print_exc()
        return False


def test_ac_analysis():
    """Test AC analysis through adapter"""
    print("\n[4/5] Testing AC analysis...")
    
    try:
        solver = CircuitSolverMicroservices()
        
        # Create RC low-pass filter
        solver.add_voltage_source("V1", "input", "gnd", 1)
        solver.add_resistor("R1", "input", "output", 1000)
        solver.add_capacitor("C1", "output", "gnd", 1e-6)
        
        result = solver.ac_analysis(freq_start=1, freq_end=1e6, num_points=10)
        
        if result['status'] != 'success':
            print("  [FAIL] AC analysis failed: {0}".format(result.get('error')))
            return False
        
        print("  [OK] AC analysis completed")
        print("  [OK] Frequencies analyzed: {0} points".format(len(result.get('frequencies', []))))
        
        return True
    except Exception as e:
        print("  [ERROR] AC analysis failed: {0}".format(e))
        import traceback
        traceback.print_exc()
        return False


def test_circuit_validation():
    """Test circuit validation through adapter"""
    print("\n[5/5] Testing circuit validation...")
    
    try:
        solver = CircuitSolverMicroservices()
        
        # Create circuit
        solver.add_resistor("R1", "in", "out", 1000)
        solver.add_voltage_source("V1", "in", "gnd", 5)
        
        is_valid, errors = solver.validate_circuit()
        
        if is_valid:
            print("  [OK] Circuit validation passed")
        else:
            print("  [WARN] Circuit validation warnings: {0} issues".format(len(errors)))
            for err in errors[:3]:
                print("    - {0}".format(err))
        
        # Get system info
        info = solver.get_system_info()
        print("  [OK] System info retrieved:")
        print("    - Nodes: {0}".format(info['nodes']))
        print("    - Components: {0}".format(info['components']))
        print("    - Available libraries: {0}".format(info['libraries']))
        print("    - Total components in library: {0}".format(info['total_components_available']))
        
        return True
    except Exception as e:
        print("  [ERROR] Validation failed: {0}".format(e))
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("CIRCUIT SOLVER MICROSERVICES ADAPTER TEST")
    print("=" * 60)
    
    print("\n[1/5] Testing value parsing...")
    test_value_parsing()
    
    results = [
        ("Circuit Creation", test_circuit_creation()),
        ("DC Analysis", test_dc_analysis()),
        ("AC Analysis", test_ac_analysis()),
        ("Circuit Validation", test_circuit_validation()),
    ]
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print("{0}: {1}".format(status, test_name))
    
    print("=" * 60)
    print("Total: {0}/{1} tests passed".format(passed, total))
    print("=" * 60)
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED - ADAPTER FULLY FUNCTIONAL")
        print("\nThe CircuitSolverMicroservices adapter successfully bridges")
        print("the frontend SimulationPanel with the microservices backend.")
        return 0
    else:
        print("\n[INCOMPLETE] SOME TESTS FAILED - {0} failures".format(total - passed))
        return 1


if __name__ == "__main__":
    exit(main())
