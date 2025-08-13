import 'dart:async';
import 'dart:math';

class LipSyncManager {
  Timer? _lipSyncTimer;
  Timer? _safetyTimer;
  List<String> _lipSyncPhonemes = [];
  int _currentPhonemeIndex = 0;
  Function(String)? _onSetLipSync;
  Function()? _onClearLipSync;

  /// Initialize the LipSyncManager with callbacks to the VRM viewer
  void initialize({
    required Function(String) onSetLipSync,
    required Function() onClearLipSync,
  }) {
    _onSetLipSync = onSetLipSync;
    _onClearLipSync = onClearLipSync;
    print("🎭 LipSyncManager initialized");
  }

  /// Start lip-sync animation for the given text
  /// [text] - The text to convert to phonemes
  /// [durationPerWord] - Duration per phoneme (used when totalDuration is null)
  /// [totalDuration] - Total audio duration in seconds (for voice sync)
  void startLipSync(String text, {double durationPerWord = 0.15, double? totalDuration}) {
    try {
      // Convert text to phonemes (one per word, simple mapping)
      final phonemes = _textToPhonemes(text);
      print("🎭 Starting lip-sync with ${phonemes.length} phonemes: $phonemes");

      // Cancel any existing lip-sync
      stopLipSync();

      if (phonemes.isEmpty) return;

      late double phonemeDuration;

      if (totalDuration != null) {
        // Voice mode: distribute phonemes evenly across total audio duration
        phonemeDuration = totalDuration / phonemes.length;
        print("🎭 Voice mode: ${totalDuration.toStringAsFixed(2)}s total, ${phonemes.length} phonemes, ${phonemeDuration.toStringAsFixed(3)}s per phoneme");
      } else {
        // Text mode: use fixed timing
        phonemeDuration = durationPerWord;
        print("🎭 Text mode: ${phonemeDuration.toStringAsFixed(3)}s per phoneme");
      }

      // Start lip-sync animation
      _lipSyncPhonemes = phonemes;
      _currentPhonemeIndex = 0;

      _lipSyncTimer = Timer.periodic(
        Duration(milliseconds: (phonemeDuration * 1000).round()),
        (_) => _nextPhoneme(),
      );

      // Set a safety timer to stop lip-sync SLIGHTLY BEFORE audio should end
      if (totalDuration != null) {
        _safetyTimer = Timer(
          Duration(milliseconds: ((totalDuration - 0.1) * 1000).round()), // End 100ms before audio ends
          () => stopLipSync(),
        );
      }

      // Start with first phoneme
      _setCurrentPhoneme();
    } catch (e) {
      print("⚠️ Failed to start lip-sync: $e");
    }
  }

  /// Stop lip-sync animation
  void stopLipSync() {
    _lipSyncTimer?.cancel();
    _lipSyncTimer = null;

    _safetyTimer?.cancel();
    _safetyTimer = null;

    _lipSyncPhonemes.clear();
    _currentPhonemeIndex = 0;

    // Clear lip-sync expressions
    _onClearLipSync?.call();
  }

  /// Move to next phoneme in lip-sync sequence
  void _nextPhoneme() {
    if (_lipSyncPhonemes.isNotEmpty) {
      _currentPhonemeIndex++;

      if (_currentPhonemeIndex >= _lipSyncPhonemes.length) {
        // Lip-sync complete
        stopLipSync();
        print("🎭 Lip-sync animation complete");
      } else {
        // Set next phoneme
        _setCurrentPhoneme();
      }
    }
  }

  /// Set the current phoneme expression
  void _setCurrentPhoneme() {
    if (_lipSyncPhonemes.isNotEmpty && 
        _currentPhonemeIndex < _lipSyncPhonemes.length) {
      final phoneme = _lipSyncPhonemes[_currentPhonemeIndex];
      _onSetLipSync?.call(phoneme);
      print("🎭 Lip-sync phoneme ${_currentPhonemeIndex + 1}/${_lipSyncPhonemes.length}: $phoneme");
    }
  }

  /// Convert text to phonemes for lip-sync animation - Restored to working version
  List<String> _textToPhonemes(String text) {
    // Original phoneme mapping that worked well (before conservative changes)
    final phonemeMap = {
      'a': 'aa', 'e': 'ee', 'i': 'ih', 'o': 'oh', 'u': 'ou',
      'A': 'aa', 'E': 'ee', 'I': 'ih', 'O': 'oh', 'U': 'ou',
      'y': 'ih', 'Y': 'ih'
    };

    final phonemes = <String>[];
    final words = text.split(' ');

    for (final word in words) {
      if (word.trim().isEmpty) continue;
      
      final wordLower = word.toLowerCase();
      
      // Find the primary vowel sound
      String primaryPhoneme = 'aa'; // default
      for (final entry in phonemeMap.entries) {
        if (wordLower.contains(entry.key.toLowerCase())) {
          primaryPhoneme = entry.value;
          break;
        }
      }

      // Add multiple phonemes per word for more active movement
      if (word.length <= 3) {
        // Short words: 2 phonemes (open + close)
        phonemes.add(primaryPhoneme);
        phonemes.add('ih'); // brief close
      } else if (word.length <= 6) {
        // Medium words: 3 phonemes (open + close + open)
        phonemes.add(primaryPhoneme);
        phonemes.add('ih'); // brief close
        phonemes.add('aa'); // secondary opening
      } else {
        // Long words: 4 phonemes (more active movement)
        phonemes.add(primaryPhoneme);
        phonemes.add('ih'); // brief close
        phonemes.add('aa'); // secondary opening
        phonemes.add('ih'); // another brief close
      }
    }

    return phonemes;
  }

  void dispose() {
    stopLipSync();
  }
}
