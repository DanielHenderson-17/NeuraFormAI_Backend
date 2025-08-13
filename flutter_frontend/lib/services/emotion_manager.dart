import 'dart:async';
import 'dart:math';

class EmotionManager {
  Timer? _emotionTimer;
  Function(String)? _onSetEmotion;
  Function()? _onResetExpressions;

  /// Initialize the EmotionManager with callbacks to the VRM viewer
  void initialize({
    required Function(String) onSetEmotion,
    required Function() onResetExpressions,
  }) {
    _onSetEmotion = onSetEmotion;
    _onResetExpressions = onResetExpressions;
    print("😊 EmotionManager initialized");
  }

  /// Analyze text for emotional content and trigger appropriate VRM expressions
  void analyzeAndSetEmotion(String text) {
    try {
      final emotion = _detectEmotion(text);
      
      if (emotion.isNotEmpty) {
        print("😊 Detected emotion: $emotion for text: \"${text.length > 50 ? '${text.substring(0, 50)}...' : text}\"");
        _setEmotionWithTimeout(emotion);
      } else {
        print("😐 No strong emotion detected, staying neutral");
      }
    } catch (e) {
      print("⚠️ Failed to analyze emotion: $e");
    }
  }

  /// Set emotion expression with automatic timeout to return to neutral
  void _setEmotionWithTimeout(String emotion, {int durationSeconds = 3}) {
    // Cancel any existing emotion timer
    _emotionTimer?.cancel();

    // Set the emotion
    _onSetEmotion?.call(emotion);

    // Set timer to return to neutral
    _emotionTimer = Timer(Duration(seconds: durationSeconds), () {
      _onResetExpressions?.call();
      print("😐 Emotion timeout - returning to neutral");
    });
  }

  /// Detect emotion from text - matches Python implementation logic
  String _detectEmotion(String text) {
    final lowerText = text.toLowerCase();

    // Happiness indicators
    final happyWords = [
      'happy', 'joy', 'excited', 'wonderful', 'amazing', 'great', 'awesome',
      'fantastic', 'excellent', 'perfect', 'love', 'haha', 'lol', '😊', '😄',
      '😁', '😃', '😀', '🙂', '😍', '🥰', 'yay', 'hooray', 'brilliant',
      'delighted', 'thrilled', 'cheerful', 'glad', 'pleased'
    ];

    // Sadness indicators
    final sadWords = [
      'sad', 'cry', 'upset', 'depressed', 'unhappy', 'disappointed', 'hurt',
      'pain', 'sorrow', 'grief', 'miserable', 'awful', 'terrible', '😢', '😭',
      '😞', '😔', '🙁', '😟', '😕', 'sorry', 'regret', 'unfortunate',
      'heartbroken', 'devastated', 'gloomy', 'melancholy'
    ];

    // Anger indicators
    final angryWords = [
      'angry', 'mad', 'furious', 'rage', 'annoyed', 'frustrated', 'irritated',
      'pissed', 'hate', 'damn', 'stupid', 'ridiculous', '😠', '😡', '🤬',
      '😤', 'outraged', 'livid', 'enraged', 'infuriated', 'irate'
    ];

    // Surprise indicators
    final surpriseWords = [
      'wow', 'omg', 'surprised', 'shocked', 'amazing', 'incredible', 'unbelievable',
      'astonishing', '😲', '😮', '😯', '🤯', 'whoa', 'no way', 'really?',
      'seriously?', 'unexpected', 'stunning', 'remarkable'
    ];

    // Fear/worry indicators
    final fearWords = [
      'scared', 'afraid', 'fear', 'worried', 'nervous', 'anxious', 'panic',
      'terrified', 'frightened', '😨', '😰', '😱', '😧', 'concerned',
      'troubled', 'uneasy', 'apprehensive'
    ];

    // Disgust indicators
    final disgustWords = [
      'disgusting', 'gross', 'yuck', 'eww', 'nasty', 'revolting', 'repulsive',
      '🤢', '🤮', '😷', 'ugh', 'sick', 'vile', 'awful'
    ];

    // Count occurrences and calculate emotion scores
    final emotionScores = <String, int>{
      'happy': _countMatches(lowerText, happyWords),
      'sad': _countMatches(lowerText, sadWords),
      'angry': _countMatches(lowerText, angryWords),
      'surprised': _countMatches(lowerText, surpriseWords),
      'fear': _countMatches(lowerText, fearWords),
      'disgust': _countMatches(lowerText, disgustWords),
    };

    // Find the emotion with the highest score
    String dominantEmotion = '';
    int maxScore = 0;

    emotionScores.forEach((emotion, score) {
      if (score > maxScore) {
        maxScore = score;
        dominantEmotion = emotion;
      }
    });

    // Only return emotion if it has a strong enough signal (at least 1 match)
    if (maxScore > 0) {
      return dominantEmotion;
    }

    return ''; // No strong emotion detected
  }

  /// Count how many words from the emotion word list appear in the text
  int _countMatches(String text, List<String> emotionWords) {
    int count = 0;
    for (final word in emotionWords) {
      if (text.contains(word)) {
        count++;
      }
    }
    return count;
  }

  /// Clear any active emotion and return to neutral
  void clearEmotion() {
    _emotionTimer?.cancel();
    _emotionTimer = null;
    _onResetExpressions?.call();
    print("😐 Emotion cleared - returning to neutral");
  }

  void dispose() {
    _emotionTimer?.cancel();
  }
}
