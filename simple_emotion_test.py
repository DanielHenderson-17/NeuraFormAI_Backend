#!/usr/bin/env python3
"""
Simple emotion detection test - standalone version
"""

def detect_emotion(message):
    """Detect emotion from message content with semantic understanding"""
    message_lower = message.lower()
    
    # Direct emotion keywords (high confidence)
    emotion_keywords = {
        'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', '😊', '😄', '😍', 'fantastic', 'awesome'],
        'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', '😠', '😡', '🤬', 'upset', 'annoyed'],
        'relaxed': ['fun', 'funny', 'lol', 'haha', 'amusing', '😆', '😂', '🤣', 'hilarious', 'joke'],
        'sad': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate', '😢', '😭', '😔', 'unfortunate', 'disappointed'],
        'Surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected', '😲', '😱', '🤯', 'incredible', 'unbelievable']
    }
    
    # Check direct emotion keywords first (highest priority)
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return emotion
    
    # Semantic emotion detection using word families and context
    def check_semantic_patterns(text):
        # Job stress and frustration patterns
        job_stress_patterns = [
            'quit', 'quitting', 'resign', 'resigning', 'leave', 'leaving',
            'burnout', 'burning out', 'burn out', 'burned out',
            'stress', 'stressed', 'stressing', 'overwhelmed', 'overwhelm',
            'exhausted', 'exhausting', 'tired of', 'sick of', 'fed up',
            'frustrated', 'frustrating', 'annoyed', 'annoying', 'pissed',
            'hate', 'hating', 'terrible', 'awful', 'horrible', 'worst',
            'unfair', 'wrong', 'stupid', 'idiot', 'dumb', 'ridiculous'
        ]
        
        # Loss and grief patterns
        loss_patterns = [
            'died', 'death', 'dead', 'lost', 'loss', 'miss', 'missing', 'gone',
            'passed away', 'passed', 'grandpa', 'grandma', 'father', 'mother',
            'sister', 'brother', 'friend', 'family', 'failed', 'failure',
            'broke', 'broken', 'lost job', 'fired', 'divorce', 'sick',
            'illness', 'cancer', 'hospital', 'pain', 'hurt', 'crying'
        ]
        
        # Success and achievement patterns
        success_patterns = [
            'got', 'received', 'won', 'success', 'achieved', 'accomplished',
            'graduated', 'promoted', 'new job', 'new house', 'engaged',
            'married', 'baby', 'pregnant', 'birthday', 'anniversary',
            'celebration', 'congratulations', 'amazing', 'incredible'
        ]
        
        # Surprise and shock patterns
        surprise_patterns = [
            'unexpected', 'shocking', 'unbelievable', 'incredible',
            'never thought', 'didn\'t expect', 'out of nowhere', 'suddenly',
            'just found out', 'discovered', 'wow', 'omg', 'oh my god'
        ]
        
        # Check each pattern family
        if any(pattern in text for pattern in job_stress_patterns):
            return 'angry'
        elif any(pattern in text for pattern in loss_patterns):
            return 'sad'
        elif any(pattern in text for pattern in success_patterns):
            return 'happy'
        elif any(pattern in text for pattern in surprise_patterns):
            return 'Surprised'
        
        return None
    
    # Try semantic detection
    semantic_result = check_semantic_patterns(message_lower)
    if semantic_result:
        return semantic_result
    
    # Additional context clues
    # Check for negative sentiment words that might indicate frustration
    negative_words = ['bad', 'worst', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'can\'t stand']
    if any(word in message_lower for word in negative_words):
        return 'angry'
    
    return 'neutral'

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