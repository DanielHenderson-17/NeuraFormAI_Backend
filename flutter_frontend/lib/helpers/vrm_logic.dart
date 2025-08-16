import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';

/// VRM and animation loading logic extracted from VRMContainer
class VRMLogic {
  /// Plays an animation using the provided JavaScript executor
  static Future<void> playAnimation({
    required String animationName,
    required Future<String> Function(String) executeJavaScript,
    bool isWebViewReady = true,
  }) async {
    if (!isWebViewReady) {
      print("🎬 [VRMLogic] WebView not ready for animation");
      return;
    }
    final base64Data = await loadAnimation(animationName);
    print("🎬 [VRMLogic] Animation file: $animationName.vrma");
    String result = await executeJavaScript('''
      (function() {
        try {
          var output = [];
          output.push("🔍 Basic verification starting...");
          output.push("🔍 Window exists: " + (typeof window !== 'undefined'));
          output.push("🔍 THREE exists: " + (typeof THREE !== 'undefined'));
          output.push("🔍 VRM Viewer ready: " + window.vrmViewerReady);
          output.push("🔍 Animation functions:");
          output.push("🔍 - loadAnimation: " + (typeof window.loadAnimation));
          output.push("🔍 - playAnimation: " + (typeof window.playAnimation));
          output.push("🔍 VRM Animation imports:");
          output.push("🔍 - createVRMAnimationClip: " + (typeof createVRMAnimationClip));
          output.push("🔍 - VRMAnimationLoaderPlugin: " + (typeof VRMAnimationLoaderPlugin));
          output.push("🔍 - VRMLookAtQuaternionProxy: " + (typeof VRMLookAtQuaternionProxy));
          output.push("🔍 Current animation state:");
          output.push("🔍 - VRM loaded: " + !!window.vrm);
          output.push("🔍 - Mixer exists: " + !!window.mixer);
          output.push("🔍 - Animation clip exists: " + !!window.animationClip);
          output.push("🔍 - Is playing: " + window.isPlaying);
          output.push("🎬 Creating blob URL for animation...");
          const byteCharacters = atob('$base64Data');
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], {type: 'application/octet-stream'});
          const blobUrl = URL.createObjectURL(blob);
          output.push("🎬 Created blob URL: " + blobUrl);
          if (typeof window.loadAnimation === 'function') {
            output.push("🎬 Calling loadAnimation with blob URL...");
            window.loadAnimation(blobUrl).then(function(loaded) {
              if (loaded && typeof window.playAnimation === 'function') {
                window.playAnimation();
              }
            });
            output.push("🎬 Animation loading started asynchronously");
          } else {
            output.push("❌ loadAnimation function not available!");
          }
          return "VERIFICATION_RESULTS:" + output.join("|");
        } catch (error) {
          return "VERIFICATION_ERROR:" + error.message + "|" + error.stack;
        }
      })();
    ''');
    print("🎬 [VRMLogic] JavaScript response: '$result'");
    if (result.trim().isNotEmpty) {
      if (result.startsWith("VERIFICATION_RESULTS:")) {
        print("🎬 [VRMLogic] ✅ JavaScript verification completed successfully!");
        var logs = result.substring("VERIFICATION_RESULTS:".length).split("|");
        for (var log in logs) {
          if (log.isNotEmpty) {
            print("🎬 [JS->Flutter] $log");
          }
        }
      } else if (result.startsWith("VERIFICATION_ERROR:")) {
        print("🎬 [VRMLogic] ❌ JavaScript verification failed!");
        print("🎬 [VRMLogic] Error: ${result.substring("VERIFICATION_ERROR:".length)}");
      } else {
        print("🎬 [VRMLogic] ✅ JavaScript executed, result: $result");
      }
    } else {
      print("🎬 [VRMLogic] ⚠️ JavaScript returned empty result");
    }
    print("🎬 [VRMLogic] JavaScript executed successfully");
    print("🎬 [VRMLogic] ============ PLAY ANIMATION COMPLETE ============");
  }

  /// Stops the animation using the provided JavaScript executor
  static Future<void> stopAnimation({
    required Future<String> Function(String) executeJavaScript,
  }) async {
    try {
      print("⏹️ [VRMLogic] Stopping animation");
      await executeJavaScript('''
        if (window.stopAnimation) {
          window.stopAnimation();
        } else {
          console.warn('stopAnimation function not available');
        }
      ''');
    } catch (e) {
      print("❌ [VRMLogic] Failed to stop animation: $e");
    }
  }
  /// Loads a VRM model from assets and returns the base64 string
  static Future<String> loadVRMModel(String vrmModel) async {
    final vrmData = await rootBundle.load('assets/vrm_models/$vrmModel');
    final bytes = vrmData.buffer.asUint8List();
    return base64Encode(bytes);
  }

  /// Loads an animation file from assets and returns the base64 string
  static Future<String> loadAnimation(String animationName) async {
    final animationData = await rootBundle.load('assets/animations/$animationName.vrma');
    final bytes = animationData.buffer.asUint8List();
    return base64Encode(bytes);
  }

  /// Discovers available animations in assets/animations/
  static Future<List<Map<String, String>>> discoverAvailableAnimations() async {
    final manifestContent = await rootBundle.loadString('AssetManifest.json');
    final Map<String, dynamic> manifestMap = json.decode(manifestContent);
    final List<Map<String, String>> animations = [];
    for (String key in manifestMap.keys) {
      if (key.startsWith('assets/animations/') &&
          key.endsWith('.vrma') &&
          !key.contains('/old/') &&
          key.split('/').length == 3) {
        final fileName = key.split('/').last;
        final animationName = fileName.replaceAll('.vrma', '');
        final displayName = animationName[0].toUpperCase() + animationName.substring(1);
        String emoji = '🎭';
        switch (animationName.toLowerCase()) {
          case 'peace': emoji = '✌️'; break;
          case 'greeting': emoji = '👋'; break;
          case 'pose': emoji = '🤸'; break;
          case 'squat': emoji = '🏃'; break;
          case 'spin': emoji = '🌀'; break;
          case 'shoot': emoji = '🔫'; break;
          case 'full': emoji = '💫'; break;
          default: emoji = '🎭';
        }
        animations.add({
          'name': animationName,
          'displayName': displayName,
          'emoji': emoji,
          'path': key,
        });
      }
    }
    return animations;
  }
}
