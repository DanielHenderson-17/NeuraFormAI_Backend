#!/usr/bin/env python3
"""
Test script to verify VRM blinking functionality.
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer

# Add the chat_ui directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

from chat_ui.center.vrm_container import VRMContainer

class BlinkTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRM Blink Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create VRM container
        self.vrm_container = VRMContainer()
        layout.addWidget(self.vrm_container)
        
        # Create test button
        self.blink_button = QPushButton("Trigger Blink")
        self.blink_button.clicked.connect(self.trigger_blink)
        layout.addWidget(self.blink_button)
        
        # Load a VRM model
        vrm_path = os.path.join(os.path.dirname(__file__), "chat_ui", "assets", "vrms", "gwen_model.vrm")
        if os.path.exists(vrm_path):
            print(f"Loading VRM: {vrm_path}")
            self.vrm_container.load_vrm(vrm_path)
        else:
            print(f"VRM file not found: {vrm_path}")
        
        # Set up auto-blink timer (every 3 seconds)
        self.auto_blink_timer = QTimer()
        self.auto_blink_timer.timeout.connect(self.trigger_blink)
        self.auto_blink_timer.start(3000)  # 3 seconds
    
    def trigger_blink(self):
        """Trigger a manual blink"""
        print("🟢 Manual blink triggered!")
        self.vrm_container.trigger_blink()

def main():
    app = QApplication(sys.argv)
    
    window = BlinkTestWindow()
    window.show()
    
    print("🟢 Blink test window opened. The VRM should blink automatically every 3 seconds.")
    print("🟢 You can also click the 'Trigger Blink' button to manually trigger blinks.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 