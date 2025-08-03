#!/usr/bin/env python3
"""
Simple VRM Expression Test

This script directly tests the VRM expressions by importing the VRMWebView
and triggering expressions programmatically.

Usage:
    python simple_test.py
"""

import sys
import os
import time

# Add the chat_ui directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

def test_expressions():
    """Test VRM expressions directly"""
    print("🎭 Testing VRM Expressions...")
    
    try:
        # Import the VRM webview
        from center.vrm_webview import VRMWebView
        
        # Create VRM viewer
        print("📱 Creating VRM viewer...")
        vrm_viewer = VRMWebView()
        
        # Load a VRM model
        print("🔄 Loading VRM model...")
        vrm_path = "chat_ui/assets/vrms/fuka_model.vrm"
        vrm_viewer.load_vrm(vrm_path)
        
        # Wait a bit for the model to load
        print("⏳ Waiting for model to load...")
        time.sleep(5)
        
        # Test different expressions
        print("\n🎭 Testing Expressions:")
        
        expressions_to_test = [
            ("😊 Joy", "joy"),
            ("😠 Angry", "angry"), 
            ("😄 Fun", "fun"),
            ("😢 Sorrow", "sorrow"),
            ("😲 Surprised", "surprised"),
            ("😐 Neutral", "neutral")
        ]
        
        for name, emotion in expressions_to_test:
            print(f"  Testing {name}...")
            vrm_viewer.set_emotion(emotion)
            time.sleep(2)  # Hold each expression for 2 seconds
        
        # Test lip sync
        print("\n👄 Testing Lip Sync:")
        phonemes = ['a', 'i', 'u', 'e', 'o']
        for phoneme in phonemes:
            print(f"  Testing phoneme '{phoneme}'...")
            vrm_viewer.set_lip_sync(phoneme)
            time.sleep(0.5)
        
        # Clear lip sync
        vrm_viewer.clear_lip_sync()
        
        # Test blink
        print("\n👁️ Testing Blink:")
        for i in range(3):
            print(f"  Blink {i+1}/3...")
            vrm_viewer.trigger_blink()
            time.sleep(1)
        
        # Reset to neutral
        print("\n🔄 Resetting to neutral...")
        vrm_viewer.reset_expressions()
        
        print("\n✅ Expression test completed!")
        print("You should have seen the VRM model change expressions.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your main application is running and the VRM viewer is loaded.")

if __name__ == "__main__":
    test_expressions() 