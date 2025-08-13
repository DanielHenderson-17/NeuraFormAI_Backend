import 'dart:async';
import 'dart:math';
import 'package:webview_windows/webview_windows.dart';
import 'lip_sync_manager.dart';
import 'emotion_manager.dart';

class VRMExpressionManager {
  WebviewController? _webviewController;
  final LipSyncManager _lipSyncManager = LipSyncManager();
  final EmotionManager _emotionManager = EmotionManager();
  Timer? _blinkTimer;
  
  bool _isInitialized = false;
  final Random _random = Random();

  /// Initialize the VRM Expression Manager with the webview controller
  Future<void> initialize(WebviewController webviewController) async {
    try {
      _webviewController = webviewController;

      // Initialize sub-managers with VRM viewer callbacks
      _lipSyncManager.initialize(
        onSetLipSync: _setLipSync,
        onClearLipSync: _clearLipSync,
      );

      _emotionManager.initialize(
        onSetEmotion: _setEmotion,
        onResetExpressions: _resetExpressions,
      );

      // Start automatic blinking
      _startAutoBlink();

      _isInitialized = true;
      print("🎭 VRMExpressionManager initialized successfully");
    } catch (e) {
      print("⚠️ Failed to initialize VRMExpressionManager: $e");
    }
  }

  /// Load a VRM model in the viewer
  Future<void> loadVRM(String vrmFilePath) async {
    if (!_isInitialized || _webviewController == null) {
      print("⚠️ VRMExpressionManager not initialized");
      return;
    }

    try {
      await _webviewController!.executeScript("loadVRM('$vrmFilePath');");
      print("🎭 Loading VRM: $vrmFilePath");
    } catch (e) {
      print("⚠️ Failed to load VRM: $e");
    }
  }

  /// Start voice-synchronized lip sync with emotion detection
  Future<void> startVoiceLipSync(String text, {required double audioDuration}) async {
    if (!_isInitialized) {
      print("⚠️ VRMExpressionManager not initialized");
      return;
    }

    try {
      // Clear any existing expressions first to avoid conflicts with lip sync
      await _resetExpressions();
      await Future.delayed(Duration(milliseconds: 50)); // Brief pause to ensure expressions are cleared
      
      // Analyze emotion first (but after clearing)
      _emotionManager.analyzeAndSetEmotion(text);

      // Start lip sync with exact audio duration
      _lipSyncManager.startLipSync(
        text,
        totalDuration: audioDuration,
      );

      print("🎭 Started voice lip-sync for ${audioDuration.toStringAsFixed(2)}s: \"${text.length > 50 ? '${text.substring(0, 50)}...' : text}\"");
    } catch (e) {
      print("⚠️ Failed to start voice lip-sync: $e");
    }
  }

  /// Start text-only lip sync (without audio)
  Future<void> startTextLipSync(String text, {double durationPerWord = 0.15}) async {
    if (!_isInitialized) {
      print("⚠️ VRMExpressionManager not initialized");
      return;
    }

    try {
      // Analyze emotion first
      _emotionManager.analyzeAndSetEmotion(text);

      // Start lip sync without audio duration
      _lipSyncManager.startLipSync(
        text,
        durationPerWord: durationPerWord,
      );

      print("🎭 Started text lip-sync: \"${text.length > 50 ? '${text.substring(0, 50)}...' : text}\"");
    } catch (e) {
      print("⚠️ Failed to start text lip-sync: $e");
    }
  }

  /// Stop all lip sync animation
  Future<void> stopLipSync() async {
    _lipSyncManager.stopLipSync();
    print("🎭 Stopped lip-sync");
  }

  /// Set a specific emotion expression
  Future<void> setEmotion(String emotion) async {
    _emotionManager.analyzeAndSetEmotion("I am feeling $emotion"); // Trigger the emotion
  }

  /// Clear all expressions and return to neutral
  Future<void> clearAllExpressions() async {
    _lipSyncManager.stopLipSync();
    _emotionManager.clearEmotion();
    await _resetExpressions();
    print("🎭 Cleared all expressions");
  }

  /// Trigger a manual blink
  Future<void> triggerBlink() async {
    await _triggerBlink();
  }

  // Internal methods for VRM viewer communication

  Future<void> _setLipSync(String phoneme) async {
    if (_webviewController != null) {
      try {
        await _webviewController!.executeScript("setLipSync('$phoneme');");
      } catch (e) {
        print("⚠️ Failed to set lip sync: $e");
      }
    }
  }

  Future<void> _clearLipSync() async {
    if (_webviewController != null) {
      try {
        await _webviewController!.executeScript("clearLipSync();");
      } catch (e) {
        print("⚠️ Failed to clear lip sync: $e");
      }
    }
  }

  Future<void> _setEmotion(String emotion) async {
    if (_webviewController != null) {
      try {
        await _webviewController!.executeScript("setEmotion('$emotion');");
      } catch (e) {
        print("⚠️ Failed to set emotion: $e");
      }
    }
  }

  Future<void> _resetExpressions() async {
    if (_webviewController != null) {
      try {
        await _webviewController!.executeScript("resetExpressions();");
      } catch (e) {
        print("⚠️ Failed to reset expressions: $e");
      }
    }
  }

  Future<void> _triggerBlink() async {
    if (_webviewController != null) {
      try {
        await _webviewController!.executeScript("triggerBlink();");
      } catch (e) {
        print("⚠️ Failed to trigger blink: $e");
      }
    }
  }

  /// Start automatic blinking - matches Python implementation
  void _startAutoBlink() {
    // Random blink every 2-8 seconds
    _scheduleNextBlink();
  }

  void _scheduleNextBlink() {
    final nextBlinkDelay = 2000 + _random.nextInt(6000); // 2-8 seconds
    _blinkTimer = Timer(Duration(milliseconds: nextBlinkDelay), () {
      _triggerBlink();
      _scheduleNextBlink(); // Schedule the next blink
    });
  }

  void dispose() {
    _lipSyncManager.dispose();
    _emotionManager.dispose();
    _blinkTimer?.cancel();
    _isInitialized = false;
    print("🎭 VRMExpressionManager disposed");
  }
}
