# Virtual Electrical Designer & Simulator

A comprehensive desktop application for designing, simulating, and analyzing electrical circuits and power systems.

## ✨ Latest Features (NEW)

### 🎨 **Interactive Circuit Editing**
- **Component Visual Resizing**: Click and drag blue corner dots to resize components dynamically
- **Wire Drawing**: Click blue port dots and drag to create connections between components
- **Live Component Dragging**: Move components anywhere on the canvas
- **Grid Snapping**: Components snap to grid for organized layouts
- **Multi-select**: Select multiple components for batch operations

### 🔍 **Enhanced Oscilloscope Tool**
- **Dynamic Channel Management**: Add/remove channels on-demand (no longer limited to 4)
- **Flexible Channel Configuration**: Each channel configurable for coupling, scale, and color
- **Live Measurements**: Automatic frequency, period, amplitude, and RMS calculations
- **Smart Measurements Update**: Measurements dynamically update based on enabled channels
- **8-Color Channel Support**: Channels cycle through distinct colors for easy identification

### 🔌 **Interactive Simulation Engine**
- **Edit Component Values Live**: Double-click properties to change resistance, capacitance, voltage, current, inductance
- **Component Descriptions**: See detailed descriptions and instructions for every component property
- **Three Analysis Types**:
  - **DC Analysis**: Steady-state voltages, currents, and power dissipation
  - **AC Analysis**: Frequency sweep with impedance and phase response
  - **Transient Analysis**: Time-domain responses (capacitor charging, inductor kick, etc.)
- **Real-time Results**: View node voltages, component currents, and power in formatted tables
- **Unit Parsing**: Automatic conversion (1k → 1000Ω, 100n → 100nF, 10u → 10µF, etc.)

### 📊 **Smart Properties Panel**
- Click any component to see all its properties
- Each property has:
  - **Value Editor**: Spinbox or text field for easy editing
  - **Description**: What this property means and does
  - **Instructions**: How to use and typical values
  - **Units**: Proper electrical units displayed
- **Organized Categories**: Electrical, Physical, Simulation, Advanced tabs

### 🎛️ **Component Support**
- **Resistors**: Resistance, tolerance, power rating, temperature coefficient, package, part number
- **Capacitors**: Capacitance, voltage rating, ESR, dielectric type, temperature coefficient
- **Inductors**: Inductance, DCR, saturation current, core type, Q factor
- **Voltage Sources**: Voltage, internal impedance, type (DC/AC)
- **Current Sources**: Current, type (DC/AC)
- **Ground/Reference**: For circuit grounding

## Features

- **Circuit Design**: Intuitive drag-and-drop interface for building electrical circuits
- **Multi-type Simulation**: DC, AC, transient, parametric sweep, and Monte Carlo analysis
- **Power Systems Analysis**: Three-phase load flow, fault analysis, and protection curves
- **Design Wizards**: Transformer design, cable sizing, power factor correction, and battery sizing
- **Component Library**: Built-in and customizable component libraries with full property definitions
- **Reports & Export**: Generate comprehensive reports and export in PDF, HTML, CSV, PNG, and SVG formats
- **AI-powered Assistant**: Circuit error checking, fix suggestions, and component explanations
- **Script Editor**: Python scripting interface for advanced automation

## Project Structure

```
virtual-electrical-designer/
├── src/
│   ├── frontend/              # PySide6 UI components
│   │   ├── ui/               # Main window and dialogs
│   │   └── panels/           # Panel components (library, inspector, console, simulation, etc.)
│   └── backend/              # Core simulation and analysis engines
│       ├── circuit/          # Circuit model and management
│       ├── simulation/       # DC/AC/transient solvers + circuit solver ✨ NEW
│       ├── power_systems/    # Three-phase and fault analysis
│       ├── design_wizards/   # Design calculation tools
│       ├── reporting/        # Report generation
│       ├── ai_helper/        # AI-assisted features
│       └── scripting/        # Python script runtime
├── data/
│   ├── projects/             # User project files (.vedproj, .vedcir)
│   ├── libraries/            # Component libraries (.vedlib) - Updated with full properties ✨
│   └── exports/              # Generated exports (PDF, HTML, CSV, etc.)
├── docs/                      # Documentation
├── tests/                     # Unit and integration tests
├── QUICK_START.md            # ✨ Quick start guide for simulation
├── SIMULATION_GUIDE.md       # ✨ Detailed simulation documentation
├── README_SIMULATION.md      # ✨ Complete simulation features overview
└── requirements.txt           # Python dependencies
```

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python -m src.frontend.main
```

## Current Status

✅ **All Features Operational**
- Main application running and fully functional
- All 7 menus (File, Edit, View, Simulation, Tools, Window, Help) connected and working
- 6 Engineering tools available (Transformer Designer, Cable Sizing, Fault Calculator, PF Correction, Battery Tool, Library Manager)
- Script Editor fully functional
- All toolbar buttons and keyboard shortcuts working
- **99 Components** loaded from extended libraries (Resistors, Capacitors, Transistors, Diodes, ICs, Sensors, Test Equipment, etc.)
- **SVG Icon System** with modern open-source icons
- **Windows Unicode Support** for international characters and symbols
- **Component Resizing** with dynamic port calculation
- **Wire Dragging** from blue port dots with visual preview
- **Oscilloscope Channels** fully dynamic with unlimited channel support

See `FIX_SUMMARY.md` for latest fixes and `VALIDATION_REPORT.md` for detailed verification.

## Technology Stack

- **Frontend**: Python, PySide6, pyqtgraph with SVG icon support
- **Backend**: Python with NumPy, SciPy, SymPy, NetworkX
- **Graphics**: Painter-based canvas with dynamic scaling and anti-aliasing
- **Data Formats**:
  - Projects: `.vedproj`
  - Circuits: `.vedcir`
  - Component Libraries: `.vedlib` (13 library files with 99 components)
  - Exports: `.csv`, `.pdf`, `.html`, `.png`, `.svg`
- **UI Assets**: SVG icons in `assets/icons/` directory

## Development

### Backend Modules

- **ProjectManager**: Project lifecycle management
- **CircuitModel**: Node/component graph representation
- **SimulationEngine**: DC/AC/transient solvers
- **PowerSystemEngine**: Three-phase and fault analysis
- **DesignWizardsEngine**: Engineering calculation tools
- **ReportGenerator**: Report and export generation
- **AIHelper**: Intelligent circuit assistance
- **ScriptRuntime**: Custom Python script execution

### Frontend Components

- **MenuBar**: File, Edit, View, Simulation, Tools, Window, Help menus
- **MainToolbar**: Quick access to common operations
- **ComponentLibraryPanel**: Searchable component catalog
- **CircuitCanvas**: Interactive circuit editor with grid and pan/zoom
- **InspectorPanel**: Component, circuit, and simulation properties
- **ConsolePanel**: Log viewer with filtering
- **WaveformPanel**: Signal visualization with cursors
- **ReportsPanel**: Summary, BOM, and results
- **ScriptEditorPanel**: Python code editor and execution

## License

MIT License

Copyright (c) 2025 Virtual Electrical Designer contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

