#!/usr/bin/env python3
"""
Test VRM Expressions with Running Application

This script tests VRM expressions by connecting to your existing running application.
Make sure your main PyQt app is running first, then run this script.

Usage:
    1. Start your main application (run_all.bat)
    2. Run: python test_with_running_app.py
"""

import sys
import os
import time

# Add the chat_ui directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chat_ui'))

def test_expressions_with_running_app():
    """Test VRM expressions by connecting to the running application"""
    print("🎭 Testing VRM Expressions with Running Application...")
    print("Make sure your main PyQt app is running!")
    print("="*60)
    
    try:
        # Import the VRM webview
        from center.vrm_webview import VRMWebView
        
        # Create a new VRM viewer instance (this will be separate from your main app)
        print("📱 Creating test VRM viewer...")
        vrm_viewer = VRMWebView()
        
        # Load a VRM model
        print("🔄 Loading VRM model...")
        vrm_path = "chat_ui/assets/vrms/fuka_model.vrm"
        vrm_viewer.load_vrm(vrm_path)
        
        # Wait for the model to load
        print("⏳ Waiting for model to load...")
        time.sleep(8)  # Give more time for loading
        
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
            time.sleep(3)  # Hold each expression for 3 seconds
        
        # Test lip sync
        print("\n👄 Testing Lip Sync:")
        phonemes = ['a', 'i', 'u', 'e', 'o']
        for phoneme in phonemes:
            print(f"  Testing phoneme '{phoneme}'...")
            vrm_viewer.set_lip_sync(phoneme)
            time.sleep(1)
        
        # Clear lip sync
        vrm_viewer.clear_lip_sync()
        
        # Test blink
        print("\n👁️ Testing Blink:")
        for i in range(3):
            print(f"  Blink {i+1}/3...")
            vrm_viewer.trigger_blink()
            time.sleep(2)
        
        # Reset to neutral
        print("\n🔄 Resetting to neutral...")
        vrm_viewer.reset_expressions()
        
        print("\n✅ Expression test completed!")
        print("You should have seen the VRM model change expressions in a separate window.")
        print("This demonstrates the expression system is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your main application is running")
        print("2. Make sure the VRM viewer bundle is built (run_all.bat)")
        print("3. Check that the VRM files exist in chat_ui/assets/vrms/")

def test_emotion_detection():
    """Test emotion detection logic"""
    print("\n🧠 Testing Emotion Detection Logic:")
    print("="*40)
    
    def detect_emotion(message):
        """Detect emotion from message content"""
        message_lower = message.lower()
        
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love'],
            'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful'],
            'fun': ['fun', 'funny', 'lol', 'haha', 'amusing'],
            'sorrow': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate'],
            'surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return emotion
        return 'neutral'
    
    # Test messages
    test_messages = [
        "I'm so happy today!",
        "This makes me angry!",
        "That's so funny!",
        "I'm feeling sad",
        "Wow, that's amazing!",
        "How are you doing?"
    ]
    
    for message in test_messages:
        emotion = detect_emotion(message)
        print(f"Message: '{message}' → Emotion: {emotion}")

if __name__ == "__main__":
    print("🎭 VRM Expression System Test")
    print("="*60)
    
    # Test emotion detection first
    test_emotion_detection()
    
    # Ask user if they want to test VRM expressions
    print("\n" + "="*60)
    response = input("Do you want to test VRM expressions? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        test_expressions_with_running_app()
    else:
        print("Skipping VRM expression test.")
        print("You can run this script again later to test expressions.")
    
    print("\n✅ Test completed!") 