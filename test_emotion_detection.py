#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced emotion detection system
"""

# Import the emotion detection function
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_ui.right.chat_window import detect_emotion

def test_emotion_detection():
    """Test various phrases to see what emotions they trigger"""
    
    test_phrases = [
        # Direct emotion keywords
        ("I'm so happy!", "happy"),
        ("This makes me angry!", "angry"),
        ("That's so funny!", "relaxed"),
        ("I'm feeling sad", "sad"),
        ("Wow, that's amazing!", "Surprised"),
        
        # Job stress patterns
        ("I want to quit my job", "angry"),
        ("I'm thinking of resigning", "angry"),
        ("This job is burning me out", "angry"),
        ("I'm so stressed at work", "angry"),
        ("I'm overwhelmed with work", "angry"),
        ("I'm exhausted from this job", "angry"),
        ("I'm tired of this place", "angry"),
        ("I'm fed up with my boss", "angry"),
        ("I hate my job", "angry"),
        ("This is the worst job ever", "angry"),
        ("My job is terrible", "angry"),
        ("I can't stand this anymore", "angry"),
        
        # Loss and grief patterns
        ("My grandpa died", "sad"),
        ("I lost my job", "sad"),
        ("My friend passed away", "sad"),
        ("I'm missing my family", "sad"),
        ("I failed the test", "sad"),
        ("My relationship broke", "sad"),
        ("I'm sick and tired", "sad"),
        
        # Success patterns
        ("I got a promotion!", "happy"),
        ("I won the lottery!", "happy"),
        ("I graduated!", "happy"),
        ("I got engaged!", "happy"),
        ("I'm having a baby!", "happy"),
        ("Congratulations!", "happy"),
        
        # Surprise patterns
        ("That's unbelievable!", "Surprised"),
        ("I never thought this would happen", "Surprised"),
        ("This is incredible!", "Surprised"),
        ("I just found out something shocking", "Surprised"),
        ("Oh my god!", "Surprised"),
        
        # Neutral phrases
        ("How are you doing?", "neutral"),
        ("What's the weather like?", "neutral"),
        ("I need to go to the store", "neutral"),
    ]
    
    print("🎭 Enhanced Emotion Detection Test")
    print("=" * 50)
    
    correct = 0
    total = len(test_phrases)
    
    for phrase, expected in test_phrases:
        detected = detect_emotion(phrase)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{phrase}' → {detected} (expected: {expected})")
        if detected == expected:
            correct += 1
    
    print("=" * 50)
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    
    # Interactive testing
    print("\n🧪 Interactive Testing Mode")
    print("Type phrases to test emotion detection (type 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("Enter a phrase: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input:
                emotion = detect_emotion(user_input)
                print(f"🎭 Detected emotion: {emotion}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\n👋 Testing complete!")

if __name__ == "__main__":
    test_emotion_detection() 