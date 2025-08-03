#!/usr/bin/env python3
"""
VRM Expression Test Script

This script demonstrates the new expression capabilities by calling
the JavaScript functions we added to the VRM viewer.

Usage:
    python test_expressions.py
"""

import time
import sys
import os

# Add the chat_ui directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QComboBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import json

class VRMExpressionTester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRM Expression Tester")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create VRM viewer
        self.vrm_viewer = QWebEngineView()
        vrm_path = os.path.abspath("chat_ui/assets/vrm_viewer/index.html")
        self.vrm_viewer.setUrl(QUrl.fromLocalFile(vrm_path))
        layout.addWidget(self.vrm_viewer, 2)
        
        # Create control panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel, 1)
        
        # Model selector
        model_label = QLabel("Select VRM Model:")
        control_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "fuka_model.vrm",
            "gwen_model.vrm", 
            "kenji_model.vrm",
            "koan_model.vrm",
            "nika_model.vrm"
        ])
        self.model_combo.currentTextChanged.connect(self.load_model)
        control_layout.addWidget(self.model_combo)
        
        # Load model button
        load_btn = QPushButton("Load Model")
        load_btn.clicked.connect(self.load_model)
        control_layout.addWidget(load_btn)
        
        control_layout.addSpacing(20)
        
        # Expression controls
        expr_label = QLabel("Expression Controls:")
        control_layout.addWidget(expr_label)
        
        # Individual expression buttons
        expressions = [
            ("Neutral", "neutral"),
            ("Joy", "joy"),
            ("Angry", "angry"),
            ("Fun", "fun"),
            ("Sorrow", "sorrow"),
            ("Surprised", "surprised")
        ]
        
        for name, expr in expressions:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, e=expr: self.set_expression(e))
            control_layout.addWidget(btn)
        
        control_layout.addSpacing(20)
        
        # Lip sync controls
        lip_label = QLabel("Lip Sync Controls:")
        control_layout.addWidget(lip_label)
        
        lip_buttons = [
            ("A (Ah)", "a"),
            ("I (Ee)", "i"),
            ("U (Oo)", "u"),
            ("E (Eh)", "e"),
            ("O (Oh)", "o")
        ]
        
        for name, phoneme in lip_buttons:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, p=phoneme: self.set_lip_sync(p))
            control_layout.addWidget(btn)
        
        # Clear lip sync button
        clear_lip_btn = QPushButton("Clear Lip Sync")
        clear_lip_btn.clicked.connect(self.clear_lip_sync)
        control_layout.addWidget(clear_lip_btn)
        
        control_layout.addSpacing(20)
        
        # Utility buttons
        util_label = QLabel("Utility Controls:")
        control_layout.addWidget(util_label)
        
        reset_btn = QPushButton("Reset All Expressions")
        reset_btn.clicked.connect(self.reset_expressions)
        control_layout.addWidget(reset_btn)
        
        blink_btn = QPushButton("Trigger Blink")
        blink_btn.clicked.connect(self.trigger_blink)
        control_layout.addWidget(blink_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        # Wait for VRM viewer to be ready
        self.ready_timer = QTimer()
        self.ready_timer.timeout.connect(self.check_vrm_ready)
        self.ready_timer.start(100)
        
        # Load first model
        QTimer.singleShot(2000, self.load_model)
    
    def check_vrm_ready(self):
        """Check if VRM viewer is ready"""
        self.vrm_viewer.page().runJavaScript(
            "window.vrmViewerReady",
            self.on_vrm_ready_check
        )
    
    def on_vrm_ready_check(self, result):
        if result:
            self.ready_timer.stop()
            self.status_label.setText("VRM Viewer Ready")
            self.load_model()
    
    def load_model(self):
        """Load the selected VRM model"""
        model_name = self.model_combo.currentText()
        vrm_path = f"../vrms/{model_name}"
        
        self.vrm_viewer.page().runJavaScript(
            f'window.loadVRM("{vrm_path}")',
            self.on_model_loaded
        )
        self.status_label.setText(f"Loading {model_name}...")
    
    def on_model_loaded(self, result):
        """Called when model is loaded"""
        self.status_label.setText("Model loaded successfully")
        
        # Get available expressions
        self.vrm_viewer.page().runJavaScript(
            "window.getAvailableExpressions()",
            self.on_expressions_loaded
        )
    
    def on_expressions_loaded(self, expressions):
        """Called when expressions are loaded"""
        if expressions:
            print(f"Available expressions: {expressions}")
    
    def set_expression(self, expression_name):
        """Set a specific expression"""
        self.vrm_viewer.page().runJavaScript(
            f'window.setExpression("{expression_name}", 1.0)',
            lambda result: self.status_label.setText(f"Set expression: {expression_name}")
        )
    
    def set_lip_sync(self, phoneme):
        """Set lip sync expression"""
        self.vrm_viewer.page().runJavaScript(
            f'window.setLipSync("{phoneme}")',
            lambda result: self.status_label.setText(f"Set lip sync: {phoneme}")
        )
    
    def clear_lip_sync(self):
        """Clear lip sync expressions"""
        self.vrm_viewer.page().runJavaScript(
            "window.clearLipSync()",
            lambda result: self.status_label.setText("Cleared lip sync")
        )
    
    def reset_expressions(self):
        """Reset all expressions to neutral"""
        self.vrm_viewer.page().runJavaScript(
            "window.resetExpressions()",
            lambda result: self.status_label.setText("Reset all expressions")
        )
    
    def trigger_blink(self):
        """Trigger a blink"""
        self.vrm_viewer.page().runJavaScript(
            "window.triggerBlink()",
            lambda result: self.status_label.setText("Triggered blink")
        )

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = VRMExpressionTester()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 