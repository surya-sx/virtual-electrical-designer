"""
Backend-integrated component library panel
Direct integration with backend services (no HTTP API)
"""

from typing import Optional, Dict, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox
from PySide6.QtCore import Qt, Signal, QMimeData, QTimer, QByteArray
from PySide6.QtGui import QDrag
import logging

from frontend.backend_connector import get_backend_connector

logger = logging.getLogger(__name__)


class DraggableComponentTree(QTreeWidget):
    """Custom tree widget with proper drag-and-drop support for components"""
    
    def mousePressEvent(self, event):
        """Handle mouse press to start drag"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to start dragging"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if not hasattr(self, 'drag_start_position'):
            return
        
        # Check if we've moved far enough to start drag
        distance = (event.position() - self.drag_start_position).manhattanLength()
        if distance < 4:
            return
        
        # Get the item under cursor
        item = self.itemAt(int(self.drag_start_position.x()), int(self.drag_start_position.y()))
        if not item:
            return
        
        # Only drag components, not categories
        item_type = item.data(0, Qt.UserRole)
        if item_type != "component":
            return
        
        comp_id = item.data(0, Qt.UserRole + 1)
        comp_name = item.data(0, Qt.UserRole + 2)
        
        if not comp_id or not comp_name:
            return
        
        # Create mime data
        mime = QMimeData()
        mime.setData("component/type", comp_id.encode('utf-8'))
        mime.setData("component/name", comp_name.encode('utf-8'))
        mime.setText(f"{comp_id}|{comp_name}")
        
        # Create drag
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)


class BackendComponentLibraryPanel(QWidget):
    """
    Component Library Panel with direct backend integration
    
    Features:
    - Loads components directly from backend services
    - Local caching for performance
    - Search and filtering
    - Drag-and-drop support
    """
    
    # Signals
    component_selected = Signal(str, str)  # component_id, component_name
    component_loaded = Signal(list)  # loaded components
    library_error = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        
        try:
            self.backend = get_backend_connector()
        except Exception as e:
            logger.warning(f"Backend not available: {e}")
            self.backend = None
        
        self.component_cache: Dict[str, Dict] = {}
        self.category_items: Dict[str, QTreeWidgetItem] = {}
        
        # Setup UI
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)
        
        # Search bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search components...")
        self.search_box.setMinimumHeight(32)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 2px solid #90caf9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.search_box.textChanged.connect(self._filter_components)
        layout.addWidget(self.search_box)
        
        # Component tree (use custom draggable tree)
        self.tree = DraggableComponentTree()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTreeWidget::item {
                padding: 4px;
                height: 24px;
            }
            QTreeWidget::item:hover {
                background: #e3f2fd;
            }
            QTreeWidget::item:selected {
                background: #bbdefb;
            }
        """)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)
        
        # Register for library change notifications
        if self.backend:
            self.backend.register_library_change_callback(self._on_library_changed)
        
        # Load components from backend
        QTimer.singleShot(100, self._load_components)
    
    def _load_components(self):
        """Load components from backend"""
        try:
            if not self.backend:
                logger.warning("Backend not available, using fallback components")
                self._populate_fallback_components()
                return
            
            logger.info("Loading components from backend...")
            
            # Get categories from backend
            categories = self.backend.get_component_categories()
            
            if not isinstance(categories, dict) or len(categories) == 0:
                logger.warning("No categories from backend")
                self._populate_fallback_components()
                return
            
            self.tree.clear()
            self.category_items.clear()
            self.component_cache.clear()
            
            total_components = 0
            
            # Add each category and its components
            for category_name, components in categories.items():
                cat_item = QTreeWidgetItem([category_name])
                cat_item.setData(0, Qt.UserRole, "category")
                self.tree.addTopLevelItem(cat_item)
                self.category_items[category_name] = cat_item
                
                # Add components from the category
                try:
                    if isinstance(components, list):
                        for comp in components:
                            comp_id = comp.get('id') or comp.get('name', '').lower()
                            comp_name = comp.get('name', '')
                            
                            if comp_name:
                                comp_item = QTreeWidgetItem([comp_name])
                                comp_item.setData(0, Qt.UserRole, "component")
                                comp_item.setData(0, Qt.UserRole + 1, comp_id)
                                comp_item.setData(0, Qt.UserRole + 2, comp_name)
                                
                                # Cache component
                                self.component_cache[comp_id] = comp
                                
                                # Add tooltip
                                description = comp.get('description', f'Component: {comp_name}')
                                comp_item.setToolTip(0, description)
                                
                                cat_item.addChild(comp_item)
                                total_components += 1
                
                except Exception as e:
                    logger.error(f"Error loading category {category_name}: {e}")
            
            self.tree.expandAll()
            logger.info(f"✓ Loaded {total_components} components from backend")
            self.component_loaded.emit(list(self.component_cache.values()))
        
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            self.library_error.emit(str(e))
            self._populate_fallback_components()
    
    def _populate_fallback_components(self):
        """Fallback component library (static list)"""
        logger.info("Loading fallback component library...")
        
        components_by_category = {
            "Passive Components": [
                ("resistor", "Resistor"),
                ("capacitor", "Capacitor"),
                ("inductor", "Inductor"),
                ("ground", "Ground"),
            ],
            "Power Sources": [
                ("dc_source", "DC Source"),
                ("ac_source", "AC Source"),
                ("battery", "Battery"),
                ("current_source", "Current Source"),
            ],
            "Semiconductors": [
                ("diode", "Diode"),
                ("led", "LED"),
                ("bjt", "BJT Transistor"),
                ("mosfet", "MOSFET"),
                ("scr", "SCR"),
            ],
            "Integrated Circuits": [
                ("opamp", "Op-Amp"),
                ("timer_555", "555 Timer"),
                ("comparator", "Comparator"),
                ("multiplexer", "Multiplexer"),
            ],
            "Logic Gates": [
                ("and_gate", "AND Gate"),
                ("or_gate", "OR Gate"),
                ("not_gate", "NOT Gate"),
                ("nand_gate", "NAND Gate"),
            ],
            "Measurement": [
                ("ammeter", "Ammeter"),
                ("voltmeter", "Voltmeter"),
                ("wattmeter", "Wattmeter"),
            ],
            "Test Equipment": [
                ("oscilloscope", "Oscilloscope"),
                ("function_generator", "Function Generator"),
                ("multimeter_digital", "Digital Multimeter"),
                ("spectrum_analyzer", "Spectrum Analyzer"),
                ("power_supply_bench", "Bench Power Supply"),
                ("clamp_meter", "Clamp Meter"),
                ("logic_analyzer", "Logic Analyzer"),
                ("lcr_meter", "LCR Meter"),
            ],
        }
        
        self.tree.clear()
        self.category_items.clear()
        
        for category, items in components_by_category.items():
            cat_item = QTreeWidgetItem([category])
            cat_item.setData(0, Qt.UserRole, "category")
            self.tree.addTopLevelItem(cat_item)
            self.category_items[category] = cat_item
            
            for comp_id, comp_name in items:
                comp_item = QTreeWidgetItem([comp_name])
                comp_item.setData(0, Qt.UserRole, "component")
                comp_item.setData(0, Qt.UserRole + 1, comp_id)
                comp_item.setData(0, Qt.UserRole + 2, comp_name)
                cat_item.addChild(comp_item)
                
                # Cache for compatibility
                self.component_cache[comp_id] = {
                    'id': comp_id,
                    'name': comp_name,
                    'category': category
                }
        
        self.tree.expandAll()
        logger.info("✓ Fallback library loaded")
    
    def _filter_components(self, text: str):
        """Filter components based on search text"""
        text_lower = text.lower()
        
        for cat_name, cat_item in self.category_items.items():
            any_child_visible = False
            
            for i in range(cat_item.childCount()):
                child = cat_item.child(i)
                child_name = child.text(0).lower()
                
                # Match by name
                matches = text_lower in child_name
                child.setHidden(not matches)
                
                if matches:
                    any_child_visible = True
            
            cat_item.setHidden(not any_child_visible)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on component item"""
        comp_id = item.data(0, Qt.UserRole + 1)
        comp_name = item.data(0, Qt.UserRole + 2)
        
        if comp_id and comp_name:
            self.component_selected.emit(comp_id, comp_name)
    
    def search_components(self, query: str) -> List[Dict]:
        """Search components by query"""
        if not self.backend:
            return []
        
        try:
            return self.backend.search_components(query)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_component_details(self, component_id: str) -> Optional[Dict]:
        """Get component details"""
        if component_id in self.component_cache:
            return self.component_cache[component_id]
        
        if not self.backend:
            return None
        
        try:
            return self.backend.get_component_details(component_id)
        except Exception as e:
            logger.error(f"Error getting component details: {e}")
            return None
    
    def reload_from_backend(self):
        """Reload components from backend"""
        logger.info("Reloading components from backend...")
        self._load_components()
    
    def _on_library_changed(self, library_name: str):
        """Called when a library file changes on disk."""
        logger.info(f"Library changed: {library_name}, reloading UI...")
        self._load_components()

