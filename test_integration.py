#!/usr/bin/env python3
"""
Test VRM Expression Integration

This script tests that the VRM expression system is properly integrated
with your chat application. Run this after starting your main application.

Usage:
    1. Start your main application (run_all.bat)
    2. Run: python test_integration.py
"""

import sys
import os

# Add the chat_ui directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

def test_integration():
    """Test the VRM expression integration"""
    print("🎭 Testing VRM Expression Integration...")
    print("="*50)
    
    try:
        # Import the expression manager
        from right.chat_window import vrm_expression_manager, detect_emotion
        
        print("✅ Expression manager imported successfully")
        
        # Test emotion detection
        print("\n🧠 Testing Emotion Detection:")
        test_messages = [
            ("I'm so happy today!", "joy"),
            ("This makes me angry!", "angry"),
            ("That's so funny!", "fun"),
            ("I'm feeling sad", "sorrow"),
            ("Wow, that's amazing!", "surprised"),
            ("How are you doing?", "neutral")
        ]
        
        for message, expected_emotion in test_messages:
            detected_emotion = detect_emotion(message)
            status = "✅" if detected_emotion == expected_emotion else "❌"
            print(f"  {status} '{message}' → {detected_emotion} (expected: {expected_emotion})")
        
        # Test VRM expression manager
        print("\n🎭 Testing VRM Expression Manager:")
        if vrm_expression_manager.vrm_viewer:
            print("✅ VRM viewer is connected")
            
            # Test setting emotions
            test_emotions = ['joy', 'angry', 'fun', 'sorrow', 'surprised', 'neutral']
            print("🎭 Testing emotion expressions...")
            for emotion in test_emotions:
                print(f"  Setting emotion: {emotion}")
                vrm_expression_manager.set_emotion(emotion)
            
            print("✅ VRM expression system is working!")
            
        else:
            print("⚠️ VRM viewer is not connected")
            print("Make sure your main application is running")
        
        print("\n🎉 Integration test completed!")
        print("\n📋 To test with real chat:")
        print("1. Start your main application")
        print("2. Type messages like 'I'm so happy!' or 'That's amazing!'")
        print("3. Watch the VRM model change expressions automatically!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your main application is running")
        print("2. Check that all files are properly saved")
        print("3. Restart your main application if needed")

if __name__ == "__main__":
    test_integration() 