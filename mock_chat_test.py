#!/usr/bin/env python3
"""
Mock Chat Expression Test

This script simulates how the VRM expression system would work with real chat messages.
It demonstrates emotion detection and automatic expression triggering.

Usage:
    python mock_chat_test.py
"""

import time
import random

def detect_emotion(message):
    """Detect emotion from message content"""
    message_lower = message.lower()
    
    # Emotion keywords
    emotion_keywords = {
        'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', '😊', '😄', '😍', 'fantastic', 'awesome'],
        'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', '😠', '😡', '🤬', 'upset', 'annoyed'],
        'fun': ['fun', 'funny', 'lol', 'haha', 'amusing', '😆', '😂', '🤣', 'hilarious', 'joke'],
        'sorrow': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate', '😢', '😭', '😔', 'unfortunate', 'disappointed'],
        'surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected', '😲', '😱', '🤯', 'incredible', 'unbelievable']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return emotion
    
    return 'neutral'

def simulate_vrm_expression(emotion):
    """Simulate setting VRM expression"""
    print(f"🎭 VRM Model: Setting expression to '{emotion}'")
    # In real implementation, this would call: vrm_viewer.set_emotion(emotion)

def simulate_lip_sync():
    """Simulate lip sync during speech"""
    print("👄 VRM Model: Lip sync animation playing...")
    # In real implementation, this would call lip sync methods

def simulate_chat_interaction(user_message, ai_response):
    """Simulate a complete chat interaction with expressions"""
    print(f"\n{'='*60}")
    print(f"💬 User: {user_message}")
    
    # Detect emotion from user message
    user_emotion = detect_emotion(user_message)
    if user_emotion != 'neutral':
        print(f"🎭 Detected user emotion: {user_emotion}")
        simulate_vrm_expression(user_emotion)
    
    print(f"🤖 AI: {ai_response}")
    
    # Detect emotion from AI response
    ai_emotion = detect_emotion(ai_response)
    if ai_emotion != 'neutral':
        print(f"🎭 Detected AI emotion: {ai_emotion}")
        simulate_vrm_expression(ai_emotion)
    
    # Simulate lip sync during AI speech
    simulate_lip_sync()
    
    time.sleep(1)  # Pause to show the interaction

def main():
    """Run mock chat interactions"""
    print("🎭 Mock Chat Expression Test")
    print("This simulates how VRM expressions would work with real chat messages")
    print("="*60)
    
    # Sample chat interactions
    chat_examples = [
        ("I'm so happy today!", "That's wonderful! I'm glad you're feeling great! 😊"),
        ("This makes me really angry!", "I understand you're upset. Let's talk about what happened."),
        ("That's so funny! 😂", "Haha, I'm glad you found it amusing! It was quite entertaining."),
        ("I'm feeling really sad today", "I'm sorry to hear that. Would you like to talk about what's bothering you?"),
        ("Wow, that's incredible news!", "I'm shocked too! That's absolutely amazing! 😲"),
        ("How are you doing?", "I'm doing well, thank you for asking! How about you?"),
        ("I love this conversation!", "I'm so happy you're enjoying our chat! It's been wonderful talking with you! 😍"),
        ("This is terrible news", "I'm sorry to hear that. That sounds really unfortunate and disappointing."),
        ("LOL that's hilarious!", "Haha, I'm glad you think so! It was pretty funny! 😆"),
        ("OMG that's unbelievable!", "I know, right? That's absolutely incredible! I'm shocked too! 🤯")
    ]
    
    for i, (user_msg, ai_response) in enumerate(chat_examples, 1):
        print(f"\n📝 Chat Interaction #{i}")
        simulate_chat_interaction(user_msg, ai_response)
        
        if i < len(chat_examples):
            print("⏳ Waiting 2 seconds before next interaction...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ Mock chat test completed!")
    print("\n📋 Summary of what would happen in real implementation:")
    print("• User messages trigger emotion detection")
    print("• AI responses trigger emotion detection") 
    print("• VRM model automatically changes facial expressions")
    print("• Lip sync plays during AI speech")
    print("• Expressions match the emotional content of messages")
    
    print("\n🔧 To integrate this into your real chat system:")
    print("1. Add emotion detection to your chat handlers")
    print("2. Call vrm_viewer.set_emotion(emotion) when emotions are detected")
    print("3. Call vrm_viewer.set_lip_sync() during AI speech")
    print("4. Call vrm_viewer.clear_lip_sync() when speech ends")

if __name__ == "__main__":
    main() 