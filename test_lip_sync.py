#!/usr/bin/env python3
"""
Test script for lip-sync phoneme conversion
"""

def text_to_phonemes(text):
    """Convert text to phonemes for lip-sync animation"""
    # Simple phoneme mapping based on vowel sounds
    phoneme_map = {
        'a': 'aa', 'e': 'ee', 'i': 'ih', 'o': 'oh', 'u': 'ou',
        'A': 'aa', 'E': 'ee', 'I': 'ih', 'O': 'oh', 'U': 'ou',
        'y': 'ih', 'Y': 'ih'
    }
    
    phonemes = []
    words = text.split()
    
    for word in words:
        # Find the most prominent vowel in each word
        word_lower = word.lower()
        for vowel, phoneme in phoneme_map.items():
            if vowel in word_lower:
                phonemes.append(phoneme)
                break
        else:
            # If no vowel found, use neutral 'aa'
            phonemes.append('aa')
    
    return phonemes

def test_lip_sync():
    """Test the lip-sync phoneme conversion"""
    
    test_phrases = [
        "Hello there!",
        "I am so happy to see you!",
        "This is amazing!",
        "How are you doing today?",
        "That's incredible news!",
        "I love this conversation!",
        "What do you think about that?",
        "Absolutely fantastic!",
        "You're wonderful!",
        "Let's talk more!"
    ]
    
    print("🎭 Lip-Sync Phoneme Test")
    print("=" * 50)
    
    for phrase in test_phrases:
        phonemes = text_to_phonemes(phrase)
        print(f"📝 '{phrase}'")
        print(f"🎭 Phonemes: {phonemes}")
        print(f"📊 Count: {len(phonemes)} phonemes")
        print("-" * 30)
    
    # Interactive testing
    print("\n🧪 Interactive Testing Mode")
    print("Type phrases to test phoneme conversion (type 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("Enter a phrase: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input:
                phonemes = text_to_phonemes(user_input)
                print(f"🎭 Phonemes: {phonemes}")
                print(f"📊 Count: {len(phonemes)} phonemes")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\n👋 Testing complete!")

if __name__ == "__main__":
    test_lip_sync() 