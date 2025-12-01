"""
Main application entry point for Virtual Electrical Designer & Simulator
"""
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress Qt font warnings before importing
os.environ['QT_DEBUG_PLUGINS'] = '0'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Import and install message handler BEFORE QApplication
from PySide6.QtCore import QtMsgType, qInstallMessageHandler

def qt_message_handler(msg_type, context, message):
    """Suppress Qt font warnings"""
    if "QFont::setPointSize" in message or "QBackingStore" in message or "QPaintDevice" in message:
        return

qInstallMessageHandler(qt_message_handler)

# NOW import QApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add src directory to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from frontend.ui.main_window import MainWindow
from frontend.backend_connector import get_backend_connector


def main():
    """Initialize and run the application"""
    # Initialize backend services
    print("\n" + "=" * 70)
    print("Virtual Electrical Designer & Simulator")
    print("=" * 70)
    
    try:
        backend = get_backend_connector()
        print("[OK] Backend services initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize backend: {e}")
        print("  Application will continue with limited functionality")
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Virtual Electrical Designer & Simulator")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("VED")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    exit_code = app.exec()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
