"""
Oscilloscope Properties Dialog - for configuring and viewing oscilloscope channels
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


class OscilloscopeDialog(QDialog):
    """Dialog for oscilloscope configuration and channel display"""
    
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None, comp_name="Oscilloscope", properties=None):
        super().__init__(parent)
        self.setWindowTitle(f"Oscilloscope - {comp_name}")
        self.setGeometry(100, 100, 600, 500)
        self.properties = properties or {}
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Oscilloscope Settings Tab
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        # Channels Tab
        channels_tab = self._create_channels_tab()
        tabs.addTab(channels_tab, "Channels")
        
        # Measurements Tab
        measurements_tab = self._create_measurements_tab()
        tabs.addTab(measurements_tab, "Measurements")
        
        # Button bar
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        close_btn = QPushButton("Close")
        apply_btn.clicked.connect(self._apply_settings)
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def _create_settings_tab(self):
        """Create oscilloscope settings tab"""
        widget = QGroupBox("Oscilloscope Settings")
        layout = QVBoxLayout()
        
        # Timebase
        timebase_layout = QHBoxLayout()
        timebase_layout.addWidget(QLabel("Timebase (s/div):"))
        self.timebase_combo = QComboBox()
        self.timebase_combo.addItems([
            "100 ns", "200 ns", "500 ns", "1 µs", "2 µs", "5 µs",
            "10 µs", "20 µs", "50 µs", "100 µs", "200 µs", "500 µs",
            "1 ms", "2 ms", "5 ms", "10 ms", "20 ms", "50 ms", "100 ms"
        ])
        self.timebase_combo.setCurrentText("1 ms")
        timebase_layout.addWidget(self.timebase_combo)
        layout.addLayout(timebase_layout)
        
        # Bandwidth
        bandwidth_layout = QHBoxLayout()
        bandwidth_layout.addWidget(QLabel("Bandwidth (MHz):"))
        self.bandwidth_spin = QSpinBox()
        self.bandwidth_spin.setRange(1, 500)
        self.bandwidth_spin.setValue(500)
        bandwidth_layout.addWidget(self.bandwidth_spin)
        layout.addLayout(bandwidth_layout)
        
        # Sampling Rate
        sampling_layout = QHBoxLayout()
        sampling_layout.addWidget(QLabel("Sampling Rate (GSa/s):"))
        self.sampling_spin = QDoubleSpinBox()
        self.sampling_spin.setRange(0.1, 10)
        self.sampling_spin.setValue(1)
        self.sampling_spin.setSingleStep(0.1)
        sampling_layout.addWidget(self.sampling_spin)
        layout.addLayout(sampling_layout)
        
        # Record Length
        record_layout = QHBoxLayout()
        record_layout.addWidget(QLabel("Record Length (points):"))
        self.record_spin = QSpinBox()
        self.record_spin.setRange(1000, 10000000)
        self.record_spin.setValue(1000)
        self.record_spin.setSingleStep(1000)
        record_layout.addWidget(self.record_spin)
        layout.addLayout(record_layout)
        
        # Trigger Mode
        trigger_layout = QHBoxLayout()
        trigger_layout.addWidget(QLabel("Trigger Mode:"))
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(["Auto", "Normal", "Single"])
        trigger_layout.addWidget(self.trigger_combo)
        layout.addLayout(trigger_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_channels_tab(self):
        """Create channels configuration tab"""
        widget = QGroupBox("Channel Configuration")
        layout = QVBoxLayout()
        
        # Add channel button
        button_layout = QHBoxLayout()
        add_channel_btn = QPushButton("Add Channel")
        add_channel_btn.clicked.connect(self._add_channel)
        button_layout.addWidget(add_channel_btn)
        
        remove_channel_btn = QPushButton("Remove Channel")
        remove_channel_btn.clicked.connect(self._remove_channel)
        button_layout.addWidget(remove_channel_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Channel settings table
        self.channels_table = QTableWidget()
        self.channels_table.setColumnCount(5)
        self.channels_table.setHorizontalHeaderLabels(
            ["Channel", "Color", "Enabled", "Coupling", "Scale (V/div)"]
        )
        self.channels_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        
        # Add 4 channels initially
        self._init_channels()
        
        layout.addWidget(self.channels_table)
        widget.setLayout(layout)
        return widget
    
    def _init_channels(self):
        """Initialize default channels"""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
        for i in range(4):
            self._add_channel_row(f"CH{i+1}", colors[i], i < 2)
    
    def _add_channel_row(self, ch_name, color, enabled):
        """Add a channel row to the table"""
        row = self.channels_table.rowCount()
        self.channels_table.insertRow(row)
        
        # Channel name
        ch_item = QTableWidgetItem(ch_name)
        ch_item.setFlags(ch_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.channels_table.setItem(row, 0, ch_item)
        
        # Color
        color_item = QTableWidgetItem()
        color_item.setBackground(QColor(color))
        color_item.setFlags(color_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.channels_table.setItem(row, 1, color_item)
        
        # Enabled checkbox
        enabled_item = QTableWidgetItem("✓")
        enabled_item.setFlags(enabled_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        enabled_item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
        self.channels_table.setItem(row, 2, enabled_item)
        
        # Coupling
        coupling_item = QTableWidgetItem("DC")
        self.channels_table.setItem(row, 3, coupling_item)
        
        # Scale
        scale_item = QTableWidgetItem("1 V")
        self.channels_table.setItem(row, 4, scale_item)
    
    def _add_channel(self):
        """Add a new channel to the oscilloscope"""
        num_channels = self.channels_table.rowCount()
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#808080"]
        
        # Cycle through colors if more than 8 channels
        color = colors[num_channels % len(colors)]
        ch_name = f"CH{num_channels + 1}"
        
        self._add_channel_row(ch_name, color, enabled=True)
        self.channels_table.resizeColumnsToContents()
    
    def _remove_channel(self):
        """Remove the last channel from the oscilloscope"""
        num_channels = self.channels_table.rowCount()
        if num_channels > 1:  # Keep at least 1 channel
            self.channels_table.removeRow(num_channels - 1)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Must have at least 1 channel")
    
    def _create_measurements_tab(self):
        """Create measurements/statistics tab"""
        widget = QGroupBox("Measurements")
        layout = QVBoxLayout()
        
        # Measurements table
        self.measurements_table = QTableWidget()
        self.measurements_table.setColumnCount(4)
        self.measurements_table.setHorizontalHeaderLabels(
            ["Channel", "Measurement", "Value", "Unit"]
        )
        self.measurements_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        
        # Measurements will be populated based on enabled channels
        self._populate_measurements()
        
        layout.addWidget(self.measurements_table)
        
        # Update button
        update_btn = QPushButton("Update Measurements")
        update_btn.clicked.connect(self._update_measurements)
        layout.addWidget(update_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _populate_measurements(self):
        """Populate measurements table based on enabled channels"""
        self.measurements_table.setRowCount(0)
        
        measurement_types = ["Frequency", "Period", "Amplitude", "RMS"]
        measurement_units = ["Hz", "s", "V", "V"]
        
        row = 0
        for ch_idx in range(self.channels_table.rowCount()):
            ch_item = self.channels_table.item(ch_idx, 0)
            enabled_item = self.channels_table.item(ch_idx, 2)
            
            if ch_item and enabled_item and enabled_item.checkState() == Qt.CheckState.Checked:
                ch_name = ch_item.text()
                
                for meas, unit in zip(measurement_types, measurement_units):
                    self.measurements_table.insertRow(row)
                    self.measurements_table.setItem(row, 0, QTableWidgetItem(ch_name))
                    self.measurements_table.setItem(row, 1, QTableWidgetItem(meas))
                    self.measurements_table.setItem(row, 2, QTableWidgetItem("0"))
                    self.measurements_table.setItem(row, 3, QTableWidgetItem(unit))
                    row += 1
    
    def _apply_settings(self):
        """Apply settings and emit signal"""
        settings = {
            "timebase": self.timebase_combo.currentText(),
            "bandwidth": self.bandwidth_spin.value(),
            "sampling_rate": self.sampling_spin.value(),
            "record_length": self.record_spin.value(),
            "trigger_mode": self.trigger_combo.currentText(),
        }
        self.settings_changed.emit(settings)
    
    def _update_measurements(self):
        """Update measurements based on currently enabled channels"""
        self._populate_measurements()
    
    def get_settings(self):
        """Get current settings"""
        return {
            "timebase": self.timebase_combo.currentText(),
            "bandwidth": self.bandwidth_spin.value(),
            "sampling_rate": self.sampling_spin.value(),
            "record_length": self.record_spin.value(),
            "trigger_mode": self.trigger_combo.currentText(),
        }
    
    def get_channel_configuration(self):
        """Get the current channel configuration
        
        Returns:
            dict: Configuration with channel settings
        """
        channels = []
        for row in range(self.channels_table.rowCount()):
            ch_name = self.channels_table.item(row, 0).text()
            color = self.channels_table.item(row, 1).background().color().name()
            enabled = self.channels_table.item(row, 2).checkState() == Qt.CheckState.Checked
            coupling = self.channels_table.cellWidget(row, 3).currentText() if self.channels_table.cellWidget(row, 3) else "AC"
            scale = self.channels_table.item(row, 4).text() if self.channels_table.item(row, 4) else "1V"
            
            channels.append({
                "name": ch_name,
                "color": color,
                "enabled": enabled,
                "coupling": coupling,
                "scale": scale
            })
        
        return {
            "timebase": self.timebase_combo.currentText(),
            "bandwidth": self.bandwidth_spin.value(),
            "sampling_rate": self.sampling_spin.value(),
            "record_length": self.record_spin.value(),
            "trigger_mode": self.trigger_combo.currentText(),
            "channels": channels
        }
