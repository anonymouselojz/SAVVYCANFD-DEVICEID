#!/usr/bin/env python3
"""
SavvyCANFD Device ID Tool - PyQt6 GUI Version
A simple Qt wrapper for the original CLI tool

Author: Kimi Claw
Date: 2025
"""

import sys
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
        QMessageBox, QGroupBox, QComboBox, QTextEdit, QSplitter
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError:
    print("Error: PyQt6 not installed. Run: pip install PyQt6")
    sys.exit(1)

# Import original logic (copy from savvycanfd_device_id.py)
SAVVYCANFD_CHANNELS = [
    "PCAN_ISABUS1", "PCAN_ISABUS2", "PCAN_ISABUS3", "PCAN_ISABUS4",
    "PCAN_ISABUS5", "PCAN_ISABUS6", "PCAN_ISABUS7", "PCAN_ISABUS8",
    "PCAN_DNGBUS1",
    "PCAN_PCIBUS1", "PCAN_PCIBUS2", "PCAN_PCIBUS3", "PCAN_PCIBUS4",
    "PCAN_PCIBUS5", "PCAN_PCIBUS6", "PCAN_PCIBUS7", "PCAN_PCIBUS8",
    "PCAN_PCIBUS9", "PCAN_PCIBUS10", "PCAN_PCIBUS11", "PCAN_PCIBUS12",
    "PCAN_PCIBUS13", "PCAN_PCIBUS14", "PCAN_PCIBUS15", "PCAN_PCIBUS16",
    "PCAN_USBBUS1", "PCAN_USBBUS2", "PCAN_USBBUS3", "PCAN_USBBUS4",
    "PCAN_USBBUS5", "PCAN_USBBUS6", "PCAN_USBBUS7", "PCAN_USBBUS8",
    "PCAN_USBBUS9", "PCAN_USBBUS10", "PCAN_USBBUS11", "PCAN_USBBUS12",
    "PCAN_USBBUS13", "PCAN_USBBUS14", "PCAN_USBBUS15", "PCAN_USBBUS16",
    "PCAN_PCCBUS1", "PCAN_PCCBUS2",
    "PCAN_LANBUS1", "PCAN_LANBUS2", "PCAN_LANBUS3", "PCAN_LANBUS4",
    "PCAN_LANBUS5", "PCAN_LANBUS6", "PCAN_LANBUS7", "PCAN_LANBUS8",
    "PCAN_LANBUS9", "PCAN_LANBUS10", "PCAN_LANBUS11", "PCAN_LANBUS12",
    "PCAN_LANBUS13", "PCAN_LANBUS14", "PCAN_LANBUS15", "PCAN_LANBUS16",
]

try:
    from can.interfaces.pcan import PcanBus
    PCAN_AVAILABLE = True
except ImportError:
    PCAN_AVAILABLE = False


def parse_id(id_str: str) -> int:
    """Parse Device ID string, supports decimal and hexadecimal"""
    id_str = id_str.strip()
    if id_str.lower().startswith('0x'):
        return int(id_str, 16)
    if id_str.lower().endswith('h'):
        return int(id_str[:-1], 16)
    return int(id_str)


def format_id(device_id: int) -> str:
    """Format Device ID display"""
    return f"{device_id} (0x{device_id:08X})"


def list_devices():
    """Scan and list all available SavvyCANFD devices"""
    if not PCAN_AVAILABLE:
        return []
    
    devices = []
    for channel in SAVVYCANFD_CHANNELS:
        try:
            bus = PcanBus(channel=channel, bitrate=500000)
            try:
                device_id = bus.get_device_number()
                devices.append((channel, device_id, "Connected"))
            except Exception as e:
                devices.append((channel, None, f"Error: {e}"))
            finally:
                bus.shutdown()
        except Exception:
            pass
    return devices


def get_device_id(channel: str) -> Optional[int]:
    """Get DEVICE ID for specified channel"""
    if not PCAN_AVAILABLE:
        return None
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            return bus.get_device_number()
        finally:
            bus.shutdown()
    except Exception:
        return None


def set_device_id(channel: str, device_id: int) -> bool:
    """Set DEVICE ID for specified channel"""
    if not PCAN_AVAILABLE:
        return False
    if not 0 <= device_id <= 0xFFFFFFFF:
        return False
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            return bus.set_device_number(device_id)
        finally:
            bus.shutdown()
    except Exception:
        return False


# Worker thread for scanning devices
class ScanWorker(QThread):
    finished = pyqtSignal(list)
    
    def run(self):
        devices = list_devices()
        self.finished.emit(devices)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SavvyCANFD Device ID Tool")
        self.setMinimumSize(800, 500)
        
        # Check dependencies
        if not PCAN_AVAILABLE:
            QMessageBox.warning(self, "Warning", 
                "python-can not installed or PCAN driver not found.\n"
                "Install with: pip install python-can")
        
        self.init_ui()
        self.scan_devices()
    
    def init_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Device list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Device table
        left_layout.addWidget(QLabel("<b>Connected Devices</b>"))
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels(["Channel", "Device ID", "Status"])
        self.device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.device_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.device_table.itemSelectionChanged.connect(self.on_device_selected)
        self.device_table.setColumnWidth(0, 150)
        self.device_table.setColumnWidth(1, 200)
        left_layout.addWidget(self.device_table)
        
        # Scan button
        self.scan_btn = QPushButton("🔄 Scan Devices")
        self.scan_btn.clicked.connect(self.scan_devices)
        left_layout.addWidget(self.scan_btn)
        
        layout.addWidget(left_panel, stretch=2)
        
        # Right panel - Operations
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Current device info
        info_group = QGroupBox("Device Info")
        info_layout = QVBoxLayout(info_group)
        
        self.selected_channel = QLabel("Channel: <none>")
        info_layout.addWidget(self.selected_channel)
        
        self.current_id_label = QLabel("Current ID: <none>")
        info_layout.addWidget(self.current_id_label)
        
        right_layout.addWidget(info_group)
        
        # Get ID section
        get_group = QGroupBox("Get Device ID")
        get_layout = QVBoxLayout(get_group)
        
        self.get_channel_input = QLineEdit()
        self.get_channel_input.setPlaceholderText("PCAN_USBBUS1")
        get_layout.addWidget(QLabel("Channel:"))
        get_layout.addWidget(self.get_channel_input)
        
        get_btn = QPushButton("📖 Get ID")
        get_btn.clicked.connect(self.get_id_clicked)
        get_layout.addWidget(get_btn)
        
        right_layout.addWidget(get_group)
        
        # Set ID section
        set_group = QGroupBox("Set Device ID")
        set_layout = QVBoxLayout(set_group)
        
        self.set_channel_input = QLineEdit()
        self.set_channel_input.setPlaceholderText("PCAN_USBBUS1")
        set_layout.addWidget(QLabel("Channel:"))
        set_layout.addWidget(self.set_channel_input)
        
        self.new_id_input = QLineEdit()
        self.new_id_input.setPlaceholderText("0x80FF0000 or 2164191232")
        set_layout.addWidget(QLabel("New ID (hex or decimal):"))
        set_layout.addWidget(self.new_id_input)
        
        set_btn = QPushButton("✏️ Set ID")
        set_btn.clicked.connect(self.set_id_clicked)
        set_layout.addWidget(set_btn)
        
        right_layout.addWidget(set_group)
        
        # Log output
        right_layout.addWidget(QLabel("<b>Log</b>"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(100)
        right_layout.addWidget(self.log_output)
        
        layout.addWidget(right_panel, stretch=1)
    
    def log(self, message: str):
        """Add log message"""
        self.log_output.append(message)
    
    def scan_devices(self):
        """Start device scan"""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.device_table.setRowCount(0)
        
        self.worker = ScanWorker()
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()
    
    def on_scan_finished(self, devices):
        """Handle scan completion"""
        self.device_table.setRowCount(len(devices))
        
        for row, (channel, dev_id, status) in enumerate(devices):
            self.device_table.setItem(row, 0, QTableWidgetItem(channel))
            
            id_str = format_id(dev_id) if dev_id is not None else "N/A"
            self.device_table.setItem(row, 1, QTableWidgetItem(id_str))
            
            self.device_table.setItem(row, 2, QTableWidgetItem(status))
        
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔄 Scan Devices")
        self.log(f"Found {len(devices)} device(s)")
    
    def on_device_selected(self):
        """Handle device selection"""
        selected = self.device_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        channel = self.device_table.item(row, 0).text()
        dev_id_str = self.device_table.item(row, 1).text()
        
        self.selected_channel.setText(f"Channel: {channel}")
        self.current_id_label.setText(f"Current ID: {dev_id_str}")
        
        # Auto-fill input fields
        self.get_channel_input.setText(channel)
        self.set_channel_input.setText(channel)
    
    def get_id_clicked(self):
        """Handle Get ID button"""
        channel = self.get_channel_input.text().strip().upper()
        if not channel:
            QMessageBox.warning(self, "Input Error", "Please enter a channel name")
            return
        
        device_id = get_device_id(channel)
        if device_id is not None:
            self.log(f"{channel} ID: {format_id(device_id)}")
            QMessageBox.information(self, "Device ID", 
                f"Channel: {channel}\nDevice ID: {format_id(device_id)}")
        else:
            self.log(f"Failed to get ID for {channel}")
            QMessageBox.warning(self, "Error", f"Cannot access {channel}")
    
    def set_id_clicked(self):
        """Handle Set ID button"""
        channel = self.set_channel_input.text().strip().upper()
        id_str = self.new_id_input.text().strip()
        
        if not channel or not id_str:
            QMessageBox.warning(self, "Input Error", "Please enter channel and new ID")
            return
        
        try:
            new_id = parse_id(id_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid ID format")
            return
        
        if not 0 <= new_id <= 0xFFFFFFFF:
            QMessageBox.warning(self, "Input Error", 
                "ID must be in range 0 - 0xFFFFFFFF")
            return
        
        # Get current ID for confirmation
        current_id = get_device_id(channel)
        if current_id is None:
            QMessageBox.warning(self, "Error", f"Cannot access {channel}")
            return
        
        # Confirm
        reply = QMessageBox.question(self, "Confirm Change",
            f"Change {channel} ID from\n{format_id(current_id)}\nto\n{format_id(new_id)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if set_device_id(channel, new_id):
                self.log(f"✓ Changed {channel} ID to {format_id(new_id)}")
                QMessageBox.information(self, "Success",
                    f"Device ID changed successfully!\n"
                    f"Please replug the device or restart system.")
                self.scan_devices()  # Refresh list
            else:
                self.log(f"✗ Failed to set {channel} ID")
                QMessageBox.critical(self, "Error", "Failed to set device ID")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
