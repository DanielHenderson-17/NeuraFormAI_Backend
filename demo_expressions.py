#!/usr/bin/env python3
"""
VRM Expression Integration Demo

This script demonstrates how to integrate the new VRM expression capabilities
into your existing chat system. It shows how to trigger different expressions
based on chat content, emotions, or user interactions.

Usage:
    python demo_expressions.py
"""

import sys
import os
import time
import random
from typing import List, Dict

# Add the chat_ui directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QTextEdit, QComboBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# Import the VRM webview
from center.vrm_webview import VRMWebView

class ExpressionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRM Expression Integration Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create VRM viewer (left side)
        self.vrm_viewer = VRMWebView()
        layout.addWidget(self.vrm_viewer, 2)
        
        # Create control panel (right side)
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
        
        # Chat simulation section
        chat_label = QLabel("Chat Simulation:")
        control_layout.addWidget(chat_label)
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("Type a message to simulate chat...")
        control_layout.addWidget(self.chat_input)
        
        # Send button
        send_btn = QPushButton("Send Message")
        send_btn.clicked.connect(self.simulate_chat)
        control_layout.addWidget(send_btn)
        
        control_layout.addSpacing(20)
        
        # Manual expression controls
        expr_label = QLabel("Manual Expression Controls:")
        control_layout.addWidget(expr_label)
        
        # Emotional expressions
        emotions = [
            ("😊 Joy", "joy"),
            ("😠 Angry", "angry"),
            ("😄 Fun", "fun"),
            ("😢 Sorrow", "sorrow"),
            ("😲 Surprised", "surprised"),
            ("😐 Neutral", "neutral")
        ]
        
        for name, emotion in emotions:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, e=emotion: self.set_emotion(e))
            control_layout.addWidget(btn)
        
        control_layout.addSpacing(20)
        
        # Lip sync demo
        lip_label = QLabel("Lip Sync Demo:")
        control_layout.addWidget(lip_label)
        
        lip_btn = QPushButton("Demo Lip Sync Sequence")
        lip_btn.clicked.connect(self.demo_lip_sync)
        control_layout.addWidget(lip_btn)
        
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
        
        # Load first model
        QTimer.singleShot(2000, self.load_model)
        
        # Expression mapping for chat simulation
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', '😊', '😄', '😍'],
            'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', '😠', '😡', '🤬'],
            'fun': ['fun', 'funny', 'lol', 'haha', 'amusing', '😆', '😂', '🤣'],
            'sorrow': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate', '😢', '😭', '😔'],
            'surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected', '😲', '😱', '🤯']
        }
    
    def load_model(self):
        """Load the selected VRM model"""
        model_name = self.model_combo.currentText()
        vrm_path = f"chat_ui/assets/vrms/{model_name}"
        
        self.vrm_viewer.load_vrm(vrm_path)
        self.status_label.setText(f"Loading {model_name}...")
        
        # Get available expressions after loading
        QTimer.singleShot(3000, self.vrm_viewer.get_available_expressions)
    
    def simulate_chat(self):
        """Simulate chat and trigger appropriate expressions"""
        message = self.chat_input.toPlainText().lower()
        if not message:
            return
        
        # Determine emotion from message content
        detected_emotion = self.detect_emotion(message)
        
        if detected_emotion:
            self.set_emotion(detected_emotion)
            self.status_label.setText(f"Detected emotion: {detected_emotion}")
        else:
            # Default to neutral for neutral messages
            self.set_emotion("neutral")
            self.status_label.setText("No specific emotion detected")
        
        # Clear input
        self.chat_input.clear()
        
        # Simulate lip sync for speaking
        self.simulate_speaking()
    
    def detect_emotion(self, message: str) -> str:
        """Detect emotion from message content"""
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in message for keyword in keywords):
                return emotion
        return None
    
    def simulate_speaking(self):
        """Simulate speaking with lip sync"""
        # Create a sequence of lip sync expressions
        phonemes = ['a', 'i', 'u', 'e', 'o']
        
        def speak_sequence(index=0):
            if index < len(phonemes):
                self.vrm_viewer.set_lip_sync(phonemes[index])
                QTimer.singleShot(200, lambda: speak_sequence(index + 1))
            else:
                # Clear lip sync after sequence
                QTimer.singleShot(500, self.vrm_viewer.clear_lip_sync)
        
        speak_sequence()
    
    def set_emotion(self, emotion: str):
        """Set emotional expression"""
        self.vrm_viewer.set_emotion(emotion)
        self.status_label.setText(f"Set emotion: {emotion}")
    
    def demo_lip_sync(self):
        """Demonstrate lip sync with a sequence"""
        self.status_label.setText("Running lip sync demo...")
        
        # More complex lip sync sequence
        sequence = [
            ('a', 300), ('i', 200), ('u', 300), ('e', 200), ('o', 300),
            ('a', 200), ('i', 300), ('u', 200), ('e', 300), ('o', 200)
        ]
        
        def run_sequence(index=0):
            if index < len(sequence):
                phoneme, duration = sequence[index]
                self.vrm_viewer.set_lip_sync(phoneme)
                QTimer.singleShot(duration, lambda: run_sequence(index + 1))
            else:
                self.vrm_viewer.clear_lip_sync()
                self.status_label.setText("Lip sync demo completed")
        
        run_sequence()
    
    def clear_lip_sync(self):
        """Clear lip sync expressions"""
        self.vrm_viewer.clear_lip_sync()
        self.status_label.setText("Cleared lip sync")
    
    def reset_expressions(self):
        """Reset all expressions to neutral"""
        self.vrm_viewer.reset_expressions()
        self.status_label.setText("Reset all expressions")
    
    def trigger_blink(self):
        """Trigger a blink"""
        self.vrm_viewer.trigger_blink()
        self.status_label.setText("Triggered blink")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = ExpressionDemo()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 